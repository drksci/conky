"""House rules: the vocabulary page agrees with the code, and there are no fix-later notes."""

import argparse
import importlib
import importlib.util
import pkgutil
import re
from pathlib import Path

import pytest

import conky
from conky import arch, cache, cli, connect, model, page, present, voice
from conky.vault import KINDS, Refusal, Trailer

ROOT = Path(__file__).resolve().parent.parent
SELF = Path(__file__).resolve()

# Built from parts so this file does not trip its own check.
MARKERS = ["TO" + "DO", "FIX" + "ME", "X" + "XX", "HA" + "CK"]
PAGE = ROOT / "docs" / "reference" / "vocabulary.md"


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


@arch.holds("law.debt.none")
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


def vocabulary() -> dict[str, list[str]]:
    """Return each table of the vocabulary page: its heading and the names in its first column."""
    tables: dict[str, list[str]] = {}
    heading = None
    for line in PAGE.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            heading = line[3:].strip()
        elif heading and line.startswith("| `"):
            name, meaning = line.strip("| ").split("|", 1)[0], line.split("|")[2].strip()
            assert meaning, f"{heading}: {name.strip()} has no meaning: write one in {PAGE}"
            tables.setdefault(heading, []).append(name.strip().strip("`"))
    return tables


def subparsers(parser: argparse.ArgumentParser) -> dict[str, argparse.ArgumentParser]:
    """Return the sub-parsers of a parser by name, or nothing when it has none."""
    for action in parser._actions:
        if isinstance(action, argparse._SubParsersAction):
            return dict(action.choices)
    return {}


def options(parser: argparse.ArgumentParser) -> set[str]:
    """Return the long options a parser defines itself, leaving out help and repeats of globals."""
    return {
        flag
        for action in parser._actions
        for flag in action.option_strings
        if flag.startswith("--") and flag != "--help" and action.default != argparse.SUPPRESS
    }


def errors() -> set[str]:
    """Return the names of the exception classes the package defines."""
    found = set()
    for info in pkgutil.iter_modules(conky.__path__):
        module = importlib.import_module(f"conky.{info.name}")
        found |= {
            name
            for name, value in vars(module).items()
            if isinstance(value, type)
            and issubclass(value, Exception)
            and value.__module__ == module.__name__
        }
    return found


def command_options() -> set[str]:
    found = set()
    for name, parser in subparsers(cli._parser()).items():
        found |= {f"{name} {flag}" for flag in options(parser)}
        for inner, sub in subparsers(parser).items():
            found |= {f"{name} {inner} {flag}" for flag in options(sub)}
    return found


def code() -> dict[str, set[str]]:
    """Return every set of names the code exposes, keyed by the heading that lists it."""
    parser = cli._parser()
    return {
        "Commands": set(subparsers(parser)),
        "Global options": options(parser),
        "Command options": command_options(),
        "Connectors": set(subparsers(subparsers(parser)["connect"])),
        "Reserved keys": set(page.RESERVED),
        "Shows keys": set(page.SHOWS_KEYS),
        "Watch keys": set(page.WATCH_KEYS),
        "Watch relations": set(page.RELATIONS),
        "Ask keys": set(page.ASK_KEYS),
        "Trailer keys": {str(key) for key in Trailer},
        "Kinds": set(KINDS),
        "Refusals": {str(word) for word in Refusal},
        "Errors": errors(),
        "Cache modes": {str(mode) for mode in cache.Mode},
        "Provider shapes": set(model.APIS),
        "Provider choices": set(model.CHOICES),
        "Built-in commands": set(model.BUILTIN_COMMANDS),
        "Environment variables": {
            model.PROVIDER_VARIABLE,
            model.MODEL_VARIABLE,
            *model.KEY_VARIABLES.values(),
            model.SECRET_PREFIX + "<NAME>",
            model.COMMAND_PREFIX + "<NAME>",
            cache.MODE_VARIABLE,
            cache.DIR_VARIABLE,
            cache.MAX_VARIABLE,
            present.NO_COLOR,
            connect.TERM,
        },
    }


def test_every_table_is_checked_or_stated():
    stated = {"Concepts", "Verbs"}
    unknown = set(vocabulary()) - set(code()) - stated
    assert not unknown, f"{PAGE} has a table the code is not compared with: {sorted(unknown)}"


@arch.holds("law.word.exist")
@pytest.mark.parametrize("heading", sorted(code()))
def test_vocabulary_agrees_with_the_code(heading):
    listed = vocabulary().get(heading, [])
    assert len(listed) == len(set(listed)), f"{heading}: a name is listed twice in {PAGE}"
    exposed = code()[heading]
    missing = sorted(exposed - set(listed))
    gone = sorted(set(listed) - exposed)
    assert not missing, f"{heading}: the code has {missing}: add a row for each to {PAGE}"
    assert not gone, (
        f"{heading}: {PAGE} lists {gone}, which the code no longer has: remove the rows"
    )


def test_concepts_and_verbs_are_stated():
    tables = vocabulary()
    for heading in ("Concepts", "Verbs"):
        assert tables.get(heading), f"{PAGE} needs a {heading} table: restore it"
        assert len(tables[heading]) == len(set(tables[heading])), f"{heading}: a word repeats"


def test_the_rules_point_at_the_page():
    text = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
    assert "docs/reference/vocabulary.md" in text, "CLAUDE.md must name the vocabulary page"


def test_every_line_the_runtime_says_to_a_model_is_on_the_voice_page_and_used():
    asked = set()
    for path in (ROOT / "src" / "conky").glob("*.py"):
        asked |= set(re.findall(r'voice\.(?:line|told)\(\s*"([a-z-]+)"', path.read_text("utf-8")))
    held = voice.names()
    assert not asked - held, f"the code asks voice.md for {sorted(asked - held)}: add a section"
    assert not held - asked, f"voice.md holds {sorted(held - asked)}, which nothing says: remove it"
    for key in held:
        assert voice.line(key, **dict.fromkeys(FILLED, "x")), f"{key} is empty"
    assert voice.line("plain") == model.PLAIN


FILLED = [
    *("keys", "cap", "page", "space", "reason", "shown", "least"),
    *("entry", "root", "name", "where", "other"),
]
