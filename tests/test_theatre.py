"""A theatre: a vault and the settings true only on this machine, found from any folder in it."""

import os
import subprocess
from pathlib import Path

import pytest

from conky import Vault, cache, theatre
from conky.cli import main
from conky.errors import BadInput, VerifyFailed
from conky.page import load_value

from .conftest import AT, git

FILE = "marionette.md"
WRONG = sorted((Path(__file__).parent / "invalid" / "marionette").glob("*.yaml"))


@pytest.fixture(autouse=True)
def bare_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in list(os.environ):
        if name.startswith("CONKY_") or name in ("ANTHROPIC_API_KEY", "OPENAI_API_KEY"):
            monkeypatch.delenv(name)


def say(capsys: pytest.CaptureFixture[str], *args: str) -> tuple[int, str, str]:
    code = main(["--color", "never", *args])
    out = capsys.readouterr()
    return code, out.out, out.err


def settle(root: Path, text: str) -> None:
    (root / FILE).write_text(f"---\n{text}---\nNotes about this machine.\n", "utf-8")


def resolved(root: Path, **flags: str | None) -> theatre.Theatre:
    return theatre.resolve(root, os.environ, **flags)


def test_a_vault_is_found_from_a_folder_inside_it(
    vault: Vault, keys_dir: Path, monkeypatch: pytest.MonkeyPatch, capsys
) -> None:
    deep = vault.path / "pages" / "deeper"
    deep.mkdir(parents=True)
    assert theatre.find(deep) == vault.path.resolve()
    monkeypatch.chdir(deep)
    assert say(capsys, "--keys", str(keys_dir), "write", "a", "n=1", "--as", "alice")[0] == 0
    assert say(capsys, "--keys", str(keys_dir), "verify")[0] == 0


def test_the_vault_flag_wins_over_the_folder(
    tmp_path: Path, vault: Vault, monkeypatch: pytest.MonkeyPatch, capsys
) -> None:
    other = Vault.init(tmp_path / "other", tmp_path / "k2")
    other.write("only-here", {"n": 1}, None, actor="alice", at=AT)
    monkeypatch.chdir(vault.path)
    assert say(capsys, "--vault", str(other.path), "read", "only-here")[0] == 0
    assert say(capsys, "read", "only-here")[0] == 1


def test_no_vault_found_is_the_error_of_today(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys
) -> None:
    empty = tmp_path / "empty"
    empty.mkdir()
    monkeypatch.chdir(empty)
    assert theatre.find(empty) is None
    code, _, err = say(capsys, "log")
    assert code == 1 and "is not a vault: create one with `conky init" in err


def test_with_no_file_every_setting_is_its_default(vault: Vault) -> None:
    found = resolved(vault.path)
    assert found.file is None
    assert (found.name.value, found.name.source) == (vault.path.name, theatre.DEFAULT)
    assert (found.domain.value, found.full_name) == ("local", f"{vault.path.name}.local")
    assert found.keys_dir() is None and found.keys.source == theatre.DEFAULT
    assert found.cache_dir() == cache.default_dir() and found.provider.value is None
    assert found.overlay(os.environ) == {}
    assert resolved(vault.path.parent / "Odd Name").name.value == "theatre"


def test_each_key_takes_effect(vault: Vault) -> None:
    settle(
        vault.path,
        "name: lemon\ndomain: home\nkeys: ks\ncache: store\nprovider: claude\nmodel: m1\n"
        "command:\n  stand: python3 stand.py\n",
    )
    found = resolved(vault.path)
    assert found.full_name == "lemon.home"
    assert found.keys_dir() == vault.path.resolve() / "ks"
    assert found.cache_dir() == vault.path.resolve() / "store"
    assert found.overlay(os.environ) == {
        "CONKY_PROVIDER": "claude",
        "CONKY_MODEL": "m1",
        "CONKY_COMMAND_STAND": "python3 stand.py",
    }
    assert {s.source for s in (found.name, found.domain, found.keys, found.cache)} == {FILE}


