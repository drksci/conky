"""An expression laid out in lines for the view to print as written, never reflowed.

    from bench.expression import lines
    lines("a && b || c.d().e()", width=36)

Pure and deterministic: text in, lines out, nothing evaluated. An expression that fits the width
is one line. A longer one breaks, in this order of preference, at the first kind of place it has
at the top level (outside brackets): before `&&` and `||`; before the `?` and `:` of a ternary;
before each `.call(` of a method chain after the first call. Every line after the first is
indented two spaces, and a line still too long breaks again inside, two spaces deeper. A break is
never made inside a string, a number or a name, so joining the lines gives the text back.
"""

from __future__ import annotations

import re

WIDTH = 36  # characters a line of an expression holds in a cell before it breaks
INDENT = "  "
TOKEN = re.compile(
    r"""("(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*'|\d+(?:\.\d+)?|[A-Za-z_][A-Za-z0-9_]*|&&|\|\||[=!<>]=|\s+|.)""",
    re.DOTALL,
)
OPEN, CLOSE = "([{", ")]}"


def tokens(text: str) -> list[str]:
    """The text split into strings, numbers, names, operators and runs of space."""
    return TOKEN.findall(text)


def _top(parts: list[str]) -> list[int]:
    """The depth of brackets each token sits at, the opening and closing ones at the outer."""
    depth, out = 0, []
    for tok in parts:
        if tok in CLOSE:
            depth = max(depth - 1, 0)
        out.append(depth)
        if tok in OPEN:
            depth += 1
    return out


def _cuts(parts: list[str]) -> list[int]:
    """Where a too long expression breaks: the indexes of the tokens a new line starts with."""
    depth = _top(parts)
    top = [i for i, tok in enumerate(parts) if depth[i] == 0]
    logic = [i for i in top if parts[i] in ("&&", "||")]
    if logic:
        return logic
    ternary = [i for i in top if parts[i] in ("?", ":")]
    if ternary:
        return ternary
    chain = []
    for i in top:
        before = next((parts[k] for k in range(i - 1, -1, -1) if not parts[k].isspace()), "")
        named = i + 2 < len(parts) and re.match(r"[A-Za-z_]", parts[i + 1])
        if parts[i] == "." and before == ")" and named and parts[i + 2] == "(":
            chain.append(i)
    return chain


def _split(text: str, width: int, indent: str) -> list[str]:
    if len(indent) + len(text) <= width:
        return [indent + text]
    parts = tokens(text)
    cuts = [c for c in _cuts(parts) if "".join(parts[:c]).strip()]  # never before the first token
    if not cuts:
        return [indent + text]
    pieces, start = [], 0
    for at in [*cuts, len(parts)]:
        piece = "".join(parts[start:at]).strip()
        if piece:
            pieces.append(piece)
        start = at
    out = _split(pieces[0], width, indent)
    for piece in pieces[1:]:
        out += _split(piece, width, indent + INDENT)
    return out


def lines(text: str, width: int = WIDTH) -> list[str]:
    """The expression as lines of at most width characters where it has places to break."""
    flat = "".join(" " if tok.isspace() else tok for tok in tokens(str(text))).strip()
    return _split(flat, width, "") if flat else []
