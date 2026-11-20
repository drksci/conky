"""ANSI styling with the standard library only: colour, boxes, badges and width-aware wrapping."""

from __future__ import annotations

import re

PINK = "#FF5FAF"
PURPLE = "#874BFD"
MINT = "#04B575"
RED = "#FF5F87"
AMBER = "#FFB454"
GREY = "#6C6C6C"
BRIGHT = "#EEEEEE"
INK = "#000000"

RESET = "\x1b[0m"
_ESCAPE = re.compile(r"\x1b\[[0-9;]*m")


def _rgb(colour: str) -> str:
    return f"{int(colour[1:3], 16)};{int(colour[3:5], 16)};{int(colour[5:7], 16)}"


def _wrap_codes(text: str, codes: str) -> str:
    return f"\x1b[{codes}m{text}{RESET}"


def colour(text: str, hex_colour: str, *, bold: bool = False) -> str:
    """Return text in a 24-bit foreground colour, optionally bold."""
    codes = f"38;2;{_rgb(hex_colour)}"
    return _wrap_codes(text, f"1;{codes}" if bold else codes)


def bold(text: str) -> str:
    """Return text in bold."""
    return _wrap_codes(text, "1")


def dim(text: str) -> str:
    """Return text in the dim grey of the palette."""
    return colour(text, GREY)


def bright(text: str) -> str:
    """Return text in the bright text colour."""
    return colour(text, BRIGHT)


def badge(text: str, background: str, foreground: str = INK) -> str:
    """Return a pill: bold text on a coloured background, one space of padding each side."""
    return _wrap_codes(f" {text} ", f"1;38;2;{_rgb(foreground)};48;2;{_rgb(background)}")


def title(text: str) -> str:
    """Return a section title in bold pink, with no rule under it."""
    return colour(text, PINK, bold=True)


def strip(text: str) -> str:
    """Return text without its escape sequences."""
    return _ESCAPE.sub("", text)


def visible_len(text: str) -> int:
    """Return the number of characters a terminal shows for text."""
    return len(strip(text))


def pad(text: str, width: int) -> str:
    """Pad text with spaces on the right up to width visible characters."""
    return text + " " * max(0, width - visible_len(text))


def wrap(text: str, width: int, first: str = "", rest: str = "") -> list[str]:
    """Wrap text on spaces to width visible characters, ignoring escapes when measuring.

    A word longer than the line is kept whole, so a path is never broken.
    """
    lines: list[str] = []
    current = first
    started = False
    for word in text.split():
        if started and visible_len(current) + 1 + visible_len(word) > width:
            lines.append(current)
            current, started = rest, False
        current += (" " if started else "") + word
        started = True
    lines.append(current)
    return lines


def box(lines: list[str], border: str = PURPLE) -> list[str]:
    """Draw a rounded box around lines, one space of padding inside each side."""
    inner = max((visible_len(line) for line in lines), default=0)
    side = colour("│", border)
    out = [colour("╭" + "─" * (inner + 2) + "╮", border)]
    out += [f"{side} {pad(line, inner)} {side}" for line in lines]
    out.append(colour("╰" + "─" * (inner + 2) + "╯", border))
    return out
