"""Draw a benchmark results directory as charts, with the data behind them.

    python -m bench.charts RESULTS_DIR --out DIR

Writes each chart in `FIGURES` as `NAME.light.svg` and `NAME.dark.svg`, drawn by Plotly from the
one template in `bench/kit.py`, and beside them `runs.csv` and `runs.json` (the standard record of
each run, see `bench/record.py`), `series.json` (its series) and `shapes.json` (what each run
became), so the same data can be drawn another way. A chart carries only what must sit on its
marks: row labels, a few direct values and a small legend. Its heading, caption and conditions
are written beside it in Markdown by `bench/publish.py`.

Every chart has one row a harness, in the same order (`rows`): the subject first, then the
harnesses that use a model, then those that do not. Without Plotly and kaleido the data files are
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
    then those that do not, each group by its label."""
    return sorted(
        arms,
        key=lambda a: (
            not record.manifest(a).get("accent"),
            arms[a][0].model == "none",
            record.label(a),
        ),
    )


def subject(arm: str) -> bool:
    return bool(record.manifest(arm).get("accent"))


def name(arm: str) -> str:
    """A row label: the harness's name, bold for the subject."""
    return f"<b>{record.label(arm)}</b>" if subject(arm) else record.label(arm)


def median_run(rs: list[Run], key) -> Run:
    """The run nearest the median on key, among those that reached the goal when any did."""
    pool = [r for r in rs if r.ending == "reached"] or rs
    middle = statistics.median(key(r) for r in pool)
    return min(pool, key=lambda r: (abs(key(r) - middle), r.seed))


def short(number: float) -> str:
    return f"{number / 1000:,.0f}k" if number >= 1000 else f"{number:,.0f}"


def _height(n: int, each: float, extra: float = 0) -> int:
    return round(n * each + extra + 12)


def _hbar(look, label, values, ys, role, text=None, **extra):
    import plotly.graph_objects as go

    return go.Bar(
        name=label,
        # An empty segment draws nothing, not a stray outline; a label rides on an empty one.
        x=values if text else [v or None for v in values],
        y=ys,
        orientation="h",
        marker=kit.fill(role, look),
        text=text,
        textposition="outside",
        cliponaxis=False,
        outsidetextfont={"size": kit.FONT, "color": kit.palette(look)["ink"]},
        hoverinfo="skip",
        **extra,
    )


def _rows_axis(order: list[str]) -> dict:
    """A category axis that lists the rows top to bottom."""
    return {
        "type": "category",
        "categoryorder": "array",
        "categoryarray": [name(a) for a in reversed(order)],
    }


def draw_reached(runs: list[Run], look: str):
    """How far every run got: one row a harness, a thin bar a run, the goal as one line."""
    arms = by_arm(runs)
    order = rows(arms)
    goal = runs[0].progress["goal"]
    seeds = max(len(rs) for rs in arms.values())
    lane = seeds + 2
    traces, ticks, words = [], [], []
    for i, arm in enumerate(order):
        rs = arms[arm]
        ys = [-(i * lane + k) for k in range(len(rs))]
        traces.append(
            _hbar(
                look,
                record.label(arm),
                [max(r.value, goal * 0.004) for r in rs],
                ys,
                "subject" if subject(arm) else "other",
                width=0.62,
            )
        )
        ticks.append(-(i * lane + (len(rs) - 1) / 2))
        words.append(name(arm))
    c = kit.palette(look)
    notes = [
        {
            "x": 1.0,
            "xref": "paper",
            "xanchor": "left",
            "y": tick,
            "text": f"{sum(r.ending == 'reached' for r in arms[arm])} of {len(arms[arm])}",
            "showarrow": False,
            "font": {"size": kit.FONT, "color": c["ink"]},
        }
        for tick, arm in zip(ticks, order, strict=True)
    ]
    end = runs[0].progress
    return kit.figure(
        look,
        *traces,
        height=_height(len(order) * lane, 9.5, 30),
        barmode="overlay",
        xaxis={
            "range": [0, goal],
            "tickvals": [0, goal],
            "ticktext": [end["start"], end["end"]],
        },
        yaxis={"tickvals": ticks, "ticktext": words, "range": [-(len(order) * lane - 1.2), 0.8]},
        shapes=[
            {
                "type": "line",
                "x0": goal,
                "x1": goal,
                "y0": 0,
                "y1": 1,
                "yref": "paper",
                "line": {"color": c["ink"], "width": 1},
            }
        ],
        annotations=notes,
        margin={"l": 4, "r": 56, "t": 4, "b": 4, "pad": 6},
    )


