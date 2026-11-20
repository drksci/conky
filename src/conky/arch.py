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

LANES = (
    "lane.person",
    "lane.connector",
    "lane.page",
    "lane.space",
    "lane.runtime",
    "lane.history",
    "lane.provider",
    "lane.outside",
)
LANE_MEANING = {
    "lane.person": "A person at the command line, or any caller outside the vault.",
    "lane.connector": "A process beside the vault, such as `conky connect terminal`.",
    "lane.page": "A page: the one written, or one that watches.",
    "lane.space": "A space page above a page, handing down its rules.",
    "lane.runtime": "The fixed conky code that judges, reacts and records.",
    "lane.history": "The Git history of the vault.",
    "lane.provider": "A model, reached by an HTTP call or a local program.",
    "lane.outside": "Everything else: a program, the network, the environment, a Git host.",
}


@dataclass(frozen=True)
class Layer:
    """One layer, from the store upwards."""

    id: str
    name: str
    holds: str


LAYERS = (
    Layer(
        "layer.git",
        "Git",
        "The repository, signed commits, clone, bundle, `ssh-keygen`, `git fsck`.",
    ),
    Layer(
        "layer.history", "Pages and history", "The page format, the write path, trailers, refusals."
    ),
    Layer("layer.reflex", "Reflexes", "CEL rules, reactions, the depth bound, measures, pressure."),
    Layer("layer.space", "Spaces", "`within`, rules handed down, leaving judged."),
    Layer(
        "layer.character",
        "Characters",
        "Pages that ask a model, providers, answers that are pages.",
    ),
    Layer(
        "layer.edge", "The edge", "The command line, presenters, connectors, `demo`, `assimilate`."
    ),
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
        "flow.write.accept",
        "An accepted write",
        "A write that holds becomes one signed commit, and then the pages that watch it react.",
        "vault-format.md#a-write",
    ),
    Flow(
        "flow.write.refuse",
        "A refused write",
        "A refusal is an empty signed commit with the reason and the attempt, and it triggers "
        "no reactions.",
        "vault-format.md#a-refusal",
    ),
    Flow(
        "flow.watch.react",
        "A reaction cascade with the depth bound",
        "After a commit pages react in name order, depth first, and nesting past 12 is a "
        "recorded refusal.",
        "rules-and-reactions.md#reactions",
    ),
    Flow(
        "flow.watch.measure",
        "A measure and pressure",
        "A page watching itself writes its own number as an event, and a threshold sets a "
        "state others watch.",
        "rules-and-reactions.md#measures",
        "R2",
    ),
    Flow(
        "flow.ask.model",
        "Asking a model",
        "A named provider is tried first, then detected models in order, then a plain "
        "sentence that a later model replaces.",
        "rules-and-reactions.md#asking-a-model",
        "R26",
    ),
    Flow(
        "flow.ask.pages",
        "An answer that is pages",
        "The answer is written first, then each page lands as a write by the asker inside "
        "the named space.",
        "rules-and-reactions.md#an-answer-that-is-pages",
        "R29",
    ),
    Flow(
        "flow.connect.sense",
        "Perception in through the terminal connector",
        "The connector turns what a program shows into a signed write to the screen page.",
        "connectors.md#the-screen-page",
    ),
    Flow(
        "flow.connect.act",
        "Action out through the hands page",
        "A write to the hands page is typed into the program only when its turn matches the "
        "current screen.",
        "connectors.md#the-hands-page",
    ),
    Flow(
        "flow.space.move",
        "Joining and leaving a space",
        "A write to `within` is judged by the rules of the spaces after it and before it.",
        "rules-and-reactions.md#rules-and-spaces",
        "R29",
    ),
    Flow(
        "flow.vault.verify",
        "Verify",
        "Verify stops at the first problem and checks seals and shape, not rules.",
        "vault-format.md#what-verify-checks",
    ),
    Flow(
        "flow.vault.rebuild",
        "Rebuild",
        "A hand edit blocks the next write and fails verify, and rebuild restores the pages "
        "from the history.",
        "vault-format.md#rebuild",
    ),
    Flow(
        "flow.vault.clone",
        "Clone and leave",
        "A vault travels by plain Git, verifies without the author's key, and keeps no secret.",
        "vault-format.md#reading-with-plain-git",
    ),
    Flow(
        "flow.vault.assimilate",
        "Assimilate, a stranger resumes a stopped vault",
        "A stranger checks a stopped vault, reads it and carries on as a new actor, with no model.",
        "cli.md#assimilate",
        "R21",
    ),
    Flow(
        "flow.page.read",
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


def change(name: str, what: str, *, doc: str, roadmap: str | None = None):
    """Mark who changes what, under `place.page`, `place.runtime` or `place.beside`."""
    return _mark("change", name=name, text=what, doc=doc, roadmap=roadmap)


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
    name="law.output.out",
    statement="Runtime output never enters the repository, except the golden vault.",
    doc="../../CLAUDE.md",
)
declare(
    "law",
    "docs/decisions/0018-not-doing.md",
    name="law.scope.out",
    statement="No batching to hide, no second authority, no hidden state, no control by "
    "instruction.",
    doc="../decisions/0018-not-doing.md",
)
declare(
    "law",
    "scripts/check_docs.py",
    name="law.docs.check",
    statement="Ideas climb rungs, and the documents, links and this index are checked.",
    doc="../decisions/0015-ideas-climb-rungs.md",
)
declare(
    "law",
    "tests/test_house.py",
    name="law.debt.none",
    statement="No fix-later notes, shims or dead code.",
    doc="../decisions/0010-no-debt-no-down-migrations.md",
)


