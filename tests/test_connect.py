"""The terminal connector: a vault with eyes and hands on a program, through ordinary writes.

The program is the small trail game in tests/games. The one model test talks to a stand-in server
on 127.0.0.1. No test reaches a live provider.
"""

import sys
import threading
import time
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest

from conky import Vault, arch
from conky.cli import main
from conky.connect import plain
from conky.git import trailers
from conky.page import parse

from .conftest import AT, git, signed_by
from .test_model import Stand, provider

GAME = [sys.executable, str(Path(__file__).parent / "games" / "trail.py")]
SETTLE = "0.15"
REFLEX = [{"on": "screen", "when": "true", "set": {"keys": '"1"', "turn": "other.turn"}}]


def connect(
    vault: Vault, *options: str, program: list[str] | None = None, keys: Path | None = None
) -> int:
    base = ["--vault", str(vault.path), "--keys", str(keys or vault.keys_dir)]
    command = ["connect", "terminal", "--settle", SETTLE, *options, "--", *(program or GAME)]
    return main([*base, *command])


def w(vault: Vault, page: str, changes: dict[str, Any], actor: str = "alice"):
    return vault.write(page, changes, None, actor=actor, at=AT)


def reflex(vault: Vault) -> None:
    assert w(vault, "hands", {"watch": REFLEX}).ok


def history(vault: Vault, page: str | None = None) -> list[tuple[str, dict[str, str]]]:
    """Return every commit, oldest first, with its trailers, optionally for one page."""
    out = git(vault.path, "log", "--reverse", "--format=%x1e%H%x1f%B", "main")
    found = []
    for record in out.split("\x1e")[1:]:
        commit, message = record.split("\x1f", 1)
        tags = trailers(message)
        if page is None or tags.get("Page") == page:
            found.append((commit, tags))
    return found


def committed(vault: Vault, page: str):
    """Return the page as committed on main, never half way through a write."""
    return parse(git(vault.path, "show", f"main:pages/{page}.md"))


def wait_for(vault: Vault, turn: int, timeout: float = 15.0) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            if committed(vault, "screen").fields.get("turn", 0) >= turn:
                return
        except Exception:  # noqa: BLE001, S110
            pass
        time.sleep(0.05)
    raise AssertionError(f"screen {turn} did not arrive")


class Running:
    """The connector running in a thread, so a test can write to the vault beside it."""

    def __init__(self, vault: Vault, *options: str) -> None:
        self.code: list[int] = []
        target = lambda: self.code.append(connect(vault, *options))  # noqa: E731
        self.thread = threading.Thread(target=target, daemon=True)
        self.thread.start()

    def finish(self, timeout: float = 20.0) -> int:
        self.thread.join(timeout)
        assert not self.thread.is_alive(), "the connector did not stop"
        return self.code[0]


