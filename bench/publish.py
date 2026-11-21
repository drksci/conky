"""Publish a results directory: charts, data and words, with nothing to edit by hand.

    python -m bench.publish RESULTS_DIR --name pilot-1 --kind pilot

Writes, from the run files alone:

- `docs/results/NAME/`: the charts (light and dark) with `runs.csv` and `runs.json` beside them;
- `docs/research/results.md`: the method, the tables, every chart and the limits;
- the block between the two `bench` markers in `README.md`: a short summary, then each chart
  under a heading with a caption, the scores as a table, and one footer line of links and units.

A chart carries only what sits on its marks; every word about it is written here, in Markdown.

Running it again on the same runs writes the same files. `--kind pilot` says the runs are too few
to support a claim, and the words say so; `--kind result` is for a run of the fixed protocol.
"""

from __future__ import annotations

import argparse
import statistics
import sys
from pathlib import Path

from bench import analyse, charts, dynamics, record

ROOT = Path(__file__).resolve().parent.parent
REPOSITORY = "https://github.com/drksci/conky"
PAGE = "docs/research/results.md"
START, END = "<!-- bench:start -->", "<!-- bench:end -->"
SHOWN = ("reached", "became", "cost", "time", "text")  # on the front page, in this order
PAGE_ONLY = ("progress", "spend", "rules", "board")
HEADS = {
    "reached": "How far each run got",
    "became": "What each harness left behind",
    "cost": "What a run cost",
    "time": "Where the time went",
    "text": "Where the text came from",
    "progress": "Distance left, turn by turn",
    "spend": "Model calls, turn by turn",
    "rules": "House rules broken",
    "board": "Every measure on one board",
}
ALT = {
    "reached": "Horizontal bars, one a run, grouped by harness, each running from {start} "
    "toward {end}.",
    "became": "Horizontal bars, one a harness, of the parts its median run ended with.",
    "cost": "Horizontal bars, one a harness that uses a model, of a median run's cost.",
    "time": "Stacked horizontal bars, one a harness, of a median run's seconds.",
    "text": "Stacked horizontal bars, one a harness that uses a model, of a median run's text.",
    "progress": "Step lines of {unit} left against turn, one a harness.",
    "spend": "Step lines of model calls made against turn, one a harness that uses a model.",
    "rules": "A row a run with a square at each turn a house rule was broken.",
    "board": "A shaded grid: a row a harness, a column a measure, the median in each cell.",
}


def picture(folder: str, name: str, f: dict, width: int = 720) -> str:
    alt = ALT[name].format(**f["progress"])
    return (
        f'<picture><source media="(prefers-color-scheme: dark)" '
        f'srcset="{folder}/{name}.dark.svg"><img src="{folder}/{name}.light.svg" '
        f'alt="{alt}" width="{width}"></picture>'
    )


def short(commit: str) -> str:
    """The first ten characters of a commit, with `+changes` kept when the tree was dirty."""
    return commit[:10] + ("+changes" if commit.endswith("+changes") else "")


def facts(runs: list[charts.Run]) -> dict:
    arms = charts.by_arm(runs)
    order = charts.arm_order(arms)
    seeds = sorted({r.seed for r in runs})
    per = {}
    for arm in order:
        rs = arms[arm]
        per[arm] = {
            "n": len(rs),
            "arrived": sum(r.ending == "reached" for r in rs),
            "value": statistics.median(r.value for r in rs),
            "gloss": rs[0].row["gloss"],
            "calls": statistics.median(len(r.calls) for r in rs),
            "broken": statistics.median(len(r.breaks) for r in rs),
            "wall": statistics.median(r.wall for r in rs),
        }
    return {
        "order": order,
        "per": per,
        "seeds": seeds,
        "models": sorted({r.model for r in runs if r.model != "none"}) or ["none"],
        "progress": runs[0].progress,
        "summary": record.scenario_config(runs[0].scenario).get("summary", ""),
        "standing": record.scenario_config(runs[0].scenario).get("standing", ""),
        "scenario_version": runs[0].row["scenario_version"],
        "prompt": runs[0].row["prompt"],
        "prompt_sha": runs[0].row["prompt_sha"],
        "commit": runs[0].row["commit"],
        "reasons": record.comparable([r.row for r in runs]),
        "date": max(r.date for r in runs),
        "budget": max(r.budget_calls for r in runs),
        "scenario": runs[0].scenario,
        "scripted": any(r.backend == "scripted" for r in runs),
    }


