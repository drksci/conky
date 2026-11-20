"""A connector that gives a vault eyes and hands on a terminal program.

The connector holds no state. It writes what the program shows to a screen page, and types what a
hands page says into the program. Both are ordinary signed writes, so every rule applies. POSIX
only: the program runs in a pseudo-terminal.
"""

from __future__ import annotations

import codecs
import os
import re
import select
import struct
import subprocess
import time
from collections.abc import Callable
from dataclasses import dataclass

from conky import arch, git, present
from conky.errors import BadInput
from conky.vault import Vault

TERM = "TERM"
SETTLE = 0.3
MAX_STEPS = 200
LINES = 60
POLL = 0.05
KEPT = 100_000
_ESCAPES = re.compile(
    r"\x1b(?:\[[0-?]*[ -/]*[@-~]|\][^\x07\x1b]*(?:\x07|\x1b\\)?|[()][0-9A-Za-z]|[@-Z\\-_=>])"
)
_SCREEN_BODY = "What the program shows, as plain text. A connector writes it; see `conky connect`."
_HANDS_BODY = (
    "What to type into the program. Set `keys` and the `turn` of the screen being answered. "
    "Set `enter` to false to send no newline."
)


@dataclass(frozen=True)
class Settings:
    """The pages, the actor and the pace of one run."""

    actor: str
    screen: str
    hands: str
    settle: float
    max_steps: int


@arch.step(
    "flow.connect.sense",
    3,
    "lane.connector",
    None,
    "wait for quiet, strip control sequences, keep the last 60 lines",
)
def plain(text: str) -> str:
    """Return text as a terminal would show it, with control sequences removed."""
    lines, col = [""], 0
    for char in _ESCAPES.sub("", text):
        if char == "\n":
            lines.append("")
            col = 0
        elif char == "\r":
            col = 0
        elif char == "\b":
            col = max(0, col - 1)
        elif char >= " " and char != "\x7f":
            line = lines[-1]
            lines[-1] = line[:col] + char + line[col + 1 :]
            col += 1
    shown = "\n".join(line.rstrip() for line in lines).rstrip()
    return "\n".join(shown.split("\n")[-LINES:])


@arch.step(
    "flow.connect.sense",
    2,
    "lane.outside",
    "lane.connector",
    "the program prints, in a pseudo-terminal",
)
def _start(program: list[str]) -> tuple[int, subprocess.Popen[bytes]]:
    try:
        import fcntl
        import pty
        import termios
    except ImportError as exc:
        raise BadInput(
            "conky connect terminal needs a POSIX system: run it on Linux or macOS"
        ) from exc
    master, slave = pty.openpty()
    fcntl.ioctl(slave, termios.TIOCSWINSZ, struct.pack("HHHH", 24, 80, 0, 0))
    env = {**os.environ, TERM: os.environ.get(TERM, "xterm")}
    try:
        proc = subprocess.Popen(
            program, stdin=slave, stdout=slave, stderr=slave, env=env, start_new_session=True
        )
    except OSError as exc:
        os.close(master)
        raise BadInput(
            f"cannot start {program[0]!r}: {exc.strerror}: check the command and that it is on PATH"
        ) from exc
    finally:
        os.close(slave)
    return master, proc


def _read(master: int) -> bytes:
    try:
        return os.read(master, 4096)
    except OSError:
        return b""


@arch.step(
    "flow.connect.act",
    2,
    "lane.connector",
    "lane.history",
    "poll for a new commit that touches the hands page",
)
def _last(vault: Vault, page: str) -> str:
    """Return the id of the latest commit that changed the page, or nothing."""
    return git.run(
        ["log", "-1", "--format=%H", "main", "--", f"pages/{page}.md"], vault.path
    ).strip()


@arch.archetype(
    "kind.hands",
    "a person or a character writes it, the connector creates it",
    "`keys`, `turn` and `enter`: what to type.",
    doc="connectors.md#the-hands-page",
)
@arch.stage(
    "act",
    "stage.act.hands",
    "The connector types what a hands page says.",
    doc="connectors.md#the-hands-page",
)
@arch.step(
    "flow.connect.act",
    1,
    "lane.page",
    "lane.runtime",
    "write hands: keys and the turn it answers, and a rule may refuse it",
)
@arch.step("flow.connect.act", 3, "lane.connector", "lane.runtime", "read the hands page")
@arch.step(
    "flow.connect.act",
    4,
    "lane.connector",
    None,
    "keys must be text, the turn must equal the screen and not be answered",
)
def _typed(vault: Vault, hands: str, turn: int, answered: int) -> str | None:
    """Return what the hands page asks to type for the current screen, if it asks."""
    try:
        fields = vault.read(hands).fields
    except BadInput:
        return None
    keys = fields.get("keys")
    if not isinstance(keys, str) or not keys or fields.get("turn") != turn or turn == answered:
        return None
    return keys if fields.get("enter") is False else keys + "\n"


