"""The runner: runs a matrix of (scenario, arm, prompt variant, seed), each in its own directory.

    python -m bench.run --scenario trail --arms conky,loop,floor-continue \\
        --prompts full,minimal --seeds 1-5 --backend scripted --model stand-in \\
        --calls 200 --tokens 400000 --out /tmp/bench-results

Every run gets a fresh directory under `--out` (never inside this repository) holding the
game's transcript (`transcript.jsonl`, the ground truth), the meter's trace (`meter.jsonl`),
the shelf log (`shelf.jsonl`), the arm's standard output and error per segment, its working
directory and home, and `run.json`. Seeds are paired: every arm and variant plays the same seeds.

Options for experiments and debugging:

- `--stop-when COND` (repeatable): end the run when a condition holds on the state the game
  printed, tested before each input: `turn>=8`, `food<50`, `prompt==eat`, `inputs>=20`.
  The exit reason is `stopped` and everything stays on disk.
- `--resume RUN_DIR [--arm NAME]`: carry on a stopped run in a fresh process, of the same arm
  (handed its working directory) or of another arm (handed nothing but the world).
- `--step`: after each input, print the screen, the line typed and the model calls made for
  it, and wait for Enter. One run only.
- `--probe resume|portability|constraint|overhead`: see `bench/probes/`.
- `--agent COMMAND`, `--replay RUN_DIR`: for the `cli` arm only, a stock agent command line
  outside the meter. `--agent` replaces its command line; `--replay` types the lines a finished
  run recorded, with no command line at all. It has no probes and no resume, and its results are
  never pooled with metered arms (see `bench/adapters/cli/README.md`).

- `--cache-mode branch --replay-from RESULTS_DIR [--live-from CALL]`: answer from an earlier
  run's record while a request matches it, and go live from the first that does not, or from
  call number CALL. `run.json` gets `branched_from`, `live_from`, `replayed_calls` and
  `live_calls`.

A stepped run, a run resumed by hand, a branched run and a run on the `scripted` backend are
marked in `run.json` and are never reported as results.
"""

from __future__ import annotations

import argparse
import contextlib
import itertools
import json
import os
import platform
import secrets
import shutil
import signal
import subprocess
import sys
import time
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path

from bench import backends
from bench.envs import textenv
from bench.envs.oregon_trail_1975 import fetch
from bench.meter import Budget, Meter

ROOT = Path(__file__).resolve().parent.parent
BENCH = ROOT / "bench"
LAUNCH = BENCH / "envs" / "oregon_trail_1975" / "launch.py"
PROBES = ("resume", "portability", "constraint", "overhead")
SAMPLE = 5


def arms() -> dict[str, dict]:
    """Every arm declared by an adapter manifest, with its directory and manifest."""
    found = {}
    for manifest in sorted((BENCH / "adapters").glob("*/adapter.json")):
        data = json.loads(manifest.read_text())
        for name, command in data["arms"].items():
            found[name] = {"dir": manifest.parent, "command": command, "manifest": data}
    return found


def expand(command: list[str], folder: Path) -> list[str]:
    out = []
    for part in command:
        part = part.replace("{python}", sys.executable)
        if not part.startswith("-") and (folder / part).exists():
            part = str(folder / part)
        out.append(part)
    return out


def seeds(text: str) -> list[int]:
    found = []
    for piece in text.split(","):
        first, _, last = piece.partition("-")
        found += list(range(int(first), int(last or first) + 1))
    return found


def git_commit() -> str:
    done = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True, check=False
    )
    dirty = subprocess.run(
        ["git", "status", "--porcelain"], cwd=ROOT, capture_output=True, text=True, check=False
    )
    return done.stdout.strip() + ("+changes" if dirty.stdout.strip() else "")


def now() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


@dataclass
class Plan:
    """One run: what to run and how it is limited."""

    scenario: Path
    arm: str
    prompt: str
    seed: int
    backend: str
    model: str
    budget: Budget
    out: Path
    wall: float = 1800
    stall: float = 300
    stop_when: list[str] = field(default_factory=list)
    probe: str = ""
    step: bool = False
    recording: Path | None = None
    cache: Path | None = None
    game: Path | None = None
    cache_mode: str = ""
    replay_from: Path | None = None
    live_from: int | None = None
    answers: str = "keys"
    agent: str = ""
    replay: Path | None = None


