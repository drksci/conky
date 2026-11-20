"""How results are shown: one plain form for scripts, one styled form for people.

Each command builds its result once and hands it to a presenter. `choose` is the only place that
decides which presenter is used, so the commands never branch on styling.
"""

from __future__ import annotations

import os
import re
import shutil
import textwrap
from collections.abc import Mapping
from dataclasses import dataclass
from typing import TextIO

from conky import style

PLAIN_WIDTH = 78
MAX_WIDTH = 88
MIN_WIDTH = 30
LABEL_WIDTH = 18


@dataclass(frozen=True)
class Outcome:
    """What one demo write did: whether it was written, and the reactions that followed."""

    ok: bool
    page: str
    reason: str
    reactions: tuple[tuple[str, str], ...]


def _fill(text: str, width: int, *, initial_indent: str, subsequent_indent: str) -> str:
    """Wrap text on spaces only, so a path or a hyphenated name is never split."""
    return textwrap.fill(
        text,
        width,
        initial_indent=initial_indent,
        subsequent_indent=subsequent_indent,
        break_long_words=False,
        break_on_hyphens=False,
    )


def _next_commands(shown: object, look_at: str) -> list[tuple[str, str]]:
    return [
        ("The history:", f"git -C {shown} log --oneline"),
        ("A page:", f"conky --vault {shown} read {look_at}"),
        ("The checks:", f"conky --vault {shown} verify"),
    ]


class Plain:
    """Unstyled text: the stable form that scripts and tests read."""

    def listing(self, entries: list[tuple[str, str]]) -> list[str]:
        """Return the examples with their summaries."""
        lines = []
        for name, summary in entries:
            lines.append(name)
            lines.append(
                textwrap.fill(summary, PLAIN_WIDTH, initial_indent="  ", subsequent_indent="  ")
            )
        return lines

    def demo_title(self, title: str, summary: str) -> list[str]:
        """Return the opening of a demo."""
        return [title, textwrap.fill(summary, PLAIN_WIDTH)]

    def step(self, number: int, say: str) -> list[str]:
        """Return the head of a step: a blank line and the numbered narration."""
        initial = f"{number}. "
        fill = _fill(say, PLAIN_WIDTH, initial_indent=initial, subsequent_indent="   ")
        return ["", fill]

    def result(self, number: int, outcome: Outcome) -> list[str]:
        """Return what a write did, and the reactions that followed it."""
        if outcome.ok:
            text = f"written: {outcome.page}"
        else:
            text = f"refused: {outcome.page}, because {outcome.reason}"
        for page, verb in outcome.reactions:
            text += f". Then {page} {verb}"
        return [_fill(text, PLAIN_WIDTH, initial_indent="     -> ", subsequent_indent="        ")]

    def note(self, number: int, state: str, label: str, text: str) -> list[str]:
        """Return one finding under a step: ok or fail with a label, or info with none."""
        deeper = " " * 8
        if state == "info":
            return [_fill(text, PLAIN_WIDTH, initial_indent=deeper, subsequent_indent=deeper)]
        return [
            _fill(
                f"{label}: {text}",
                PLAIN_WIDTH,
                initial_indent="     -> ",
                subsequent_indent=deeper,
            )
        ]

    def closing(self, title: str, paragraphs: list[str]) -> list[str]:
        """Return a closing block: a title and short paragraphs."""
        fill = [
            _fill(p, PLAIN_WIDTH, initial_indent="  ", subsequent_indent="  ") for p in paragraphs
        ]
        return ["", title, *fill]

    def demo_step(self, number: int, say: str, outcome: Outcome) -> list[str]:
        """Return one step: a blank line, the narration and what happened."""
        return [*self.step(number, say), *self.result(number, outcome)]

    def demo_next(self, shown: object, look_at: str) -> list[str]:
        """Return the closing block that says what to look at next."""
        lines = ["", "What to look at next", f"  The vault is in {shown}"]
        for label, command in _next_commands(shown, look_at):
            lines.append(f"  {label:<{LABEL_WIDTH}}{command}")
        return lines

    def initialised(self, path: str) -> str:
        """Return the result of init."""
        return f"initialised {path}"

    def written(self, commit: str) -> str:
        """Return the result of a write that was kept."""
        return f"written (commit {commit})"

    def refused(self, commit: str, reason: str) -> str:
        """Return the result of a write that was refused."""
        return f"refused (commit {commit}): {reason}"

    def verified(self, count: int) -> str:
        """Return the result of verify."""
        return f"ok: {count} commits verified"

    def restored(self) -> str:
        """Return the result of rebuild."""
        return "restored the working tree from the committed history"

    def error(self, message: str) -> str:
        """Return an error line."""
        return f"error: {message}"

    def screen(self, turn: int, commit: str) -> str:
        """Return the line for a screen written to the vault."""
        return f"screen {turn} written (commit {commit})"

    def keys(self, turn: int, text: str) -> str:
        """Return the line for keys sent to the program."""
        return f"keys sent for screen {turn}: {text}"

    def ended(self, reason: str) -> str:
        """Return the line for the end of a run."""
        return f"ended: {reason}"

    def log(self, lines: list[str]) -> list[str]:
        """Return the history lines."""
        return lines

    def read(self, text: str) -> str:
        """Return a page as stored."""
        return text


