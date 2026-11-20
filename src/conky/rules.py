"""Rules: pure CEL expressions evaluated with cel-python."""

from __future__ import annotations

import re
from typing import Any

import celpy
from celpy import celtypes

from conky import arch

MAX_TEXT = 65536
MAX_PATTERN = 256


# Text functions. The names and shapes of all but `captures` follow the CEL strings extension
# (cel-go ext/README.md, "Strings"); `captures` is conky's own, because the standard regex
# extension needs optional types and a single group. Each is pure and bounded by MAX_TEXT and
# MAX_PATTERN; a failure raises ValueError, which evaluation turns into a RuleError.

_FUNCTIONS: dict[str, Any] = {}


def _text(*values: str) -> None:
    for value in values:
        if len(value) > MAX_TEXT:
            raise ValueError(f"text is longer than {MAX_TEXT} characters")


def _function(name: str, meaning: str):
    def register(fn):
        _FUNCTIONS[name] = fn
        doc = "rules-and-reactions.md#text-functions"
        return arch.part(f"part.rule.{name.lower()}", "layer.reflex", meaning, doc=doc)(fn)

    return register


def _str(value: str) -> celtypes.StringType:
    return celtypes.StringType(value)


def _strs(values: list[str]) -> celtypes.ListType:
    return celtypes.ListType([_str(v) for v in values])


@_function("split", "Split text on a separator, with an optional limit on the pieces.")
def _split(text: str, sep: str, limit: int = -1) -> celtypes.ListType:
    _text(text, sep)
    if limit == 0:
        return _strs([])
    if sep == "":
        chars = list(text)
        if 0 < limit < len(chars):
            chars = [*chars[: limit - 1], "".join(chars[limit - 1 :])]
        return _strs(chars)
    return _strs(text.split(sep, limit - 1 if limit > 0 else -1))


@_function("substring", "Take the characters from a start to an optional end position.")
def _substring(text: str, start: int, end: int | None = None) -> celtypes.StringType:
    _text(text)
    stop = len(text) if end is None else int(end)
    if not 0 <= start <= stop <= len(text):
        raise ValueError("substring positions are out of range")
    return _str(text[int(start) : stop])


@_function("indexOf", "The position of a substring from an optional start, or -1.")
def _index_of(text: str, find: str, start: int = 0) -> celtypes.IntType:
    _text(text, find)
    if start < 0:
        raise ValueError("indexOf start is negative")
    return celtypes.IntType(text.find(find, int(start)) if start <= len(text) else -1)


@_function("trim", "Remove leading and trailing whitespace.")
def _trim(text: str) -> celtypes.StringType:
    _text(text)
    return _str(text.strip())


@_function("lowerAscii", "Lower-case the ASCII letters only.")
def _lower_ascii(text: str) -> celtypes.StringType:
    _text(text)
    return _str("".join(c.lower() if c.isascii() else c for c in text))


@_function("replace", "Replace occurrences of a substring, with an optional limit.")
def _replace(text: str, find: str, by: str, limit: int = -1) -> celtypes.StringType:
    _text(text, find, by)
    out = text.replace(find, by, int(limit)) if limit >= 0 else text.replace(find, by)
    _text(out)
    return _str(out)


@_function("join", "Join a list of text with an optional separator.")
def _join(items: list[str], sep: str = "") -> celtypes.StringType:
    _text(sep)
    out = sep.join(str(i) for i in items)
    _text(out)
    return _str(out)


@_function("captures", "The groups of the first match of a pattern, else an empty list.")
def _captures(text: str, pattern: str) -> celtypes.ListType:
    _text(text)
    if len(pattern) > MAX_PATTERN:
        raise ValueError(f"pattern is longer than {MAX_PATTERN} characters")
    try:
        found = re.search(pattern, text)
    except re.error as exc:
        raise ValueError(f"bad pattern: {exc}") from exc
    if found is None:
        return _strs([])
    return _strs([g or "" for g in found.groups()] if found.re.groups else [found.group(0)])


_ENV = celpy.Environment()


class RuleError(Exception):
    """An expression failed to parse, failed to evaluate or returned an unusable value."""


def _plain(value: Any) -> Any:
    if isinstance(value, celtypes.BoolType):
        return bool(value)
    if isinstance(value, celtypes.IntType | celtypes.UintType):
        return int(value)
    if isinstance(value, celtypes.DoubleType):
        return float(value)
    if isinstance(value, celtypes.StringType):
        return str(value)
    if isinstance(value, celtypes.ListType):
        return [_plain(v) for v in value]
    if isinstance(value, celtypes.MapType):
        return {str(k): _plain(v) for k, v in value.items()}
    if value is None or isinstance(value, celtypes.NullType):
        return None
    raise RuleError(f"result of type {type(value).__name__} cannot be stored")


@arch.law(
    "law.rule.pure",
    "Rules and measures are pure: no clock, randomness or input and output.",
    doc="rules-and-reactions.md#expressions",
)
def evaluate(expression: str, variables: dict[str, Any]) -> Any:
    """Evaluate expression with the given variables and return a plain Python value."""
    try:
        program = _ENV.program(_ENV.compile(expression), functions=_FUNCTIONS)
        result = program.evaluate({k: celpy.json_to_cel(v) for k, v in variables.items()})
    except (celpy.CELParseError, celpy.CELEvalError) as exc:
        raise RuleError(str(exc).strip().splitlines()[0] if str(exc).strip() else "error") from exc
    return _plain(result)


@arch.law(
    "law.rule.never",
    "Anything that must never happen is a rule the runtime evaluates.",
    doc="rules-and-reactions.md#expressions",
)
@arch.part(
    "part.rule",
    "layer.reflex",
    "A CEL expression judged before a write is kept.",
    doc="rules-and-reactions.md#expressions",
)
def holds(expression: str, variables: dict[str, Any]) -> bool:
    """Return True only if expression evaluates to the boolean true."""
    return evaluate(expression, variables) is True
