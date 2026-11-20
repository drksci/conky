"""Run the 1975 Oregon Trail port deterministically, without changing a line of it.

The port reads three things that change between runs, and the launcher pins each from outside
before running `main.py` with `runpy`:

- `random`: seeded with `--seed` before the game starts.
- `datetime.datetime.now()`: event selection draws `random.randint(minutes, 100)` with the minutes
  of the current hour, so later in the hour gives harder events. It always reports minute 30.
- `time.time()`: the shooting sequence ("TYPE BANG") scores the seconds between the prompt and
  the answer, so it would measure a player's latency, not its judgement. The clock advances by
  exactly 2 seconds on every read, so every shot takes 2 seconds whoever types it: a fair shot,
  neither the best (1 second or less) nor a poor one.

Every input and output passes through a `textenv.Session`, which records the transcript, the
runner's stop conditions and steps, and resumes by replay. A line the game cannot read as a
number ends the game, as it does in the port; the launcher records it as a crash and prints one
line saying so.

    python launch.py --game main.py --seed 7 --transcript run/transcript.jsonl \\
        [--stop-when turn>=8] [--step-dir DIR] [--resume]
"""

from __future__ import annotations

import argparse
import builtins
import datetime
import os
import random
import runpy
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from bench.envs import textenv  # noqa: E402
from bench.envs.oregon_trail_1975 import parse  # noqa: E402

MINUTE = 30
SHOT_SECONDS = 1.0


class _Clock:
    def __init__(self) -> None:
        self.now = 0.0

    def __call__(self) -> float:
        self.now += SHOT_SECONDS
        return self.now


class _FixedDateTime(datetime.datetime):
    @classmethod
    def now(cls, tz=None):
        return cls(1847, 3, 29, 12, MINUTE, 0, tzinfo=tz)


def pin(seed: int) -> None:
    """Make the game's three sources of change fixed for this seed."""
    random.seed(seed)
    time.time = _Clock()
    datetime.datetime = _FixedDateTime


def run(game: Path, seed: int, session: textenv.Session) -> dict:
    """Run the game to its end in this process; return how it ended."""
    session.record(
        {"kind": "start", "seed": seed, "resumed": bool(session.replay), "pid": os.getpid()}
    )
    real_out, real_input = sys.stdout, builtins.input
    real_time, real_datetime = time.time, datetime.datetime
    pin(seed)
    sys.stdout = session
    builtins.input = session.ask
    ending = {"outcome": "ended"}
    try:
        runpy.run_path(str(game), run_name="__main__")
    except textenv.Stopped as stop:
        ending = {"outcome": "stopped", "condition": str(stop)}
    except SystemExit:
        ending = {"outcome": "ended"}
    except EOFError:
        ending = {"outcome": "no-input"}
    except (ValueError, IndexError) as exc:
        session.write(f"\nTHE GAME STOPPED: IT COULD NOT READ THAT ANSWER ({exc})\n")
        session.record({"kind": "crash", "error": f"{type(exc).__name__}: {exc}"})
        ending = {"outcome": "crashed"}
    finally:
        sys.stdout, builtins.input = real_out, real_input
        time.time, datetime.datetime = real_time, real_datetime
    session.record({"kind": "end", **ending})
    return ending


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the 1975 port deterministically.")
    parser.add_argument("--game", type=Path, required=True)
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--transcript", type=Path, default=None)
    parser.add_argument("--stop-when", action="append", default=[])
    parser.add_argument("--step-dir", type=Path, default=None)
    parser.add_argument(
        "--opening",
        action="append",
        default=[],
        help="a line the environment answers before the player does (repeatable)",
    )
    parser.add_argument(
        "--resume", action="store_true", help="replay the transcript's inputs, then play on"
    )
    args = parser.parse_args(argv)
    replay: list[str] = []
    if args.resume and args.transcript is not None:
        replay = [e["line"] for e in textenv.read(args.transcript) if e["kind"] == "in"]
    session = textenv.Session(
        args.transcript,
        parse.state_of,
        [textenv.Condition(c) for c in args.stop_when],
        args.step_dir,
        replay,
        opening=[] if replay else args.opening,
    )
    run(args.game, args.seed, session)
    return 0


if __name__ == "__main__":
    sys.exit(main())
