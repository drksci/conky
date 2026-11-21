"""The theatre is a page: when a vault has one, every other page lies within it."""

import re

import pytest

from conky import Vault, arch
from conky.cli import main
from conky.page import CONTEXT_CAP, Page, above, parse, resolve_text

from .conftest import AT, git
from .test_pages import refusals


def w(vault: Vault, page: str, changes: dict, body: str | None = None):
    return vault.write(page, changes, body, actor="alice", at=AT)


def house(vault: Vault, **changes: object) -> None:
    assert w(vault, "theatre", changes, "No page here is rude.").ok


def test_a_vault_without_the_page_has_no_outermost_space(vault: Vault) -> None:
    assert w(vault, "den", {"limit": 2}).ok
    assert vault._above("den", None) == []
    assert vault._context("den", None) == {}
    assert not vault._inside(None, "theatre", "den")
    assert resolve_text("![[theatre#members]]", {"den": Page()}) == ""


@arch.holds("law.rule.tighten", "law.space.theatre")
def test_each_rule_of_the_theatre_binds_every_write_and_names_it(vault: Vault) -> None:
    assert w(vault, "camp", {}).ok and w(vault, "den", {"within": "camp"}).ok
    house(vault, rules=[{"each": "size < 400"}])
    assert w(vault, "bare", {"n": 1}).ok
    for page in ("bare", "den"):
        refused = w(vault, page, {"text": "x" * 500})
        assert not refused.ok
        assert "(from theatre)" in (refused.reason or "")
        assert refusals(vault)[-1]["From"] == "theatre"


def test_a_plain_rule_of_the_theatre_binds_only_the_theatre(vault: Vault) -> None:
    assert w(vault, "bare", {"n": 5}).ok
    house(vault, rules=["page.n == 1"], n=1)
    assert w(vault, "bare", {"n": 6}).ok


def test_an_each_rule_is_tried_on_every_page_when_it_is_written(vault: Vault) -> None:
    assert w(vault, "bare", {"n": 5}).ok
    house(vault)
    refused = w(vault, "theatre", {"rules": [{"each": "page.n < 3"}]})
    assert not refused.ok and "for bare, within it" in (refused.reason or "")


def test_a_page_that_names_no_space_is_refused_by_a_rule_of_the_house(vault: Vault) -> None:
    house(vault, rules=[{"each": "page.n < 2"}])
    assert not w(vault, "stray", {"n": 5}).ok
    assert w(vault, "stray", {"n": 1}).ok


@arch.holds("law.context.down")
def test_the_theatre_fields_are_context_at_the_lowest_precedence(vault: Vault) -> None:
    house(vault, limit=9, tone="grey")
    assert w(vault, "camp", {"limit": 3}).ok
    assert w(vault, "den", {"within": "camp"}).ok
    assert vault._context("den", "camp") == {"limit": 3, "tone": "grey"}
    assert vault._context("bare", None) == {"limit": 9, "tone": "grey"}
    assert vault._context("theatre", None) == {}


def test_the_theatre_is_listed_once_and_last_however_it_is_named() -> None:
    found = {"theatre": Page(), "camp": Page("theatre"), "den": Page(["theatre", "camp"])}
    order = [(o, d) for o, _, d in above("den", found["den"].within, found.get)]
    assert order == [("camp", 1), ("theatre", 2)]
    assert above("theatre", None, found.get) == []


@arch.holds("law.embed.context")
def test_the_theatre_body_is_the_last_block_of_a_context() -> None:
    found = {
        "theatre": Page(None, [], [], {}, "House rules."),
        "camp": Page(None, [], [], {}, "Camp words."),
        "den": Page("camp"),
        "bare": Page(),
    }
    shown = resolve_text("![[den#context]]", found)
    assert shown == "camp says:\nCamp words.\n\ntheatre says:\nHouse rules."
    assert resolve_text("![[bare#context]]", found) == "theatre says:\nHouse rules."
    assert resolve_text("![[theatre#context]]", found) == ""


def test_the_cap_cuts_the_middle_and_the_theatre_keeps_its_place() -> None:
    found = {"theatre": Page(None, [], [], {}, "House rules."), "keeper": Page("s0")}
    for i in range(CONTEXT_CAP + 2):
        found[f"s{i}"] = Page(f"s{i + 1}", [], [], {}, f"word {i}")
    shown = resolve_text("![[keeper#context]]", found).split("\n\n")
    assert len(shown) == CONTEXT_CAP + 1
    assert shown[0] == "s0 says:\nword 0"
    assert shown[-2] == "(3 more spaces not shown)"
    assert shown[-1] == "theatre says:\nHouse rules."


