"""The standard run record, from the hand-made results directory of test_bench_charts.

Two arms: `loop` arrives in three turns with three calls (one house rule broken on turn 1);
`floor-random` makes no call, breaks the same rule on turn 1 and dies.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from bench import record

from tests.test_bench_charts import build

SHARED = ("record.py", "charts.py", "publish.py", "analyse.py")
SCENARIO_WORDS = re.compile(r"\b(oregon|miles|den|traveller)\b", re.IGNORECASE)


def folder(root: Path, arm: str) -> Path:
    return root / "trail" / arm / "full" / "seed-1"


def test_the_row_has_the_standard_keys_and_values(tmp_path: Path) -> None:
    root = build(tmp_path / "r", "scripted")
    loop = record.row(folder(root, "loop"))
    assert tuple(loop) == record.KEYS
    assert loop | {"tape": "", "commit": ""} == {
        "scenario": "trail",
        "scenario_version": None,
        "harness": "loop",
        "gloss": "the bare model, asked each turn",
        "model": "stand-in",
        "seed": 1,
        "commit": "",
        "prompt": "",
        "prompt_sha": "",
        "budget_calls": 10,
        "backend": "scripted",
        "date": "2026-11-20",
        "ending": "reached",
        "progress": 1.0,
        "value": 2040.0,
        "steps": 3,
        "calls": 3,
        "chars": 3009,
        "tokens": 36,
        "wall_s": 30.0,
        "violations": 1,
        "kept": None,
        "tape": "",
        "version": "",
        "cost": None,
        "model_s": 0.0,
    }
    assert re.fullmatch(r"[0-9a-f]{12}", loop["tape"])
    dead = record.row(folder(root, "floor-random"))
    assert (dead["ending"], dead["calls"], dead["violations"]) == ("lost", 0, 1)
    assert dead["gloss"] == "no model, keys at random"


def test_a_harness_that_uses_no_model_has_the_model_none(tmp_path: Path) -> None:
    root = build(tmp_path / "r", "scripted")
    meta = folder(root, "floor-random") / "run.json"
    data = json.loads(meta.read_text())
    meta.write_text(json.dumps(data | {"uses_model": False}), encoding="utf-8")
    assert record.row(folder(root, "floor-random"))["model"] == "none"


def test_the_series_has_one_entry_a_step(tmp_path: Path) -> None:
    root = build(tmp_path / "r", "scripted")
    steps = record.series(folder(root, "loop"))
    assert [s["step"] for s in steps] == [1, 2, 3]
    assert [round(s["progress"], 4) for s in steps] == [0.0, 0.1471, 1.0]
    assert [(s["calls"], s["chars"]) for s in steps] == [(2, 2006), (3, 3009), (3, 3009)]
    assert [s["violations"] for s in steps] == [["eat-poorly"], [], []]


def test_kept_is_counted_as_the_harness_declares(tmp_path: Path) -> None:
    run = tmp_path / "run"
    pages = run / "pages"
    pages.mkdir(parents=True)
    (pages / "a.md").write_text("---\nwithin: nest\n---\n", encoding="utf-8")
    (pages / "b.md").write_text("---\nwithin: nest\n---\n", encoding="utf-8")
    (pages / "c.md").write_text("---\nwithin: elsewhere\n---\n", encoding="utf-8")
    declared = {"glob": "pages/*.md", "contains": "\nwithin: nest\n", "except": ["b"]}
    assert record.kept(run, declared) == 1
    assert record.kept(run, None) is None


def rows(**changes) -> list[dict]:
    base = {
        "harness": "a",
        "model": "m",
        "seed": 1,
        "commit": "abc",
        "prompt_sha": "p",
        "budget_calls": 10,
        "scenario_version": 1,
        "backend": "live",
    }
    return [base | {"harness": "a"}, base | {"harness": "b"} | changes]


def test_arms_that_differ_in_nothing_are_comparable() -> None:
    assert record.comparable(rows()) == []


def test_each_difference_is_a_reason() -> None:
    assert "different ones" in record.comparable(rows(model="n"))[0]
    assert record.comparable(rows(model="none")) == []
    assert "seeds" in record.comparable(rows(seed=2))[0]
    assert "prompts" in record.comparable(rows(prompt_sha="q"))[0]
    assert "call budgets" in record.comparable(rows(budget_calls=5))[0]
    assert "scenario versions" in record.comparable(rows(scenario_version=2))[0]
    assert "backends" in record.comparable(rows(backend="scripted"))[0]
    assert "different commits" in record.comparable(rows(commit="def"))[0]
    dirty = rows(commit="abc+changes")
    assert any("uncommitted" in r for r in record.comparable(dirty))


def test_shared_bench_code_names_no_scenario() -> None:
    bench = Path(__file__).resolve().parent.parent / "bench"
    for name in SHARED:
        found = SCENARIO_WORDS.findall((bench / name).read_text(encoding="utf-8"))
        assert not found, f"bench/{name} names {found}: declare it in scenario.json instead"


def test_dollars_come_from_the_price_list_and_say_how_tokens_were_counted() -> None:
    listed = record.prices()
    price = listed["models"]["haiku"]
    made = [{"chars": 4_000_400, "answer": 400}]
    cost, basis = record.dollars("haiku", made)
    per = listed["characters_per_token"]
    want = (4_000_000 / per * price["input"] + 400 / per * price["output"]) / 1e6
    assert abs(cost - want) < 1e-12
    assert "estimated" in basis and str(per) in basis
    assert record.dollars("a-model-with-no-price", made) is None
    assert record.dollars("haiku", []) is None
