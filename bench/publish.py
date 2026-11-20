"""Publish a results directory: charts, data and words, with nothing to edit by hand.

    python -m bench.publish RESULTS_DIR --name pilot-1 --kind pilot

Writes, from the run files alone:

- `docs/results/NAME/`: the charts (light and dark) with `runs.csv` and `runs.json` beside them;
- `docs/research/results.md`: the method, the table, every chart and the limits;
- the block between the two `bench` markers in `README.md`: one chart and a short summary.

Running it again on the same runs writes the same files. `--kind pilot` says the runs are too few
to support a claim, and the words say so; `--kind result` is for a run of the fixed protocol.
"""

from __future__ import annotations

import argparse
import statistics
import sys
from pathlib import Path

from bench import charts

ROOT = Path(__file__).resolve().parent.parent
PAGE = "docs/research/results.md"
START, END = "<!-- bench:start -->", "<!-- bench:end -->"
SHOWN = ("trail", "progress", "spend", "rules", "board")
ALT = {
    "trail": "Where each run ended on the road to Oregon, one row per way of playing.",
    "progress": "Miles left to Oregon against turn, one line per arm.",
    "spend": "Model calls and text sent against turn, one line per arm.",
    "rules": "House rules broken in the game, by turn, for each run.",
    "board": "Every measure for every arm on one board.",
}


def picture(folder: str, name: str, width: int = 800) -> str:
    return (
        f'<picture><source media="(prefers-color-scheme: dark)" '
        f'srcset="{folder}/{name}.dark.svg"><img src="{folder}/{name}.light.svg" '
        f'alt="{ALT[name]}" width="{width}"></picture>'
    )


def facts(runs: list[charts.Run]) -> dict:
    arms = charts.by_arm(runs)
    order = [a for a in charts.GLOSS if a in arms] + [a for a in arms if a not in charts.GLOSS]
    seeds = sorted({r.seed for r in runs})
    per = {}
    for arm in order:
        rs = arms[arm]
        per[arm] = {
            "n": len(rs),
            "arrived": sum(r.ending == "arrived" for r in rs),
            "miles": statistics.median(r.miles for r in rs),
            "calls": statistics.median(len(r.calls) for r in rs),
            "broken": statistics.median(len(r.breaks) for r in rs),
            "wall": statistics.median(r.wall for r in rs),
        }
    return {
        "order": order,
        "per": per,
        "seeds": seeds,
        "models": sorted({r.model for r in runs}),
        "date": max(r.date for r in runs),
        "budget": max(r.budget_calls for r in runs),
        "scenario": runs[0].scenario,
        "scripted": any(r.backend == "scripted" for r in runs),
    }


def sentence(arm: str, f: dict) -> str:
    cost = f"{f['calls']:,.0f} model calls" if f["calls"] else "no model"
    return (
        f"`{arm}` ({charts.GLOSS.get(arm, 'an arm')}) arrived in {f['arrived']} of {f['n']} runs "
        f"with {cost} and {f['broken']:,.0f} rules broken at the median"
    )


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
    head = "| Arm | What it is | Arrived | Miles | Model calls | Rules broken | Seconds |\n"
    head += "|---|---|---|---|---|---|---|\n"
    body = ""
    for arm in f["order"]:
        p = f["per"][arm]
        body += (
            f"| `{arm}` | {charts.GLOSS.get(arm, '')} | {p['arrived']} of {p['n']} | "
            f"{p['miles']:,.0f} | {p['calls']:,.0f} | {p['broken']:,.0f} | {p['wall']:,.0f} |\n"
        )
    return head + body


def setup(f: dict) -> str:
    seeds = f["seeds"]
    span = f"{seeds[0]} to {seeds[-1]}" if len(seeds) > 1 else f"{seeds[0]}"
    return (
        f"Scenario `{f['scenario']}`, the 1975 text Oregon Trail, fetched at run time. "
        f"Seeds {span}, the same for every arm, so runs are paired. "
        f"Model `{', '.join(f['models'])}` "
        f"for every arm that uses one, at most {f['budget']} model calls a run. "
        f"Every arm starts from one agent and the same opening prompt."
    )


def readme_block(name: str, kind: str, f: dict) -> str:
    folder = f"docs/results/{name}"
    word = "Pilot" if kind == "pilot" else "Result"
    arms = "; ".join(sentence(a, f["per"][a]) for a in f["order"] if f["per"][a]["calls"])
    return "\n".join(
        [
            START,
            "### Benchmark",
            "",
            "Same game, same model, same luck, same opening prompt. Each row is a way of playing.",
            "",
            f'<p align="center"><a href="{PAGE}">{picture(folder, "trail")}</a></p>',
            "",
            f"**{word}, {f['date']}.** {setup(f)}",
            "",
            f"{arms[0].upper() + arms[1:]}. The two floors use no model and never arrive, so the "
            f"game is not won by pressing keys. {limits(kind, f)}",
            "",
            f'<p align="center"><a href="{PAGE}">Method and every chart</a>'
            f'&nbsp;&nbsp;·&nbsp;&nbsp;<a href="{folder}/runs.csv">the data</a>'
            f'&nbsp;&nbsp;·&nbsp;&nbsp;<a href="docs/research/benchmark-protocol.md">'
            f"the protocol</a></p>",
            "",
            "<br>",
            END,
        ]
    )


def page(name: str, kind: str, f: dict) -> str:
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
        limits(kind, f),
        "",
        "## Method",
        "",
        setup(f) + " The measures and how they are scored are stated in the "
        "[benchmark protocol](benchmark-protocol.md).",
        "",
        "## Results",
        "",
        "Counts are runs. Other columns are the median over seeds.",
        "",
        table(f),
    ]
    for chart in SHOWN:
        parts += [f'<p align="center">{picture(folder, chart)}</p>', ""]
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
    runs = charts.load(results)
    if not runs:
        raise SystemExit(f"no runs under {results}: run bench.run first, or point at its --out")
    f = facts(runs)
    out = root / "docs" / "results" / name
    written = [
        p for p in charts.render(runs, out) if p.suffix != ".svg" or p.name.split(".")[0] in SHOWN
    ]
    for stray in out.glob("*.svg"):
        if stray.name.split(".")[0] not in SHOWN:
            stray.unlink()
    doc = root / "docs" / "research" / "results.md"
    doc.write_text(page(name, kind, f), encoding="utf-8")
    readme = root / "README.md"
    text = readme.read_text(encoding="utf-8")
    if START not in text or END not in text:
        raise SystemExit(f"README.md has no {START} and {END} markers: add them where it goes")
    head, rest = text.split(START, 1)
    readme.write_text(head + readme_block(name, kind, f) + rest.split(END, 1)[1], encoding="utf-8")
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
