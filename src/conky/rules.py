"""Rules: pure CEL expressions evaluated with cel-python."""

from __future__ import annotations

import operator
import re
from collections.abc import Callable, Iterable
from typing import Any

import celpy
from celpy import celtypes
from celpy.evaluation import CELEvalError, Evaluator

from conky import arch, voice

MAX_TEXT = 65536
MAX_PATTERN = 256

# Text functions. The names and shapes of all but `captures` and `capturesAll` follow the CEL
# strings extension (cel-go ext/README.md, "Strings"); those two are conky's own, because the
# standard regex extension (`regex.extract`, `regex.extractAll`) needs optional types, a single
# group and a namespaced name that cel-python cannot register as a method. Each is pure and
# bounded by MAX_TEXT and MAX_PATTERN; a failure raises ValueError, which evaluation turns into
# a RuleError.

_FUNCTIONS: dict[str, Any] = {}


def _text(*values: str) -> None:
    for value in values:
        if len(value) > MAX_TEXT:
            raise ValueError(f"text is longer than {MAX_TEXT} characters")


def _function(name: str, meaning: str):
    def register(fn):
        _FUNCTIONS[name] = fn
        doc = "rules-and-reactions.md#text-functions"
        return arch.part(f"part.rule.{name.lower()}", "layer.reflex", meaning, doc=doc)(fn)

    return register


def _str(value: str) -> celtypes.StringType:
    return celtypes.StringType(value)


def _strs(values: list[str]) -> celtypes.ListType:
    return celtypes.ListType([_str(v) for v in values])


@_function("split", "Split text on a separator, with an optional limit on the pieces.")
def _split(text: str, sep: str, limit: int = -1) -> celtypes.ListType:
    _text(text, sep)
    if limit == 0:
        return _strs([])
    if sep == "":
        chars = list(text)
        if 0 < limit < len(chars):
            chars = [*chars[: limit - 1], "".join(chars[limit - 1 :])]
        return _strs(chars)
    return _strs(text.split(sep, limit - 1 if limit > 0 else -1))


@_function("substring", "Take the characters from a start to an optional end position.")
def _substring(text: str, start: int, end: int | None = None) -> celtypes.StringType:
    _text(text)
    stop = len(text) if end is None else int(end)
    if not 0 <= start <= stop <= len(text):
        raise ValueError("substring positions are out of range")
    return _str(text[int(start) : stop])


@_function("indexOf", "The position of a substring from an optional start, or -1.")
def _index_of(text: str, find: str, start: int = 0) -> celtypes.IntType:
    _text(text, find)
    if start < 0:
        raise ValueError("indexOf start is negative")
    return celtypes.IntType(text.find(find, int(start)) if start <= len(text) else -1)


@_function("trim", "Remove leading and trailing whitespace.")
def _trim(text: str) -> celtypes.StringType:
    _text(text)
    return _str(text.strip())


@_function("lowerAscii", "Lower-case the ASCII letters only.")
def _lower_ascii(text: str) -> celtypes.StringType:
    _text(text)
    return _str("".join(c.lower() if c.isascii() else c for c in text))


@_function("replace", "Replace occurrences of a substring, with an optional limit.")
def _replace(text: str, find: str, by: str, limit: int = -1) -> celtypes.StringType:
    _text(text, find, by)
    out = text.replace(find, by, int(limit)) if limit >= 0 else text.replace(find, by)
    _text(out)
    return _str(out)


@_function("join", "Join a list of text with an optional separator.")
def _join(items: list[str], sep: str = "") -> celtypes.StringType:
    _text(sep)
    out = sep.join(str(i) for i in items)
    _text(out)
    return _str(out)


def _search(text: str, pattern: str, first: bool) -> list[str]:
    _text(text)
    if len(pattern) > MAX_PATTERN:
        raise ValueError(f"pattern is longer than {MAX_PATTERN} characters")
    try:
        found = [re.search(pattern, text)] if first else list(re.finditer(pattern, text))
    except re.error as exc:
        raise ValueError(f"bad pattern: {exc}") from exc
    out: list[str] = []
    for m in found:
        if m is None:
            continue
        if not m.re.groups:
            out.append(m.group(0))
        elif first:
            out.extend(g or "" for g in m.groups())
        else:
            out.append(m.group(1) or "")
    return out


