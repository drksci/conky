"""Read a results directory and compute the pre-stated measures, standard library only.

    python -m bench.analyse RESULTS_DIR [--json out.json] [--markdown out.md]

For every run it scores the game's transcript (the ground truth) and reads the meter's trace.
Then, per scenario, probe, arm and prompt variant: mean, median and a bootstrap 95 percent
interval. Where seeds are paired it adds paired differences between arms at a fixed prompt
(harness effect), between prompts at a fixed arm (prompt effect), the arm-by-prompt interaction
for each pair of arms and pair of prompts, and a two-factor decomposition of the cell means.
Every number carries its result class: mechanism, harness or prompt.

It refuses to make a results table from runs on the `scripted` backend, from stepped runs, from
runs resumed by hand, from runs whose answers were replayed from a record, from runs on a
stand-in game, and from `fixed` runs whose recording came from a stand-in.
"""

from __future__ import annotations

import argparse
import json
import random
import statistics
import sys
from pathlib import Path

from bench.backends import MODEL_FREE
from bench.envs import textenv
from bench.scenarios.trail import score

RESAMPLES = 2000
SEED = 20261120
METRICS = (
    "arrived",
    "mileage",
    "violations",
    "invalid",
    "inputs",
    "calls",
    "tokens",
    "wall_s",
    "scaffold_bytes_per_call",
    "image_bytes",
    "shelf_reads",
    "accountability",
)
STAND_INS = ("scripted", "adversary")


class Refused(Exception):
    """The runs cannot make a results table; the message says why."""


def run_metrics(folder: Path) -> dict:
    """Every measure of one run, from its transcript, trace, shelf log and record."""
    record = json.loads((folder / "run.json").read_text())
    events = textenv.read(folder / "transcript.jsonl")
    found = score.outcome(events)
    trace = folder / "meter.jsonl"
    calls = [json.loads(x) for x in trace.read_text().splitlines()] if trace.exists() else []
    answered = [c for c in calls if c.get("status") == 200]
    known = all(c.get("tokens_known") for c in answered)
    tokens = sum((c.get("tokens_in") or 0) + (c.get("tokens_out") or 0) for c in answered)
    shelf = folder / "shelf.jsonl"
    reads = [json.loads(x) for x in shelf.read_text().splitlines()] if shelf.exists() else []
    reads = [r for r in reads if r.get("name") and r.get("status", 200) == 200]
    wall = sum(s["end"] - s["start"] for s in record.get("segments", []))
    account = record.get("accountability") or {}
    metrics = {
        **{k: found[k] for k in ("arrived", "mileage", "violations", "invalid", "inputs")},
        "arrived": 1.0 if found["arrived"] else 0.0,
        "outcome": found["outcome"],
        "calls": len(answered),
        "refused_calls": len(calls) - len(answered),
        "tokens": tokens if known else None,
        "chars": sum(c.get("chars_in", 0) + c.get("chars_out", 0) for c in answered),
        "wall_s": round(wall, 3),
        "scaffold_bytes_per_call": (
            statistics.mean(c["scaffold_bytes"] for c in answered) if answered else 0.0
        ),
        "pack_ok": all(c.get("pack_ok", True) for c in calls),
        "image_bytes": sum(c.get("image_bytes", 0) for c in calls),
        "shelf_reads": len(reads),
        "shelf_names": sorted({r["name"] for r in reads}),
        "proposed": sum(1 for c in answered if (c.get("note") or {}).get("proposed")),
        "accountability": (
            account["answerable"] / account["sampled"] if account.get("sampled") else None
        ),
        "exit": record.get("exit"),
    }
    for rule in score.RULES:
        metrics[f"violations.{rule}"] = found[f"violations.{rule}"]
    if record.get("probe") in ("resume", "portability"):
        metrics.update(resume_metrics(events))
    if record.get("portability"):
        metrics["portable"] = 1.0 if record["portability"].get("verify_code") == 0 else 0.0
    return {"record": record, "metrics": metrics, "dir": str(folder)}