# The steps performed by `conky.vault`, one row each: flow, order, from lane, to lane (None for a
# note), text, the function that performs it, and whether the step is inside a refusal branch.
VAULT_STEPS: tuple[tuple[Any, ...], ...] = (
    (
        "flow.write.accept",
        1,
        "lane.person",
        "lane.runtime",
        "write page, fields and body, as an actor",
        "conky.vault.Vault.write",
    ),
    (
        "flow.write.accept",
        2,
        "lane.runtime",
        "lane.history",
        "is the working tree clean",
        "conky.vault.Vault.write",
    ),
    (
        "flow.write.accept",
        3,
        "lane.runtime",
        "lane.page",
        "load the page as it is and apply the changes",
        "conky.vault.Vault._write",
    ),
    (
        "flow.write.accept",
        4,
        "lane.runtime",
        "lane.page",
        "judge its own rules, with size in scope",
        "conky.vault.Vault._rule_reason",
    ),
    (
        "flow.write.accept",
        5,
        "lane.runtime",
        "lane.space",
        "judge the rules of each space up the chain",
        "conky.vault.Vault._walk",
    ),
    (
        "flow.write.accept",
        7,
        "lane.runtime",
        "lane.history",
        "one signed commit with Kind, Page and Cause",
        "conky.vault.Vault._record",
    ),
    (
        "flow.write.accept",
        8,
        "lane.runtime",
        "lane.page",
        "run every watcher, see the reaction cascade",
        "conky.vault.Vault._react",
    ),
    (
        "flow.ask.pages",
        1,
        "lane.page",
        "lane.runtime",
        "an ask entry with writes names a space",
        "conky.vault.Vault._react",
    ),
    (
        "flow.ask.pages",
        4,
        "lane.runtime",
        "lane.history",
        "the answer is written first, by the asking page, and a refused answer applies no page",
        "conky.vault.Vault._answered",
    ),
    (
        "flow.ask.pages",
        5,
        "lane.runtime",
        "lane.history",
        "a header with no name or a malformed page: one shape refusal, the rest still apply",
        "conky.vault.Vault._land",
        True,
    ),
    (
        "flow.ask.pages",
        6,
        "lane.runtime",
        "lane.space",
        "within the named space before and after, no secret or command, no wider watch",
        "conky.vault.Vault._breach",
    ),
    (
        "flow.ask.pages",
        7,
        "lane.runtime",
        "lane.space",
        "the rules of every space involved, including a space it leaves",
        "conky.vault.Vault._rule_reason",
    ),
    (
        "flow.ask.pages",
        8,
        "lane.runtime",
        "lane.history",
        "a limit or a rule is broken: a recorded refusal",
        "conky.vault.Vault._write",
        True,
    ),
    (
        "flow.ask.pages",
        9,
        "lane.runtime",
        "lane.history",
        "a signed write by the asker, caused by the answer",
        "conky.vault.Vault._land",
    ),
    (
        "flow.ask.pages",
        10,
        "lane.runtime",
        "lane.page",
        "reactions, one level deeper each",
        "conky.vault.Vault._react",
    ),
    (
        "flow.ask.model",
        1,
        "lane.page",
        "lane.runtime",
        "an ask entry fires",
        "conky.vault.Vault._react",
    ),
    (
        "flow.ask.model",
        2,
        "lane.person",
        "lane.runtime",
        "or a person runs conky ask",
        "conky.vault.Vault.ask",
    ),
    (
        "flow.ask.model",
        3,
        "lane.runtime",
        "lane.page",
        "resolve embeds in the prompt, and add the page instruction when writes is set",
        "conky.vault.Vault._ask",
    ),
    (
        "flow.ask.model",
        4,
        "lane.runtime",
        None,
        "skip when into_asked marks this prompt and the answer still in place",
        "conky.vault.Vault._ask",
    ),
    (
        "flow.ask.model",
        5,
        "lane.runtime",
        "lane.page",
        "a provider page is named: read it",
        "conky.vault.Vault._ask",
    ),
    (
        "flow.ask.model",
        10,
        "lane.runtime",
        "lane.history",
        "the named provider failed: a model refusal on the asking page",
        "conky.vault.Vault._ask",
        True,
    ),
    (
        "flow.ask.model",
        12,
        "lane.runtime",
        "lane.provider",
        "each detected model in order, a failure goes on to the next",
        "conky.vault.Vault._ask",
    ),
    (
        "flow.ask.model",
        13,
        "lane.runtime",
        "lane.history",
        "a signed write by the asking page, with Model, tokens, Read and the prompt",
        "conky.vault.Vault._answered",
    ),
    (
        "flow.ask.model",
        14,
        "lane.runtime",
        "lane.history",
        "none answered: a plain sentence, Model none, no marker, so a later model replaces it",
        "conky.vault.Vault._plain",
    ),
    (
        "flow.vault.clone",
        3,
        "lane.person",
        "lane.runtime",
        "verify, with Git and ssh-keygen only",
        "conky.vault.Vault.verify",
    ),
    (
        "flow.vault.clone",
        4,
        "lane.runtime",
        "lane.history",
        "every seal against allowed_signers",
        "conky.vault.Vault._check_commit",
    ),
    (
        "flow.vault.clone",
        5,
        "lane.runtime",
        "lane.person",
        "ok, and no private key was needed",
        "conky.vault.Vault.verify",
    ),
    (
        "flow.space.move",
        1,
        "lane.person",
        "lane.runtime",
        "write within: a space name, or nothing",
        "conky.vault.Vault.write",
    ),
    (
        "flow.space.move",
        2,
        "lane.runtime",
        "lane.page",
        "the page as it would be after the write",
        "conky.vault.Vault._write",
    ),
    (
        "flow.space.move",
        3,
        "lane.runtime",
        "lane.space",
        "the rules of the page and of every space it will be in",
        "conky.vault.Vault._rule_reason",
    ),
    (
        "flow.space.move",
        4,
        "lane.runtime",
        "lane.space",
        "if it was in a space: that space's rules, against the page after",
        "conky.vault.Vault._rule_reason",
    ),
    (
        "flow.space.move",
        5,
        "lane.space",
        None,
        "a space that says nothing lets its members go",
        "conky.vault.Vault._walk",
    ),
    (
        "flow.space.move",
        6,
        "lane.runtime",
        "lane.history",
        "every rule holds: a signed write",
        "conky.vault.Vault._record",
    ),
    (
        "flow.space.move",
        7,
        "lane.runtime",
        "lane.history",
        "a rule is false or a space is missing: a refusal naming that space in From",
        "conky.vault.Vault._refuse",
        True,
    ),
    (
        "flow.watch.measure",
        1,
        "lane.person",
        "lane.runtime",
        "a large write to a page with no size rule",
        "conky.vault.Vault.write",
    ),
    (
        "flow.watch.measure",
        2,
        "lane.runtime",
        "lane.history",
        "the write is kept, with no refusal",
        "conky.vault.Vault._record",
    ),
    (
        "flow.watch.measure",
        3,
        "lane.runtime",
        "lane.page",
        "self-watch: on itself, set pressure from size",
        "conky.vault.Vault._react",
    ),
    (
        "flow.watch.measure",
        4,
        "lane.runtime",
        "lane.history",
        "the number is its own signed event",
        "conky.vault.Vault._record",
    ),
    (
        "flow.watch.measure",
        5,
        "lane.runtime",
        "lane.page",
        "second entry: when pressure passes the threshold a state is set",
        "conky.vault.Vault._react",
    ),
    (
        "flow.watch.measure",
        6,
        "lane.runtime",
        "lane.page",
        "pages that watch that state react",
        "conky.vault.Vault._react",
    ),
    (
        "flow.watch.measure",
        7,
        "lane.runtime",
        None,
        "unchanged values are skipped, so the chain settles",
        "conky.vault.Vault._react",
    ),
    (
        "flow.watch.measure",
        8,
        "lane.runtime",
        None,
        "reading history evaluates nothing, and nothing yet relieves pressure",
        "conky.vault.Vault.log",
    ),
    (
        "flow.watch.react",
        1,
        "lane.runtime",
        "lane.page",
        "visit every page in order of name for watch entries on the page just written",
        "conky.vault.Vault._react",
    ),
    (
        "flow.watch.react",
        2,
        "lane.runtime",
        "lane.page",
        "evaluate when, with page, other, size, other_size and event",
        "conky.vault.Vault._react",
    ),
    (
        "flow.watch.react",
        3,
        "lane.runtime",
        "lane.history",
        "when or a set expression fails: a watch refusal on the watching page",
        "conky.vault.Vault._react",
        True,
    ),
    (
        "flow.watch.react",
        4,
        "lane.runtime",
        None,
        "when is false, or the change leaves the page as it is: skipped",
        "conky.vault.Vault._react",
    ),
    (
        "flow.watch.react",
        5,
        "lane.runtime",
        "lane.page",
        "write as the watching page, one level deeper",
        "conky.vault.Vault._write",
    ),
    (
        "flow.watch.react",
        6,
        "lane.runtime",
        "lane.history",
        "a signed commit by the watching page, with Cause",
        "conky.vault.Vault._record",
    ),
    (
        "flow.watch.react",
        7,
        "lane.runtime",
        "lane.page",
        "its own watchers react in turn, depth first",
        "conky.vault.Vault._react",
    ),
    (
        "flow.watch.react",
        8,
        "lane.runtime",
        "lane.history",
        "deeper than 12: a cycle refusal, and nothing deeper runs",
        "conky.vault.Vault._write",
        True,
    ),
    (
        "flow.page.read",
        1,
        "lane.person",
        "lane.runtime",
        "conky read page",
        "conky.vault.Vault.read",
    ),
    (
        "flow.page.read",
        2,
        "lane.runtime",
        "lane.page",
        "load the stored page",
        "conky.vault.Vault.read",
    ),
    (
        "flow.page.read",
        4,
        "lane.runtime",
        "lane.person",
        "the page, and a missing target gives nothing",
        "conky.vault.Vault.read",
    ),
    ("flow.page.read", 5, "lane.person", "lane.runtime", "conky log", "conky.vault.Vault.log"),
    (
        "flow.page.read",
        6,
        "lane.runtime",
        "lane.history",
        "commits oldest first",
        "conky.vault.Vault.log",
    ),
    (
        "flow.page.read",
        7,
        "lane.runtime",
        "lane.person",
        "one line each, with cause, model, read and from",
        "conky.vault.Vault.log",
    ),
    (
        "flow.page.read",
        8,
        "lane.runtime",
        None,
        "no model is called and no event is made",
        "conky.vault.Vault.log",
    ),
    (
        "flow.vault.rebuild",
        1,
        "lane.person",
        "lane.page",
        "a page is edited by hand, so the tree is dirty",
        "conky.vault.Vault._dirty",
    ),
    (
        "flow.vault.rebuild",
        2,
        "lane.runtime",
        "lane.person",
        "verify or the next write: an error naming the fix",
        "conky.vault.Vault._dirty_message",
    ),
    (
        "flow.vault.rebuild",
        3,
        "lane.person",
        "lane.runtime",
        "conky rebuild",
        "conky.vault.Vault.rebuild",
    ),
    (
        "flow.vault.rebuild",
        4,
        "lane.runtime",
        "lane.history",
        "reset hard to main",
        "conky.vault.Vault.rebuild",
    ),
    (
        "flow.vault.rebuild",
        5,
        "lane.runtime",
        "lane.page",
        "remove untracked files under pages and keys",
        "conky.vault.Vault.rebuild",
    ),
    (
        "flow.write.refuse",
        1,
        "lane.person",
        "lane.runtime",
        "a write that breaks a rule",
        "conky.vault.Vault.write",
    ),
    (
        "flow.write.refuse",
        2,
        "lane.runtime",
        "lane.page",
        "apply the changes, a malformed key is a shape refusal",
        "conky.vault.Vault._write",
    ),
    (
        "flow.write.refuse",
        3,
        "lane.runtime",
        "lane.page",
        "judge its own rules",
        "conky.vault.Vault._rule_reason",
    ),
    (
        "flow.write.refuse",
        4,
        "lane.runtime",
        "lane.space",
        "judge each space up the chain: a rule is false, fails or loops",
        "conky.vault.Vault._walk",
    ),
    (
        "flow.write.refuse",
        5,
        "lane.runtime",
        None,
        "reason, attempt, body size, and From when a space refused",
        "conky.vault.Vault._refuse",
    ),
    (
        "flow.write.refuse",
        6,
        "lane.runtime",
        "lane.history",
        "an empty signed commit, Kind refused, no page changed",
        "conky.vault.Vault._record",
    ),
    (
        "flow.write.refuse",
        7,
        "lane.runtime",
        "lane.page",
        "no reactions run, because nothing changed",
        "conky.vault.Vault._write",
    ),
    (
        "flow.vault.verify",
        1,
        "lane.person",
        "lane.runtime",
        "conky verify",
        "conky.vault.Vault.verify",
    ),
    (
        "flow.vault.verify",
        2,
        "lane.runtime",
        "lane.history",
        "is the working tree clean",
        "conky.vault.Vault.verify",
    ),
    (
        "flow.vault.verify",
        3,
        "lane.runtime",
        "lane.outside",
        "git fsck strict",
        "conky.vault.Vault.verify",
    ),
    (
        "flow.vault.verify",
        4,
        "lane.runtime",
        "lane.history",
        "each commit, oldest first: a good signature from a listed key",
        "conky.vault.Vault._check_commit",
    ),
    (
        "flow.vault.verify",
        5,
        "lane.runtime",
        "lane.history",
        "Kind is write or refused",
        "conky.vault.Vault._check_commit",
    ),
    (
        "flow.vault.verify",
        6,
        "lane.runtime",
        "lane.history",
        "a write touches only pages and allowed_signers, a refusal only allowed_signers",
        "conky.vault.Vault._check_commit",
    ),
    (
        "flow.vault.verify",
        7,
        "lane.runtime",
        "lane.person",
        "the first problem is an error, exit 1",
        "conky.vault.Vault._check_commit",
        True,
    ),
    (
        "flow.vault.verify",
        9,
        "lane.runtime",
        None,
        "rules are not evaluated and page content is not read",
        "conky.vault.Vault.verify",
    ),
)

for _row in VAULT_STEPS:
    _flow, _order, _frm, _to, _text, _func, *_refusal = _row
    declare(
        "step",
        _func,
        flow=_flow,
        order=_order,
        frm=_frm,
        to=_to,
        text=_text,
        refusal=bool(_refusal and _refusal[0]),
    )
