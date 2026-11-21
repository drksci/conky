"""Pages: Markdown with YAML frontmatter, serialised deterministically."""

from __future__ import annotations

import json
import re
from collections import deque
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

import yaml

from conky import arch, voice
from conky.errors import BadInput
from conky.rules import RULE_NAMES, WATCH_NAMES, RuleError, check, concerns, evaluate

RESERVED = arch.constant(
    ("within", "rules", "watch"),
    "reserved key",
    "conky.page.RESERVED",
    "slot.key",
    "Keys of a page's frontmatter that are not fields.",
    doc="vocabulary.md#reserved-keys",
)
WATCH_KEYS = arch.constant(
    ("on", "when", "set", "ask", "each"),
    "watch key",
    "conky.page.WATCH_KEYS",
    "slot.watch",
    "Keys of a watch entry, `each` being the wrapper of one a space hands down.",
    doc="vocabulary.md#watch-keys",
)
RELATIONS = arch.constant(
    ("within", "link", "refusal"),
    "watch relation",
    "conky.page.RELATIONS",
    "slot.watch",
    "Words for `on` that name a relation in place of a page.",
    doc="vocabulary.md#watch-relations",
)
LINK = re.compile(r"(?<!!)\[\[([^\]#|]+)(?:[#|][^\]]*)?\]\]")
ASK_KEYS = arch.constant(
    ("prompt", "into", "provider", "otherwise", "writes"),
    "ask key",
    "conky.page.ASK_KEYS",
    "slot.ask",
    "Keys of an ask.",
    doc="vocabulary.md#ask-keys",
)
NAME = re.compile(r"^[a-z0-9][a-z0-9_-]{0,63}$")
THEATRE = "theatre"
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

    within: str | list[str] | None = None
    rules: list[str | dict[str, str]] = field(default_factory=list)
    watch: list[dict[str, Any]] = field(default_factory=list)
    fields: dict[str, Any] = field(default_factory=dict)
    body: str = ""


def spaces(within: Any) -> list[str]:
    """Return the spaces a `within` names, in order: none, one name or a list of names."""
    if isinstance(within, str):
        return [within]
    if isinstance(within, list):
        return [name for name in within if isinstance(name, str)]
    return []


def home(within: Any) -> str | None:
    """Return the first of the spaces a `within` names, the page's home, or None."""
    return next(iter(spaces(within)), None)


def _check_within(value: Any) -> str | list[str] | None:
    """Return a `within` as it is stored, or raise ShapeError with what to write instead."""
    if value is None or (isinstance(value, str) and NAME.match(value)):
        return value
    if not isinstance(value, list):
        raise ShapeError(voice.line("within-shape"))
    for entry in value:
        if not (isinstance(entry, str) and NAME.match(entry)):
            raise ShapeError(voice.line("within-entry", entry=repr(entry)))
    if len(set(value)) != len(value):
        raise ShapeError(voice.line("within-repeat"))
    return value[0] if len(value) == 1 else (value or None)


def check_theatre(name: str, page: Page) -> None:
    """Raise ShapeError when the page named `theatre` is within a space or has a bad `name`."""
    if name != THEATRE:
        return
    if page.within is not None:
        raise ShapeError(voice.line("theatre-within"))
    given_name = page.fields.get("name")
    if given_name is not None and not (isinstance(given_name, str) and NAME.match(given_name)):
        raise ShapeError(voice.line("theatre-name", name=repr(given_name)))


def check_name(name: str) -> str:
    """Return name if it is a valid page or actor name, else raise BadInput."""
    if not isinstance(name, str) or not NAME.match(name):
        raise BadInput(f"invalid name {name!r}: use lowercase letters, digits, '-' and '_'")
    return name


