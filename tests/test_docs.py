"""The documentation check passes: frontmatter, folders, statuses and links."""

import importlib.util
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "check_docs.py"


def test_docs_pass_the_check():
    spec = importlib.util.spec_from_file_location("check_docs", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert module.check() == []
