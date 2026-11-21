"""A rule can see who is acting: `event` in rules, and `within(NAME, SPACE)` for roles."""

import pytest

from conky import Vault, arch
from conky.page import Terms
from conky.rules import RuleError, evaluate

from .conftest import AT
from .test_pages import refusals


def w(vault: Vault, page: str, changes: dict, actor: str = "alice", body: str | None = None):
    return vault.write(page, changes, body, actor=actor, at=AT)


@arch.holds("law.rule.who")
def test_a_field_can_be_restricted_to_one_actor_and_the_refusal_is_recorded(vault: Vault) -> None:
    rule = {"each": "event.by == 'owner' || !has(page.price)"}
    assert w(vault, "shop", {"rules": [rule]}, "owner").ok
    assert w(vault, "bread", {"within": "shop", "price": 3}, "owner").ok
    refused = w(vault, "bread", {"price": 1}, "alice")
    assert not refused.ok and "(from shop)" in (refused.reason or "")
    assert refusals(vault)[-1]["Page"] == "bread"
    assert vault.read("bread").fields["price"] == 3
    assert w(vault, "bread", {"price": 4}, "owner").ok


@arch.holds("law.rule.who")
def test_a_role_rule_admits_a_member_and_stops_when_the_member_leaves(vault: Vault) -> None:
    assert w(vault, "staff", {}).ok and w(vault, "club", {}).ok
    assert w(vault, "bob", {"within": "staff"}).ok
    assert w(vault, "shop", {"rules": [{"each": "within(event.by, 'staff')"}]}).ok
    assert w(vault, "till", {"within": "shop", "cash": 1}, "bob").ok
    assert not w(vault, "till", {"cash": 2}, "carol").ok
    assert not w(vault, "till", {"cash": 2}, "alice").ok
    assert w(vault, "till", {"cash": 3}, "bob").ok
    assert w(vault, "bob", {"within": "club"}).ok
    assert not w(vault, "till", {"cash": 4}, "bob").ok
    assert vault.read("till").fields["cash"] == 3


@arch.holds("law.rule.who")
def test_the_theatre_can_say_who_may_write_its_own_fields_and_every_page(vault: Vault) -> None:
    theatre = {
        "rules": ["event.by == 'alice'", {"each": "event.by == 'alice' || !has(page.motto)"}],
    }
    assert w(vault, "theatre", theatre, "alice").ok
    assert not w(vault, "theatre", {"motto": "hush"}, "bob").ok
    assert w(vault, "theatre", {"motto": "hush"}, "alice").ok
    assert w(vault, "den", {"motto": "mine"}, "alice").ok
    assert not w(vault, "den", {"motto": "yours"}, "bob").ok
    assert not w(vault, "den", {"other": 1}, "bob").ok
    assert w(vault, "scrap", {"n": 1}, "bob").ok


@arch.holds("law.rule.who")
def test_within_is_false_for_a_name_that_is_not_a_page_and_true_through_a_chain(
    vault: Vault,
) -> None:
    assert w(vault, "crew", {}).ok and w(vault, "staff", {"within": "crew"}).ok
    assert w(vault, "bob", {"within": "staff"}).ok
    known = Terms(vault._all)
    assert known.within("bob", "crew") and known.within("bob", "staff")
    assert not known.within("crew", "bob") and not known.within("ghost", "crew")
    assert not known.within("bob", "bob")
    assert evaluate("within('bob', 'crew')", {}, known) is True
    with pytest.raises(RuleError):
        evaluate("within('bob', 'crew')", {})


def test_a_rule_may_read_the_fields_of_event_and_no_others(vault: Vault) -> None:
    assert w(vault, "den", {"rules": ["event.kind == 'write' && event.reason == ''"]}).ok
    assert not w(vault, "den", {"rules": ["event.nope == 1"]}).ok