def ends(run: Run) -> dict:
    """What a run had become when it stopped: everything it ended with, and what it kept."""
    found = {f["name"]: f["value"] for f in shape.shape(run.folder)["facts"]}
    if "pages at end" in found:
        return {"all": found["pages at end"], "own": found["pages it wrote"], "unit": "pages"}
    if "messages" in found:
        own = found.get("kept after it stops", 0)
        return {"all": found["messages"], "own": own, "unit": "messages"}
    return {"all": 0, "own": 0, "unit": ""}


def draw_became(runs: list[Run], look: str):
    """What each harness's median run ended as: the parts it was handed and those it kept."""
    arms = by_arm(runs)
    order = rows(arms)
    end = {a: ends(median_run(arms[a], lambda r: r.row["chars"])) for a in order}
    given = [end[a]["all"] - end[a]["own"] for a in order]
    own = [end[a]["own"] for a in order]
    ys = [name(a) for a in order]
    words = []
    for a in order:
        e = end[a]
        if not e["unit"]:
            words.append("nothing")
        elif not e["all"]:
            words.append("not recorded")
        else:
            words.append(f"{e['all']} {e['unit']}, {e['own'] or 'none'} its own")
    kept = [
        _hbar(look, "its own", [o], [y], "subject" if subject(a) else "harness")
        for a, o, y in zip(order, own, ys, strict=True)
    ]
    marks = _hbar(look, "handed to it", given, ys, "other")
    tail = _hbar(look, "", [0] * len(order), ys, "idle", text=words)
    tail.marker.line.width = 0
    return kit.figure(
        look,
        marks,
        *kept,
        tail,
        height=_height(len(order), 30, 8),
        yaxis=_rows_axis(order),
        xaxis={"visible": False, "range": [0, max(e["all"] for e in end.values()) * 1.35 or 1]},
    )


def run_cost(rs: list[Run]) -> float:
    """The median dollars of the runs whose cost is known, or nothing."""
    known = [r.row["cost"] for r in rs if r.row["cost"] is not None]
    return statistics.median(known) if known else 0.0


def draw_cost(runs: list[Run], look: str):
    """What the median run cost, in dollars at list price: one row a harness that uses a model."""
    arms = by_arm(runs)
    order = [a for a in rows(arms) if arms[a][0].model != "none"]
    ys = [name(a) for a in order]
    medians = [run_cost(arms[a]) for a in order]
    bars = [
        _hbar(
            look,
            record.label(a),
            [m],
            [y],
            "subject" if subject(a) else "other",
            text=[f"${m:.4f}"],
        )  # fmt: skip
        for a, m, y in zip(order, medians, ys, strict=True)
    ]
    most = max(medians, default=0) or 1
    return kit.figure(
        look,
        *bars,
        height=_height(len(order), 34, 8),
        yaxis=_rows_axis(order),
        xaxis={"visible": False, "range": [0, most * 1.25]},
    )


def _parts(look, order, totals: dict[str, dict[str, float]], kinds, words, unit):
    """One stacked bar a harness, a segment a kind, its total written at the end."""
    ys = [name(a) for a in order]
    traces = [
        _hbar(look, words[k], [totals[a].get(k, 0) for a in order], ys, k, legendrank=n)
        for n, k in enumerate(kinds)
    ]
    whole = [sum(totals[a].values()) for a in order]
    tail = _hbar(
        look,
        "",
        [0] * len(order),
        ys,
        "idle",
        text=[f"{short(w)} {unit}" if w else "not recorded" for w in whole],
        showlegend=False,
    )
    tail.marker.line.width = 0
    return kit.figure(
        look,
        *traces,
        tail,
        height=_height(len(order), 34, 34),
        showlegend=True,
        yaxis=_rows_axis(order),
        xaxis={"visible": False, "range": [0, max(whole, default=1) * 1.2 or 1]},
        margin={"l": 4, "r": 4, "t": 30, "b": 4, "pad": 6},
    )


def draw_text(runs: list[Run], look: str):
    """Where the text of each harness's median run came from, in characters."""
    arms = by_arm(runs)
    order = [a for a in rows(arms) if arms[a][0].model != "none"]
    totals = {}
    for a in order:
        run = median_run(arms[a], lambda r: r.row["chars"])
        totals[a] = {k: float(sum(c.get(k, 0) for c in run.calls)) for k in LAYERS}
    return _parts(look, order, totals, LAYERS, SOURCES, "characters")