def test_the_members_of_the_theatre_are_every_other_page(vault: Vault) -> None:
    house(vault)
    assert w(vault, "den", {}, "A den.").ok and w(vault, "hall", {"within": "den"}).ok
    lines = resolve_text("![[theatre#members]]", vault._all()).splitlines()
    assert lines == ["den: A den.", "hall"]


@arch.holds("law.pressure.notice")
def test_the_theatre_hears_every_write_and_every_refusal_once(vault: Vault) -> None:
    heard = [
        {"on": "within", "when": "true", "set": {"writes": "page.writes + 1"}},
        {"on": "refusal", "when": "true", "set": {"refusals": "page.refusals + 1"}},
    ]
    house(vault, watch=heard, writes=0, refusals=0, rules=[{"each": "size < 400"}])
    assert w(vault, "bare", {"n": 1}).ok and w(vault, "den", {"within": "bare"}).ok
    assert vault.read("theatre").fields["writes"] == 2
    assert not w(vault, "bare", {"text": "x" * 500}).ok
    assert vault.read("theatre").fields["refusals"] == 1


def test_naming_the_theatre_changes_nothing_and_leaving_it_is_not_possible(vault: Vault) -> None:
    house(vault, rules=[{"each": "size < 400"}])
    assert w(vault, "den", {"within": "theatre"}).ok
    assert [o for o, _, _ in vault._above("den", "theatre")] == ["theatre"]
    assert w(vault, "den", {"within": None}).ok
    assert [o for o, _, _ in vault._above("den", None)] == ["theatre"]
    assert not w(vault, "den", {"text": "x" * 500}).ok
    assert len(refusals(vault)) == 1


def test_a_change_of_within_judges_the_theatre_once(vault: Vault) -> None:
    house(vault, rules=[{"each": "size < 400"}])
    assert w(vault, "camp", {}).ok and w(vault, "den", {"within": "camp"}).ok
    assert w(vault, "den", {"within": None}).ok
    assert w(vault, "den", {"within": "camp"}).ok
    assert refusals(vault) == []


def test_an_answer_may_add_to_the_house_and_the_house_cannot_be_loosened(vault: Vault) -> None:
    house(vault, rules=[{"each": "size < 400"}])
    before = vault.read("theatre")
    assert vault._bind("theatre", before, {"rules": [{"each": "size < 300"}]}, None) is None
    assert vault._bind("theatre", before, {"rules": []}, "words") is not None
    assert vault._breach("den", None, Page(), "theatre") is not None
    assert vault._breach("den", None, Page("theatre"), "theatre") is None


def test_the_name_travels_and_the_identity_is_the_first_commit(
    vault: Vault, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.chdir(vault.path)
    assert main(["theatre"]) == 0
    out = capsys.readouterr().out
    assert "identity: appears with the first write" in out
    assert re.search(rf"theatre: {vault.path.name}\.local\n", out)
    house(vault, name="lemon")
    short = git(vault.path, "rev-list", "--max-parents=0", "main").strip()[:8]
    assert main(["theatre"]) == 0
    out = capsys.readouterr().out
    assert f"theatre: lemon-{short}.local" in out
    assert f"identity: {short}" in out and "name: lemon (theatre page)" in out
    (vault.path / "marionette.md").write_text("---\nname: pear\n---\n", encoding="utf-8")
    assert main(["theatre"]) == 0
    assert f"theatre: pear-{short}.local" in capsys.readouterr().out


def test_verify_and_rebuild_agree_on_a_vault_with_a_theatre(vault: Vault) -> None:
    house(vault, name="lemon", rules=[{"each": "size < 400"}])
    assert w(vault, "den", {"n": 1}).ok and not w(vault, "den", {"text": "x" * 500}).ok
    before = {p.name: p.read_text() for p in vault.pages_dir.glob("*.md")}
    vault.verify()
    vault.rebuild()
    vault.verify()
    assert before == {p.name: p.read_text() for p in vault.pages_dir.glob("*.md")}
    assert parse(before["theatre.md"]).within is None


def test_a_theatre_page_cannot_lie_within_a_space(vault: Vault) -> None:
    assert w(vault, "camp", {}).ok
    refused = w(vault, "theatre", {"within": "camp"})
    assert not refused.ok and "outermost space" in (refused.reason or "")


def test_the_theatre_page_is_not_within_itself_or_told_of_its_own_write(vault: Vault) -> None:
    heard = [{"on": "within", "when": "true", "set": {"writes": "page.writes + 1"}}]
    house(vault, watch=heard, writes=0)
    assert w(vault, "theatre", {"tone": "grey"}).ok
    assert vault.read("theatre").fields["writes"] == 0
