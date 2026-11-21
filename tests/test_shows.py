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
    said = "(1 not ordered: first gives no number for a)"
    assert shown == ["n2: note 2", "n1: note 1", "n0: note 0", "a", "b", said]


def test_things_are_ordered_by_distance_nearest_first() -> None:
    found = {"den": Page(None, [], [], {"shows": {"first": "0.0 - page.distance"}}, "")}
    for name, distance in (("far", 9.5), ("near", 0.25), ("mid", 3.0)):
        found[name] = Page("den", [], [], {"distance": distance}, "")
    assert resolve_text(EMBED, found).splitlines() == ["near", "mid", "far"]


@arch.holds("law.embed.proven")
def test_a_first_that_fails_when_read_says_so_in_what_is_shown() -> None:
    found = desk({"first": "page.weight - 0.5"}, 5)
    found["z"] = Page("den", [], [], {}, "no weight")
    shown = resolve_text(EMBED, found).splitlines()
    assert shown[:6] == [f"n{i}: note {i}" for i in range(5)] + ["z: no weight"]
    assert shown[6] == "(5 not ordered: first gives no number for n0, n1, n2 and 2 more)"
    cut = resolve_text(EMBED, desk({"most": 1, "first": "page.weight - 0.5"}, 2)).splitlines()
    assert cut == [
        "n0: note 0",
        "(1 more not shown)",
        "(2 not ordered: first gives no number for n0, n1)",
    ]


@arch.holds("law.embed.proven")
def test_a_first_that_scores_no_member_it_reads_is_refused_when_written(vault: Vault) -> None:
    def w(page: str, changes: dict):
        return vault.write(page, changes, None, actor="alice", at=AT)

    assert w("den", {}).ok and w("a", {"within": "den", "weight": 1}).ok
    assert w("b", {"within": "den", "weight": 2}).ok and w("c", {"within": "den"}).ok
    for wrong in ("page.weight - 0.5", "page.weight > 1", "space.gone + page.weight"):
        refused = w("den", {"shows": {"first": wrong}})
        assert not refused.ok and refused.reason.startswith("shape: ")
        assert "den" in refused.reason and "double(page.FIELD)" in refused.reason
    assert "shows" not in vault.read("den").fields
    assert w("den", {"shows": {"first": "double(page.weight) - 0.5"}}).ok
    assert w("a", {"weight": "heavy"}).ok
    assert w("den", {"shows": {"most": 5, "first": "double(page.weight) - 0.5"}}).ok
    assert w("den", {"shows": {"first": "page.size"}}).ok


def test_a_first_written_before_any_member_is_accepted_and_speaks_when_read(vault: Vault) -> None:
    def w(page: str, changes: dict):
        return vault.write(page, changes, None, actor="alice", at=AT)

    assert w("den", {"shows": {"first": "page.weight - 0.5"}}).ok
    assert w("a", {"within": "den", "weight": 1}).ok
    assert vault.write("reader", {}, EMBED, actor="alice", at=AT).ok
    assert vault.read("reader").body.splitlines() == [
        "a",
        "(1 not ordered: first gives no number for a)",
    ]


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