def draw_time(runs: list[Run], look: str):
    """Where the time of each harness's median run went: in the model or in the harness."""
    arms = by_arm(runs)
    order = rows(arms)
    totals = {}
    for a in order:
        run = median_run(arms[a], lambda r: r.wall)
        model = run.row["model_s"] or 0.0
        totals[a] = {"model": model, "harness": max(run.wall - model, 0.0)}
    words = {"model": "in the model", "harness": "in the harness"}
    return _parts(look, order, totals, ("model", "harness"), words, "seconds")


DASHES = ("solid", "dot", "dash", "longdash", "dashdot")


def _lines(look, arms, order, value, top):
    """A median line an arm against turn: the subject in its colour, the rest in ink, dashed."""
    import plotly.graph_objects as go

    c = kit.palette(look)
    traces = []
    for n, a in enumerate(order):
        rows_ = band(arms[a], value)
        traces.append(
            go.Scatter(
                name=record.label(a),
                x=[t for t, *_ in rows_],
                y=[m for _, m, *_ in rows_],
                mode="lines",
                line={
                    "color": c["subject"] if subject(a) else c["ink"],
                    "width": 2.4 if subject(a) else 1.2,
                    "dash": "solid" if subject(a) else DASHES[1 + n % 4],
                    "shape": "hv",
                },
                hoverinfo="skip",
            )
        )
    return traces


def _turn_axis(look) -> dict:
    return {"title": {"text": "turn"}, "showline": True, "linecolor": kit.palette(look)["ink"]}


def draw_progress(runs: list[Run], look: str):
    """What was left to the goal at each turn, the median over seeds, one line an arm."""
    arms = by_arm(runs)
    order = rows(arms)
    p = runs[0].progress
    return kit.figure(
        look,
        *_lines(look, arms, order, left_at, p["goal"]),
        height=300,
        showlegend=True,
        xaxis=_turn_axis(look),
        yaxis={"title": {"text": f"{p['unit']} left"}, "rangemode": "tozero"},
        margin={"l": 4, "r": 4, "t": 30, "b": 4, "pad": 4},
    )


def draw_spend(runs: list[Run], look: str):
    """Model calls made by each turn, the median over seeds, one line an arm that uses a model."""
    arms = by_arm(runs)
    order = [a for a in rows(arms) if arms[a][0].model != "none"]
    return kit.figure(
        look,
        *_lines(look, arms, order, lambda r, t: cumulative(r, t, "calls"), None),
        height=280,
        showlegend=True,
        xaxis=_turn_axis(look),
        yaxis={"title": {"text": "model calls"}, "rangemode": "tozero"},
        margin={"l": 4, "r": 4, "t": 30, "b": 4, "pad": 4},
    )


def draw_rules(runs: list[Run], look: str):
    """Each house rule broken in the game, at its turn, as a filled square; a breaking input
    a model proposed that never reached the game, as a hollow one. One line a run."""
    import plotly.graph_objects as go

    arms = by_arm(runs)
    order = rows(arms)
    c = kit.palette(look)
    ys, xs, labels, spans, offered = [], [], [], [], []
    for a in order:
        for r in arms[a]:
            label = f"{record.label(a)} {r.seed}"
            labels.append(f"<b>{label}</b>" if subject(a) else label)
            spans.append((label, r.turns))
            for t, _ in r.breaks:
                xs.append(t)
                ys.append(labels[-1])
            typed = set(r.breaks)
            offered += [(t, labels[-1]) for t, rule in r.proposed if (t, rule) not in typed]
    track = go.Bar(
        x=[t for _, t in spans],
        y=labels,
        orientation="h",
        width=0.08,
        marker={"color": c["ramp2"], "line": {"width": 0}},
        hoverinfo="skip",
    )
    broken = go.Scatter(
        x=xs,
        y=ys,
        mode="markers",
        marker={
            "symbol": "square",
            "size": 9,
            "color": kit.colour("notable", look),
            "line": {"color": c["ink"], "width": 1},
        },
        hoverinfo="skip",
    )
    hollow = go.Scatter(
        x=[t for t, _ in offered],
        y=[y for _, y in offered],
        mode="markers",
        marker={
            "symbol": "square-open",
            "size": 9,
            "color": kit.colour("notable", look),
            "line": {"width": 1.5},
        },
        hoverinfo="skip",
    )
    return kit.figure(
        look,
        track,
        broken,
        hollow,
        height=_height(len(labels), 18, 30),
        xaxis=_turn_axis(look),
        yaxis={
            "type": "category",
            "categoryorder": "array",
            "categoryarray": list(reversed(labels)),
        },
    )