def _check_watch(entry: Any) -> None:
    """Refuse a watch entry that is malformed, or reads a name a watch entry does not have.

    An entry may be wrapped as `{each: ENTRY}`, a reflex handed to the pages within a space.
    """
    if isinstance(entry, dict) and "each" in entry:
        inner = entry["each"]
        if set(entry) != {"each"} or not isinstance(inner, dict) or "each" in inner:
            raise ShapeError(voice.line("each-watch-shape"))
        entry = inner
    ok = (
        isinstance(entry, dict)
        and {"on", "when"} <= set(entry)
        and len(set(entry) & {"set", "ask"}) == 1
        and set(entry) <= set(WATCH_KEYS)
        and isinstance(entry["on"], str)
        and (entry["on"] in RELATIONS or NAME.match(entry["on"]))
        and isinstance(entry["when"], str)
        and (_set_ok(entry["set"]) if "set" in entry else _ask_ok(entry["ask"]))
    )
    if not ok:
        raise ShapeError(voice.line("watch-shape"))
    try:
        check(entry["when"], WATCH_NAMES)
        for value in entry.get("set", {}).values():
            check(value, WATCH_NAMES)
    except RuleError as exc:
        raise ShapeError(f"watch on {entry['on']}: {exc}") from exc


AKA = "aka"
AKA_MIN = 2


@arch.law(
    "law.link.known",
    "A page is known by the phrases it lists, and text that uses one counts as linking to it.",
    doc="../decisions/0044-a-page-is-known-by-its-phrases.md",
    roadmap="R41",
)
class Terms:
    """The phrases the pages of a vault are known by, built once from the pages when first asked.

    A phrase is recognised in a text when it occurs as whole words, compared without regard to
    case, with any run of whitespace standing for one space and a trailing possessive (`'s` or
    `’s`) allowed on its last word. A page's own name is not a phrase unless it is listed.
    """

    def __init__(self, load: Callable[[], dict[str, Page]]) -> None:
        self._load = load
        self._found: list[tuple[re.Pattern[str], str]] | None = None

    def _index(self) -> list[tuple[re.Pattern[str], str]]:
        if self._found is None:
            self._found = []
            for name, page in sorted(self._load().items()):
                phrases = page.fields.get(AKA)
                for phrase in phrases if isinstance(phrases, list) else []:
                    if not isinstance(phrase, str) or len(phrase.strip()) < AKA_MIN:
                        continue
                    words = r"\s+".join(re.escape(w) for w in phrase.split())
                    pattern = rf"(?<!\w){words}(?:['’]s)?(?!\w)"
                    self._found.append((re.compile(pattern, re.IGNORECASE), name))
        return self._found

    def __call__(self, text: str) -> list[str]:
        """Return the sorted names of the pages one of whose phrases the text uses."""
        return sorted({name for pattern, name in self._index() if pattern.search(text)})

    def within(self, name: str, space: str) -> bool:
        """Return whether a page called name exists and lies within space, by any path."""
        lookup = self._load()
        return name in lookup and _within(name, space, lookup)


def links(page: Page, terms: Terms | None = None, name: str = "") -> set[str]:
    """Return the names a page, called name, links to.

    These are the names its body and text fields write in brackets, and with terms every page
    whose phrases its body uses. A page does not link to itself by its phrases.
    """
    texts = [page.body, *(v for v in page.fields.values() if isinstance(v, str))]
    found = {m.group(1).strip() for text in texts for m in LINK.finditer(text)}
    if terms is not None:
        found |= {n for n in terms(page.body) if n != name}
    return found


def _check_budget(value: Any) -> None:
    """Raise ShapeError unless value is a mapping with `asks`, a whole number of zero or more."""
    asks = value.get("asks") if isinstance(value, dict) else None
    ok = isinstance(value, dict) and set(value) == set(BUDGET_KEYS)
    if not ok or isinstance(asks, bool) or not isinstance(asks, int) or asks < 0:
        raise ShapeError(voice.line("budget-shape", keys=", ".join(BUDGET_KEYS)))


def _check_aka(value: Any) -> None:
    """Refuse a `aka` that is not a list of phrases of at least two characters."""
    ok = (
        isinstance(value, list)
        and bool(value)
        and all(isinstance(p, str) and len(p.strip()) >= AKA_MIN for p in value)
    )
    if not ok:
        raise ShapeError(voice.line("aka-shape", least=AKA_MIN))


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
            within = _check_within(value)
        elif key == "rules":
            if value is None:
                value = []
            if not isinstance(value, list):
                raise ShapeError("rules must be a list")
            for entry in value:
                _check_rule(entry)
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
            raise ShapeError(voice.line("members-name"))
        elif key == CONTEXT:
            raise ShapeError(voice.line("context-name"))
        elif key == BUDGET:
            if value is None:
                fields.pop(key, None)
            else:
                _check_budget(value)
                fields[key] = value
        elif key == SHOWS:
            if value is not None:
                _check_shows(value)
            fields[key] = value
        elif key == AKA:
            if value is not None:
                _check_aka(value)
            fields[key] = value
        else:
            fields[key] = value
    result = Page(within, rules, watch, fields, page.body if body is None else body)
    return parse(serialize(result))


