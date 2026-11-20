"""The documentation check passes: frontmatter, folders, statuses and links."""

import importlib.util
import sys
from pathlib import Path

import pytest

from conky import arch

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "check_docs.py"


@arch.holds("law.docs.check")
def test_docs_pass_the_check():
    spec = importlib.util.spec_from_file_location("check_docs", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert module.check() == []


def test_paper_register_depths_are_valid():
    register = SCRIPT.parent.parent / "docs" / "research" / "papers.md"
    rows = []
    in_table = False
    for line in register.read_text(encoding="utf-8").splitlines():
        if line.startswith("| Paper |"):
            in_table = True
            continue
        if in_table and line.startswith("|---"):
            continue
        if in_table and line.startswith("|"):
            rows.append([cell.strip() for cell in line.strip("|").split("|")])
        elif in_table:
            break
    assert rows, "no register rows found"
    bad = [row[0] for row in rows if row[2] not in {"listed", "abstract", "read"}]
    assert bad == []


def load_check():
    spec = importlib.util.spec_from_file_location("check_docs", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_scan_reminder_is_silent_when_fresh_and_at_seven_days_and_speaks_when_stale():
    from datetime import date

    remind = load_check().scan_reminder
    today = date(2026, 11, 20)
    assert remind("2026-11-20", today) is None
    assert remind("2026-11-13", today) is None
    stale = remind("2026-11-12", today)
    assert stale == (
        "reminder: docs/research/dair-2026.md was last scanned on 2026-11-12, 8 days ago: "
        "rescan its source and update the index and docs/research/papers.md"
    )
    assert remind(date(2026, 11, 1), today).startswith("reminder:")
    assert remind("not a date", today) is None


def load_generator():
    path = SCRIPT.parent / "gen_architecture.py"
    spec = importlib.util.spec_from_file_location("gen_architecture", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules["gen_architecture"] = module
    spec.loader.exec_module(module)
    return module


def test_the_architecture_page_is_what_the_generator_makes():
    assert load_generator().check() == []


def test_the_generator_names_what_to_fix():
    gen = load_generator()
    with pytest.raises(gen.ArchitectureError, match="heading that does not exist"):
        gen.check_link("vault-format.md#no-such-heading", "a row")
    with pytest.raises(gen.ArchitectureError, match="is done, so this is built"):
        gen.state_of("R2", None, "a row", False)
    with pytest.raises(gen.ArchitectureError, match="says is later"):
        gen.state_of("R22", None, "a marker", True)
    with pytest.raises(gen.ArchitectureError, match="is not in docs/project/roadmap.md"):
        gen.state_of("R999", None, "a row", False)


def test_every_diagram_has_the_same_lanes_in_the_same_order():
    gen = load_generator()
    made = gen.build()
    lanes = ["    participant " + lane for lane in gen.arch.LANES]
    diagrams = made.split("```mermaid")[2:]
    assert len(diagrams) >= 25
    for text in diagrams:
        found = [line for line in text.splitlines() if line.startswith("    participant ")]
        assert found == lanes
