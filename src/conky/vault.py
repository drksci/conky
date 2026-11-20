"""The vault: a Git repository whose commits are the events and whose files are the pages."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path
from typing import Any

from conky import git, model
from conky.errors import BadInput, VerifyFailed
from conky.page import (
    Page,
    ShapeError,
    apply,
    check_name,
    embedded,
    parse,
    resolve,
    resolve_text,
    serialize,
)
from conky.rules import RuleError, evaluate, holds

MAX_DEPTH = 12
KINDS = ("write", "refused")


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


class Refusal(StrEnum):
    """The word a refusal's reason starts with, saying which law refused."""

    CYCLE = "cycle"
    SHAPE = "shape"
    RULE = "rule"
    WATCH = "watch"
    MODEL = "model"


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


class Vault:
    """A Git repository of pages, with public keys tracked and private keys kept elsewhere."""

    def __init__(self, path: str | Path, keys_dir: str | Path | None = None) -> None:
        git.require_tools()
        self.path = Path(path)
        if not (self.path / ".git").exists():
            raise BadInput(f"{self.path} is not a vault: create one with `conky init {self.path}`")
        self.pages_dir = self.path / "pages"
        self.signers = self.path / git.SIGNERS
        self.keys_dir = Path(keys_dir) if keys_dir is not None else Path.home() / ".conky" / "keys"

    @classmethod
    def init(cls, path: str | Path, keys_dir: str | Path | None = None) -> Vault:
        """Create an empty vault at path and return it."""
        git.require_tools()
        if (Path(path) / ".git").exists():
            raise BadInput(f"{path} is already a vault")
        git.init(Path(path))
        return cls(path, keys_dir)

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
        into: str,
        *,
        provider: str | None = None,
        prompt: str,
        actor: str,
        at: str,
        cause: str | None = None,
    ) -> Result:
        """Ask a model once and write the answer to a field of the page, or record why not.

        With no provider page the model is detected from the environment and the PATH.
        """
        check_name(page)
        check_name(actor)
        if provider is not None:
            check_name(provider)
        if not into:
            raise BadInput("the field to write the answer to must be a non-empty name")
        if self._dirty():
            raise BadInput(self._dirty_message())
        return self._ask(
            page, into, provider, prompt, None, actor, at, cause, 0, skip_settled=False
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
    ) -> Result:
        def refuse(reason: str) -> Result:
            return self._refuse(page, changes, body, actor, at, cause, reason, asked)

        if depth > MAX_DEPTH:
            return refuse(_CYCLE)
        try:
            result = apply(self._load(page) or Page(), changes, body)
        except ShapeError as exc:
            return refuse(f"{Refusal.SHAPE}: {exc}")
        refused = self._rule_reason(page, result)
        if refused:
            reason, space = refused
            if space != page:
                asked = ([*asked[0], (Trailer.FROM, space)], asked[1])
            return self._refuse(page, changes, body, actor, at, cause, reason, asked)
        commit = self._record("write", page, actor, at, cause, asked[0], result, asked[1])
        self._react(page, result, commit, at, depth)
        return Result(True, commit)

    def _rule_reason(self, name: str, page: Page) -> tuple[str, str] | None:
        """Return the reason a rule refuses the page and the page the rule came from."""
        scope = {"page": page.fields, "size": _size(page)}
        seen = {name}
        space, owner = page, name
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
                    ask = entry["ask"]
                    args = (ask["into"], ask.get("provider"), ask["prompt"], ask.get("otherwise"))
                    self._ask(watcher, *args, watcher, at, commit, depth + 1, skip_settled=True)
                elif not unchanged:
                    self._write(watcher, changes, None, watcher, at, commit, depth + 1)

    def _ask(
        self,
        page: str,
        into: str,
        provider: str | None,
        template: str,
        otherwise: str | None,
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
        prompt = resolve_text(template, pages)
        digest = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
        marker = f"{into}_asked"
        current = (self._load(page) or Page()).fields
        if skip_settled and into in current and current.get(marker) == digest:
            return None
        if provider is not None:
            try:
                loaded = self._load(provider)
                found = model.provider(provider, None if loaded is None else loaded.fields)
                secret = model.find_secret(found.secret, self.keys_dir) if found.secret else None
                answer = model.ask(found, secret, prompt, self.keys_dir)
                return self._answered(
                    found,
                    answer,
                    into,
                    digest,
                    template,
                    pages,
                    prompt,
                    (page, actor, at, cause, depth),
                )
            except model.ModelError as exc:
                self._refuse(page, {}, None, actor, at, cause, f"{Refusal.MODEL}: {exc}")
        for choice in model.detect().choices:
            try:
                answer = model.ask(choice.provider, choice.secret, prompt, self.keys_dir)
            except model.ModelError:
                continue
            where = (page, actor, at, cause, depth)
            return self._answered(
                choice.provider, answer, into, digest, template, pages, prompt, where
            )
        where = (page, actor, at, cause, depth)
        return self._plain(where, into, otherwise, template, pages, prompt, skip_settled)

    def _answered(
        self,
        found: model.Provider,
        answer: model.Answer,
        into: str,
        digest: str,
        template: str,
        pages: dict[str, Page],
        prompt: str,
        where: tuple[str, str, str, str | None, int],
    ) -> Result:
        """Write a model's answer to the asking page, with the trailers that record it."""
        page, actor, at, cause, depth = where
        trailers = [(Trailer.MODEL, found.page), (Trailer.MODEL_NAME, found.name)]
        if answer.tokens_in is not None:
            trailers.append((Trailer.TOKENS_IN, str(answer.tokens_in)))
        if answer.tokens_out is not None:
            trailers.append((Trailer.TOKENS_OUT, str(answer.tokens_out)))
        trailers += [(Trailer.READ, name) for name in embedded(template, pages)]
        changes = {into: answer.text, f"{into}_asked": digest}
        return self._write(page, changes, None, actor, at, cause, depth, (trailers, prompt))

    def _plain(
        self,
        where: tuple[str, str, str, str | None, int],
        into: str,
        otherwise: str | None,
        template: str,
        pages: dict[str, Page],
        prompt: str,
        skip_same: bool,
    ) -> Result | None:
        """Write a plain sentence because no model answered, and leave the question unsettled.

        The field `<into>_asked` is not written, so the next ask with a model asks for real.
        Returns None when a reaction would write the sentence the page already holds.
        """
        page, actor, at, cause, depth = where
        if otherwise is None:
            text = model.plain_sentence(page, into, prompt)
        else:
            text = resolve_text(otherwise, pages).strip()
        if skip_same and (self._load(page) or Page()).fields.get(into) == text:
            return None
        trailers = [(Trailer.MODEL, "none")] + [
            (Trailer.READ, name) for name in embedded(template, pages)
        ]
        result = self._write(page, {into: text}, None, actor, at, cause, depth, (trailers, prompt))
        return Result(result.ok, result.id, result.reason, plain=True)
