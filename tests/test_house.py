"""House rules: the plain vocabulary and no fix-later notes."""

import importlib.util
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SELF = Path(__file__).resolve()

# Built from parts so this file does not trip its own checks.
RETIRED = [
    "cre" + "st",
    "sur" + "face",
    "sl" + "ot",
    "gu" + "ard",
    "pu" + "lse",
    "et" + "ch",
    "pe" + "ek",
    "air" + "lock",
    "wa" + "rd",
    "re" + "alm",
    "spr" + "awl",
    "for" + "ge",
    "cap" + "sule",
]
MARKERS = ["TO" + "DO", "FIX" + "ME", "X" + "XX", "HA" + "CK"]


def vocabulary_files() -> list[Path]:
    files = list((ROOT / "src").rglob("*.py"))
    files += [p for p in (ROOT / "tests").rglob("*.py") if p.resolve() != SELF]
    files += [ROOT / "README.md", ROOT / "CLAUDE.md", ROOT / "docs" / "design.md"]
    return [p for p in files if p.exists()]


def marker_files() -> list[Path]:
    files = []
    for folder in ("src", "tests", "scripts"):
        files += [
            p
            for p in (ROOT / folder).rglob("*")
            if p.is_file() and p.suffix in {".py", ".md", ".toml"}
        ]
    return [p for p in files if p.resolve() != SELF]


def find(pattern: re.Pattern[str], files: list[Path]) -> list[str]:
    found = []
    for path in files:
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            for match in pattern.finditer(line):
                found.append(f"{path.relative_to(ROOT)}:{number}: {match.group(0)}")
    return found


def test_retired_words_do_not_appear():
    pattern = re.compile(r"\b(" + "|".join(RETIRED) + r")\b", re.IGNORECASE)
    assert find(pattern, vocabulary_files()) == []


def test_no_fix_later_notes():
    pattern = re.compile(r"\b(" + "|".join(MARKERS) + r")\b")
    assert find(pattern, marker_files()) == []


def load_check_commits():
    path = ROOT / "scripts" / "check_commits.py"
    spec = importlib.util.spec_from_file_location("check_commits", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_commit_subject_matching():
    ok = load_check_commits().subject_ok
    assert ok("feat: add a thing")
    assert ok("chore: x" + "y" * 60)
    assert not ok("Add a thing")
    assert not ok("feature: add a thing")
    assert not ok("fix: Capital start")
    assert not ok("fix: trailing full stop.")
    assert not ok("fix:no space")
    assert not ok("docs: " + "y" * 67)


def test_changelog_has_unreleased_section():
    text = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    assert re.search(r"^## \[Unreleased\]$", text, re.MULTILINE)
