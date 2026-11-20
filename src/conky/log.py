"""The event log: append-only canonical JSON lines, hash-chained and sealed."""

from __future__ import annotations

import hashlib
import json
import os
from collections.abc import Callable
from pathlib import Path
from typing import Any

ZERO = "0" * 64


def canonical(obj: Any) -> str:
    """Return obj as canonical JSON: sorted keys, no extra whitespace, UTF-8 text."""
    return json.dumps(
        obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False
    )


def digest(line: str) -> str:
    """Return the hex sha256 of a canonical line."""
    return hashlib.sha256(line.encode("utf-8")).hexdigest()


class Log:
    """The append-only file of events."""

    def __init__(self, path: Path) -> None:
        self.path = path

    def lines(self) -> list[str]:
        """Return every line of the log, without newlines."""
        if not self.path.exists():
            return []
        lines = self.path.read_text(encoding="utf-8").split("\n")
        return lines[:-1] if lines[-1] == "" else lines

    def events(self) -> list[dict[str, Any]]:
        """Return every event in order."""
        return [json.loads(line) for line in self.lines()]

    def append(self, event: dict[str, Any], sign: Callable[[bytes], str]) -> dict[str, Any]:
        """Chain, seal and append event; return it as stored."""
        lines = self.lines()
        event = {**event, "seq": len(lines), "prev": digest(lines[-1]) if lines else ZERO}
        event["seal"] = sign(canonical(event).encode("utf-8"))
        with self.path.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(canonical(event) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        return event
