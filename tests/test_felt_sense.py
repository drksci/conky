"""The felt-sense experiment: generators, renderings, analysis and the stand-in pipeline."""

from __future__ import annotations

import re

import pytest
from bench.experiments.felt_sense import analyse, render, run, tasks
from bench.experiments.felt_sense.walk import StandIn

NAMES = {n: v for rows in render.ANCHORS.values() for v, *names in rows for n in names}


def placed_value(text: str) -> float:
    """The value a placement states: its ratio times its nearest anchor."""
    ratio, name = re.search(r"([\d.]+) x (a [\w' ]+?)$", text).groups()
    return float(ratio) * NAMES[name]


def test_generators_are_deterministic() -> None:
    for task in tasks.GENERATORS:
        assert tasks.generate(task, 7, "inside") == tasks.generate(task, 7, "inside")
        assert tasks.generate(task, 7, "inside") != tasks.generate(task, 8, "inside")


def test_ground_truth_on_hand_checked_cases() -> None:
    for seed in range(60):
        i = tasks.t1(seed, "inside")
        ratio = i.slots["S"] * i.values["p"] / i.values["D"]
        assert (i.truth == "lasts") == (ratio >= 1)
        assert not 1 / 1.3 < ratio < 1.3
        j = tasks.t3(seed, "inside")
        ratio = j.values["d"] * j.slots["n"] / j.values["K"]
        assert (j.truth == "correct") == (ratio > 1)
        assert not 1 / 1.3 < ratio < 1.3
        k = tasks.t2(seed, "inside")
        urgency = {c: k.values[f"e{c}"] / k.values[f"w{c}"] for c in "ABCD"}
        assert k.order == sorted(urgency, key=lambda c: -urgency[c])
        assert k.truth == k.order[0]


@pytest.mark.parametrize("stratum", tasks.STRATA)
def test_stratum_and_margin_hold_in_every_stratum(stratum: str) -> None:
    for seed in range(40):
        for task in tasks.GENERATORS:
            i = tasks.generate(task, seed, stratum)
            assert i.stratum == stratum
            assert all(v > 0 for v in i.values.values())
            # the decision survives the two-figure precision of condition c
            shown = {
                k: placed_value(render.place(v, i.dimension, False)) for k, v in i.values.items()
            }
            if task == "T1":
                assert (i.slots["S"] * shown["p"] >= shown["D"]) == (i.truth == "lasts")
            elif task == "T3":
                assert (shown["d"] * i.slots["n"] > shown["K"]) == (i.truth == "correct")
            else:
                urgency = {c: shown[f"e{c}"] / shown[f"w{c}"] for c in "ABCD"}
                assert max(urgency, key=urgency.get) == i.truth


def test_placement_rule_on_the_page_example() -> None:
    assert render.show(259200, "time", "a") == "259200"
    assert render.show(259200, "time", "b") == "259200 s"
    assert render.show(259200, "time", "c") == "between a night and a week, 0.43 x a week"
    assert render.show(259200, "time", "d") == "between a dosk and a mirl, 0.43 x a mirl"
    assert render.show(259200, "time", "e") == (
        "259200 s (between a night and a week, 0.43 x a week)"
    )
    assert render.show(1, "time", "c") == "below a moment, 0.5 x a moment"
    assert render.show(4e9, "money", "c") == "beyond a house, 10000 x a house"


def test_every_rendering_carries_the_same_information() -> None:
    for instance in tasks.instances(12):
        for value in instance.values.values():
            raw = {c: render.show(value, instance.dimension, c) for c in render.CONDITIONS}
            assert float(raw["a"]) == float(raw["b"].split()[0]) == float(raw["e"].split()[0])
            for text in (raw["c"], raw["d"]):
                assert abs(placed_value(text) / value - 1) < 0.06
            familiar, opaque = raw["c"], raw["d"]
            for old, new in zip(
                [r[1] for rows in render.ANCHORS.values() for r in rows],
                [r[2] for rows in render.ANCHORS.values() for r in rows],
                strict=True,
            ):
                familiar = familiar.replace(old, new)
            assert familiar == opaque
            assert raw["e"].endswith(f"({raw['c']})")
    assert "Anchors" not in render.prompt(tasks.t1(1, "inside"), "b")
    assert render.prompt(tasks.t1(1, "inside"), "c").startswith("Anchors")


def rows_of(table: list[tuple[str, str, bool, str]]) -> list[dict]:
    return [
        {"instance": i, "task": "T1", "stratum": "inside", "condition": c, "correct": ok,
         "answer": a, "confidence": None, "tokens_in": 1, "tokens_out": 1}
        for i, c, ok, a in table
    ]  # fmt: skip


def test_analysis_gives_known_answers() -> None:
    rows = rows_of(
        [("x", "b", False, "no"), ("x", "b", True, "yes"), ("x", "c", True, "yes"),
         ("x", "c", True, "yes"), ("y", "b", False, "no"), ("y", "b", False, "no"),
         ("y", "c", True, "yes"), ("y", "c", False, "no")]
    )  # fmt: skip
    assert analyse.accuracy(rows) == {"b": 0.25, "c": 0.75}
    assert analyse.consistency(rows) == {"b": 0.5, "c": 0.5}
    found = analyse.contrast(rows, "c", "b", resamples=500)
    assert found["difference"] == pytest.approx(0.5)
    assert found["low"] <= 0.5 <= found["high"] and found["n"] == 2
    assert analyse.parse("so\nANSWER: `Runs out`\nCONFIDENCE: 80", "T1") == ("runs out", 80)
    assert analyse.parse("ANSWER: C, A, B, D", "T2") == ("C", None)
    assert analyse.parse("no answer line", "T1") == ("", None)


def test_the_stand_in_walk_runs_through_the_meter(tmp_path) -> None:
    found = tasks.instances(10)
    rows = run.run(found, StandIn(found), tmp_path, repeats=1)
    assert len(rows) == 50
    assert {r["condition"] for r in rows} == set(render.CONDITIONS)
    assert len((tmp_path / "meter.jsonl").read_text().splitlines()) == 50
    assert len(run.table(rows, resamples=200).splitlines()) == 6
    again = run.run(found, StandIn(found), tmp_path / "again", repeats=1)
    assert [r["correct"] for r in again] == [r["correct"] for r in rows]