def _check_rule(entry: Any) -> None:
    """Refuse a rule entry that is not a condition, or reads a name a rule does not have."""
    if isinstance(entry, dict) and set(entry) == {"each"}:
        entry = entry["each"]
    if not isinstance(entry, str):
        raise ShapeError(voice.line("rule-shape", entry=repr(entry)))
    try:
        check(entry, RULE_NAMES)
    except RuleError as exc:
        raise ShapeError(str(exc)) from exc


def _watch_head(entry: dict[str, Any]) -> dict[str, Any]:
    if "each" in entry:
        return {"each": _watch_head(entry["each"])}
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
CONTEXT = "context"
ASKS = "asks"
BUDGET = "budget"
BUDGET_KEYS = arch.constant(
    ("asks",),
    "budget key",
    "conky.page.BUDGET_KEYS",
    "slot.key",
    "Keys of a page's `budget`: how many times the page may ask a model.",
    doc="vocabulary.md#budget-keys",
)
CONTEXT_CAP = arch.constant(
    5,
    "context cap",
    "conky.page.CONTEXT_CAP",
    "slot.key",
    "Most spaces whose words an embedded context shows before it counts the rest; "
    "the length of one space's words is not capped.",
    doc="vault-format.md#pages",
)
MEMBERS_CAP = arch.constant(
    20,
    "members cap",
    "conky.page.MEMBERS_CAP",
    "slot.key",
    "Most lines an embedded list of members shows before it counts the rest.",
    doc="vault-format.md#pages",
)


SHOWS = "shows"
SHOWS_KEYS = arch.constant(
    ("most", "first"),
    "shows key",
    "conky.page.SHOWS_KEYS",
    "slot.key",
    "Keys of a space's `shows`: how many members an embedded list shows and what orders them.",
    doc="vocabulary.md#shows-keys",
)
SHOWS_NAMES = ("page", "space", "text")


def _within(name: str, space: str, lookup: dict[str, Page]) -> bool:
    """Return whether the page name lies within space, directly or through spaces.

    Every page but the theatre lies within the page named `theatre`, when there is one.
    """
    if space == THEATRE and name != THEATRE and THEATRE in lookup:
        return True
    seen: set[str] = set()
    todo = spaces(lookup[name].within) if name in lookup else []
    while todo:
        found = todo.pop()
        if found == space:
            return True
        if found not in seen:
            seen.add(found)
            todo += spaces(lookup[found].within) if found in lookup else []
    return False


def _check_shows(value: Any) -> None:
    """Refuse a `shows` that is not a mapping of `most` and `first` with each in range."""
    ok = isinstance(value, dict) and set(value) <= set(SHOWS_KEYS)
    if not ok:
        raise ShapeError(voice.line("shows-shape", keys=", ".join(SHOWS_KEYS)))
    most = value.get("most", MEMBERS_CAP)
    if isinstance(most, bool) or not isinstance(most, int) or not 1 <= most <= MEMBERS_CAP:
        raise ShapeError(voice.line("shows-most", cap=MEMBERS_CAP))
    if "first" in value:
        try:
            if not isinstance(value["first"], str):
                raise RuleError(f"{value['first']!r} is not an expression")
            check(value["first"], SHOWS_NAMES)
        except RuleError as exc:
            raise ShapeError(voice.line("shows-first", reason=str(exc))) from exc


def _score(expression: str, member: Page, space: Page, terms: Terms) -> float | None:
    """Return what `first` makes of one member, or None when it is not a number."""
    scope = {"page": member.fields, "text": member.body, "space": space.fields}
    try:
        value = evaluate(expression, scope, terms)
    except RuleError:
        return None
    if isinstance(value, bool) or not isinstance(value, int | float) or value != value:
        return None
    return value


