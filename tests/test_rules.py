"""The rule language: its text functions, what an expression costs and what it gives back."""

import resource
import subprocess
import sys
import time

import pytest

from conky import arch, rules
from conky.rules import RuleError, evaluate

from .conftest import AT


@pytest.mark.parametrize(
    ("expression", "expected"),
    [
        ("'a,b,c'.split(',')", ["a", "b", "c"]),
        ("'hello hello hello'.split(' ', 2)", ["hello", "hello hello"]),
        ("'abc'.split('')", ["a", "b", "c"]),
        ("'tacocat'.substring(4)", "cat"),
        ("'tacocat'.substring(0, 4)", "taco"),
        ("'hello mellow'.indexOf('ello', 2)", 7),
        ("'hello'.indexOf('z')", -1),
        ("'  x '.trim()", "x"),
        ("'TacoCÆt'.lowerAscii()", "tacocÆt"),
        ("'hello hello'.replace('he', 'we', 1)", "wello hello"),
        ("['a', 'b'].join('/')", "a/b"),
        ("'x=1 y=2.5'.captures('x=(\\d+) y=([0-9.]+)')", ["1", "2.5"]),
        ("'x=1'.captures('x=\\d')", ["x=1"]),
        ("'x=1'.captures('z')", []),
        ("double('x=2.5'.captures('x=(.*)')[0])", 2.5),
        ("'**a** and **b**'.capturesAll('\\*\\*(.+?)\\*\\*')", ["a", "b"]),
        ("'a1 b22'.capturesAll('\\d+')", ["1", "22"]),
        ("'a1 b22'.capturesAll('(\\w)(\\d)')", ["a", "b"]),
        ("'x'.capturesAll('z')", []),
        ("'**a**'.capturesAll('\\*\\*(.+?)\\*\\*').join('; ')", "a"),
        ("replace('a-b', '-', '+')", "a+b"),
    ],
)
def test_examples(expression, expected):
    assert evaluate(expression, {}) == expected


@pytest.mark.parametrize(
    "expression",
    [
        "'a'.substring(3)",
        "'abc'.substring(2, 1)",
        "'abc'.indexOf('a', -1)",
        "'a'.captures('(')",
        "'a'.captures('x=(\\d+)')[0]",
        "'a'.capturesAll('(')",
        "'a'.capturesAll('" + "a" * (rules.MAX_PATTERN + 1) + "')",
        "x.capturesAll('a')",
        "'a'.captures('" + "a" * (rules.MAX_PATTERN + 1) + "')",
        "x.trim()",
        "x.split(',')",
        "x.replace('a', 'aa')",
    ],
)
def test_bad_input_is_a_rule_error(expression):
    with pytest.raises(RuleError):
        evaluate(expression, {"x": "a" * (rules.MAX_TEXT + 1)})


def test_a_result_over_the_limit_is_an_error():
    with pytest.raises(RuleError):
        evaluate("x.replace('a', 'aa')", {"x": "a" * (rules.MAX_TEXT - 1)})


def test_text_at_the_limit_is_accepted():
    assert evaluate("x.trim().size()", {"x": "a" * rules.MAX_TEXT}) == rules.MAX_TEXT


CHOICES = "\n".join(f"Choice number {n}" for n in range(57))
CHOOSES = (
    "event.by != 'ada' || !has(page.next) || page.can.split('\\n').exists(c, "
    "c.lowerAscii() == page.next.split('\\n')[0].trim().lowerAscii())"
)


def bounded(code: str, seconds: int = 60, megabytes: int = 1024) -> str:
    """Run code in a fresh interpreter that is stopped at a time and a memory limit."""

    def limit() -> None:
        size = megabytes * 1024 * 1024
        resource.setrlimit(resource.RLIMIT_AS, (size, size))

    done = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        timeout=seconds,
        preexec_fn=limit,
        check=False,
    )
    return done.stdout.strip() or done.stderr.strip().splitlines()[-1]


def test_a_list_where_every_item_fails_is_judged_in_bounded_time_and_memory():
    code = (
        "from conky.rules import RuleError, evaluate\n"
        f"scope = {{'page': {{'can': {CHOICES!r}}}, 'event': {{'by': 'ada'}}}}\n"
        "try:\n"
        "    print(evaluate(\"page.can.split('\\\\n').exists(c, c == page.next)\", scope))\n"
        "except RuleError:\n"
        "    print('refused')\n"
    )
    assert bounded(code) == "refused"


def test_a_page_with_a_long_list_of_choices_is_written_and_judged(tmp_path):
    code = (
        "from pathlib import Path\n"
        "from conky import Vault\n"
        f"vault = Vault.init(Path({str(tmp_path / 'vault')!r}), Path({str(tmp_path / 'keys')!r}))\n"
        "def w(changes, actor):\n"
        f"    return vault.write('door', changes, None, actor=actor, at={AT!r})\n"
        f"first = w({{'can': {CHOICES!r}, 'rules': [{CHOOSES!r}]}}, 'bob')\n"
        "chosen = w({'next': 'choice NUMBER 56\\nand on'}, 'ada')\n"
        "refused = w({'next': 'the window'}, 'ada')\n"
        "print(first.ok, chosen.ok, refused.ok, refused.reason.split(':')[0])\n"
    )
    assert bounded(code) == "True True False rule"


