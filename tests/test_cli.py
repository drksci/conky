from pathlib import Path

import pytest

from conky.cli import main


def run(tmp_path: Path, *args: str) -> int:
    return main(["--vault", str(tmp_path / "v"), "--keys", str(tmp_path / "k"), *args])


def test_cli_init_write_read_verify(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
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
    assert run(tmp_path, "verify") == 0
    assert run(tmp_path, "rebuild") == 0
    assert run(tmp_path, "verify") == 0


def test_cli_verify_fails_with_nonzero_exit(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    main(["--keys", str(tmp_path / "k"), "init", str(tmp_path / "v")])
    run(tmp_path, "write", "stall", "stock=1", "--as", "alice")
    page = tmp_path / "v" / "pages" / "stall.md"
    page.write_text(page.read_text().replace("1", "2"))
    capsys.readouterr()
    assert run(tmp_path, "verify") == 1
    assert "stall" in capsys.readouterr().err
