"""A refused answer is asked again once, with the reason as the last thing the model reads."""

import sys
from pathlib import Path

import pytest

from conky import Vault, voice
from conky.git import trailers

from .conftest import git
from .test_pages import Stand, w


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
