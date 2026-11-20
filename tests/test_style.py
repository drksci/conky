import re
from pathlib import Path

import pytest

from conky import demo as examples
from conky import style
from conky.cli import main

ESCAPE = re.compile(r"\x1b\[[0-9;]*m")


def test_visible_len_ignores_escapes() -> None:
    text = style.colour("pink", style.PINK, bold=True) + " " + style.dim("grey")
    assert style.visible_len(text) == len("pink grey")
    assert style.strip(text) == "pink grey"


def test_colours_are_24_bit() -> None:
    assert style.colour("x", "#FF5FAF").startswith("\x1b[38;2;255;95;175m")
    assert "48;2;135;75;253" in style.badge("1", style.PURPLE)


def test_badge_has_one_space_of_padding_each_side() -> None:
    assert style.strip(style.badge("written", style.MINT)) == " written "


def test_box_is_rounded_and_every_line_has_the_same_width() -> None:
    lines = style.box([style.title("Title"), style.dim("a longer line of text")])
    plain = [style.strip(x) for x in lines]
    assert plain[0].startswith("╭─") and plain[0].endswith("─╮")
    assert plain[-1].startswith("╰─") and plain[-1].endswith("─╯")
    assert plain[1].startswith("│ Title") and plain[1].endswith(" │")
    assert len({len(x) for x in plain}) == 1


def test_wrap_measures_visible_characters_and_keeps_long_words() -> None:
    text = f"{style.dim('alpha')} beta gamma /a/very/long/path/that/cannot/break"
    lines = style.wrap(text, 12, "- ", "  ")
    assert all(style.visible_len(x) <= 12 for x in lines[:-1])
    assert style.strip(lines[0]) == "- alpha beta"
    assert style.strip(lines[-1]) == "  /a/very/long/path/that/cannot/break"


def demo(tmp_path: Path, capsys: pytest.CaptureFixture[str], *flags: str) -> str:
    keys = str(tmp_path / "k")
    assert main([*flags, "--keys", keys, "demo", "--into", str(tmp_path / "vault")]) == 0
    return capsys.readouterr().out


def test_plain_output_has_no_escapes_when_not_a_terminal_or_never_or_no_color(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    auto = demo(tmp_path / "a", capsys)
    never = demo(tmp_path / "b", capsys, "--color", "never")
    monkeypatch.setenv("NO_COLOR", "1")
    no_color = demo(tmp_path / "c", capsys, "--color", "auto")
    for out in (auto, never, no_color):
        assert "\x1b" not in out
        assert "refused: stall, because rule:" in out
    assert auto.replace("/a/", "/x/") == never.replace("/b/", "/x/")


def test_always_styles_the_demo_and_loses_nothing(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("COLUMNS", "88")
    plain = demo(tmp_path / "p", capsys, "--color", "never")
    styled = demo(tmp_path / "s", capsys, "--color", "always")
    assert "\x1b[" in styled
    for corner in "╭╮╰╯":
        assert corner in styled
    seen = " ".join(ESCAPE.sub("", styled).split())
    assert "written" in seen and "refused" in seen
    assert "↳ depot changed by itself" in seen
    for step in examples.load("stall").steps:
        assert " ".join(step.say.split()) in seen
    for page in re.findall(r"-> written: (\w+)", plain):
        assert f"written {page}" in seen
    assert re.findall(r"-> refused: (\w+)", plain) == ["stall"]
    assert "refused stall" in seen
    assert "because rule: !has(page.stock) || page.stock >= 0 (from market) is false" in seen


def test_narrow_terminal_keeps_every_styled_line_within_the_width(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("COLUMNS", "60")
    monkeypatch.chdir(tmp_path)
    keys = str(tmp_path / "k")
    assert main(["--color", "always", "--keys", keys, "demo", "--into", "vault"]) == 0
    lines = ESCAPE.sub("", capsys.readouterr().out).splitlines()
    assert any(line.startswith("╭") for line in lines)
    for line in lines:
        assert len(line) <= 60 or "vault" in line


def test_styled_commands_keep_their_words(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    base = ["--color", "always", "--vault", str(tmp_path / "v"), "--keys", str(tmp_path / "k")]
    assert (
        main(["--color", "always", "--keys", str(tmp_path / "k"), "init", str(tmp_path / "v")]) == 0
    )
    assert "initialised" in ESCAPE.sub("", capsys.readouterr().out)
    assert main([*base, "write", "m", 'rules=["page.n >= 0"]', "n=0", "--as", "alice"]) == 0
    assert ESCAPE.sub("", capsys.readouterr().out).startswith(" ✓ written ")
    assert main([*base, "write", "m", "n=-1", "--as", "alice"]) == 1
    err = ESCAPE.sub("", capsys.readouterr().err)
    assert "✗ refused" in err and "rule: page.n >= 0" in err
    assert main([*base, "read", "m"]) == 0
    assert ESCAPE.sub("", capsys.readouterr().out) == "---\nrules:\n- page.n >= 0\nn: 0\n---\n"
    assert main([*base, "log"]) == 0
    log = ESCAPE.sub("", capsys.readouterr().out)
    assert "written" in log and "refused" in log
    assert main([*base, "verify"]) == 0
    assert "verified 2 commits" in " ".join(ESCAPE.sub("", capsys.readouterr().out).split())
    assert main([*base, "write", "m", "oops", "--as", "alice"]) == 1
    err = ESCAPE.sub("", capsys.readouterr().err)
    assert err.startswith(" ✗ error ") and "expected field=value, got 'oops'" in err


def test_styled_log_aligns_columns_and_marks_model_answers() -> None:
    from conky.present import Styled

    lines = [
        "a1b2c3d 2026-11-20T10:00:00Z alice write stall",
        "b2c3d4e 2026-11-20T10:00:01Z depot write depot cause a1b2c3d",
        "c3d4e5f 2026-11-20T10:00:02Z alice refused stall model: no key model helper",
    ]
    out = Styled(88).log(lines)
    plain = [ESCAPE.sub("", x) for x in out]
    assert len({x.index("written") for x in plain if "written" in x}) == 1
    assert "cause a1b2c3d" in plain[1]
    assert " ".join(plain[2].split()).endswith("model helper") and "refused" in plain[2]
    assert "48;2;135;75;253" in out[2]
