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
    kinds = {n["id"]: n["header"]["kinds"] for n in g["nodes"]}
    assert kinds["den"] == ["space"] and kinds["keeper"] == ["character"]
    assert kinds["helper"] == ["provider"] and kinds["payment-baker"] == ["page"]
    parents = {n["id"]: n["parent"] for n in g["nodes"]}
    assert parents["keeper"] == "den" and parents["payment-baker"] == "den"


def test_every_panel_kind_appears_and_edges_run_between_sockets(tiny: Vault) -> None:
    g = tiny_graph(tiny)
    panels = {p["kind"] for n in g["nodes"] for p in n["panels"]}
    assert panels == {"text", "holds", "bound", "when"}
    sockets = {s["id"]: s for n in g["nodes"] for s in n["sockets"]}
    kinds = {e["kind"] for e in g["edges"]}
    assert {"turned-away", "asks", "heard"} <= kinds
    for e in g["edges"]:  # socket to socket, output to input, one kind of signal
        a, b = sockets[e["sourceSocket"]], sockets[e["targetSocket"]]
        assert a["kind"] == b["kind"] == e["signal"] and a["plugged"] and b["plugged"]
        assert a["side"] in ("EAST", "SOUTH") and b["side"] == "WEST"
    for n in g["nodes"]:  # sockets in the one fixed order: west, east, south, each by the table
        order = [(dynamics.SIDES.index(s["side"]),
                  dynamics.SOCKET_ORDER[s["side"]].index(s["kind"]))
                 for s in n["sockets"]]  # fmt: skip
        assert order == sorted(order) and [s["order"] for s in n["sockets"]] == list(
            range(len(order))
        )
        for p in n["panels"]:
            if p["kind"] == "bound":  # every expression carries its body, lines and names read
                assert all(r["expr"]["lines"] and r["expr"]["reads"] == ["page", "space"]
                           for r in p["rows"])  # fmt: skip
    den = next(n for n in g["nodes"] if n["id"] == "den")
    slots = {s["slot"]: s for s in den["footer"]["slots"]}
    assert slots["hands"]["filled"] and slots["shows"]["filled"] and den["footer"]["members"]
    keeper = next(n for n in g["nodes"] if n["id"] == "keeper")
    assert [s["slot"] for s in keeper["footer"]["slots"]] == ["asks", "writes"]
    payment = next(n for n in g["nodes"] if n["id"] == "payment-baker")
    handed = [r for p in payment["panels"] if p["kind"] == "bound" for r in p["rows"]]
    assert [r["from"] for r in handed] == ["den"]  # the rule den hands down, said to come from den


def test_an_empty_slot_is_hollow_and_a_self_watch_is_said_plainly(vault: Vault) -> None:
    ask = {"on": "clerk", "when": "page.heard != ''", "ask": {"prompt": "p", "into": "said"}}
    w(vault, "clerk", {"heard": "", "watch": [ask]})
    g = dynamics.graph(timeline(vault.pages_dir.parent), "self", 1)
    clerk = g["nodes"][0]
    slots = {s["slot"]: s for s in clerk["footer"]["slots"]}
    assert not slots["asks"]["filled"] and g["values"][slots["asks"]["id"]] == "default provider"
    assert not slots["writes"]["filled"]
    when = next(p for p in clerk["panels"] if p["kind"] == "when")["rows"][0]
    assert when["when"] == "its own page changing"
    assert when["then"] == [{"words": "asks the default provider, puts the answer in said",
                             "expr": None}]  # fmt: skip


def test_steps_reference_only_what_exists_and_pens_mean_something(tiny: Vault) -> None:
    g = tiny_graph(tiny)
    ids = {n["id"] for n in g["nodes"]} | {e["id"] for e in g["edges"]}
    ids |= {s["id"] for n in g["nodes"] for s in n["sockets"]}
    ids |= {s["id"] for n in g["nodes"] for s in n["footer"]["slots"]}
    for n in g["nodes"]:
        for p in n["panels"]:
            ids |= {p["id"]} if p["kind"] == "text" else {r["id"] for r in p["rows"]}
            ids |= {r["id"] for r in p.get("record", [])}
    for step in g["steps"]:
        assert set(step["appear"]) <= ids and set(step["dim"]) <= ids
        assert {c["id"] for c in step["change"]} <= set(g["values"])
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
    assert refused["words"] == ("landlord-payment is turned away: it breaks a rule den hands down.")


