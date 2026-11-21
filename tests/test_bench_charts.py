"""The benchmark charts and the words beside them, from a tiny hand-made results directory.

A chart is checked as the figure Plotly is asked to draw (its data and layout), so these tests
need no browser; they skip where Plotly or the templates are missing. One test exports a
chart twice and compares the bytes, where kaleido is installed too.

No model and no game are run. The fixture has two arms: `loop` arrives in three turns with three
calls (one house rule broken on turn 1); `floor-random` makes no call, breaks the same rule on
turn 1 and dies.
"""

from __future__ import annotations

import json
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest
from bench import charts, kit, record

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


def drawn(runs, chart: str, look: str = "light") -> dict:
    """A chart's figure as plain data: what Plotly is asked to draw, without drawing it."""
    pytest.importorskip("plotly")
    pytest.importorskip("dash_bootstrap_templates")
    return charts.FIGURES[chart](runs, look).to_plotly_json()


def test_every_chart_is_drawn_in_the_installed_template_for_its_file(results: Path) -> None:
    import plotly.io as pio

    runs = charts.load(results)
    for chart in charts.FIGURES:
        for look in kit.LOOKS:
            layout = drawn(runs, chart, look)["layout"]
            theme = pio.templates[kit.THEMES[look]].layout
            made = layout["template"]["layout"]
            # the colours of the marks are the template's, and its layout
            assert made["colorway"] == list(theme.colorway)
            assert made["xaxis"]["gridwidth"] == theme.xaxis.gridwidth
            assert made["paper_bgcolor"] == made["plot_bgcolor"] == "rgba(0,0,0,0)"
            assert made["font"]["family"] == kit.TEXT
            assert "title" not in layout, f"{chart}: a title belongs in the Markdown"
    assert len({kit.THEMES[look] for look in kit.LOOKS}) == len(kit.LOOKS)


def named(tree, key: str) -> list:
    """Every value held under a key anywhere in a figure's plain data."""
    if isinstance(tree, dict):
        return [v for k, v in tree.items() if k == key] + [
            x for k, v in tree.items() if k != key for x in named(v, key)
        ]
    if isinstance(tree, list | tuple):
        return [x for v in tree for x in named(v, key)]
    return []


def test_words_and_rules_are_one_neutral_and_only_marks_carry_colour(results: Path) -> None:
    runs = charts.load(results)
    for chart in charts.FIGURES:
        for look in kit.LOOKS:
            fig = drawn(runs, chart, look)
            ink, rule = kit.INK[look], kit.RULE[look]
            made = fig["layout"].pop("template")["layout"]
            # every colour a word is given, anywhere in the template, is the look's ink
            words = [c for font in named(made, "font") for c in named(font, "color")]
            assert words and set(words) == {ink}, f"{chart}: a word in a colour"
            assert named(made["annotationdefaults"], "arrowcolor") == [ink]
            assert named(made["shapedefaults"], "color") == [ink]
            for axis in ("xaxis", "yaxis"):
                lines = [made[axis].get(k) for k in
                         ("gridcolor", "linecolor", "zerolinecolor", "tickcolor")]  # fmt: skip
                assert set(lines) == {rule}, f"{chart}: an axis line in a colour"
            # and the figure itself gives no word, line or shape a colour of its own
            assert not named(fig["layout"], "color") and not named(fig["layout"], "font")
            assert not [c for trace in fig["data"] for c in named(trace, "textfont")]
    assert kit.INK["light"] != kit.INK["dark"]


def test_a_chart_sets_no_colour_of_its_own(results: Path) -> None:
    runs = charts.load(results)
    for chart in charts.FIGURES:
        for look in kit.LOOKS:
            fig = drawn(runs, chart, look)
            for trace in fig["data"]:
                assert not named(trace, "color"), f"{chart}: a trace sets a colour"
                assert not named(trace, "pattern"), f"{chart}: a mark is not a plain fill"
                assert "line" not in trace.get("marker", {}), f"{chart}: a mark is outlined"
            assert "colorway" not in fig["layout"]
            bars = fig["layout"]["template"]["data"]["bar"]
            assert all(bar["marker"]["line"]["width"] == 0 for bar in bars)


def test_rows_keep_one_order_in_every_chart(results: Path) -> None:
    runs = charts.load(results)
    assert charts.rows(charts.by_arm(runs)) == ["loop", "floor-random"]
    became = drawn(runs, "became")
    assert list(became["data"][0]["y"]) == ["bare", "random"]
    assert became["layout"]["yaxis"]["autorange"] == "reversed"  # listed top to bottom


def test_reached_draws_a_bar_a_run_to_its_distance(results: Path) -> None:
    fig = drawn(charts.load(results), "reached")
    bars = {t["name"]: t["x"] for t in fig["data"]}
    assert list(bars["bare"]) == [2040.0]
    assert [t["y"][0] for t in fig["data"]] == ["bare 1", "random 1"]
    assert fig["layout"]["shapes"][0]["x0"] == 2040  # the goal, as one line


def test_time_splits_the_median_run_between_model_and_harness(results: Path) -> None:
    fig = drawn(charts.load(results), "time")
    parts = {t["name"]: list(t["x"]) for t in fig["data"] if t["name"]}
    assert set(parts) == {"in the model", "in the harness"}
    assert parts["in the harness"][1] == pytest.approx(30.0)  # random: no model, all harness


def test_text_stacks_each_source_of_the_median_run(results: Path) -> None:
    fig = drawn(charts.load(results), "text")
    parts = {t["name"]: list(t["x"]) for t in fig["data"] if t["name"]}
    assert parts["screen"][0] == 900.0  # 200 + 300 + 400 characters of screen
    assert parts["task"][0] == 300.0


