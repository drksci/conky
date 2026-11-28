"""A command provider page names the model and the effort it answers with.

No test reaches a live model: every program is a small script written here that records how it
was started.
"""

import json
import os
import shutil
import stat
import sys
from pathlib import Path

import pytest
from bench import cards

from conky import Vault, model
from conky.cache import Cache
from conky.git import trailers

from .conftest import AT, git

SECRET_LINE = "secret-command-line-marker"
EXPECTED_OLD_KEY = "a494b0b1b7ce3b0f4bc9172ca0264ec6b08857ac5dea8b878d6de5833d563af9"


def w(vault: Vault, page: str, changes: dict):
    return vault.write(page, changes, None, actor="alice", at=AT)


def commits(vault: Vault) -> list[dict[str, str]]:
    """Return the trailers of every commit of the vault that records an answer, oldest first."""
    found = []
    for commit in reversed(git(vault.path, "log", "--format=%H").split()):
        got = trailers(git(vault.path, "log", "-1", "--format=%B", commit))
        if "Model" in got:
            found.append(got)
    return found


def recorder(tmp_path: Path, name: str, seen: Path) -> Path:
    """Write a program that records its argv and the two variables it was told, and answers."""
    tool = tmp_path / "bin" / name
    tool.parent.mkdir(exist_ok=True)
    tool.write_text(
        f"#!{sys.executable}\nimport json, os, sys\nsys.stdin.read()\n"
        f"open({str(seen)!r}, 'a').write(json.dumps({{'argv': sys.argv[1:], "
        "'model': os.environ.get('CONKY_ASK_MODEL'), "
        "'effort': os.environ.get('CONKY_ASK_EFFORT')}) + '\\n')\n"
        "print('answered')\n",
        encoding="utf-8",
    )
    tool.chmod(tool.stat().st_mode | stat.S_IXUSR)
    return tool


def told(seen: Path) -> list[dict]:
    return [json.loads(line) for line in seen.read_text(encoding="utf-8").splitlines()]


