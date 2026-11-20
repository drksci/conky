"""A provider can be a program on this machine, and a model can be detected with no page.

No test reaches a live model: the programs are small scripts written by the tests.
"""

import shutil
import stat
import sys
from pathlib import Path

import pytest

from conky import Vault, arch, model
from conky.cli import main
from conky.git import trailers

from .conftest import AT, git

PROMPT = "Say hello to ![[ticket#text]]"


def w(vault: Vault, page: str, changes: dict, actor: str = "alice"):
    return vault.write(page, changes, None, actor=actor, at=AT)


def script(tmp_path: Path, name: str, body: str) -> str:
    """Write a Python program that reads standard input and return its path."""
    path = tmp_path / f"{name}.py"
    path.write_text("import sys, time\nprompt = sys.stdin.read()\n" + body, encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IXUSR)
    return str(path)


def program(monkeypatch: pytest.MonkeyPatch, name: str, path: str) -> None:
    monkeypatch.setenv(f"CONKY_COMMAND_{name.upper()}", f"{sys.executable} {path}")


def provider(vault: Vault, command: str = "echo", **extra: object) -> None:
    assert w(vault, "helper", {"api": "command", "command": command, **extra}).ok


def asked(vault: Vault, provider_name: str | None = "helper"):
    assert w(vault, "ticket", {"text": "printer"}).ok
    return vault.ask("desk", "summary", provider=provider_name, prompt=PROMPT, actor="alice", at=AT)


def refusal(vault: Vault) -> str:
    """The reason of the refusal recorded just before the plain sentence."""
    return trailers(git(vault.path, "log", "-1", "--format=%B", "HEAD~1"))["Reason"]


def head(vault: Vault) -> dict[str, str]:
    return trailers(git(vault.path, "log", "-1", "--format=%B"))


@pytest.fixture(autouse=True)
def clean_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in (
        "CONKY_MODEL",
        "ANTHROPIC_API_KEY",
        "OPENAI_API_KEY",
        "CONKY_COMMAND_ECHO",
        "CONKY_COMMAND_CLAUDE",
        "CONKY_COMMAND_CODEX",
    ):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("CONKY_PROVIDER", "none")


