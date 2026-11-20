"""Check commit subjects: `<type>: <summary>`, at most 72 characters."""

from __future__ import annotations

import re
import subprocess
import sys

TYPES = ("feat", "fix", "docs", "test", "refactor", "chore")
MAX_LENGTH = 72
FALLBACK_COUNT = 20
SUBJECT = re.compile(r"^(" + "|".join(TYPES) + r"): [^A-Z\s].*$")


def subject_ok(subject: str) -> bool:
    """True if the subject is `<type>: <summary>` with a lower-case start and no full stop."""
    return len(subject) <= MAX_LENGTH and not subject.endswith(".") and bool(SUBJECT.match(subject))


def git(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], capture_output=True, text=True)


def subjects() -> list[str]:
    """Subjects of non-merge commits not on origin/main, else of the last 20 commits."""
    if git("rev-parse", "--verify", "--quiet", "refs/remotes/origin/main").returncode == 0:
        args = ["log", "--no-merges", "--format=%s", "origin/main..HEAD"]
    else:
        args = ["log", "--no-merges", "--format=%s", f"-{FALLBACK_COUNT}"]
    result = git(*args)
    if result.returncode != 0:
        print(result.stderr.strip())
        raise SystemExit(1)
    return result.stdout.splitlines()


def main() -> int:
    bad = [s for s in subjects() if not subject_ok(s)]
    for subject in bad:
        print(f"bad commit subject: {subject}")
    if bad:
        print(f"{len(bad)} commit subject(s) do not match '<type>: <summary>'")
        return 1
    print("commit subjects ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
