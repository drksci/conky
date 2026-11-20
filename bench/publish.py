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

from bench import analyse, charts, record

ROOT = Path(__file__).resolve().parent.parent
REPOSITORY = "https://github.com/drksci/conky"
PAGE = "docs/research/results.md"
START, END = "<!-- bench:start -->", "<!-- bench:end -->"
PLATES = ("reached", "became", "cost", "time", "text")
SHOWN = (*PLATES, "progress", "spend", "rules", "board")
ALT = {
    "reached": "Every run drawn as a bar from {start} to {end}, one band per harness, under "
    "the model, seeds, budget and commit that were held equal.",
    "became": "The parts each harness was made of when its median run stopped.",
    "cost": "Text sent against progress made, one line for every run.",
    "text": "The text each harness sent in its median run, cut by where it came from.",
    "time": "The median run of each harness along a time axis: steps above, model calls below.",
    "progress": "{unit} left to {end} against turn, one line per arm.",
    "spend": "Model calls and text sent against turn, one line per arm.",
    "rules": "House rules broken in the game, by turn, for each run.",
    "board": "Every measure for every arm on one board.",
}


def picture(folder: str, name: str, f: dict, width: int = 720) -> str:
    return (
        f'<picture><source media="(prefers-color-scheme: dark)" '
        f'srcset="{folder}/{name}.dark.svg"><img src="{folder}/{name}.light.svg" '
        f'alt="{ALT[name].format(**f["progress"])}" width="{width}"></picture>'
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


def scores(f: dict, runs: list[charts.Run]) -> str:
    """The scores as one small table for the front page: a row a harness, medians over seeds."""
    heads = ("benchmark", "harness", "model", "runs", "reached", f["progress"]["unit"], "calls")
    heads += ("text sent", "cost a run", "seconds", "rules broken", "pages kept")
    out = ["<table>", "<tr>" + "".join(f"<th><sub>{h}</sub></th>" for h in heads) + "</tr>"]
    for arm in f["order"]:
        rs = [r for r in runs if r.arm == arm]
        p = f["per"][arm]
        kept = [r.kept for r in rs if r.kept is not None]
        sent = statistics.median(r.row["chars"] for r in rs)
        paid = [record.dollars(r.row["model"], r.calls) for r in rs]
        cost = statistics.median(p[0] for p in paid) if paid and all(paid) else None
        cells = (
            f["scenario"],
            f"<b>{arm}</b>",
            rs[0].row["model"],
            p["n"],
            f"<b>{p['arrived']} of {p['n']}</b>",
            f"{p['value']:,.0f}",
            f"{p['calls']:,.0f}",
            f"{sent:,.0f}" if sent else "0",
            f"${cost:.4f}" if cost is not None else ("$0" if not sent else ""),
            f"{p['wall']:,.0f}",
            sum(len(r.breaks) for r in rs),
            sum(kept) if kept else "",
        )
        out.append("<tr>" + "".join(f"<td><sub>{c}</sub></td>" for c in cells) + "</tr>")
    out.append("</table>")
    return "\n".join(out)


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
        lines.append(f"A plain loop around the model arrived {per['loop']['arrived']} times.")
    if "conky" in per:
        told = f"A Conky character arrived {per['conky']['arrived']} times"
        if "loop" in per:
            for key, less, more in (
                ("chars", "sent {n}% less text", "sent {n}% more text"),
                ("wall_s", "took {n}% less time", "took {n}% longer"),
            ):
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
    if f["scripted"]:
        lines.append("These runs used a scripted stand-in for the model, so none of it counts.")
    elif kind == "pilot":
        lines.append("It is a pilot: too few trips to call a winner, so none is called.")
    return " ".join(lines)


def readme_block(name: str, kind: str, f: dict, runs: list[charts.Run]) -> str:
    folder = f"docs/results/{name}"
    commit = f["commit"].removesuffix("+changes")
    code = (
        f'&nbsp;&nbsp;·&nbsp;&nbsp;<a href="{REPOSITORY}/commit/{commit}">the code that ran</a>'
        if commit
        else ""
    )
    return "\n".join(
        [
            START,
            "### Benchmark",
            "",
            story(kind, f, runs),
            "",
            scores(f, runs),
            "",
            *(
                line
                for name in PLATES
                for line in (
                    f'<p align="center"><a href="{PAGE}">{picture(folder, name, f)}</a></p>',
                    "",
                )
            ),
            "",
            f'<p align="center"><a href="{PAGE}">Method and every chart</a>'
            f'&nbsp;&nbsp;·&nbsp;&nbsp;<a href="{folder}/runs.csv">the data</a>'
            f'&nbsp;&nbsp;·&nbsp;&nbsp;<a href="docs/research/benchmark-protocol.md">'
            f"the protocol</a>{code}</p>",
            "",
            "<br>",
            END,
        ]
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
    ]
    for chart in SHOWN:
        parts += [f'<p align="center">{picture(folder, chart, f)}</p>', ""]
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
    written = [
        p
        for p in charts.render(runs, out, kind)
        if p.suffix != ".svg" or p.name.split(".")[0] in SHOWN
    ]
    for stray in out.glob("*.svg"):
        if stray.name.split(".")[0] not in SHOWN:
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
