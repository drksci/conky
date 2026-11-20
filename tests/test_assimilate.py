import subprocess
import sys
from importlib import resources
from pathlib import Path

import pytest

from conky import arch, style
from conky.cli import main
from conky.vault import Vault

from .conftest import git, signed_by

ROOT = Path(__file__).resolve().parent.parent
STOPPED = resources.files("conky") / "stopped"
BUNDLE = Path(str(STOPPED / "lemonade.bundle"))


def take(tmp_path: Path, *args: str, color: str = "never") -> int:
    return main(["--color", color, "assimilate", *args])


def stopped_copy(tmp_path: Path, name: str = "source") -> Path:
    """A plain clone of the packaged vault: a directory someone could hand over."""
    git(tmp_path, "clone", "-q", str(BUNDLE), name)
    return tmp_path / name


@arch.holds("flow.vault.assimilate")
def test_bare_command_takes_checks_carries_on_and_checks_again(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.chdir(tmp_path)
    assert take(tmp_path) == 0
    out = capsys.readouterr().out
    vault = Vault(tmp_path / "conky-assimilated", tmp_path / "keys")
    vault.verify()
    lines = [line.split() for line in vault.log()]
    assert len(lines) == 6
    _, _, actor, kind, page, *_ = lines[4]
    assert (actor, kind, page) == ("newcomer", "write", "cooler")
    assert lines[5][2:5] == ["supplier", "write", "supplier"]
    assert lines[5][5:] == ["cause", lines[4][0]]
    assert signed_by(vault.path, "HEAD~1") == "newcomer@conky"
    assert vault.read("cooler").fields["cups"] == 4
    assert vault.read("supplier").fields["ordered"] is True
    assert "4 commits, 3 pages, 1 space" in out
    assert "Then supplier changed by itself" in out
    assert "What this shows" in out and "no model was involved" in out
    assert "\x1b" not in out


@arch.holds("flow.vault.assimilate")
def test_no_key_of_the_original_author_is_needed_and_the_newcomer_is_listed_at_once(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.chdir(tmp_path)
    assert b"PRIVATE KEY" not in BUNDLE.read_bytes()
    for name in ("lemonade.yaml", "how-it-was-made.txt"):
        assert "PRIVATE KEY" not in (STOPPED / name).read_text(encoding="utf-8")
    assert take(tmp_path) == 0
    keys = tmp_path / "keys"
    assert sorted(p.name for p in keys.iterdir()) == [
        "newcomer",
        "newcomer.pub",
        "supplier",
        "supplier.pub",
    ]
    assert not (home / ".conky").exists()
    vault = tmp_path / "conky-assimilated"
    changed = git(vault, "show", "--name-only", "--format=", "HEAD~1").split()
    assert changed == ["keys/allowed_signers", "pages/cooler.md"]
    signers = (vault / "keys" / "allowed_signers").read_text()
    assert signers.count("newcomer@conky") == 1
    assert git(vault, "log", "-1", "--format=%an", "HEAD~1").strip() == "newcomer"


@arch.holds("flow.vault.assimilate")
@pytest.mark.parametrize("form", ["directory", "bundle", "url"])
def test_the_source_can_be_a_directory_a_bundle_or_a_url(
    tmp_path: Path, form: str, capsys: pytest.CaptureFixture[str]
) -> None:
    source = stopped_copy(tmp_path)
    if form == "bundle":
        shipped = tmp_path / "again.bundle"
        git(source, "bundle", "create", str(shipped), "--all")
        given = str(shipped)
    else:
        given = source.as_uri() if form == "url" else str(source)
    into, keys = tmp_path / "taken", tmp_path / "k"
    args = [given, "--into", str(into), "--keys", str(keys), "--then", "cooler", "cups=4"]
    assert take(tmp_path, *args) == 0
    Vault(into, keys).verify()
    log = Vault(into, keys).log()
    assert len(log) == 6 and log[-1].split()[2:5] == ["supplier", "write", "supplier"]
    assert "Then supplier changed by itself" in capsys.readouterr().out


def test_without_then_it_stops_after_reading_and_says_how_to_continue(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    source = stopped_copy(tmp_path)
    into = tmp_path / "taken"
    assert take(tmp_path, str(source), "--into", str(into), "--keys", str(tmp_path / "k")) == 0
    out = capsys.readouterr().out
    assert "stand: not in a space; 0 rules (0 own, 0 inherited)" in out
    assert "cooler: in stand; 1 rule (0 own, 1 inherited)" in out
    assert "supplier: not in a space; 0 rules (0 own, 0 inherited); watches cooler" in out
    flat = " ".join(out.split())
    assert f"conky --vault {into}" in flat and "write PAGE FIELD=VALUE" in flat
    assert len(Vault(into, tmp_path / "k").log()) == 4
    assert not (tmp_path / "k").exists()


@arch.holds("flow.vault.assimilate")
def test_a_tampered_source_fails_at_the_check_and_names_the_problem(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    source = stopped_copy(tmp_path)
    git(source, "commit", "-q", "--allow-empty", "-m", "slipped in")
    into = tmp_path / "taken"
    assert take(tmp_path, str(source), "--into", str(into), "--keys", str(tmp_path / "k")) == 1
    out = capsys.readouterr().out
    assert "failed" in out and "has no good signature" in out
    assert "Check again" not in out and "What this shows" not in out
    assert not (tmp_path / "k").exists()


def test_then_writes_run_in_order_and_a_refusal_alone_does_not_fail_the_run(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    into, keys = tmp_path / "taken", tmp_path / "k"
    args = [str(BUNDLE), "--into", str(into), "--keys", str(keys), "--as", "carol"]
    args += ["--then", "cooler", "cups=-1", "--then", "cooler", "cups=4"]
    assert take(tmp_path, *args) == 0
    out = capsys.readouterr().out
    assert "refused: cooler, because rule: " in out
    assert "(from stand) is false" in out
    kinds = [line.split()[3:5] for line in Vault(into, keys).log()[4:]]
    assert kinds == [["refused", "cooler"], ["write", "cooler"], ["write", "supplier"]]
    assert out.index("refused: cooler") < out.index("written: cooler")


def test_into_an_existing_folder_fails_helpfully(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert take(tmp_path, "--into", str(tmp_path)) == 1
    captured = capsys.readouterr()
    assert "already exists" in captured.err and "--into" in captured.err
    assert captured.out == ""


def test_a_source_that_cannot_be_cloned_says_what_to_give(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert take(tmp_path, str(tmp_path / "nowhere"), "--into", str(tmp_path / "t")) == 1
    err = capsys.readouterr().err
    assert "cannot take" in err and "a vault directory, a bundle file" in err


def test_a_name_that_already_has_a_key_is_refused_before_any_write(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    keys = tmp_path / "k"
    keys.mkdir()
    (keys / "newcomer").write_text("taken")
    assert take(tmp_path, "--into", str(tmp_path / "t"), "--keys", str(keys)) == 1
    assert "already exists" in capsys.readouterr().err
    assert len(Vault(tmp_path / "t", keys).log()) == 4


def test_plain_output_has_no_escape_codes_and_styled_output_loses_nothing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    shown = {}
    for mode in ("never", "always"):
        place = tmp_path / mode
        place.mkdir()
        monkeypatch.chdir(place)
        args = [str(BUNDLE), "--then", "cooler", "cups=-1", "--then", "cooler", "cups=4"]
        assert take(place, *args, color=mode) == 0
        shown[mode] = capsys.readouterr().out
    plain, styled = shown["never"], shown["always"]
    assert "\x1b" not in plain and "\x1b" in styled
    for badge in ("✓ taken", "✓ verified", "✓ written", "✗ refused", "↳"):
        assert badge in style.strip(styled)
    stripped = " ".join(style.strip(styled).split())
    for fact in (
        "supplier: not in a space; 0 rules (0 own, 0 inherited); watches cooler",
        "because rule: ",
        "(from stand) is false",
        "cause",
        "no model was involved",
    ):
        assert fact in " ".join(plain.split())
        assert fact in stripped


def test_the_packaged_bundle_is_reproducible(tmp_path: Path) -> None:
    rebuilt = tmp_path / "rebuilt.bundle"
    subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "build_stopped_vault.py"), str(rebuilt)],
        check=True,
        capture_output=True,
    )
    git(tmp_path, "clone", "-q", str(rebuilt), "new")
    git(tmp_path, "clone", "-q", str(BUNDLE), "shipped")
    ids = git(tmp_path / "new", "rev-list", "main")
    assert ids == git(tmp_path / "shipped", "rev-list", "main")
    assert len(ids.split()) == 4
