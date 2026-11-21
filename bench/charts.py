"""Draw a benchmark results directory as charts, with the data behind them.

    python -m bench.charts RESULTS_DIR --out DIR

Writes each chart in `FIGURES` as `NAME.light.svg` and `NAME.dark.svg`, drawn by Plotly in its
built-in theme and default style (`bench/kit.py`), and beside them `runs.csv` and `runs.json`
(the standard record of each run, see `bench/record.py`), `series.json` (its series) and
`shapes.json` (what each run became), so the same data can be drawn another way. A chart sets
its data and its chart type and nothing else. Its heading, caption and conditions are written
beside it in Markdown by `bench/publish.py`.

Harnesses are listed in one order (`rows`): the subject first, then the harnesses that use a
model, then those that do not; Plotly's default colour sequence colours them in that order, so
the subject takes the first colour in every chart. Without Plotly and kaleido the data files are
still written and the charts already on disk are left as they are.
"""

from __future__ import annotations

import argparse
import csv
import json
import statistics
import sys
from dataclasses import dataclass, field
from pathlib import Path

from bench import kit, record, shape

LAYERS = ("task", "screen", "scaffold", "answer")  # where a call's text came from
SOURCES = {"task": "task", "screen": "screen", "scaffold": "scaffolding", "answer": "answer"}


@dataclass
class Run:
    """One run, as plain step-indexed series read from its standard record."""

    arm: str
    seed: int
    backend: str
    model: str
    scenario: str
    date: str
    budget_calls: int
    ending: str  # reached, lost, capped or broke
    turns: int
    value: float  # progress in the scenario's unit
    left: dict[int, float]  # step -> what is left to the goal, at the end of that step
    progress: dict  # the scenario's declaration: unit, goal, start, end, milestones
    row: dict  # the standard record, as written to runs.csv
    series: list[dict]
    calls: list[dict] = field(default_factory=list)  # step, bytes by layer, chars, tokens
    breaks: list[tuple[int, str]] = field(default_factory=list)
    proposed: list[tuple[int, str]] = field(default_factory=list)
    wall: float = 0.0
    tokens_known: bool = True
    kept: int | None = None  # pages a character wrote for itself, None when not counted
    folder: Path | None = None  # where the run's files are


def load_run(folder: Path) -> Run:
    standard = record.row(folder)
    steps = record.series(folder)
    made = [{**c, "turn": c["step"]} for c in record.calls(folder)]
    progress = record.scenario_config(standard["scenario"])["progress"]
    goal = progress["goal"]
    return Run(
        arm=standard["harness"],
        seed=standard["seed"],
        backend=standard["backend"],
        model=standard["model"],
        scenario=standard["scenario"],
        date=standard["date"],
        budget_calls=standard["budget_calls"],
        ending=standard["ending"],
        turns=standard["steps"],
        value=standard["value"],
        left={s["step"]: round(goal * (1 - s["progress"]), 6) for s in steps},
        progress=progress,
        row=standard,
        series=steps,
        calls=made,
        breaks=[(s["step"], rule) for s in steps for rule in s["violations"]],
        proposed=[(c["turn"], c["proposed"]) for c in made if c["proposed"]],
        wall=standard["wall_s"],
        tokens_known=all(c["tokens_known"] for c in made),
        kept=standard["kept"],
        folder=folder,
    )


def load(results: Path) -> list[Run]:
    return [load_run(p.parent) for p in sorted(results.rglob("run.json"))]


def by_arm(runs: list[Run]) -> dict[str, list[Run]]:
    arms: dict[str, list[Run]] = {}
    for run in runs:
        arms.setdefault(run.arm, []).append(run)
    return {arm: sorted(rs, key=lambda r: r.seed) for arm, rs in sorted(arms.items())}


def cumulative(run: Run, turn: int, key: str) -> float:
    """Total of a call measure over the calls made up to the end of this turn."""
    if key == "calls":
        return float(sum(1 for c in run.calls if c["turn"] <= turn))
    return float(sum(c[key] for c in run.calls if c["turn"] <= turn))