def test_every_symbol_named_is_in_the_one_table(tiny: Vault) -> None:
    g = tiny_graph(tiny)
    named = {n["header"]["symbol"] for n in g["nodes"]} | {s["symbol"] for s in g["steps"]}
    named |= {k for n in g["nodes"] for k in n["header"]["kinds"]}
    archetypes = {"character", "provider", "measure", "reflex", "screen", "hands", "page"}
    known = set(TOKENS["symbol"])
    assert named <= known and archetypes <= known
    assert set(dynamics.STEP_SYMBOL.values()) <= known
    sockets = {s["kind"] for n in g["nodes"] for s in n["sockets"]}
    assert sockets <= set(TOKENS["socket"]) and set(TOKENS["socket"]) == {
        k for side in TOKENS["socket_order"].values() for k in side
    }  # every kind of socket has its place in the order, and nothing else has
    marks = [v["mark"] for v in TOKENS["socket"].values()]
    assert len(set(marks)) == len(marks)  # one mark a kind, never two kinds alike


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
    assert kept == ["note-07"] and len(last["dim"]) == 32  # the note the answer was found in
    regions = {r["kind"]: r for r in g["arrangements"][last["arrangement"]]}
    assert len(regions["shown"]["members"]) == 8 and len(regions["hidden"]["members"]) == 32
    assert "note-07" in regions["shown"]["members"]
    beats = [s for s in g["steps"] if s["kind"] == "answer"]
    assert len(beats) == 2 and len(g["arrangements"]) == 3  # the desk, then one a question
    bulk = [s for s in g["steps"] if s["kind"] == "bulk"]
    assert bulk and all(2 <= len([a for a in s["appear"] if a.startswith("note-")
                                  and "/" not in a and "#" not in a]) <= dynamics.CHUNK
                        for s in bulk)  # fmt: skip


def complete(events: list[dict], g: dict) -> None:
    """Every top-level field of every page is drawn where it belongs (header, a panel, the
    footer) or is bookkeeping the runtime keeps (`dynamics.bookkeeping`); every rule and watch
    entry is a row; every provider and space a watch entry names is a footer slot; the body is
    the text panel, or a crowded note's line; every commit is part of a step."""
    last = {e["page"]: e["state"] for e in events if e["state"]}
    nodes = {n["id"]: n for n in g["nodes"]}
    for page, state in last.items():
        node, whole = nodes[page], dynamics.full(state)
        panels = {p["kind"]: p for p in node["panels"]}

        def rows(kind: str, panels: dict = panels) -> list[dict]:
            return panels[kind]["rows"] if kind in panels else []

        slots = {(s["slot"], g["values"][s["id"]]) for s in node["footer"]["slots"]}
        drawn = {r["name"] for r in rows("holds")}
        more = panels["holds"]["more"] if "holds" in panels else 0
        missing = []
        for key, value in whole.fields.items():
            if key == "avatar":
                assert node["header"]["avatar"] == str(value)
            elif key == "known_as":
                assert node["header"]["known_as"] == [str(v) for v in value]
            elif key == "shows":
                assert any(s["slot"] == "shows" and s["filled"] for s in node["footer"]["slots"])
            elif not dynamics.bookkeeping(key) and key not in drawn:
                missing.append(key)
        assert len(missing) <= more, f"{page}: {missing} are not in its cell"
        assert node["header"]["within"] == state["within"]
        own = [r for r in rows("bound") if not r["from"]]
        assert len(own) == len(whole.rules) and len(rows("when")) == len(whole.watch)
        for entry in state["watch"]:
            if entry["asks"]:
                assert ("asks", entry["provider"] or "default provider") in slots
                assert ("writes", entry["writes"] or "no space named") in slots
        if node["form"] == "note":
            assert node["header"]["line"] == dynamics.plain(
                whole.body.strip().splitlines()[0], dynamics.NOTE_WIDTH
            )
        elif whole.body.strip():
            assert panels["text"]["body"] == whole.body.strip()
        assert node["versions"][-1]["source"] == state["source"]
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