def test_the_prompt_goes_to_standard_input_and_trimmed_output_is_the_answer(
    vault: Vault, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    program(monkeypatch, "echo", script(tmp_path, "echo", "print('heard: ' + prompt + '  \\n\\n')"))
    provider(vault)
    result = asked(vault)
    assert result.ok
    assert vault.read("desk").fields["summary"] == "heard: Say hello to printer"
    text = git(vault.path, "log", "-1", "--format=%B")
    found = trailers(text)
    assert found["Model"] == "helper" and found["Model-Name"] == "echo"
    assert found["Read"] == "ticket"
    assert "Tokens-In" not in found and "Tokens-Out" not in found
    vault.verify()


def test_the_model_field_names_the_model_in_the_commit_and_sends_nothing_extra(
    vault: Vault, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    program(monkeypatch, "echo", script(tmp_path, "echo", "print(sys.argv[1:])"))
    provider(vault, model="some-model", max_tokens=5)
    assert asked(vault).ok
    assert vault.read("desk").fields["summary"] == "[]"
    assert trailers(git(vault.path, "log", "-1", "--format=%B"))["Model-Name"] == "some-model"


def test_the_argv_comes_from_a_file_in_the_key_directory(
    vault: Vault, keys_dir: Path, tmp_path: Path
) -> None:
    keys_dir.mkdir(exist_ok=True)
    path = script(tmp_path, "echo", "print('from file')")
    (keys_dir / "echo.command").write_text(f'{sys.executable} "{path}"\n', encoding="utf-8")
    provider(vault)
    assert asked(vault).ok
    assert vault.read("desk").fields["summary"] == "from file"


def test_the_environment_wins_over_the_file(
    vault: Vault, keys_dir: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    keys_dir.mkdir(exist_ok=True)
    (keys_dir / "echo.command").write_text("false", encoding="utf-8")
    program(monkeypatch, "echo", script(tmp_path, "echo", "print('env')"))
    provider(vault)
    assert asked(vault).ok
    assert vault.read("desk").fields["summary"] == "env"


def test_the_argv_is_split_into_words_and_never_run_through_a_shell(
    vault: Vault, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = script(tmp_path, "echo", "print(sys.argv[1:])")
    monkeypatch.setenv("CONKY_COMMAND_ECHO", f"{sys.executable} {path} 'a b' $HOME; touch pwned")
    provider(vault)
    assert asked(vault).ok
    assert vault.read("desk").fields["summary"] == "['a b', '$HOME;', 'touch', 'pwned']"
    assert not Path("pwned").exists()


@pytest.mark.parametrize(
    ("how", "words"),
    [
        ("exit", ["exited with status 3", "boom"]),
        ("sleep", ["no answer in", "then ask again"]),
        ("silent", ["printed no answer"]),
        ("missing", ["cannot start", "CONKY_COMMAND_ECHO"]),
        ("unset", ["is not set up", "CONKY_COMMAND_ECHO", "echo.command"]),
    ],
)
def test_every_failure_is_a_model_refusal_that_says_what_to_do(
    vault: Vault, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, how: str, words: list[str]
) -> None:
    monkeypatch.setattr(model, "COMMAND_TIMEOUT", 1)
    bodies = {
        "exit": "sys.stderr.write('boom'); sys.exit(3)",
        "sleep": "time.sleep(30)",
        "silent": "print('   ')",
    }
    if how in bodies:
        program(monkeypatch, "echo", script(tmp_path, "echo", bodies[how]))
    elif how == "missing":
        monkeypatch.setenv("CONKY_COMMAND_ECHO", str(tmp_path / "no-such-program"))
    provider(vault)
    result = asked(vault)
    assert result.ok and result.plain
    reason = refusal(vault)
    assert reason.startswith("model: ") and all(word in reason for word in words)
    assert head(vault)["Model"] == "none"
    assert vault.read("desk").fields["summary"].startswith("No model was around")
    vault.verify()


@pytest.mark.parametrize(
    "value",
    ["rm -rf /", "echo hi", "/bin/sh", "../x", "a;b", "$(x)", "Echo", "", "a b", 3, None, ["echo"]],
)
def test_a_vault_cannot_make_a_machine_run_anything_but_a_named_command(
    vault: Vault, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, value: object
) -> None:
    mark = tmp_path / "ran"
    monkeypatch.setenv("CONKY_COMMAND_ECHO", f"{sys.executable} -c \"open('{mark}', 'w')\"")
    assert w(vault, "helper", {"api": "command", "command": value, "argv": ["touch", str(mark)]}).ok
    assert asked(vault).plain
    assert "never a command line" in refusal(vault)
    assert not mark.exists()


def test_a_page_cannot_supply_an_argv_even_beside_a_valid_name(
    vault: Vault, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    mark = tmp_path / "ran"
    program(monkeypatch, "echo", script(tmp_path, "echo", "print('safe')"))
    provider(vault, argv=["touch", str(mark)], args="touch x", url="http://127.0.0.1:1")
    assert asked(vault).ok
    assert not mark.exists()


def test_a_watch_entry_on_a_command_provider_asks_as_the_page(
    vault: Vault, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    program(monkeypatch, "echo", script(tmp_path, "echo", "print('ok')"))
    provider(vault)
    ask = {"provider": "helper", "prompt": PROMPT, "into": "summary"}
    assert w(vault, "ticket", {"status": "old", "text": "printer"}).ok
    watch = [{"on": "ticket", "when": "other.status == 'new'", "ask": ask}]
    assert w(vault, "desk", {"watch": watch}).ok
    assert w(vault, "ticket", {"status": "new"}).ok
    assert vault.read("desk").fields["summary"] == "ok"


# Detection and the cascade


def path_with(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, *names: str) -> None:
    """Make PATH hold git, ssh-keygen and the named fake programs, and nothing else."""
    folder = tmp_path / "bin"
    shutil.rmtree(folder, ignore_errors=True)
    folder.mkdir()
    for real in ("git", "ssh-keygen"):
        link = folder / real
        if not link.exists():
            link.symlink_to(shutil.which(real) or real)
    for name in names:
        tool = folder / name
        tool.write_text("#!/bin/sh\n", encoding="utf-8")
        tool.chmod(0o755)
    monkeypatch.setenv("PATH", str(folder))


def pages(found: model.Detected) -> list[str]:
    return [c.provider.page for c in found.choices]


@arch.holds("law.fallback.always", "flow.ask.model")
def test_detection_lists_anthropic_then_openai_then_claude_then_codex(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("CONKY_PROVIDER")
    path_with(tmp_path, monkeypatch, "claude", "codex")
    monkeypatch.setenv("OPENAI_API_KEY", "o")
    monkeypatch.setenv("CONKY_MODEL", "m")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "a")
    found = model.detect()
    assert pages(found) == [f"detected:{n}" for n in ("anthropic", "openai", "claude", "codex")]
    assert found.choices[0].provider.name == "m" and found.choices[0].secret == "a"
    monkeypatch.setenv("CONKY_PROVIDER", "codex")
    assert pages(model.detect())[:2] == ["detected:codex", "detected:anthropic"]
    monkeypatch.delenv("CONKY_PROVIDER")
    monkeypatch.delenv("ANTHROPIC_API_KEY")
    assert pages(model.detect())[0] == "detected:openai"
    monkeypatch.delenv("OPENAI_API_KEY")
    assert pages(model.detect()) == ["detected:claude", "detected:codex"]
    path_with(tmp_path, monkeypatch, "codex")
    assert pages(model.detect()) == ["detected:codex"]
    path_with(tmp_path, monkeypatch)
    assert model.detect().choices == []


def test_none_lists_nothing_even_when_a_key_is_set(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ANTHROPIC_API_KEY", "a")
    assert model.detect().choices == []


def test_anthropic_has_a_default_model_and_openai_is_skipped_without_one(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("CONKY_PROVIDER")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "a")
    found = model.detect().choices[0].provider
    assert found.name == model.ANTHROPIC_DEFAULT_MODEL
    monkeypatch.delenv("ANTHROPIC_API_KEY")
    monkeypatch.setenv("OPENAI_API_KEY", "o")
    skipped = model.detect()
    assert not any(c.provider.api == "openai" for c in skipped.choices)
    assert any("set CONKY_MODEL" in note for note in skipped.notes)


def test_an_unknown_provider_choice_is_ignored_with_a_note(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path_with(tmp_path, monkeypatch, "claude")
    monkeypatch.setenv("CONKY_PROVIDER", "gemini")
    found = model.detect()
    assert pages(found) == ["detected:claude"]
    assert "anthropic, openai, claude, codex, none" in found.notes[0]


def test_an_ask_with_no_provider_runs_the_detected_command_and_records_it(
    vault: Vault, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("CONKY_PROVIDER")
    path_with(tmp_path, monkeypatch, "claude")
    program(monkeypatch, "claude", script(tmp_path, "claude", "print('detected')"))
    assert asked(vault, None).ok
    assert vault.read("desk").fields["summary"] == "detected"
    found = head(vault)
    assert found["Model"] == "detected:claude" and found["Model-Name"] == "claude"


@arch.holds("law.fallback.always", "flow.ask.model")
def test_a_failing_detected_model_falls_to_the_next_and_then_to_a_sentence(
    vault: Vault, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("CONKY_PROVIDER")
    path_with(tmp_path, monkeypatch, "claude", "codex")
    program(monkeypatch, "claude", script(tmp_path, "claude", "sys.exit(1)"))
    program(monkeypatch, "codex", script(tmp_path, "codex", "print('second')"))
    assert asked(vault, None).ok
    assert vault.read("desk").fields["summary"] == "second"
    assert head(vault)["Model"] == "detected:codex"
    program(monkeypatch, "codex", script(tmp_path, "codex", "print('')"))
    result = asked(vault, None)
    assert result.plain and head(vault)["Model"] == "none"


@arch.holds("flow.ask.model")
def test_a_failing_named_page_is_recorded_and_the_detected_models_still_answer(
    vault: Vault, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("CONKY_PROVIDER")
    path_with(tmp_path, monkeypatch, "claude")
    program(monkeypatch, "claude", script(tmp_path, "claude", "print('rescued')"))
    program(monkeypatch, "echo", script(tmp_path, "echo", "sys.exit(2)"))
    provider(vault)
    assert asked(vault).ok
    assert refusal(vault).startswith("model: ")
    assert vault.read("desk").fields["summary"] == "rescued"
    assert head(vault)["Model"] == "detected:claude"


@pytest.mark.parametrize("how", ["missing-page", "unknown-api"])
def test_a_broken_provider_page_is_recorded_and_the_asking_page_still_gets_a_sentence(
    vault: Vault, how: str
) -> None:
    if how == "unknown-api":
        assert w(vault, "helper", {"api": "carrier-pigeon"}).ok
    assert asked(vault).plain
    assert "model: provider page 'helper'" in refusal(vault)
    vault.verify()


@arch.holds("law.fallback.always")
def test_with_no_model_an_ask_writes_a_sentence_that_names_the_question(
    vault: Vault,
) -> None:
    result = asked(vault, None)
    assert result.ok and result.plain
    summary = vault.read("desk").fields["summary"]
    assert summary == (
        'No model was around to answer "Say hello to printer", so desk keeps this line in '
        "summary until one is."
    )
    found = head(vault)
    assert found["Model"] == "none" and found["Read"] == "ticket" and "Model-Name" not in found
    assert "summary_asked" not in vault.read("desk").fields
    vault.verify()


def test_a_long_question_is_cut_in_the_sentence() -> None:
    sentence = model.plain_sentence("desk", "note", "word " * 40)
    assert sentence.count("word") < 40 and '..."' in sentence


def test_a_watch_entry_writes_its_otherwise_sentence_when_no_model_is_available(
    vault: Vault,
) -> None:
    assert w(vault, "ticket", {"status": "old", "text": "printer"}).ok
    ask = {"prompt": PROMPT, "into": "summary", "otherwise": "A note about ![[ticket#text]]."}
    watch = [{"on": "ticket", "when": "other.status == 'new'", "ask": ask}]
    assert w(vault, "desk", {"watch": watch}).ok
    assert w(vault, "ticket", {"status": "new"}).ok
    assert vault.read("desk").fields["summary"] == "A note about printer."
    assert head(vault)["Model"] == "none"
    vault.verify()


@arch.holds("flow.ask.model")
def test_a_sentence_is_not_a_settled_answer_so_a_later_model_replaces_it(
    vault: Vault, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    assert w(vault, "ticket", {"status": "old", "text": "printer"}).ok
    ask = {"prompt": PROMPT, "into": "summary"}
    watch = [{"on": "ticket", "when": "other.status == 'new'", "ask": ask}]
    assert w(vault, "desk", {"watch": watch}).ok
    assert w(vault, "ticket", {"status": "new"}).ok
    assert vault.read("desk").fields["summary"].startswith("No model was around")
    before = len(vault.log())
    assert w(vault, "ticket", {"status": "new", "n": 1}).ok
    assert len(vault.log()) == before + 1
    monkeypatch.setenv("CONKY_PROVIDER", "claude")
    path_with(tmp_path, monkeypatch, "claude")
    program(monkeypatch, "claude", script(tmp_path, "claude", "print('real')"))
    assert w(vault, "ticket", {"status": "new", "n": 2}).ok
    assert vault.read("desk").fields["summary"] == "real"
    assert "summary_asked" in vault.read("desk").fields
    before = len(vault.log())
    assert w(vault, "ticket", {"status": "new", "n": 3}).ok
    assert vault.read("desk").fields["summary"] == "real"
    assert len(vault.log()) == before + 1


def test_a_named_provider_page_wins_over_detection(
    vault: Vault, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    program(monkeypatch, "echo", script(tmp_path, "echo", "print('page')"))
    provider(vault)
    assert asked(vault).ok
    assert vault.read("desk").fields["summary"] == "page"


def test_conky_model_shows_the_order_and_what_happens_if_all_fail(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.delenv("CONKY_PROVIDER")
    path_with(tmp_path, monkeypatch, "claude", "codex")
    assert main(["model"]) == 0
    out = capsys.readouterr().out
    assert "detected:claude: claude is on the PATH" in out
    assert "then detected:codex" in out and "writes a plain sentence" in out
    path_with(tmp_path, monkeypatch)
    assert main(["model"]) == 0
    out = capsys.readouterr().out
    assert "no model is available" in out and "ANTHROPIC_API_KEY" in out


def test_conky_ask_with_no_model_prints_the_sentence_and_a_hint_and_succeeds(
    vault: Vault, keys_dir: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert w(vault, "ticket", {"text": "printer"}).ok
    argv = ["--vault", str(vault.path), "--keys", str(keys_dir), "ask", "desk", "summary"]
    assert main([*argv, "--prompt", "hi", "--as", "alice"]) == 0
    seen = capsys.readouterr()
    assert 'No model was around to answer "hi"' in seen.out
    assert "To give Conky one" in seen.err and "ANTHROPIC_API_KEY" in seen.err


def test_conky_ask_without_a_provider_uses_detection(
    vault: Vault, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, keys_dir: Path
) -> None:
    monkeypatch.delenv("CONKY_PROVIDER")
    path_with(tmp_path, monkeypatch, "codex")
    program(monkeypatch, "codex", script(tmp_path, "codex", "print('cli')"))
    argv = ["--vault", str(vault.path), "--keys", str(keys_dir), "ask", "desk", "summary"]
    assert main([*argv, "--prompt", "hi", "--as", "alice"]) == 0
    assert vault.read("desk").fields["summary"] == "cli"


def test_a_missing_key_directory_or_an_unreadable_file_never_breaks_asking(
    vault: Vault, keys_dir: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    assert not keys_dir.joinpath("echo.command").exists()
    provider(vault)
    assert asked(vault).plain
    assert "is not set up" in refusal(vault)
    keys_dir.mkdir(exist_ok=True)
    (keys_dir / "echo.command").write_bytes(b"\xff\xfe\x00")
    assert asked(vault).plain
    assert "cannot read echo.command" in refusal(vault)
    vault.verify()


def test_a_command_provider_starts_in_an_empty_folder_and_sees_only_its_prompt(
    vault: Vault, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A model sees its prompt and nothing else: no project files lie about where it starts."""
    body = "import os\nprint('files', len(os.listdir('.')), os.getcwd() == os.environ['STARTED'])\n"
    program(monkeypatch, "echo", script(tmp_path, "where", body))
    monkeypatch.setenv("STARTED", str(Path.cwd()))
    provider(vault)
    assert asked(vault).ok
    assert vault.read("desk").fields["summary"] == "files 0 False"
    assert model.BUILTIN_COMMANDS["claude"][:4] == ["claude", "-p", "--tools", ""]
