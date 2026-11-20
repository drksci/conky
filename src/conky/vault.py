"""The vault: a Git repository whose commits are the events and whose files are the pages."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path
from typing import Any

from conky import answer, arch, git, model
from conky.cache import Cache
from conky.errors import BadInput, VerifyFailed
from conky.page import (
    EMBED,
    MEMBERS,
    NAME,
    RELATIONS,
    Page,
    ShapeError,
    apply,
    check_name,
    embedded,
    given,
    links,
    parse,
    resolve,
    resolve_text,
    serialize,
)
from conky.rules import RuleError, evaluate, holds, missing

MAX_DEPTH = 12
KINDS = arch.constant(
    ("write", "refused"),
    "event kind",
    "conky.vault.KINDS",
    "slot.event",
    "What an event is: a write or a refusal.",
    doc="vault-format.md#commits",
)
CACHE_HIT = "hit"


@arch.slot(
    "slot.trailer", "trailer", "A key of a commit's trailer block.", doc="vault-format.md#commits"
)
class Trailer(StrEnum):
    """The keys of a commit's trailer block."""

    KIND = "Kind"
    PAGE = "Page"
    CAUSE = "Cause"
    REASON = "Reason"
    ATTEMPT = "Attempt"
    BODY_BYTES = "Body-Bytes"
    FROM = "From"
    MODEL = "Model"
    MODEL_NAME = "Model-Name"
    TOKENS_IN = "Tokens-In"
    TOKENS_OUT = "Tokens-Out"
    READ = "Read"
    CACHE = "Cache"


@arch.slot(
    "slot.refusal",
    "refusal",
    "The word a refusal's reason starts with.",
    doc="rules-and-reactions.md#refusals",
)
class Refusal(StrEnum):
    """The word a refusal's reason starts with, saying which law refused."""

    CYCLE = "cycle"
    SHAPE = "shape"
    RULE = "rule"
    WATCH = "watch"
    MODEL = "model"
    LIMIT = "limit"


RETRY = "Your last answer was refused: {reason} Answer again so that it holds."
_CYCLE = f"{Refusal.CYCLE}: reactions nested deeper than {MAX_DEPTH}"


def _mark(prompt: str, answer: str | None) -> str:
    """Return the digest that settles a question: its resolved prompt and the answer it got."""
    return hashlib.sha256(f"{prompt}\0{answer or ''}".encode()).hexdigest()


def _ruled(result: Result) -> Result | None:
    """Return the first write of an answer that a rule refused, or None."""
    for found in (result, *(each for _, each in result.pages)):
        if not found.ok and (found.reason or "").startswith(f"{Refusal.RULE}:"):
            return found
    return None


def _joined(kept: list[Any], added: list[Any]) -> list[Any]:
    """Return the rules kept, then each added entry that is not already among them."""
    rules = list(kept)
    for entry in added:
        if entry not in rules:
            rules.append(entry)
    return rules


def _size(page: Page) -> int:
    """Return the byte length of the page as serialised."""
    return len(serialize(page).encode("utf-8"))


def _compact(value: Any) -> str:
    """Return value as compact JSON on one line."""
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


@dataclass(frozen=True)
class Result:
    """The outcome of a write: whether it held, the commit id, and why not."""

    ok: bool
    id: str
    reason: str | None = None
    plain: bool = False
    pages: tuple[tuple[str, Result], ...] = ()


@dataclass(frozen=True)
class Ask:
    """One question to a model, as a watch entry or the command line puts it."""

    prompt: str
    into: str | None = None
    writes: str | None = None
    provider: str | None = None
    otherwise: str | None = None

    @property
    def marker(self) -> str:
        """The field that records which prompt got an answer."""
        return f"{self.into or 'writes'}_asked"