COLUMNS = (
    # key, header, best direction
    ("outcome", "arrived", "high"),
    ("value", "progress", "high"),
    ("turns", "turns", "low"),
    ("calls", "calls", "low"),
    ("tokens", "tokens", "low"),
    ("wall", "seconds", "low"),
    ("broken", "rules broken", "low"),
)


def board_values(rs: list[Run]) -> dict[str, list[float]]:
    known = all(r.tokens_known for r in rs if r.calls)
    return {
        "outcome": [1.0 if r.ending == "reached" else 0.0 for r in rs],
        "value": [r.value for r in rs],
        "turns": [float(r.turns) for r in rs],
        "calls": [float(len(r.calls)) for r in rs],
        "tokens": [float(sum(c["tokens" if known else "chars"] for c in r.calls)) for r in rs],
        "wall": [r.wall for r in rs],
        "broken": [float(len(r.breaks)) for r in rs],
    }


def board(runs: list[Run]) -> tuple[list[str], list[list[float]], list[list[str]]]:
    """The board's rows, a shade a cell (0 worst to 1 best in its column) and its median."""
    arms = by_arm(runs)
    order = rows(arms)
    data = {a: board_values(arms[a]) for a in order}
    shades, words = [], []
    for a in order:
        line, said = [], []
        for key, _, direction in COLUMNS:
            med = statistics.median(data[a][key])
            pool = [statistics.median(data[b][key]) for b in order]
            low, high = min(pool), max(pool)
            share = (med - low) / (high - low) if high > low else 1.0
            line.append(share if direction == "high" else 1 - share)
            n = len(data[a][key])
            said.append(f"{int(sum(data[a][key]))} of {n}" if key == "outcome" else f"{med:,.0f}")
        shades.append(line)
        words.append(said)
    return order, shades, words


def draw_board(runs: list[Run], look: str):
    """Every measure for every arm, the median over seeds, each column shaded on its own scale
    from worst (pale) to best (deep)."""
    import plotly.graph_objects as go

    order, shades, words = board(runs)
    c = kit.palette(look)
    ramp = [c[f"seq{i}"] for i in range(1, len(kit.CHART["sequential"][look]) + 1)]
    known = all(r.tokens_known for r in runs if r.calls)
    heads = [
        runs[0].progress["unit"] if k == "value" else "characters" if k == "tokens" and not known
        else h
        for k, h, _ in COLUMNS
    ]  # fmt: skip
    top = len(order) - 1
    cells = [
        {
            "type": "rect",
            "x0": j - 0.48,
            "x1": j + 0.48,
            "y0": top - i - 0.44,
            "y1": top - i + 0.44,
            "fillcolor": ramp[round(share * (len(ramp) - 1))],
            "line": {"width": 0},
            "layer": "below",
        }
        for i, line in enumerate(shades)
        for j, share in enumerate(line)
    ]  # a shape a cell, drawn as vector: a heatmap trace would export as a raster image
    said = go.Scatter(
        x=[j for line in words for j in range(len(line))],
        y=[top - i for i, line in enumerate(words) for _ in line],
        text=[w for line in words for w in line],
        mode="text",
        textfont={"size": kit.FONT, "color": c["ink"]},
        hoverinfo="skip",
    )
    return kit.figure(
        look,
        said,
        shapes=cells,
        height=_height(len(order), 34, 30),
        xaxis={
            "side": "top",
            "tickvals": list(range(len(heads))),
            "ticktext": heads,
            "range": [-0.5, len(heads) - 0.5],
        },
        yaxis={
            "tickvals": list(range(len(order))),
            "ticktext": [name(a) for a in reversed(order)],
            "range": [-0.5, len(order) - 0.5],
        },
    )


FIGURES = {
    "reached": draw_reached,
    "became": draw_became,
    "cost": draw_cost,
    "time": draw_time,
    "text": draw_text,
    "progress": draw_progress,
    "spend": draw_spend,
    "rules": draw_rules,
    "board": draw_board,
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
