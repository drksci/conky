"""Exceptions for caller mistakes and failed verification."""

from conky import arch


@arch.part(
    "error",
    "history",
    "A message that says what went wrong and what to do next.",
    doc="cli.md#errors",
)
class BadInput(Exception):
    """The caller passed something that cannot be a name, a value or a page."""


class VerifyFailed(Exception):
    """The vault does not verify; the message names the first failure."""
