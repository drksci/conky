"""The trial pictures: a timeline read from a tiny vault, the graph the view draws made from it,
and the published records. No model is run: a vault is built by writes alone. The view itself is
tested by `npm test` in viewer/."""

from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

import pytest
from bench import dynamics
from bench.timeline import classify, timeline

from conky import Vault
from conky.page import Page
from tests.test_pages import AT, w

ROOT = Path(__file__).resolve().parent.parent
CARDS = ROOT / "docs" / "results" / "cards"
TOKENS = json.loads((ROOT / "src" / "conky" / "tokens.json").read_text())
ASK = {"on": "order", "when": "true", "ask": {"provider": "helper", "writes": "den", "prompt": "p"}}


@pytest.fixture
def tiny(vault: Vault) -> Vault:
    """A den with a rule, a counting reflex and `shows`, a keeper that asks a provider, a
    payment, a refused payment and the count."""
    count = {"on": "refusal", "when": "true", "set": {"turned_away": "page.turned_away + 1"}}
    shows = {"most": 3, "first": "page.amount"}
    rule = [{"each": "page.amount <= space.cash - 20"}]
    w(vault, "helper", {"api": "command", "command": "stand"})
    w(vault, "den", {"cash": 80, "turned_away": 0, "rules": rule, "shows": shows})
    w(vault, "order", {})
    w(vault, "keeper", {"within": "den", "watch": [ASK]})
    vault.write(
        "payment-baker", {"within": "den", "amount": 30}, "for [[order]]", actor="alice", at=AT
    )
    w(vault, "den", {"watch": [count]}, actor="keeper")
    w(vault, "landlord-payment", {"within": "den", "amount": 70})
    return vault


def test_a_page_is_classified_by_what_it_carries() -> None:
    ask = {"on": "x", "ask": {"prompt": "p", "provider": "helper"}}
    count = {"on": "refusal", "when": "true", "set": {"n": "page.n + 1"}}
    own = {"on": "tally", "when": "true", "set": {"n": "page.n + 1"}}
    assert classify("a", Page(watch=[ask, count])) == "character"
    assert classify("a", Page(watch=[count])) == "reflex"
    assert classify("tally", Page(watch=[own])) == "measure"
    assert classify("a", Page(fields={"api": "command"})) == "provider"
    assert classify("a", Page(fields={"turn": 1, "ended": False})) == "screen"
    assert classify("a", Page(fields={"keys": "x"})) == "hands"
    assert classify("a", Page(fields={"cash": 3})) == "page"


def test_the_timeline_reads_the_history_oldest_first(tiny: Vault) -> None:
    events = timeline(tiny.pages_dir.parent)
    assert json.loads(json.dumps(events)) == events
    kinds = [(e["kind"], e["page"]) for e in events]
    assert kinds[-3:] == [("write", "den"), ("refused", "landlord-payment"), ("write", "den")]
    den = events[1]
    assert den["rules"] == [{"each": True, "text": "page.amount <= space.cash - 20"}]
    assert den["state"]["shows"] == {"most": 3, "first": "page.amount"}
    keeper = events[3]
    assert keeper["role"] == "character" and keeper["state"]["watch"][0]["provider"] == "helper"
    assert events[4]["links"] == ["order"] and events[4]["within"] == "den"
    assert events[-2]["reason"].startswith("rule:") and events[-2]["from"] == "den"
    assert events[-1]["fields"] == {"turned_away": [0, 1]} and events[-1]["cause"] == 7


def tiny_graph(tiny: Vault) -> dict:
    return dynamics.graph(timeline(tiny.pages_dir.parent), "tiny", 1)


def test_the_graph_has_a_node_a_page_with_its_archetype(tiny: Vault) -> None:
    events = timeline(tiny.pages_dir.parent)
    g = dynamics.graph(events, "tiny", 1)
    assert json.dumps(g) == json.dumps(dynamics.graph(events, "tiny", 1))  # deterministic
    pages = {e["page"] for e in events}
    assert sorted(n["id"] for n in g["nodes"]) == sorted(pages)
    final = {e["page"]: e["role"] for e in events if e["kind"] == "write"}
    for node in g["nodes"]:
        assert node["archetype"] == final.get(node["id"], "page")
    kinds = {n["id"]: n["kind"] for n in g["nodes"]}
    assert kinds["den"].startswith("space") and kinds["keeper"] == "character"
    assert kinds["helper"] == "provider" and kinds["payment-baker"] == "page"
    parents = {n["id"]: n["parent"] for n in g["nodes"]}
    assert parents["keeper"] == "den" and parents["payment-baker"] == "den"