@_function("captures", "The groups of the first match of a pattern, else an empty list.")
def _captures(text: str, pattern: str) -> celtypes.ListType:
    return _strs(_search(text, pattern, True))


@_function("capturesAll", "The first group of every match of a pattern, else an empty list.")
def _captures_all(text: str, pattern: str) -> celtypes.ListType:
    return _strs(_search(text, pattern, False))


def _terms(known: Callable[[str], list[str]]) -> Callable[[str], celtypes.ListType]:
    def terms(text: str) -> celtypes.ListType:
        _text(text)
        return _strs(known(text))

    return terms


@arch.part(
    "part.rule.within",
    "layer.reflex",
    "Whether a named page lies within a space, so a space can say who may write.",
    doc="rules-and-reactions.md#who-may-write",
)
def _within(lies: Callable[[str, str], bool]) -> Callable[[str, str], celtypes.BoolType]:
    def within(name: str, space: str) -> celtypes.BoolType:
        _text(name, space)
        return celtypes.BoolType(lies(name, space))

    return within


def _typed(value: Any) -> Any:
    """Give a value an operator made its CEL type back, so it keeps its methods and can be kept."""
    if type(value) is str:
        return _str(value)
    if type(value) is list:
        return celtypes.ListType(value)
    if type(value) is float:
        return celtypes.DoubleType(value)
    return value


_MIXED = {celtypes.IntType, celtypes.DoubleType}


def _retyped(fn: Callable[[Any, Any], Any]) -> Callable[[Any, Any], Any]:
    def typed(left: Any, right: Any) -> Any:
        if {type(left), type(right)} == _MIXED:
            raise TypeError("a whole number and a number with a fraction do not mix")
        return _typed(fn(left, right))

    return typed


# cel-python maps the arithmetic operators to Python's own. `+`, `-` and `*` then give a plain
# Python value for two texts, two lists or two numbers with a fraction: one with no CEL methods,
# and one that cannot be given back as a result. A whole number beside a number with a fraction
# is an error in CEL, and Python's own takes it on one side and not the other, so it is refused
# on both.
_OPERATORS: dict[str, Any] = {
    "_+_": _retyped(operator.add),
    "_-_": _retyped(operator.sub),
    "_*_": _retyped(operator.mul),
    "_/_": _retyped(operator.truediv),
    "_%_": _retyped(operator.mod),
}


@arch.law(
    "law.rule.bounded",
    "A rule costs no more than the items it reads, and a decided `||`, `&&`, `exists` or `all` "
    "evaluates nothing more.",
    doc="rules-and-reactions.md#what-an-expression-costs",
)
def _decide(values: Iterable[Any], decisive: bool, tree: Any) -> Any:
    """Fold `||` (decisive true) or `&&` (decisive false) over values taken one at a time.

    The answer is CEL's: a decisive value wins whatever stands beside it, and otherwise an error
    or a value that is no boolean makes the whole an error. The first decisive value ends the
    fold, so nothing after it is evaluated, and an error is carried as it is and never quoted
    inside another.
    """
    failed: CELEvalError | None = None
    for value in values:
        if isinstance(value, celtypes.BoolType):
            if bool(value) is decisive:
                return value
        elif failed is None:
            if isinstance(value, CELEvalError):
                failed = value
            else:
                kind = type(value).__name__
                failed = CELEvalError(f"no such overload: {kind} is not true or false", tree=tree)
    return celtypes.BoolType(not decisive) if failed is None else failed


class _Judge(Evaluator):
    """cel-python's evaluator with `||`, `&&`, `exists` and `all` folded by `_decide`.

    The library evaluates both sides of `||` and `&&` and every item of `exists` and `all`
    before it combines them, and it combines two errors into one that quotes both, so a list in
    which every item fails makes a message that doubles with each item.
    """

    def sub_evaluator(self, ast: Any) -> Evaluator:
        return _Judge(ast, activation=self.activation)

    def _either(self, tree: Any, decisive: bool) -> Any:
        if len(tree.children) != 2:
            return self.visit_children(tree)[0]
        return _decide((self.visit(side) for side in tree.children), decisive, tree)

    def conditionalor(self, tree: Any) -> Any:
        return self._either(tree, True)

    def conditionaland(self, tree: Any) -> Any:
        return self._either(tree, False)

    def member_dot_arg(self, tree: Any) -> Any:
        if len(tree.children) != 3 or str(tree.children[1]) not in ("exists", "all"):
            return super().member_dot_arg(tree)
        items = self.visit(tree.children[0])
        if isinstance(items, CELEvalError):
            return items
        judge = self.build_ss_macro_eval(tree)
        return _decide(map(judge, items), str(tree.children[1]) == "exists", tree)


