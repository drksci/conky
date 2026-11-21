"""An expression laid out in lines: pure, deterministic, and never broken inside a word."""

from __future__ import annotations

import pytest
from bench.expression import lines, tokens

LONG = [
    "terms(space.heard).filter(t, terms(text).contains(t)).size()",
    "page.amount > 3 && page.name == 'a  b' || space.cash - page.amount >= 20 && page.ok",
    "page.cash > 10 ? 'a long string of words here' : page.low + page.high * 2",
    "page.heard.trim().lowerAscii().endsWith('?') && page.said.size() < 4000",
]


def test_a_short_expression_is_one_line() -> None:
    assert lines("page.amount <= space.cash - 20") == ["page.amount <= space.cash - 20"]
    assert lines("  page.a\n  + 1 ") == ["page.a + 1"]
    assert lines("") == []


def test_breaks_come_before_logic_then_ternary_arms_then_chained_calls() -> None:
    assert lines(LONG[0]) == [
        "terms(space.heard)",
        "  .filter(t, terms(text).contains(t))",
        "  .size()",
    ]
    assert lines(LONG[1]) == [
        "page.amount > 3",
        "  && page.name == 'a  b'",
        "  || space.cash - page.amount >= 20",
        "  && page.ok",
    ]
    assert lines(LONG[2]) == [
        "page.cash > 10",
        "  ? 'a long string of words here'",
        "  : page.low + page.high * 2",
    ]


@pytest.mark.parametrize("text", LONG)
def test_lines_give_the_text_back_and_split_no_token(text: str) -> None:
    out = lines(text, width=24)
    assert out == lines(text, width=24)  # deterministic
    assert "".join(x.strip() for x in out).replace(" ", "") == text.replace(" ", "")
    words = [t for t in tokens(text) if not t.isspace()]
    flat = [t for line in out for t in tokens(line.strip()) if not t.isspace()]
    assert flat == words  # no string, number or name is cut
    assert all(x.startswith("  ") for x in out[1:]) and not out[0].startswith(" ")


def test_a_line_with_nowhere_to_break_is_left_whole() -> None:
    name = "page." + "a" * 50
    assert lines(name, width=10) == [name]