def test_rules_marks_the_turn_of_each_break(results: Path) -> None:
    fig = drawn(charts.load(results), "rules")
    broken = fig["data"][0]
    assert [list(t["x"]) for t in fig["data"][:2]] == [[1], [1]]  # one in each arm, at turn 1
    assert list(broken["y"]) == ["bare 1"]


def test_proposals_that_did_not_reach_the_game_are_hollow(tmp_path: Path) -> None:
    root = build(tmp_path / "p", "scripted")
    meter = root / "trail" / "loop" / "full" / "seed-1" / "meter.jsonl"
    rows = [json.loads(x) for x in meter.read_text().splitlines()]
    rows[2]["note"] = {"proposed": "attack-friendly"}
    write(meter, rows)
    hollow = drawn(charts.load(root), "rules")["data"][-2]
    assert hollow["marker"]["symbol"] == "circle-open" and list(hollow["x"]) == [2]


def test_export_is_byte_stable(results: Path, tmp_path: Path) -> None:
    if not kit.available():
        pytest.skip("Plotly, kaleido and the templates are not installed")
    runs = charts.load(results)
    first, second = tmp_path / "a.svg", tmp_path / "b.svg"
    kit.export({first: (charts.draw_text(runs, "dark"), "text-dark")})
    kit.export({second: (charts.draw_text(runs, "dark"), "text-dark")})
    svg = parsed(first)
    assert first.read_bytes() == second.read_bytes()
    assert svg.count("font-family") == 1 and "<image" not in svg


def test_without_plotly_the_data_is_written_and_the_charts_left_alone(
    results: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys
) -> None:
    out = tmp_path / "svg"
    out.mkdir()
    (out / "reached.light.svg").write_text("<svg/>", encoding="utf-8")
    monkeypatch.setattr(kit, "available", lambda: False)
    written = charts.render(charts.load(results), out)
    assert sorted(p.name for p in written) == [
        "runs.csv",
        "runs.json",
        "series.json",
        "shapes.json",
    ]
    assert (out / "reached.light.svg").read_text() == "<svg/>"
    assert "charts not drawn" in capsys.readouterr().err
    table = (out / "runs.csv").read_text(encoding="utf-8").splitlines()
    assert table[0] == ",".join(record.KEYS)


def test_the_command_refuses_an_empty_directory(
    tmp_path: Path, capsys: pytest.CaptureFixture
) -> None:
    empty = tmp_path / "none"
    empty.mkdir()
    assert charts.main([str(empty), "--out", str(tmp_path / "charts")]) == 1
    assert "run bench.run first" in capsys.readouterr().err


def test_publishing_writes_the_page_the_data_and_the_readme_block_and_is_repeatable(
    results: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from bench import publish

    monkeypatch.setattr(kit, "available", lambda: False)  # the words, not the drawing
    root = tmp_path / "repo"
    (root / "docs" / "research").mkdir(parents=True)
    readme = root / "README.md"
    readme.write_text(f"before\n{publish.START}\nold\n{publish.END}\nafter\n", encoding="utf-8")
    written = publish.publish(results, "sample", "pilot", root)
    first = {p: p.read_bytes() for p in written}
    text = readme.read_text(encoding="utf-8")
    assert text.startswith("before\n") and text.endswith("\nafter\n") and "old" not in text
    assert "### Benchmark" in text and "docs/results/sample/reached.dark.svg" in text
    assert "scripted stand-in" in text and "none of it counts" in text
    block = text.split(publish.START)[1].split(publish.END)[0]
    for chart in publish.SHOWN:
        head = f"#### {publish.HEADS[chart]}"
        assert head in block, f"no heading for {chart}"
        after = block.split(head)[1].split("\n\n")
        assert f"{chart}.light.svg" in after[1], f"{chart}: the chart is not under its heading"
        assert after[2].endswith("a scripted stand-in, not a result."), f"{chart}: caption"
        assert not publish.HEADS[chart].startswith("The ")
    assert "| Harness | Version | Model | Reached | Cost | Model s | Own s | Score |" in block
    assert "scores.light.svg" not in block
    assert "<sub>[Method and every chart](docs/research/results.md)" in block
    page = (root / "docs" / "research" / "results.md").read_text(encoding="utf-8")
    assert page.startswith("---\nkind: research\n") and "status: draft" in page
    assert (root / "docs" / "results" / "sample" / "runs.csv").exists()
    assert "## Compared like for like" in page and "### Scores" in page
    publish.publish(results, "sample", "pilot", root)
    assert {p: p.read_bytes() for p in written} == first
    readme.write_text("no markers", encoding="utf-8")
    with pytest.raises(SystemExit, match="markers"):
        publish.publish(results, "sample", "pilot", root)


def test_each_caption_describes_what_its_chart_shows(results: Path) -> None:
    from bench import publish

    runs = charts.load(results)
    said = publish.captions("pilot", publish.facts(runs), runs)
    assert set(said) == set(charts.FIGURES) == {*publish.SHOWN, *publish.PAGE_ONLY}
    assert said["reached"].startswith("A bar a run, from ")
    assert said["cost"].startswith("Dollars a run at list price against ")
    assert (
        "a dot a run" in said["cost"]
        and publish.HEADS["cost"] == "What a run cost and how far it got"
    )
    assert "a run with no dot broke none" in said["rules"]
    assert said["time"].startswith("Seconds a median run") and "no bar" in said["text"]
    assert publish.ALT["became"].startswith("Stacked horizontal bars")
    assert publish.ALT["rules"].startswith("A row a run with a dot")


def test_a_result_is_refused_when_the_arms_are_not_comparable(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from bench import publish

    monkeypatch.setattr(kit, "available", lambda: False)
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