def test_the_file_reaches_the_commands(
    vault: Vault, monkeypatch: pytest.MonkeyPatch, capsys
) -> None:
    settle(vault.path, "provider: none\ncache: held\n")
    monkeypatch.chdir(vault.path)
    code, out, _ = say(capsys, "model")
    assert code == 0 and "no model is available" in out
    code, out, _ = say(capsys, "cache")
    assert str(vault.path.resolve() / "held") in out
    assert "CONKY_PROVIDER" not in os.environ


def test_flag_then_environment_then_file_then_default(
    vault: Vault, monkeypatch: pytest.MonkeyPatch
) -> None:
    settle(vault.path, "keys: from-file\ncache: from-file\nprovider: claude\nmodel: file\n")
    found = resolved(vault.path)
    assert [found.keys.source, found.cache.source, found.provider.source] == [FILE] * 3
    monkeypatch.setenv("CONKY_PROVIDER", "codex")
    monkeypatch.setenv("CONKY_MODEL", "env")
    monkeypatch.setenv("CONKY_CACHE_DIR", "/tmp/env-cache")
    found = resolved(vault.path)
    assert (found.provider.value, found.provider.source) == ("codex", "environment")
    assert (found.model.value, found.model.source) == ("env", "environment")
    assert (found.cache.value, found.cache.source) == ("/tmp/env-cache", "environment")
    assert found.overlay(os.environ) == {}
    found = resolved(vault.path, keys="/k", cache_dir="/c")
    assert (found.keys.value, found.keys.source) == ("/k", "flag")
    assert (found.cache.value, found.cache.source) == ("/c", "flag")


def test_a_variable_in_the_environment_beats_the_file_for_a_command(
    vault: Vault, monkeypatch: pytest.MonkeyPatch
) -> None:
    settle(vault.path, "command:\n  stand: from-file\n")
    monkeypatch.setenv("CONKY_COMMAND_STAND", "from-env")
    assert resolved(vault.path).commands["stand"].source == "environment"
    assert resolved(vault.path).overlay(os.environ) == {}


@pytest.mark.parametrize("path", WRONG, ids=lambda p: p.stem)
def test_a_wrong_settings_file_is_refused_when_read(path: Path, vault: Vault) -> None:
    plan = load_value(path.read_text(encoding="utf-8"))
    (vault.path / FILE).write_text(plan["file"], encoding="utf-8")
    with pytest.raises(BadInput) as refused:
        theatre.read(vault.path)
    assert plan["refused"] in str(refused.value), f"{path.stem}: {refused.value}"


def test_an_unknown_key_names_the_ones_allowed(vault: Vault) -> None:
    settle(vault.path, "colour: red\n")
    with pytest.raises(BadInput, match="colour is not a setting: use one of name, domain, keys"):
        theatre.read(vault.path)


def test_a_malformed_file_stops_the_command_with_advice(
    vault: Vault, monkeypatch: pytest.MonkeyPatch, capsys
) -> None:
    settle(vault.path, "api_key: abc\n")
    monkeypatch.chdir(vault.path)
    code, _, err = say(capsys, "log")
    assert code == 1 and "marionette.md: api_key looks like a secret" in err


def test_the_file_is_excluded_after_init_and_never_in_the_history(
    tmp_path: Path, keys_dir: Path, capsys
) -> None:
    assert say(capsys, "--keys", str(keys_dir), "init", str(tmp_path / "v"))[0] == 0
    root = tmp_path / "v"
    assert FILE in (root / ".git" / "info" / "exclude").read_text("utf-8")
    settle(root, "name: lemon\n")
    assert git(root, "status", "--porcelain") == ""
    assert Vault(root, keys_dir).write("a", {"n": 1}, None, actor="alice", at=AT).ok
    assert git(root, "ls-files", FILE) == ""
    Vault(root, keys_dir).verify()


def test_a_first_read_excludes_a_file_written_by_hand(vault: Vault) -> None:
    exclude = vault.path / ".git" / "info" / "exclude"
    exclude.write_text("", encoding="utf-8")
    settle(vault.path, "name: lemon\n")
    assert git(vault.path, "status", "--porcelain").strip() == f"?? {FILE}"
    resolved(vault.path)
    assert git(vault.path, "status", "--porcelain") == ""
    resolved(vault.path)
    assert exclude.read_text("utf-8").splitlines().count(FILE) == 1


