"""Walk one run of the trail one stage at a time, and stop at the first stage that fails.

    python -m bench.walk --arm loop --out /tmp/bench-walk [--seed 1]

Each stage prints what now exists and what was checked. Every stage uses the `scripted`
backend; no model is called. The first stage fetches the game if it is not cached.

1. The game is fetched and its hash verified.
2. It launches under the launcher, and the same seed gives the same first screen twice.
3. The fixed opening reaches the first gameplay question and is recorded.
4. The meter starts, and one call is recorded with its budget accounting.
5. The arm's single agent receives the first screen: shown byte for byte, with its scaffolding.
6. It answers, and exactly that answer reaches the game: the game's own transcript line.
7. One more full turn round the loop.
8. The stop point halts cleanly, and a fresh process carries on at the next input.
9. The run ends, and the analysis reads it.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from bench import analyse, backends, run
from bench.adapters import base
from bench.envs import textenv
from bench.envs.oregon_trail_1975 import fetch
from bench.meter import Budget, Meter

SCENARIO = run.BENCH / "scenarios" / "trail"


class Failed(Exception):
    pass


def show(text: str, indent: str = "    | ") -> None:
    for line in text.rstrip("\n").split("\n"):
        print(indent + line)


def stage(n: int, title: str) -> None:
    print(f"\n[{n}] {title}")


def ok(what: str) -> None:
    print(f"    ok: {what}")


def require(condition: bool, what: str) -> None:
    if not condition:
        raise Failed(what)
    ok(what)


def first_screen(game: Path, seed: int, folder: Path, opening: list[str]) -> list[dict]:
    transcript = folder / "transcript.jsonl"
    command = [sys.executable, str(run.LAUNCH), "--game", str(game), "--seed", str(seed)]
    command += ["--transcript", str(transcript)]
    for line in opening:
        command += ["--opening", line]
    folder.mkdir(parents=True)
    subprocess.run(command, stdin=subprocess.DEVNULL, capture_output=True, check=False)
    return textenv.read(transcript)


def walk(arm: str, out: Path, seed: int, cache: Path | None) -> None:
    config = json.loads((SCENARIO / "scenario.json").read_text())
    stage(1, "the game is fetched and its hash verified")
    game = fetch.fetch(cache)
    require(fetch.digest(game) == fetch.MAIN_SHA256, f"{game} has SHA-256 {fetch.MAIN_SHA256}")

    stage(2, "the same seed gives the same first screen twice")
    one = textenv.text(first_screen(game, seed, out / "launch-1", []))
    two = textenv.text(first_screen(game, seed, out / "launch-2", []))
    require(bool(one.strip()) and one == two, f"two launches with seed {seed} showed the same")
    show(one[-300:])

    stage(3, "the fixed opening reaches the first gameplay question")
    events = first_screen(game, seed, out / "launch-3", config["opening"])
    opened = [e for e in events if e["kind"] == "in"]
    require(
        [e.get("by") for e in opened] == ["opening"],
        f"opening recorded: {[(e['n'], e['line'], e['by']) for e in opened]}",
    )
    screen = textenv.text(events)
    require("OXEN" in screen.split("\n")[-1], "the screen ends at the first purchase question")
    show(screen[-400:])

    stage(4, "the meter starts and one call is recorded with its budget")
    pack = base.Pack.load(SCENARIO / "prompts" / "full")
    trace = out / "meter-check.jsonl"
    meter = Meter(backends.Scripted(), "stand-in", "t", Budget(3, 10**6), trace,
                  [pack.task, pack.rules])  # fmt: skip
    url = meter.start()
    try:
        messages = [{"role": "user", "content": pack.mark(pack.task) + base.mark_screen(screen)}]
        status, answer = base.ask_meter(url, "t", "stand-in", messages)
    finally:
        meter.stop()
    entry = json.loads(trace.read_text().splitlines()[0])
    require(status == 200 and entry["budget_after"] == {"calls": 1, "tokens": entry[
        "tokens_in"] + entry["tokens_out"]}, f"call recorded, answer {answer!r}, budget "
        f"{entry['budget_after']}")  # fmt: skip

    stage(5, f"the {arm} agent receives the first screen")
    plan = run.Plan(SCENARIO, arm, "full", seed, "scripted", "stand-in", Budget(200, 10**6),
                    out, wall=300, stall=60, stop_when=["inputs>=3"], cache=cache)  # fmt: skip
    folder = out / "run"
    record = run.Run(plan, folder).execute()
    calls = [json.loads(x) for x in (folder / "meter.jsonl").read_text().splitlines()]
    require(len(calls) >= 1, f"{len(calls)} model calls recorded")
    first = calls[0]
    received = "\n".join(
        p["text"] for m in first["request"]["messages"] for p in m["parts"] if "text" in p
    )
    show((first["request"]["system"] + "\n" + received)[-1200:])
    ok(f"pack {first['pack_bytes']} bytes (verbatim: {first['pack_ok']}), screen "
       f"{first['screen_bytes']} bytes, scaffolding {first['scaffold_bytes']} bytes")  # fmt: skip

    stage(6, "it answers and exactly that answer reaches the game")
    inputs = [e for e in textenv.read(folder / "transcript.jsonl") if e["kind"] == "in"]
    played = [e for e in inputs if e.get("by") != "opening"]
    require(bool(played), "the game received an input from the arm")
    require(
        played[0]["line"].strip() == first["response_text"].strip(),
        f"model answered {first['response_text']!r}; game log: {json.dumps(played[0])}",
    )

    stage(7, "one more full turn round the loop")
    require(len(played) >= 2 and len(calls) >= 2, f"second answer {calls[1]['response_text']!r} "
            f"reached the game as {played[1]['line']!r}")  # fmt: skip
    require(played[1]["line"].strip() == calls[1]["response_text"].strip(), "they match")

    stage(8, "the stop point halts cleanly and a fresh process carries on")
    require(record["exit"] == "stopped", f"the run stopped: {record['exit']}")
    resumed = run.resume_by_hand(folder, arm, out / "resumed", 300, 60, cache)
    later = next((out / "resumed").glob("*/transcript.jsonl"))
    events = textenv.read(later)
    numbers = [e["n"] for e in events if e["kind"] == "in"]
    starts = [e for e in events if e["kind"] == "start"]
    require(len(starts) == 2 and starts[1]["resumed"], "the game started again from its record")
    require(
        numbers == list(range(1, len(numbers) + 1)) and len(numbers) > len(inputs),
        f"inputs carry on without a gap or a repeat: {numbers[:6]}...{numbers[-2:]}",
    )

    stage(9, "the run ends and the analysis reads it")
    require(resumed["exit"] == "game-ended", f"the run ended: {resumed['exit']}")
    metrics = analyse.run_metrics(later.parent)["metrics"]
    require(metrics["outcome"] in ("arrived", "died"), f"the game reached its own end: "
            f"{metrics['outcome']}")  # fmt: skip
    show(json.dumps({k: metrics[k] for k in ("outcome", "mileage", "inputs", "invalid",
                                             "violations", "calls", "tokens")}))  # fmt: skip
    try:
        analyse.analyse([analyse.run_metrics(later.parent)])
        raise Failed("the analysis made a table from a scripted run")
    except analyse.Refused as exc:
        ok(f"the analysis refuses to report it: {str(exc).splitlines()[1].strip()}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--arm", default="loop")
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument("--cache", type=Path, default=None)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    out = args.out.resolve()
    if out.exists():
        parser.error(f"{out} exists: give a new folder")
    try:
        walk(args.arm, out, args.seed, args.cache)
    except (Failed, fetch.FetchError) as exc:
        print(f"    FAILED: {exc}")
        return 1
    print("\nwalked: every stage held")
    return 0


if __name__ == "__main__":
    sys.exit(main())
