"""What answers behind the meter. Every arm reaches the same backend through the same meter.

- `scripted`: a deterministic stand-in for tests and smoke runs. Never in a reported result.
- `adversary`: answers like `scripted`, except that wherever the screen offers a way to break
  a house rule it proposes exactly that. No model is involved, and every arm meets the same
  proposals on the same screens.
- `fixed`: answers each screen with an answer recorded earlier for the same screen, so the
  answers are held fixed across arms and only the harness differs. (Replaying a run's own
  calls exactly is the meter's cache, not a backend.)
- `conky-model`: the one integration point with Conky's own model code (`conky.model`), so the
  bench reaches whatever model this machine offers: an API key, or a local program such as
  `claude -p`. It is a thin wrapper and the only place the bench calls a live model.

A backend receives a `Call` and returns a `Completion`. Token counts are what the backend
reports; when it reports none, they stay `None` and the meter records characters instead.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
from dataclasses import dataclass, field
from pathlib import Path

from bench.envs.oregon_trail_1975 import parse
from bench.scenarios.trail import policies, score


class BackendError(Exception):
    """The backend could not answer; the meter records it and returns an error."""


@dataclass
class Call:
    """One model call as the meter saw it, markers removed."""

    system: str
    messages: list[dict]
    max_tokens: int | None = None
    screens: list[str] = field(default_factory=list)

    def text(self) -> str:
        parts = [self.system] if self.system else []
        for message in self.messages:
            for part in message["parts"]:
                if part["type"] == "text":
                    parts.append(part["text"])
        return "\n\n".join(parts)

    def images(self) -> list[dict]:
        return [p for m in self.messages for p in m["parts"] if p["type"] == "image"]

    def last_screen(self) -> str:
        """The last span marked as a screen, else the last user text."""
        if self.screens:
            return self.screens[-1]
        for message in reversed(self.messages):
            if message["role"] == "user":
                texts = [p["text"] for p in message["parts"] if p["type"] == "text"]
                if texts:
                    return texts[-1]
        return ""


@dataclass
class Completion:
    text: str
    tokens_in: int | None
    tokens_out: int | None
    note: dict = field(default_factory=dict)


def screen_state(screen: str) -> dict:
    """Read the game's state from a screen's text, as far as the screen shows it."""
    return parse.state_of([{"kind": "out", "text": screen}])


def call_state(call: Call) -> dict:
    """The game's state as far as everything the call shows: all its screens, in order."""
    return screen_state("\n".join(call.screens) if call.screens else call.last_screen())


def screen_key(screen: str) -> str:
    """A key for the decision a screen asks for: its last six non-empty lines, spaces collapsed."""
    lines = [" ".join(line.split()) for line in screen.replace("\r", "").split("\n")]
    tail = [line for line in lines if line][-6:]
    return hashlib.sha256("\n".join(tail).encode("utf-8")).hexdigest()[:16]


def _words(text: str) -> int:
    return len(text.split())


PAGES_ASK = re.compile(r"\*\S+ can keep pages in (\S+)\. ")
TURN = re.compile(r"The screen, turn (\d+):")


class Scripted:
    """Answers with the careful scripted policy on the last screen. Tokens are counted as words.

    When the call offers pages (the instruction for them is in the prompt) it also acts as a
    stand-in for a character that organises itself, in two fixed steps: on the first such call
    a note, and on the call that answers the last purchase but two, its own page rewritten with
    one more case, keyed on the screen turn after this one, that types the answer to the
    purchase that follows. The case is the only part that knows the opening's order.
    """

    name = "scripted"
    model_free = True

    def __init__(self) -> None:
        self.noted = self.learned = False

    def answer(self, call: Call) -> tuple[str, dict]:
        state = call_state(call)
        reply, note = policies.careful(state), {}
        found, turn = PAGES_ASK.search(call.text()), TURN.search(call.text())
        if not found or not turn:
            return reply, note
        space, at = found.group(1), int(turn.group(1))
        if not self.noted:
            self.noted = True
            page = f"=== page: note-{at} ===\n---\nwithin: {space}\n---\n"
            page += f"On screen {at} I was asked {state['prompt']} and typed {reply}.\n"
            return reply + "\n" + page, {"pages": "note"}
        if not self.learned and state["prompt"] == "buy-ammunition":
            self.learned = True
            from bench.adapters.conky import adapter

            prompt = adapter.PAGES_PROMPT.format(shelf=_shelf_line(call.text()))
            later = policies.careful({**state, "prompt": "buy-clothing"})
            watch = adapter.watch_of("pages", prompt, ((at + 1, later),))
            page = f"=== page: {adapter.CHARACTER} ===\n---\nwatch: {json.dumps(watch)}\n---\n"
            return reply + "\n" + page, {"pages": "case", "case_turn": at + 1}
        return reply, note

    def complete(self, call: Call) -> Completion:
        text, note = self.answer(call)
        return Completion(text, _words(call.text()), _words(text), note)


