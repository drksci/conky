"""The benchmark harness under bench/: environment hold, scoring, meter, arms, runner, analysis.

No test reaches the network or a live model. Games are stand-ins written for these tests
(tests/games/stand_in.py and one inline), never the fetched 1975 port, except one test that
is skipped unless that port is already in the local cache.
"""

from __future__ import annotations

import io
import json
import random
import subprocess
import sys
from pathlib import Path

import pytest
from bench import analyse, backends, run
from bench.adapters import base
from bench.envs import textenv
from bench.envs.oregon_trail_1975 import fetch, launch, parse
from bench.meter import Budget, Meter
from bench.scenarios.trail import score

from .conftest import git

ROOT = Path(__file__).resolve().parent.parent
STAND_IN = ROOT / "tests" / "games" / "stand_in.py"
SCENARIO = ROOT / "bench" / "scenarios" / "trail"
PACK = SCENARIO / "prompts" / "full"

# A game written for these tests: it reads the three things the launcher pins.
PINNED = """
import datetime, random, time
print("draw", random.randint(0, 10**9))
print("minute", datetime.datetime.now().minute)
start = time.time()
name = input("NAME? ")
print("seconds", int(time.time() - start), "for", name)
count = int(input("HOW MANY? "))
print("twice", count * 2)
"""

# A hand-typed transcript in this test's own words around the few fragments the parser keys on.
SYNTHETIC = [
    {"kind": "start", "seed": 1},
    {"kind": "out", "text": "--------\nMONDAY APRIL 1 1847\nTOTAL MILEAGE IS 300\n"},
    {"kind": "out", "text": "FOOD, BULLETS, CLOTHING, SUPPLIES, CASH\n"},
    {"kind": "out", "text": "   55     900        40        30   45\n"},
    {"kind": "out", "text": "\nDO YOU WANT TO (1) STOP AT THE NEXT FORT, (2) HUNT, OR (3) GO: "},
    {"kind": "in", "n": 1, "line": "3"},
    {"kind": "out", "text": "DO YOU WANT TO EAT (1) THINLY (2) FAIRLY (3) RICHLY: "},
    {"kind": "in", "n": 2, "line": "1"},
    {"kind": "out", "text": "\nRIDERS AHEAD.  THEY DON'T LOOK HOSTILE\nCHOICE: "},
    {"kind": "in", "n": 3, "line": "2"},
    {"kind": "out", "text": "--------\nMONDAY APRIL 15 1847\nTOTAL MILEAGE IS 480\n"},
    {
        "kind": "out",
        "text": "FOOD, BULLETS, CLOTHING, SUPPLIES, CASH\n   20 -  10   40   30   45\n",
    },
    {"kind": "out", "text": "DO YOU WANT TO EAT (1) THINLY (2) FAIRLY (3) RICHLY: "},
    {"kind": "in", "n": 4, "line": "1"},
    {"kind": "out", "text": "DO YOU WANT TO EAT (1) THINLY (2) FAIRLY (3) RICHLY: "},
    {"kind": "in", "n": 5, "line": "seven"},
]


def session(tmp_path: Path, lines: list[str], **extra) -> textenv.Session:
    transcript = tmp_path / "transcript.jsonl"
    stdin = io.StringIO("".join(f"{line}\n" for line in lines))
    return textenv.Session(transcript, parse.state_of, stdin=stdin, stdout=io.StringIO(), **extra)


def pinned_game(tmp_path: Path) -> Path:
    path = tmp_path / "pinned.py"
    path.write_text(PINNED)
    return path


# The environment's hold on a game.


def test_the_launcher_pins_every_source_of_change(tmp_path: Path) -> None:
    game = pinned_game(tmp_path)
    shown = []
    for folder in ("one", "two"):
        (tmp_path / folder).mkdir()
        held = session(tmp_path / folder, ["ada", "21"])
        assert launch.run(game, 7, held)["outcome"] == "ended"
        shown.append(textenv.text(held.events))
    assert shown[0] == shown[1]
    assert "minute 30" in shown[0] and "seconds 1 for ada" in shown[0] and "twice 42" in shown[0]
    assert str(random.Random(7).randint(0, 10**9)) in shown[0]