class Run:
    def __init__(self, plan: Plan, folder: Path) -> None:
        self.plan, self.dir = plan, folder
        self.dir.mkdir(parents=True, exist_ok=False)
        self.transcript = self.dir / "transcript.jsonl"
        self.token = secrets.token_hex(16)
        self.record: dict = {}
        config = json.loads((plan.scenario / "scenario.json").read_text())
        self.config = config
        self.shelf = config["prompts"][plan.prompt]["shelf"]
        self.prompts = plan.scenario / "prompts" / plan.prompt
        self.arm = arms()[plan.arm]

    def environment(self, resume: bool, stop_when: list[str], game: Path) -> list[str]:
        command = [sys.executable, str(LAUNCH), "--game", str(game), "--seed", str(self.plan.seed)]
        command += ["--transcript", str(self.transcript)]
        for condition in stop_when:
            command += ["--stop-when", condition]
        for line in [] if self.plan.game else self.config.get("opening", []):
            command += ["--opening", line]
        if self.plan.step:
            (self.dir / "step").mkdir(exist_ok=True)
            command += ["--step-dir", str(self.dir / "step")]
        if resume:
            command.append("--resume")
        return command

    def adapter(self, workdir: Path, url: str, resume: bool, env_command: list[str]) -> list[str]:
        command = expand(self.arm["command"], self.arm["dir"])
        command += ["--scenario", str(self.plan.scenario), "--prompts", str(self.prompts)]
        command += ["--workdir", str(workdir), "--meter", url, "--token", self.token]
        command += ["--model", self.plan.model, "--seed", str(self.plan.seed)]
        command += ["--calls", str(self.plan.budget.calls)]
        command += ["--tokens", str(self.plan.budget.tokens)]
        if self.plan.answers != "keys":
            command += ["--answers", self.plan.answers]
        if self.plan.agent:
            command += ["--agent", self.plan.agent]
        if self.plan.replay:
            command += ["--replay", str(self.plan.replay)]
        if self.shelf:
            command.append("--shelf")
        if resume:
            command.append("--resume")
        return [*command, "--", *env_command]

    def segment(
        self,
        n: int,
        meter: Meter,
        url: str,
        workdir: Path,
        home: Path,
        *,
        resume: bool,
        stop_when: list[str],
        game: Path,
        resume_game: bool | None = None,
    ) -> dict:
        """Run the arm once until the game ends, a limit is hit, or a stop condition holds."""
        home.mkdir(parents=True, exist_ok=True)
        workdir.mkdir(parents=True, exist_ok=True)
        env = {**os.environ, "HOME": str(home), "NO_PROXY": "127.0.0.1,localhost"}
        env["no_proxy"] = env["NO_PROXY"]
        env["PYTHONPATH"] = os.pathsep.join(filter(None, [str(ROOT), env.get("PYTHONPATH")]))
        replay = resume if resume_game is None else resume_game
        command = self.adapter(workdir, url, resume, self.environment(replay, stop_when, game))
        started = time.time()
        with (
            (self.dir / f"adapter-{n}.out").open("w") as out,
            (self.dir / f"adapter-{n}.err").open("w") as err,
        ):
            proc = subprocess.Popen(
                command, stdout=out, stderr=err, env=env, start_new_session=True
            )
            reason = self.watch(proc, meter, started)
        self.kill_game()
        return {
            "segment": n,
            "command": command,
            "start": started,
            "end": time.time(),
            "exit": reason,
            "returncode": proc.returncode,
            "resume": resume,
        }

    def watch(self, proc: subprocess.Popen, meter: Meter, started: float) -> str:
        size, changed, finished, paused = -1, time.time(), None, set()
        while True:
            if proc.poll() is not None:
                return self.ending() or f"adapter exited with {proc.returncode}"
            current = self.transcript.stat().st_size if self.transcript.exists() else 0
            if current != size:
                size, changed = current, time.time()
            if self.plan.step:
                self.step(paused)
                changed = time.time()
            reason = None
            if finished is None and self.ending():
                finished = time.time()
            if finished is not None and time.time() - finished > 20:
                reason = self.ending()
            elif meter.exhausted:
                reason = "budget-exhausted"
            elif time.time() - started > self.plan.wall:
                reason = "wall-clock"
            elif time.time() - changed > self.plan.stall:
                reason = "stalled"
            if reason:
                stop(proc)
                return reason
            time.sleep(0.1)

    def ending(self) -> str | None:
        events = textenv.read(self.transcript)
        ends = [e for e in events if e["kind"] == "end"]
        if not ends:
            return None
        return "stopped" if ends[-1].get("outcome") == "stopped" else "game-ended"

    def kill_game(self) -> None:
        for event in textenv.read(self.transcript):
            if event["kind"] == "start" and event.get("pid"):
                with contextlib.suppress(ProcessLookupError, PermissionError):
                    os.kill(event["pid"], signal.SIGKILL)

    def step(self, paused: set) -> None:
        folder = self.dir / "step"
        for path in sorted(folder.glob("paused-*"), key=lambda p: int(p.name.split("-")[1])):
            n = int(path.name.split("-")[1])
            if n in paused:
                continue
            paused.add(n)
            events = textenv.read(self.transcript)
            inputs = [e for e in events if e["kind"] == "in"]
            calls = []
            trace = self.dir / "meter.jsonl"
            if trace.exists():
                calls = [json.loads(x) for x in trace.read_text().splitlines()]
            shown = textenv.text(events[-40:])
            print(f"\n=== before input {n} ===\n{shown[-1500:]}")
            if inputs:
                print(f"--- last line typed: {inputs[-1]['line']!r}")
            print(f"--- model calls so far: {len(calls)}")
            for call in calls[-3:]:
                print(
                    f"    call {call['n']}: status {call['status']}, "
                    f"answer {call.get('response_text', '')[:60]!r}"
                )
            input("--- press Enter for the next input ")
            (folder / f"go-{n}").write_text("go")

    def execute(self) -> dict:
        plan = self.plan
        game = plan.game or fetch.fetch(plan.cache)
        backend_name = plan.backend
        if plan.probe == "constraint":
            backend_name = "adversary"
        if plan.probe == "overhead":
            backend_name = "fixed"
        backend = backends.make(backend_name, plan.recording)
        packs = [(self.prompts / n).read_text(encoding="utf-8") for n in ("task.md", "rules.md")]
        shelf_dir = plan.scenario / "shelf" if self.shelf else None
        manifest = self.arm["manifest"]
        control = manifest.get("control", "") if manifest.get("metered", True) is False else ""
        if control:
            backend_name = control
        mode = plan.cache_mode or ("off" if backend_name in backends.MODEL_FREE else "record")
        if control:
            mode = "off"
        meter = Meter(
            backend,
            plan.model,
            self.token,
            plan.budget,
            self.dir / "meter.jsonl",
            packs,
            shelf_dir,
            self.dir / "shelf.jsonl",
            mode,
            self.dir / "cache",
            plan.replay_from,
            plan.live_from,
        )
        url = meter.start()
        workdir, home = self.dir / "workdir", self.dir / "home"
        segments = []
        self.record = {
            "scenario": plan.scenario.name,
            "scenario_version": self.config["version"],
            "arm": plan.arm,
            "uses_model": self.arm["manifest"].get("uses_model", True),
            "prompt": plan.prompt,
            "prompt_sha256": fetch.digest(self.prompts / "task.md")[:16]
            + fetch.digest(self.prompts / "rules.md")[:16],
            "shelf": self.shelf,
            "seed": plan.seed,
            "paired": self.config.get("paired_seeds", True),
            "model": plan.model,
            "backend": backend_name,
            "backend_detail": getattr(backend, "describe", lambda: {})(),
            "recording_source": getattr(backend, "source", None),
            "budget": {"calls": plan.budget.calls, "tokens": plan.budget.tokens},
            "wall": plan.wall,
            "stall": plan.stall,
            "probe": plan.probe,
            "stop_when": plan.stop_when,
            "step": plan.step,
            "manual_resume": False,
            "stand_in_game": str(plan.game) if plan.game else None,
            "answers": plan.answers,
            "metered": not control,
            "control": control,
            "agent": plan.agent,
            "replay_session": str(plan.replay) if plan.replay else None,
            "cache_mode": mode,
            "replay_from": str(plan.replay_from) if plan.replay_from else None,
            "branched_from": str(plan.replay_from.parent) if mode == "branch" else None,
            "live_from": plan.live_from if mode == "branch" else None,
            "versions": {
                "python": platform.python_version(),
                "repository": git_commit(),
                "game": {
                    "repository": fetch.REPOSITORY,
                    "commit": fetch.COMMIT,
                    "main_sha256": fetch.MAIN_SHA256,
                },
            },
            "start": now(),
        }
        try:
            if plan.probe in ("resume", "portability"):
                first = plan.stop_when or ["turn>=6"]
                segments.append(
                    self.segment(
                        1, meter, url, workdir, home, resume=False, stop_when=first, game=game
                    )
                )
                if plan.probe == "portability":
                    workdir, home = self.port(workdir)
                if segments[-1]["exit"] == "stopped":
                    segments.append(
                        self.segment(
                            2, meter, url, workdir, home, resume=True, stop_when=[], game=game
                        )
                    )
            else:
                segments.append(
                    self.segment(
                        1,
                        meter,
                        url,
                        workdir,
                        home,
                        resume=False,
                        stop_when=plan.stop_when,
                        game=game,
                    )
                )
        finally:
            meter.stop()
        self.record["segments"] = segments
        self.record["exit"] = segments[-1]["exit"]
        self.record["end"] = now()
        if mode == "branch":
            self.record["replayed_calls"] = meter.branched["replayed"]
            self.record["live_calls"] = meter.branched["live"]
        self.record["accountability"] = self.accountability(workdir)
        self.record["self_reported"] = self.self_reported(workdir) if control else None
        self.record["shelf_reads_recorded"] = self.shelf_reads(workdir)
        (self.dir / "run.json").write_text(json.dumps(self.record, indent=1, default=str))
        return self.record

    def run_tool(self, key: str, workdir: Path, *extra: str) -> tuple[int, str]:
        command = self.arm["manifest"].get(key)
        if not command:
            return -1, ""
        full = expand(command, self.arm["dir"]) + ["--workdir", str(workdir), *extra]
        env = {**os.environ, "PYTHONPATH": str(ROOT)}
        done = subprocess.run(
            full, capture_output=True, text=True, env=env, check=False, timeout=120
        )
        return done.returncode, done.stdout.strip()

    def port(self, workdir: Path) -> tuple[Path, Path]:
        """Copy only the arm's declared state to a new place with a new home, and verify it."""
        target = self.dir / "ported" / "workdir"
        target.mkdir(parents=True)
        for name in self.arm["manifest"].get("state", []):
            source = workdir / name
            if source.is_dir():
                shutil.copytree(source, target / name)
            elif source.exists():
                shutil.copy2(source, target / name)
        code, out = self.run_tool("verify", target)
        self.record["portability"] = {
            "copied": self.arm["manifest"].get("state", []),
            "verify_code": code,
            "verify": out,
        }
        return target, self.dir / "ported" / "home"

    def accountability(self, workdir: Path) -> dict:
        """Ask the arm's own record what caused a sample of the inputs the game received."""
        inputs = [
            e
            for e in textenv.read(self.transcript)
            if e["kind"] == "in" and e.get("by") != "opening"
        ]
        declared = bool(self.arm["manifest"].get("explain"))
        if not inputs or not declared:
            return {"declared": declared, "sampled": 0, "answerable": 0}
        code, out = self.run_tool("explain", workdir)
        answers = json.loads(out) if code == 0 and out else []
        matched = align([e["line"] for e in inputs], answers)
        step = max(1, len(inputs) // SAMPLE)
        checked = []
        for index in range(0, len(inputs), step)[:SAMPLE]:
            found = matched[index]
            ok = bool(found and found.get("actor") and found.get("cause"))
            checked.append(
                {"n": inputs[index]["n"], "line": inputs[index]["line"], "found": found, "ok": ok}
            )
        return {
            "declared": True,
            "sampled": len(checked),
            "answerable": sum(1 for c in checked if c["ok"]),
            "checked": checked,
        }

    @staticmethod
    def self_reported(workdir: Path) -> dict | None:
        """What an unmetered arm's command line said about its own usage: never checked."""
        path = workdir / "report.json"
        return json.loads(path.read_text()).get("self_reported") if path.exists() else None

    def shelf_reads(self, workdir: Path) -> list:
        code, out = self.run_tool("shelf_reads", workdir)
        if code != 0 or not out:
            return []
        found = json.loads(out)
        with (self.dir / "shelf.jsonl").open("a") as handle:
            for read in found:
                handle.write(json.dumps({**read, "source": "arm-record"}) + "\n")
        return found


def align(lines: list[str], answers: list[dict], window: int = 3) -> list[dict | None]:
    """Match each line the game received to the arm's record of the answer it typed.

    Both lists are in order. An answer the game never received (typed as a run was stopped)
    is skipped, looking at most `window` answers ahead.
    """
    matched: list[dict | None] = []
    at = 0
    for line in lines:
        found = None
        for ahead in range(at, min(at + window, len(answers))):
            if str(answers[ahead].get("keys", "")).strip() == line.strip():
                found, at = answers[ahead], ahead + 1
                break
        matched.append(found)
    return matched


def stop(proc: subprocess.Popen) -> None:
    try:
        os.killpg(proc.pid, signal.SIGTERM)
        proc.wait(timeout=5)
    except (ProcessLookupError, subprocess.TimeoutExpired):
        with contextlib.suppress(ProcessLookupError):
            os.killpg(proc.pid, signal.SIGKILL)
        proc.wait()


def resume_by_hand(
    source: Path,
    arm: str | None,
    out: Path,
    wall: float,
    stall: float,
    cache: Path | None,
    stand_in: Path | None = None,
) -> dict:
    """Carry on a stopped run in a fresh process; marked as never a reported result."""
    old = json.loads((source / "run.json").read_text())
    arm = arm or old["arm"]
    if arms()[arm]["manifest"].get("metered", True) is False:
        raise SystemExit(f"arm {arm!r} is unmetered and cannot be resumed: replay it with --replay")
    plan = Plan(
        BENCH / "scenarios" / old["scenario"],
        arm,
        old["prompt"],
        old["seed"],
        old["backend"],
        old["model"],
        Budget(**old["budget"]),
        out,
        wall,
        stall,
        cache=cache,
        answers=old.get("answers", "keys"),
    )
    folder = out / f"{source.name}-resumed-{arm}-{secrets.token_hex(3)}"
    run = Run(plan, folder)
    shutil.copy2(source / "transcript.jsonl", run.transcript)
    same = arm == old["arm"]
    if same and (source / "workdir").exists():
        shutil.copytree(source / "workdir", folder / "workdir")
    game = stand_in or fetch.fetch(cache)
    backend = backends.make(plan.backend)
    packs = [(run.prompts / n).read_text(encoding="utf-8") for n in ("task.md", "rules.md")]
    meter = Meter(
        backend,
        plan.model,
        run.token,
        plan.budget,
        folder / "meter.jsonl",
        packs,
        plan.scenario / "shelf" if run.shelf else None,
        folder / "shelf.jsonl",
    )
    url = meter.start()
    try:
        segment = run.segment(
            1,
            meter,
            url,
            folder / "workdir",
            folder / "home",
            resume=same,
            stop_when=[],
            game=game,
            resume_game=True,
        )
    finally:
        meter.stop()
    record = {
        "scenario": old["scenario"],
        "arm": arm,
        "prompt": old["prompt"],
        "seed": old["seed"],
        "backend": plan.backend,
        "model": plan.model,
        "manual_resume": True,
        "resumed_from": str(source),
        "segments": [segment],
        "exit": segment["exit"],
    }
    (folder / "run.json").write_text(json.dumps(record, indent=1, default=str))
    return record


def matrix(scenario: str, arm_names: list[str], prompts: list[str], seed_list: list[int]):
    """The full crossing, seeds innermost so every arm and variant plays the same seeds."""
    return list(itertools.product([scenario], arm_names, prompts, seed_list))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--scenario", default="trail")
    parser.add_argument("--arms", default="conky,loop,floor-continue,floor-random")
    parser.add_argument("--prompts", default="full")
    parser.add_argument("--seeds", default="1")
    parser.add_argument("--backend", default="scripted", choices=backends.BACKENDS)
    parser.add_argument("--recording", type=Path, default=None)
    parser.add_argument("--model", default="stand-in")
    parser.add_argument("--calls", type=int, default=200)
    parser.add_argument("--tokens", type=int, default=400_000)
    parser.add_argument("--wall", type=float, default=1800)
    parser.add_argument("--stall", type=float, default=300)
    parser.add_argument("--stop-when", action="append", default=[])
    parser.add_argument("--probe", choices=PROBES, default="")
    parser.add_argument("--step", action="store_true")
    parser.add_argument("--resume", type=Path, default=None, help="a stopped run's directory")
    parser.add_argument("--arm", default=None, help="with --resume: the arm to hand it to")
    parser.add_argument("--cache", type=Path, default=None, help="where the game is fetched to")
    parser.add_argument(
        "--game", type=Path, default=None, help="a stand-in game program, for tests only"
    )
    parser.add_argument(
        "--cache-mode",
        choices=("record", "replay", "branch", "off"),
        default="",
        help="model calls: record (default with a model), replay (stored answers only), "
        "branch (stored answers while the request matches, live from the first that does not), off",
    )
    parser.add_argument(
        "--replay-from",
        type=Path,
        default=None,
        help="with --cache-mode replay or branch: the results dir of the run to read answers from",
    )
    parser.add_argument(
        "--live-from",
        type=int,
        default=None,
        metavar="CALL",
        help="with --cache-mode branch: go live from this call number (the meter's own count of "
        "calls in the run, from 1) even where the request matches a stored answer",
    )
    parser.add_argument(
        "--answers",
        choices=("keys", "pages"),
        default="keys",
        help="for an arm that declares it: what an answer is, a line to type or a line and pages",
    )
    parser.add_argument(
        "--agent",
        default="",
        help="for an arm that declares it: the command line it runs, {model} filled in",
    )
    parser.add_argument(
        "--replay",
        type=Path,
        default=None,
        help="for an arm that declares it: type the lines a finished run recorded, no command line",
    )
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    out = args.out.resolve()
    if out == ROOT or ROOT in out.parents:
        parser.error(f"--out {out} is inside the repository: choose a folder outside it")
    if args.resume:
        record = resume_by_hand(
            args.resume.resolve(),
            args.arm,
            out,
            args.wall,
            args.stall,
            args.cache,
            args.game.resolve() if args.game else None,
        )
        print(json.dumps({"exit": record["exit"], "dir": str(out)}))
        return 0
    known = arms()
    chosen = [a.strip() for a in args.arms.split(",") if a.strip()]
    for name in chosen:
        if name not in known:
            parser.error(f"unknown arm {name!r}: known arms are {', '.join(sorted(known))}")
    if args.answers != "keys":
        for name in chosen:
            if args.answers not in known[name]["manifest"].get("answers", ["keys"]):
                parser.error(f"arm {name!r} has no --answers {args.answers}")
    for name in chosen:
        manifest = known[name]["manifest"]
        if (args.agent or args.replay) and not manifest.get("agent"):
            parser.error(f"arm {name!r} takes no --agent or --replay")
        if args.probe and manifest.get("metered", True) is False:
            parser.error(f"arm {name!r} is unmetered: it has no --probe, see its README")
    if args.cache_mode == "branch" and not args.replay_from:
        parser.error("--cache-mode branch needs --replay-from RESULTS_DIR, the run to branch from")
    if args.live_from is not None and args.cache_mode != "branch":
        parser.error("--live-from only applies with --cache-mode branch")
    cells = matrix(args.scenario, chosen, args.prompts.split(","), seeds(args.seeds))
    if args.step and len(cells) != 1:
        parser.error("--step runs exactly one run: give one arm, one prompt and one seed")
    scenario = BENCH / "scenarios" / args.scenario
    for name, arm, prompt, seed in cells:
        plan = Plan(
            scenario,
            arm,
            prompt,
            seed,
            args.backend,
            args.model,
            Budget(args.calls, args.tokens),
            out,
            args.wall,
            args.stall,
            args.stop_when,
            args.probe,
            args.step,
            args.recording,
            args.cache,
            args.game.resolve() if args.game else None,
            args.cache_mode,
            live_from=args.live_from,
            answers=args.answers,
            agent=args.agent,
            replay=args.replay.resolve() if args.replay else None,
        )
        label = f"{name}/{arm}/{prompt}/seed-{seed}" + (f"-{args.probe}" if args.probe else "")
        if args.replay_from:
            plan.replay_from = args.replay_from.resolve() / label / "cache"
        folder = out / label
        if folder.exists():
            print(f"skip {label}: already run")
            continue
        record = Run(plan, folder).execute()
        print(f"{label}: {record['exit']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
