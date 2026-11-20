"""Markers that describe the architecture where it is defined.

Each marker returns what it is given and does nothing at run time. It only records a fact in
`ENTRIES`, so `scripts/gen_architecture.py` can write `docs/reference/architecture.md` from the
code and nobody edits that page by hand. A planned or idea fact is written in the frontmatter of
the document that holds it, under the key `arch`, and the generator merges the two.

The markers: `law`, `part`, `archetype`, `step`, `slot`, `stage`, `change` and `data` describe
what is built. `holds` links a test to the law or flow it holds, as a measured check. `judged`
declares an open-ended check and `bundle` writes its evidence. `constant` registers a constant
that already is the list, so its members are not repeated. `declare` registers a fact with no
object to mark, such as a rule held by a file. The layers, the lanes and the flows are declared
here once.
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, TypeVar

T = TypeVar("T")

LANES = ("Person", "Connector", "Page", "Space", "Runtime", "History", "Provider", "Outside")
LANE_MEANING = {
    "Person": "A person at the command line, or any caller outside the vault.",
    "Connector": "A process beside the vault, such as `conky connect terminal`.",
    "Page": "A page: the one written, or one that watches.",
    "Space": "A space page above a page, handing down its rules.",
    "Runtime": "The fixed conky code that judges, reacts and records.",
    "History": "The Git history of the vault.",
    "Provider": "A model, reached by an HTTP call or a local program.",
    "Outside": "Everything else: a program, the network, the environment, a Git host.",
}


@dataclass(frozen=True)
class Layer:
    """One layer, from the store upwards."""

    id: str
    name: str
    holds: str


LAYERS = (
    Layer("git", "Git", "The repository, signed commits, clone, bundle, `ssh-keygen`, `git fsck`."),
    Layer("history", "Pages and history", "The page format, the write path, trailers, refusals."),
    Layer("reflexes", "Reflexes", "CEL rules, reactions, the depth bound, measures, pressure."),
    Layer("spaces", "Spaces", "`within`, rules handed down, leaving judged."),
    Layer("characters", "Characters", "Pages that ask a model, providers, answers that are pages."),
    Layer("edge", "The edge", "The command line, presenters, connectors, `demo`, `assimilate`."),
)


@dataclass(frozen=True)
class Flow:
    """A built flow: its name, title, one-line statement and the document that defines it."""

    name: str
    title: str
    statement: str
    doc: str
    roadmap: str | None = None


FLOWS = (
    Flow(
        "accepted-write",
        "An accepted write",
        "A write that holds becomes one signed commit, and then the pages that watch it react.",
        "vault-format.md#a-write",
    ),
    Flow(
        "refused-write",
        "A refused write",
        "A refusal is an empty signed commit with the reason and the attempt, and it triggers "
        "no reactions.",
        "vault-format.md#a-refusal",
    ),
    Flow(
        "reaction-cascade",
        "A reaction cascade with the depth bound",
        "After a commit pages react in name order, depth first, and nesting past 12 is a "
        "recorded refusal.",
        "rules-and-reactions.md#reactions",
    ),
    Flow(
        "measure-and-pressure",
        "A measure and pressure",
        "A page watching itself writes its own number as an event, and a threshold sets a "
        "state others watch.",
        "rules-and-reactions.md#measures",
        "R2",
    ),
    Flow(
        "asking-a-model",
        "Asking a model",
        "A named provider is tried first, then detected models in order, then a plain "
        "sentence that a later model replaces.",
        "rules-and-reactions.md#asking-a-model",
        "R26",
    ),
    Flow(
        "answer-is-pages",
        "An answer that is pages",
        "The answer is written first, then each page lands as a write by the asker inside "
        "the named space.",
        "rules-and-reactions.md#an-answer-that-is-pages",
        "R29",
    ),
    Flow(
        "perception-in",
        "Perception in through the terminal connector",
        "The connector turns what a program shows into a signed write to the screen page.",
        "connectors.md#the-screen-page",
    ),
    Flow(
        "action-out",
        "Action out through the hands page",
        "A write to the hands page is typed into the program only when its turn matches the "
        "current screen.",
        "connectors.md#the-hands-page",
    ),
    Flow(
        "join-and-leave",
        "Joining and leaving a space",
        "A write to `within` is judged by the rules of the spaces after it and before it.",
        "rules-and-reactions.md#rules-and-spaces",
        "R29",
    ),
    Flow(
        "verify",
        "Verify",
        "Verify stops at the first problem and checks seals and shape, not rules.",
        "vault-format.md#what-verify-checks",
    ),
    Flow(
        "rebuild",
        "Rebuild",
        "A hand edit blocks the next write and fails verify, and rebuild restores the pages "
        "from the history.",
        "vault-format.md#rebuild",
    ),
    Flow(
        "clone-and-leave",
        "Clone and leave",
        "A vault travels by plain Git, verifies without the author's key, and keeps no secret.",
        "vault-format.md#reading-with-plain-git",
    ),
    Flow(
        "assimilate",
        "Assimilate, a stranger resumes a stopped vault",
        "A stranger checks a stopped vault, reads it and carries on as a new actor, with no model.",
        "cli.md#assimilate",
        "R21",
    ),
    Flow(
        "read-a-page",
        "Reading a page and the history",
        "Reading resolves embeds and changes nothing, and the log is the history one line at "
        "a time.",
        "vault-format.md#pages",
    ),
)

STAGE_PHASES = ("stimulus", "notice", "attention", "think", "act", "record")
CHANGE_PLACES = ("page", "runtime", "beside")
DATA_KINDS = ("document", "file", "table", "stream", "engine")


@dataclass(frozen=True)
class Entry:
    """One registered fact: its kind, the code it marks and what it says."""

    kind: str
    ref: str
    facts: dict[str, Any] = field(default_factory=dict)


ENTRIES: list[Entry] = []


def _ref(obj: object) -> str:
    return f"{getattr(obj, '__module__', '')}.{getattr(obj, '__qualname__', '')}"


def _mark(what: str, /, **facts: Any):
    def apply(obj: T) -> T:
        ENTRIES.append(Entry(what, _ref(obj), facts))
        return obj

    return apply


def law(name: str, statement: str, *, doc: str, roadmap: str | None = None):
    """Mark the code that enforces a law."""
    return _mark("law", name=name, statement=statement, doc=doc, roadmap=roadmap)


def part(word: str, layer: str, meaning: str, *, doc: str, roadmap: str | None = None):
    """Mark the code of a concept word or a named part, and the layer it lives in."""
    return _mark("part", name=word, layer=layer, text=meaning, doc=doc, roadmap=roadmap)


def archetype(name: str, by: str, text: str, *, doc: str, roadmap: str | None = None):
    """Mark the code that reads or makes a kind of page, and who makes the page."""
    return _mark("archetype", name=name, by=by, text=text, doc=doc, roadmap=roadmap)


def step(flow: str, order: int, frm: str, to: str | None, text: str, *, refusal: bool = False):
    """Mark one step of a flow. With `to` the arrow runs from lane `frm` to lane `to`.

    Without it the step is a note over `frm`. A refusal step is drawn inside a refusal branch.
    """
    return _mark("step", flow=flow, order=order, frm=frm, to=to, text=text, refusal=refusal)


def slot(name: str, kind: str, text: str, *, doc: str):
    """Mark a named place that something plugs into, such as a provider shape or a trailer."""
    return _mark("slot", name=name, slot=kind, text=text, doc=doc)


def stage(phase: str, name: str, text: str, *, doc: str, roadmap: str | None = None):
    """Mark the code of one stage of the chain from stimulus to action."""
    return _mark("stage", phase=phase, name=name, text=text, doc=doc, roadmap=roadmap)


def change(where: str, what: str, *, doc: str, roadmap: str | None = None):
    """Mark who changes what: in a `page`, by the `runtime`, or `beside` the vault."""
    return _mark("change", where=where, name=what, doc=doc, roadmap=roadmap)


def data(kind: str, text: str, *, doc: str, roadmap: str | None = None):
    """Mark the code of a kind of data: document, file, table, stream or engine."""
    return _mark("data", name=kind, text=text, doc=doc, roadmap=roadmap)


def holds(*names: str, kind: str = "measured"):
    """Mark a test with the laws and flows it holds.

    A measured check is a deterministic assertion with an exact expected result. Every pytest
    test is one, so that is the default. An open-ended check is declared with `judged`.
    """
    return _mark("holds", names=names, kind=kind)


def judged(name: str, question: str, evidence: str, scale: str, *, checks: tuple[str, ...] = ()):
    """Declare a judged check: open-ended behaviour that no assertion can settle.

    The declaration names the question a reader must answer from the end state, the evidence to
    look at and the scale of the answer, and the laws or flows it checks. It is not a pass or
    fail. `bundle` writes the evidence and the question, and records a verdict only when one is
    given.
    """
    return _mark(
        "judged", name=name, question=question, evidence=evidence, scale=scale, checks=checks
    )


def bundle(
    name: str,
    source: str | Path,
    out: str | Path,
    *,
    verdict: str | None = None,
    by: str | None = None,
) -> Path:
    """Write the evidence bundle of a judged check for a vault or run directory.

    The bundle holds the question, the evidence to look at, the scale, the history and the pages
    when `source` is a vault, and the verdict and who gave it when both are supplied. It never
    invents a verdict.
    """
    found = [e.facts for e in ENTRIES if e.kind == "judged" and e.facts["name"] == name]
    if not found:
        raise KeyError(f"no judged check named {name!r}: declare it with arch.judged")
    if (verdict is None) != (by is None):
        raise ValueError("give a verdict and who gave it together, or neither")
    facts, source = found[0], Path(source)
    lines = [
        f"# {name}",
        "",
        f"Question: {facts['question']}",
        "",
        f"Evidence to look at: {facts['evidence']}",
        "",
        f"Scale: {facts['scale']}",
        "",
    ]
    if (source / ".git").exists():
        log = subprocess.run(
            ["git", "-C", str(source), "log", "--reverse", "--format=%h %an %s"],
            capture_output=True,
            text=True,
            check=False,
        )
        lines += ["## History", "", log.stdout.rstrip() or "no commits", ""]
        for page in sorted((source / "pages").glob("*.md")):
            lines += [f"## Page {page.stem}", "", page.read_text(encoding="utf-8").rstrip(), ""]
    elif source.is_dir():
        lines += ["## Files", ""] + [f"- {p.name}" for p in sorted(source.iterdir())] + [""]
    lines += ["## Verdict", "", f"{verdict} (given by {by})" if verdict else "not given", ""]
    target = Path(out) / f"judged-{name}.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("\n".join(lines), encoding="utf-8")
    return target


def constant(value: T, kind: str, ref: str, name: str, text: str, *, doc: str) -> T:
    """Register a constant that already is the list, so the page shows its members."""
    ENTRIES.append(Entry("slot", ref, {"name": name, "slot": kind, "text": text, "doc": doc}))
    return value


def declare(kind: str, ref: str, **facts: Any) -> None:
    """Register a fact held by something that has no code object, such as a file."""
    ENTRIES.append(Entry(kind, ref, facts))


declare(
    "law",
    ".gitignore",
    name="output-stays-out",
    statement="Runtime output never enters the repository, except the golden vault.",
    doc="../../CLAUDE.md",
)
declare(
    "law",
    "docs/decisions/0018-not-doing.md",
    name="not-doing",
    statement="No batching to hide, no second authority, no hidden state, no control by "
    "instruction.",
    doc="../decisions/0018-not-doing.md",
)
declare(
    "law",
    "scripts/check_docs.py",
    name="docs-are-checked",
    statement="Ideas climb rungs, and the documents, links and this index are checked.",
    doc="../decisions/0015-ideas-climb-rungs.md",
)
declare(
    "law",
    "tests/test_house.py",
    name="no-debt",
    statement="No fix-later notes, shims or dead code.",
    doc="../decisions/0010-no-debt-no-down-migrations.md",
)
