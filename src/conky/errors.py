"""Exceptions for caller mistakes and failed verification."""


class BadInput(Exception):
    """The caller passed something that cannot be a name, a value or a page."""


class VerifyFailed(Exception):
    """The vault does not verify; the message names the first failure."""
