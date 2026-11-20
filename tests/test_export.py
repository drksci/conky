"""The export: a vault shown as an Obsidian or Notion folder, the same bytes, off the history."""

import json
import zipfile
from pathlib import Path

import pytest

from conky import Vault
from conky.cli import main
from conky.export import CANVAS, OVERVIEW, WHO, ZIP

from .conftest import AT

ASK = {"prompt": "say hello", "into": "said", "provider": "model"}
WATCH = [{"on": "kitchen", "when": "true", "ask": ASK}]
RULE = [{"each": "true"}]


def put(vault: Vault, page: str, changes: dict, body: str | None = None) -> None:
    assert vault.write(page, changes, body, actor="alice", at=AT).ok


@pytest.fixture
def small(vault: Vault) -> Vault:
    put(vault, "kitchen", {}, "The kitchen.\n")
    put(vault, "model", {"api": "stub"}, "A provider.\n")
    put(vault, "cellar", {"within": "kitchen", "rules": RULE}, "Cold.\n")
    put(vault, "wine", {"within": "cellar"}, "Red.\n")
    put(vault, "cook", {"within": "kitchen", "watch": WATCH}, "A cook, see [[wine]].\n")
    put(vault, "note", {}, "Loose ![[kitchen#members]]\n")
    return vault


def run(vault: Vault, *args: str) -> int:
    return main(["--vault", str(vault.path), "--keys", str(vault.keys_dir), "export", *args])


def tree(folder: Path) -> dict[str, str]:
    return {
        p.relative_to(folder).as_posix(): p.read_text(encoding="utf-8")
        for p in sorted(folder.rglob("*"))
        if p.is_file() and p.suffix != ".zip"
    }


def test_the_tree_follows_spaces(small: Vault):
    assert run(small, "obsidian") == 0
    folder = small.path / "dist" / "obsidian"
    assert sorted(tree(folder)) == [
        CANVAS,
        "kitchen/cellar/cellar.md",
        "kitchen/cellar/wine.md",
        "kitchen/cook.md",
        "kitchen/kitchen.md",
        "model.md",
        "note.md",
        OVERVIEW,
        WHO,
    ]


def test_a_note_keeps_its_frontmatter_and_body(small: Vault):
    run(small, "obsidian")
    files = tree(small.path / "dist" / "obsidian")
    assert files["kitchen/cook.md"] == (small.pages_dir / "cook.md").read_text(encoding="utf-8")
    assert "A cook, see [[wine]]." in files["kitchen/cook.md"]
    assert files["note.md"].endswith("Loose ![[kitchen#members]]\n")


def test_a_note_is_the_page_as_written_and_nothing_more(small: Vault):
    run(small, "obsidian")
    files = tree(small.path / "dist" / "obsidian")
    for name, where in (("kitchen", "kitchen/kitchen.md"), ("cook", "kitchen/cook.md")):
        assert files[where] == (small.pages_dir / f"{name}.md").read_text(encoding="utf-8")


def test_the_canvas_has_the_required_fields(small: Vault):
    run(small, "obsidian")
    canvas = json.loads((small.path / "dist" / "obsidian" / CANVAS).read_text(encoding="utf-8"))
    nodes = {n["id"]: n for n in canvas["nodes"]}
    assert len(nodes) == len(canvas["nodes"])
    for node in nodes.values():
        assert {"id", "type", "x", "y", "width", "height"} <= set(node)
        assert node["type"] in {"file", "group"}
        if node["type"] == "file":
            assert (small.path / "dist" / "obsidian" / node["file"]).is_file()
    assert {n["label"] for n in nodes.values() if n["type"] == "group"} == {"kitchen", "cellar"}
    ids = set(nodes)
    for edge in canvas["edges"]:
        assert {"id", "fromNode", "toNode"} <= set(edge)
        assert edge["fromNode"] in ids and edge["toNode"] in ids
    assert {e["label"] for e in canvas["edges"]} == {"within", "watch", "ask"}
    assert len({e["id"] for e in canvas["edges"]}) == len(canvas["edges"])