def _scores(space: str, names: list[str], lookup: dict[str, Page]) -> dict[str, float | None]:
    """Return what the `first` of space makes of each named member."""
    first = lookup[space].fields[SHOWS]["first"]
    terms = Terms(lambda: lookup)
    return {n: _score(first, lookup[n], lookup[space], terms) for n in names}


def _unordered(space: str, scores: dict[str, float | None], lookup: dict[str, Page]) -> list[str]:
    """Return the members `first` reads and gives no number for, as against those it passes by.

    A member that lacks a field `first` reads off `page` is not what the order is about, as an
    `each` rule is not about a page without the fields it reads. A member that has them all
    and still gets no number is a failure of the expression.
    """
    first = lookup[space].fields[SHOWS]["first"]
    read = [n for n in scores if concerns(first, {"page": lookup[n].fields})]
    return [n for n in read if scores[n] is None]


@arch.law(
    "law.embed.proven",
    "A `first` is tried on the members already within when it is written and lands only if it "
    "gives one of those it reads a number; a failure met on reading is said in what is shown.",
    doc="vault-format.md#pages",
)
def unshown(space: str, lookup: dict[str, Page]) -> str | None:
    """Return why the `first` of space cannot land: it reads members and scores none of them."""
    shows = lookup[space].fields.get(SHOWS)
    if not isinstance(shows, dict) or "first" not in shows:
        return None
    names = sorted(n for n in lookup if _within(n, space, lookup))
    scores = _scores(space, names, lookup)
    failed = _unordered(space, scores, lookup)
    if not failed or any(score is not None for score in scores.values()):
        return None
    return voice.line("shows-scores", space=space, name=failed[0])


@arch.law(
    "law.embed.shows",
    "A space says how its members are shown, and the order is worked out on reading, never stored.",
    doc="vault-format.md#pages",
    roadmap="R40",
)
def _members_text(space: str, lookup: dict[str, Page]) -> str | None:
    """Return one line per page within space, or None when there is none.

    The lines are sorted by name and cut at MEMBERS_CAP. A space that carries `shows` orders
    them by `first`, highest first, with ties and members it cannot score after by name, and
    cuts at `most`. A last line names the members `first` reads and gives no number for.
    Nothing is written: the order is worked out each time the embed is resolved.
    """
    names = sorted(n for n in lookup if _within(n, space, lookup))
    shows = lookup[space].fields.get(SHOWS)
    cap = MEMBERS_CAP
    failed: list[str] = []
    if isinstance(shows, dict):
        cap = shows.get("most", MEMBERS_CAP)
        if "first" in shows:
            scores = _scores(space, names, lookup)
            failed = _unordered(space, scores, lookup)
            names.sort(key=lambda n: (scores[n] is None, -(scores[n] or 0)))
    lines = []
    for name in names[:cap]:
        first = next((ln.strip() for ln in lookup[name].body.splitlines() if ln.strip()), "")
        lines.append(f"{name}: {first}" if first else name)
    if len(names) > cap:
        lines.append(f"({len(names) - cap} more not shown)")
    if failed:
        rest = f" and {len(failed) - 3} more" if len(failed) > 3 else ""
        named = ", ".join(failed[:3]) + rest
        lines.append(voice.line("shows-unordered", count=len(failed), names=named))
    return "\n".join(lines) or None


@arch.law(
    "law.space.theatre",
    "A vault with a page named theatre has every other page within it, last in the order of "
    "spaces, so its rules, words and reactions reach the whole vault; without the page nothing "
    "is outermost.",
    doc="../decisions/0051-the-theatre-is-a-page.md",
    roadmap="R43",
)
def above(
    name: str,
    within: Any,
    load: Callable[[str], Page | None],
    theatre: bool = True,
) -> list[tuple[str, Page | None, int]]:
    """Return the spaces above a page named name that is within `within`, each once.

    Each comes with its page (None when it does not exist) and its distance: a space the
    page names is at 1, the spaces it lies within at 2, and a space reached by two paths
    at the nearer. They are ordered nearest first, and among spaces at one distance by the
    order they were reached, which follows the order the page lists its spaces in. The
    page itself appears when a loop leads back to it, and is not climbed past.

    When there is a page named `theatre`, every page but that one lies within it, so it comes
    last, one step beyond the farthest space, however the page names it. Without `theatre` the
    spaces are only those the page names.
    """
    found: list[tuple[str, Page | None, int]] = []
    outer = load(THEATRE) if theatre and name != THEATRE else None
    queue = deque((space, 1) for space in spaces(within) if outer is None or space != THEATRE)
    seen: set[str] = set()
    while queue:
        space, distance = queue.popleft()
        if space in seen:
            continue
        seen.add(space)
        held = None if space == name else load(space)
        found.append((space, held, distance))
        if held is not None:
            queue.extend(
                (up, distance + 1) for up in spaces(held.within) if outer is None or up != THEATRE
            )
    if outer is not None:
        found.append((THEATRE, outer, max((d for _, _, d in found), default=0) + 1))
    return found


