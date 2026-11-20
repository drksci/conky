"""The stand-in walk: ten instances, five conditions, one repeat, no model.

    python -m bench.experiments.felt_sense.walk

The stand-in answers from ground truth with a fixed chance per condition and wrongly otherwise.
Its numbers prove the pipeline and say nothing about any model. A walk is never a result.
"""

from __future__ import annotations

import hashlib
import tempfile
from pathlib import Path

from bench.backends import Call, Completion
from bench.experiments.felt_sense import render, run, tasks

# the share of prompts the stand-in answers correctly, by condition: invented, for the walk only
RIGHT = {"a": 0.4, "b": 0.6, "c": 0.9, "d": 0.7, "e": 0.9}


class StandIn:
    """`stub`: a deterministic stand-in that knows each prompt's answer. Never a result."""

    name = "stand-in"
    model_free = True

    def __init__(self, instances: list[tasks.Instance]) -> None:
        self.known = {render.prompt(i, c): (i, c) for i in instances for c in render.CONDITIONS}

    def complete(self, call: Call) -> Completion:
        text = call.text()
        instance, condition = self.known[text]
        draw = int(hashlib.sha256(text.encode("utf-8")).hexdigest()[:8], 16) / 16**8
        right = draw < RIGHT[condition]
        flip = {"lasts": "runs out", "runs out": "lasts", "correct": "leave", "leave": "correct"}
        other = flip.get(instance.truth) or next(k for k in "ABCD" if k != instance.truth)
        given = instance.truth if right else other
        reply = f"Working it out.\nANSWER: {given}\nCONFIDENCE: {90 if right else 70}"
        return Completion(reply, len(text.split()), len(reply.split()))


def main() -> None:
    found = tasks.instances(10)
    with tempfile.TemporaryDirectory() as tmp:
        rows = run.run(found, StandIn(found), Path(tmp), repeats=1)
    print(run.table(rows, resamples=2000))


if __name__ == "__main__":
    main()
