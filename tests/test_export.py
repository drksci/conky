"""The export: a vault shown as an Obsidian folder, the same bytes each time, off the history."""

import json
from pathlib import Path

import pytest

from conky import Vault
from conky.cli import main
from conky.export import CANVAS

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
        if p.is_file()
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


def test_affine_writes_nothing_and_says_what_was_found(small: Vault, capsys):
    assert run(small, "affine") == 1
    assert not (small.path / "dist").exists()
    said = capsys.readouterr().err
    assert "2026-11-20" in said
    assert "conky export obsidian" in said
