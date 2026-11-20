"""Rules: pure CEL expressions evaluated with cel-python."""

from __future__ import annotations

from typing import Any

import celpy
from celpy import celtypes

from conky import arch

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
        program = _ENV.program(_ENV.compile(expression))
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