def test_an_answer_the_game_cannot_read_is_recorded_as_a_crash(tmp_path: Path) -> None:
    held = session(tmp_path, ["ada", "many"])
    assert launch.run(pinned_game(tmp_path), 7, held)["outcome"] == "crashed"
    assert [e for e in held.events if e["kind"] == "crash"]


def test_a_stop_condition_ends_the_game_and_a_replay_carries_on(tmp_path: Path) -> None:
    game = pinned_game(tmp_path)
    held = session(tmp_path, ["ada", "21"], stop_when=[textenv.Condition("inputs>=1")])
    assert launch.run(game, 7, held)["outcome"] == "stopped"
    assert [e["line"] for e in held.events if e["kind"] == "in"] == ["ada"]
    out = io.StringIO()
    again = textenv.Session(
        tmp_path / "transcript.jsonl",
        parse.state_of,
        replay=["ada"],
        stdin=io.StringIO("21\n"),
        stdout=out,
    )
    assert launch.run(game, 7, again)["outcome"] == "ended"
    assert "The game resumes where it stopped" in out.getvalue() and "twice 42" in out.getvalue()
    events = textenv.read(tmp_path / "transcript.jsonl")
    assert [e["line"] for e in events if e["kind"] == "in"] == ["ada", "21"]
    assert "seconds 1 for ada" not in out.getvalue().split("resumes")[1].split("NAME")[0]


def test_conditions_read_and_compare() -> None:
    assert textenv.Condition("turn>=8").holds({"turn": 8})
    assert not textenv.Condition("food<50").holds({"food": 50})
    assert textenv.Condition("prompt==eat").holds({"prompt": "eat"})
    assert not textenv.Condition("cash>1").holds({"cash": None})
    with pytest.raises(ValueError, match="NAME OP VALUE"):
        textenv.Condition("turn is eight")


