"""conky: a runtime where every actor is a living Markdown page."""

from conky.errors import BadInput, VerifyFailed
from conky.page import Page
from conky.vault import Result, Vault

__all__ = ["BadInput", "Page", "Result", "Vault", "VerifyFailed"]
__version__ = "0.1.0"
