"""The five renderings of a magnitude, the anchor tables and the prompt, as pure functions."""

from __future__ import annotations

import math
from bisect import bisect_right
from decimal import Decimal

from bench.experiments.felt_sense.tasks import Instance

CONDITIONS = ("a", "b", "c", "d", "e")
UNITS = {"time": " s", "money": " dollars"}

# value in base units, familiar name, opaque name (a fixed shuffle, set before any run)
ANCHORS = {
    "time": [
        (2, "a moment", "a veld"),
        (1800, "a meal", "a prin"),
        (28800, "a night", "a dosk"),
        (604800, "a week", "a mirl"),
        (7889400, "a season", "a tave"),
    ],
    "money": [
        (4, "a coffee", "a kess"),
        (40, "a restaurant meal", "a ralm"),
        (1500, "a month's rent", "a vonk"),
        (30000, "a car", "a brell"),
        (400000, "a house", "a sorn"),
    ],
}
WRAPPER = (
    "Work it out briefly. End with two lines: `ANSWER: <your answer>` and "
    "`CONFIDENCE: <a whole number from 0 to 100, your chance of being right>`."
)


def plain(value: float, digits: int) -> str:
    """A number to `digits` significant figures, never in exponent form."""
    return format(Decimal(f"{value:.{digits}g}"), "f")


def place(value: float, dimension: str, opaque: bool) -> str:
    """The fixed rule: between two anchors, below the lowest, or beyond the highest."""
    anchors = ANCHORS[dimension]
    name = 2 if opaque else 1
    nearest = min(anchors, key=lambda a: abs(math.log(value / a[0])))
    ratio = f"{plain(value / nearest[0], 2)} x {nearest[name]}"
    if value < anchors[0][0]:
        return f"below {anchors[0][name]}, {ratio}"
    if value > anchors[-1][0]:
        return f"beyond {anchors[-1][name]}, {ratio}"
    above = min(bisect_right([a[0] for a in anchors], value), len(anchors) - 1)
    low, high = anchors[above - 1], anchors[above]
    return f"between {low[name]} and {high[name]}, {ratio}"


def show(value: float, dimension: str, condition: str) -> str:
    raw = format(Decimal(repr(float(value))).normalize(), "f")
    if condition == "a":
        return raw
    if condition == "b":
        return raw + UNITS[dimension]
    if condition == "c":
        return place(value, dimension, opaque=False)
    if condition == "d":
        return place(value, dimension, opaque=True)
    if condition == "e":
        return f"{raw}{UNITS[dimension]} ({place(value, dimension, opaque=False)})"
    raise ValueError(f"unknown condition {condition!r}: use one of {', '.join(CONDITIONS)}")


def table(dimension: str, opaque: bool) -> str:
    name = 2 if opaque else 1
    rows = [f"- {a[name]}: {plain(a[0], 8)}{UNITS[dimension]}" for a in ANCHORS[dimension]]
    return "Anchors, each with its value:\n" + "\n".join(rows)


def prompt(instance: Instance, condition: str) -> str:
    shown = {k: show(v, instance.dimension, condition) for k, v in instance.values.items()}
    sentence = instance.template.format(**shown, **instance.slots)
    head = ""
    if condition in "cde":
        head = table(instance.dimension, opaque=condition == "d") + "\n\n"
    return f"{head}{sentence}\n\n{WRAPPER}"