def test_a_group_holds_what_is_within_it(small: Vault):
    run(small, "obsidian")
    canvas = json.loads((small.path / "dist" / "obsidian" / CANVAS).read_text(encoding="utf-8"))
    nodes = {n["id"]: n for n in canvas["nodes"]}
    outer, inner, wine = nodes["space-kitchen"], nodes["space-cellar"], nodes["page-wine"]
    for inside, around in ((inner, outer), (wine, inner)):
        assert around["x"] <= inside["x"]
        assert around["y"] <= inside["y"]
        assert inside["x"] + inside["width"] <= around["x"] + around["width"]
        assert inside["y"] + inside["height"] <= around["y"] + around["height"]


def test_the_same_vault_gives_the_same_bytes(small: Vault):
    run(small, "obsidian")
    first = tree(small.path / "dist" / "obsidian")
    (small.path / "dist" / "obsidian" / "stray.md").write_text("x", encoding="utf-8")
    run(small, "obsidian")
    assert tree(small.path / "dist" / "obsidian") == first


def test_the_output_is_outside_the_history(small: Vault):
    before = small.log()
    run(small, "obsidian")
    exclude = (small.path / ".git" / "info" / "exclude").read_text(encoding="utf-8")
    assert exclude.splitlines().count("dist/") == 1
    run(small, "obsidian")
    assert (small.path / ".git" / "info" / "exclude").read_text(encoding="utf-8") == exclude
    small.verify()
    assert small.log() == before


def test_an_uncommitted_edit_does_not_reach_the_export(small: Vault):
    (small.pages_dir / "note.md").write_text("---\n---\nstray\n", encoding="utf-8")
    run(small, "obsidian", "--out", str(small.path.parent / "shown"))
    assert "stray" not in (small.path.parent / "shown" / "note.md").read_text(encoding="utf-8")


def test_an_empty_vault_exports_an_empty_canvas(vault: Vault):
    assert run(vault, "obsidian") == 0
    canvas = json.loads((vault.path / "dist" / "obsidian" / CANVAS).read_text(encoding="utf-8"))
    assert canvas == {"nodes": [], "edges": []}


def test_out_must_be_a_folder_of_its_own(small: Vault, tmp_path: Path, capsys):
    assert run(small, "obsidian", "--out", str(small.path)) == 1
    other = tmp_path / "docs"
    other.mkdir()
    (other / "mine.txt").write_text("keep", encoding="utf-8")
    assert run(small, "obsidian", "--out", str(other)) == 1
    assert (other / "mine.txt").read_text(encoding="utf-8") == "keep"
    assert "give --out a new folder" in capsys.readouterr().err


def who_rows(vault: Vault) -> dict[str, list[str]]:
    who = (vault.path / "dist" / "obsidian" / WHO).read_text(encoding="utf-8")
    return {
        line.split("|")[1].strip(): [c.strip() for c in line.split("|")[2:-1]]
        for line in who.splitlines()
        if line.startswith("| [[")
    }


def test_who_lists_each_page_from_the_history(small: Vault):
    put(small, "wine", {}, "Rose.\n")
    run(small, "obsidian")
    who = (small.path / "dist" / "obsidian" / WHO).read_text(encoding="utf-8")
    assert who.startswith("<!-- Generated by conky export from the vault's Git history.")
    rows = who_rows(small)
    names = ("cellar", "cook", "kitchen", "model", "note", "wine")
    assert sorted(rows) == [f"[[{n}]]" for n in names]
    actor, when, kind, cause, count = rows["[[wine]]"]
    assert (actor, kind, cause, count) == ("alice", "write", "-", "2")
    assert when.endswith("Z") and when[:4].isdigit()
    assert rows["[[kitchen]]"][-1] == "1"


