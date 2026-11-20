"""The vault: pages as projections of a signed, append-only log."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from conky import keys, log
from conky.errors import BadInput, VerifyFailed
from conky.page import (
    Page,
    ShapeError,
    apply,
    check_name,
    parse,
    resolve,
    serialize,
)
from conky.rules import RuleError, evaluate, holds

MAX_DEPTH = 12
_BASE_KEYS = {"seq", "at", "actor", "page", "kind", "set", "body", "cause", "prev", "seal"}


@dataclass(frozen=True)
class Result:
    """The outcome of a write: whether it held, the event's seq, and why not."""

    ok: bool
    seq: int
    reason: str | None = None


class Vault:
    """A directory of pages, an event log and public keys."""

    def __init__(self, path: str | Path, keys_dir: str | Path | None = None) -> None:
        self.path = Path(path)
        self.pages_dir = self.path / "pages"
        self.public_dir = self.path / "keys"
        self.log = log.Log(self.path / "log" / "events.jsonl")
        private = Path(keys_dir) if keys_dir is not None else Path.home() / ".conky" / "keys"
        self.keyring = keys.Keyring(private, self.public_dir)

    @classmethod
    def init(cls, path: str | Path, keys_dir: str | Path | None = None) -> Vault:
        """Create an empty vault at path and return it."""
        vault = cls(path, keys_dir)
        if vault.log.path.exists():
            raise BadInput(f"{vault.path} is already a vault")
        for directory in (vault.pages_dir, vault.public_dir, vault.log.path.parent):
            directory.mkdir(parents=True, exist_ok=True)
        vault.log.path.touch()
        return vault

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
        cause: int | None = None,
    ) -> Result:
        """Write fields and body to a page, or record why the write was refused."""
        check_name(page)
        check_name(actor)
        try:
            log.canonical({"set": set, "body": body})
        except (TypeError, ValueError) as exc:
            raise BadInput(f"values must be plain JSON data: {exc}") from exc
        return self._write(page, dict(set), body, actor, at, cause, 0)

    def verify(self) -> None:
        """Raise VerifyFailed naming the first problem in the chain, seals or pages."""
        try:
            text = self.log.path.read_bytes().decode("utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            raise VerifyFailed(f"log cannot be read: {exc}") from exc
        if text and not text.endswith("\n"):
            raise VerifyFailed("log does not end with a newline")
        state: dict[str, Page] = {}
        prev = log.ZERO
        for index, line in enumerate(text.split("\n")[:-1]):
            event = self._check_event(index, line, prev)
            if event["kind"] == "write":
                try:
                    state[event["page"]] = apply(
                        state.get(event["page"], Page()), event["set"], event["body"]
                    )
                except ShapeError as exc:
                    raise VerifyFailed(f"event {index}: write cannot be replayed: {exc}") from exc
            prev = log.digest(line)
        self._check_pages(state)

    def rebuild(self) -> None:
        """Delete pages/ and regenerate it from the log alone."""
        for stale in self.pages_dir.glob("*.md"):
            stale.unlink()
        self.pages_dir.mkdir(parents=True, exist_ok=True)
        state: dict[str, Page] = {}
        for event in self.log.events():
            if event["kind"] == "write":
                state[event["page"]] = apply(
                    state.get(event["page"], Page()), event["set"], event["body"]
                )
        for name, page in state.items():
            self._store(name, page)

    def _check_event(self, index: int, line: str, prev: str) -> dict[str, Any]:
        def fail(why: str) -> VerifyFailed:
            return VerifyFailed(f"event {index}: {why}")

        try:
            event = json.loads(line)
        except json.JSONDecodeError as exc:
            raise fail(f"not valid JSON: {exc}") from exc
        if not isinstance(event, dict) or log.canonical(event) != line:
            raise fail("line is not canonical JSON")
        expected = _BASE_KEYS | ({"reason"} if event.get("kind") == "refused" else set())
        if set(event) != expected or event["kind"] not in ("write", "refused"):
            raise fail("fields do not match the event format")
        if event["seq"] != index:
            raise fail(f"seq is {event['seq']}, expected {index}")
        if event["prev"] != prev:
            raise fail("prev does not match the hash of the previous event")
        unsealed = log.canonical({k: v for k, v in event.items() if k != "seal"})
        problem = keys.check_seal(
            self.public_dir, str(event["actor"]), unsealed.encode("utf-8"), str(event["seal"])
        )
        if problem:
            raise fail(problem)
        try:
            check_name(event["page"])
        except BadInput as exc:
            raise fail(str(exc)) from exc
        return event

    def _check_pages(self, state: dict[str, Page]) -> None:
        on_disk = {p.stem: p for p in self.pages_dir.glob("*.md")}
        extra = sorted(set(on_disk) - set(state))
        if extra:
            raise VerifyFailed(f"page {extra[0]!r} exists but no event writes it")
        for name, page in sorted(state.items()):
            if name not in on_disk:
                raise VerifyFailed(f"page {name!r} is missing from pages/")
            if on_disk[name].read_bytes() != serialize(page).encode("utf-8"):
                raise VerifyFailed(f"page {name!r} differs from the log replayed from empty")

    def _load(self, name: str) -> Page | None:
        path = self.pages_dir / f"{name}.md"
        return parse(path.read_text(encoding="utf-8")) if path.exists() else None

    def _store(self, name: str, page: Page) -> None:
        (self.pages_dir / f"{name}.md").write_bytes(serialize(page).encode("utf-8"))

    def _all(self) -> dict[str, Page]:
        return {p.stem: parse(p.read_text(encoding="utf-8")) for p in self.pages_dir.glob("*.md")}

    def _record(
        self,
        kind: str,
        page: str,
        changes: dict[str, Any],
        body: str | None,
        actor: str,
        at: str,
        cause: int | None,
        reason: str | None,
    ) -> int:
        event: dict[str, Any] = {
            "at": at, "actor": actor, "page": page, "kind": kind,
            "set": changes, "body": body, "cause": cause,
        }  # fmt: skip
        if reason is not None:
            event["reason"] = reason
        stored = self.log.append(event, lambda data: self.keyring.sign(actor, data))
        return stored["seq"]

    def _refuse(
        self,
        page: str,
        changes: dict[str, Any],
        body: str | None,
        actor: str,
        at: str,
        cause: int | None,
        reason: str,
    ) -> Result:
        seq = self._record("refused", page, changes, body, actor, at, cause, reason)
        return Result(False, seq, reason)

    def _write(
        self,
        page: str,
        changes: dict[str, Any],
        body: str | None,
        actor: str,
        at: str,
        cause: int | None,
        depth: int,
    ) -> Result:
        def refuse(reason: str) -> Result:
            return self._refuse(page, changes, body, actor, at, cause, reason)

        if depth > MAX_DEPTH:
            return refuse(f"cycle: reactions nested deeper than {MAX_DEPTH}")
        try:
            result = apply(self._load(page) or Page(), changes, body)
        except ShapeError as exc:
            return refuse(f"shape: {exc}")
        reason = self._rule_reason(page, result)
        if reason:
            return refuse(reason)
        seq = self._record("write", page, changes, body, actor, at, cause, None)
        self._store(page, result)
        self._react(page, result, seq, at, depth)
        return Result(True, seq)

    def _rule_reason(self, name: str, page: Page) -> str | None:
        scope = {"page": page.fields, "size": len(serialize(page).encode("utf-8"))}
        seen = {name}
        space, owner = page, name
        while True:
            for rule in space.rules:
                try:
                    held = holds(rule, scope)
                except RuleError as exc:
                    return f"rule: {rule} (from {owner}) failed to evaluate: {exc}"
                if not held:
                    return f"rule: {rule} (from {owner}) is false"
            if not space.within:
                return None
            owner = space.within
            if owner in seen:
                return f"rule: within chain loops back to {owner}"
            seen.add(owner)
            found = self._load(owner)
            if found is None:
                return f"rule: space {owner} does not exist"
            space = found

    def _react(self, source: str, written: Page, seq: int, at: str, depth: int) -> None:
        for watcher in sorted(p.stem for p in self.pages_dir.glob("*.md")):
            for entry in (self._load(watcher) or Page()).watch:
                if entry["on"] != source:
                    continue
                current = self._load(watcher) or Page()
                scope = {"other": written.fields, "page": current.fields}
                try:
                    if not holds(entry["when"], scope):
                        continue
                    changes = {k: evaluate(v, scope) for k, v in entry["set"].items()}
                    unchanged = serialize(apply(current, changes, None)) == serialize(current)
                except (RuleError, ShapeError) as exc:
                    reason = f"watch: {entry['when']} (on {watcher}) failed: {exc}"
                    self._refuse(watcher, {}, None, watcher, at, seq, reason)
                    continue
                if not unchanged:
                    self._write(watcher, changes, None, watcher, at, seq, depth + 1)
