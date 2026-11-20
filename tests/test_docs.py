"""The documentation check passes: frontmatter, folders, statuses and links."""

import importlib.util
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "check_docs.py"


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
