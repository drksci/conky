"""A page is known by its phrases: text that uses one links to the page, and a condition can ask."""

import pytest

from conky import Vault, arch
from conky.page import Page, Terms, links
from conky.rules import RuleError, evaluate

from .conftest import AT


def desk() -> dict[str, Page]:
    return {
        "okafor": Page(None, [], [], {"aka": ["Mrs Okafor", "the landlady"]}, ""),
        "rent": Page(None, [], [], {"aka": ["rent"]}, ""),
        "plain": Page(None, [], [], {}, "Mrs Okafor"),
    }


@pytest.mark.parametrize(
    ("text", "found"),
    [
        ("mrs okafor", ["okafor"]),
        ("MRS \t OKAFOR", ["okafor"]),
        ("Mrs Okafor's", ["okafor"]),
        ("Mrs Okafor\u2019s", ["okafor"]),
        ("Mrs Okaforish", []),
        ("Mrs Okafors", []),
        ("okafor", []),
        ("the landlady, who owes rent.", ["okafor", "rent"]),
        ("current", []),
    ],
)
def test_a_phrase_is_recognised_as_whole_words(text: str, found: list[str]) -> None:
    assert Terms(desk)(text) == found


def test_a_page_does_not_link_to_itself_by_its_phrases() -> None:
    pages = desk()
    page = Page(None, [], [], {"aka": ["Mrs Okafor"]}, "Mrs Okafor and [[rent]]")
    assert links(page, Terms(lambda: pages), "okafor") == {"rent"}
    assert links(page, Terms(lambda: pages), "other") == {"okafor", "rent"}


@arch.holds("law.link.known")
def test_a_vault_with_no_phrases_links_only_by_brackets() -> None:
    page = Page(None, [], [], {}, "Mrs Okafor and [[rent]]")
    assert links(page, Terms(lambda: {"a": Page(), "b": Page()})) == {"rent"}
    assert links(page) == {"rent"}


def test_the_phrases_are_read_once_per_pass() -> None:
    asked = []

    def load() -> dict[str, Page]:
        asked.append(1)
        return desk()

    terms = Terms(load)
    assert asked == []
    terms("a"), terms("b"), terms("c")
    assert asked == [1]


def test_terms_is_a_function_of_the_pages_when_it_is_called() -> None:
    known = Terms(desk)
    assert evaluate("terms(text)", {"text": "the landlady"}, known) == ["okafor"]
    assert evaluate("terms(text).size()", {"text": "nothing"}, known) == 0
    with pytest.raises(RuleError):
        evaluate("terms(text)", {"text": "the landlady"})


@arch.holds("law.link.known")
def test_a_write_that_uses_a_phrase_tells_its_watchers_and_the_vault_verifies(vault: Vault) -> None:
    watch = [{"on": "link", "when": "true", "set": {"n": "page.n + 1"}}]
    fields = {"aka": ["Mrs Okafor"], "n": 0, "watch": watch}
    assert vault.write("okafor", fields, None, actor="alice", at=AT).ok
    assert vault.write("note", {}, "Mrs Okafor is late", actor="alice", at=AT).ok
    assert vault.read("okafor").fields["n"] == 1
    assert vault.read("note").body.strip() == "Mrs Okafor is late"
    vault.verify()
    vault.rebuild()
    vault.verify()
    assert vault.read("okafor").fields["n"] == 1