class _Runner(celpy.InterpretedRunner):
    def evaluate(self, context: Any) -> Any:
        return _Judge(ast=self.ast, activation=self.new_activation()).evaluate(context)


_ENV = celpy.Environment(runner_class=_Runner)


class RuleError(Exception):
    """An expression failed to parse, failed to evaluate or returned an unusable value."""


def _plain(value: Any) -> Any:
    if isinstance(value, celtypes.BoolType):
        return bool(value)
    if isinstance(value, celtypes.IntType | celtypes.UintType):
        return int(value)
    if isinstance(value, celtypes.DoubleType):
        return float(value)
    if isinstance(value, celtypes.StringType):
        return str(value)
    if isinstance(value, celtypes.ListType):
        return [_plain(v) for v in value]
    if isinstance(value, celtypes.MapType):
        return {str(k): _plain(v) for k, v in value.items()}
    if value is None or isinstance(value, celtypes.NullType):
        return None
    raise RuleError(f"result of type {type(value).__name__} cannot be stored")


RULE_NAMES = ("page", "space", "size", "text", "event", "asks")
WATCH_NAMES = (*RULE_NAMES, "other", "other_text", "other_size", "other_name")
EVENT_FIELDS = ("kind", "by", "reason", "id")
_BINDING = ("all", "exists", "exists_one", "map", "filter")


def _idents(node: Any) -> list[str]:
    return [str(t) for t in node.scan_values(lambda v: getattr(v, "type", "") == "IDENT")]


def _walk(node: Any, bound: frozenset[str], names: set[str], reads: list[tuple[str, str]]) -> None:
    """Collect the names an expression reads from outside itself, and each `name.field` read."""
    if not hasattr(node, "data"):
        return
    kids = node.children
    if node.data == "ident":
        if str(kids[0]) not in bound:
            names.add(str(kids[0]))
        return
    if node.data == "member_dot" and getattr(kids[0], "data", "") == "member":
        head = kids[0].children[0] if len(kids[0].children) == 1 else None
        found = head.children[0] if getattr(head, "data", "") == "primary" else None
        if getattr(found, "data", "") == "ident" and str(found.children[0]) not in bound:
            reads.append((str(found.children[0]), str(kids[1])))
    if node.data == "member_dot_arg" and str(kids[1]) in _BINDING and len(kids) == 3:
        _walk(kids[0], bound, names, reads)
        args = kids[2].children
        inner = bound | set(_idents(args[0])) if args else bound
        for arg in args[1:]:
            _walk(arg, inner, names, reads)
        return
    for kid in kids:
        _walk(kid, bound, names, reads)


def reads(expression: str) -> tuple[set[str], list[tuple[str, str]]]:
    """Return the names an expression reads and each field read off a name, as (name, field).

    Names come from the structure of the parsed expression, so nothing is evaluated. A variable
    bound by `all`, `exists`, `map` or `filter` is not a name read from outside. A syntax error
    raises RuleError.
    """
    try:
        tree = _ENV.compile(expression)
    except celpy.CELParseError as exc:
        raise RuleError(f"{expression} is not a valid expression") from exc
    names: set[str] = set()
    fields: list[tuple[str, str]] = []
    _walk(tree, frozenset(), names, fields)
    return names, fields


def _remarks(expression: str) -> list[str]:
    """Return the text of each `//` comment in an expression that parses, in order.

    A `//` inside a text literal is part of the text: the parsed tree says where each literal
    lies, and only slashes outside every one start a comment.
    """
    tree = _ENV.compile(expression)
    held = [(t.start_pos, t.end_pos) for t in tree.scan_values(lambda v: hasattr(v, "start_pos"))]
    found: list[str] = []
    at = expression.find("//")
    while at >= 0:
        if any(start <= at < end for start, end in held):
            at = expression.find("//", at + 2)
            continue
        end = expression.find("\n", at)
        end = len(expression) if end < 0 else end
        found.append(expression[at + 2 : end].strip())
        at = expression.find("//", end)
    return found


