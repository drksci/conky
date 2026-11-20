"""A habit made by hand from parts that exist: cases first, thought only when no case fits.

This is a pathfinding test for docs/ideas/habit.md. It adds nothing to the runtime. A character
keeps its cases as ordinary watch entries on its own page, asks a model only for a situation no
case covers, and the answer adds the case. The model is a stand-in; no test reaches a live one.
"""

import sys
from pathlib import Path

import pytest

from conky import Vault

from .test_pages import Stand, history, w

FALLBACK = (
    "- on: gate\n"
    '  when: "page.handled != other.turn"\n'
    "  ask:\n"
    "    provider: helper\n"
    '    prompt: "The gate asks: ![[gate#asks]]"\n'
    "    into: said\n"
    "    writes: camp\n"
)


def case(asks: str, answer: str) -> str:
    """One case as a watch entry: when the gate asks this, say that, and mark it handled."""
    return (
        "- on: gate\n"
        f"  when: \"other.asks == '{asks}'\"\n"
        "  set:\n"
        f"    said: \"'{answer}'\"\n"
        "    handled: other.turn\n"
    )


def learns(answer: str, cases: dict[str, str]) -> str:
    """What the stand-in model says: the answer, and its own page rewritten with these cases."""
    entries = "".join(case(asks, said) for asks, said in cases.items()) + FALLBACK
    return f"{answer}\n=== page: guide ===\n---\nwatch:\n{entries}---\n"


@pytest.fixture
def stand(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Stand:
    found = Stand(tmp_path / "stand")
    monkeypatch.setenv("CONKY_COMMAND_STAND", f"{sys.executable} {found.folder / 'model.py'}")
    return found


@pytest.fixture
def camp(vault: Vault, stand: Stand) -> Vault:
    """A space, a gate that asks things, and a guide that starts with no cases at all."""
    assert w(vault, "helper", {"api": "command", "command": "stand"}).ok
    assert w(vault, "camp", {}).ok
    assert w(vault, "gate", {"asks": "", "turn": 0}).ok
    start = [
        {
            "on": "gate",
            "when": "page.handled != other.turn",
            "ask": {
                "provider": "helper",
                "prompt": "The gate asks: ![[gate#asks]]",
                "into": "said",
                "writes": "camp",
            },
        }
    ]
    assert w(vault, "guide", {"within": "camp", "handled": -1, "said": "", "watch": start}).ok
    return vault


def gate_asks(vault: Vault, asks: str) -> None:
    """The gate asks something. Each asking has its own turn, so a case can mark the one it met."""
    turn = vault.read("gate").fields["turn"] + 1
    assert w(vault, "gate", {"asks": asks, "turn": turn}).ok


def thought(vault: Vault) -> int:
    """How many commits in the history were answered by a model."""
    return sum(1 for _, found in history(vault) if "Model" in found)


def test_a_situation_met_twice_is_thought_about_once(camp: Vault, stand: Stand) -> None:
    stand.says(learns("no", {"ford": "no"}))
    gate_asks(camp, "ford")
    assert camp.read("guide").fields["said"] == "no"
    assert len(stand.prompts) == 1

    stand.says(learns("yes", {"ford": "no", "hunt": "yes"}))
    gate_asks(camp, "hunt")
    assert camp.read("guide").fields["said"] == "yes"
    assert len(stand.prompts) == 2

    asked = thought(camp)
    for asks, said in (("ford", "no"), ("hunt", "yes"), ("ford", "no")):
        gate_asks(camp, asks)
        assert camp.read("guide").fields["said"] == said
    assert len(stand.prompts) == 2, "a case answered, so the model was not asked again"
    assert thought(camp) == asked
    camp.verify()


def test_a_new_situation_still_goes_to_thought(camp: Vault, stand: Stand) -> None:
    stand.says(learns("no", {"ford": "no"}))
    gate_asks(camp, "ford")
    stand.says(learns("rest", {"ford": "no", "storm": "rest"}))
    gate_asks(camp, "storm")
    assert camp.read("guide").fields["said"] == "rest"
    assert len(stand.prompts) == 2
    camp.verify()


def test_removing_the_cases_changes_only_the_cost(camp: Vault, stand: Stand) -> None:
    stand.says(learns("no", {"ford": "no"}))
    gate_asks(camp, "ford")
    gate_asks(camp, "hunt")
    gate_asks(camp, "ford")
    assert len(stand.prompts) == 2, "the second ford was answered by its case"

    kept = camp.read("guide").watch[-1]
    assert w(camp, "guide", {"watch": [kept]}).ok
    stand.says("no")
    gate_asks(camp, "storm")
    gate_asks(camp, "ford")
    assert camp.read("guide").fields["said"] == "no"
    assert len(stand.prompts) == 4, "with no case, each situation goes back to thought"
    camp.verify()
