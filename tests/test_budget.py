"""A budget the runtime holds: asks are counted from the history and an ask past it is refused.

Every model is a small local program that prints a prepared answer.
"""

import sys
from pathlib import Path

import pytest

from conky import Vault, arch
from conky.git import trailers

from .conftest import AT, git
from .test_pages import Stand, w

PROMPT = "Seen ![[ticket#n]]."


def history(vault: Vault) -> list[dict[str, str]]:
    ids = git(vault.path, "log", "--reverse", "--format=%H", "main").split()
    return [trailers(git(vault.path, "log", "-1", "--format=%B", i)) for i in ids]


def limits(vault: Vault) -> list[dict[str, str]]:
    return [t for t in history(vault) if t.get("Reason", "").startswith("limit:")]


def scribe(prompt: str = PROMPT, **more: object) -> dict:
    ask = {"provider": "helper", "prompt": prompt, "into": "said"}
    return {"watch": [{"on": "ticket", "when": "true", "ask": ask}], **more}


@pytest.fixture
def stand(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Stand:
    found = Stand(tmp_path / "stand")
    monkeypatch.setenv("CONKY_COMMAND_STAND", f"{sys.executable} {found.folder / 'model.py'}")
    found.says("answer {n}")
    return found


@pytest.fixture
def house(vault: Vault, stand: Stand) -> Vault:
    assert w(vault, "helper", {"api": "command", "command": "stand"}).ok
    assert w(vault, "ticket", {"n": 0}).ok
    return vault


def wake(vault: Vault, times: int, start: int = 1) -> None:
    for n in range(start, start + times):
        assert w(vault, "ticket", {"n": n}).ok


@arch.holds("law.budget.held", "law.refusal.record")
def test_a_budget_cannot_be_exceeded(house: Vault, stand: Stand) -> None:
    assert w(house, "scribe", scribe(budget={"asks": 2})).ok
    wake(house, 5)
    assert len(stand.prompts) == 2
    stopped = limits(house)
    assert len(stopped) == 3 and all(t["Page"] == "scribe" for t in stopped)
    assert "Model" not in stopped[0]
    reason = stopped[0]["Reason"]
    assert "all 2 asks" in reason and "Write the budget of scribe again" in reason
    assert house.read("scribe").fields["said"] == "answer 2"
    house.verify()
    before = house.read("scribe")
    house.rebuild()
    house.verify()
    assert house.read("scribe") == before


def test_a_watcher_of_refusals_is_told_and_its_reflex_counts(house: Vault, stand: Stand) -> None:
    when = "event.reason.startsWith('limit')"
    count = {"on": "refusal", "when": when, "set": {"n": "page.n + 1"}}
    assert w(house, "den", {"n": 0, "watch": [count]}).ok
    assert w(house, "scribe", scribe(within="den", budget={"asks": 2})).ok
    wake(house, 5)
    assert house.read("den").fields["n"] == 3 and len(stand.prompts) == 2


def test_writing_the_budget_again_refills_it_even_at_the_same_size(
    house: Vault, stand: Stand
) -> None:
    assert w(house, "scribe", scribe(budget={"asks": 2})).ok
    wake(house, 3)
    assert len(stand.prompts) == 2 and len(limits(house)) == 1
    assert w(house, "scribe", {"budget": {"asks": 2}}).ok
    wake(house, 3, start=4)
    assert len(stand.prompts) == 4 and len(limits(house)) == 2


def test_a_write_that_leaves_the_budget_alone_does_not_refill_it(
    house: Vault, stand: Stand
) -> None:
    assert w(house, "scribe", scribe(budget={"asks": 1})).ok
    wake(house, 1)
    assert w(house, "scribe", {"mood": "keen"}).ok
    wake(house, 1, start=2)
    assert len(stand.prompts) == 1 and len(limits(house)) == 1


def test_a_space_hands_its_members_a_default_and_their_own_wins(house: Vault, stand: Stand) -> None:
    assert w(house, "den", {"budget": {"asks": 1}}).ok
    assert w(house, "scribe", scribe(within="den")).ok
    wake(house, 3)
    assert len(stand.prompts) == 1 and len(limits(house)) == 2
    assert w(house, "den", {"budget": {"asks": 1}}).ok
    wake(house, 1, start=4)
    assert len(stand.prompts) == 2
    assert w(house, "scribe", {"budget": {"asks": 3}}).ok
    wake(house, 4, start=5)
    assert len(stand.prompts) == 5


def test_a_space_budget_is_a_default_per_member_and_not_a_pool(house: Vault, stand: Stand) -> None:
    assert w(house, "den", {"budget": {"asks": 1}}).ok
    for name in ("a", "b"):
        assert w(house, name, scribe(PROMPT + name, within="den")).ok
    wake(house, 2)
    assert len(stand.prompts) == 2 and len(limits(house)) == 2


def test_the_theatre_gives_every_character_a_default(house: Vault, stand: Stand) -> None:
    assert w(house, "theatre", {"budget": {"asks": 1}}).ok
    assert w(house, "scribe", scribe()).ok
    wake(house, 3)
    assert len(stand.prompts) == 1 and len(limits(house)) == 2


def test_no_budget_means_no_limit(house: Vault, stand: Stand) -> None:
    assert w(house, "scribe", scribe()).ok
    wake(house, 5)
    assert len(stand.prompts) == 5 and not limits(house)


def test_an_answer_from_the_cache_is_not_counted(house: Vault, stand: Stand) -> None:
    assert w(house, "scribe", {"budget": {"asks": 2}}).ok
    cause = git(house.path, "rev-parse", "HEAD").strip()

    def ask(at: str | None) -> None:
        house.ask("scribe", "said", provider="helper", prompt="Hi.", actor="alice", at=AT, cause=at)

    ask(cause)
    ask(cause)
    assert len(stand.prompts) == 1
    assert [t.get("Cache") for t in history(house)[-2:]] == [None, "hit"]
    ask(None)
    assert len(stand.prompts) == 2 and not limits(house)
    ask(None)
    assert len(limits(house)) == 1


def test_an_answer_a_rule_refused_is_spent_and_so_is_its_retry(house: Vault, stand: Stand) -> None:
    assert w(house, "den", {"rules": [{"each": "!has(page.said) || page.said == ''"}]}).ok
    assert w(house, "scribe", scribe(within="den", budget={"asks": 2})).ok
    wake(house, 1)
    assert len(stand.prompts) == 2 and not limits(house)
    wake(house, 1, start=2)
    assert len(stand.prompts) == 2 and len(limits(house)) == 1


def test_a_condition_reads_what_is_left_and_stops_the_ask_before_a_refusal(
    house: Vault, stand: Stand
) -> None:
    entry = scribe()["watch"][0] | {"when": "asks.left > 0"}
    assert w(house, "scribe", {"watch": [entry], "budget": {"asks": 2}}).ok
    wake(house, 5)
    assert len(stand.prompts) == 2 and not limits(house)


def test_a_rule_may_read_asks_and_a_page_without_budget_reads_a_large_left(house: Vault) -> None:
    assert w(house, "scribe", {"rules": ["asks.left > 1000 && asks.spent == 0"]}).ok
    assert w(house, "other", {"budget": {"asks": 3}, "rules": ["asks.left == 3"]}).ok


def test_a_prompt_embeds_what_is_left(house: Vault, stand: Stand) -> None:
    prompt = "![[scribe#asks]] at ![[ticket#n]]"
    assert w(house, "scribe", scribe(prompt, budget={"asks": 3})).ok
    wake(house, 2)
    assert stand.prompts == ["3 of 3 asks left at 1", "2 of 3 asks left at 2"]


def test_a_prompt_embedding_asks_of_a_page_without_budget_says_nothing(
    house: Vault, stand: Stand
) -> None:
    assert w(house, "scribe", scribe("[![[scribe#asks]]] ![[ticket#n]]")).ok
    wake(house, 1)
    assert stand.prompts == ["[] 1"]


def test_a_budget_removed_lifts_the_limit(house: Vault, stand: Stand) -> None:
    assert w(house, "scribe", scribe(budget={"asks": 1})).ok
    wake(house, 2)
    assert len(stand.prompts) == 1
    assert w(house, "scribe", {"budget": None}).ok
    assert "budget" not in house.read("scribe").fields
    wake(house, 2, start=3)
    assert len(stand.prompts) == 3


def test_a_budget_is_a_record_in_the_history_and_nothing_else(house: Vault) -> None:
    assert w(house, "scribe", {"budget": {"asks": 4}}).ok
    assert history(house)[-1]["Budget"] == "4"
    assert w(house, "scribe", {"budget": None}).ok
    assert history(house)[-1]["Budget"] == "none"
    assert w(house, "scribe", {"mood": "keen"}).ok
    assert "Budget" not in history(house)[-1]
