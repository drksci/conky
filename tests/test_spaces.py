"""A page may be within several spaces: precedence, rules, joining, leaving and rebuilding."""

import pytest

from conky import Vault, arch
from conky.page import Page, parse, serialize

from .conftest import AT


def w(vault: Vault, page: str, changes: dict, body: str | None = None):
    return vault.write(page, changes, body, actor="alice", at=AT)


def climb(vault: Vault) -> None:
    """A camp, a tent in it, a den in it, a hall and a choir, each handing down a limit."""
    w(vault, "camp", {"limit": 9, "note": "camp"})
    w(vault, "tent", {"within": "camp", "limit": 2})
    w(vault, "den", {"within": "camp"})
    w(vault, "hall", {"limit": 7, "tone": "hall"})
    w(vault, "choir", {"limit": 4, "tone": "choir"})


@arch.holds("law.context.down")
def test_the_space_listed_first_wins_among_a_pages_own_spaces(vault: Vault) -> None:
    climb(vault)
    assert vault._context("x", ["hall", "choir"])["limit"] == 7
    assert vault._context("x", ["choir", "hall"])["limit"] == 4
    assert vault._context("x", ["choir", "hall"])["tone"] == "choir"


@arch.holds("law.context.down")
def test_a_nearer_space_beats_a_farther_one_whatever_the_order(vault: Vault) -> None:
    climb(vault)
    assert vault._context("x", ["den", "tent"])["limit"] == 2
    assert vault._context("x", ["tent", "den"])["limit"] == 2
    assert vault._context("x", ["den", "tent"])["note"] == "camp"


@arch.holds("law.context.down")
def test_a_space_reached_by_two_paths_counts_at_its_nearest_distance(vault: Vault) -> None:
    climb(vault)
    assert vault._context("x", ["camp", "tent"])["limit"] == 9
    assert vault._context("x", ["tent", "camp"])["limit"] == 2
    assert [d for _, _, d in vault._above("x", ["tent", "camp"])] == [1, 1]


def test_a_list_of_one_is_stored_as_the_name_and_an_empty_list_as_no_space(vault: Vault) -> None:
    w(vault, "den", {})
    assert w(vault, "kid", {"within": ["den"]}).ok
    assert vault.read("kid").within == "den"
    assert "within: den\n" in (vault.pages_dir / "kid.md").read_text(encoding="utf-8")
    assert w(vault, "kid", {"within": []}).ok
    assert vault.read("kid").within is None
    assert parse(serialize(Page(["a", "b"]))).within == ["a", "b"]


def test_a_list_of_one_is_the_same_as_the_name_for_rules(vault: Vault) -> None:
    w(vault, "den", {"rules": [{"each": "!has(page.cups) || page.cups >= 0"}]})
    assert w(vault, "kid", {"within": ["den"], "cups": 1}).ok
    assert not w(vault, "kid", {"cups": -1}).ok
    assert not w(vault, "twin", {"within": "den", "cups": -1}).ok


def test_each_space_is_judged_once_when_two_paths_lead_to_it(vault: Vault) -> None:
    w(vault, "camp", {"rules": [{"each": "!has(page.cups) || page.cups >= 0"}]})
    w(vault, "tent", {"within": "camp"})
    w(vault, "den", {"within": "camp"})
    result = w(vault, "kid", {"within": ["tent", "den"], "cups": -1})
    assert not result.ok and result.reason is not None
    assert result.reason.count("(from camp)") == 1
    assert [o for o, _, _ in vault._above("kid", ["tent", "den"])] == ["tent", "den", "camp"]


@arch.holds("law.rule.tighten")
def test_joining_is_refused_by_the_space_joined(vault: Vault) -> None:
    w(vault, "choir", {"rules": [{"each": "!has(page.cups) || page.cups <= 5"}]})
    w(vault, "den", {})
    assert w(vault, "kid", {"within": "den", "cups": 9}).ok
    result = w(vault, "kid", {"within": ["den", "choir"]})
    assert not result.ok and "(from choir)" in (result.reason or "")
    assert vault.read("kid").within == "den"


@arch.holds("law.rule.tighten")
def test_leaving_is_refused_by_the_space_left_and_a_move_by_both(vault: Vault) -> None:
    w(vault, "club", {"rules": [{"each": "size <= 60"}]})
    w(vault, "gate", {"rules": [{"each": "!has(page.badge)"}]})
    w(vault, "street", {})
    assert w(vault, "kid", {"within": ["club", "street"]}, "short").ok
    long = "x" * 100
    left = w(vault, "kid", {"within": "street"}, long)
    assert not left.ok and "(from club)" in (left.reason or "")
    still = w(vault, "kid", {"within": ["club", "street"]}, long)
    assert not still.ok and "(from club)" in (still.reason or "")
    joined = w(vault, "kid", {"within": ["street", "gate"], "badge": 1}, "short")
    assert not joined.ok and "(from gate)" in (joined.reason or "")
    moved = w(vault, "kid", {"within": ["street", "gate"]}, "short")
    assert moved.ok
    vault.verify()


def test_a_missing_space_in_a_list_is_refused_as_a_single_one_is(vault: Vault) -> None:
    w(vault, "den", {})
    one = w(vault, "kid", {"within": "nowhere"})
    several = w(vault, "kid", {"within": ["den", "nowhere"]})
    assert not one.ok and not several.ok
    assert "space nowhere does not exist" in (several.reason or "")


def test_a_write_by_an_answer_cannot_join_a_page_to_several_spaces(vault: Vault) -> None:
    w(vault, "den", {})
    w(vault, "choir", {})
    other = vault._breach("kid", None, Page(["den", "choir"]), "den")
    assert other is not None and "not a list" in other
    assert vault._breach("kid", None, Page("den"), "den") is None
    assert vault._breach("kid", Page(["den", "choir"]), Page("den"), "den") is not None


def test_the_vault_verifies_and_rebuilds_with_several_spaces(vault: Vault) -> None:
    climb(vault)
    w(vault, "den", {"rules": [{"each": "!has(page.cups) || page.cups >= 0"}]})
    assert w(vault, "kid", {"within": ["den", "choir", "hall"], "cups": 2}).ok
    assert not w(vault, "kid", {"cups": -2}).ok
    vault.verify()
    before = vault.read("kid")
    vault.rebuild()
    vault.verify()
    assert vault.read("kid") == before
    assert before.within == ["den", "choir", "hall"]


@pytest.mark.parametrize("within", [["a", "a"], ["a", 1], 5, {"a": 1}])
def test_a_wrong_within_is_a_shape_refusal_with_what_to_write(vault: Vault, within) -> None:
    result = w(vault, "kid", {"within": within})
    assert not result.ok and (result.reason or "").startswith("shape")
    assert "within" in (result.reason or "")
