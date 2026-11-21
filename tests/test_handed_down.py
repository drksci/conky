"""A space hands down reactions: an `each` watch entry is a reflex every page within has."""

from conky import Vault, arch
from conky.page import parse, serialize

from .conftest import AT
from .test_pages import history, refusals


def w(vault: Vault, page: str, changes: dict, body: str | None = None):
    return vault.write(page, changes, body, actor="alice", at=AT)


def hand(on: str = "bell", when: str = "has(page.cups)", **put: str) -> dict:
    return {"each": {"on": on, "when": when, "set": put or {"rang": "other.n"}}}


@arch.holds("law.reflex.down")
def test_every_page_within_a_space_reacts_as_if_it_carried_the_entry(vault: Vault) -> None:
    w(vault, "bell", {"n": 1})
    w(vault, "desk", {"watch": [hand()]})
    w(vault, "note-a", {"within": "desk", "cups": 1})
    w(vault, "note-b", {"within": "desk", "cups": 2})
    assert w(vault, "bell", {"n": 7}).ok
    assert vault.read("note-a").fields["rang"] == 7
    assert vault.read("note-b").fields["rang"] == 7
    assert "rang" not in vault.read("desk").fields
    assert not refusals(vault)
    vault.verify()
    before = vault.read("note-a")
    vault.rebuild()
    vault.verify()
    assert vault.read("note-a") == before


def test_the_reaction_is_the_members_write_caused_by_the_one_it_answered(vault: Vault) -> None:
    w(vault, "bell", {"n": 1})
    w(vault, "desk", {"watch": [hand()]})
    w(vault, "note", {"within": "desk", "cups": 1})
    rung = w(vault, "bell", {"n": 2})
    assert rung.ok
    last = history(vault)[-1][1]
    assert last["Cause"] == rung.id and last["Page"] == "note"


def test_a_member_without_the_fields_the_entry_reads_is_passed_over(vault: Vault) -> None:
    w(vault, "bell", {"n": 1})
    w(vault, "desk", {"watch": [hand()]})
    w(vault, "plain", {"within": "desk"})
    w(vault, "note", {"within": "desk", "cups": 1})
    assert w(vault, "bell", {"n": 2}).ok
    assert "rang" not in vault.read("plain").fields
    assert vault.read("note").fields["rang"] == 2
    assert not refusals(vault)


def test_a_page_outside_the_space_is_untouched(vault: Vault) -> None:
    w(vault, "bell", {"n": 1})
    w(vault, "desk", {"watch": [hand()]})
    w(vault, "stray", {"cups": 1})
    assert w(vault, "bell", {"n": 2}).ok
    assert "rang" not in vault.read("stray").fields


@arch.holds("law.reflex.down", "law.space.theatre")
def test_a_page_reacts_by_its_own_entries_then_each_space_nearest_outward(vault: Vault) -> None:
    def put(digit: int) -> dict:
        return hand(when="has(page.trail)", trail=f"page.trail * 10 + {digit}")

    w(vault, "bell", {"n": 1})
    w(vault, "theatre", {"watch": [put(4)]})
    w(vault, "camp", {"watch": [put(9)]})
    w(vault, "hall", {"within": "camp", "watch": [put(3)]})
    w(vault, "den", {"within": "hall", "watch": [put(2)]})
    own = {"on": "bell", "when": "true", "set": {"trail": "page.trail * 10 + 1"}}
    w(vault, "kid", {"within": "den", "trail": 0, "watch": [own]})
    assert w(vault, "bell", {"n": 2}).ok
    assert vault.read("kid").fields["trail"] == 12394


def test_a_space_reached_by_two_paths_hands_its_entry_down_once(vault: Vault) -> None:
    w(vault, "bell", {"n": 1})
    w(vault, "camp", {"watch": [hand(when="has(page.t)", t="page.t + 1")]})
    w(vault, "tent", {"within": "camp"})
    w(vault, "den", {"within": "camp"})
    w(vault, "kid", {"within": ["tent", "den", "camp"], "t": 0})
    assert w(vault, "bell", {"n": 2}).ok
    assert vault.read("kid").fields["t"] == 1


def test_a_space_does_not_carry_what_it_hands_down(vault: Vault) -> None:
    w(vault, "bell", {"n": 1})
    w(vault, "desk", {"t": 0, "watch": [hand(when="has(page.t)", t="page.t + 1")]})
    assert w(vault, "bell", {"n": 2}).ok
    assert vault.read("desk").fields["t"] == 0


def test_a_handed_down_entry_hears_a_relation_relative_to_the_member(vault: Vault) -> None:
    w(vault, "desk", {"watch": [hand(on="within", when="has(page.heard)", heard="other_name")]})
    w(vault, "club", {"within": "desk", "heard": ""})
    w(vault, "kid", {"within": "club"})
    assert vault.read("club").fields["heard"] == "kid"
    assert "heard" not in vault.read("kid").fields


def test_a_watch_entry_without_each_is_the_pages_own_and_binds_no_other(vault: Vault) -> None:
    w(vault, "bell", {"n": 1})
    w(vault, "desk", {"watch": [{"on": "bell", "when": "true", "set": {"rang": "other.n"}}]})
    w(vault, "note", {"within": "desk"})
    assert w(vault, "bell", {"n": 2}).ok
    assert vault.read("desk").fields["rang"] == 2
    assert "rang" not in vault.read("note").fields


def test_an_each_entry_is_stored_and_read_back_as_written() -> None:
    text = "---\nwatch:\n- each:\n    on: bell\n    when: 'true'\n    set:\n      a: '1'\n---\n"
    page = parse(text)
    assert serialize(page) == text
    assert page.watch == [{"each": {"on": "bell", "when": "true", "set": {"a": "1"}}}]


def test_a_fan_out_of_twenty_members_settles(vault: Vault) -> None:
    w(vault, "bell", {"n": 0})
    w(vault, "desk", {"watch": [hand(when="has(page.t)", t="page.t + 1")]})
    for i in range(20):
        w(vault, f"m{i:02}", {"within": "desk", "t": 0})
    assert w(vault, "bell", {"n": 1}).ok
    assert [vault.read(f"m{i:02}").fields["t"] for i in range(20)] == [1] * 20
    vault.verify()


def test_a_handed_down_entry_that_feeds_itself_stops_at_the_depth_limit(vault: Vault) -> None:
    w(vault, "desk", {"watch": [hand(on="m0", when="has(page.t)", t="page.t + 1")]})
    w(vault, "m0", {"within": "desk", "t": 0})
    assert w(vault, "m0", {"t": 5}).ok
    assert any("cycle" in found["Reason"] for found in refusals(vault))
    vault.verify()