_FIELD = re.compile(r"^(\s*(?:- )*)([^\s:#-][^:]*:)(\s.*|)$")
_MODEL_TAIL = re.compile(r"^(.*?)(?:^| )model (\S+)(?: read (.+))?$")
_FROM_TAIL = re.compile(r"^(.*?)(?:^| )from (\S+)$")


class Styled(Plain):
    """Rounded boxes and small badges in soft pinks and purples, for people at a terminal."""

    def __init__(self, columns: int) -> None:
        self.width = max(MIN_WIDTH, min(MAX_WIDTH, columns))

    def listing(self, entries: list[tuple[str, str]]) -> list[str]:
        lines = []
        for name, summary in entries:
            lines.append(style.title(name))
            lines += [style.dim(x) for x in style.wrap(summary, self.width, "  ", "  ")]
        return lines

    def demo_title(self, title: str, summary: str) -> list[str]:
        inner = [style.title(title)]
        inner += [style.dim(x) for x in style.wrap(summary, self.width - 4)]
        return style.box(inner)

    def _indent(self, number: int) -> str:
        return " " * (style.visible_len(style.badge(str(number), style.PURPLE)) + 1)

    def step(self, number: int, say: str) -> list[str]:
        pill = style.badge(str(number), style.PURPLE, style.BRIGHT)
        return ["", *style.wrap(say, self.width, pill + " ", self._indent(number))]

    def result(self, number: int, outcome: Outcome) -> list[str]:
        indent = self._indent(number)
        page = style.bright(outcome.page)
        lines = []
        if outcome.ok:
            lines.append(f"{indent}{style.badge('✓ written', style.MINT)}  {page}")
        else:
            lines.append(f"{indent}{style.badge('✗ refused', style.RED)}  {page}")
            deeper = indent + "  "
            reason = style.wrap(f"because {outcome.reason}", self.width, deeper, deeper)
            lines += [style.dim(x) for x in reason]
        for other, verb in outcome.reactions:
            name = style.colour(other, style.AMBER)
            lines.append(f"{indent} {style.dim('↳')} {name} {style.dim(verb)}")
        return lines

    def note(self, number: int, state: str, label: str, text: str) -> list[str]:
        indent = self._indent(number)
        if state == "info":
            deeper = indent + "    "
            return [style.bright(x) for x in style.wrap(text, self.width, deeper, deeper)]
        if state == "ok":
            mark = style.badge(f"✓ {label}", style.MINT)
        else:
            mark = style.badge(f"✗ {label}", style.RED)
        room = max(self.width - style.visible_len(indent + mark) - 2, MIN_WIDTH // 2)
        lines = style.wrap(text, room)
        hang = " " * (style.visible_len(indent + mark) + 2)
        return [f"{indent}{mark}  {style.bright(lines[0])}"] + [
            hang + style.bright(x) for x in lines[1:]
        ]

    def closing(self, title: str, paragraphs: list[str]) -> list[str]:
        inner = [style.title(title)]
        for paragraph in paragraphs:
            inner += [style.dim(x) for x in style.wrap(paragraph, self.width - 4)]
        return ["", *style.box(inner)]

    def demo_step(self, number: int, say: str, outcome: Outcome) -> list[str]:
        return [*self.step(number, say), *self.result(number, outcome)]

    def demo_next(self, shown: object, look_at: str) -> list[str]:
        inner = [style.title("What to look at next")]
        inner.append(f"{style.dim('The vault is in')} {style.bright(str(shown))}")
        for label, command in _next_commands(shown, look_at):
            inner.append(style.dim(f"{label:<{LABEL_WIDTH}}") + style.bright(command))
        return ["", *style.box(inner)]

    def initialised(self, path: str) -> str:
        return f"{style.badge('✓ initialised', style.MINT)} {style.bright(path)}"

    def written(self, commit: str) -> str:
        return f"{style.badge('✓ written', style.MINT)} {style.dim(f'(commit {commit})')}"

    def refused(self, commit: str, reason: str) -> str:
        head = style.badge("✗ refused", style.RED)
        return f"{head} {style.dim(f'(commit {commit}): {reason}')}"

    def verified(self, count: int) -> str:
        return f"{style.badge('✓ verified', style.MINT)} {style.bright(f'{count} commits')}"

    def restored(self) -> str:
        badge = style.badge("✓ restored", style.MINT)
        return f"{badge} {style.bright('the working tree from the committed history')}"

    def error(self, message: str) -> str:
        head, sep, todo = message.partition(": ")
        badge = style.badge("✗ error", style.RED)
        if not sep:
            return f"{badge} {style.colour(message, style.RED)}"
        return f"{badge} {style.colour(head + sep, style.RED)}{style.bright(todo)}"

    def screen(self, turn: int, commit: str) -> str:
        badge = style.badge(f"screen {turn}", style.MINT)
        return f"{badge} {style.dim(f'(commit {commit})')}"

    def keys(self, turn: int, text: str) -> str:
        badge = style.badge(f"keys for {turn}", style.PURPLE, style.BRIGHT)
        return f"{badge} {style.bright(text)}"

    def ended(self, reason: str) -> str:
        return f"{style.badge('ended', style.AMBER)} {style.bright(reason)}"

    def log(self, lines: list[str]) -> list[str]:
        rows = [line.split(None, 5) for line in lines]
        rows = [[*row, ""] if len(row) == 5 else row for row in rows]
        actor_width = max((len(r[2]) for r in rows), default=0)
        page_width = max((len(r[4]) for r in rows), default=0)
        out = []
        for short, at, actor, kind, page, detail in rows:
            if kind == "write":
                mark = style.badge("written", style.MINT)
            elif kind == "refused":
                mark = style.badge("refused", style.RED)
            else:
                mark = style.pad(style.dim(f" {kind}"), 9)
            line = (
                f"{style.dim(short)} {style.dim(at)} {style.bright(actor.ljust(actor_width))} "
                f"{mark} {style.bright(page.ljust(page_width))}"
            )
            found = _MODEL_TAIL.match(detail)
            space = _FROM_TAIL.match(detail)
            if found:
                text, provider, read = found.groups()
                tail = f"{style.dim(text)} " if text else ""
                pill = style.badge("model", style.PURPLE, style.BRIGHT)
                line += f" {tail}{pill} {style.bright(provider)}"
                if read:
                    line += f" {style.dim('read')} {style.bright(read)}"
            elif space:
                text, name = space.groups()
                tail = f"{style.dim(text)} " if text else ""
                line += f" {tail}{style.dim('from')} {style.bright(name)}"
            elif detail:
                line += f" {style.dim(detail)}"
            out.append(line)
        return out

    def read(self, text: str) -> str:
        out, inside = [], False
        for number, line in enumerate(text.splitlines(keepends=True)):
            body = line.rstrip("\n")
            newline = line[len(body) :]
            if body == "---" and (number == 0 or inside):
                inside = number == 0
                out.append(style.dim(body) + newline)
            elif inside:
                found = _FIELD.match(body)
                if found:
                    lead, name, value = found.groups()
                    out.append(lead + style.dim(name) + style.bright(value) + newline)
                else:
                    out.append(style.bright(body) + newline)
            else:
                out.append(line)
        return "".join(out)


def choose(mode: str, stream: TextIO, environ: Mapping[str, str] | None = None) -> Plain:
    """Return the presenter for stream: styled when asked, or when auto on a terminal.

    Auto styles only a terminal and only when NO_COLOR is not set. `always` styles regardless and
    `never` never does.
    """
    env = os.environ if environ is None else environ
    if mode == "always" or (mode == "auto" and "NO_COLOR" not in env and stream.isatty()):
        return Styled(shutil.get_terminal_size((MAX_WIDTH, 24)).columns)
    return Plain()
