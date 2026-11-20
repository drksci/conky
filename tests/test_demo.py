from pathlib import Path

import pytest

from conky import demo
from conky.cli import main
from conky.errors import BadInput


def run_demo(tmp_path: Path, *args: str) -> int:
    return main(["--keys", str(tmp_path / "k"), "demo", *args])


@pytest.mark.parametrize("name", ["stall", "team"])
def test_example_files_validate(name: str) -> None:
    example = demo.load(name)
    assert example.steps
    assert all(step.say and (step.fields or step.body) for step in example.steps)


def test_a_malformed_example_is_named_and_explained() -> None:
    with pytest.raises(BadInput, match="step 1 needs a narration line"):
        demo.parse(
            "x",
            {
                "title": "t",
                "summary": "s",
                "look_at": "p",
                "steps": [{"say": " ", "write": {"page": "p", "actor": "a", "fields": {"n": 1}}}],
            },
        )


def test_demo_stall_runs_verifies_and_records_refusal_and_reaction(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    vault = tmp_path / "vault"
    assert run_demo(tmp_path, "--into", str(vault)) == 0
    out = capsys.readouterr().out
    assert "refused: stall" in out
    assert "Then depot changed by itself" in out
    assert "\x1b" not in out
    assert max(len(x) for x in out.splitlines() if str(vault) not in x) <= 80
    assert f"git -C {vault} log --oneline" in out
    assert f"conky --vault {vault} read depot" in out
    log = main(["--vault", str(vault), "log"])
    history = capsys.readouterr().out.splitlines()
    assert log == 0
    assert any(" refused stall " in line for line in history)
    assert any(" depot write depot cause " in line for line in history)
    assert any(" journal write journal cause " in line for line in history)
    assert main(["--vault", str(vault), "verify"]) == 0


def test_demo_team_runs_and_verifies(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    vault = tmp_path / "vault"
    assert run_demo(tmp_path, "team", "--into", str(vault)) == 0
    out = capsys.readouterr().out
    assert "refused: task-1" in out
    assert "Then board changed by itself" in out
    assert main(["--vault", str(vault), "verify"]) == 0


def test_demo_keys_default_to_a_folder_beside_the_vault(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert main(["demo", "--into", str(tmp_path / "vault")]) == 0
    assert (tmp_path / "keys" / "alice").exists()
    assert not (tmp_path / "vault" / "keys" / "alice").exists()


def test_demo_list_shows_the_examples(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["demo", "--list"]) == 0
    out = capsys.readouterr().out
    assert "stall" in out and "team" in out


def test_demo_into_an_existing_folder_fails_helpfully(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert run_demo(tmp_path, "--into", str(tmp_path)) == 1
    err = capsys.readouterr().err
    assert "already exists" in err and "--into" in err


def test_demo_unknown_example_points_to_the_list(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert run_demo(tmp_path, "nope", "--into", str(tmp_path / "v")) == 1
    assert "demo --list" in capsys.readouterr().err
