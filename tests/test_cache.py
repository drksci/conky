"""Pay once: a costly answer is kept as derived data, keyed to the moment it was asked in.

Every test talks to a stand-in provider on 127.0.0.1 and to a cache in a temporary directory.
"""

import dataclasses
import os
import shutil
from collections.abc import Iterator
from pathlib import Path

import pytest

from conky import Vault, model
from conky.cache import Cache, Mode, digest
from conky.cli import main

from .conftest import AT, git
from .test_model import Stand, message, provider, w


@pytest.fixture(autouse=True)
def local_network(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in ("no_proxy", "NO_PROXY"):
        monkeypatch.setenv(name, "127.0.0.1")


@pytest.fixture
def stand() -> Iterator[Stand]:
    found = Stand()
    yield found
    found.stop()


def entries(folder: Path) -> list[Path]:
    return sorted(folder.glob("*.json")) if folder.exists() else []


def ask(vault: Vault, cause: str | None = None, prompt: str = "Say hello."):
    return vault.ask(
        "desk", "summary", provider="helper", prompt=prompt, actor="alice", at=AT, cause=cause
    )


def with_mode(vault: Vault, mode: Mode) -> None:
    vault.cache = dataclasses.replace(vault.cache, mode=mode)


@pytest.fixture
def helped(vault: Vault, stand: Stand) -> Vault:
    provider(vault, stand)
    assert w(vault, "desk", {"summary": ""}).ok
    return vault


def head(vault: Vault) -> str:
    return git(vault.path, "rev-parse", "HEAD").strip()


def test_the_same_question_for_the_same_event_is_paid_for_once(helped: Vault, stand: Stand) -> None:
    cause = head(helped)
    assert ask(helped, cause).ok
    first = message(helped)[1]
    assert ask(helped, cause).ok
    second = message(helped)[1]
    assert len(stand.requests) == 1
    assert "Cache" not in first and first["Tokens-In"] == "11"
    assert second["Cache"] == "hit"
    assert "Tokens-In" not in second and "Tokens-Out" not in second
    assert second["Model"] == "helper" and second["Model-Name"] == "test-model"
    assert helped.read("desk").fields["summary"] == "The printer keeps jamming."
    assert helped.log()[-1].endswith("model helper")
    helped.verify()


def test_the_same_words_after_a_new_event_are_asked_afresh(helped: Vault, stand: Stand) -> None:
    stand.answer = lambda n: f"answer {n}"
    assert ask(helped).ok
    assert ask(helped).ok
    assert len(stand.requests) == 2
    assert helped.read("desk").fields["summary"] == "answer 2"
    assert "Cache" not in message(helped)[1]


def test_a_reaction_is_keyed_to_the_event_that_caused_it(helped: Vault, stand: Stand) -> None:
    ask_entry = {"provider": "helper", "prompt": "Say hello.", "into": "summary"}
    watch = [{"on": "ticket", "when": "true", "ask": ask_entry}]
    assert w(helped, "desk", {"watch": watch}).ok
    assert w(helped, "ticket", {"n": 1}).ok
    cause = git(helped.path, "log", "-2", "--format=%H").split()[1]
    assert message(helped)[1]["Cause"] == cause
    found = model.provider("helper", helped.read("helper").fields)
    assert helped.cache.get(model.moment_key(found, "Say hello.", cause)) is not None
    assert len(stand.requests) == 1


@pytest.mark.parametrize(
    "change",
    [
        {"api": "anthropic"},
        {"model": "other-model"},
        {"max_tokens": 5},
        {"url": "http://127.0.0.1:1/v1/chat/completions"},
    ],
)
def test_every_part_of_the_moment_is_in_the_key(change: dict) -> None:
    base = model.provider("a", {"api": "openai", "url": "http://x/y", "model": "m"})
    other = model.provider("a", {**{"api": "openai", "url": "http://x/y", "model": "m"}, **change})
    assert model.moment_key(base, "p", "c") != model.moment_key(other, "p", "c")
    assert model.moment_key(base, "p", "c") != model.moment_key(base, "q", "c")
    assert model.moment_key(base, "p", "c") != model.moment_key(base, "p", "d")


def test_the_key_ignores_the_page_name_and_the_secret_name() -> None:
    fields = {"api": "openai", "url": "http://x/y", "model": "m"}
    one = model.provider("one", {**fields, "secret": "a"})
    two = model.provider("two", {**fields, "secret": "b"})
    assert model.moment_key(one, "p", "c") == model.moment_key(two, "p", "c")


def test_a_command_is_keyed_by_its_name() -> None:
    one = model.provider("p", {"api": "command", "command": "claude"})
    two = model.provider("p", {"api": "command", "command": "codex"})
    assert model.moment_key(one, "p", "c") != model.moment_key(two, "p", "c")


def test_parts_cannot_run_together() -> None:
    assert digest("ab", "c") != digest("a", "bc")


def test_mode_off_neither_reads_nor_writes(helped: Vault, stand: Stand) -> None:
    with_mode(helped, Mode.OFF)
    cause = head(helped)
    assert ask(helped, cause).ok and ask(helped, cause).ok
    assert len(stand.requests) == 2
    assert entries(helped.cache.directory) == []
    assert "Cache" not in message(helped)[1]


def test_mode_refresh_ignores_entries_and_writes_new_ones(helped: Vault, stand: Stand) -> None:
    cause = head(helped)
    assert ask(helped, cause).ok
    stand.answer = "A newer answer."
    with_mode(helped, Mode.REFRESH)
    assert ask(helped, cause).ok
    assert len(stand.requests) == 2 and "Cache" not in message(helped)[1]
    with_mode(helped, Mode.ON)
    assert ask(helped, cause).ok
    assert len(stand.requests) == 2
    assert helped.read("desk").fields["summary"] == "A newer answer."
    assert message(helped)[1]["Cache"] == "hit"


def test_mode_only_never_calls_a_provider(helped: Vault, stand: Stand) -> None:
    with_mode(helped, Mode.ONLY)
    result = ask(helped, head(helped))
    assert result.ok and result.plain
    assert stand.requests == []
    assert message(helped)[1]["Model"] == "none"
    assert entries(helped.cache.directory) == []
    assert helped.read("desk").fields["summary"].startswith("No model was around")


def test_mode_only_answers_from_the_cache_when_it_has_the_answer(
    helped: Vault, stand: Stand
) -> None:
    cause = head(helped)
    assert ask(helped, cause).ok
    with_mode(helped, Mode.ONLY)
    result = ask(helped, cause)
    assert result.ok and not result.plain
    assert len(stand.requests) == 1
    assert message(helped)[1]["Cache"] == "hit"


def test_a_failed_call_and_the_plain_sentence_are_never_kept(helped: Vault, stand: Stand) -> None:
    stand.status = 500
    cause = head(helped)
    assert ask(helped, cause).plain
    assert entries(helped.cache.directory) == []
    stand.status = 200
    assert not ask(helped, cause).plain
    assert len(stand.requests) == 2
    assert len(entries(helped.cache.directory)) == 1


def test_deleting_the_cache_in_the_middle_changes_only_the_cost(
    helped: Vault, stand: Stand
) -> None:
    cause = head(helped)
    assert ask(helped, cause).ok
    shutil.rmtree(helped.cache.directory)
    assert ask(helped, cause).ok
    assert len(stand.requests) == 2
    assert helped.read("desk").fields["summary"] == "The printer keeps jamming."
    assert ask(helped, cause).ok
    assert len(stand.requests) == 2
    helped.verify()


@pytest.mark.parametrize("junk", ["not json {", '{"text": 5}', '{"text": "  "}', "[]", ""])
def test_an_unreadable_entry_is_a_miss_and_is_replaced(
    helped: Vault, stand: Stand, junk: str
) -> None:
    cause = head(helped)
    assert ask(helped, cause).ok
    (path,) = entries(helped.cache.directory)
    path.write_text(junk, encoding="utf-8")
    assert ask(helped, cause).ok
    assert len(stand.requests) == 2
    assert "Cache" not in message(helped)[1]
    assert ask(helped, cause).ok
    assert len(stand.requests) == 2
    assert message(helped)[1]["Cache"] == "hit"


def test_the_oldest_entries_go_first_and_a_hit_renews_one(tmp_path: Path) -> None:
    store = Cache(tmp_path / "c", limit=100)
    for number, name in enumerate(("a", "b", "c")):
        store.put(name, {"text": "x" * 15})
        os.utime(store.directory / f"{name}.json", (number, number))
    assert store.stats().entries == 3
    assert store.get("a") is not None
    store.put("d", {"text": "x" * 15})
    assert [p.stem for p in entries(store.directory)] == ["a", "c", "d"]


def test_the_newest_entry_stays_even_when_it_alone_is_over_the_bound(tmp_path: Path) -> None:
    store = Cache(tmp_path, limit=1)
    store.put("a", {"text": "x" * 50})
    store.put("b", {"text": "x" * 50})
    assert [p.stem for p in entries(tmp_path)] == ["b"]


def test_a_cache_that_cannot_be_written_is_skipped(tmp_path: Path) -> None:
    blocked = tmp_path / "file"
    blocked.write_text("in the way")
    store = Cache(blocked / "cache")
    store.put("a", {"text": "x"})
    assert store.get("a") is None and store.stats().entries == 0


def test_a_populated_cache_is_not_the_history(helped: Vault, stand: Stand) -> None:
    assert ask(helped, head(helped)).ok
    assert entries(helped.cache.directory)
    assert not helped.cache.directory.is_relative_to(helped.path)
    assert git(helped.path, "status", "--porcelain").strip() == ""
    names = git(helped.path, "log", "--name-only", "--format=").split()
    assert all(n.startswith(("pages/", "keys/")) for n in names)
    helped.verify()
    shutil.rmtree(helped.cache.directory)
    helped.verify()


def test_the_command_shows_and_clears_the_cache(
    helped: Vault,
    capsys: pytest.CaptureFixture[str],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    assert ask(helped, head(helped)).ok
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    monkeypatch.chdir(elsewhere)
    assert main(["--color", "never", "cache"]) == 0
    shown = capsys.readouterr().out
    assert str(helped.cache.directory) in shown and "1 entry" in shown
    assert main(["--color", "never", "cache", "clear"]) == 0
    assert "cleared 1 entry" in capsys.readouterr().out
    assert entries(helped.cache.directory) == []
    assert main(["--color", "never", "cache"]) == 0
    assert "0 entries" in capsys.readouterr().out


def test_the_option_wins_over_the_environment(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    where = tmp_path / "chosen"
    assert main(["--cache-dir", str(where), "--cache-mode", "only", "cache"]) == 0
    shown = capsys.readouterr().out
    assert str(where) in shown and "mode only" in shown


def test_a_mode_the_cache_does_not_know_says_what_to_use(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setenv("CONKY_CACHE", "sometimes")
    assert main(["cache"]) == 1
    assert "use one of on, off, refresh, only" in capsys.readouterr().err


def test_the_size_bound_has_a_default_and_one_variable(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    assert Cache.open(tmp_path).limit == 64 * 1024 * 1024
    monkeypatch.setenv("CONKY_CACHE_MAX", "2")
    assert Cache.open(tmp_path).limit == 2 * 1024 * 1024
    monkeypatch.setenv("CONKY_CACHE_MAX", "lots")
    with pytest.raises(Exception, match="CONKY_CACHE_MAX"):
        Cache.open(tmp_path)
