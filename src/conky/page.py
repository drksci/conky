"""Pages: Markdown with YAML frontmatter, serialised deterministically."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Any

import yaml

from conky.errors import BadInput

RESERVED = ("within", "rules", "watch")
NAME = re.compile(r"^[a-z0-9][a-z0-9_-]{0,63}$")
EMBED = re.compile(r"!\[\[([^\]#]+)#([^\]]+)\]\]")


def _bool_is_true_false(base: type) -> type:
    """Return base with YAML 1.2 booleans, so the key `on` stays text."""

    class Strict(base):  # type: ignore[valid-type, misc]
        pass

    tag = "tag:yaml.org,2002:bool"
    Strict.yaml_implicit_resolvers = {
        first: [(t, rx) for t, rx in entries if t != tag]
        for first, entries in base.yaml_implicit_resolvers.items()  # type: ignore[attr-defined]
    }
    Strict.add_implicit_resolver(tag, re.compile(r"^(?:true|false)$"), list("tf"))  # type: ignore[attr-defined]
    return Strict


_Loader = _bool_is_true_false(yaml.SafeLoader)
_Dumper = _bool_is_true_false(yaml.SafeDumper)


def load_value(text: str) -> Any:
    """Parse text as a YAML scalar or flow value, as page frontmatter does."""
    return yaml.load(text, Loader=_Loader)  # noqa: S506


class ShapeError(Exception):
    """A write would give a page a malformed reserved key or field."""


@dataclass
class Page:
    """One page: its space, rules, watches, own fields and body."""

    within: str | None = None
    rules: list[str] = field(default_factory=list)
    watch: list[dict[str, Any]] = field(default_factory=list)
    fields: dict[str, Any] = field(default_factory=dict)
    body: str = ""


def check_name(name: str) -> str:
    """Return name if it is a valid page or actor name, else raise BadInput."""
    if not isinstance(name, str) or not NAME.match(name):
        raise BadInput(f"invalid name {name!r}: use lowercase letters, digits, '-' and '_'")
    return name


def _check_watch(entry: Any) -> None:
    ok = (
        isinstance(entry, dict)
        and {"on", "when"} <= set(entry)
        and len(set(entry) & {"set", "ask"}) == 1
        and set(entry) <= {"on", "when", "set", "ask"}
        and isinstance(entry["on"], str)
        and NAME.match(entry["on"])
        and isinstance(entry["when"], str)
        and (_set_ok(entry["set"]) if "set" in entry else _ask_ok(entry["ask"]))
    )
    if not ok:
        raise ShapeError(
            "watch entries need on (page name), when (text) and either set (field: text) "
            "or ask (provider, prompt, into)"
        )


def _set_ok(value: Any) -> bool:
    return isinstance(value, dict) and all(
        isinstance(k, str) and isinstance(v, str) for k, v in value.items()
    )


def _ask_ok(value: Any) -> bool:
    return (
        isinstance(value, dict)
        and set(value) == {"provider", "prompt", "into"}
        and all(isinstance(v, str) for v in value.values())
        and bool(NAME.match(value["provider"]))
        and bool(value["into"])
    )


def apply(page: Page, changes: dict[str, Any], body: str | None) -> Page:
    """Return the page after changes and body, normalised through its serialised form."""
    within, rules, watch = page.within, list(page.rules), list(page.watch)
    fields = dict(page.fields)
    for key, value in changes.items():
        if not isinstance(key, str) or not key:
            raise ShapeError(f"field name {key!r} must be non-empty text")
        if key == "within":
            if value is not None and not (isinstance(value, str) and NAME.match(value)):
                raise ShapeError("within must be a page name")
            within = value
        elif key == "rules":
            if value is None:
                value = []
            if not isinstance(value, list) or not all(isinstance(r, str) for r in value):
                raise ShapeError("rules must be a list of text")
            rules = value
        elif key == "watch":
            if value is None:
                value = []
            if not isinstance(value, list):
                raise ShapeError("watch must be a list")
            for entry in value:
                _check_watch(entry)
            watch = value
        else:
            fields[key] = value
    result = Page(within, rules, watch, fields, page.body if body is None else body)
    return parse(serialize(result))


def _watch_head(entry: dict[str, Any]) -> dict[str, Any]:
    head = {"on": entry["on"], "when": entry["when"]}
    for part in ("set", "ask"):
        if part in entry:
            head[part] = dict(sorted(entry[part].items()))
    return head


def serialize(page: Page) -> str:
    """Return the page as Markdown: reserved keys, then fields by name, then the body."""
    head: dict[str, Any] = {}
    if page.within:
        head["within"] = page.within
    if page.rules:
        head["rules"] = page.rules
    if page.watch:
        head["watch"] = [_watch_head(w) for w in page.watch]
    for key in sorted(page.fields):
        head[key] = page.fields[key]
    text = ""
    if head:
        text = yaml.dump(
            head,
            Dumper=_Dumper,
            sort_keys=False,
            allow_unicode=True,
            default_flow_style=False,
            width=10**9,
        )
    body = page.body
    if body and not body.endswith("\n"):
        body += "\n"
    return f"---\n{text}---\n{body}"


def parse(text: str) -> Page:
    """Parse serialised Markdown into a page."""
    if not text.startswith("---\n"):
        raise BadInput("page does not start with frontmatter")
    rest = text[4:]
    if rest.startswith("---\n"):
        raw, body = "", rest[4:]
    else:
        end = rest.find("\n---\n")
        if end < 0:
            raise BadInput("frontmatter is not closed")
        raw, body = rest[: end + 1], rest[end + 5 :]
    head = load_value(raw) or {}
    fields = {k: v for k, v in head.items() if k not in RESERVED}
    return Page(head.get("within"), head.get("rules") or [], head.get("watch") or [], fields, body)


def resolve_text(text: str, lookup: dict[str, Page]) -> str:
    """Return text with each embed replaced by the field value it names in lookup."""

    def value_text(match: re.Match[str]) -> str:
        target = lookup.get(match.group(1))
        if target is None or match.group(2) not in target.fields:
            return ""
        value = target.fields[match.group(2)]
        if isinstance(value, str):
            return value
        if isinstance(value, bool):
            return "true" if value else "false"
        return "" if value is None else json.dumps(value, sort_keys=True, ensure_ascii=False)

    return EMBED.sub(value_text, text)


def resolve(page: Page, lookup: dict[str, Page]) -> Page:
    """Return a copy of page whose embeds are replaced by field values from lookup."""
    return Page(page.within, page.rules, page.watch, page.fields, resolve_text(page.body, lookup))