def limits(kind: str, f: dict) -> str:
    if f["scripted"]:
        return "These runs used a scripted stand-in for the model. They are not a result."
    if kind == "pilot":
        return (
            f"This is a pilot: {len(f['seeds'])} seeds, one scenario and one model. It shows "
            "that the apparatus runs end to end and what a result will look like. It supports "
            "no claim that one arm is better than another."
        )
    return "The protocol was fixed before these runs, and every run started is reported."


def table(f: dict) -> str:
    unit = f["progress"]["unit"].capitalize()
    head = f"| Arm | What it is | Arrived | {unit} | Model calls | Rules broken | Seconds |\n"
    head += "|---|---|---|---|---|---|---|\n"
    body = ""
    for arm in f["order"]:
        p = f["per"][arm]
        body += (
            f"| `{arm}` | {p['gloss']} | {p['arrived']} of {p['n']} | "
            f"{p['value']:,.0f} | {p['calls']:,.0f} | {p['broken']:,.0f} | {p['wall']:,.0f} |\n"
        )
    return head + body


WEIGHTS = {"reach": 70, "cost": 15, "time": 15}


def _own_seconds(rs: list[charts.Run]) -> list[float]:
    """The harness's own seconds for each run: the wall clock less the time spent in the model."""
    return [
        max(r.row["wall_s"] - r.row["model_s"], 0.0)
        for r in rs
        if r.row["model_s"] is not None and (r.row["model_s"] or r.row["model"] == "none")
    ]


def totals(runs: list[charts.Run], order: list[str]) -> dict[str, dict]:
    """A row a harness: the share that reached the goal, the median cost and time of a run, and
    a score out of 100. Time is the harness's own: the wall clock less what was spent waiting on
    the model, when every harness that uses a model records that; the whole wall clock otherwise.

    The score is the share of runs that reached the goal, times the weights: `reach` in full,
    `cost` and `time` each in proportion to the cheapest and the quickest harness that uses a
    model. A harness that never reaches the goal scores nothing, however cheap or quick it is.
    """
    out = {}
    for arm in order:
        rs = [r for r in runs if r.arm == arm]
        costs = [r.row["cost"] for r in rs]
        out[arm] = {
            "reach": sum(r.row["ending"] == "reached" for r in rs) / len(rs),
            "n": len(rs),
            "cost": statistics.median(known)
            if (known := [c for c in costs if c is not None])
            else None,
            "time": statistics.median(r.row["wall_s"] for r in rs),
            "own": statistics.median(own) if (own := _own_seconds(rs)) else None,
            "uses": rs[0].row["model"] != "none",
            "row": rs[0].row,
        }
    paid = [t for t in out.values() if t["uses"]]
    cheapest = min((t["cost"] for t in paid if t["cost"]), default=None)
    timed = all(t["own"] is not None for t in paid)
    for t in out.values():
        t["pace"] = t["own"] if timed else t["time"]
    quickest = min((t["pace"] for t in paid if t["pace"]), default=None)
    for t in out.values():
        part = WEIGHTS["reach"]
        if t["uses"] and t["cost"] and cheapest:
            part += WEIGHTS["cost"] * cheapest / t["cost"]
        if t["uses"] and t["pace"] and quickest:
            part += WEIGHTS["time"] * quickest / t["pace"]
        t["score"] = round(t["reach"] * part)
    return out