def test_who_shows_the_cause_and_leaves_notes_alone(small: Vault):
    cause = small.log()[0].split()[0]
    assert small.write("note", {"x": 1}, None, actor="bob", at=AT, cause=cause).ok
    run(small, "obsidian")
    row = who_rows(small)["[[note]]"]
    assert row[0] == "bob" and row[3] == cause[:7]
    folder = small.path / "dist" / "obsidian"
    assert (folder / "note.md").read_text(encoding="utf-8") == (
        small.pages_dir / "note.md"
    ).read_text(encoding="utf-8")


def test_who_does_not_count_a_refusal(small: Vault):
    put(small, "cellar", {"rules": [{"each": "false"}]})
    refused = small.write("wine", {"x": 1}, None, actor="mallory", at=AT)
    assert not refused.ok
    run(small, "obsidian")
    actor, _when, _kind, _cause, count = who_rows(small)["[[wine]]"]
    assert (actor, count) == ("alice", "1")


def test_who_is_the_same_each_time(small: Vault):
    run(small, "obsidian")
    first = (small.path / "dist" / "obsidian" / WHO).read_bytes()
    run(small, "obsidian")
    assert (small.path / "dist" / "obsidian" / WHO).read_bytes() == first


def test_the_overview_shows_only_nested_spaces_with_counts(small: Vault):
    run(small, "obsidian")
    canvas = json.loads((small.path / "dist" / "obsidian" / OVERVIEW).read_text(encoding="utf-8"))
    assert canvas["edges"] == []
    nodes = {n["id"]: n for n in canvas["nodes"]}
    assert set(nodes) == {"space-kitchen", "space-cellar"}
    assert all(n["type"] == "group" for n in nodes.values())
    assert nodes["space-kitchen"]["label"] == "kitchen: 3 pages"
    assert nodes["space-cellar"]["label"] == "cellar: 1 page"
    outer, inner = nodes["space-kitchen"], nodes["space-cellar"]
    assert outer["x"] <= inner["x"] and outer["y"] <= inner["y"]
    assert inner["x"] + inner["width"] <= outer["x"] + outer["width"]
    assert inner["y"] + inner["height"] <= outer["y"] + outer["height"]


def test_the_overview_of_a_vault_without_spaces_is_empty(vault: Vault):
    put(vault, "note", {}, "Loose.\n")
    run(vault, "obsidian")
    canvas = json.loads((vault.path / "dist" / "obsidian" / OVERVIEW).read_text(encoding="utf-8"))
    assert canvas == {"nodes": [], "edges": []}


def test_notion_fences_the_frontmatter_and_keeps_the_tree(small: Vault):
    assert run(small, "notion") == 0
    folder = small.path / "dist" / "notion"
    files = tree(folder)
    assert sorted(files) == [
        "kitchen/cellar/cellar.md",
        "kitchen/cellar/wine.md",
        "kitchen/cook.md",
        "kitchen/kitchen.md",
        "model.md",
        "note.md",
        WHO,
    ]
    cook = files["kitchen/cook.md"]
    assert cook.startswith("```yaml\n") and "within: kitchen" in cook.split("```")[1]
    assert cook.endswith("```\n\nA cook, see [[wine]].\n")
    assert files["note.md"].startswith("```yaml\n")


def test_notion_zip_holds_one_folder_of_the_same_notes(small: Vault):
    run(small, "notion")
    folder = small.path / "dist" / "notion"
    with zipfile.ZipFile(folder / ZIP) as archive:
        assert archive.testzip() is None
        names = archive.namelist()
        assert names == sorted(names) and {n.split("/")[0] for n in names} == {"conky"}
        assert len(names) == 7
        for name in names:
            note = folder / name.removeprefix("conky/")
            assert archive.read(name).decode("utf-8") == note.read_text(encoding="utf-8")
    first = (folder / ZIP).read_bytes()
    run(small, "notion")
    assert (folder / ZIP).read_bytes() == first
    exclude = (small.path / ".git" / "info" / "exclude").read_text(encoding="utf-8")
    assert "dist/" in exclude


def test_only_obsidian_and_notion_are_forms(small: Vault):
    with pytest.raises(SystemExit):
        run(small, "affine")
    assert not (small.path / "dist").exists()
