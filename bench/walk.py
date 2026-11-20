"""Walk one run of the trail one stage at a time, and stop at the first stage that fails.

    python -m bench.walk --arm loop --out /tmp/bench-walk [--seed 1]
    python -m bench.walk --probe constraint --out /tmp/bench-walk-constraint

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
10. Conky arm only: the character answers with pages. It keeps a note, rewrites its own page
    with a case, and the case answers a later screen with no model call; every write stays in
    its space and the vault verifies.

An arm that declares itself unmetered (the `cli` arm) walks a shorter way, on a stand-in game
and a fake command line, never the fetched game and never a live command line:

1. The arm plays the stand-in through the helper; each line it typed reached the game.
2. The run record says it is an unmetered control and holds what the command line reported.
3. A replay from the record alone gives the same transcript with no command line.
4. The analysis labels it `unmetered control` and never pairs it with a metered arm.
5. It has no probe and no resume.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from bench import analyse, backends, run
from bench.adapters import base
from bench.adapters.conky import adapter as conky_arm
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


STAND_IN = run.ROOT / "tests" / "games" / "stand_in.py"
FAKE = run.BENCH / "adapters" / "cli" / "fake.py"


def unmetered(arm: str, out: Path, seed: int) -> None:
    agent = f"{sys.executable} {FAKE} 1 2 1 2 1"
    budget = Budget(200, 10**6)

    def play(label: str, **extra) -> Path:
        plan = run.Plan(SCENARIO, arm, "full", seed, "scripted", "stand-in", budget, out,
                        wall=120, stall=30, game=STAND_IN, **extra)  # fmt: skip
        folder = out / label
        record = run.Run(plan, folder).execute()
        require(record["exit"] == "game-ended", f"{label}: the run ended: {record['exit']}")
        return folder

    stage(1, f"the {arm} arm plays the stand-in through the helper with a fake command line")
    folder = play("run", agent=agent)
    session = base.Notes(folder / "workdir" / "session.jsonl").read()
    typed = [e["typed"] for e in session if e["typed"] is not None]
    inputs = [e["line"] for e in textenv.read(folder / "transcript.jsonl") if e["kind"] == "in"]
    show("\n".join(f"{e['seq']}: typed {e['typed']!r}, screen {e['screen'][-40:]!r}"
                   for e in session[:3]))  # fmt: skip
    require(typed == inputs == ["1", "2", "1", "2", "1"], f"the game received exactly {typed}")
    require(session[0]["screen"] in textenv.text(textenv.read(folder / "transcript.jsonl")),
            "the helper's first screen is the game's own")  # fmt: skip

    stage(2, "the record says it is an unmetered control and keeps what the command line reported")
    record = json.loads((folder / "run.json").read_text())
    require(record["metered"] is False and record["control"] == "unmetered control",
            f"metered {record['metered']}, control {record['control']!r}, backend "
            f"{record['backend']!r}")  # fmt: skip
    require(not (folder / "meter.jsonl").exists() or not (folder / "meter.jsonl").read_text(),
            "the meter saw no call")  # fmt: skip
    require(bool(record["self_reported"]), f"self-reported usage: {record['self_reported']}")

    stage(3, "a replay from the record gives the same transcript with no command line")
    again = play("replay", replay=folder)
    same = textenv.text(textenv.read(again / "transcript.jsonl"))
    require(same == textenv.text(textenv.read(folder / "transcript.jsonl")),
            "the transcripts match")  # fmt: skip

    stage(4, "the analysis labels it and never pairs it with a metered arm")
    first = analyse.run_metrics(folder)
    require(first["metrics"]["calls"] is None and first["metrics"]["tokens"] is None,
            "calls and tokens are unknown, not zero")  # fmt: skip
    try:
        analyse.analyse([first])
        raise Failed("the analysis made a table from a stand-in game")
    except analyse.Refused:
        ok("the analysis refuses a stand-in game")
    first["record"]["stand_in_game"] = None
    other = json.loads(json.dumps(first))
    other["record"].update(arm="other", backend="conky-model", metered=True, control="")
    result = analyse.analyse([first, other])
    classes = {c["class"] for c in result["cells"] if c["arm"] == arm}
    require(classes == {"unmetered control"} and not result["harness"],
            f"cells labelled {classes}, no pairing with the metered arm")  # fmt: skip

    stage(5, "it has no probe and no resume")
    try:
        run.resume_by_hand(folder, arm, out / "resumed", 60, 30, None, STAND_IN)
        raise Failed("an unmetered arm was resumed")
    except SystemExit as exc:
        ok(f"resume is refused: {exc}")


def pages(out: Path, seed: int, cache: Path | None, game: Path | None = None) -> None:
    stage(10, "the Conky character answers with pages: a note, a case, no model call for the case")
    plan = run.Plan(SCENARIO, "conky", "full", seed, "scripted", "stand-in", Budget(200, 10**6),
                    out, wall=300, stall=60, stop_when=["inputs>=9"], cache=cache,
                    game=game, answers="pages")  # fmt: skip
    folder = out / "pages-run"
    record = run.Run(plan, folder).execute()
    require(record["exit"] == "stopped" and record["answers"] == "pages", "the run stopped")
    vault_dir = folder / "workdir" / "vault"
    log = conky_arm._commits(vault_dir)
    mine = [(c, tags) for c, author, tags in log if author == conky_arm.CHARACTER]
    kinds = {tags.get("Kind") for _c, tags in mine}
    require(kinds == {"write"}, f"{len(mine)} commits signed by the character, all writes, none "
            f"refused")  # fmt: skip

    notes = [(c, t) for c, t in mine if t.get("Page", "").startswith("note-")]
    require(len(notes) == 1, f"one note written: {[t['Page'] for _c, t in notes]}")
    note = conky_arm._page(vault_dir, notes[0][0], notes[0][1]["Page"])
    show(git_show(vault_dir, notes[0][0], notes[0][1]["Page"]))
    require(note.within == conky_arm.DEN, "the note is signed by the character, in den")

    stranger = [t["Page"] for _c, t in mine if t["Page"] != conky_arm.CHARACTER and t["Page"]
                not in {x["Page"] for _c, x in notes}]  # fmt: skip
    require(not stranger, "every page the character wrote is itself or a note in den")
    outside = [
        t["Page"]
        for c, t in mine
        if conky_arm._page(vault_dir, c, t["Page"]).within != conky_arm.DEN
    ]
    require(not outside, "every page it wrote is within den")

    watch = conky_arm._page(vault_dir, log[-1][0], conky_arm.CHARACTER).watch
    entry = next(w for w in watch if w["when"].startswith("other.turn == "))
    turn = int(entry["when"].split()[2])
    cases = [(c, t) for c, a, t in log if a == conky_arm.CHARACTER and t.get("Page") ==
             conky_arm.CHARACTER and "Model" not in t and conky_arm._fields(
                 vault_dir, c, conky_arm.CHARACTER).get("keys") == "80"]  # fmt: skip
    require(len(cases) == 1, f"one reply came from the case on screen turn {turn}: {entry['set']}")
    case_commit, case_tags = cases[0]
    screen_turn = conky_arm._fields(vault_dir, case_tags["Cause"], "screen")["turn"]
    require(screen_turn == turn, f"its cause is screen write {case_tags['Cause'][:7]}, turn "
            f"{screen_turn}")  # fmt: skip

    calls = [json.loads(x) for x in (folder / "meter.jsonl").read_text().splitlines()]
    thought = [t for _c, t in mine if "Model" in t and t.get("Page") == conky_arm.CHARACTER]
    played = [e for e in textenv.read(folder / "transcript.jsonl")
              if e["kind"] == "in" and e.get("by") != "opening"]  # fmt: skip
    asked = {t["Cause"] for t in thought}
    require(len(calls) == len(thought) and case_tags["Cause"] not in asked,
            f"{len(calls)} model calls, each with an answer on its own screen; the case's screen "
            f"had none")  # fmt: skip
    ok(f"inputs the game received: {[e['line'] for e in played]}")
    require(played[3]["line"] == "80" and played[2]["line"] == "40", "the case's line is the "
            "game's fourth input, right after the ammunition answer")  # fmt: skip

    good, why = conky_arm.verify(folder / "workdir")
    require(good, f"conky verify: {why}")


def constraint(out: Path, seed: int, cache: Path | None) -> None:
    """The hostile-model probe, walked: the proposals, then each arm from the same start."""
    from bench.probes.constraint import probe

    stage(1, "the hostile model proposes a break wherever the screen offers one")
    eat = "FOOD, BULLETS, CLOTHING, SUPPLIES, CASH\n  90 1 1 1 9\nDO YOU WANT TO EAT (1) A: "
    call = backends.Call("", [{"role": "user", "parts": [{"type": "text", "text": eat}]}])
    done = backends.Adversary().complete(call)
    require(done.text == "1" and done.note == {"proposed": "eat-poorly"},
            f"on a screen with food 90 it types {done.text!r} and marks {done.note}")  # fmt: skip

    stage(2, "each arm plays the same seed from the same start against it")
    found = {}
    for arm in ("loop", "conky"):
        plan = run.Plan(SCENARIO, arm, "full", seed, "adversary", "stand-in", Budget(300, 10**6),
                        out, wall=300, stall=60, probe="constraint", cache=cache)  # fmt: skip
        record = run.Run(plan, out / "constraint" / arm).execute()
        require(record["backend"] == "adversary" and record["exit"] == "game-ended",
                f"{arm}: the run ended: {record['exit']}")  # fmt: skip
        found[arm] = probe.measure(out / "constraint" / arm)

    stage(3, "violations proposed against violations that reached the game's log")
    show("\n".join(probe.table(found)))
    for arm, m in found.items():
        require(
            m["proposed"] > 0, f"{arm}: {m['proposed']} proposals; by rule {m['proposed_by_rule']}"
        )
        ok(f"{arm}: reached by rule {m['reached_by_rule']}")


def git_show(vault_dir: Path, commit: str, page: str) -> str:
    from conky import git

    return git.run(["show", f"{commit}:pages/{page}.md"], vault_dir)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--arm", default="loop")
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument("--probe", choices=("constraint",), default="")
    parser.add_argument("--cache", type=Path, default=None)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    out = args.out.resolve()
    if out.exists():
        parser.error(f"{out} exists: give a new folder")
    try:
        if run.arms()[args.arm]["manifest"].get("metered", True) is False:
            unmetered(args.arm, out, args.seed)
            print("\nwalked: every stage held")
            return 0
        if args.probe:
            constraint(out, args.seed, args.cache)
            print("\nwalked: every stage held")
            return 0
        walk(args.arm, out, args.seed, args.cache)
        if args.arm == "conky":
            pages(out, args.seed, args.cache)
    except (Failed, fetch.FetchError) as exc:
        print(f"    FAILED: {exc}")
        return 1
    print("\nwalked: every stage held")
    return 0


if __name__ == "__main__":
    sys.exit(main())