def band(runs: list[Run], value) -> list[tuple[int, float, float, float]]:
    """Per turn: (turn, median, lowest, highest) over the runs still going at that turn."""
    out = []
    for turn in range(max((r.turns for r in runs), default=0) + 1):
        values = [value(r, turn) for r in runs if turn <= r.turns]
        if values:
            out.append((turn, statistics.median(values), min(values), max(values)))
    return out


def total(run: Run, key: str) -> float:
    return float(sum(c[key] for c in run.calls))


def left_at(run: Run, turn: int) -> float:
    known = [t for t in run.left if t <= turn]
    return run.left[max(known)] if known else float(run.progress["goal"])


def arm_order(arms: dict[str, list[Run]]) -> list[str]:
    """Arms that use no model first, then the rest by name."""
    return sorted(arms, key=lambda a: (arms[a][0].model != "none", a))


# ---------------------------------------------------------------- drawing


def rows(arms: dict[str, list[Run]]) -> list[str]:
    """The one row order every chart uses: the subject, then the harnesses that use a model,
    then those that do not, each group by its label. A chart colours a harness by its place in
    this order, so the subject takes Plotly's first colour in every chart."""
    return sorted(
        arms,
        key=lambda a: (
            not record.manifest(a).get("accent"),
            arms[a][0].model == "none",
            record.label(a),
        ),
    )


def paid(arms: dict[str, list[Run]]) -> list[str]:
    """The rows of the harnesses that use a model, in the same order."""
    return [a for a in rows(arms) if arms[a][0].model != "none"]


def labels_of(arms: dict[str, list[Run]]) -> dict[str, str]:
    return {a: record.label(a) for a in arms}


def median_run(rs: list[Run], key) -> Run:
    """The run nearest the median on key, among those that reached the goal when any did."""
    pool = [r for r in rs if r.ending == "reached"] or rs
    middle = statistics.median(key(r) for r in pool)
    return min(pool, key=lambda r: (abs(key(r) - middle), r.seed))


def run_cost(rs: list[Run]) -> float:
    """The median dollars of the runs whose cost is known, or nothing."""
    known = [r.row["cost"] for r in rs if r.row["cost"] is not None]
    return statistics.median(known) if known else 0.0


def ends(run: Run) -> dict:
    """What a run had become when it stopped: everything it ended with, and what it kept."""
    found = {f["name"]: f["value"] for f in shape.shape(run.folder)["facts"]}
    if "pages at end" in found:
        return {"all": found["pages at end"], "own": found["pages it wrote"], "unit": "pages"}
    if "messages" in found:
        own = found.get("kept after it stops", 0)
        return {"all": found["messages"], "own": own, "unit": "messages"}
    return {"all": 0, "own": 0, "unit": ""}


def _figure(look: str, traces, height: int, **layout):
    """A figure on the look's theme, the traces in the colour order Plotly gives them."""
    import plotly.graph_objects as go

    fig = go.Figure(data=list(traces), layout={"template": kit.template(look)})
    return kit.finish(fig, height, **layout)


def _stacked(look, arms, order, parts: dict[str, dict[str, float]], kinds, axis, height):
    """Stacked horizontal bars, one a harness, a part of each kind, listed top to bottom."""
    import plotly.graph_objects as go

    names = labels_of(arms)
    bars = [
        go.Bar(name=k, x=[parts[a].get(k, 0) for a in order], y=[names[a] for a in order],
               orientation="h")
        for k in kinds
    ]  # fmt: skip
    fig = _figure(look, bars, height, barmode="stack", xaxis={"title": {"text": axis}})
    return fig.update_yaxes(autorange="reversed")


def draw_reached(runs: list[Run], look: str):
    """How far every run got: a bar a run, grouped by harness, and the goal as one line."""
    import plotly.graph_objects as go

    arms = by_arm(runs)
    p = runs[0].progress
    bars = [
        go.Bar(
            name=record.label(a),
            x=[r.value for r in arms[a]],
            y=[f"{record.label(a)} {r.seed}" for r in arms[a]],
            orientation="h",
        )
        for a in rows(arms)
    ]
    fig = _figure(look, bars, 90 + 17 * len(runs), xaxis={"title": {"text": p["unit"]}})
    fig.update_yaxes(autorange="reversed")
    return fig.add_vline(x=p["goal"], annotation_text=p["end"])


