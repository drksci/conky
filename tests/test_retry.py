"""A refused answer is asked again once, with the reason as the last thing the model reads."""

import json
import sys
from pathlib import Path

import pytest

from conky import Vault, voice
from conky.git import trailers

from .conftest import git
from .test_pages import Stand, w

SERIAL = """import json, pathlib, sys
here = pathlib.Path(__file__).parent
prompt = sys.stdin.read()
with (here / "asked.jsonl").open("a") as log:
    log.write(json.dumps(prompt) + "\\n")
n = len((here / "asked.jsonl").read_text().splitlines())
answers = json.loads((here / "answers.json").read_text())
print(answers[min(n, len(answers)) - 1])
"""
BADLY_NAMED = "Done.\n=== page: Mrs Okafor's parcel, shelf 12 ===\n---\nwithin: den\n---\nOn 12.\n"
WELL_NAMED = "Done.\n=== page: parcel-shelf-12 ===\n---\nwithin: den\n---\nOn 12.\n"
SECRET = "Done.\n=== page: own ===\n---\nwithin: den\napi: openai\nsecret: mine\n---\n"


class Series(Stand):
    """A stand-in model that gives its prepared answers one after another, the last one again."""

    def __init__(self, folder: Path) -> None:
        super().__init__(folder)
        (folder / "model.py").write_text(SERIAL, encoding="utf-8")

    def gives(self, *answers: str) -> None:
        (self.folder / "answers.json").write_text(json.dumps(list(answers)), encoding="utf-8")


def den(vault: Vault, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, **more: object) -> Series:
    """Make a provider, a den and a scribe in it that writes pages into the den when ticketed."""
    stand = Series(tmp_path / "series")
    monkeypatch.setenv("CONKY_COMMAND_STAND", f"{sys.executable} {stand.folder / 'model.py'}")
    assert w(vault, "helper", {"api": "command", "command": "stand"}).ok
    assert w(vault, "den", {}).ok
    assert w(vault, "ticket", {"text": "one"}).ok
    ask = {"provider": "helper", "prompt": "Tidy ![[ticket#text]]", "writes": "den", "into": "said"}
    watch = [{"on": "ticket", "when": "other.text != 'one'", "ask": {**ask, **more}}]
    assert w(vault, "scribe", {"within": "den", "watch": watch}).ok
    return stand


def reasons(vault: Vault) -> list[str]:
    ids = git(vault.path, "log", "--reverse", "--format=%H", "main").split()
    found = [trailers(git(vault.path, "log", "-1", "--format=%B", c)) for c in ids]
    return [t["Reason"] for t in found if t["Kind"] == "refused"]


def test_a_retried_answer_is_a_refusal_then_a_write_caused_by_it(
    vault: Vault, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    stand = Stand(tmp_path / "stand")
    monkeypatch.setenv("CONKY_COMMAND_STAND", f"{sys.executable} {stand.folder / 'model.py'}")
    assert w(vault, "helper", {"api": "command", "command": "stand"}).ok
    assert w(vault, "camp", {"rules": [{"each": "!has(page.said) || page.said != 'ask 1'"}]}).ok
    assert w(vault, "gate", {"asks": ""}).ok
    watch = [
        {
            "on": "gate",
            "when": "other.asks != ''",
            "ask": {"provider": "helper", "prompt": "Asked: ![[gate#asks]]", "into": "said"},
        }
    ]
    assert w(vault, "guide", {"within": "camp", "said": "", "watch": watch}).ok
    stand.says("ask {n}")
    assert w(vault, "gate", {"asks": "hunt"}).ok
    first, second = stand.prompts
    assert first == "Asked: hunt"
    assert second.startswith("Asked: hunt\n\n*guide's last answer was turned away: rule: ")
    assert second.endswith(voice.line("retry", page="guide", reason="\0").split("\0")[1] + "*")
    ids = git(vault.path, "log", "-3", "--format=%H").split()
    kinds = [trailers(git(vault.path, "log", "-1", "--format=%B", c)) for c in ids]
    assert kinds[1]["Reason"].startswith("rule:") and kinds[1]["Cause"] == ids[2]
    assert kinds[0]["Cause"] == ids[1]


def test_an_answer_whose_page_block_names_no_page_is_asked_again_with_the_reason(
    vault: Vault, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    stand = den(vault, tmp_path, monkeypatch)
    stand.gives(BADLY_NAMED, WELL_NAMED)
    assert w(vault, "ticket", {"text": "two"}).ok
    first, second = stand.prompts
    assert first.endswith("Tidy two") and "turned away" not in first
    assert second.startswith(first + "\n\n*scribe's last answer was turned away: shape: page block")
    assert "does not name a page" in second
    assert second.endswith(voice.line("retry", page="scribe", reason="\0").split("\0")[1] + "*")
    assert vault.read("parcel-shelf-12").body == "On 12.\n"
    (found,) = reasons(vault)
    assert found.startswith("shape: ")
    vault.verify()


def test_a_second_refusal_for_shape_stops_and_writes_the_otherwise_text_when_there_is_one(
    vault: Vault, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    stand = den(vault, tmp_path, monkeypatch, otherwise="Nothing kept.")
    stand.gives(BADLY_NAMED)
    assert w(vault, "ticket", {"text": "two"}).ok
    assert len(stand.prompts) == 2
    assert vault.read("scribe").fields["said"] == "Nothing kept."
    assert len(reasons(vault)) == 2


def test_a_second_refusal_for_shape_without_otherwise_stops_after_two_asks(
    vault: Vault, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    stand = den(vault, tmp_path, monkeypatch)
    stand.gives(BADLY_NAMED)
    assert w(vault, "ticket", {"text": "two"}).ok
    assert len(stand.prompts) == 2
    assert len(reasons(vault)) == 2 and all(r.startswith("shape: ") for r in reasons(vault))


def test_a_refusal_for_limit_is_not_asked_again(
    vault: Vault, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    stand = den(vault, tmp_path, monkeypatch)
    stand.gives(SECRET)
    assert w(vault, "ticket", {"text": "two"}).ok
    assert len(stand.prompts) == 1
    (found,) = reasons(vault)
    assert found.startswith("limit: ")


def test_a_failure_to_ask_is_not_asked_again(
    vault: Vault, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    stand = den(vault, tmp_path, monkeypatch)
    stand.gives(WELL_NAMED)
    monkeypatch.setenv("CONKY_COMMAND_STAND", str(tmp_path / "no-such-program"))
    assert w(vault, "ticket", {"text": "two"}).ok
    assert stand.prompts == []
    (found,) = reasons(vault)
    assert found.startswith("model: ")


def test_the_second_ask_is_held_to_the_budget_and_a_spent_one_is_a_limit_refusal(
    vault: Vault, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    stand = den(vault, tmp_path, monkeypatch)
    stand.gives(BADLY_NAMED, WELL_NAMED)
    assert w(vault, "scribe", {"budget": {"asks": 1}}).ok
    assert w(vault, "ticket", {"text": "two"}).ok
    assert len(stand.prompts) == 1
    found = reasons(vault)
    assert [r.split(":")[0] for r in found] == ["shape", "limit"]
    assert not (vault.pages_dir / "parcel-shelf-12.md").exists()