def resume_metrics(events: list[dict]) -> dict:
    starts = [i for i, e in enumerate(events) if e["kind"] == "start"]
    if len(starts) < 2:
        return {"resumed": 0.0}
    from bench.envs.oregon_trail_1975 import parse

    before, _, _ = parse.walk(events[: starts[1]])
    after, _, _ = parse.walk(events)
    later = after[len(before) :]
    broke = score.violations(later)
    return {
        "resumed": 1.0 if later else 0.0,
        "first_input_valid": 0.0 if not later or later[0]["invalid"] else 1.0,
        "invalid_after_resume": sum(1 for d in later if d["invalid"]),
        "violations_after_resume": len(broke),
    }


def load(results: Path) -> list[dict]:
    return [run_metrics(p.parent) for p in sorted(results.rglob("run.json"))]


def check(runs: list[dict]) -> None:
    """Refuse runs that may never be reported, saying why."""
    problems = []
    for run in runs:
        record = run["record"]
        where = run["dir"]
        if record.get("backend") == "scripted":
            problems.append(f"{where}: backend is scripted, a stand-in for tests")
        if record.get("stand_in_game"):
            problems.append(f"{where}: played a stand-in game, not the scenario's")
        if record.get("step"):
            problems.append(f"{where}: stepped by a person")
        if record.get("manual_resume"):
            problems.append(f"{where}: resumed by hand")
        if record.get("cache_mode") == "replay":
            problems.append(f"{where}: answers replayed from a record, not a new result")
        source = record.get("recording_source") or {}
        if record.get("backend") == "fixed" and (
            not source.get("backends") or set(source["backends"]) & set(STAND_INS)
        ):
            problems.append(f"{where}: fixed answers recorded from a stand-in")
    if problems:
        raise Refused(
            "no results table: these runs can never be reported:\n  " + "\n  ".join(problems)
        )


def bootstrap(values: list[float], rng: random.Random | None = None) -> tuple[float, float]:
    """A percentile bootstrap 95 percent interval of the mean."""
    if not values:
        return (float("nan"), float("nan"))
    if len(values) == 1:
        return (values[0], values[0])
    rng = rng or random.Random(SEED)
    means = sorted(statistics.fmean(rng.choice(values) for _ in values) for _ in range(RESAMPLES))
    return means[int(0.025 * RESAMPLES)], means[int(0.975 * RESAMPLES) - 1]


def summary(values: list[float]) -> dict:
    values = [v for v in values if v is not None]
    if not values:
        return {"n": 0}
    low, high = bootstrap(values)
    return {
        "n": len(values),
        "mean": statistics.fmean(values),
        "median": statistics.median(values),
        "low": low,
        "high": high,
    }


def result_class(backend: str, contrast: str) -> str:
    """The class a number carries. No model involved: mechanism. Prompts compared: prompt."""
    if backend in MODEL_FREE:
        return "mechanism"
    return "prompt" if contrast in ("prompt", "interaction") else "harness"


def cells(runs: list[dict]) -> dict[tuple, dict[int, dict]]:
    """Runs grouped by (scenario, probe, backend, arm, prompt), then by seed."""
    grouped: dict[tuple, dict[int, dict]] = {}
    for run in runs:
        r = run["record"]
        key = (r["scenario"], r.get("probe", ""), r["backend"], r["arm"], r["prompt"])
        grouped.setdefault(key, {})[r["seed"]] = run["metrics"]
    return grouped


def paired(a: dict[int, dict], b: dict[int, dict], metric: str) -> list[float]:
    common = sorted(set(a) & set(b))
    return [
        a[s][metric] - b[s][metric]
        for s in common
        if a[s].get(metric) is not None and b[s].get(metric) is not None
    ]


