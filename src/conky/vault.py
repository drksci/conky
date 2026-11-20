"""The vault: a Git repository whose commits are the events and whose files are the pages."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path
from typing import Any

from conky import answer, git, model
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
KINDS = ("write", "refused")
CACHE_HIT = "hit"


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

    def read(self, page: str) -> Page:
        """Return the page with its embeds resolved."""
        found = self._load(check_name(page))
        if found is None:
            raise BadInput(f"no page named {page!r}")
        return resolve(found, self._all())

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
