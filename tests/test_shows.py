"""A space says how it shows its members: in what order and how many."""

import pytest

from conky import Vault, arch
from conky.page import MEMBERS_CAP, Page, ShapeError, apply, resolve_text

from .conftest import AT, git

EMBED = "![[den#members]]"


def desk(shows: object, count: int = 3) -> dict[str, Page]:
    """Return a space and members whose weight is their number and whose body names it."""
    den = Page(None, [], [], {} if shows is None else {"shows": shows}, "")
    found = {"den": den}
    for i in range(count):
        found[f"n{i}"] = Page("den", [], [], {"weight": i}, f"note {i}")
    return found


def test_a_space_that_does_not_show_lists_by_name_at_the_cap() -> None:
    lines = resolve_text(EMBED, desk(None, MEMBERS_CAP + 2)).splitlines()
    assert lines[:3] == ["n0: note 0", "n1: note 1", "n10: note 10"]
    assert len(lines) == MEMBERS_CAP + 1 and lines[-1] == "(2 more not shown)"
    assert resolve_text(EMBED, desk({}, 4)) == resolve_text(EMBED, desk(None, 4))


@arch.holds("law.embed.shows")
def test_a_space_that_shows_orders_by_first_and_cuts_to_most() -> None:
    shown = resolve_text(EMBED, desk({"most": 2, "first": "page.weight"}, 4))
    assert shown == "n3: note 3\nn2: note 2\n(2 more not shown)"
    tied = resolve_text(EMBED, desk({"first": "text.size()"}, 3))
    assert tied.splitlines() == ["n0: note 0", "n1: note 1", "n2: note 2"]


def test_a_member_first_cannot_score_comes_after_the_scored() -> None:
    found = desk({"first": "page.weight"}, 3)
    found["a"] = Page("den", [], [], {"weight": "heavy"}, "")
    found["b"] = Page("den", [], [], {}, "")
    shown = resolve_text(EMBED, found).splitlines()
    assert shown == ["n2: note 2", "n1: note 1", "n0: note 0", "a", "b"]


@pytest.mark.parametrize(
    "shows",
    [
        {"most": 0},
        {"most": MEMBERS_CAP + 1},
        {"most": True},
        {"first": "other.weight"},
        {"first": "page.weight +"},
        {"first": 3},
        {"least": 1},
        "most",
    ],
)
def test_a_wrong_shows_is_refused_with_what_to_write(shows: object) -> None:
    with pytest.raises(ShapeError) as refused:
        apply(Page(None, [], [], {}, ""), {"shows": shows}, None)
    assert len(str(refused.value)) > 30


@arch.holds("law.embed.shows")
def test_reading_a_space_that_shows_writes_nothing(vault: Vault) -> None:
    ok = vault.write("den", {"shows": {"first": "page.weight"}}, None, actor="alice", at=AT)
    assert ok.ok
    for name, weight in (("a", 1), ("b", 2)):
        assert vault.write(name, {"within": "den", "weight": weight}, None, actor="alice", at=AT).ok
    before = git(vault.path, "rev-parse", "HEAD")
    text = vault.write("reader", {}, EMBED, actor="alice", at=AT)
    assert text.ok
    mark = git(vault.path, "rev-parse", "HEAD")
    assert vault.read("reader").body.splitlines() == ["b", "a"]
    assert git(vault.path, "rev-parse", "HEAD") == mark != before
