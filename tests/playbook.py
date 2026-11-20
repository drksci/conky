"""Run a playbook, a short scenario in YAML. The format is in docs/reference/playbooks.md."""

from pathlib import Path
from typing import Any

from conky import Vault
from conky.git import trailers
from conky.page import load_value

from .conftest import AT, git
from .test_pages import Stand

SETS = ("write", "says", "expect")


class Failed(AssertionError):
    """An expectation did not hold: names the playbook, the step, what was expected and found."""


def run(path: Path, vault: Vault, stand: Stand) -> None:
    """Build the starting pages, then play each step in order."""
    plan = load_value(path.read_text(encoding="utf-8"))
    last = None
    for page, fields in plan.get("pages", {}).items():
        made = vault.write(page, fields, None, actor="alice", at=AT)
        assert made.ok, f"{path.stem}: starting page {page} was refused: {made.reason}"
    for number, step in enumerate(plan["steps"], start=1):
        (kind,) = step
        if kind == "says":
            stand.says(step["says"])
        elif kind == "write":
            put = step["write"]
            last = vault.write(
                put["page"],
                put.get("fields", {}),
                put.get("body"),
                actor=put.get("actor", "alice"),
                at=AT,
            )
        elif kind == "expect":
            for found in expectations(step["expect"], vault, stand, last):
                raise Failed(f"{path.stem}, step {number}: {found}")
        else:
            raise Failed(f"{path.stem}, step {number}: unknown step {kind!r}, use one of {SETS}")


def expectations(expect: dict[str, Any], vault: Vault, stand: Stand, last: Any) -> list[str]:
    """Return one line for each expectation that does not hold."""
    out = []

    def check(what: str, wanted: Any, got: Any) -> None:
        if wanted != got:
            out.append(f"{what}: expected {wanted!r}, found {got!r}")

    for key, wanted in expect.items():
        if key == "fields":
            for where, value in wanted.items():
                page, field = where.split(".", 1)
                check(where, value, vault.read(page).fields.get(field))
        elif key == "exists":
            for page in wanted:
                check(f"{page} exists", True, (vault.pages_dir / f"{page}.md").exists())
        elif key == "missing":
            for page in wanted:
                check(f"{page} exists", False, (vault.pages_dir / f"{page}.md").exists())
        elif key == "refused":
            reason = None if last is None or last.ok else last.reason
            check("last write refused with", wanted, reason and reason.split(":")[0])
        elif key == "model_calls":
            check("model calls", wanted, len(stand.prompts))
        elif key == "model_commits":
            ids = git(vault.path, "log", "--format=%H", "main").split()
            said = [
                i
                for i in ids
                if "Model" in trailers(git(vault.path, "log", "-1", "--format=%B", i))
            ]
            check("commits answered by a model", wanted, len(said))
        elif key == "verify":
            vault.verify()
        else:
            out.append(f"unknown expectation {key!r}")
    return out
