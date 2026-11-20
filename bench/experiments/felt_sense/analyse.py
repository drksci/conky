"""Scoring and the analysis: accuracy per condition, the paired contrast, repeat consistency."""

from __future__ import annotations

import random
import re
from collections import defaultdict
from itertools import combinations

ANSWER = re.compile(r"^\s*ANSWER:\s*(.+?)\s*$", re.MULTILINE)
CONFIDENCE = re.compile(r"^\s*CONFIDENCE:\s*(\d{1,3})\b", re.MULTILINE)


def parse(text: str, task: str) -> tuple[str, int | None]:
    """The answer (T2: the first letter listed) and the confidence; empty when absent."""
    found = ANSWER.findall(text)
    answer = found[-1].strip("` ").lower() if found else ""
    if task == "T2":
        letters = re.findall(r"\b[A-D]\b", answer.upper())
        answer = letters[0] if letters else ""
    stated = CONFIDENCE.findall(text)
    return answer, (min(int(stated[-1]), 100) if stated else None)


def mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else float("nan")


def accuracy(rows: list[dict]) -> dict[str, float]:
    """Per condition, the mean over instances of the share of repeats that are right."""
    return {
        c: mean(list(by_instance(rows, c).values())) for c in sorted({r["condition"] for r in rows})
    }


def by_instance(rows: list[dict], condition: str) -> dict[str, float]:
    shares: dict[str, list[float]] = defaultdict(list)
    for row in rows:
        if row["condition"] == condition:
            shares[row["instance"]].append(1.0 if row["correct"] else 0.0)
    return {k: mean(v) for k, v in shares.items()}


def contrast(
    rows: list[dict], plus: str, minus: str, resamples: int = 10000, seed: int = 0
) -> dict:
    """The mean paired difference plus minus, with a 95 percent percentile bootstrap interval.

    Instances are resampled within task. An instance missing either condition is left out.
    """
    first, second = by_instance(rows, plus), by_instance(rows, minus)
    task_of = {r["instance"]: r["task"] for r in rows}
    groups: dict[str, list[float]] = defaultdict(list)
    for key in sorted(first.keys() & second.keys()):
        groups[task_of[key]].append(first[key] - second[key])
    pooled = [d for g in groups.values() for d in g]
    rng = random.Random(seed)
    draws = []
    for _ in range(resamples):
        total = sum(rng.choice(g) for g in groups.values() for _ in g)
        draws.append(total / len(pooled))
    draws.sort()
    low, high = draws[int(0.025 * resamples)], draws[min(int(0.975 * resamples), resamples - 1)]
    return {"difference": mean(pooled), "low": low, "high": high, "n": len(pooled), "seed": seed}


def consistency(rows: list[dict]) -> dict[str, float | None]:
    """Per condition, the share of repeat pairs giving the same answer; None with one repeat."""
    result: dict[str, float | None] = {}
    for condition in sorted({r["condition"] for r in rows}):
        answers: dict[str, list[str]] = defaultdict(list)
        for row in rows:
            if row["condition"] == condition:
                answers[row["instance"]].append(row["answer"])
        same = [x == y for a in answers.values() for x, y in combinations(a, 2)]
        result[condition] = mean([1.0 if s else 0.0 for s in same]) if same else None
    return result


def brier(rows: list[dict]) -> dict[str, float]:
    """Per stratum, the Brier score of stated confidence; unstated confidence counts as 0.5."""
    scores: dict[str, list[float]] = defaultdict(list)
    for row in rows:
        said = row["confidence"] / 100 if row["confidence"] is not None else 0.5
        scores[row["stratum"]].append((said - (1.0 if row["correct"] else 0.0)) ** 2)
    return {k: mean(v) for k, v in sorted(scores.items())}


def tokens(rows: list[dict]) -> dict[str, tuple[float, float]]:
    """Per condition, the mean input and output tokens per call."""
    found: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        found[row["condition"]].append(row)
    return {
        c: (mean([r["tokens_in"] or 0 for r in v]), mean([r["tokens_out"] or 0 for r in v]))
        for c, v in sorted(found.items())
    }