def test_a_tracked_file_fails_verify_with_advice(vault: Vault) -> None:
    vault.write("a", {"n": 1}, None, actor="alice", at=AT)
    settle(vault.path, "name: lemon\n")
    git(vault.path, "add", "-f", FILE)
    with pytest.raises(VerifyFailed, match="git rm --cached marionette.md"):
        vault.verify()
    git(vault.path, "-c", "commit.gpgsign=false", "commit", "-qm", "oops")
    git(vault.path, "rm", "-q", "--cached", FILE)
    git(vault.path, "-c", "commit.gpgsign=false", "commit", "-qm", "gone")
    with pytest.raises(VerifyFailed, match="is in the history"):
        vault.verify()


def test_a_clone_arrives_without_the_file_and_verifies(
    tmp_path: Path, vault: Vault, keys_dir: Path
) -> None:
    vault.write("a", {"n": 1}, None, actor="alice", at=AT)
    settle(vault.path, "name: lemon\nprovider: none\n")
    clone = tmp_path / "clone"
    subprocess.run(["git", "clone", "-q", str(vault.path), str(clone)], check=True)
    assert not (clone / FILE).exists()
    Vault(clone, keys_dir).verify()
    found = resolved(clone)
    assert found.file is None and found.provider.source == theatre.DEFAULT


def test_one_vault_in_two_folders_has_one_history(tmp_path: Path, vault: Vault) -> None:
    vault.write("a", {"n": 1}, None, actor="alice", at=AT)
    twin = tmp_path / "twin"
    subprocess.run(["git", "clone", "-q", str(vault.path), str(twin)], check=True)
    settle(vault.path, "name: lemon\ndomain: home\nprovider: none\n")
    settle(twin, "name: pear\ndomain: farm\nprovider: claude\n")
    short = git(vault.path, "rev-list", "--max-parents=0", "main").strip()[:8]
    assert resolved(vault.path).full_name == f"lemon-{short}.home"
    assert resolved(twin).full_name == f"pear-{short}.farm"
    log = ["log", "main", "--format=%H%B"]
    assert git(vault.path, *log) == git(twin, *log)


def test_the_theatre_command_prints_sources_and_never_a_secret(
    vault: Vault, monkeypatch: pytest.MonkeyPatch, capsys
) -> None:
    settle(vault.path, "name: lemon\nmodel: m1\n")
    (vault.path / "keys").mkdir(exist_ok=True)
    monkeypatch.chdir(vault.path / "keys")
    monkeypatch.setenv("CONKY_PROVIDER", "none")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-very-private")
    monkeypatch.setenv("CONKY_SECRET_STAND", "hunter2")
    code, out, _ = say(capsys, "theatre")
    assert code == 0
    assert "theatre: lemon.local" in out and f"vault: {vault.path.resolve()}" in out
    assert "name: lemon (marionette.md)" in out and "domain: local (default)" in out
    assert "provider: none (environment)" in out and "model: m1 (marionette.md)" in out
    assert "keys: ~/.conky/keys (default)" in out
    assert "secret ANTHROPIC_API_KEY: set" in out and "secret OPENAI_API_KEY: not set" in out
    assert "secret CONKY_SECRET_STAND: set" in out
    assert "sk-very-private" not in out and "hunter2" not in out


def test_the_theatre_command_works_where_there_is_no_vault(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys
) -> None:
    monkeypatch.chdir(tmp_path)
    code, out, _ = say(capsys, "theatre")
    assert code == 0 and "every setting is its default" in out


def test_a_repository_that_is_no_vault_is_not_found_from_inside_it(tmp_path: Path) -> None:
    other = tmp_path / "project"
    (other / ".git").mkdir(parents=True)
    deep = other / "src" / "lib"
    deep.mkdir(parents=True)
    assert theatre.find(deep) is None
    assert theatre.find(other) == other.resolve()