def draw_became(runs: list[Run], look: str):
    """What each harness's median run ended as: the parts it was handed and those it kept."""
    arms = by_arm(runs)
    order = rows(arms)
    end = {a: ends(median_run(arms[a], lambda r: r.row["chars"])) for a in order}
    parts = {
        a: {"handed to it": end[a]["all"] - end[a]["own"], "its own": end[a]["own"]} for a in order
    }
    unit = next((e["unit"] for e in end.values() if e["unit"]), "parts")
    return _stacked(
        look, arms, order, parts, ("handed to it", "its own"), f"{unit} at the end",
        120 + 40 * len(order),
    )  # fmt: skip


def draw_cost(runs: list[Run], look: str):
    """What each run cost against how far it got: a dot a run, a colour a harness that uses a
    model."""
    import plotly.graph_objects as go

    arms = by_arm(runs)
    p = runs[0].progress
    dots = [
        go.Scatter(
            name=record.label(a),
            mode="markers",
            x=[r.row["cost"] for r in arms[a] if r.row["cost"] is not None],
            y=[r.value for r in arms[a] if r.row["cost"] is not None],
        )
        for a in paid(arms)
    ]
    fig = _figure(
        look,
        dots,
        320,
        xaxis={"title": {"text": "dollars a run"}},
        yaxis={"title": {"text": p["unit"]}},
    )
    return fig.add_hline(y=p["goal"], annotation_text=p["end"])


def draw_text(runs: list[Run], look: str):
    """Where the text of each harness's median run came from, in characters."""
    arms = by_arm(runs)
    order = paid(arms)
    parts = {}
    for a in order:
        run = median_run(arms[a], lambda r: r.row["chars"])
        parts[a] = {SOURCES[k]: float(sum(c.get(k, 0) for c in run.calls)) for k in LAYERS}
    return _stacked(
        look, arms, order, parts, tuple(SOURCES.values()), "characters", 120 + 40 * len(order)
    )


def draw_time(runs: list[Run], look: str):
    """Where the time of each harness's median run went: in the model or in the harness."""
    arms = by_arm(runs)
    order = rows(arms)
    parts = {}
    for a in order:
        run = median_run(arms[a], lambda r: r.wall)
        model = run.row["model_s"] or 0.0
        parts[a] = {"in the model": model, "in the harness": max(run.wall - model, 0.0)}
    return _stacked(
        look, arms, order, parts, ("in the model", "in the harness"), "seconds",
        120 + 40 * len(order),
    )  # fmt: skip


def _lines(look, arms, order, value, axis, height):
    """A median line a harness against turn, stepped: a value holds until the next turn."""
    import plotly.graph_objects as go

    lines = []
    for a in order:
        found = band(arms[a], value)
        lines.append(
            go.Scatter(
                name=record.label(a),
                mode="lines",
                line_shape="hv",
                x=[t for t, *_ in found],
                y=[m for _, m, *_ in found],
            )
        )
    return _figure(
        look, lines, height, xaxis={"title": {"text": "turn"}}, yaxis={"title": {"text": axis}}
    )


def draw_progress(runs: list[Run], look: str):
    """What was left to the goal at each turn, the median over seeds, one line a harness."""
    arms = by_arm(runs)
    return _lines(look, arms, rows(arms), left_at, f"{runs[0].progress['unit']} left", 320)


def draw_spend(runs: list[Run], look: str):
    """Model calls made by each turn, the median over seeds, one line a harness that uses a
    model."""
    arms = by_arm(runs)
    return _lines(
        look, arms, paid(arms), lambda r, t: cumulative(r, t, "calls"), "model calls", 300
    )