@arch.part(
    "part.vault",
    "layer.history",
    "A Git repository whose commits are the history.",
    doc="vault-format.md#layout",
)
class Vault:
    """A Git repository of pages, with public keys tracked and private keys kept elsewhere."""

    def __init__(
        self, path: str | Path, keys_dir: str | Path | None = None, cache: Cache | None = None
    ) -> None:
        git.require_tools()
        self.path = Path(path)
        if not (self.path / ".git").exists():
            raise BadInput(f"{self.path} is not a vault: create one with `conky init {self.path}`")
        self.pages_dir = self.path / "pages"
        self.signers = self.path / git.SIGNERS
        self.keys_dir = Path(keys_dir) if keys_dir is not None else Path.home() / ".conky" / "keys"
        self.cache = cache if cache is not None else Cache.open()

    @classmethod
    def init(
        cls, path: str | Path, keys_dir: str | Path | None = None, cache: Cache | None = None
    ) -> Vault:
        """Create an empty vault at path and return it."""
        git.require_tools()
        if (Path(path) / ".git").exists():
            raise BadInput(f"{path} is already a vault")
        git.init(Path(path))
        return cls(path, keys_dir, cache)

    @arch.part(
        "part.read",
        "layer.history",
        "Return a page with its embeds resolved.",
        doc="cli.md#read",
    )
    def read(self, page: str) -> Page:
        """Return the page with its embeds resolved."""
        found = self._load(check_name(page))
        if found is None:
            raise BadInput(f"no page named {page!r}")
        return resolve(found, self._all())

    @arch.law(
        "law.write.only",
        "State changes only through a write committed to the history.",
        doc="../decisions/0002-git-is-the-store.md",
    )
    @arch.part(
        "part.write",
        "layer.history",
        "Commit a change to a page, or commit its refusal.",
        doc="cli.md#write",
    )
    def write(
        self,
        page: str,
        set: dict[str, Any],
        body: str | None = None,
        *,
        actor: str,
        at: str,
        cause: str | None = None,
    ) -> Result:
        """Write fields and body to a page, or record why the write was refused."""
        check_name(page)
        check_name(actor)
        try:
            _compact({"set": set, "body": body})
        except (TypeError, ValueError) as exc:
            raise BadInput(f"values must be plain JSON data: {exc}") from exc
        if self._dirty():
            raise BadInput(self._dirty_message())
        return self._write(page, dict(set), body, actor, at, cause, 0)

    def ask(
        self,
        page: str,
        into: str | None = None,
        *,
        writes: str | None = None,
        provider: str | None = None,
        prompt: str,
        actor: str,
        at: str,
        cause: str | None = None,
    ) -> Result:
        """Ask a model once and write the answer to a field of the page, or record why not.

        With `writes` the answer may also hold pages, which are written by the actor into that
        space and listed in the result. With no provider page the model is detected from the
        environment and the PATH.
        """
        check_name(page)
        check_name(actor)
        if provider is not None:
            check_name(provider)
        if writes is not None:
            check_name(writes)
        if not into and writes is None:
            raise BadInput(
                "give a field to write the answer to, a space to write pages into, or both"
            )
        if self._dirty():
            raise BadInput(self._dirty_message())
        ask = Ask(prompt, into or None, writes, provider)
        return self._ask(page, ask, actor, at, cause, 0, skip_settled=False)

    @arch.data(
        "data.stream",
        "The Git history, the one stream every vault already has, read oldest first.",
        doc="vault-format.md#commits",
    )
    def log(self) -> list[str]:
        """Return the history oldest first, one line per commit."""
        if not self._has_commits():
            return []
        out = git.run(
            ["log", "--reverse", "--format=%x1e%h%x1f%at%x1f%an%x1f%B", "main"], self.path
        )
        lines = []
        for record in out.split("\x1e")[1:]:
            short, stamp, actor, message = record.split("\x1f", 3)
            at = datetime.fromtimestamp(int(stamp), UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
            found = git.trailers(message)
            detail = found.get(Trailer.REASON) or (
                f"cause {found[Trailer.CAUSE][:7]}" if Trailer.CAUSE in found else ""
            )
            if Trailer.MODEL in found:
                detail = f"{detail} model {found[Trailer.MODEL]}".strip()
            if Trailer.READ in found:
                detail = f"{detail} read {found[Trailer.READ]}".strip()
            if Trailer.FROM in found:
                detail = f"{detail} from {found[Trailer.FROM]}".strip()
            fields = [
                short,
                at,
                actor,
                found.get(Trailer.KIND, "-"),
                found.get(Trailer.PAGE, "-"),
                detail,
            ]
            lines.append(" ".join(fields).rstrip())
        return lines

    @arch.law(
        "law.page.commit",
        "Pages are the committed files, and a stray edit is refused or discarded.",
        doc="vault-format.md#what-verify-checks",
    )
    @arch.change(
        "place.runtime.verify",
        "Checking the history, never changing it.",
        doc="vault-format.md#what-verify-checks",
    )
    def verify(self) -> None:
        """Raise VerifyFailed naming the first problem in the tree, the objects or the history."""
        if self._dirty():
            raise VerifyFailed(self._dirty_message())
        try:
            git.run(["fsck", "--strict"], self.path)
        except BadInput as exc:
            raise VerifyFailed(f"{exc}: restore the vault from another clone") from exc
        if not self._has_commits():
            return
        files = self._changed_files()
        out = git.run(["log", "--reverse", "--format=%x1e%H%x1f%G?%x1f%B", "main"], self.path)
        for record in out.split("\x1e")[1:]:
            commit, signature, message = record.split("\x1f", 2)
            self._check_commit(commit[:7], signature, git.trailers(message), files[commit])

    @arch.change(
        "place.runtime.rebuild",
        "Restoring the working tree from the history.",
        doc="vault-format.md#rebuild",
    )
    def rebuild(self) -> None:
        """Restore the working tree to the committed state, discarding stray changes."""
        if self._has_commits():
            git.run(["reset", "-q", "--hard", "main"], self.path)
        git.run(["clean", "-fdq", "--", "pages", "keys"], self.path)

    def _check_commit(
        self, short: str, signature: str, found: dict[str, str], files: list[str]
    ) -> None:
        if signature != "G":
            raise VerifyFailed(
                f"commit {short} has no good signature from a key in {git.SIGNERS} "
                f"(status {signature}): restore the vault from another clone"
            )
        kind = found.get(Trailer.KIND)
        if kind not in KINDS:
            raise VerifyFailed(
                f"commit {short} has no valid Kind trailer: it was not made by conky"
            )
        allowed = [
            f for f in files if f == git.SIGNERS or (kind == "write" and f.startswith("pages/"))
        ]
        if allowed != files:
            stray = next(f for f in files if f not in allowed)
            raise VerifyFailed(f"commit {short} ({kind}) changes {stray}, which a {kind} must not")

    def _changed_files(self) -> dict[str, list[str]]:
        out = git.run(["log", "--name-only", "--format=%x1e%H", "main"], self.path)
        changed = {}
        for record in out.split("\x1e")[1:]:
            commit, *names = record.split("\n")
            changed[commit] = [n for n in names if n]
        return changed

    def _head(self) -> str:
        """Return the id of the latest event, or nothing in a vault with none."""
        return git.run(["rev-parse", "HEAD"], self.path).strip() if self._has_commits() else ""

    def _has_commits(self) -> bool:
        return bool(git.run(["branch", "--list", "main"], self.path).strip())

    def _dirty(self) -> bool:
        return bool(git.run(["status", "--porcelain"], self.path).strip())

    def _dirty_message(self) -> str:
        return (
            "the working tree has changes that were not made through conky: "
            f"run `conky --vault {self.path} rebuild` to discard them"
        )

    def _load(self, name: str) -> Page | None:
        path = self.pages_dir / f"{name}.md"
        return parse(path.read_text(encoding="utf-8")) if path.exists() else None

    def _all(self) -> dict[str, Page]:
        return {p.stem: parse(p.read_text(encoding="utf-8")) for p in self.pages_dir.glob("*.md")}

    @arch.law(
        "law.event.seal",
        "Every change is signed and says what caused it.",
        doc="vault-format.md#a-write",
    )
    @arch.part(
        "part.event",
        "layer.history",
        "A commit: one write or one refusal.",
        doc="vault-format.md#commits",
    )
    @arch.stage(
        "record",
        "stage.record.event",
        "Every stimulus and every action is an event, or a refusal.",
        doc="vault-format.md#commits",
    )
    @arch.change(
        "place.runtime.record",
        "Signing every event and recording every refusal.",
        doc="vault-format.md#commits",
    )
    def _record(
        self,
        kind: str,
        page: str,
        actor: str,
        at: str,
        cause: str | None,
        extra: list[tuple[str, str]],
        content: Page | None,
        note: str = "",
    ) -> str:
        """Make one signed commit; store content as the page file when it is given."""
        key, line = git.register(self.keys_dir, self.signers, actor)
        paths = []
        if line is not None:
            self.signers.parent.mkdir(exist_ok=True)
            with self.signers.open("a", encoding="utf-8") as handle:
                handle.write(line)
            paths.append(git.SIGNERS)
        if content is not None:
            self.pages_dir.mkdir(exist_ok=True)
            (self.pages_dir / f"{page}.md").write_bytes(serialize(content).encode("utf-8"))
            paths.append(f"pages/{page}.md")
        trailers = [(Trailer.KIND, kind), (Trailer.PAGE, page), *extra]
        if cause is not None:
            trailers.append((Trailer.CAUSE, cause))
        return git.commit(
            self.path,
            actor=actor,
            at=at,
            key=key,
            subject=f"{kind} {page}",
            trailers=trailers,
            paths=paths,
            body=note,
        )

    @arch.law(
        "law.refusal.record",
        "A refused write is recorded as an empty commit, never dropped.",
        doc="vault-format.md#a-refusal",
    )
    def _refuse(
        self,
        page: str,
        changes: dict[str, Any],
        body: str | None,
        actor: str,
        at: str,
        cause: str | None,
        reason: str,
        asked: tuple[list[tuple[str, str]], str] = ([], ""),
    ) -> Result:
        extra = [(Trailer.REASON, " ".join(reason.split())), (Trailer.ATTEMPT, _compact(changes))]
        if body is not None:
            extra.append((Trailer.BODY_BYTES, str(len(body.encode("utf-8")))))
        extra += asked[0]
        return Result(
            False, self._record("refused", page, actor, at, cause, extra, None, asked[1]), reason
        )

    @arch.change(
        "place.runtime.judge",
        "Judging rules, shape and limits before a write is kept.",
        doc="rules-and-reactions.md#refusals",
    )
    def _write(
        self,
        page: str,
        changes: dict[str, Any],
        body: str | None,
        actor: str,
        at: str,
        cause: str | None,
        depth: int,
        asked: tuple[list[tuple[str, str]], str] = ([], ""),
        bound: str | None = None,
    ) -> Result:
        def refuse(reason: str) -> Result:
            return self._refuse(page, changes, body, actor, at, cause, reason, asked)

        if depth > MAX_DEPTH:
            return refuse(_CYCLE)
        if page in RELATIONS:
            return refuse(f"{Refusal.SHAPE}: {page} names a watch relation: use another page name")
        before = self._load(page)
        applied = changes
        if bound is not None and page == bound:
            problem = self._bind(page, before, changes, body)
            if problem:
                return refuse(f"{Refusal.LIMIT}: {problem}")
            assert before is not None
            applied = {"rules": _joined(before.rules, changes["rules"])}
        try:
            result = apply(before or Page(), applied, body)
        except ShapeError as exc:
            return refuse(f"{Refusal.SHAPE}: {exc}")
        if bound is not None and page != bound:
            breach = self._breach(page, before, result, bound)
            if breach:
                return refuse(f"{Refusal.LIMIT}: {breach}")
        refused = self._rule_reason(page, result, before) or self._each_reason(page, result, before)
        if refused:
            reason, space = refused
            if space != page:
                asked = ([*asked[0], (Trailer.FROM, space)], asked[1])
            return self._refuse(page, changes, body, actor, at, cause, reason, asked)
        commit = self._record("write", page, actor, at, cause, asked[0], result, asked[1])
        self._react(page, result, commit, at, depth)
        return Result(True, commit)

    def _inside(self, name: str | None, space: str) -> bool:
        """Return whether name is space or lies within it, directly or through spaces."""
        seen: set[str] = set()
        while name is not None and name not in seen:
            if name == space:
                return True
            seen.add(name)
            found = self._load(name)
            name = found.within if found is not None else None
        return False

    def _scope(self, name: str, page: Page) -> dict[str, Any]:
        """Return what a rule reads for a page: its fields, its space, its size and its text."""
        return {
            "page": page.fields,
            "space": self._context(name, page.within),
            "size": _size(page),
            "text": page.body,
        }

    @arch.law(
        "law.rule.proven",
        "An `each` rule is tried on the pages already within when it is written, so it lands only "
        "if it can be evaluated and holds for them.",
        doc="rules-and-reactions.md#rules-and-spaces",
    )
    def _each_reason(self, name: str, page: Page, before: Page | None) -> tuple[str, str] | None:
        """Return the reason an `each` rule just added fails for a page already within it."""
        old = before.rules if before else []
        rules = [r["each"] for r in page.rules if isinstance(r, dict) and r not in old]
        if not rules:
            return None
        for member in sorted(p.stem for p in self.pages_dir.glob("*.md")):
            held = self._load(member)
            if member == name or held is None or not self._inside(held.within, name):
                continue
            scope = self._scope(member, held)
            for rule in rules:
                try:
                    ok = holds(rule, scope)
                    why = "is false"
                except RuleError:
                    ok, why = False, f"failed to evaluate: {missing([rule], scope)}"
                if not ok:
                    return (
                        f"{Refusal.RULE}: {rule} (from {name}) {why} for {member}, within it",
                        name,
                    )
        return None

    @arch.law(
        "law.reach.down",
        "A character writes only inside the space it was given, and creates nothing wider.",
        doc="../decisions/0029-autonomy-inside-limits-that-hold.md",
        roadmap="R29",
    )
    @arch.law(
        "law.runtime.fixed",
        "The runtime is not a page, so no character can change it.",
        doc="../decisions/0029-autonomy-inside-limits-that-hold.md",
    )
    @arch.change(
        "place.runtime.limit",
        "Enforcing the limits of an answer that is pages.",
        doc="rules-and-reactions.md#an-answer-that-is-pages",
        roadmap="R29",
    )
    def _breach(self, name: str, before: Page | None, page: Page, space: str) -> str | None:
        """Return the limit a page written by an answer breaks, if any.

        The page must lie within the space before the write, when it exists, and after it.
        The space page itself is judged by `_bind`.
        """
        if not self._inside(page.within, space):
            return f"page {name} is not within space {space}: set within to it or a space inside it"
        if before is not None and not self._inside(before.within, space):
            return f"page {name} lies outside space {space}, so an answer cannot change it"
        if "secret" in page.fields or "command" in page.fields:
            return (
                f"page {name} names a secret or a command, which a page written by an answer "
                "may not: leave that to the person who sets up the provider"
            )
        for entry in page.watch:
            target = entry.get("ask", {}).get("writes")
            if target is not None and not self._inside(target, space):
                return (
                    f"a watch entry of {name} writes into {target}, outside space {space}: "
                    f"name {space} or a space inside it"
                )
        return None

    def _bind(
        self, name: str, before: Page | None, changes: dict[str, Any], body: str | None
    ) -> str | None:
        """Return why an answer may not write the space it writes into, or None when it may.

        The one thing allowed is `rules` and nothing else: the entries are added to the rules
        the space has, and the write is judged like any other.
        """
        if before is None:
            return f"space {name} does not exist, so an answer cannot make it"
        if set(changes) != {"rules"} or body is not None:
            return (
                f"page {name} is the space this answer writes into: an answer may add rules "
                "to it and nothing else, so send only a rules list and no body"
            )
        if not isinstance(changes["rules"], list):
            return f"rules for {name} must be a list of conditions to add"
        return None

    @arch.law(
        "law.context.down",
        "A space hands its fields down: the nearest space wins, and a rule reads them as `space`.",
        doc="rules-and-reactions.md#context-from-spaces",
        roadmap="R22",
    )
    def _context(self, name: str, within: str | None) -> dict[str, Any]:
        """Return the fields of the spaces above a page, the nearest overriding the rest.

        A missing space or a loop ends the climb; `_walk` is what refuses those.
        """
        chain: list[Page] = []
        seen = {name}
        while within is not None and within not in seen:
            seen.add(within)
            found = self._load(within)
            if found is None:
                break
            chain.append(found)
            within = found.within
        context: dict[str, Any] = {}
        for found in reversed(chain):
            context.update(found.fields)
        return context

    @arch.law(
        "law.rule.tighten",
        "A member adds a rule and cannot remove one or leave one behind.",
        doc="../decisions/0022-leaving-a-space-is-a-write-the-space-can-refuse.md",
        roadmap="R29",
    )
    def _rule_reason(
        self, name: str, page: Page, before: Page | None = None
    ) -> tuple[str, str] | None:
        """Return the reason a rule refuses the page and the page the rule came from.

        The plain rules of the page and the `each` rules of every space above it are judged. A
        write that changes `within` is also judged by the `each` rules of the spaces the page
        was in before it.
        """
        scope = self._scope(name, page)
        found = self._walk(name, page, name, scope)
        if found or before is None or not before.within or before.within == page.within:
            return found
        left = self._load(before.within)
        if left is None:
            return f"{Refusal.RULE}: space {before.within} does not exist", name
        return self._walk(name, left, before.within, scope)

    @arch.part(
        "part.space",
        "layer.space",
        "A page that others lie within, handing down its rules, with leaving judged.",
        doc="rules-and-reactions.md#rules-and-spaces",
        roadmap="R29",
    )
    @arch.archetype(
        "kind.space",
        "a person or a character",
        "A page others name in `within`, with `rules`.",
        doc="rules-and-reactions.md#rules-and-spaces",
        roadmap="R29",
    )
    def _walk(
        self, name: str, space: Page, owner: str, scope: dict[str, Any]
    ) -> tuple[str, str] | None:
        """Judge the rules of space and of the spaces above it against scope.

        A plain rule is judged only when it is the page's own, and an `each` rule only when it
        comes from a space above the page.
        """
        seen = {name}
        while True:
            for entry in space.rules:
                if isinstance(entry, dict):
                    if owner == name:
                        continue
                    rule = entry["each"]
                elif owner == name:
                    rule = entry
                else:
                    continue
                try:
                    held = holds(rule, scope)
                except RuleError:
                    why = missing([rule], scope)
                    return f"{Refusal.RULE}: {rule} (from {owner}) failed to evaluate: {why}", owner
                if not held:
                    return f"{Refusal.RULE}: {rule} (from {owner}) is false", owner
            if not space.within:
                return None
            owner = space.within
            if owner in seen:
                return f"{Refusal.RULE}: within chain loops back to {owner}", name
            seen.add(owner)
            found = self._load(owner)
            if found is None:
                return f"{Refusal.RULE}: space {owner} does not exist", name
            space = found

    def _notices(self, on: str, watcher: str, source: str, written: Page) -> bool:
        """Return whether a watch entry's `on` matches the page just written."""
        if on == "within":
            return source != watcher and self._inside(written.within, watcher)
        if on == "link":
            return source != watcher and watcher in links(written)
        return on == source

    @arch.law(
        "law.pressure.notice",
        "Anything to be noticed is a pressure that triggers a reaction, not a wall.",
        doc="rules-and-reactions.md#measures",
        roadmap="R2",
    )
    @arch.law(
        "law.measure.watch",
        "A measure is a page watching itself, and its value is a recorded event.",
        doc="../decisions/0008-measures-are-self-watches.md",
        roadmap="R2",
    )
    @arch.law(
        "law.reflex.free",
        "Whatever follows from state is a reflex with no model call.",
        doc="../decisions/0007-inference-for-real-thinking.md",
    )
    @arch.part(
        "part.watch",
        "layer.reflex",
        "Name a page whose writes make this page react.",
        doc="rules-and-reactions.md#reactions",
    )
    @arch.archetype(
        "kind.character",
        "a person or a character",
        "Any page with `watch` entries or an `ask`.",
        doc="../decisions/0020-everything-is-somebody.md",
        roadmap="R4",
    )
    @arch.archetype(
        "kind.measure",
        "a person or a character",
        "A diary, a counter or any page with a self-watch.",
        doc="rules-and-reactions.md#measures",
        roadmap="R2",
    )
    @arch.stage(
        "stimulus",
        "stage.stimulus.page",
        "Every write, a reaction included, is the stimulus for the pages that watch it.",
        doc="rules-and-reactions.md#reactions",
    )
    @arch.stage(
        "notice",
        "stage.notice.watch",
        "`on` names the page and `when` must be the boolean true.",
        doc="rules-and-reactions.md#reactions",
    )
    @arch.stage(
        "notice",
        "stage.notice.relation",
        "`on: within` and `on: link` notice a write by its place or its links, not its name.",
        doc="rules-and-reactions.md#reactions",
    )
    @arch.stage(
        "notice",
        "stage.notice.pressure",
        "A second self-watch entry whose `when` reads the number crossing a threshold.",
        doc="rules-and-reactions.md#measures",
        roadmap="R2",
    )
    @arch.stage(
        "notice",
        "stage.notice.unchanged",
        "A reaction that leaves the page unchanged is not written.",
        doc="rules-and-reactions.md#reactions",
    )
    @arch.stage(
        "notice",
        "stage.notice.text",
        "`text` and `other_text` are the bodies of the watching page and of the page just "
        "written, so a watch can read what a page says.",
        doc="rules-and-reactions.md#variables-in-scope",
    )
    @arch.change(
        "place.runtime.react",
        "Running reactions after a write, depth first, bounded at 12.",
        doc="rules-and-reactions.md#reactions",
    )
    def _react(self, source: str, written: Page, commit: str, at: str, depth: int) -> None:
        for watcher in sorted(p.stem for p in self.pages_dir.glob("*.md")):
            for entry in (self._load(watcher) or Page()).watch:
                if not self._notices(entry["on"], watcher, source, written):
                    continue
                current = self._load(watcher) or Page()
                scope = {
                    "other": written.fields,
                    "other_name": source,
                    "page": current.fields,
                    "space": self._context(watcher, current.within),
                    "other_size": _size(written),
                    "size": _size(current),
                    "other_text": written.body,
                    "text": current.body,
                    "event": commit,
                }
                try:
                    if not holds(entry["when"], scope):
                        continue
                    changes = {k: evaluate(v, scope) for k, v in entry.get("set", {}).items()}
                    unchanged = serialize(apply(current, changes, None)) == serialize(current)
                except (RuleError, ShapeError) as exc:
                    why = (
                        str(exc)
                        if isinstance(exc, ShapeError)
                        else missing([entry["when"], *entry.get("set", {}).values()], scope)
                    )
                    reason = f"{Refusal.WATCH}: {entry['when']} (on {watcher}) failed: {why}"
                    self._refuse(watcher, {}, None, watcher, at, commit, reason)
                    continue
                if "ask" in entry:
                    ask = Ask(**entry["ask"])
                    self._ask(watcher, ask, watcher, at, commit, depth + 1, skip_settled=True)
                elif not unchanged:
                    self._write(watcher, changes, None, watcher, at, commit, depth + 1)

    @arch.stage(
        "notice",
        "stage.notice.event",
        "A watch entry reads `event`, the id of the change it is reacting to, so a case "
        "can mark what it met.",
        doc="rules-and-reactions.md#variables-in-scope",
    )
    @arch.stage(
        "notice",
        "stage.notice.settled",
        "A question is settled only while its recorded answer is still in place; "
        "an overwritten answer is asked again.",
        doc="rules-and-reactions.md#asking-a-model",
    )
    @arch.stage(
        "think",
        "stage.think.retry",
        "An answer a rule refused is asked again once, with the reason; a second refusal "
        "writes the entry's `otherwise` text or stops.",
        doc="rules-and-reactions.md#when-an-answer-is-refused",
    )
    @arch.stage(
        "think",
        "stage.think.ask",
        "A prompt whose embeds are resolved and recorded as `Read`.",
        doc="rules-and-reactions.md#asking-a-model",
        roadmap="R4",
    )
    @arch.stage(
        "think",
        "stage.think.provider",
        "A named page first, then detection, then a plain sentence.",
        doc="providers.md#when-no-model-answers",
        roadmap="R26",
    )
    def _ask(
        self,
        page: str,
        ask: Ask,
        actor: str,
        at: str,
        cause: str | None,
        depth: int,
        *,
        skip_settled: bool,
    ) -> Result | None:
        """Ask a model and write the answer to a field of page, always leaving a sentence there.

        The provider page, when one is named, is tried first and its failure is recorded as a
        refusal whose reason starts with `model:`. Then each detected model is tried in order,
        and when none answers a plain sentence is written. Returns None when the question is
        skipped because its answer is already recorded.

        When a rule refuses the answer, or a page of it, the same prompt is sent once more with
        the reason after it, caused by the refusal. A second refusal by a rule writes the
        entry's `otherwise` text when it has one and stops. Never more than that one retry.
        """
        if depth > MAX_DEPTH:
            return self._refuse(page, {}, None, actor, at, cause, _CYCLE)
        pages = self._all()
        prompt = resolve_text(ask.prompt, pages)
        if ask.writes is not None:
            shown = any(
                (found.group(1), found.group(2)) == (ask.writes, MEMBERS)
                for found in EMBED.finditer(ask.prompt)
            )
            prompt = answer.instruction(page, ask.writes, shown) + prompt
        current = (self._load(page) or Page()).fields
        if (
            skip_settled
            and (ask.into is None or ask.into in current)
            and current.get(ask.marker) == _mark(prompt, current.get(ask.into or ""))
        ):
            return None
        where = (page, actor, at, cause, depth)
        result = self._think(ask, pages, prompt, prompt, where, skip_settled)
        refused = None if result is None or result.plain else _ruled(result)
        if refused is None:
            return result
        note = RETRY.format(reason=" ".join((refused.reason or "").split()))
        again = (page, actor, at, refused.id, depth)
        result = self._think(ask, pages, prompt, f"{prompt}\n\n{note}", again, False)
        refused = None if result is None or result.plain else _ruled(result)
        if refused is None or ask.into is None or ask.otherwise is None:
            return result
        last = (page, actor, at, refused.id, depth)
        return self._plain(last, ask, pages, prompt, False)

    def _think(
        self,
        ask: Ask,
        pages: dict[str, Page],
        prompt: str,
        sent: str,
        where: tuple[str, str, str, str | None, int],
        skip_settled: bool,
    ) -> Result | None:
        """Put sent to the models in order and write what comes back, or a plain sentence.

        The question is settled by prompt, the digest of what the entry asked, so a retry that
        adds a note to sent still settles the entry's own prompt.
        """
        page, actor, at, cause, _ = where
        moment = cause or self._head()
        if ask.provider is not None:
            try:
                loaded = self._load(ask.provider)
                found = model.provider(ask.provider, None if loaded is None else loaded.fields)

                def secret(found: model.Provider = found) -> str | None:
                    return model.find_secret(found.secret, self.keys_dir) if found.secret else None

                reply = model.ask_once(self.cache, found, secret, sent, self.keys_dir, moment)
                if reply is not None:
                    return self._answered(found, reply, ask, pages, prompt, sent, where)
            except model.ModelError as exc:
                self._refuse(page, {}, None, actor, at, cause, f"{Refusal.MODEL}: {exc}")
        for choice in model.detect().choices:
            try:
                reply = model.ask_once(
                    self.cache,
                    choice.provider,
                    lambda choice=choice: choice.secret,
                    sent,
                    self.keys_dir,
                    moment,
                )
            except model.ModelError:
                continue
            if reply is not None:
                return self._answered(choice.provider, reply, ask, pages, prompt, sent, where)
        return self._plain(where, ask, pages, prompt, skip_settled)

    @arch.stage(
        "act",
        "stage.act.field",
        "The answer is written to `into` by the asking page.",
        doc="rules-and-reactions.md#asking-a-model",
        roadmap="R4",
    )
    def _answered(
        self,
        found: model.Provider,
        reply: model.Answer,
        ask: Ask,
        pages: dict[str, Page],
        prompt: str,
        sent: str,
        where: tuple[str, str, str, str | None, int],
    ) -> Result:
        """Write a model's answer to the asking page, with the trailers that record it.

        When the entry may write pages, the answer is cut into plain text and page blocks. The
        text goes to `into`, and once that write has held each block is written in order as the
        actor, caused by the answer, one level deeper.
        """
        page, actor, at, cause, depth = where
        trailers = [(Trailer.MODEL, found.page), (Trailer.MODEL_NAME, found.name)]
        if reply.cached:
            trailers.append((Trailer.CACHE, CACHE_HIT))
        if reply.tokens_in is not None:
            trailers.append((Trailer.TOKENS_IN, str(reply.tokens_in)))
        if reply.tokens_out is not None:
            trailers.append((Trailer.TOKENS_OUT, str(reply.tokens_out)))
        trailers += [(Trailer.READ, name) for name in embedded(ask.prompt, pages)]
        text, blocks = reply.text, []
        if ask.writes is not None:
            text, blocks = answer.split(reply.text)
        changes = {ask.marker: _mark(prompt, text if ask.into is not None else None)}
        if ask.into is not None:
            changes[ask.into] = text
        result = self._write(page, changes, None, actor, at, cause, depth, (trailers, sent))
        if not (result.ok and blocks and ask.writes is not None):
            return result
        landed = self._land(blocks, ask.writes, page, actor, at, result.id, depth + 1)
        return Result(True, result.id, pages=landed)

    @arch.law(
        "law.answer.pages",
        "An answer is pages, so a character can make notes, characters, spaces and rules.",
        doc="rules-and-reactions.md#an-answer-that-is-pages",
        roadmap="R29",
    )
    @arch.stage(
        "act",
        "stage.act.page",
        "Each page is a write by the asker inside the named space.",
        doc="rules-and-reactions.md#an-answer-that-is-pages",
        roadmap="R29",
    )
    @arch.judged(
        "check.character.organise",
        "State, after a live run, whether the single character organised itself "
        "in a way that helped the task or only looked busy.",
        "The vault's pages and its history: which pages it wrote, which rules "
        "and watch entries it added, and what each was caused by.",
        "1 hurt, 2 no effect, 3 helped, 4 helped and is worth keeping",
        checks=["law.answer.pages", "flow.ask.pages"],
    )
    def _land(
        self,
        blocks: list[answer.Block],
        space: str,
        asker: str,
        actor: str,
        at: str,
        cause: str,
        depth: int,
    ) -> tuple[tuple[str, Result], ...]:
        """Write each page block into space, in order. A bad block is one recorded refusal."""
        landed = []
        for block in blocks:
            name = block.name if NAME.match(block.name) else asker
            try:
                if block.problem is not None:
                    raise ShapeError(block.problem)
                changes, body = given(block.text)
            except ShapeError as exc:
                reason = f"{Refusal.SHAPE}: page block {block.name or '(no name)'}: {exc}"
                landed.append((name, self._refuse(name, {}, None, actor, at, cause, reason)))
                continue
            landed.append(
                (name, self._write(name, changes, body, actor, at, cause, depth, bound=space))
            )
        return tuple(landed)

    @arch.change(
        "place.runtime.plain",
        "Writing a plain sentence when no model answers.",
        doc="providers.md#when-no-model-answers",
        roadmap="R26",
    )
    def _plain(
        self,
        where: tuple[str, str, str, str | None, int],
        ask: Ask,
        pages: dict[str, Page],
        prompt: str,
        skip_same: bool,
    ) -> Result | None:
        """Write a plain sentence because no model answered, and leave the question unsettled.

        The field `<into>_asked` is not written, so the next ask with a model asks for real.
        Returns None when a reaction would write the sentence the page already holds. An ask
        with no `into` has nowhere to put a sentence, so the failure is recorded as a refusal
        and no page is written.
        """
        page, actor, at, cause, depth = where
        if ask.into is None:
            reason = (
                f"{Refusal.MODEL}: no model answered, so no pages were written: "
                f"to give Conky one, {model.WAYS}"
            )
            return self._refuse(page, {}, None, actor, at, cause, reason)
        if ask.otherwise is None:
            text = model.plain_sentence(page, ask.into, prompt)
        else:
            text = resolve_text(ask.otherwise, pages).strip()
        if skip_same and (self._load(page) or Page()).fields.get(ask.into) == text:
            return None
        trailers = [(Trailer.MODEL, "none")] + [
            (Trailer.READ, name) for name in embedded(ask.prompt, pages)
        ]
        changes = {ask.into: text}
        result = self._write(page, changes, None, actor, at, cause, depth, (trailers, prompt))
        return Result(result.ok, result.id, result.reason, plain=True)