def on_path(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Make PATH hold git, ssh-keygen and what is in tmp_path/bin, and nothing else."""
    for real in ("git", "ssh-keygen"):
        link = tmp_path / "bin" / real
        if not link.exists():
            link.symlink_to(shutil.which(real) or real)
    monkeypatch.setenv("PATH", str(tmp_path / "bin"))


@pytest.fixture(autouse=True)
def clean_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in (
        "CONKY_MODEL",
        "ANTHROPIC_API_KEY",
        "OPENAI_API_KEY",
        "CONKY_COMMAND_CLAUDE",
        "CONKY_COMMAND_CODEX",
        "CONKY_COMMAND_STAND",
        "CONKY_ASK_MODEL",
        "CONKY_ASK_EFFORT",
    ):
        monkeypatch.delenv(name, raising=False)


def listens(provider: str) -> dict:
    return {
        "said": "",
        "watch": [
            {
                "on": "counter",
                "when": "true",
                "ask": {"provider": provider, "into": "said", "prompt": "Answer: ![[counter]]"},
            }
        ],
    }


def test_two_provider_pages_answer_with_their_own_model_and_effort_in_one_run(
    vault: Vault, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    seen = tmp_path / "seen.jsonl"
    recorder(tmp_path, "claude", seen)
    on_path(tmp_path, monkeypatch)
    small = {"api": "command", "command": "claude", "model": "small-model", "effort": "low"}
    large = {"api": "command", "command": "claude", "model": "large-model", "effort": "high"}
    assert w(vault, "small", small).ok and w(vault, "large", large).ok
    assert w(vault, "ear", listens("small")).ok and w(vault, "clerk", listens("large")).ok
    assert w(vault, "counter", {"n": 1}).ok
    runs = told(seen)
    assert len(runs) == 2
    tails = {tuple(run["argv"][-4:]) for run in runs}
    assert tails == {
        ("--model", "small-model", "--effort", "low"),
        ("--model", "large-model", "--effort", "high"),
    }
    answers = {(got["Model"], got["Model-Name"], got["Effort"]) for got in commits(vault)}
    assert answers == {("small", "small-model", "low"), ("large", "large-model", "high")}
    vault.verify()


def test_a_configured_command_is_told_through_the_environment_and_its_argv_is_unchanged(
    vault: Vault, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    seen = tmp_path / "seen.jsonl"
    tool = recorder(tmp_path, "stand", seen)
    monkeypatch.setenv("CONKY_COMMAND_STAND", f"{sys.executable} {tool}")
    fields = {"api": "command", "command": "stand", "model": "some-model", "effort": "careful"}
    assert w(vault, "helper", fields).ok and w(vault, "clerk", listens("helper")).ok
    assert w(vault, "counter", {"n": 1}).ok
    assert told(seen) == [{"argv": [], "model": "some-model", "effort": "careful"}]
    assert commits(vault)[0]["Effort"] == "careful"
    assert commits(vault)[0]["Model-Name"] == "some-model"


def test_without_an_effort_nothing_is_told_and_nothing_is_recorded(
    vault: Vault, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    seen = tmp_path / "seen.jsonl"
    tool = recorder(tmp_path, "stand", seen)
    monkeypatch.setenv("CONKY_COMMAND_STAND", f"{sys.executable} {tool}")
    assert w(vault, "helper", {"api": "command", "command": "stand"}).ok
    assert w(vault, "clerk", listens("helper")).ok and w(vault, "counter", {"n": 1}).ok
    assert told(seen) == [{"argv": [], "model": None, "effort": None}]
    assert "Effort" not in commits(vault)[0]


def test_the_built_in_claude_with_no_effort_is_started_as_it_always_was(
    vault: Vault, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    seen = tmp_path / "seen.jsonl"
    recorder(tmp_path, "claude", seen)
    on_path(tmp_path, monkeypatch)
    assert w(vault, "helper", {"api": "command", "command": "claude"}).ok
    assert w(vault, "clerk", listens("helper")).ok and w(vault, "counter", {"n": 1}).ok
    (run,) = told(seen)
    assert run["argv"][-2:] == ["--model", model.ANTHROPIC_DEFAULT_MODEL]
    assert "--effort" not in run["argv"]
    assert run["model"] is None and run["effort"] is None
    assert "Effort" not in commits(vault)[0]


def test_an_effort_on_a_built_in_that_takes_none_is_refused_and_detection_goes_on(
    vault: Vault, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    seen = tmp_path / "seen.jsonl"
    recorder(tmp_path, "claude", seen)
    recorder(tmp_path, "codex", seen)
    on_path(tmp_path, monkeypatch)
    monkeypatch.delenv("CONKY_PROVIDER", raising=False)
    assert w(vault, "helper", {"api": "command", "command": "codex", "effort": "low"}).ok
    assert w(vault, "clerk", listens("helper")).ok and w(vault, "counter", {"n": 1}).ok
    reasons = [
        trailers(git(vault.path, "log", "-1", "--format=%B", commit)).get("Reason", "")
        for commit in git(vault.path, "log", "--format=%H").split()
    ]
    refused = [reason for reason in reasons if "takes no effort" in reason]
    assert refused and refused[0].startswith("model: ") and "remove effort" in refused[0]
    assert commits(vault)[0]["Model"] == "detected:claude"


def test_the_same_question_at_another_effort_is_another_cache_entry(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    low = model.Provider("p", "command", None, "m", None, None, "stand", "low")
    high = model.Provider("p", "command", None, "m", None, None, "stand", "high")
    assert model.moment_key(low, "Say it", "c1") != model.moment_key(high, "Say it", "c1")
    cache = Cache(tmp_path / "cache")
    asked = []

    def stand(found: model.Provider) -> model.Answer | None:
        return model.ask_once(cache, found, lambda: None, "Say it", tmp_path, "c1")

    seen = tmp_path / "seen.jsonl"
    tool = recorder(tmp_path, "stand", seen)
    monkeypatch.setenv("CONKY_COMMAND_STAND", f"{sys.executable} {tool}")
    for found in (low, high, low):
        reply = stand(found)
        assert reply is not None
        asked.append((reply.cached, reply.effort))
    assert asked == [(False, "low"), (False, "high"), (True, "low")]
    assert len(told(seen)) == 2


def test_a_page_without_an_effort_keeps_the_key_it_always_had() -> None:
    found = model.Provider("p", "command", None, "some-model", None, None, "claude")
    assert model.moment_key(found, "Say hello", "abc123") == EXPECTED_OLD_KEY


@pytest.mark.parametrize(
    ("fields", "why"),
    [
        ({"api": "command", "command": "claude", "effort": "extreme"}, "low, medium, high"),
        ({"api": "command", "command": "stand", "effort": "two words"}, "one plain word"),
        ({"api": "command", "command": "stand", "effort": 3}, "one plain word"),
        ({"api": "command", "command": "stand", "model": ""}, "model"),
        ({"api": "openai", "url": "https://x.example", "model": "m", "effort": "low"}, "command"),
    ],
)
def test_a_wrong_effort_or_model_is_refused_when_the_page_is_written(
    vault: Vault, fields: dict, why: str
) -> None:
    result = w(vault, "helper", fields)
    assert not result.ok and result.reason is not None
    assert result.reason.startswith("shape: ") and why in result.reason
    assert not (vault.pages_dir / "helper.md").exists()


def test_a_command_that_is_not_text_never_breaks_the_check_of_an_effort(vault: Vault) -> None:
    """A built-in is looked up by its name, so a `command` that is no name has no levels."""
    assert model.check_provider({"api": "command", "command": ["a"], "effort": "low"}) is None
    assert model.check_provider({"api": "command", "command": {"a": 1}, "effort": "not a word"})
    done = w(vault, "p", {"api": "command", "command": ["a"], "effort": "low"})
    assert done.ok or done.reason


def test_a_page_that_is_not_a_provider_may_use_the_word_for_itself(vault: Vault) -> None:
    assert w(vault, "gym", {"effort": 3}).ok
    assert w(vault, "helper", {"api": "command", "command": "stand", "effort": "any-word"}).ok


def test_no_secret_and_no_command_line_is_written_to_the_vault(
    vault: Vault, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    seen = tmp_path / "seen.jsonl"
    tool = recorder(tmp_path, "stand", seen)
    monkeypatch.setenv("CONKY_COMMAND_STAND", f"{sys.executable} {tool} {SECRET_LINE}")
    assert w(vault, "helper", {"api": "command", "command": "stand", "effort": "low"}).ok
    assert w(vault, "clerk", listens("helper")).ok and w(vault, "counter", {"n": 1}).ok
    assert told(seen)
    for found in vault.path.rglob("*"):
        if found.is_file():
            assert SECRET_LINE.encode() not in found.read_bytes(), found
    assert SECRET_LINE not in git(vault.path, "log", "--all", "-p", "--format=fuller")


def test_a_card_draws_each_page_s_model_and_effort_into_the_call(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    seen = tmp_path / "seen.jsonl"
    program = tmp_path / "bin" / "claude"
    program.parent.mkdir()
    program.write_text(
        f"#!{sys.executable}\nimport json, os, sys\nsys.stdin.read()\n"
        "told = [os.environ.get('CONKY_ASK_MODEL'), os.environ.get('CONKY_ASK_EFFORT')]\n"
        f"open({str(seen)!r}, 'a').write(json.dumps(told) + '\\n')\n"
        "print('told %s, shelf 12' % told)\n",
        encoding="utf-8",
    )
    program.chmod(program.stat().st_mode | stat.S_IXUSR)
    monkeypatch.setenv("PATH", f"{tmp_path / 'bin'}{os.pathsep}{os.environ['PATH']}")
    monkeypatch.setenv("CONKY_PROVIDER", "claude")
    monkeypatch.setenv("CONKY_COMMAND_CLAUDE", str(program))
    card = Path(__file__).parent.parent / "bench" / "cards" / "a-clerk-has-a-small-ear.yaml"
    out = tmp_path / "out"
    assert cards.main([str(card), "--draws", "1", "--out", str(out)]) == 0
    (row,) = [json.loads(line) for line in (out / "rows.jsonl").read_text().splitlines()]
    assert [json.loads(line) for line in seen.read_text().splitlines()] == [
        ["claude-haiku-5-5", "low"],
        [None, "medium"],
    ]
    kept = Vault(row["vault"], Path(row["vault"]).parent / "keys")
    answers = [(got["Model"], got["Model-Name"], got["Effort"]) for got in commits(kept)]
    assert answers == [
        ("ear-model", "claude-haiku-5-5", "low"),
        ("clerk-model", "stand", "medium"),
    ]
