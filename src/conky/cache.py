"""A cache for costly work: derived data that sits beside the keys, outside any vault's history.

An entry is a small JSON file named by the hash of everything that decides its answer. The cache
is never the truth: deleting it loses nothing but the cost of asking again, and an entry that
cannot be read is a miss.
"""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Any

from conky import arch
from conky.errors import BadInput

DIR_VARIABLE = "CONKY_CACHE_DIR"
MODE_VARIABLE = "CONKY_CACHE"
MAX_VARIABLE = "CONKY_CACHE_MAX"
DEFAULT_MAX_MB = 64
SUFFIX = ".json"
PARTIAL = ".partial"


class Mode(StrEnum):
    """What the cache may do: the word of CONKY_CACHE and of `--cache-mode`."""

    ON = "on"
    OFF = "off"
    REFRESH = "refresh"
    ONLY = "only"


def default_dir() -> Path:
    """Return the cache directory, beside the default key directory and outside any vault."""
    return Path.home() / ".conky" / "cache"


def digest(*parts: str) -> str:
    """Return the hash of parts, each length-prefixed so that no two lists of parts collide."""
    hasher = hashlib.sha256()
    for part in parts:
        raw = part.encode("utf-8")
        hasher.update(f"{len(raw)}:".encode("ascii"))
        hasher.update(raw)
    return hasher.hexdigest()


@dataclass(frozen=True)
class Stats:
    """How many entries the cache holds and how many bytes they take."""

    entries: int
    size: int


@arch.part(
    "part.answer.cache",
    "layer.character",
    "Model answers kept outside the history, keyed to the moment.",
    doc="providers.md#cache",
    roadmap="R30",
)
@arch.change(
    "place.beside.cache",
    "Cached answers: derived data outside every vault, deletable.",
    doc="providers.md#cache",
    roadmap="R30",
)
@dataclass(frozen=True)
class Cache:
    """A directory of entries, a mode and a size bound in bytes."""

    directory: Path
    mode: Mode = Mode.ON
    limit: int = DEFAULT_MAX_MB * 1024 * 1024

    @classmethod
    def open(cls, directory: str | Path | None = None, mode: str | None = None) -> Cache:
        """Return the cache named by the arguments, else by the environment, else the defaults."""
        env = os.environ
        chosen = mode or env.get(MODE_VARIABLE, "").strip().lower() or Mode.ON
        try:
            found = Mode(chosen)
        except ValueError as exc:
            where = "--cache-mode" if mode else MODE_VARIABLE
            raise BadInput(f"{where} is {chosen!r}: use one of {', '.join(Mode)}") from exc
        text = env.get(MAX_VARIABLE, "").strip()
        try:
            megabytes = float(text) if text else DEFAULT_MAX_MB
        except ValueError:
            megabytes = -1
        if megabytes < 0:
            raise BadInput(
                f"{MAX_VARIABLE} is {text!r}: set it to the most megabytes to keep, such as 64"
            )
        place = directory or env.get(DIR_VARIABLE, "").strip() or default_dir()
        return cls(Path(place), found, int(megabytes * 1024 * 1024))

    def get(self, key: str) -> Any | None:
        """Return the value stored under key, or None on a miss, a corrupt entry or mode off."""
        if self.mode in (Mode.OFF, Mode.REFRESH):
            return None
        path = self._path(key)
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
            os.utime(path)
        except (OSError, ValueError):
            return None
        return value

    def put(self, key: str, value: Any) -> None:
        """Store value under key, then drop the oldest entries beyond the bound.

        Nothing is stored in mode `off` or `only`. A cache that cannot be written is skipped.
        """
        if self.mode in (Mode.OFF, Mode.ONLY):
            return
        try:
            self.directory.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile(
                "w", encoding="utf-8", dir=self.directory, suffix=PARTIAL, delete=False
            ) as handle:
                json.dump(value, handle, ensure_ascii=False)
            os.replace(handle.name, self._path(key))
            self._trim(self._path(key))
        except (OSError, TypeError, ValueError):
            return

    def stats(self) -> Stats:
        """Return the entry count and byte size, counting nothing when there is no directory."""
        sizes = [size for _, size, _ in self._entries()]
        return Stats(len(sizes), sum(sizes))

    def clear(self) -> int:
        """Delete every entry and return how many there were."""
        removed = 0
        for path in self._files():
            try:
                path.unlink()
            except OSError:
                continue
            removed += path.suffix == SUFFIX
        return removed

    def _path(self, key: str) -> Path:
        return self.directory / f"{key}{SUFFIX}"

    def _files(self) -> list[Path]:
        try:
            return [p for p in self.directory.iterdir() if p.suffix in (SUFFIX, PARTIAL)]
        except OSError:
            return []

    def _entries(self) -> list[tuple[Path, int, float]]:
        found = []
        for path in self._files():
            try:
                info = path.stat()
            except OSError:
                continue
            if path.suffix == SUFFIX:
                found.append((path, info.st_size, info.st_mtime))
        return found

    def _trim(self, keep: Path) -> None:
        entries = sorted(self._entries(), key=lambda e: e[2])
        total = sum(size for _, size, _ in entries)
        for path, size, _ in entries:
            if total <= self.limit:
                break
            if path == keep:
                continue
            try:
                path.unlink()
            except OSError:
                continue
            total -= size
