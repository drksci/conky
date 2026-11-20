"""Take over a stopped vault from its folder alone, check it and carry on from where it stopped.

This is the mechanical form of the assimilation test. No model is involved, so it shows that the
state travels and resumes and says nothing about behaviour.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, replace
from importlib import resources
from pathlib import Path

from conky import demo, git
from conky.errors import BadInput, VerifyFailed
from conky.page import Page, check_name, load_value, parse
from conky.present import Plain
from conky.vault import Vault

TITLE = "Assimilating a stopped vault"
SUMMARY = (
    "A stopped vault is taken over from its folder alone: check it, read it and carry on from "
    "where it stopped. No model is involved."
)
INTO = "conky-assimilated"
PACKAGED = "the stopped market stall that ships with conky"


@dataclass(frozen=True)
class Carry:
    """One write to make as the newcomer; expects names the pages that must react, if it is set.

    A write from the built-in vault sets expects and must be kept. A write from the user leaves it
    unset, and a refusal of it is reported without failing the run.
    """

    step: demo.Step
    expects: tuple[str, ...] | None = None


def packaged_carry(actor: str) -> list[Carry]:
    """Return the carry-on writes that ship beside the built-in vault, as the actor."""
    text = (resources.files("conky") / "stopped" / "stall.yaml").read_text(encoding="utf-8")
    carried = []
    for item in load_value(text)["steps"]:
        write = item["write"]
        step = demo.Step(item["say"], write["page"], actor, write.get("fields", {}), None)
        carried.append(Carry(step, tuple(item.get("reacts", []))))
    return carried


def _take(source: str | None, into: Path) -> None:
    """Clone the source, or the built-in vault, into the new folder. Nothing else is copied."""
    into.parent.mkdir(parents=True, exist_ok=True)
    try:
        if source is None:
            with resources.as_file(resources.files("conky") / "stopped" / "stall.bundle") as path:
                git.run(["clone", "-q", "--", str(path), str(into.resolve())], into.parent)
        else:
            found = Path(source)
            where = str(found.resolve()) if found.exists() else source
            git.run(["clone", "-q", "--", where, str(into.resolve())], into.parent)
    except BadInput as exc:
        raise BadInput(
            f"cannot take {source}: {exc}: give a vault directory, a bundle file "
            "or a URL that `git clone` accepts"
        ) from exc


def _pages(vault: Vault) -> dict[str, Page]:
    paths = sorted(vault.pages_dir.glob("*.md"))
    return {p.stem: parse(p.read_text(encoding="utf-8")) for p in paths}


def _plural(count: int, word: str) -> str:
    return f"{count} {word}" if count == 1 else f"{count} {word}s"


def _facts(vault: Vault) -> str:
    log, pages = vault.log(), _pages(vault)
    spaces = {page.within for page in pages.values() if page.within}
    counts = f"{_plural(len(log), 'commit')}, {_plural(len(pages), 'page')}"
    counts += f", {_plural(len(spaces), 'space')}"
    if not log:
        return counts
    short, at, actor, kind, page, *_ = log[-1].split()
    return f"{counts}. Last change: {short}, {at}, by {actor}, {kind} {page}."


def _room(vault: Vault) -> list[str]:
    """Describe each page from its file: its space, the rules that apply, and what it watches."""
    pages = _pages(vault)
    lines = []
    for name, page in pages.items():
        inherited, seen, space = 0, {name}, page.within
        while space and space in pages and space not in seen:
            seen.add(space)
            inherited += len(pages[space].rules)
            space = pages[space].within
        rules = _plural(len(page.rules) + inherited, "rule")
        watched = sorted({entry["on"] for entry in page.watch})
        where = f"in {page.within}" if page.within else "not in a space"
        watches = f"watches {', '.join(watched)}" if watched else "watches nothing"
        lines.append(
            f"{name}: {where}; {rules} ({len(page.rules)} own, {inherited} inherited); {watches}"
        )
    return lines or ["no pages"]


def _problem(vault: Vault) -> str | None:
    try:
        vault.verify()
    except VerifyFailed as exc:
        return str(exc)
    return None


def _prepare(vault: Vault, actor: str, keys: Path) -> None:
    """Refuse an actor that is already in the vault or already has a key, so the key is new."""
    if (keys / actor).exists():
        raise BadInput(
            f"a key named {actor!r} already exists in {keys}: "
            "choose another name with --as ACTOR or another folder with --keys DIR"
        )
    if vault.signers.exists() and f"{actor}@conky " in vault.signers.read_text(encoding="utf-8"):
        raise BadInput(
            f"{actor!r} is already listed in the vault's {git.SIGNERS}: "
            "choose a new name with --as ACTOR"
        )


def _carry_on(
    vault: Vault,
    carry: list[Carry],
    actor: str,
    clock: Callable[[], str],
    ui: Plain,
    say: Callable[[list[str]], None],
) -> bool:
    """Make each write as the newcomer and report it; return False if a required one failed."""
    for item in carry:
        say(ui.note(4, "info", "", item.step.say))
        outcome = demo.play(vault, replace(item.step, actor=actor), len(vault.log()), clock)
        say(ui.result(4, outcome))
        if item.expects is None:
            continue
        reacted = tuple(page for page, _ in outcome.reactions)
        if not outcome.ok:
            say(ui.note(4, "fail", "failed", "this write was expected to be kept"))
        elif reacted != item.expects:
            wanted = ", ".join(item.expects) or "nothing"
            say(ui.note(4, "fail", "failed", f"expected a reaction from {wanted}"))
        else:
            continue
        return False
    return True


def run(
    source: str | None,
    into: Path,
    actor: str,
    keys: Path | None,
    extra: list[Carry],
    clock: Callable[[], str],
    ui: Plain,
    out: Callable[[str], None],
) -> int:
    """Take over the source, check it, read it, carry on and check again; return the exit code."""
    check_name(actor)
    if into.exists():
        raise BadInput(f"{into} already exists: choose another folder with --into PATH")
    keys = (keys if keys is not None else into.parent / "keys").resolve()
    carry = [*(packaged_carry(actor) if source is None else []), *extra]

    def say(lines: list[str]) -> None:
        for line in lines:
            out(line)

    say(ui.demo_title(TITLE, SUMMARY))
    taking = f"Take the folder: clone {source or PACKAGED} into {into}."
    say(ui.step(1, f"{taking} Nothing else is copied: no keys and no settings."))
    _take(source, into)
    vault = Vault(into, keys)
    say(ui.note(1, "ok", "taken", f"the vault is in {into}"))

    say(ui.step(2, "Check it: signed commits, valid trailers and a clean tree."))
    problem = _problem(vault)
    if problem:
        say(ui.note(2, "fail", "failed", problem))
        return 1
    say(ui.note(2, "ok", "verified", "every commit is signed by a key the vault lists"))
    say(ui.note(2, "info", "", _facts(vault)))

    say(ui.step(3, "Read the room: space, rules and watches of each page, from the files only."))
    for line in _room(vault):
        say(ui.note(3, "info", "", line))

    if not carry:
        paragraphs = [
            "The folder alone was enough to check the history. Nothing was changed.",
            f"To carry on, write as a new actor: conky --vault {into} --keys {keys} "
            "write PAGE FIELD=VALUE --as ACTOR.",
        ]
    else:
        newcomer = f"Carry on as a newcomer: {actor} is a new actor with a new key in {keys}."
        say(ui.step(4, f"{newcomer} The original author's key is not needed."))
        _prepare(vault, actor, keys)
        start = len(vault.log())
        kept = _carry_on(vault, carry, actor, clock, ui, say)
        say(ui.step(5, "Check again: verify once more and list what the carry-on added."))
        problem = _problem(vault)
        if problem:
            say(ui.note(5, "fail", "failed", problem))
            return 1
        say(ui.note(5, "ok", "verified", "the history is still intact"))
        say(ui.note(5, "info", "", _facts(vault)))
        say([" " * 8 + line for line in ui.log(vault.log()[start:])])
        if not kept:
            return 1
        paragraphs = [
            "Shown: the folder alone was enough to check the history and to continue it. "
            "The newcomer's key was created here and listed in its first commit."
        ]
    paragraphs.append(
        "Not shown: no model was involved, so this says nothing about how an agent behaves. "
        "It shows that the state travels and resumes."
    )
    say(ui.closing("What this shows", paragraphs))
    return 0
