"""A rule can say why: the words after `//` in a rule are the reason a refusal gives."""

import sys
from pathlib import Path

import pytest
from bench import dynamics

from conky import Vault, arch
from conky.git import trailers
from conky.rules import says

from .conftest import AT, git
from .test_pages import Stand

CUPS = "!has(page.cups) || page.cups <= 50"
WORDS = "Sell 50 cups at most."
BOTH = "Sell 50 cups and no fewer than none."


def w(vault: Vault, page: str, changes: dict):
    return vault.write(page, changes, None, actor="alice", at=AT)


def recorded(vault: Vault) -> dict[str, str]:
    return trailers(git(vault.path, "log", "-1", "--format=%B"))


@pytest.mark.parametrize(
    ("rule", "words"),
    [
        (CUPS, None),
        (f"{CUPS} // {WORDS}", WORDS),
        (f"{CUPS}//{WORDS}", WORDS),
        (f"// {WORDS}\n{CUPS}", WORDS),
        ("page.cups <= 50 // Sell 50 cups\n&& page.cups >= 0 // and no fewer than none.", BOTH),
        ("page.site.startsWith('http://')", None),
        ("page.site.startsWith('http://') // Give the whole address.", "Give the whole address."),
        ('page.note != "a // b" // Say something else.', "Say something else."),
        ("page.cups <= 50 //", None),
        ("page.cups <=", None),
    ],
)
def test_the_words_of_a_rule_are_what_follows_its_slashes(rule: str, words: str | None) -> None:
    assert says(rule) == words


@arch.holds("law.rule.says")
def test_a_refusal_gives_the_words_of_the_rule_and_records_them(vault: Vault) -> None:
    assert w(vault, "stall", {"cups": 1, "rules": [f"{CUPS} // {WORDS}"]}).ok
    refused = w(vault, "stall", {"cups": 51})
    assert not refused.ok and refused.reason == f"rule: {WORDS} (from stall)"
    assert recorded(vault)["Reason"] == f"rule: {WORDS} (from stall)"
    assert w(vault, "stall", {"cups": 50}).ok


@arch.holds("law.rule.says")
def test_a_space_says_why_for_every_page_within_it(vault: Vault) -> None:
    assert w(vault, "stand", {"rules": [{"each": f"{CUPS} // {WORDS}"}]}).ok
    refused = w(vault, "cooler", {"within": "stand", "cups": 51})
    assert not refused.ok and refused.reason == f"rule: {WORDS} (from stand)"
    assert recorded(vault)["From"] == "stand"
    assert w(vault, "cooler", {"within": "stand", "cups": 5}).ok
    added = w(vault, "stand", {"rules": [{"each": "page.cups <= 4 // Sell 4 cups at most."}]})
    assert added.reason == "rule: Sell 4 cups at most. (from stand) for cooler, within it"


def test_a_rule_without_words_is_refused_as_before(vault: Vault) -> None:
    assert w(vault, "stand", {"rules": [{"each": CUPS}]}).ok
    assert w(vault, "stall", {"site": "http://a", "rules": ["page.site.startsWith('http://')"]}).ok
    assert w(vault, "cooler", {"within": "stand", "cups": 51}).reason == (
        f"rule: {CUPS} (from stand) is false"
    )
    assert w(vault, "stall", {"site": "ftp://a"}).reason == (
        "rule: page.site.startsWith('http://') (from stall) is false"
    )


def test_a_rule_with_words_that_cannot_be_worked_out_still_shows_the_rule(vault: Vault) -> None:
    assert w(vault, "stall", {"rules": [f"page.cups <= 50 // {WORDS}"]}).reason.startswith(
        f"rule: page.cups <= 50 // {WORDS} (from stall) failed to evaluate: "
    )


@arch.holds("law.rule.says")
def test_a_model_turned_away_reads_the_words_of_the_rule(
    vault: Vault, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    stand = Stand(tmp_path / "stand")
    monkeypatch.setenv("CONKY_COMMAND_STAND", f"{sys.executable} {stand.folder / 'model.py'}")
    assert w(vault, "helper", {"api": "command", "command": "stand"}).ok
    rule = "!has(page.said) || page.said != 'ask 1' // Say anything but the first thing."
    assert w(vault, "camp", {"rules": [{"each": rule}]}).ok and w(vault, "gate", {"asks": ""}).ok
    ask = {"provider": "helper", "prompt": "Asked: ![[gate#asks]]", "into": "said"}
    watch = [{"on": "gate", "when": "other.asks != ''", "ask": ask}]
    assert w(vault, "guide", {"within": "camp", "said": "", "watch": watch}).ok
    stand.says("ask {n}")
    assert w(vault, "gate", {"asks": "hunt"}).ok
    turned = "*guide's last answer was turned away: rule: Say anything but the first thing. "
    assert stand.prompts[1].startswith(f"Asked: hunt\n\n{turned}(from camp). guide may answer")


def test_the_trial_picture_reads_a_refusal_that_carries_words() -> None:
    for reason in ("rule: page.n < 5 (from den) is false", f"rule: {WORDS} (from den)"):
        event = {"kind": "refused", "page": "note", "by": "ada", "reason": reason}
        said = dynamics._describe(event, [event])
        assert said["words"] == "note is turned away: it breaks a rule den hands down."