@arch.holds("law.rule.bounded")
def test_a_rule_costs_no_more_than_the_items_it_reads():
    seen: list[str] = []

    def terms(text: str) -> list[str]:
        seen.append(text)
        return []

    items = {"page": {"items": [f"item {n}" for n in range(400)]}}
    began = time.perf_counter()
    assert evaluate("page.items.exists(i, terms(i).size() == 0)", items, terms) is True
    assert seen == ["item 0"]
    seen.clear()
    assert evaluate("page.items.all(i, terms(i).size() == 1)", items, terms) is False
    assert seen == ["item 0"]
    seen.clear()
    assert evaluate("page.items.exists(i, terms(i).size() == 1)", items, terms) is False
    assert len(seen) == 400
    for macro in ("exists", "all"):
        with pytest.raises(RuleError) as failed:
            evaluate(f"page.items.{macro}(i, i == page.gone)", items)
        assert len(str(failed.value)) < 400
    assert time.perf_counter() - began < 5


@arch.holds("law.rule.bounded")
def test_a_decided_or_and_and_evaluate_nothing_more():
    seen: list[str] = []

    def terms(text: str) -> list[str]:
        seen.append(text)
        return []

    assert evaluate("true || terms('a').size() == 0", {}, terms) is True
    assert evaluate("false && terms('a').size() == 0", {}, terms) is False
    assert seen == []
    assert evaluate("false || terms('a').size() == 0", {}, terms) is True
    assert seen == ["a"]


@pytest.mark.parametrize(
    ("expression", "expected"),
    [
        ("page.gone == 1 || true", True),
        ("true || page.gone == 1", True),
        ("page.gone == 1 && false", False),
        ("false && page.gone == 1", False),
        ("[1, 2].exists(n, n / (n - 1) == 2)", True),
        ("[1, 2].all(n, n / (n - 1) == 7)", False),
        ("[].exists(n, n == 1)", False),
        ("[].all(n, n == 1)", True),
        ("{'a': 1, 'b': 2}.exists(k, k == 'b')", True),
        ("{'a': 1, 'b': 2}.all(k, k == 'b')", False),
    ],
)
def test_or_and_and_keep_the_standard_answer_beside_an_error(expression, expected):
    assert evaluate(expression, {"page": {}}) is expected


@pytest.mark.parametrize(
    "expression",
    [
        "page.gone == 1 || false",
        "false || page.gone == 1",
        "page.gone == 1 && true",
        "1 || false",
        "[1, 2].exists(n, n / (n - 1) == 7)",
        "[1, 2].all(n, n / (n - 1) == 2)",
        "page.gone.exists(n, n == 1)",
    ],
)
def test_an_error_nothing_decides_is_still_an_error(expression):
    with pytest.raises(RuleError):
        evaluate(expression, {"page": {}})


@pytest.mark.parametrize(
    ("expression", "expected"),
    [
        ("('\\n' + page.can + '\\n').contains('\\nb\\n')", True),
        ("(page.can + 'c').endsWith('c')", True),
        ("page.can + '!'", "a\nb!"),
        ("(page.list + ['c']).size()", 3),
        ("page.list + ['c']", ["a", "b", "c"]),
    ],
)
def test_joined_text_and_joined_lists_keep_their_methods(expression, expected):
    assert evaluate(expression, {"page": {"can": "a\nb", "list": ["a", "b"]}}) == expected


@pytest.mark.parametrize(
    ("expression", "expected"),
    [
        ("0.0 - page.distance", -2.5),
        ("page.distance + 1.0", 3.5),
        ("page.distance * 2.0", 5.0),
        ("page.distance / 2.0", 1.25),
        ("-page.distance", -2.5),
        ("[1.5, 2.5].map(x, x * 2.0)", [3.0, 5.0]),
        ("(page.distance - 0.5) * 2.0 > 3.0", True),
        ("page.steps - 1", 2),
    ],
)
def test_arithmetic_on_numbers_with_a_fraction_gives_a_number(expression, expected):
    found = evaluate(expression, {"page": {"distance": 2.5, "steps": 3}})
    assert found == expected and type(found) is type(expected)


@pytest.mark.parametrize("sign", ["+", "-", "*", "/"])
def test_a_whole_number_and_a_fraction_do_not_mix_on_either_side(sign):
    scope = {"page": {"distance": 2.5, "steps": 3}}
    for expression in (f"page.steps {sign} page.distance", f"page.distance {sign} page.steps"):
        with pytest.raises(RuleError):
            evaluate(expression, scope)
    assert evaluate(f"double(page.steps) {sign} page.distance", scope) is not None
    assert evaluate(f"page.steps {sign} 2", scope) is not None
