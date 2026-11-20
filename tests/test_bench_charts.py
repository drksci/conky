"""The benchmark charts, from a tiny hand-made results directory with known numbers.

No model and no game are run. The fixture has two arms: `loop` arrives in three turns with three
calls (one house rule broken on turn 1); `floor-random` makes no call, breaks the same rule on
turn 1 and dies.
"""

from __future__ import annotations

import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest
from bench import charts, record

HEADER = "FOOD, BULLETS, CLOTHING, SUPPLIES, CASH\n 100 50 50 50 100\n"
ACTION = "DO YOU WANT TO (1) HUNT, (2) CONTINUE"
EAT = "DO YOU WANT TO EAT (1) POORLY (2) MODERATELY (3) WELL"


def write(path: Path, rows: list[dict]) -> None:
    path.write_text("\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")


def make_run(root: Path, arm: str, events: list[dict], calls: list[dict], backend: str) -> None:
    folder = root / "trail" / arm / "full" / "seed-1"
    folder.mkdir(parents=True)
    record = {
        "scenario": "trail",
        "arm": arm,
        "seed": 1,
        "model": "stand-in",
        "backend": backend,
        "budget": {"calls": 10, "tokens": 1000},
        "start": "2026-11-20T10:00:00Z",
        "exit": "game-ended",
        "segments": [{"start": 100.0, "end": 130.0}],
    }
    (folder / "run.json").write_text(json.dumps(record), encoding="utf-8")
    write(folder / "transcript.jsonl", events)
    if calls:
        write(folder / "meter.jsonl", calls)


def out(text: str, t: float) -> dict:
    return {"t": t, "kind": "out", "text": text}


def typed(n: int, line: str, t: float) -> dict:
    return {"t": t, "kind": "in", "n": n, "line": line, "prompt": ""}


def call(n: int, t: float, screen: int) -> dict:
    return {
        "n": n, "t_start": t, "status": 200, "pack_bytes": 100, "screen_bytes": screen,
        "scaffold_bytes": 50, "image_bytes": 0, "chars_in": 1000, "chars_out": 3,
        "tokens_in": 10, "tokens_out": 2, "tokens_known": True, "note": {},
    }  # fmt: skip


@pytest.fixture
def results(tmp_path: Path) -> Path:
    return build(tmp_path / "scripted", "scripted")


def build(root: Path, backend: str) -> Path:
    make_run(
        root,
        "loop",
        [
            out(HEADER + "MONDAY APRIL 12 1847\nTOTAL MILEAGE IS 0\n" + ACTION, 99.0),
            typed(1, "2", 100.0),
            out("\n" + EAT, 101.0),
            typed(2, "1", 110.0),
            out("\nMONDAY APRIL 26 1847\nTOTAL MILEAGE IS 300\n" + ACTION, 111.0),
            typed(3, "2", 120.0),
            out("\nMONDAY MAY 10 1847\nTOTAL MILEAGE IS 2040\n", 121.0),
            out("YOU FINALLY ARRIVED AT OREGON CITY\n", 121.5),
            {"t": 122.0, "kind": "end", "outcome": "ended"},
        ],
        [call(1, 99.9, 200), call(2, 109.9, 300), call(3, 119.9, 400)],
        backend,
    )  # fmt: skip
    make_run(
        root,
        "floor-random",
        [
            out(HEADER + "MONDAY APRIL 12 1847\nTOTAL MILEAGE IS 0\n" + EAT, 99.0),
            typed(1, "1", 100.0),
            out("\nYOU DIED OF PNEUMONIA\n", 101.0),
            {"t": 102.0, "kind": "end", "outcome": "ended"},
        ],
        [],
        backend,
    )
    return root


def parsed(svg: Path) -> str:
    ET.parse(svg)
    return svg.read_text(encoding="utf-8")


def test_load_reads_plain_series(results: Path) -> None:
    arms = charts.by_arm(charts.load(results))
    assert list(arms) == ["floor-random", "loop"]
    loop = arms["loop"][0]
    assert (loop.ending, loop.turns, loop.value) == ("reached", 3, 2040.0)
    assert loop.left == {1: 2040.0, 2: 1740.0, 3: 0.0}
    assert [c["turn"] for c in loop.calls] == [1, 1, 2]
    assert [c["screen"] for c in loop.calls] == [200, 300, 400]
    assert charts.cumulative(loop, 1, "calls") == 2.0
    assert charts.cumulative(loop, 3, "tokens") == 36.0
    assert loop.breaks == [(1, "eat-poorly")]
    assert loop.wall == 30.0
    dead = arms["floor-random"][0]
    assert (dead.ending, dead.turns, dead.calls, dead.breaks) == (
        "lost",
        1,
        [],
        [(1, "eat-poorly")],
    )


def test_every_chart_renders_light_and_dark(results: Path, tmp_path: Path) -> None:
    written = charts.render(charts.load(results), tmp_path / "svg")
    drawn = [p for p in written if p.suffix == ".svg"]
    assert sorted(p.name for p in drawn) == sorted(
        f"{name}.{look}.svg" for name in charts.CHARTS for look in ("light", "dark")
    )
    assert sorted(p.name for p in written if p not in drawn) == [
        "runs.csv",
        "runs.json",
        "series.json",
    ]
    table = (tmp_path / "svg" / "runs.csv").read_text(encoding="utf-8").splitlines()
    assert table[0] == ",".join(record.KEYS)
    assert len(table) == 1 + len(charts.load(results))
    for path in drawn:
        svg = parsed(path)
        assert "SCRIPTED: NOT A RESULT" in svg
        assert "trail / model stand-in / seeds 1 / 2026-11-20" in svg
        ink = charts.INKS["light" if ".light." in path.name else "dark"]
        assert ink in svg
    assert charts.INKS == {"light": "#1E1E1E", "dark": "#EDEDED"}