def scores(found: dict[str, dict]) -> str:
    """The scores as a Markdown table, best first, each harness linked and the subject in bold."""
    lines = [
        "| Harness | Version | Model | Reached | Cost | Model s | Own s | Score |",
        "|---|---|---|--:|--:|--:|--:|--:|",
    ]
    for arm in sorted(found, key=lambda arm: (-found[arm]["score"], record.label(arm))):
        t = found[arm]
        where, label = record.link(arm), record.label(arm)
        cells = [
            f"[{label}]({where})" if where else label,
            t["row"]["version"],
            f"`{t['row']['model']}`",
            f"{round(t['reach'] * t['n'])}/{t['n']}",
            f"${t['cost']:.4f}" if t["cost"] else "",
            f"{t['time'] - t['own']:,.0f}" if t["own"] is not None and t["uses"] else "",
            f"{t['pace']:,.0f}",
            f"{t['score']}",
        ]
        if record.manifest(arm).get("accent"):
            cells = [f"**{c}**" if c else c for c in cells]
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def conditions(kind: str, f: dict) -> str:
    """What every number in a caption was measured under, in a few words."""
    n = len(f["seeds"])
    model = ", ".join(f"`{m}`" for m in f["models"])
    state = (
        "a scripted stand-in, not a result"
        if f["scripted"]
        else "a pilot"
        if kind == "pilot"
        else "a result"
    )
    return f"Model {model}, {n} runs a harness, {state}."


def captions(kind: str, f: dict, runs: list[charts.Run]) -> dict[str, str]:
    """One sentence a chart: what it shows and the one thing to notice, then its conditions."""
    arms = charts.by_arm(runs)
    order = charts.rows(arms)
    lead = order[0]
    who = record.label(lead)
    p = f["progress"]
    got = sum(r.ending == "reached" for r in arms[lead])
    paid = [a for a in order if arms[a][0].model != "none"]
    cost = {a: charts.run_cost(arms[a]) for a in paid}
    cheapest = min(cost, key=cost.get) if cost else lead
    run = charts.median_run(arms[lead], lambda r: r.wall)
    model_s = run.row["model_s"] or 0.0
    ends = charts.ends(charts.median_run(arms[lead], lambda r: r.row["chars"]))
    sent = {
        a: statistics.median(r.row["chars"] for r in arms[a])
        for a in paid
        if any(r.row["chars"] for r in arms[a])
    }
    text = "Characters the median run sent, by where they came from"
    others = [a for a in sent if a != lead]
    if lead in sent and others:
        rival = others[0]
        change = round(100 * (1 - sent[lead] / sent[rival]))
        more = "less" if change >= 0 else "more"
        text += f"; {who} sent {abs(change)}% {more} than {record.label(rival)}"
    words = {
        "reached": f"A bar a run, from {p['start']} to {p['end']}; {who} reached {p['end']} "
        f"in {got} of {len(arms[lead])}.",
        "became": f"The parts each median run ended with; {who} ended with {ends['all']} "
        f"{ends['unit']}, {ends['own']} of them its own.",
        "cost": f"Dollars a median run, at list price; {record.label(cheapest)} cost least, "
        f"${cost.get(cheapest, 0):.4f}."
        if cost
        else "No harness here uses a model.",
        "time": f"Seconds a median run, waiting on the model or working in the harness; "
        f"{who} spent {model_s:,.0f} of its {run.wall:,.0f} seconds waiting on the model.",
        "text": text + ".",
        "progress": f"{p['unit'].capitalize()} left to {p['end']} at each turn, the median "
        "over seeds.",
        "spend": "Model calls made by each turn, the median over seeds.",
        "rules": "A square at each turn a house rule was broken in the game.",
        "board": "The median of each measure, each column shaded from worst (pale) to best "
        "(deep) on its own scale.",
    }
    tail = conditions(kind, f)
    return {k: f"{v} {tail}" for k, v in words.items()}


def footer(name: str, f: dict, runs: list[charts.Run], links: str) -> str:
    """One line under the charts: where the method, data and code are, and the units."""
    folder = f"docs/results/{name}" if links == "readme" else f"../results/{name}"
    page = PAGE if links == "readme" else "results.md"
    protocol = (
        "docs/research/benchmark-protocol.md" if links == "readme" else "benchmark-protocol.md"
    )
    commit = f["commit"].removesuffix("+changes")
    parts = []
    if links == "readme":
        parts.append(f"[Method and every chart]({page})")
    parts += [f"[the data]({folder}/runs.csv)", f"[the protocol]({protocol})"]
    if commit:
        parts.append(f"[the code that ran]({REPOSITORY}/commit/{commit})")
    listed = record.prices()
    priced = [listed["models"][m] for m in f["models"] if m in listed["models"]]
    for price in priced:
        parts.append(
            f"{price['priced_as']} at ${price['input']:.2f} in and ${price['output']:.2f} "
            "out a million tokens"
        )
    if priced:
        parts.append(f"tokens estimated at {listed['characters_per_token']} characters each")
    return "<sub>" + " · ".join(parts) + "</sub>"