def _context_spaces(name: str, lookup: dict[str, Page]) -> list[tuple[str, str]]:
    """Return each space above a page with words, nearest first, as its name and its words."""
    return [
        (space, held.body.rstrip())
        for space, held, _ in above(name, lookup[name].within, lookup.get)
        if held is not None and held.body.strip()
    ]


def _shown(saying: list[tuple[str, str]]) -> tuple[list[tuple[str, str]], int]:
    """Return the spaces an embedded context shows and how many it leaves out.

    The nearest CONTEXT_CAP are shown. When the theatre speaks and the cap cuts, it keeps the last
    place and the cap cuts the middle, so the house rules are read whatever the nearer say.
    """
    if len(saying) <= CONTEXT_CAP:
        return saying, 0
    keep = CONTEXT_CAP - 1 if saying[-1][0] == THEATRE else CONTEXT_CAP
    return saying[:keep] + saying[-1:][: CONTEXT_CAP - keep], len(saying) - CONTEXT_CAP


def _context_text(name: str, lookup: dict[str, Page]) -> str | None:
    """Return what the spaces above a page say, nearest first, or None when they say nothing.

    Each space with a body gives `NAME says:` on a line and then the body as written, less its
    closing blank space, the blocks separated by a blank line. Only CONTEXT_CAP are shown, then
    a line counts the rest; the theatre, when it speaks, is always the last block shown. Nothing
    says who wrote a body. Nothing is written.
    """
    shown, left = _shown(_context_spaces(name, lookup))
    blocks = [f"{space} says:\n{body}" for space, body in shown]
    if left:
        count = f"({left} more spaces not shown)"
        blocks.insert(len(blocks) - (1 if shown[-1][0] == THEATRE else 0), count)
    return "\n\n".join(blocks) or None


def _embed_text(name: str, field: str | None, lookup: dict[str, Page]) -> str | None:
    """Return the text an embed names in lookup, or None when there is nothing to embed.

    With the part `members` it is the list of the pages within a space that exists. With `context`
    it is what the spaces above a page say. With a
    field it is that field's value. Without one it is the body. A missing page, a missing
    field, an empty body and a space with no members give None.
    """
    target = lookup.get(name)
    if target is None:
        return None
    if field == MEMBERS:
        return _members_text(name, lookup)
    if field == CONTEXT:
        return _context_text(name, lookup)
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
    """Return the pages whose fields or body text embeds, each once, in order of first use.

    An embed of a page's context names the spaces whose words it shows, not the page.
    """
    names: list[str] = []
    for found in EMBED.finditer(text):
        name = found.group(1)
        if _embed_text(name, found.group(2), lookup) is None:
            continue
        shown = [name]
        if found.group(2) == CONTEXT:
            shown = [space for space, _ in _shown(_context_spaces(name, lookup))[0]]
        names += [one for one in shown if one not in names]
    return names


@arch.part(
    "part.embed",
    "layer.history",
    "`![[page]]`, `![[page#field]]`, `![[space#members]]` or `![[page#context]]`, "
    "resolved on read and in prompts.",
    doc="vault-format.md#pages",
)
@arch.law(
    "law.embed.anonymous",
    "An embed shows a page's words and nothing about who wrote them.",
    doc="vault-format.md#pages",
)
@arch.law(
    "law.embed.context",
    "A prompt that embeds a page's context is told what its spaces say, so joining a space "
    "changes what a character is told and leaving it takes that away.",
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
