"""Fetch the 1975 Oregon Trail port at run time. It is never copied into this repository.

The game is James LaPlaine's Python 3 port of the 1975 HP2000 BASIC program by the Minnesota
Educational Computing Consortium, at https://github.com/csangos/oregon-trail . The repository
carries no licence file, so the bench fetches it into a cache outside this repository, pinned to
one commit, and checks the SHA-256 of `main.py` before it is run.

    python -m bench.envs.oregon_trail_1975.fetch [--cache DIR]
"""

from __future__ import annotations

import argparse
import hashlib
import os
import shutil
import subprocess
import sys
from pathlib import Path

REPOSITORY = "https://github.com/csangos/oregon-trail"
COMMIT = "1ef659a"
MAIN_SHA256 = "c2713c999febe2be2eeb082aa1e6dd52d02537263c530087e2a4a7d41fb74372"


class FetchError(Exception):
    """The game could not be fetched or is not the pinned one; the message says what to do."""


def default_cache() -> Path:
    base = os.environ.get("XDG_CACHE_HOME") or str(Path.home() / ".cache")
    return Path(base) / "conky-bench"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _git(args: list[str], cwd: Path) -> None:
    done = subprocess.run(
        ["git", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        env={**os.environ, "GIT_TERMINAL_PROMPT": "0", "GIT_CONFIG_NOSYSTEM": "1"},
        check=False,
    )
    if done.returncode != 0:
        detail = (done.stderr.strip() or done.stdout.strip() or "no output").splitlines()[-1]
        raise FetchError(f"git {args[0]} failed: {detail}")


def fetch(
    cache: Path | None = None,
    repository: str = REPOSITORY,
    commit: str = COMMIT,
    sha256: str = MAIN_SHA256,
) -> Path:
    """Return the path of the pinned `main.py`, cloning it into the cache on first use."""
    cache = cache or default_cache()
    where = cache / f"oregon-trail-1975-{commit}"
    main = where / "main.py"
    if not main.exists():
        cache.mkdir(parents=True, exist_ok=True)
        spare = cache / f".partial-{commit}"
        shutil.rmtree(spare, ignore_errors=True)
        try:
            _git(["clone", "-q", "--no-checkout", repository, str(spare)], cache)
            _git(["checkout", "-q", commit], spare)
        except FetchError as exc:
            shutil.rmtree(spare, ignore_errors=True)
            raise FetchError(
                f"cannot fetch {repository} at {commit}: {exc}. Check the network, or clone it "
                f"yourself and check out {commit} into {where}"
            ) from exc
        shutil.rmtree(where, ignore_errors=True)
        spare.rename(where)
    found = digest(main)
    if found != sha256:
        raise FetchError(
            f"{main} has SHA-256 {found}, not the pinned {sha256}: delete {where} and fetch "
            "again, or review the change before pinning a new hash"
        )
    return main


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch the pinned 1975 Oregon Trail port.")
    parser.add_argument("--cache", type=Path, default=None)
    try:
        print(fetch(parser.parse_args().cache))
    except FetchError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