def test_every_panel_kind_appears_and_edges_end_on_rows(tiny: Vault) -> None:
    g = tiny_graph(tiny)
    panels = {p["kind"] for n in g["nodes"] for p in n["panels"]}
    assert panels == set(dynamics.PANELS)
    rows = {r["id"] for n in g["nodes"] for p in n["panels"] for r in p["rows"]}
    kinds = {e["kind"] for e in g["edges"]}
    assert {"turned-away", "plugs"} <= kinds
    assert any(e["targetRow"] in rows for e in g["edges"] if e["kind"] == "turned-away")
    assert any(e["sourceRow"] in rows for e in g["edges"] if e["kind"] == "plugs")
    for e in g["edges"]:
        assert e["sourceRow"] in rows | {None} and e["targetRow"] in rows | {None}
    for n in g["nodes"]:  # every expression carries its body and the names it reads
        for p in n["panels"]:
            for r in p["rows"]:
                if p["kind"] == "rules":
                    assert r["expr"]["body"] and r["expr"]["reads"] == ["page", "space"]


def test_steps_reference_only_what_exists_and_pens_mean_something(tiny: Vault) -> None:
    g = tiny_graph(tiny)
    ids = {n["id"] for n in g["nodes"]} | {e["id"] for e in g["edges"]}
    ids |= {r["id"] for n in g["nodes"] for p in n["panels"] for r in p["rows"]}
    for step in g["steps"]:
        assert set(step["appear"]) <= ids and set(step["dim"]) <= ids
        assert {c["row"] for c in step["change"]} <= ids
        assert {s["id"] for s in step["subject"]} <= ids
        assert {s["pen"] for s in step["subject"]} <= set(TOKENS["meaning"])
        assert len({s["pen"] for s in step["subject"]}) <= 2
    shown = set().union(*(s["appear"] for s in g["steps"]))
    assert {n["id"] for n in g["nodes"]} <= shown


def test_captions_are_plain_sentences(tiny: Vault) -> None:
    for step in tiny_graph(tiny)["steps"]:
        words = step["caption"]
        assert words.endswith(".") and not re.search(r"->|=>|\b(Kind|Cause|Page|Model)\b", words)
        assert words[0].isupper() or words.split()[0].islower()
    events = timeline(tiny.pages_dir.parent)
    refused = dynamics._describe(next(e for e in events if e["kind"] == "refused"), events)
    assert refused["words"] == (
        "landlord-payment is turned away: it breaks den's rule page.amount <= space.cash - 20."
    )


def test_every_symbol_named_is_in_the_one_table(tiny: Vault) -> None:
    g = tiny_graph(tiny)
    named = {n["symbol"] for n in g["nodes"]} | {s["symbol"] for s in g["steps"]}
    named |= {p["symbol"] for n in g["nodes"] for p in n["panels"]}
    archetypes = {"character", "provider", "measure", "reflex", "screen", "hands", "page"}
    known = set(TOKENS["symbol"])
    assert named <= known and archetypes <= known
    assert set(dynamics.PANEL_SYMBOL.values()) | set(dynamics.STEP_SYMBOL.values()) <= known