def test_a_real_backend_is_labelled_data(tmp_path: Path) -> None:
    runs = charts.load(build(tmp_path / "live", "conky-model"))
    svg = charts.draw_board(runs, "#1E1E1E").svg("t")
    assert ">DATA<" in svg and "NOT A RESULT" not in svg


def test_progress_puts_the_median_where_the_miles_are(results: Path, tmp_path: Path) -> None:
    svg = charts.draw_progress(charts.load(results), "#1E1E1E").svg("t")
    # turn 2 of 3 on a 70..690 axis, 1740 of 2040 miles left on a 280..78 axis
    assert "483.3,107.7" in svg
    assert "loop 1/1 arrived" in svg and "floor-random 0/1 arrived" in svg


def test_spend_counts_calls_against_the_budget(results: Path) -> None:
    svg = charts.draw_spend(charts.load(results), "#1E1E1E").svg("t")
    assert "BUDGET 10 (OFF SCALE)" in svg  # ten calls allowed, three made
    assert "690.0,144.8" in svg  # three calls at the last turn, axis top 5
    assert "loop 3" in svg


def test_where_stacks_the_bytes_of_the_first_call(results: Path) -> None:
    svg = charts.draw_where(charts.load(results), "#1E1E1E").svg("t")
    # task text 100 bytes on a 1000 byte axis over 228 units, in the second panel
    assert 'x="416.0" y="287.2" width="107.2" height="22.8"' in svg
    assert "NO MODEL CALLS" in svg


def test_rules_marks_the_turn_of_each_break(results: Path) -> None:
    svg = charts.draw_rules(charts.load(results), "#1E1E1E").svg("t")
    filled = re.findall(r'<rect x="385\.2"[^>]*fill="#F4C430"', svg)
    assert len(filled) == 2  # one in each arm, turn 1 of 3 on a 200..760 axis
    assert "1 broken" in svg


def test_proposals_that_did_not_reach_the_game_are_hollow(tmp_path: Path) -> None:
    root = build(tmp_path / "p", "scripted")
    meter = root / "trail" / "loop" / "full" / "seed-1" / "meter.jsonl"
    rows = [json.loads(x) for x in meter.read_text().splitlines()]
    rows[2]["note"] = {"proposed": "attack-friendly"}
    write(meter, rows)
    svg = charts.draw_rules(charts.load(root), "#1E1E1E").svg("t")
    assert re.search(r'fill="none"[^>]*stroke="#F4C430"', svg)


def test_board_places_the_dot_on_its_own_scale(results: Path) -> None:
    svg = charts.draw_board(charts.load(results), "#1E1E1E").svg("t")
    # calls column: loop made 3, the column's top; second row
    assert 'cx="523.7" cy="138.0"' in svg
    assert "3 OF 3" not in svg and "1 OF 1" in svg


def test_the_command_writes_every_chart_and_refuses_an_empty_directory(
    results: Path, tmp_path: Path, capsys: pytest.CaptureFixture
) -> None:
    out_dir = tmp_path / "charts"
    assert charts.main([str(results), "--out", str(out_dir)]) == 0
    assert len(list(out_dir.glob("*.svg"))) == 2 * len(charts.CHARTS)
    empty = tmp_path / "none"
    empty.mkdir()
    assert charts.main([str(empty), "--out", str(out_dir)]) == 1
    assert "run bench.run first" in capsys.readouterr().err


def test_publishing_writes_the_page_the_data_and_the_readme_block_and_is_repeatable(
    results: Path, tmp_path: Path
) -> None:
    from bench import publish

    root = tmp_path / "repo"
    (root / "docs" / "research").mkdir(parents=True)
    readme = root / "README.md"
    readme.write_text(f"before\n{publish.START}\nold\n{publish.END}\nafter\n", encoding="utf-8")
    written = publish.publish(results, "sample", "pilot", root)
    first = {p: p.read_bytes() for p in written}
    text = readme.read_text(encoding="utf-8")
    assert text.startswith("before\n") and text.endswith("\nafter\n") and "old" not in text
    assert "### Benchmark" in text and "docs/results/sample/trail.dark.svg" in text
    assert "scripted stand-in" in text and "none of it counts" in text
    page = (root / "docs" / "research" / "results.md").read_text(encoding="utf-8")
    assert page.startswith("---\nkind: research\n") and "status: draft" in page
    assert (root / "docs" / "results" / "sample" / "runs.csv").exists()
    assert "## Compared like for like" in page and "Model `stand-in`, commit unknown." in text
    publish.publish(results, "sample", "pilot", root)
    assert {p: p.read_bytes() for p in written} == first
    readme.write_text("no markers", encoding="utf-8")
    with pytest.raises(SystemExit, match="markers"):
        publish.publish(results, "sample", "pilot", root)


def test_a_result_is_refused_when_the_arms_are_not_comparable(tmp_path: Path) -> None:
    from bench import publish

    root = build(tmp_path / "mixed", "scripted")
    meta = root / "trail" / "loop" / "full" / "seed-1" / "run.json"
    record_ = json.loads(meta.read_text())
    record_["model"] = "other"
    meta.write_text(json.dumps(record_), encoding="utf-8")
    repo = tmp_path / "repo"
    (repo / "docs" / "research").mkdir(parents=True)
    (repo / "README.md").write_text(f"{publish.START}\n{publish.END}\n", encoding="utf-8")
    with pytest.raises(SystemExit, match="different ones"):
        publish.publish(root, "mixed", "result", repo)
    publish.publish(root, "mixed", "pilot", repo)
    assert "not comparable" in (repo / "docs" / "research" / "results.md").read_text()
