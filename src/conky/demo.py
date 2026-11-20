"""Worked examples: small vaults built step by step from a data file, with a running commentary."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from importlib import resources
from pathlib import Path
from typing import Any

from conky.errors import BadInput
from conky.page import check_name, load_value
from conky.present import Outcome, Plain
from conky.vault import Vault


@dataclass(frozen=True)
class Step:
    """One step of an example: what to say, and the write that follows."""

    say: str
    page: str
    actor: str
    fields: dict[str, Any]
    body: str | None


@dataclass(frozen=True)
class Example:
    """A named example: a title, a one-line summary and ordered steps."""

    name: str
    title: str
    summary: str
    look_at: str
    steps: list[Step]


def available() -> list[str]:
    """Return the names of the shipped examples, sorted."""
    folder = resources.files("conky") / "examples"
    return sorted(
        p.name.removesuffix(".yaml") for p in folder.iterdir() if p.name.endswith(".yaml")
    )


def load(name: str) -> Example:
    """Read and check the shipped example called name."""
    if name not in available():
        raise BadInput(f"no example named {name!r}: run `conky demo --list` to see the examples")
    text = (resources.files("conky") / "examples" / f"{name}.yaml").read_text(encoding="utf-8")
    return parse(name, load_value(text))


def parse(name: str, data: Any) -> Example:
    """Check the shape of an example and return it."""

    def bad(why: str) -> BadInput:
        return BadInput(f"example {name!r} is malformed: {why}")

    if not isinstance(data, dict):
        raise bad("expected a mapping with title, summary and steps")
    for key in ("title", "summary", "look_at"):
        if not isinstance(data.get(key), str) or not data[key].strip():
            raise bad(f"{key} must be non-empty text")
    raw = data.get("steps")
    if not isinstance(raw, list) or not raw:
        raise bad("steps must be a non-empty list")
    steps = []
    for number, item in enumerate(raw, start=1):
        if not isinstance(item, dict) or not isinstance(item.get("write"), dict):
            raise bad(f"step {number} needs say and write")
        say, write = item.get("say"), item["write"]
        if not isinstance(say, str) or not say.strip():
            raise bad(f"step {number} needs a narration line in say")
        fields, body = write.get("fields", {}), write.get("body")
        if not isinstance(fields, dict) or not (body is None or isinstance(body, str)):
            raise bad(f"step {number}: fields must be a mapping and body must be text")
        if not fields and body is None:
            raise bad(f"step {number}: write needs fields or a body")
        page, actor = write.get("page"), write.get("actor")
        if not isinstance(page, str) or not isinstance(actor, str):
            raise bad(f"step {number}: write needs page and actor")
        check_name(page)
        check_name(actor)
        steps.append(Step(say.strip(), page, actor, fields, body))
    check_name(data["look_at"])
    return Example(name, data["title"].strip(), data["summary"].strip(), data["look_at"], steps)


def listing(ui: Plain) -> list[str]:
    """Return the available examples with their summaries, as lines."""
    return ui.listing([(name, load(name).summary) for name in available()])


def _outcome(vault: Vault, step: Step, before: int, clock: Callable[[], str]) -> Outcome:
    result = vault.write(step.page, step.fields, step.body, actor=step.actor, at=clock())
    reactions = []
    for line in vault.log()[before:][1:]:
        _, _, _, kind, page, *_ = line.split()
        reactions.append(
            (page, "changed by itself" if kind == "write" else "refused its own change")
        )
    return Outcome(result.ok, step.page, result.reason or "", tuple(reactions))


def run(
    example: Example,
    vault: Vault,
    clock: Callable[[], str],
    ui: Plain,
    out: Callable[[str], None],
) -> None:
    """Run every step against the vault and report each one through ui and out."""
    for line in ui.demo_title(example.title, example.summary):
        out(line)
    for number, step in enumerate(example.steps, start=1):
        outcome = _outcome(vault, step, len(vault.log()), clock)
        for line in ui.demo_step(number, step.say, outcome):
            out(line)


def build(
    name: str,
    into: Path,
    keys: Path | None,
    clock: Callable[[], str],
    ui: Plain,
    out: Callable[[str], None],
) -> None:
    """Create the vault for example name at into, run it and print what to look at next."""
    example = load(name)
    if into.exists():
        raise BadInput(f"{into} already exists: choose another folder with --into PATH")
    keys_dir = keys if keys is not None else into.resolve().parent / "keys"
    vault = Vault.init(into, keys_dir)
    run(example, vault, clock, ui, out)
    for line in ui.demo_next(into, example.look_at):
        out(line)
