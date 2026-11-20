"""Pages: Markdown with YAML frontmatter, serialised deterministically."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Any

import yaml

from conky import arch
from conky.errors import BadInput

RESERVED = arch.constant(
    ("within", "rules", "watch"),
    "reserved key",
    "conky.page.RESERVED",
    "slot.key",
    "Keys of a page's frontmatter that are not fields.",
    doc="vocabulary.md#reserved-keys",
)
WATCH_KEYS = arch.constant(
    ("on", "when", "set", "ask"),
    "watch key",
    "conky.page.WATCH_KEYS",
    "slot.watch",
    "Keys of a watch entry.",
    doc="vocabulary.md#watch-keys",
)
ASK_KEYS = arch.constant(
    ("prompt", "into", "provider", "otherwise", "writes"),
    "ask key",
    "conky.page.ASK_KEYS",
    "slot.ask",
    "Keys of an ask.",
    doc="vocabulary.md#ask-keys",
)
NAME = re.compile(r"^[a-z0-9][a-z0-9_-]{0,63}$")
EMBED = re.compile(r"!\[\[([^\]#]+)(?:#([^\]]+))?\]\]")


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


@arch.part(
    "part.page",
    "layer.history",
    "Markdown with frontmatter, serialised the same way every time.",
    doc="vault-format.md#pages",
)
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
        and set(entry) <= set(WATCH_KEYS)
        and isinstance(entry["on"], str)
        and NAME.match(entry["on"])
        and isinstance(entry["when"], str)
        and (_set_ok(entry["set"]) if "set" in entry else _ask_ok(entry["ask"]))
    )
    if not ok:
        raise ShapeError(
            "watch entries need on (page name), when (text) and either set (field: text) "
            "or ask (prompt, with into or writes or both, and optional provider and otherwise)"
        )


def _set_ok(value: Any) -> bool:
    return isinstance(value, dict) and all(
        isinstance(k, str) and isinstance(v, str) for k, v in value.items()
    )


def _ask_ok(value: Any) -> bool:
    return (
        isinstance(value, dict)
        and "prompt" in value
        and bool({"into", "writes"} & set(value))
        and set(value) <= set(ASK_KEYS)
        and all(isinstance(v, str) for v in value.values())
        and bool(NAME.match(value.get("provider", "x")))
        and bool(NAME.match(value.get("writes", "x")))
        and bool(value.get("into", "x"))
    )


@arch.change(
    "place.page.field",
    "Fields, body, `within`, `rules` and `watch`, only by a write.",
    doc="vault-format.md#pages",
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
        elif key == MEMBERS:
            raise ShapeError("members is computed from the pages within a space: use another name")
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


@arch.law(
    "law.data.three",
    "Data is a document, a table or a stream, and a change of shape is a forward re-projection.",
    doc="../decisions/0010-no-debt-no-down-migrations.md",
)
@arch.data(
    "data.document",
    "A page: Markdown with frontmatter, small, in the present tense.",
    doc="vault-format.md#pages",
)
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


def _split(text: str) -> tuple[str, str]:
    """Return the frontmatter text and the body of serialised Markdown."""
    if not text.startswith("---\n"):
        raise BadInput("page does not start with frontmatter")
    rest = text[4:]
    if rest.startswith("---\n"):
        return "", rest[4:]
    end = rest.find("\n---\n")
    if end < 0:
        raise BadInput("frontmatter is not closed")
    return rest[: end + 1], rest[end + 5 :]


def given(text: str) -> tuple[dict[str, Any], str | None]:
    """Read a page that someone gave as text: the keys it names, and its body if it has one.

    The keys are changes to apply, so a key the text leaves out stays as it is. A body is
    returned only when it holds text. Raises ShapeError saying what is wrong.
    """
    try:
        raw, body = _split(text)
        head = load_value(raw) or {}
    except BadInput as exc:
        raise ShapeError(
            f"{exc}: start it with a --- line and close the frontmatter with another"
        ) from exc
    except yaml.YAMLError as exc:
        reason = str(exc).splitlines()[0] if str(exc) else "it cannot be read"
        raise ShapeError(f"the frontmatter is not valid YAML ({reason}): correct it") from exc
    if not isinstance(head, dict) or not all(isinstance(k, str) for k in head):
        raise ShapeError("the frontmatter must be keys with values, each key text")
    try:
        json.dumps(head)
    except (TypeError, ValueError) as exc:
        raise ShapeError(f"values must be plain data: {exc}") from exc
    return head, (body if body.strip() else None)


@arch.law(
    "law.vault.golden",
    "The vault format is held stable by a golden vault that every version reads.",
    doc="../decisions/0012-rust-core-planned.md",
)
def parse(text: str) -> Page:
    """Parse serialised Markdown into a page."""
    raw, body = _split(text)
    head = load_value(raw) or {}
    fields = {k: v for k, v in head.items() if k not in RESERVED}
    return Page(head.get("within"), head.get("rules") or [], head.get("watch") or [], fields, body)


MEMBERS = "members"
MEMBERS_CAP = arch.constant(
    20,
    "members cap",
    "conky.page.MEMBERS_CAP",
    "slot.key",
    "Most lines an embedded list of members shows before it counts the rest.",
    doc="vault-format.md#pages",
)


def _within(name: str, space: str, lookup: dict[str, Page]) -> bool:
    """Return whether the page name lies within space, directly or through spaces."""
    seen: set[str] = set()
    found = lookup.get(name)
    while found is not None and found.within and found.within not in seen:
        if found.within == space:
            return True
        seen.add(found.within)
        found = lookup.get(found.within)
    return False


def _members_text(space: str, lookup: dict[str, Page]) -> str | None:
    """Return one line per page within space, sorted by name, or None when there is none."""
    names = sorted(n for n in lookup if _within(n, space, lookup))
    lines = []
    for name in names[:MEMBERS_CAP]:
        first = next((ln.strip() for ln in lookup[name].body.splitlines() if ln.strip()), "")
        lines.append(f"{name}: {first}" if first else name)
    if len(names) > MEMBERS_CAP:
        lines.append(f"({len(names) - MEMBERS_CAP} more not shown)")
    return "\n".join(lines) or None


def _embed_text(name: str, field: str | None, lookup: dict[str, Page]) -> str | None:
    """Return the text an embed names in lookup, or None when there is nothing to embed.

    With the part `members` it is the list of the pages within a space that exists. With a
    field it is that field's value. Without one it is the body. A missing page, a missing
    field, an empty body and a space with no members give None.
    """
    target = lookup.get(name)
    if target is None:
        return None
    if field == MEMBERS:
        return _members_text(name, lookup)
    if field is None:
        return target.body or None
    if field not in target.fields:
        return None
    value = target.fields[field]
    if isinstance(value, str):
        return value
    if isinstance(value, bool):
        return "true" if value else "false"
    return "" if value is None else json.dumps(value, sort_keys=True, ensure_ascii=False)


def embedded(text: str, lookup: dict[str, Page]) -> list[str]:
    """Return the pages whose fields or body text embeds, each once, in order of first use."""
    names: list[str] = []
    for found in EMBED.finditer(text):
        name = found.group(1)
        if _embed_text(name, found.group(2), lookup) is not None and name not in names:
            names.append(name)
    return names


@arch.part(
    "part.embed",
    "layer.history",
    "`![[page]]`, `![[page#field]]` or `![[space#members]]`, resolved on read and in prompts.",
    doc="vault-format.md#pages",
)
def resolve_text(text: str, lookup: dict[str, Page]) -> str:
    """Return text with each embed replaced by the field or body it names in lookup."""
    return EMBED.sub(lambda m: _embed_text(m.group(1), m.group(2), lookup) or "", text)


@arch.step(
    "flow.page.read",
    3,
    "lane.runtime",
    "lane.page",
    "replace each embed by the field or body it names",
)
def resolve(page: Page, lookup: dict[str, Page]) -> Page:
    """Return a copy of page whose embeds are replaced by field values from lookup."""
    return Page(page.within, page.rules, page.watch, page.fields, resolve_text(page.body, lookup))