def draw_rules(runs: list[Run], look: str):
    """The turn of each house rule broken in the game, a mark a break in a row a run; a breaking
    input a model proposed that never reached the game has its own mark. A run that broke
    nothing keeps its empty row."""
    import plotly.graph_objects as go

    arms = by_arm(runs)
    listed = [(a, r, f"{record.label(a)} {r.seed}") for a in rows(arms) for r in arms[a]]
    traces = [
        go.Scatter(
            name=record.label(a),
            mode="markers",
            x=[t for r in arms[a] for t, _ in r.breaks],
            y=[label for _, r, label in listed if r in arms[a] for _ in r.breaks],
        )
        for a in rows(arms)
    ]
    offered = [
        (t, label)
        for _, r, label in listed
        for t, rule in r.proposed
        if (t, rule) not in set(r.breaks)
    ]
    traces.append(
        go.Scatter(
            name="proposed, not played",
            mode="markers",
            marker_symbol="circle-open",
            x=[t for t, _ in offered],
            y=[label for _, label in offered],
        )
    )
    rowset = go.Scatter(x=[None] * len(listed), y=[label for *_, label in listed], showlegend=False)
    fig = _figure(
        look,
        [*traces, rowset],
        90 + 17 * len(listed),
        xaxis={"title": {"text": "turn"}},
        yaxis={"type": "category", "categoryorder": "array",
               "categoryarray": [label for *_, label in listed]},
    )  # fmt: skip
    return fig.update_yaxes(autorange="reversed")


FIGURES = {
    "reached": draw_reached,
    "became": draw_became,
    "cost": draw_cost,
    "time": draw_time,
    "text": draw_text,
    "progress": draw_progress,
    "spend": draw_spend,
    "rules": draw_rules,
}


def render(runs: list[Run], out: Path, kind: str = "runs") -> list[Path]:
    """Write every chart and the data behind them. kind names the set: pilot, result or runs.

    Without Plotly and kaleido only the data is written, the charts on disk are left alone, and
    a line on standard error says so."""
    out.mkdir(parents=True, exist_ok=True)
    written = []
    if kit.available():
        figures = {
            out / f"{chart}.{look}.svg": (draw(runs, look), f"{chart}-{look}")
            for chart, draw in FIGURES.items()
            for look in kit.LOOKS
        }
        written += kit.export(figures)
    else:
        print(
            "charts not drawn: Plotly and kaleido are not installed, so the charts already "
            "here are kept; install them with pip install -e '.[bench]'",
            file=sys.stderr,
        )
    written += export(runs, out)
    return written


def export(runs: list[Run], out: Path) -> list[Path]:
    """Write the standard rows as `runs.csv` and `runs.json`, their series as `series.json` and
    the shape of each run as `shapes.json`."""
    data = [r.row for r in sorted(runs, key=lambda r: (r.arm, r.seed))]
    table = out / "runs.csv"
    with table.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, record.KEYS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(data)
    tree = out / "runs.json"
    tree.write_text(json.dumps(data, indent=1) + "\n", encoding="utf-8")
    per = out / "series.json"
    per.write_text(
        json.dumps(
            [
                {"harness": r.arm, "seed": r.seed, "series": r.series}
                for r in sorted(runs, key=lambda r: (r.arm, r.seed))
            ],
            indent=1,
        )
        + "\n",
        encoding="utf-8",
    )
    shapes = out / "shapes.json"
    shapes.write_text(
        json.dumps(
            [shape.shape(r.folder) for r in sorted(runs, key=lambda r: (r.arm, r.seed))], indent=1
        )
        + "\n",
        encoding="utf-8",
    )
    return [table, tree, per, shapes]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="bench.charts", description=__doc__.split("\n")[0])
    parser.add_argument("results", type=Path, help="a results directory written by bench.run")
    parser.add_argument("--out", type=Path, required=True, help="where to write the SVG files")
    args = parser.parse_args(argv)
    runs = load(args.results)
    if not runs:
        print(
            f"no runs under {args.results}: run bench.run first, or point at its --out",
            file=sys.stderr,
        )
        return 1
    for path in render(runs, args.out):
        print(path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