@arch.law(
    "law.rule.says",
    "A rule may say what to do instead in words after `//`, and a refusal for it gives those "
    "words where it would have quoted the rule.",
    doc="rules-and-reactions.md#a-rule-that-says-why",
)
def says(expression: str) -> str | None:
    """Return the words a rule carries after `//`, joined in order, or None when it has none."""
    try:
        return " ".join(remark for remark in _remarks(expression) if remark) or None
    except celpy.CELParseError:
        return None


def wordless(expression: str) -> bool:
    """Say whether a rule has `//` with no words after it, or words and no condition."""
    lines = [line.strip() for line in expression.splitlines() if line.strip()]
    if lines and all(line.startswith("//") for line in lines):
        return True
    try:
        return "" in _remarks(expression)
    except celpy.CELParseError:
        return False


def concerns(expression: str, scope: dict[str, Any]) -> bool:
    """Say whether an `each` rule speaks about this page: the page has every field it reads.

    A rule about payments reads `page.amount`. A page within the same space that has no amount
    is not a payment, so the rule has nothing to say about it and is not judged against it.
    """
    _, fields = reads(expression)
    page = scope.get("page", {})
    return all(field in page for name, field in fields if name == "page")


def check(expression: str, allowed: tuple[str, ...]) -> None:
    """Raise RuleError unless expression parses and reads only allowed names and event fields."""
    names, fields = reads(expression)
    for root, field in fields:
        if root == "event" and field not in EVENT_FIELDS:
            raise RuleError(voice.line("event-field", name=field, keys=", ".join(EVENT_FIELDS)))
    unknown = sorted(names - set(allowed))
    if unknown:
        raise RuleError(
            f"{expression} reads {', '.join(unknown)}, which is not here: "
            f"the names allowed are {', '.join(allowed)}"
        )


_HERE = {"page": "this page", "space": "the space", "other": "the page just written"}


def missing(expressions: list[str], scope: dict[str, Any]) -> str:
    """Say in plain words which field an expression read that its thing does not have.

    When another thing in scope has a field of that name, the reason names it as the one to read.
    """
    for expression in expressions:
        try:
            _, fields = reads(expression)
        except RuleError:
            continue
        for root, name in fields:
            held = scope.get(root)
            if not isinstance(held, dict) or name in held:
                continue
            elsewhere = [r for r in _HERE if r != root and name in (scope.get(r) or {})]
            if elsewhere:
                other = elsewhere[0]
                return voice.line(
                    "missing-elsewhere", root=root, name=name, where=_HERE[other], other=other
                )
            return voice.line("missing-guard", root=root, name=name)
    return voice.line("missing-unknown")


@arch.law(
    "law.rule.pure",
    "Rules and measures are pure: no clock, randomness or input and output.",
    doc="rules-and-reactions.md#expressions",
)
def evaluate(
    expression: str,
    variables: dict[str, Any],
    terms: Callable[[str], list[str]] | None = None,
) -> Any:
    """Evaluate expression with the given variables and return a plain Python value.

    With terms, the expression may call `terms(TEXT)`, which gives the sorted names of the pages
    the text uses a phrase of. When terms also has a `within(NAME, SPACE)` method, the expression
    may call `within(NAME, SPACE)`, which says whether the page NAME lies within SPACE. Both read
    the pages that exist when they are called and nothing else.
    """
    functions = {**_FUNCTIONS, **_OPERATORS}
    if terms is not None:
        functions["terms"] = _terms(terms)
        lies = getattr(terms, "within", None)
        if lies is not None:
            functions["within"] = _within(lies)
    try:
        program = _ENV.program(_ENV.compile(expression), functions=functions)
        result = program.evaluate({k: celpy.json_to_cel(v) for k, v in variables.items()})
    except (celpy.CELParseError, celpy.CELEvalError) as exc:
        raise RuleError(str(exc).strip().splitlines()[0] if str(exc).strip() else "error") from exc
    return _plain(result)


@arch.law(
    "law.rule.never",
    "Anything that must never happen is a rule the runtime evaluates.",
    doc="rules-and-reactions.md#expressions",
)
@arch.part(
    "part.rule",
    "layer.reflex",
    "A CEL expression judged before a write is kept.",
    doc="rules-and-reactions.md#expressions",
)
def holds(
    expression: str,
    variables: dict[str, Any],
    terms: Callable[[str], list[str]] | None = None,
) -> bool:
    """Return True only if expression evaluates to the boolean true."""
    return evaluate(expression, variables, terms) is True