def test_publishing_writes_the_records_the_graph_the_board_and_the_block(
    tiny: Vault, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    run = tmp_path / "run"
    shutil.copytree(tiny.pages_dir.parent, run / "draw-1" / "vault")
    row = {"card": "a-keeper-binds-itself", "draw": 1, "model": "stand-in", "vault": "/private/x",
           "expects": [{"step": 1, "failed": []}], "calls": 0}  # fmt: skip
    (run / "rows.jsonl").write_text(json.dumps(row) + "\n", encoding="utf-8")
    (run / "observations.jsonl").write_text("{}\n", encoding="utf-8")
    (run / "verdict.txt").write_text("success met: passed 1 of 1\n", encoding="utf-8")
    root = tmp_path / "repo"
    (root / "docs" / "research").mkdir(parents=True)
    readme = root / "README.md"
    readme.write_text(f"top\n{dynamics.START}\nold\n{dynamics.END}\nend\n", encoding="utf-8")
    folder = dynamics.publish_card(run, root, "2026-11-20", "abc")
    assert sorted(p.name for p in folder.iterdir()) == [
        "graph.json", "observations.jsonl", "rows.jsonl", "run.json", "timeline.json",
        "verdict.txt",
    ]  # fmt: skip
    assert "/private" not in (folder / "rows.jsonl").read_text()
    said = dynamics.render([folder], viewer=tmp_path / "no-view")
    assert "pictures are left as they were" in said[0] and "npm ci" in said[0]
    dynamics.refresh(root)
    first = (readme.read_bytes(), (root / dynamics.BOARD).read_bytes())
    assert readme.read_text().startswith("top\n") and "old" not in readme.read_text()
    board = (root / dynamics.BOARD).read_text()
    assert "met" in board and "not drawn" in board and "topology-dark.png" in board
    dynamics.refresh(root)
    assert (readme.read_bytes(), (root / dynamics.BOARD).read_bytes()) == first


def test_the_readme_block_and_the_board_are_what_publishing_writes() -> None:
    text = (ROOT / "README.md").read_text(encoding="utf-8")
    head = text.split(dynamics.START, 1)[1].split(dynamics.END, 1)[0]
    assert dynamics.START + head + dynamics.END == dynamics.block(ROOT)
    assert (ROOT / dynamics.BOARD).read_text(encoding="utf-8") == dynamics.board(ROOT)
    assert text.count("dynamics-dark.webp") == 3 and text.count("dynamics-light.webp") == 3


def test_published_graphs_are_what_their_records_describe() -> None:
    for folder in sorted(CARDS.iterdir()):
        info = json.loads((folder / "run.json").read_text())
        events = json.loads((folder / "timeline.json").read_text())[str(info["shown"])]
        drawn = json.loads((folder / "graph.json").read_text())
        assert drawn == dynamics.graph(events, info["card"], info["shown"])
        for name in dynamics.PICTURES:
            assert (folder / name).exists(), f"{folder.name}/{name}: run npm run render in viewer/"


def test_the_crowded_desk_shows_the_notes_the_prompt_showed() -> None:
    g = json.loads((CARDS / "a-clerk-reads-a-crowded-desk" / "graph.json").read_text())
    notes = [n for n in g["nodes"] if n["form"] == "note"]
    assert len(notes) == 40 and all(n["parent"] == "clerk" for n in notes)
    last = g["steps"][-1]
    kept = [s["id"] for s in last["subject"] if s["pen"] == "kept" and s["id"].startswith("note")]
    assert len(kept) == 8 and "note-07" in kept and len(last["dim"]) == 32


def complete(events: list[dict], g: dict) -> None:
    """Every field a page ends with is a row of its node, counted in its "N more", or a field
    the graph leaves out on purpose (`dynamics.HIDDEN`, with its reason); every rule and watch
    entry is a row; every commit is part of a step."""
    last = {e["page"]: e["state"] for e in events if e["state"]}
    nodes = {n["id"]: n for n in g["nodes"]}
    for page, state in last.items():
        node = nodes[page]
        fields = [p for p in node["panels"] if p["kind"] == "fields"]
        named = {r["name"] for p in fields for r in p["rows"]}
        more = sum(p["more"] for p in fields)
        missing = [f for f in state["fields"] if f not in named and f not in dynamics.HIDDEN]
        assert len(missing) <= more, f"{page}: {missing} are not in its cell"
        rules = [r for p in node["panels"] if p["kind"] == "rules" for r in p["rows"]]
        hears = [r for p in node["panels"] if p["kind"] == "hears" for r in p["rows"]]
        assert len(rules) == len(state["rules"]) and len(hears) == len(state["watch"])
    told = sum(len(s["events"]) for s in dynamics.story(events))
    assert told == len(events)


def test_a_cell_accounts_for_its_page_and_every_commit_for_a_step(tiny: Vault) -> None:
    events = timeline(tiny.pages_dir.parent)
    complete(events, dynamics.graph(events, "tiny", 1))
    for folder in sorted(CARDS.iterdir()):
        info = json.loads((folder / "run.json").read_text())
        events = json.loads((folder / "timeline.json").read_text())[str(info["shown"])]
        complete(events, json.loads((folder / "graph.json").read_text()))


def test_no_published_card_holds_a_key_or_a_repository() -> None:
    for path in CARDS.rglob("*"):
        assert ".git" not in path.parts
        if path.is_file() and path.suffix in (".json", ".jsonl", ".txt"):
            assert "PRIVATE KEY" not in path.read_text(encoding="utf-8")
            assert "/tmp/" not in path.read_text(encoding="utf-8")
