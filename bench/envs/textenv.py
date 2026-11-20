"""The runner's hold on a line-based game: its transcript, stops, steps and resume by replay.

A launcher runs the game in this process with `input` and standard output routed through a
`Session`. Nothing the game does changes; the session only records it.

- Transcript: every piece of output and every line read, as JSON lines, with the prompt each
  line answered. It is the ground truth a run is scored from.
- Stop: before each read, the stop conditions are tested against the state parsed from the
  transcript so far. When one holds, the session records `stopped` and the game ends there.
- Step: before each read, the session writes `paused-N` in the step folder and waits for `go-N`.
- Opening: lines the environment answers itself before any player does, shown on the screen
  as typed and recorded with `"by": "opening"`.
- Resume: the inputs of an earlier transcript are fed back silently. A deterministic game then
  stands exactly where it stopped, and the player sees a short banner and the tail of what the
  game had shown, then plays on. The transcript is appended to, not rewritten.
"""

from __future__ import annotations

import io
import json
import re
import sys
import time
from collections.abc import Callable
from pathlib import Path

# The real clock, kept before a launcher pins `time.time` for the game.
_clock = time.time
TAIL_LINES = 24
MAX_INPUTS = 400
CONDITION = re.compile(r"^\s*([a-z_]+)\s*(>=|<=|==|!=|>|<)\s*(\S+)\s*$")


class Stopped(Exception):
    """A stop condition held; the game ends here."""


class Condition:
    """A test such as `turn>=8`, `food<50` or `prompt==eat` on a parsed state."""

    def __init__(self, text: str) -> None:
        found = CONDITION.match(text)
        if not found:
            raise ValueError(
                f"cannot read the condition {text!r}: write NAME OP VALUE, for example turn>=8, "
                "with OP one of >= <= == != > <"
            )
        self.text, self.name, self.op, raw = text.strip(), *found.groups()
        try:
            self.value: float | str = float(raw)
        except ValueError:
            self.value = raw

    def holds(self, state: dict) -> bool:
        if self.name not in state:
            return False
        left = state[self.name]
        right = self.value
        if isinstance(right, float):
            try:
                left = float(left)
            except (TypeError, ValueError):
                return False
        else:
            left = str(left)
        return {
            ">=": lambda: left >= right,
            "<=": lambda: left <= right,
            ">": lambda: left > right,
            "<": lambda: left < right,
            "==": lambda: left == right,
            "!=": lambda: left != right,
        }[self.op]()


def read(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def text(events: list[dict]) -> str:
    """Return the transcript as a terminal would have shown it, inputs echoed."""
    parts = []
    for event in events:
        if event["kind"] == "out":
            parts.append(event["text"])
        elif event["kind"] == "in":
            parts.append(event["line"] + "\n")
    return "".join(parts)


class Session:
    def __init__(
        self,
        transcript: Path | None,
        state_of: Callable[[list[dict]], dict],
        stop_when: list[Condition] | None = None,
        step_dir: Path | None = None,
        replay: list[str] | None = None,
        stdin=None,
        stdout=None,
        max_inputs: int = MAX_INPUTS,
        opening: list[str] | None = None,
    ) -> None:
        self.max_inputs = max_inputs
        self.opening = list(opening or [])
        self.path = transcript
        self.state_of = state_of
        self.stop_when = stop_when or []
        self.step_dir = step_dir
        self.replay = list(replay or [])
        self.stdin = stdin or sys.stdin
        self.stdout = stdout or sys.stdout
        self.events: list[dict] = read(transcript) if transcript else []
        self.inputs = sum(1 for e in self.events if e["kind"] == "in")
        self.prompt = ""
        self.hidden = io.StringIO() if self.replay else None

    def record(self, event: dict) -> None:
        event = {"t": round(_clock(), 3), **event}
        self.events.append(event)
        if self.path is not None:
            with self.path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(event, ensure_ascii=False) + "\n")

    def write(self, data: str) -> int:
        if not data:
            return 0
        if self.hidden is not None:
            self.hidden.write(data)
            return len(data)
        self.stdout.write(data)
        self.stdout.flush()
        self.record({"kind": "out", "text": data})
        self.prompt = (self.prompt + data)[-400:]
        return len(data)

    def flush(self) -> None:
        self.stdout.flush()

    def _resume_banner(self) -> None:
        shown = self.hidden.getvalue() if self.hidden is not None else ""
        self.hidden = None
        tail = "\n".join(shown.split("\n")[-TAIL_LINES:])
        self.record({"kind": "resumed", "inputs": self.inputs})
        self.write("\n(The game resumes where it stopped. Its last lines were:)\n" + tail)

    def ask(self, prompt: str = "") -> str:
        """Stand in for `input`: show the prompt, test stops, wait for a step, read one line."""
        self.write(prompt)
        if self.replay:
            line = self.replay.pop(0)
            if self.hidden is not None:
                self.hidden.write(line + "\n")
            return line
        if self.hidden is not None:
            self._resume_banner()
        if self.opening:
            line = self.opening.pop(0)
            self.write(line + "\n")
            self.inputs += 1
            event = {"kind": "in", "n": self.inputs, "line": line, "prompt": self.prompt[-200:]}
            self.record({**event, "by": "opening"})
            self.prompt = ""
            return line
        state = self.state_of(self.events)
        if self.inputs >= self.max_inputs:
            self.record({"kind": "stopped", "condition": f"inputs>={self.max_inputs}"})
            raise Stopped(f"inputs>={self.max_inputs}")
        for condition in self.stop_when:
            if condition.holds(state):
                self.record({"kind": "stopped", "condition": condition.text, "state": state})
                raise Stopped(condition.text)
        if self.step_dir is not None:
            n = self.inputs + 1
            (self.step_dir / f"paused-{n}").write_text(json.dumps(state))
            while not (self.step_dir / f"go-{n}").exists():
                time.sleep(0.1)
        line = self.stdin.readline()
        if not line:
            self.record({"kind": "eof"})
            raise EOFError
        line = line.rstrip("\r\n")
        self.inputs += 1
        self.record({"kind": "in", "n": self.inputs, "line": line, "prompt": self.prompt[-200:]})
        self.prompt = ""
        return line