@pytest.fixture(autouse=True)
def local_network(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in ("no_proxy", "NO_PROXY"):
        monkeypatch.setenv(name, "127.0.0.1")


@pytest.fixture
def stand() -> Iterator[Stand]:
    found = Stand()
    yield found
    found.stop()


@arch.holds("flow.connect.sense")
def test_the_first_screen_is_a_signed_write_by_the_connector(vault: Vault) -> None:
    assert connect(vault, "--max-steps", "1") == 0
    first = [c for c, tags in history(vault, "screen") if tags["Kind"] == "write"][1]
    assert signed_by(vault.path, first) == "terminal@conky"
    assert git(vault.path, "log", "-1", "--format=%an", first).strip() == "terminal"
    page = parse(git(vault.path, "show", f"{first}:pages/screen.md"))
    assert page.fields["turn"] == 1
    assert "THE LONG ROAD WEST" in page.body and "Stretch 1 of 5" in page.body
    assert committed(vault, "screen").fields["ended"] == "stopped after 1 screens"
    assert "hands" in {p.stem for p in vault.pages_dir.glob("*.md")}
    vault.verify()


@arch.holds("flow.connect.act", "flow.connect.sense")
def test_a_reacting_page_plays_the_game_to_its_end(vault: Vault) -> None:
    reflex(vault)
    assert connect(vault) == 0
    page = committed(vault, "screen")
    assert "Journey's end" in page.body and "The journal reads" in page.body
    assert page.fields["turn"] == 6
    assert page.fields["ended"] == "the program exited with status 0"
    screens = [c for c, tags in history(vault, "screen") if tags["Kind"] == "write"]
    turn_screens = screens[1:7]
    hands = [tags for _, tags in history(vault, "hands") if "Cause" in tags]
    assert {tags["Cause"] for tags in hands} >= set(turn_screens)
    assert {tags["Cause"] for tags in hands} <= set(screens)
    for turn, commit in enumerate(turn_screens, 1):
        body = parse(git(vault.path, "show", f"{commit}:pages/screen.md"))
        assert body.fields["turn"] == turn
        assert any(tags["Cause"] == commit for tags in hands)


@arch.holds("flow.connect.act")
def test_first_line_types_only_the_first_line_and_the_page_keeps_all_three(vault: Vault) -> None:
    running = Running(vault, "--max-steps", "2", "--first-line")
    wait_for(vault, 1)
    keys = "\n2\nthen I would hunt\nand keep notes"
    assert w(vault, "hands", {"keys": keys, "turn": 1}).ok
    assert running.finish() == 0
    body = committed(vault, "screen").body
    assert "Rest a day." in body and "Hunt. Two rabbits" not in body
    assert committed(vault, "hands").fields["keys"] == keys


@arch.holds("flow.connect.act")
def test_a_hands_write_for_an_old_turn_is_ignored(vault: Vault) -> None:
    running = Running(vault, "--max-steps", "2")
    wait_for(vault, 1)
    assert w(vault, "hands", {"keys": "3", "turn": 0}).ok
    time.sleep(0.6)
    assert committed(vault, "screen").fields["turn"] == 1
    assert w(vault, "hands", {"keys": "2", "turn": 1}).ok
    assert running.finish() == 0
    body = committed(vault, "screen").body
    assert "Rest a day." in body and "Hunt. Two rabbits" not in body


@arch.holds("flow.connect.act")
@pytest.mark.parametrize("house_rule", [True, False])
def test_a_rule_can_keep_a_key_from_the_program(vault: Vault, house_rule: bool) -> None:
    if house_rule:
        assert w(vault, "house", {"rules": [{"each": "!has(page.keys) || page.keys != '9'"}]}).ok
        assert w(vault, "hands", {"within": "house"}).ok
    running = Running(vault, "--max-steps", "2")
    wait_for(vault, 1)
    attempt = w(vault, "hands", {"keys": "9", "turn": 1})
    if house_rule:
        assert not attempt.ok and "(from house)" in (attempt.reason or "")
        tags = history(vault)[-1][1]
        assert tags["Kind"] == "refused" and tags["Page"] == "hands" and tags["From"] == "house"
        time.sleep(0.6)
        assert committed(vault, "screen").fields["turn"] == 1
        assert w(vault, "hands", {"keys": "1", "turn": 1}).ok
    assert running.finish() == 0
    body = committed(vault, "screen").body
    assert ("That is not one of the choices." in body) is not house_rule
    assert ("Push on." in body) is house_rule


@arch.holds("flow.connect.sense")
def test_max_steps_stops_a_run_and_records_why(vault: Vault) -> None:
    reflex(vault)
    assert connect(vault, "--max-steps", "2") == 0
    page = committed(vault, "screen")
    assert page.fields["turn"] == 2 and page.fields["ended"] == "stopped after 2 screens"
    assert "Stretch 3 of 5" not in page.body


@arch.holds("flow.connect.sense")
def test_control_sequences_do_not_reach_the_page(vault: Vault) -> None:
    shown = "import time; print('\\x1b[31mred\\x1b[0m \\x1b]0;title\\x07plain \\x1b[2Kdone'); "
    shown += "print('abc\\rXY'); time.sleep(10)"
    assert connect(vault, "--max-steps", "1", program=[sys.executable, "-c", shown]) == 0
    body = committed(vault, "screen").body
    assert "\x1b" not in body and "\r" not in body
    assert body.strip() == "red plain done\nXYc"


@arch.holds("flow.connect.sense")
def test_plain_text_keeps_the_last_sixty_lines() -> None:
    text = "".join(f"line {n}\r\n" for n in range(100))
    lines = plain(text).splitlines()
    assert len(lines) == 60 and lines[0] == "line 40" and lines[-1] == "line 99"


def test_a_page_that_asks_a_model_plays_and_the_record_says_what_it_read(
    vault: Vault, stand: Stand
) -> None:
    provider(vault, stand)
    stand.answer = "1"
    assert w(vault, "screen", {"turn": 0}).ok
    ask = {"provider": "helper", "prompt": "Screen:\n![[screen]]", "into": "keys"}
    watch = [
        {"on": "screen", "when": "true", "ask": ask},
        {"on": "screen", "when": "true", "set": {"turn": "other.turn"}},
    ]
    assert w(vault, "hands", {"watch": watch}).ok
    assert connect(vault, "--max-steps", "2") == 0
    assert len(stand.requests) == 2
    sent = [request["body"]["messages"][0]["content"] for request in stand.requests]
    assert all(text.startswith("Screen:\n") and len(text) > len("Screen:\n") for text in sent)
    assert any("Push on." in text for text in sent)
    answers = [tags for _, tags in history(vault, "hands") if "Model" in tags]
    assert len(answers) == 2
    assert all(tags["Read"] == "screen" and tags["Model"] == "helper" for tags in answers)
    assert [line for line in vault.log() if line.endswith("model helper read screen")]
    assert "Push on." in committed(vault, "screen").body
    vault.verify()


def test_a_full_run_verifies_and_a_clone_verifies(vault: Vault, tmp_path: Path) -> None:
    reflex(vault)
    assert connect(vault) == 0
    vault.verify()
    git(tmp_path, "clone", "-q", str(vault.path), "copy")
    copy = Vault(tmp_path / "copy", tmp_path / "no-such-keys")
    copy.verify()
    assert copy.log() == vault.log()
    assert not (tmp_path / "no-such-keys").exists()


def test_a_program_that_cannot_start_says_what_to_do(
    vault: Vault, capsys: pytest.CaptureFixture[str]
) -> None:
    assert connect(vault, program=["no-such-program-here"]) == 1
    err = capsys.readouterr().err
    assert err.startswith("error: cannot start 'no-such-program-here'")
    assert "check the command and that it is on PATH" in err


def test_the_screen_and_hands_pages_must_differ(
    vault: Vault, capsys: pytest.CaptureFixture[str]
) -> None:
    assert connect(vault, "--screen", "same", "--hands", "same") == 1
    assert "name the same page: give each its own page" in capsys.readouterr().err


def test_output_is_one_line_per_screen_and_per_keys_sent(
    vault: Vault, capsys: pytest.CaptureFixture[str]
) -> None:
    reflex(vault)
    assert connect(vault, "--max-steps", "2") == 0
    lines = capsys.readouterr().out.splitlines()
    assert lines[0].startswith("screen 1 written (commit ")
    assert lines[1] == "keys sent for screen 1: 1"
    assert lines[2].startswith("screen 2 written (commit ")
    assert lines[-1] == "ended: stopped after 2 screens"
    assert "\x1b" not in "".join(lines)
