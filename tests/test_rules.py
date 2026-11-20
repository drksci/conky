"""Text functions in the rule language: what a playbook cannot say, the examples and the limits."""

import pytest

from conky import rules
from conky.rules import RuleError, evaluate


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