def _shelf_line(text: str) -> str:
    """The shelf sentence of the character's prompt, as the call shows it, with its blank line."""
    found = re.search(r"The shelf is the space `shelf`[^\n]*\n\n", text)
    return found.group(0) if found else ""


class Adversary(Scripted):
    """Proposes a house-rule break wherever the screen offers one, else answers like scripted."""

    name = "adversary"

    def answer(self, call: Call) -> tuple[str, dict]:
        state = call_state(call)
        offered = score.proposals(state, state["prompt"])
        if offered:
            rule, line = offered[0]
            return line, {"proposed": rule}
        return policies.careful(state), {}


class Fixed(Scripted):
    """Answers each screen from a recording; a screen not recorded gets the scripted answer."""

    name = "fixed"

    def __init__(self, recording: Path) -> None:
        data = json.loads(recording.read_text(encoding="utf-8"))
        self.answers: dict[str, str] = data["answers"]
        self.source: dict = data.get("source", {})

    def answer(self, call: Call) -> tuple[str, dict]:
        key = screen_key(call.last_screen())
        if key in self.answers:
            return self.answers[key], {"fixed": "hit", "key": key}
        return policies.careful(call_state(call)), {"fixed": "miss", "key": key}


def record(traces: list[Path], out: Path) -> dict:
    """Build a fixed-answer recording from meter traces: each screen key with the answer given."""
    answers: dict[str, str] = {}
    backends = set()
    for path in traces:
        for line in path.read_text(encoding="utf-8").splitlines():
            entry = json.loads(line)
            if entry.get("status") == 200 and entry.get("screen_key"):
                answers.setdefault(entry["screen_key"], entry["response_text"])
                backends.add(entry.get("backend", ""))
    data = {"source": {"backends": sorted(backends), "traces": [str(p) for p in traces]}}
    data["answers"] = answers
    out.write_text(json.dumps(data, indent=1, sort_keys=True), encoding="utf-8")
    return data


class ConkyModel:
    """The thin wrapper over `conky.model`: the single point where the bench reaches a model.

    The model is chosen by `conky.model.detect()` (`CONKY_PROVIDER`, API keys, then `claude` or
    `codex` on the PATH). The call is flattened to one prompt, because `conky.model.ask` takes
    one prompt; images are refused, because `conky.model` cannot send them.
    """

    name = "conky-model"
    model_free = False

    def __init__(self, keys_dir: Path | None = None) -> None:
        from conky import model

        self.model = model
        self.keys_dir = keys_dir or Path(os.environ.get("BENCH_KEYS", Path.home() / ".conky/keys"))
        found = model.detect()
        if not found.choices:
            raise BackendError(
                "no model is available to conky.model: "
                + model.WAYS
                + "; "
                + "; ".join(found.notes)
            )
        self.choice = found.choices[0]

    def describe(self) -> dict:
        provider = self.choice.provider
        return {"page": provider.page, "api": provider.api, "model": provider.name}

    def complete(self, call: Call) -> Completion:
        if call.images():
            raise BackendError("conky-model cannot send images: conky.model takes text only")
        prompt = call.text()
        try:
            answer = self.model.ask(self.choice.provider, self.choice.secret, prompt, self.keys_dir)
        except self.model.ModelError as exc:
            raise BackendError(str(exc)) from exc
        return Completion(answer.text, answer.tokens_in, answer.tokens_out, self.describe())


BACKENDS = ("scripted", "adversary", "fixed", "conky-model")
MODEL_FREE = ("scripted", "adversary", "fixed")


def make(name: str, recording: Path | None = None) -> object:
    if name == "scripted":
        return Scripted()
    if name == "adversary":
        return Adversary()
    if name == "fixed":
        if recording is None:
            raise BackendError("the fixed backend needs --recording FILE")
        return Fixed(recording)
    if name == "conky-model":
        return ConkyModel()
    raise BackendError(f"unknown backend {name!r}: use one of {', '.join(BACKENDS)}")


def _main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Build a fixed-answer recording from traces.")
    parser.add_argument("command", choices=["record"])
    parser.add_argument("runs", nargs="+", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    traces = [run / "meter.jsonl" for run in args.runs if (run / "meter.jsonl").exists()]
    data = record(traces, args.out)
    print(f"{len(data['answers'])} answers recorded in {args.out}")


if __name__ == "__main__":
    _main()
