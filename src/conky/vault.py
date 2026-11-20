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
    NAME,
    Page,
    ShapeError,
    apply,
    check_name,
    embedded,
    given,
    parse,
    resolve,
    resolve_text,
    serialize,
)
from conky.rules import RuleError, evaluate, holds

MAX_DEPTH = 12
KINDS = arch.constant(
    ("write", "refused"),
    "event kind",
    "conky.vault.KINDS",
    "event kinds",
    "What an event is: a write or a refusal.",
    doc="vault-format.md#commits",
)
CACHE_HIT = "hit"


@arch.slot(
    "trailer key", "trailer", "A key of a commit's trailer block.", doc="vault-format.md#commits"
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
    "refusal",
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


_CYCLE = f"{Refusal.CYCLE}: reactions nested deeper than {MAX_DEPTH}"


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
    "vault",
    "history",
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
        "read",
        "history",
        "Return a page with its embeds resolved.",
        doc="cli.md#read",
    )
    @arch.step("read-a-page", 1, "Person", "Runtime", "conky read page")
    @arch.step("read-a-page", 2, "Runtime", "Page", "load the stored page")
    @arch.step(
        "read-a-page", 4, "Runtime", "Person", "the page, and a missing target gives nothing"
    )
    def read(self, page: str) -> Page:
        """Return the page with its embeds resolved."""
        found = self._load(check_name(page))
        if found is None:
            raise BadInput(f"no page named {page!r}")
        return resolve(found, self._all())

    @arch.law(
        "only-writes-change-state",
        "State changes only through a write committed to the history.",
        doc="../decisions/0002-git-is-the-store.md",
    )
    @arch.part(
        "write",
        "history",
        "Commit a change to a page, or commit its refusal.",
        doc="cli.md#write",
    )
    @arch.step("accepted-write", 1, "Person", "Runtime", "write page, fields and body, as an actor")
    @arch.step("accepted-write", 2, "Runtime", "History", "is the working tree clean")
    @arch.step("refused-write", 1, "Person", "Runtime", "a write that breaks a rule")
    @arch.step(
        "measure-and-pressure", 1, "Person", "Runtime", "a large write to a page with no size rule"
    )
    @arch.step("join-and-leave", 1, "Person", "Runtime", "write within: a space name, or nothing")
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

    @arch.step("asking-a-model", 2, "Person", "Runtime", "or a person runs conky ask")
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
        "stream",
        "The Git history, the one stream every vault already has, read oldest first.",
        doc="vault-format.md#commits",
    )
    @arch.step(
        "measure-and-pressure",
        8,
        "Runtime",
        None,
        "reading history evaluates nothing, and nothing yet relieves pressure",
    )
    @arch.step("read-a-page", 5, "Person", "Runtime", "conky log")
    @arch.step("read-a-page", 6, "Runtime", "History", "commits oldest first")
    @arch.step(
        "read-a-page", 7, "Runtime", "Person", "one line each, with cause, model, read and from"
    )
    @arch.step("read-a-page", 8, "Runtime", None, "no model is called and no event is made")
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
        "pages-are-the-committed-files",
        "Pages are the committed files, and a stray edit is refused or discarded.",
        doc="vault-format.md#what-verify-checks",
    )
    @arch.change(
        "runtime",
        "Checking the history, never changing it.",
        doc="vault-format.md#what-verify-checks",
    )
    @arch.step("verify", 1, "Person", "Runtime", "conky verify")
    @arch.step("verify", 2, "Runtime", "History", "is the working tree clean")
    @arch.step("verify", 3, "Runtime", "Outside", "git fsck strict")
    @arch.step("verify", 9, "Runtime", None, "rules are not evaluated and page content is not read")
    @arch.step("clone-and-leave", 3, "Person", "Runtime", "verify, with Git and ssh-keygen only")
    @arch.step("clone-and-leave", 5, "Runtime", "Person", "ok, and no private key was needed")
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
        "runtime",
        "Restoring the working tree from the history.",
        doc="vault-format.md#rebuild",
    )
    @arch.step("rebuild", 3, "Person", "Runtime", "conky rebuild")
    @arch.step("rebuild", 4, "Runtime", "History", "reset hard to main")
    @arch.step("rebuild", 5, "Runtime", "Page", "remove untracked files under pages and keys")
    def rebuild(self) -> None:
        """Restore the working tree to the committed state, discarding stray changes."""
        if self._has_commits():
            git.run(["reset", "-q", "--hard", "main"], self.path)
        git.run(["clean", "-fdq", "--", "pages", "keys"], self.path)

    @arch.step(
        "verify",
        4,
        "Runtime",
        "History",
        "each commit, oldest first: a good signature from a listed key",
    )
    @arch.step("verify", 5, "Runtime", "History", "Kind is write or refused")
    @arch.step(
        "verify",
        6,
        "Runtime",
        "History",
        "a write touches only pages and allowed_signers, a refusal only allowed_signers",
    )
    @arch.step(
        "verify", 7, "Runtime", "Person", "the first problem is an error, exit 1", refusal=True
    )
    @arch.step("clone-and-leave", 4, "Runtime", "History", "every seal against allowed_signers")
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

    @arch.step("rebuild", 1, "Person", "Page", "a page is edited by hand, so the tree is dirty")
    def _dirty(self) -> bool:
        return bool(git.run(["status", "--porcelain"], self.path).strip())

    @arch.step(
        "rebuild", 2, "Runtime", "Person", "verify or the next write: an error naming the fix"
    )
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
        "every-change-is-signed",
        "Every change is signed and says what caused it.",
        doc="vault-format.md#a-write",
    )
    @arch.part(
        "event",
        "history",
        "A commit: one write or one refusal.",
        doc="vault-format.md#commits",
    )
    @arch.stage(
        "record",
        "a signed event with its cause",
        "Every stimulus and every action is an event, or a refusal.",
        doc="vault-format.md#commits",
    )
    @arch.change(
        "runtime",
        "Signing every event and recording every refusal.",
        doc="vault-format.md#commits",
    )
    @arch.step(
        "accepted-write", 7, "Runtime", "History", "one signed commit with Kind, Page and Cause"
    )
    @arch.step(
        "refused-write",
        6,
        "Runtime",
        "History",
        "an empty signed commit, Kind refused, no page changed",
    )
    @arch.step(
        "reaction-cascade",
        6,
        "Runtime",
        "History",
        "a signed commit by the watching page, with Cause",
    )
    @arch.step(
        "measure-and-pressure", 2, "Runtime", "History", "the write is kept, with no refusal"
    )
    @arch.step(
        "measure-and-pressure", 4, "Runtime", "History", "the number is its own signed event"
    )
    @arch.step("join-and-leave", 6, "Runtime", "History", "every rule holds: a signed write")
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
        "refusal-is-recorded",
        "A refused write is recorded as an empty commit, never dropped.",
        doc="vault-format.md#a-refusal",
    )
    @arch.step(
        "refused-write",
        5,
        "Runtime",
        None,
        "reason, attempt, body size, and From when a space refused",
    )
    @arch.step(
        "join-and-leave",
        7,
        "Runtime",
        "History",
        "a rule is false or a space is missing: a refusal naming that space in From",
        refusal=True,
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
        "runtime",
        "Judging rules, shape and limits before a write is kept.",
        doc="rules-and-reactions.md#refusals",
    )
    @arch.step(
        "accepted-write", 3, "Runtime", "Page", "load the page as it is and apply the changes"
    )
    @arch.step(
        "refused-write",
        2,
        "Runtime",
        "Page",
        "apply the changes, a malformed key is a shape refusal",
    )
    @arch.step("refused-write", 7, "Runtime", "Page", "no reactions run, because nothing changed")
    @arch.step(
        "reaction-cascade", 5, "Runtime", "Page", "write as the watching page, one level deeper"
    )
    @arch.step(
        "reaction-cascade",
        8,
        "Runtime",
        "History",
        "deeper than 12: a cycle refusal, and nothing deeper runs",
        refusal=True,
    )
    @arch.step(
        "answer-is-pages",
        8,
        "Runtime",
        "History",
        "a limit or a rule is broken: a recorded refusal",
        refusal=True,
    )
    @arch.step("join-and-leave", 2, "Runtime", "Page", "the page as it would be after the write")
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
        before = self._load(page)
        try:
            result = apply(before or Page(), changes, body)
        except ShapeError as exc:
            return refuse(f"{Refusal.SHAPE}: {exc}")
        if bound is not None:
            breach = self._breach(page, before, result, bound)
            if breach:
                return refuse(f"{Refusal.LIMIT}: {breach}")
        refused = self._rule_reason(page, result, before)
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

    @arch.law(
        "reach-flows-down",
        "A character writes only inside the space it was given, and creates nothing wider.",
        doc="../decisions/0029-autonomy-inside-limits-that-hold.md",
        roadmap="R29",
    )
    @arch.law(
        "runtime-is-not-a-page",
        "The runtime is not a page, so no character can change it.",
        doc="../decisions/0029-autonomy-inside-limits-that-hold.md",
    )
    @arch.change(
        "runtime",
        "Enforcing the limits of an answer that is pages.",
        doc="rules-and-reactions.md#an-answer-that-is-pages",
        roadmap="R29",
    )
    @arch.step(
        "answer-is-pages",
        6,
        "Runtime",
        "Space",
        "within the named space before and after, no secret or command, no wider watch",
    )
    def _breach(self, name: str, before: Page | None, page: Page, space: str) -> str | None:
        """Return the limit a page written by an answer breaks, if any.

        The page must lie within the space before the write, when it exists, and after it.
        """
        if name == space or not self._inside(page.within, space):
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

    @arch.law(
        "rules-only-tighten",
        "A member adds a rule and cannot remove one or leave one behind.",
        doc="../decisions/0022-leaving-a-space-is-a-write-the-space-can-refuse.md",
        roadmap="R29",
    )
    @arch.step("accepted-write", 4, "Runtime", "Page", "judge its own rules, with size in scope")
    @arch.step("refused-write", 3, "Runtime", "Page", "judge its own rules")
    @arch.step(
        "answer-is-pages",
        7,
        "Runtime",
        "Space",
        "the rules of every space involved, including a space it leaves",
    )
    @arch.step(
        "join-and-leave",
        3,
        "Runtime",
        "Space",
        "the rules of the page and of every space it will be in",
    )
    @arch.step(
        "join-and-leave",
        4,
        "Runtime",
        "Space",
        "if it was in a space: that space's rules, against the page after",
    )
    def _rule_reason(
        self, name: str, page: Page, before: Page | None = None
    ) -> tuple[str, str] | None:
        """Return the reason a rule refuses the page and the page the rule came from.

        The rules of the page and of every space above it are judged. A write that changes
        `within` is also judged by the rules of the spaces the page was in before it.
        """
        scope = {"page": page.fields, "size": _size(page)}
        found = self._walk(name, page, name, scope)
        if found or before is None or not before.within or before.within == page.within:
            return found
        left = self._load(before.within)
        if left is None:
            return f"{Refusal.RULE}: space {before.within} does not exist", name
        return self._walk(name, left, before.within, scope)

    @arch.part(
        "space",
        "spaces",
        "A page that others lie within, handing down its rules, with leaving judged.",
        doc="rules-and-reactions.md#rules-and-spaces",
        roadmap="R29",
    )
    @arch.archetype(
        "space",
        "a person or a character",
        "A page others name in `within`, with `rules`.",
        doc="rules-and-reactions.md#rules-and-spaces",
        roadmap="R29",
    )
    @arch.step(
        "accepted-write", 5, "Runtime", "Space", "judge the rules of each space up the chain"
    )
    @arch.step(
        "refused-write",
        4,
        "Runtime",
        "Space",
        "judge each space up the chain: a rule is false, fails or loops",
    )
    @arch.step("join-and-leave", 5, "Space", None, "a space that says nothing lets its members go")
    def _walk(
        self, name: str, space: Page, owner: str, scope: dict[str, Any]
    ) -> tuple[str, str] | None:
        """Judge the rules of space and of the spaces above it against scope."""
        seen = {name}
        while True:
            for rule in space.rules:
                try:
                    held = holds(rule, scope)
                except RuleError as exc:
                    return f"{Refusal.RULE}: {rule} (from {owner}) failed to evaluate: {exc}", owner
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

    @arch.law(
        "pressure-not-walls",
        "Anything to be noticed is a pressure that triggers a reaction, not a wall.",
        doc="rules-and-reactions.md#measures",
        roadmap="R2",
    )
    @arch.law(
        "measure-is-a-self-watch",
        "A measure is a page watching itself, and its value is a recorded event.",
        doc="../decisions/0008-measures-are-self-watches.md",
        roadmap="R2",
    )
    @arch.law(
        "reflexes-are-free",
        "Whatever follows from state is a reflex with no model call.",
        doc="../decisions/0007-inference-for-real-thinking.md",
    )
    @arch.part(
        "watch",
        "reflexes",
        "Name a page whose writes make this page react.",
        doc="rules-and-reactions.md#reactions",
    )
    @arch.archetype(
        "character",
        "a person or a character",
        "Any page with `watch` entries or an `ask`.",
        doc="../decisions/0020-everything-is-somebody.md",
        roadmap="R4",
    )
    @arch.archetype(
        "measure-bearing page",
        "a person or a character",
        "A diary, a counter or any page with a self-watch.",
        doc="rules-and-reactions.md#measures",
        roadmap="R2",
    )
    @arch.stage(
        "stimulus",
        "another page's write",
        "Every write, a reaction included, is the stimulus for the pages that watch it.",
        doc="rules-and-reactions.md#reactions",
    )
    @arch.stage(
        "notice",
        "a watch entry's `on` and `when`",
        "`on` names the page and `when` must be the boolean true.",
        doc="rules-and-reactions.md#reactions",
    )
    @arch.stage(
        "notice",
        "pressure",
        "A second self-watch entry whose `when` reads the number crossing a threshold.",
        doc="rules-and-reactions.md#measures",
        roadmap="R2",
    )
    @arch.stage(
        "notice",
        "skipped when nothing changed",
        "A reaction that leaves the page unchanged is not written.",
        doc="rules-and-reactions.md#reactions",
    )
    @arch.change(
        "runtime",
        "Running reactions after a write, depth first, bounded at 12.",
        doc="rules-and-reactions.md#reactions",
    )
    @arch.step(
        "accepted-write", 8, "Runtime", "Page", "run every watcher, see the reaction cascade"
    )
    @arch.step(
        "reaction-cascade",
        1,
        "Runtime",
        "Page",
        "visit every page in order of name for watch entries on the page just written",
    )
    @arch.step(
        "reaction-cascade",
        2,
        "Runtime",
        "Page",
        "evaluate when, with page, other, size and other_size",
    )
    @arch.step(
        "reaction-cascade",
        3,
        "Runtime",
        "History",
        "when or a set expression fails: a watch refusal on the watching page",
        refusal=True,
    )
    @arch.step(
        "reaction-cascade",
        4,
        "Runtime",
        None,
        "when is false, or the change leaves the page as it is: skipped",
    )
    @arch.step(
        "reaction-cascade", 7, "Runtime", "Page", "its own watchers react in turn, depth first"
    )
    @arch.step(
        "measure-and-pressure",
        3,
        "Runtime",
        "Page",
        "self-watch: on itself, set pressure from size",
    )
    @arch.step(
        "measure-and-pressure",
        5,
        "Runtime",
        "Page",
        "second entry: when pressure passes the threshold a state is set",
    )
    @arch.step("measure-and-pressure", 6, "Runtime", "Page", "pages that watch that state react")
    @arch.step(
        "measure-and-pressure",
        7,
        "Runtime",
        None,
        "unchanged values are skipped, so the chain settles",
    )
    @arch.step("asking-a-model", 1, "Page", "Runtime", "an ask entry fires")
    @arch.step("answer-is-pages", 1, "Page", "Runtime", "an ask entry with writes names a space")
    @arch.step("answer-is-pages", 10, "Runtime", "Page", "reactions, one level deeper each")
    def _react(self, source: str, written: Page, commit: str, at: str, depth: int) -> None:
        for watcher in sorted(p.stem for p in self.pages_dir.glob("*.md")):
            for entry in (self._load(watcher) or Page()).watch:
                if entry["on"] != source:
                    continue
                current = self._load(watcher) or Page()
                scope = {
                    "other": written.fields,
                    "page": current.fields,
                    "other_size": _size(written),
                    "size": _size(current),
                }
                try:
                    if not holds(entry["when"], scope):
                        continue
                    changes = {k: evaluate(v, scope) for k, v in entry.get("set", {}).items()}
                    unchanged = serialize(apply(current, changes, None)) == serialize(current)
                except (RuleError, ShapeError) as exc:
                    reason = f"{Refusal.WATCH}: {entry['when']} (on {watcher}) failed: {exc}"
                    self._refuse(watcher, {}, None, watcher, at, commit, reason)
                    continue
                if "ask" in entry:
                    ask = Ask(**entry["ask"])
                    self._ask(watcher, ask, watcher, at, commit, depth + 1, skip_settled=True)
                elif not unchanged:
                    self._write(watcher, changes, None, watcher, at, commit, depth + 1)

    @arch.stage(
        "notice",
        "a settled question is skipped",
        "A recorded answer for the same resolved prompt is never asked twice.",
        doc="rules-and-reactions.md#asking-a-model",
    )
    @arch.stage(
        "think",
        "ask",
        "A prompt whose embeds are resolved and recorded as `Read`.",
        doc="rules-and-reactions.md#asking-a-model",
        roadmap="R4",
    )
    @arch.stage(
        "think",
        "providers in order",
        "A named page first, then detection, then a plain sentence.",
        doc="providers.md#when-no-model-answers",
        roadmap="R26",
    )
    @arch.step(
        "asking-a-model",
        3,
        "Runtime",
        "Page",
        "resolve embeds in the prompt, and add the page instruction when writes is set",
    )
    @arch.step(
        "asking-a-model",
        4,
        "Runtime",
        None,
        "skip when into_asked already holds this prompt's digest",
    )
    @arch.step("asking-a-model", 5, "Runtime", "Page", "a provider page is named: read it")
    @arch.step(
        "asking-a-model",
        10,
        "Runtime",
        "History",
        "the named provider failed: a model refusal on the asking page",
        refusal=True,
    )
    @arch.step(
        "asking-a-model",
        12,
        "Runtime",
        "Provider",
        "each detected model in order, a failure goes on to the next",
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
        """
        if depth > MAX_DEPTH:
            return self._refuse(page, {}, None, actor, at, cause, _CYCLE)
        pages = self._all()
        prompt = resolve_text(ask.prompt, pages)
        if ask.writes is not None:
            prompt += answer.instruction(ask.writes)
        digest = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
        current = (self._load(page) or Page()).fields
        if (
            skip_settled
            and (ask.into is None or ask.into in current)
            and current.get(ask.marker) == digest
        ):
            return None
        where = (page, actor, at, cause, depth)
        moment = cause or self._head()
        if ask.provider is not None:
            try:
                loaded = self._load(ask.provider)
                found = model.provider(ask.provider, None if loaded is None else loaded.fields)

                def secret(found: model.Provider = found) -> str | None:
                    return model.find_secret(found.secret, self.keys_dir) if found.secret else None

                reply = model.ask_once(self.cache, found, secret, prompt, self.keys_dir, moment)
                if reply is not None:
                    return self._answered(found, reply, ask, digest, pages, prompt, where)
            except model.ModelError as exc:
                self._refuse(page, {}, None, actor, at, cause, f"{Refusal.MODEL}: {exc}")
        for choice in model.detect().choices:
            try:
                reply = model.ask_once(
                    self.cache,
                    choice.provider,
                    lambda choice=choice: choice.secret,
                    prompt,
                    self.keys_dir,
                    moment,
                )
            except model.ModelError:
                continue
            if reply is not None:
                return self._answered(choice.provider, reply, ask, digest, pages, prompt, where)
        return self._plain(where, ask, pages, prompt, skip_settled)

    @arch.stage(
        "act",
        "a field of the asking page",
        "The answer is written to `into` by the asking page.",
        doc="rules-and-reactions.md#asking-a-model",
        roadmap="R4",
    )
    @arch.step(
        "asking-a-model",
        13,
        "Runtime",
        "History",
        "a signed write by the asking page, with Model, tokens, Read and the prompt",
    )
    @arch.step(
        "answer-is-pages",
        4,
        "Runtime",
        "History",
        "the answer is written first, by the asking page, and a refused answer applies no page",
    )
    def _answered(
        self,
        found: model.Provider,
        reply: model.Answer,
        ask: Ask,
        digest: str,
        pages: dict[str, Page],
        prompt: str,
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
        changes = {ask.marker: digest}
        if ask.into is not None:
            changes[ask.into] = text
        result = self._write(page, changes, None, actor, at, cause, depth, (trailers, prompt))
        if not (result.ok and blocks and ask.writes is not None):
            return result
        landed = self._land(blocks, ask.writes, page, actor, at, result.id, depth + 1)
        return Result(True, result.id, pages=landed)

    @arch.law(
        "pages-capability",
        "An answer is pages, so a character can make notes, characters, spaces and rules.",
        doc="rules-and-reactions.md#an-answer-that-is-pages",
        roadmap="R29",
    )
    @arch.stage(
        "act",
        "pages through writes",
        "Each page is a write by the asker inside the named space.",
        doc="rules-and-reactions.md#an-answer-that-is-pages",
        roadmap="R29",
    )
    @arch.step(
        "answer-is-pages",
        5,
        "Runtime",
        "History",
        "a header with no name or a malformed page: one shape refusal, the rest still apply",
        refusal=True,
    )
    @arch.step(
        "answer-is-pages",
        9,
        "Runtime",
        "History",
        "a signed write by the asker, caused by the answer",
    )
    @arch.judged(
        "character-organised-itself",
        "State, after a live run, whether the single character organised itself "
        "in a way that helped the task or only looked busy.",
        "The vault's pages and its history: which pages it wrote, which rules "
        "and watch entries it added, and what each was caused by.",
        "1 hurt, 2 no effect, 3 helped, 4 helped and is worth keeping",
        checks=["pages-capability", "answer-is-pages"],
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
        "runtime",
        "Writing a plain sentence when no model answers.",
        doc="providers.md#when-no-model-answers",
        roadmap="R26",
    )
    @arch.step(
        "asking-a-model",
        14,
        "Runtime",
        "History",
        "none answered: a plain sentence, Model none, no marker, so a later model replaces it",
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