@arch.archetype(
    "kind.screen",
    "a connector",
    "What a program shows, with `turn` and `ended`.",
    doc="connectors.md#the-screen-page",
)
@arch.step(
    "flow.connect.sense",
    1,
    "lane.connector",
    "lane.runtime",
    "create the screen and hands pages if missing",
)
def _prepare(vault: Vault, settings: Settings, now: Callable[[], str]) -> None:
    start = ((settings.screen, _SCREEN_BODY, {"turn": 0}), (settings.hands, _HANDS_BODY, {}))
    for page, body, fields in start:
        if (vault.pages_dir / f"{page}.md").exists():
            continue
        done = vault.write(page, fields, body, actor=settings.actor, at=now())
        if not done.ok:
            raise BadInput(
                f"cannot create the page {page!r}: {done.reason}: "
                "create it first, or change the rule"
            )


def _stop(proc: subprocess.Popen[bytes]) -> int:
    if proc.poll() is None:
        proc.terminate()
    try:
        return proc.wait(timeout=2)
    except subprocess.TimeoutExpired:
        proc.kill()
        return proc.wait()


@arch.part(
    "part.connect.terminal",
    "layer.edge",
    "The terminal connector, eyes and hands on a program.",
    doc="connectors.md#the-terminal-connector",
)
@arch.stage(
    "stimulus",
    "stage.stimulus.connector",
    "The terminal connector writes the screen page.",
    doc="connectors.md#the-screen-page",
)
@arch.change(
    "place.beside.connector",
    "Connectors: processes that hold no state and write as their own actor.",
    doc="connectors.md",
)
@arch.step(
    "flow.connect.sense",
    4,
    "lane.connector",
    None,
    "the text equals the last screen: nothing is written",
)
@arch.step(
    "flow.connect.sense",
    5,
    "lane.connector",
    "lane.runtime",
    "write screen: turn plus one, the body is the text",
)
@arch.step(
    "flow.connect.sense",
    6,
    "lane.runtime",
    "lane.page",
    "a signed write by the connector, and the pages that watch screen react",
)
@arch.step(
    "flow.connect.sense",
    7,
    "lane.runtime",
    "lane.connector",
    "refused: recorded, the connector prints it and goes on",
    refusal=True,
)
@arch.step(
    "flow.connect.sense",
    8,
    "lane.connector",
    None,
    "the run ends on exit, max steps or interrupt, and ended is written",
)
@arch.step(
    "flow.connect.act",
    5,
    "lane.connector",
    "lane.outside",
    "type the keys, with a newline unless enter is false",
)
@arch.step(
    "flow.connect.act",
    6,
    "lane.connector",
    None,
    "an old turn, or one already answered, is ignored",
)
@arch.slot(
    "slot.connector",
    "connector kind",
    "Eyes and hands on a terminal program.",
    doc="connectors.md#the-terminal-connector",
)
def terminal(
    vault: Vault,
    program: list[str],
    settings: Settings,
    now: Callable[[], str],
    ui: present.Plain,
    say: Callable[[str], None],
) -> int:
    """Run the program, write its screens to the vault and type what the hands page says."""
    if settings.screen == settings.hands:
        raise BadInput("--screen and --hands name the same page: give each its own page")
    if settings.settle < 0 or settings.max_steps < 1:
        raise BadInput("--settle must be 0 or more seconds and --max-steps at least 1")
    _prepare(vault, settings, now)
    master, proc = _start(program)
    decoder = codecs.getincrementaldecoder("utf-8")("replace")
    raw, shown, seen = "", "", _last(vault, settings.hands)
    turn = answered = 0
    pending, quiet, reason = False, time.monotonic(), ""
    try:
        while not reason:
            eof = False
            if select.select([master], [], [], POLL)[0]:
                data = _read(master)
                if data:
                    raw = (raw + decoder.decode(data))[-KEPT:]
                    pending, quiet = True, time.monotonic()
                else:
                    eof = True
            if pending and (eof or time.monotonic() - quiet >= settings.settle):
                pending, text = False, plain(raw)
                if text != shown:
                    changes: dict[str, object] = {"turn": turn + 1}
                    if turn == 0:
                        changes["ended"] = ""
                    done = vault.write(
                        settings.screen, changes, text, actor=settings.actor, at=now()
                    )
                    if done.ok:
                        shown, turn = text, turn + 1
                        say(ui.screen(turn, done.id[:7]))
                    else:
                        say(ui.refused(done.id[:7], done.reason or ""))
            if eof:
                code = _stop(proc)
                reason = f"the program exited with status {code}"
            elif turn >= settings.max_steps:
                reason = f"stopped after {turn} screens"
            elif (latest := _last(vault, settings.hands)) != seen:
                seen = latest
                keys = _typed(vault, settings.hands, turn, answered)
                if keys is not None:
                    os.write(master, keys.encode())
                    answered, quiet = turn, time.monotonic()
                    say(ui.keys(turn, keys.rstrip("\n")))
    except KeyboardInterrupt:
        reason = "interrupted"
    finally:
        _stop(proc)
        os.close(master)
    done = vault.write(settings.screen, {"ended": reason}, None, actor=settings.actor, at=now())
    say(ui.ended(reason) if done.ok else ui.refused(done.id[:7], done.reason or ""))
    return 0
