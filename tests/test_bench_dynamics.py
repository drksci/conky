"""The trial pictures: a timeline read from a tiny vault, the D2 text made from it, and the
published records. No model is run: a vault is built by writes alone. D2 itself is used only
when a `d2` program is on the machine."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest
from bench import dynamics
from bench.timeline import classify, timeline

from conky import Vault
from conky.page import Page
from tests.test_pages import AT, w

ROOT = Path(__file__).resolve().parent.parent
CARDS = ROOT / "docs" / "results" / "cards"
META = {"card": "tiny"}
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


def test_the_d2_text_has_a_node_a_page_with_the_shape_of_its_archetype(tiny: Vault) -> None:
    events = timeline(tiny.pages_dir.parent)
    text = dynamics.topology(events, META)
    assert text == dynamics.topology(events, META)
    assert dynamics.dynamics(events, META) == dynamics.dynamics(events, META)
    assert 'keeper: "keeper  ·  character"' in text and 'helper: "helper  ·  provider"' in text
    assert 'payment-baker: "payment-baker  ·  page"' in text
    classes = dict(dynamics.SHAPES)
    assert classes["character"] == "person" and classes["provider"] == "hexagon"
    assert "person" in text
    moving = dynamics.dynamics(events, META)
    assert 'payment-baker: "payment-baker" {class: page' in moving
    assert "helper" not in moving.split("steps:")[0].split("classes:")[1]  # a provider is left out
    assert text.count("steps:") == 0 and moving.count("steps:") == 1


def test_every_panel_of_a_cell_appears_in_the_topology(tiny: Vault) -> None:
    text = dynamics.topology(timeline(tiny.pages_dir.parent), META)
    for panel in dynamics.PANELS:
        assert f"{panel}: " in text and "class: panel" in text
    assert text.count("class: panel") >= len(dynamics.PANELS)
    assert '"turned_away"' in text and '"each"' in text and '"asks"' in text
    assert "landlord-payment -> den" in text and "turned away" in text


def test_the_d2_text_uses_only_colours_that_are_tokens(tiny: Vault) -> None:
    events = timeline(tiny.pages_dir.parent)
    tokens = json.loads((ROOT / "src" / "conky" / "tokens.json").read_text())
    known = {
        value.lower()
        for group in ("color", "pen")
        for pair in tokens[group].values()
        for value in pair.values()
    }
    for text in (dynamics.topology(events, META), dynamics.dynamics(events, META)):
        used = set(re.findall(r"#[0-9a-f]{6}\b", text.lower()))
        assert used and used <= known


def d2() -> str | None:
    return dynamics.d2_binary()


@pytest.mark.skipif(d2() is None, reason="no d2 program on this machine")
def test_the_d2_text_compiles_and_the_steps_animate(tiny: Vault, tmp_path: Path) -> None:
    events = timeline(tiny.pages_dir.parent)
    for name, flags in (("dynamics", ["--animate-interval", "1000"]), ("topology", [])):
        source = tmp_path / f"{name}.d2"
        source.write_text(getattr(dynamics, name)(events, META), encoding="utf-8")
        target = tmp_path / f"{name}.svg"
        done = subprocess.run(
            [d2() or "", *flags, str(source), str(target)], capture_output=True, text=True
        )
        assert done.returncode == 0, done.stderr
        assert target.read_text().startswith("<?xml") or "<svg" in target.read_text()
    assert "d2Transition" in (tmp_path / "dynamics.svg").read_text()


def test_publishing_writes_the_records_the_board_and_the_block(
    tiny: Vault, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture
) -> None:
    monkeypatch.setattr(dynamics, "d2_binary", lambda: None)
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
    assert "no d2 found" in capsys.readouterr().err
    assert sorted(p.name for p in folder.iterdir()) == [
        "dynamics.d2", "observations.jsonl", "rows.jsonl", "run.json", "timeline.json",
        "topology.d2", "verdict.txt",
    ]  # fmt: skip
    assert "/private" not in (folder / "rows.jsonl").read_text()
    dynamics.refresh(root)
    first = (readme.read_bytes(), (root / dynamics.BOARD).read_bytes())
    assert readme.read_text().startswith("top\n") and "old" not in readme.read_text()
    board = (root / dynamics.BOARD).read_text()
    assert "met" in board and "not drawn" in board and "topology.svg" in board
    dynamics.refresh(root)
    assert (readme.read_bytes(), (root / dynamics.BOARD).read_bytes()) == first


def test_the_readme_block_and_the_board_are_what_publishing_writes() -> None:
    text = (ROOT / "README.md").read_text(encoding="utf-8")
    head = text.split(dynamics.START, 1)[1].split(dynamics.END, 1)[0]
    assert dynamics.START + head + dynamics.END == dynamics.block(ROOT)
    assert (ROOT / dynamics.BOARD).read_text(encoding="utf-8") == dynamics.board(ROOT)
    assert text.count("dynamics.svg") == 3


def test_the_crowded_desk_shows_the_notes_the_prompt_showed() -> None:
    events = json.loads((CARDS / "a-clerk-reads-a-crowded-desk" / "timeline.json").read_text())["1"]
    answers = [e for e in events if e["answered"]]
    assert len(answers[-1]["shown"]) == 8 and "note-07" in answers[-1]["shown"]
    text = dynamics.dynamics(events, META)
    assert (
        "grid-columns: 10" in text
        and text.count(f"note-07.style.stroke-width: {dynamics.WEIGHT_OF['bold']}") == 1
    )


def test_no_published_card_holds_a_key_or_a_repository() -> None:
    for path in CARDS.rglob("*"):
        assert ".git" not in path.parts
        if path.is_file() and path.suffix != ".svg":
            assert "PRIVATE KEY" not in path.read_text(encoding="utf-8")
            assert "/tmp/" not in path.read_text(encoding="utf-8")
