"""Run a playbook, a short scenario in YAML. The format is in docs/reference/playbooks.md."""

import re
from collections.abc import Callable
from pathlib import Path
from typing import Any

import celpy

from conky import Vault
from conky.git import trailers
from conky.page import load_value

from .conftest import AT, git
from .test_pages import Stand

SETS = ("write", "says", "expect")
LIVE = "live"


class Failed(AssertionError):
    """An expectation did not hold: names the playbook, the step, what was expected and found."""


def run(
    path: Path,
    vault: Vault,
    stand: Stand,
    found: Callable[[int, list[str]], None] | None = None,
) -> None:
    """Build the starting pages, then play each step in order.

    A step `says: live` asks a real model, so it is an error here unless found is given, which
    is how a card runs a playbook. With found, a failed expect step is reported to it as its
    number and the lines that failed, passing steps as no lines, and the run goes on.
    """
    plan = load_value(path.read_text(encoding="utf-8"))
    last = None
    if found is None and any("judged" in s.get("expect", {}) for s in plan["steps"]):
        raise Failed(
            f"{path.stem}: judged checks ask a judge model, which a playbook test never does: "
            f"run this file as a card, python -m bench.cards {path} --draws 1"
        )
    for page, fields in plan.get("pages", {}).items():
        made = vault.write(page, fields, None, actor="alice", at=AT)
        assert made.ok, f"{path.stem}: starting page {page} was refused: {made.reason}"
    for number, step in enumerate(plan["steps"], start=1):
        (kind,) = step
        if kind == "says":
            if step["says"] == LIVE and found is None:
                raise Failed(
                    f"{path.stem}, step {number}: says: live asks a real model, "
                    f"which a playbook test never does: run this file as a card, "
                    f"python -m bench.cards {path} --draws 1"
                )
            stand.says(step["says"])
        elif kind == "write":
            put = step["write"]
            places = [None]
            if "each_ruled" in put:
                places = ruled(vault, put["each_ruled"])
            for place in places:
                fields = put.get("fields", {})
                if place is not None:
                    fields = {**fields, "within": place}
                last = vault.write(
                    put["page"], fields, put.get("body"), actor=put.get("actor", "alice"), at=AT
                )
                if not last.ok:
                    break
        elif kind == "expect":
            lines = expectations(step["expect"], vault, stand, last)
            if found is not None:
                found(number, lines)
            elif lines:
                raise Failed(f"{path.stem}, step {number}: {lines[0]}")
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
        elif key == "rules":
            for page, least in wanted.items():
                held = vault.read(page).rules if (vault.pages_dir / f"{page}.md").exists() else []
                texts = [r if isinstance(r, str) else r["each"] for r in held]
                check(f"{page} has at least {least} rules that parse", True, parsed(texts) >= least)
        elif key == "each_rules":
            for space, least in wanted.items():
                held = [space, *inside(vault, space)]
                count = sum(parsed(each_rules(vault, page)) for page in held)
                what = (
                    f"{space} and the pages within it carry at least {least} each rules that parse"
                )
                check(what, True, count >= least)
        elif key == "within_fields":
            for space, fields in wanted.items():
                for field, pattern in fields.items():
                    got = [str(vault.read(p).fields.get(field)) for p in inside(vault, space)]
                    if not any(re.search(str(pattern), g) for g in got):
                        out.append(f"no page within {space} has {field} matching {pattern!r}")
        elif key == "answer":
            for where, pattern in wanted.items():
                page, field = where.split(".", 1)
                got = vault.read(page).fields.get(field)
                if not re.search(str(pattern), "" if got is None else str(got)):
                    out.append(f"{where}: expected a match for {pattern!r}, found {got!r}")
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
        elif key == "judged":
            continue  # a card's judge answers these, see bench/cards.py
        else:
            out.append(f"unknown expectation {key!r}")
    return out


def inside(vault: Vault, space: str) -> list[str]:
    """Return the pages that lie within space, at any depth."""
    found = []
    for path in sorted(vault.pages_dir.glob("*.md")):
        seen, above = {path.stem}, vault.read(path.stem).within
        while above is not None and above != space and above not in seen:
            seen.add(above)
            above = vault.read(above).within
        if above == space:
            found.append(path.stem)
    return found


def each_rules(vault: Vault, page: str) -> list[str]:
    """Return the conditions of the `each` rules a page carries."""
    return [r["each"] for r in vault.read(page).rules if isinstance(r, dict)]


def ruled(vault: Vault, space: str) -> list[str]:
    """Return the pages within space that carry an `each` rule."""
    return [page for page in inside(vault, space) if each_rules(vault, page)]


def parsed(rules: list[str]) -> int:
    """Count the rules that are valid expressions."""
    count = 0
    for rule in rules:
        try:
            celpy.Environment().compile(rule)
        except celpy.CELParseError:
            continue
        count += 1
    return count
