import os
from pathlib import Path

import pytest

from conky.cli import main

from .conftest import git


def run(tmp_path: Path, *args: str) -> int:
    return main(["--vault", str(tmp_path / "v"), "--keys", str(tmp_path / "k"), *args])


def test_cli_init_write_refuse_read_log_verify_rebuild(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert main(["--keys", str(tmp_path / "k"), "init", str(tmp_path / "v")]) == 0
    assert (
        run(tmp_path, "write", "market", 'rules=["page.stock >= 0"]', "stock=0", "--as", "alice")
        == 0
    )
    assert run(tmp_path, "write", "stall", "within=market", "stock=40", "--as", "alice") == 0
    capsys.readouterr()
    assert run(tmp_path, "read", "stall") == 0
    assert capsys.readouterr().out == "---\nwithin: market\nstock: 40\n---\n"
    assert run(tmp_path, "write", "stall", "stock=-1", "--as", "alice") == 1
    assert "rule: page.stock >= 0" in capsys.readouterr().err
    assert run(tmp_path, "log") == 0
    lines = capsys.readouterr().out.splitlines()
    assert [line.split()[3:5] for line in lines] == [
        ["write", "market"],
        ["write", "stall"],
        ["refused", "stall"],
    ]
    assert run(tmp_path, "verify") == 0
    assert capsys.readouterr().out == "ok: 3 commits verified\n"
    (tmp_path / "v" / "pages" / "stall.md").unlink()
    assert run(tmp_path, "verify") == 1
    assert "rebuild" in capsys.readouterr().err
    assert run(tmp_path, "rebuild") == 0
    assert run(tmp_path, "verify") == 0
    assert git(tmp_path / "v", "log", "--oneline").count("\n") == 3


def test_cli_hand_edit_fails_verify_and_names_the_fix(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    main(["--keys", str(tmp_path / "k"), "init", str(tmp_path / "v")])
    run(tmp_path, "write", "stall", "stock=1", "--as", "alice")
    page = tmp_path / "v" / "pages" / "stall.md"
    page.write_text(page.read_text().replace("1", "2"))
    capsys.readouterr()
    assert run(tmp_path, "write", "stall", "stock=3", "--as", "alice") == 1
    assert "conky --vault" in capsys.readouterr().err
    assert run(tmp_path, "verify") == 1


def test_cli_outside_a_vault_says_how_to_start(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert main(["--vault", str(tmp_path), "log"]) == 1
    assert "conky init" in capsys.readouterr().err


def test_cli_missing_tool_says_what_to_install(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("PATH", str(tmp_path))
    assert main(["init", str(tmp_path / "v")]) == 1
    assert "install" in capsys.readouterr().err
    assert os.environ["PATH"] == str(tmp_path)