def charted(folder: str, names: tuple[str, ...], said: dict[str, str], f: dict, link: str) -> list:
    """Each chart under its heading, with its caption below."""
    out = []
    for chart in names:
        shown = picture(folder, chart, f)
        if link:
            shown = f'<a href="{link}">{shown}</a>'
        out += [f"#### {HEADS[chart]}", "", shown, "", said[chart], ""]
    return out


def setup(f: dict) -> str:
    seeds = f["seeds"]
    span = f"{seeds[0]} to {seeds[-1]}" if len(seeds) > 1 else f"{seeds[0]}"
    return (
        f"Scenario `{f['scenario']}`, {f['summary']}. "
        f"Seeds {span}, the same for every arm, so runs are paired. "
        f"Model `{', '.join(f['models'])}` "
        f"for every arm that uses one, at most {f['budget']} model calls a run. "
        f"Every arm starts from one agent and the same opening prompt."
    )


def like(f: dict) -> str:
    seeds = f["seeds"]
    span = f"{seeds[0]} to {seeds[-1]}" if len(seeds) > 1 else f"{seeds[0]}"
    lines = [
        f"- Model: `{', '.join(f['models'])}`",
        f"- Seeds: {span}",
        f"- Prompt: `{f['prompt']}`, hash `{f['prompt_sha']}`",
        f"- Budget: at most {f['budget']} model calls a run",
        f"- Commit: `{short(f['commit']) or 'unknown'}`",
        f"- Scenario version: {f['scenario_version']}",
    ]
    if f["reasons"]:
        lines += ["", "These runs are not comparable, because:", ""]
        lines += [f"- {reason}" for reason in f["reasons"]]
    else:
        lines += ["", "Nothing differs among the arms but the arm."]
    return "\n".join(lines)


def story(kind: str, f: dict, runs: list[charts.Run]) -> str:
    """Two or three plain sentences for the front page, every number taken from the runs."""
    n = len(f["seeds"])
    per = f["per"]
    end = f["progress"]["end"]
    lines = [f"{n} trips each to {end}: same game, same small model, same luck, same prompt."]
    floors = [a for a in f["order"] if not per[a]["calls"]]
    if floors and not any(per[a]["arrived"] for a in floors):
        lines.append("Pressing keys gets nobody there.")
    if "loop" in per:
        lines.append(f"The bare model, asked each turn, arrived {per['loop']['arrived']} times.")
    if "conky" in per:
        told = f"A Conky character arrived {per['conky']['arrived']} times"
        if "loop" in per:
            for key, less, more in (("chars", "sent {n}% less text", "sent {n}% more text"),):
                both = {
                    arm: statistics.median(r.row[key] for r in runs if r.arm == arm)
                    for arm in ("loop", "conky")
                }
                if both["loop"]:
                    change = round(100 * (both["conky"] / both["loop"] - 1))
                    if change:
                        told += ", " + (less if change < 0 else more).format(n=abs(change))
        kept = sum(r.kept or 0 for r in runs if r.arm == "conky")
        if kept:
            told += f" and kept {kept} pages of its own notes"
        lines.append(told + ".")
    for arm in f["order"]:
        if record.manifest(arm).get("control"):
            lines.append(f"Stock {record.label(arm).title()} arrived {per[arm]['arrived']} times.")
    if f["scripted"]:
        lines.append("These runs used a scripted stand-in for the model, so none of it counts.")
    elif kind == "pilot":
        lines.append("It is a pilot: too few trips to call a winner, so none is called.")
    if f.get("standing"):
        lines.append(f["standing"])
    return " ".join(lines)


def readme_block(name: str, kind: str, f: dict, runs: list[charts.Run]) -> str:
    said = captions(kind, f, runs)
    return "\n".join(
        [
            START,
            "### Benchmark",
            "",
            story(kind, f, runs),
            "",
            *charted(f"docs/results/{name}", SHOWN, said, f, PAGE),
            "#### Scores",
            "",
            scores(totals(runs, f["order"])),
            "",
            f"Best first. {SCORING} {conditions(kind, f)}",
            "",
            footer(name, f, runs, "readme"),
            "",
            "<br>",
            END,
        ]
    )