def test_fetch_pins_a_commit_and_checks_the_file(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    git(source, "init", "-q", "-b", "main")
    (source / "main.py").write_text("print('hello')\n")
    git(source, "add", "main.py")
    git(source, "commit", "-q", "-m", "one")
    commit = git(source, "rev-parse", "HEAD").strip()
    (source / "main.py").write_text("print('changed')\n")
    git(source, "commit", "-q", "-am", "two")
    wanted = fetch.digest(Path(__file__).parent / "games" / "trail.py")
    with pytest.raises(fetch.FetchError, match="not the pinned"):
        fetch.fetch(tmp_path / "cache", str(source), commit, wanted)
    import hashlib

    good = hashlib.sha256(b"print('hello')\n").hexdigest()
    found = fetch.fetch(tmp_path / "cache2", str(source), commit, good)
    assert found.read_text() == "print('hello')\n"
    with pytest.raises(fetch.FetchError, match="cannot fetch"):
        fetch.fetch(tmp_path / "cache3", str(tmp_path / "nowhere"), commit, good)


# Scoring from the transcript.


def test_the_parser_reads_state_prompts_and_invalid_answers() -> None:
    decisions, state, _ = parse.walk(SYNTHETIC)
    assert [d["prompt"] for d in decisions] == ["action", "eat", "tactics", "eat", "eat"]
    first = decisions[0]["state"]
    assert (first["food"], first["cash"], first["mileage"], first["fort"]) == (55, 45, 300, True)
    assert decisions[2]["state"]["riders"] == "friendly-looking"
    assert decisions[3]["state"]["food"] == 20 and decisions[3]["state"]["bullets"] == -10
    assert [d["invalid"] for d in decisions] == [False, False, False, False, True]
    assert state["turn"] == 2 and state["mileage"] == 480


def test_each_house_rule_is_detected_from_the_transcript() -> None:
    decisions, _, _ = parse.walk(SYNTHETIC)
    found = score.violations(decisions)
    assert [v["rule"] for v in found] == ["pass-fort-hungry", "eat-poorly", "attack-friendly"]
    result = score.outcome(SYNTHETIC)
    assert result["violations"] == 3 and result["invalid"] == 1 and result["inputs"] == 5
    assert score.broken({"food": 49}, "eat", "1") is None
    assert score.broken({"fort": True, "food": 30, "cash": 39}, "action", "3") is None
    assert score.broken({"riders": "hostile"}, "tactics", "2") is None


@pytest.mark.skipif(
    not (fetch.default_cache() / f"oregon-trail-1975-{fetch.COMMIT}" / "main.py").exists(),
    reason="the 1975 port is not in the local cache; fetch it to run this test",
)
def test_the_house_rules_bind_on_the_real_game() -> None:
    from bench.scenarios.trail import policies

    reckless = [score.outcome(policies.play(s, policies.reckless)) for s in range(1, 6)]
    careful = [score.outcome(policies.play(s, policies.careful)) for s in range(1, 6)]
    assert all(o["violations"] == 0 for o in careful)
    assert all(any(o[f"violations.{r}"] for o in reckless) for r in ("eat-poorly",))


# The meter and the backends.


class Silent:
    name = "silent"

    def complete(self, call):
        return backends.Completion("2", None, None)


def post(meter: Meter, body: dict, path="/v1/chat/completions", token="t") -> tuple[int, dict]:
    headers = {"authorization": f"Bearer {token}"}
    return meter.handle(path, headers, json.dumps(body).encode())


def test_the_meter_checks_the_token_the_model_and_the_budget(tmp_path: Path) -> None:
    trace = tmp_path / "meter.jsonl"
    meter = Meter(backends.Scripted(), "m", "t", Budget(calls=2, tokens=10**6), trace)
    ask = {"model": "m", "messages": [{"role": "user", "content": "CHOICE: "}]}
    assert post(meter, ask, token="wrong")[0] == 401
    assert post(meter, {**ask, "model": "other"})[1]["error"]["type"] == "model_mismatch"
    assert post(meter, ask)[0] == 200 and post(meter, ask)[0] == 200
    status, answer = post(meter, ask)
    assert status == 429 and answer["error"]["type"] == "budget_exhausted" and meter.exhausted
    lines = [json.loads(x) for x in trace.read_text().splitlines()]
    assert [x["status"] for x in lines] == [400, 200, 200, 429]
    assert all(x["tokens_known"] for x in lines if x["status"] == 200)


def test_the_meter_counts_bytes_by_origin_and_strips_markers(tmp_path: Path) -> None:
    trace = tmp_path / "meter.jsonl"
    pack = base.Pack.load(PACK)
    meter = Meter(Silent(), "m", "t", Budget(5, 100), trace, [pack.task, pack.rules])
    image = "data:image/png;base64,aGVsbG8="
    content = [
        {"type": "text", "text": f"{pack.mark(pack.task)}Go on.{base.mark_screen('A SCREEN')}"},
        {"type": "image_url", "image_url": {"url": image}},
    ]
    assert post(meter, {"model": "m", "messages": [{"role": "user", "content": content}]})[0] == 200
    body = {"model": "m", "system": "<<<pack>>>not the pack<<</pack>>>", "messages": []}
    status, answer = post(meter, body, path="/v1/messages")
    assert status == 200 and answer["content"][0]["text"] == "2" and "usage" not in answer
    first, second = [json.loads(x) for x in trace.read_text().splitlines()]
    assert first["pack_bytes"] == len(pack.task.encode()) and first["pack_ok"]
    assert first["screen_bytes"] == len("A SCREEN") and first["scaffold_bytes"] == len("Go on.")
    assert first["image_bytes"] == 5 and "<<<" not in json.dumps(first["request"])
    assert first["tokens_known"] is False and first["tokens_in"] is None
    assert not second["pack_ok"]


def test_the_shelf_is_served_and_every_read_logged(tmp_path: Path) -> None:
    log = tmp_path / "shelf.jsonl"
    meter = Meter(Silent(), "m", "t", Budget(1, 1), tmp_path / "m", [], SCENARIO / "shelf", log)
    url = meter.start()
    try:
        status, text = base.ask_meter(url, "t", "m", [{"role": "user", "content": "x"}])
        assert status == 200 and text == "2"
        names = meter.handle_get("/shelf", {"authorization": "Bearer t"})[1]["items"]
        assert {"name": "fables"} in names
        found = meter.handle_get("/shelf/fables", {"authorization": "Bearer t"})[1]
        assert "Tortoise" in found["text"]
        assert meter.handle_get("/shelf", {})[0] == 401
    finally:
        meter.stop()
    reads = [json.loads(x) for x in log.read_text().splitlines()]
    assert [r["name"] for r in reads] == ["", "fables"] and reads[1]["bytes"] > 1000


def test_the_adversary_proposes_breaks_and_fixed_answers_hold(tmp_path: Path) -> None:
    eat = "FOOD, BULLETS, CLOTHING, SUPPLIES, CASH\n  90 1 1 1 9\nDO YOU WANT TO EAT (1) A: "
    call = backends.Call("", [{"role": "user", "parts": [{"type": "text", "text": eat}]}])
    done = backends.Adversary().complete(call)
    assert done.text == "1" and done.note == {"proposed": "eat-poorly"}
    assert backends.Scripted().complete(call).text == "3"
    trace = tmp_path / "meter.jsonl"
    meter = Meter(backends.Adversary(), "m", "t", Budget(5, 10**6), trace)
    post(meter, {"model": "m", "messages": [{"role": "user", "content": eat}]})
    recording = tmp_path / "recording.json"
    backends.record([trace], recording)
    replay = backends.Fixed(recording)
    assert replay.complete(call).text == "1" and replay.complete(call).note["fixed"] == "hit"
    other = backends.Call("", [{"role": "user", "parts": [{"type": "text", "text": "CHOICE: "}]}])
    assert replay.complete(other).note["fixed"] == "miss"


# The runner and the arms, on the small trail game in tests/games.


@pytest.fixture(scope="module")
def results(tmp_path_factory: pytest.TempPathFactory) -> Path:
    out = tmp_path_factory.mktemp("results")
    arms = "loop,conky,floor-continue,floor-random"
    assert run.main(["--arms", arms, "--game", str(STAND_IN), "--out", str(out),
                     "--stall", "15", "--wall", "60"]) == 0  # fmt: skip
    return out


@pytest.mark.parametrize("arm", ["loop", "conky", "floor-continue", "floor-random"])
def test_every_arm_plays_to_the_end_through_the_meter(results: Path, arm: str) -> None:
    folder = results / "trail" / arm / "full" / "seed-1"
    record = json.loads((folder / "run.json").read_text())
    assert record["exit"] == "game-ended" and record["stand_in_game"]
    inputs = [e for e in textenv.read(folder / "transcript.jsonl") if e["kind"] == "in"]
    assert len(inputs) == 5
    calls = (
        [json.loads(x) for x in (folder / "meter.jsonl").read_text().splitlines()]
        if (folder / "meter.jsonl").exists()
        else []
    )
    if arm in ("loop", "conky"):
        assert len(calls) >= 5 and all(c["pack_ok"] and c["status"] == 200 for c in calls)
        assert all(c["pack_bytes"] > 0 and c["screen_bytes"] > 0 for c in calls)
        assert record["accountability"]["answerable"] == record["accountability"]["sampled"] == 5
    else:
        assert calls == []
    assert run.ROOT not in folder.resolve().parents


def test_analysis_refuses_runs_on_a_stand_in(results: Path) -> None:
    with pytest.raises(analyse.Refused, match="backend is scripted"):
        analyse.analyse(analyse.load(results))
    assert analyse.main([str(results)]) == 2


def test_the_resume_probe_stops_and_a_fresh_process_carries_on(tmp_path: Path) -> None:
    options = ["--arms", "loop", "--probe", "resume", "--stop-when", "inputs>=2"]
    assert (
        run.main([*options, "--game", str(STAND_IN), "--out", str(tmp_path), "--stall", "15"]) == 0
    )
    folder = tmp_path / "trail" / "loop" / "full" / "seed-1-resume"
    record = json.loads((folder / "run.json").read_text())
    assert [s["exit"] for s in record["segments"]] == ["stopped", "game-ended"]
    assert record["segments"][1]["resume"]
    events = textenv.read(folder / "transcript.jsonl")
    assert len([e for e in events if e["kind"] == "start"]) == 2
    assert [e["n"] for e in events if e["kind"] == "in"] == [1, 2, 3, 4, 5]
    assert analyse.resume_metrics(events)["resumed"] == 1.0


def test_the_portability_probe_moves_only_the_declared_state(tmp_path: Path) -> None:
    options = ["--arms", "loop", "--probe", "portability", "--stop-when", "inputs>=2"]
    assert (
        run.main([*options, "--game", str(STAND_IN), "--out", str(tmp_path), "--stall", "15"]) == 0
    )
    record = json.loads((tmp_path / "trail/loop/full/seed-1-portability/run.json").read_text())
    assert record["portability"]["copied"] == ["transcript.jsonl"]
    assert record["portability"]["verify_code"] == 0 and record["exit"] == "game-ended"


def test_a_stepped_run_waits_for_enter_and_a_run_resumed_by_hand_is_marked(
    tmp_path: Path,
) -> None:
    command = [sys.executable, "-m", "bench.run", "--arms", "floor-continue", "--step",
               "--game", str(STAND_IN), "--out", str(tmp_path / "a")]  # fmt: skip
    done = subprocess.run(command, input="\n" * 10, capture_output=True, text=True, cwd=ROOT,
                          timeout=60, check=False)  # fmt: skip
    assert done.returncode == 0 and "=== before input 1 ===" in done.stdout
    assert json.loads((tmp_path / "a/trail/floor-continue/full/seed-1/run.json").read_text())[
        "step"
    ]
    assert run.main(["--arms", "loop", "--stop-when", "inputs>=2", "--game", str(STAND_IN),
                     "--out", str(tmp_path / "b"), "--stall", "15"]) == 0  # fmt: skip
    stopped = tmp_path / "b" / "trail" / "loop" / "full" / "seed-1"
    assert json.loads((stopped / "run.json").read_text())["exit"] == "stopped"
    assert run.main(["--resume", str(stopped), "--arm", "floor-continue", "--game",
                     str(STAND_IN), "--out", str(tmp_path / "c")]) == 0  # fmt: skip
    resumed = next((tmp_path / "c").glob("*/run.json"))
    record = json.loads(resumed.read_text())
    assert record["manual_resume"] and record["exit"] == "game-ended"


def test_the_matrix_is_fully_crossed_and_paired_by_seed() -> None:
    cells = run.matrix("trail", ["a", "b"], ["full", "minimal"], [1, 2, 3])
    assert len(cells) == 12
    for arm in ("a", "b"):
        for prompt in ("full", "minimal"):
            assert sorted(s for _, a, p, s in cells if (a, p) == (arm, prompt)) == [1, 2, 3]
    assert run.seeds("1-3,7") == [1, 2, 3, 7]


def test_output_inside_the_repository_is_refused() -> None:
    with pytest.raises(SystemExit):
        run.main(["--out", str(ROOT / "results")])


# The analysis, on a fixture with known answers.


def fixture_runs(backend: str = "conky-model") -> list[dict]:
    """Arm a arrives on every seed; arm b only with the minimal prompt."""
    runs = []
    for arm in ("a", "b"):
        for prompt in ("full", "minimal"):
            for seed in (1, 2, 3, 4):
                arrived = 1.0 if arm == "a" or prompt == "minimal" else 0.0
                record = {"scenario": "trail", "probe": "", "backend": backend, "arm": arm,
                          "prompt": prompt, "seed": seed, "paired": True}  # fmt: skip
                metrics = {m: None for m in analyse.METRICS}
                metrics.update({"arrived": arrived, "mileage": 2040.0 * arrived + seed})
                runs.append({"record": record, "metrics": metrics, "dir": f"{arm}/{prompt}"})
    return runs


def test_the_analysis_separates_harness_prompt_and_interaction() -> None:
    result = analyse.analyse(fixture_runs())
    harness = {(r["a"], r["b"], r["metric"]): r for r in result["harness"]}
    gap = harness[("a/full", "b/full", "arrived")]
    assert gap["mean"] == 1.0 and gap["low"] == gap["high"] == 1.0 and gap["class"] == "harness"
    assert harness[("a/minimal", "b/minimal", "arrived")]["mean"] == 0.0
    prompt = {(r["a"], r["b"], r["metric"]): r for r in result["prompt"]}
    assert prompt[("b/full", "b/minimal", "arrived")]["mean"] == -1.0
    assert prompt[("b/full", "b/minimal", "arrived")]["class"] == "prompt"
    interaction = [r for r in result["interaction"] if r["metric"] == "arrived"][0]
    assert interaction["mean"] == 1.0 and interaction["class"] == "prompt"
    parts = [r for r in result["decomposition"] if r["metric"] == "arrived"][0]
    assert parts["grand"] == 0.75
    assert parts["arm"]["a"]["effect"] == 0.25 and parts["prompt"]["full"]["effect"] == -0.25
    assert parts["interaction"]["a x full"]["effect"] == 0.25
    assert abs(sum(parts["share"].values()) - 1) < 1e-9
    assert "Harness effect at a fixed prompt" in analyse.markdown(result)


def test_runs_without_a_model_are_mechanism_results_and_scripted_ones_are_refused() -> None:
    result = analyse.analyse(fixture_runs("adversary"))
    assert {r["class"] for r in result["harness"] + result["prompt"]} == {"mechanism"}
    with pytest.raises(analyse.Refused):
        analyse.analyse(fixture_runs("scripted"))


def test_the_bootstrap_is_fixed_and_brackets_the_mean() -> None:
    values = [0.0, 1.0, 1.0, 0.0, 1.0]
    low, high = analyse.bootstrap(values)
    assert (low, high) == analyse.bootstrap(values) and low <= 0.6 <= high


# The meter's record of calls: pay once, never share between runs.


class Counting:
    name = "counting"

    def __init__(self) -> None:
        self.calls = 0

    def complete(self, call):
        self.calls += 1
        return backends.Completion(f"answer {self.calls}", 1, 1)


def test_record_then_replay_serves_the_same_answers_without_calling(tmp_path: Path) -> None:
    ask = {"model": "m", "messages": [{"role": "user", "content": "same question"}]}
    live = Counting()
    first = Meter(live, "m", "t", Budget(9, 99), tmp_path / "a.jsonl", cache_mode="record",
                  cache=tmp_path / "run-1")  # fmt: skip
    answers = [post(first, ask)[1]["choices"][0]["message"]["content"] for _ in range(2)]
    assert answers == ["answer 1", "answer 2"] and live.calls == 2
    unused = Counting()
    again = Meter(unused, "m", "t", Budget(9, 99), tmp_path / "b.jsonl", cache_mode="replay",
                  cache=tmp_path / "run-1")  # fmt: skip
    replayed = [post(again, ask)[1]["choices"][0]["message"]["content"] for _ in range(2)]
    assert replayed == answers and unused.calls == 0
    status, missing = post(again, ask)
    assert status == 502 and missing["error"]["type"] == "cache_miss"
    trace = [json.loads(x) for x in (tmp_path / "b.jsonl").read_text().splitlines()]
    assert [x.get("cache") for x in trace] == ["replayed", "replayed", "miss"]


def test_two_runs_in_record_mode_never_share_an_answer(tmp_path: Path) -> None:
    ask = {"model": "m", "messages": [{"role": "user", "content": "the first screen"}]}
    live = Counting()
    for name in ("run-1", "run-2"):
        meter = Meter(live, "m", "t", Budget(9, 99), tmp_path / f"{name}.jsonl",
                      cache_mode="record", cache=tmp_path / name)  # fmt: skip
        assert post(meter, ask)[0] == 200
    assert live.calls == 2