def decompose(table: dict[tuple[str, str], dict[int, dict]], metric: str) -> dict:
    """Two-factor decomposition of cell means over the seeds every cell shares.

    With arm i and prompt j, the cell mean m_ij = g + a_i + p_j + r_ij, where g is the grand
    mean, a_i the arm's row mean minus g, p_j the prompt's column mean minus g, and r_ij what is
    left: the interaction. Sums of squares over the cells give each part's share. Intervals for
    a_i and p_j come from resampling the shared seeds with replacement, jointly for all cells.
    """
    arms = sorted({a for a, _ in table})
    prompts = sorted({p for _, p in table})
    if len(arms) < 1 or len(prompts) < 1 or len(table) != len(arms) * len(prompts):
        return {}
    shared = sorted(set.intersection(*(set(v) for v in table.values())))
    shared = [s for s in shared if all(table[c][s].get(metric) is not None for c in table)]
    if not shared:
        return {}

    def parts(sample: list[int]) -> dict:
        mean = {c: statistics.fmean(table[c][s][metric] for s in sample) for c in table}
        grand = statistics.fmean(mean.values())
        arm = {a: statistics.fmean(mean[(a, p)] for p in prompts) - grand for a in arms}
        prompt = {p: statistics.fmean(mean[(a, p)] for a in arms) - grand for p in prompts}
        rest = {
            f"{a} x {p}": mean[(a, p)] - grand - arm[a] - prompt[p] for a in arms for p in prompts
        }
        return {"grand": grand, "arm": arm, "prompt": prompt, "interaction": rest}

    point = parts(shared)
    rng = random.Random(SEED)
    draws = [parts([rng.choice(shared) for _ in shared]) for _ in range(RESAMPLES // 4)]

    def interval(kind: str, name: str) -> tuple[float, float]:
        values = sorted(d[kind][name] for d in draws)
        return values[int(0.025 * len(values))], values[int(0.975 * len(values)) - 1]

    squares = {
        kind: sum(v**2 for v in point[kind].values()) for kind in ("arm", "prompt", "interaction")
    }
    squares["arm"] *= len(prompts)
    squares["prompt"] *= len(arms)
    total = sum(squares.values()) or 1.0
    return {
        "seeds": len(shared),
        "grand": point["grand"],
        "arm": {a: {"effect": v, "interval": interval("arm", a)} for a, v in point["arm"].items()},
        "prompt": {
            p: {"effect": v, "interval": interval("prompt", p)} for p, v in point["prompt"].items()
        },
        "interaction": {
            k: {"effect": v, "interval": interval("interaction", k)}
            for k, v in point["interaction"].items()
        },
        "share": {k: v / total for k, v in squares.items()},
    }


def analyse(runs: list[dict]) -> dict:
    check(runs)
    grouped = cells(runs)
    out: dict = {"cells": [], "harness": [], "prompt": [], "interaction": [], "decomposition": []}
    for (scenario, probe, backend, arm, prompt), by_seed in sorted(grouped.items()):
        for metric in METRICS:
            stats = summary([m.get(metric) for m in by_seed.values()])
            if stats.get("n"):
                out["cells"].append(
                    {"scenario": scenario, "probe": probe, "backend": backend, "arm": arm,
                     "prompt": prompt, "metric": metric, **stats,
                     "class": result_class(backend, "cell")}
                )  # fmt: skip
    paired_ok = {
        (r["record"]["scenario"], r["record"].get("probe", "")): r["record"].get("paired", True)
        for r in runs
    }
    keys = sorted(grouped)
    for i, first in enumerate(keys):
        for second in keys[i + 1 :]:
            if first[:3] != second[:3] or not paired_ok.get(first[:2], True):
                continue
            same_prompt = first[4] == second[4]
            same_arm = first[3] == second[3]
            if not (same_prompt or same_arm):
                continue
            contrast = "harness" if same_prompt else "prompt"
            for metric in METRICS:
                diffs = paired(grouped[first], grouped[second], metric)
                if not diffs:
                    continue
                low, high = bootstrap(diffs)
                out[contrast].append(
                    {"scenario": first[0], "probe": first[1], "backend": first[2],
                     "a": f"{first[3]}/{first[4]}", "b": f"{second[3]}/{second[4]}",
                     "metric": metric, "n": len(diffs), "mean": statistics.fmean(diffs),
                     "low": low, "high": high, "class": result_class(first[2], contrast)}
                )  # fmt: skip
    groups: dict[tuple, dict] = {}
    for key, by_seed in grouped.items():
        groups.setdefault(key[:3], {})[(key[3], key[4])] = by_seed
    for head, table in sorted(groups.items()):
        if not paired_ok.get(head[:2], True):
            continue
        arms = sorted({a for a, _ in table})
        prompts = sorted({p for _, p in table})
        for metric in METRICS:
            for i, a1 in enumerate(arms):
                for a2 in arms[i + 1 :]:
                    for j, p1 in enumerate(prompts):
                        for p2 in prompts[j + 1 :]:
                            cells4 = [(a1, p1), (a2, p1), (a1, p2), (a2, p2)]
                            if not all(c in table for c in cells4):
                                continue
                            gap1 = paired(table[(a1, p1)], table[(a2, p1)], metric)
                            gap2 = paired(table[(a1, p2)], table[(a2, p2)], metric)
                            if not gap1 or len(gap1) != len(gap2):
                                continue
                            values = [x - y for x, y in zip(gap1, gap2, strict=True)]
                            low, high = bootstrap(values)
                            out["interaction"].append(
                                {"scenario": head[0], "probe": head[1], "backend": head[2],
                                 "arms": f"{a1} - {a2}", "prompts": f"{p1} vs {p2}",
                                 "metric": metric, "n": len(values),
                                 "mean": statistics.fmean(values), "low": low, "high": high,
                                 "class": result_class(head[2], "interaction")}
                            )  # fmt: skip
            found = decompose(table, metric)
            if found and (len(arms) > 1 or len(prompts) > 1):
                out["decomposition"].append(
                    {"scenario": head[0], "probe": head[1], "backend": head[2],
                     "metric": metric, **found}
                )  # fmt: skip
    return out


def _n(value: float) -> str:
    return f"{value:.3g}" if isinstance(value, float) else str(value)


def markdown(result: dict) -> str:
    lines = ["# Results", ""]
    lines += ["## Cells", "", "| class | scenario | probe | arm | prompt | measure | n | mean | "
              "median | 95% interval |", "|---|---|---|---|---|---|---|---|---|---|"]  # fmt: skip
    for row in result["cells"]:
        lines.append(
            f"| {row['class']} | {row['scenario']} | {row['probe'] or '-'} | {row['arm']} | "
            f"{row['prompt']} | {row['metric']} | {row['n']} | {_n(row['mean'])} | "
            f"{_n(row['median'])} | {_n(row['low'])} to {_n(row['high'])} |"
        )
    for kind, title in (("harness", "Harness effect at a fixed prompt (paired by seed)"),
                        ("prompt", "Prompt effect at a fixed arm (paired by seed)")):  # fmt: skip
        lines += ["", f"## {title}", "", "| class | a | b | measure | n | mean a - b | "
                  "95% interval |", "|---|---|---|---|---|---|---|"]  # fmt: skip
        for row in result[kind]:
            lines.append(
                f"| {row['class']} | {row['a']} | {row['b']} | {row['metric']} | {row['n']} | "
                f"{_n(row['mean'])} | {_n(row['low'])} to {_n(row['high'])} |"
            )
    lines += ["", "## Interaction: does the harness gap change with the prompt", "",
              "| class | arms | prompts | measure | n | mean | 95% interval |",
              "|---|---|---|---|---|---|---|"]  # fmt: skip
    for row in result["interaction"]:
        lines.append(
            f"| {row['class']} | {row['arms']} | {row['prompts']} | {row['metric']} | "
            f"{row['n']} | {_n(row['mean'])} | {_n(row['low'])} to {_n(row['high'])} |"
        )
    lines += ["", "## Decomposition of cell means", ""]
    for row in result["decomposition"]:
        shares = ", ".join(f"{k} {v:.0%}" for k, v in row["share"].items())
        lines.append(f"- {row['scenario']} {row['probe'] or ''} {row['metric']}: grand mean "
                     f"{_n(row['grand'])}; share of variation between cells: {shares}")  # fmt: skip
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("results", type=Path)
    parser.add_argument("--json", type=Path, default=None)
    parser.add_argument("--markdown", type=Path, default=None)
    args = parser.parse_args(argv)
    try:
        result = analyse(load(args.results))
    except Refused as exc:
        print(exc, file=sys.stderr)
        return 2
    text = markdown(result)
    if args.json:
        args.json.write_text(json.dumps(result, indent=1, default=str))
    if args.markdown:
        args.markdown.write_text(text)
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