SCORING = (
    "A score is out of 100: reaching the goal gives 70, and cost and the harness's own "
    "seconds give up to 15 each, against the cheapest and the quickest."
)


def page(name: str, kind: str, f: dict, runs: list[charts.Run]) -> str:
    folder = f"../results/{name}"
    status = "draft" if kind == "pilot" or f["scripted"] else "current"
    parts = [
        "---",
        "kind: research",
        'title: "Benchmark results"',
        f"status: {status}",
        f"date: {f['date']}",
        f'source: "generated by bench/publish.py from the runs named {name}"',
        "---",
        "",
        "# Benchmark results",
        "",
        "This page is generated from the run files by `bench/publish.py`. Nobody edits it by hand.",
        "",
        "## Summary",
        "",
        story(kind, f, runs),
        "",
        limits(kind, f),
        "",
        "## Method",
        "",
        setup(f) + " The measures and how they are scored are stated in the "
        "[benchmark protocol](benchmark-protocol.md).",
        "",
        "## Compared like for like",
        "",
        like(f),
        "",
        "## Results",
        "",
        "Counts are runs. Other columns are the median over seeds.",
        "",
        table(f),
        "",
        "### Scores",
        "",
        scores(totals(runs, f["order"])),
        "",
        f"Best first. {SCORING}",
        "",
        "### Charts",
        "",
        *charted(folder, (*SHOWN, *PAGE_ONLY), captions(kind, f, runs), f, ""),
        footer(name, f, runs, "page"),
        "",
    ]
    parts += [
        "## Data",
        "",
        f"One row per run: [runs.csv]({folder}/runs.csv) and [runs.json]({folder}/runs.json). "
        "The charts are drawn from the same rows by `bench/charts.py`, so they can be drawn "
        "another way. Raw transcripts hold the game's own text, which has no licence to "
        "republish, and are kept outside this repository.",
        "",
    ]
    return "\n".join(parts)


def publish(results: Path, name: str, kind: str, root: Path = ROOT) -> list[Path]:
    kept, branched = analyse.partition(results)
    if branched:
        print(analyse.skipped_note(branched), file=sys.stderr)
    runs = [charts.load_run(folder) for folder in kept]
    if not runs:
        raise SystemExit(f"no runs under {results}: run bench.run first, or point at its --out")
    f = facts(runs)
    if f["reasons"]:
        why = "; ".join(f["reasons"])
        if kind == "result":
            raise SystemExit(f"these runs cannot be published as a result: {why}")
        print(f"not comparable: {why}", file=sys.stderr)
    out = root / "docs" / "results" / name
    drawn = (*SHOWN, *PAGE_ONLY)
    written = [
        p
        for p in charts.render(runs, out, kind)
        if p.suffix != ".svg" or p.name.split(".")[0] in drawn
    ]
    for stray in out.glob("*.svg"):
        if stray.name.split(".")[0] not in drawn:
            stray.unlink()
    doc = root / "docs" / "research" / "results.md"
    doc.write_text(page(name, kind, f, runs), encoding="utf-8")
    readme = root / "README.md"
    text = readme.read_text(encoding="utf-8")
    if START not in text or END not in text:
        raise SystemExit(f"README.md has no {START} and {END} markers: add them where it goes")
    head, rest = text.split(START, 1)
    readme.write_text(
        head + readme_block(name, kind, f, runs) + rest.split(END, 1)[1], encoding="utf-8"
    )
    if dynamics.START in readme.read_text(encoding="utf-8"):
        written += dynamics.refresh(root)
    return [*written, doc, readme]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="bench.publish", description=__doc__.split("\n")[0])
    parser.add_argument("results", type=Path, help="a results directory written by bench.run")
    parser.add_argument("--name", required=True, help="a short name for these runs, as a folder")
    parser.add_argument("--kind", choices=("pilot", "result"), required=True)
    args = parser.parse_args(argv)
    for path in publish(args.results, args.name, args.kind):
        print(path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
