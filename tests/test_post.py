"""The post connector: a letter crosses between two theatres in a bundle, and laws do not.

Two vaults with separate key folders. The only thing that passes between them is a bundle file.
No test reaches a network or a live model.
"""

import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pytest

from conky import Vault, arch
from conky.cli import main
from conky.git import trailers
from conky.page import serialize

from .conftest import AT, git, signed_by

LETTER = {"text": "greetings"}


@dataclass
class World:
    """A sender's outbox and a receiver's home, each with its own keys, and the bundle between."""

    root: Path
    out: Vault
    home: Vault

    @property
    def bundle(self) -> Path:
        return self.root / "bag" / "out.bundle"

    @property
    def key(self) -> str:
        kind, blob = (self.root / "ka" / "sender.pub").read_text().split()[:2]
        return f"{kind} {blob}"


def say(vault: Vault, page: str, changes: dict[str, Any], body: str | None = None, by="alice"):
    return vault.write(page, changes, body, actor=by, at=AT)


def run(*args: str) -> int:
    return main(list(args))


def post(world: World, *args: str) -> int:
    return run("--vault", str(world.home.path), "--keys", str(world.home.keys_dir), *args)


def send(world: World) -> None:
    code = run(
        "--vault",
        str(world.out.path),
        "--keys",
        str(world.out.keys_dir),
        *("connect", "post", "publish", "--out", str(world.bundle)),
    )
    assert code == 0 and world.bundle.is_file()


def take(world: World, peer: str = "lisbon") -> int:
    return post(world, "connect", "post", "take", peer)


@pytest.fixture
def world(tmp_path: Path) -> World:
    out = Vault.init(tmp_path / "outbox", tmp_path / "ka")
    home = Vault.init(tmp_path / "home", tmp_path / "kb")
    found = World(tmp_path, out, home)
    assert say(out, "note", LETTER, "Dear friend.\n", by="sender").ok
    send(found)
    pin(found)
    return found


def pin(world: World, **more: Any) -> None:
    fields = {"key": world.key, "bundle": str(world.bundle), **more}
    assert say(world.home, "lisbon", fields).ok


def log(vault: Vault) -> list[tuple[str, str, dict[str, str]]]:
    out = git(vault.path, "log", "--reverse", "--format=%x1e%H%x1f%an%x1f%B", "main")
    found = []
    for record in out.split("\x1e")[1:]:
        commit, author, message = record.split("\x1f", 2)
        found.append((commit, author, trailers(message)))
    return found


def arrivals(vault: Vault) -> list[tuple[str, str, dict[str, str]]]:
    return [c for c in log(vault) if c[1] == "lisbon" and "Cause" in c[2]]


def head(vault: Vault) -> str:
    return git(vault.path, "rev-parse", "HEAD").strip()


@arch.holds("law.post.pinned", "law.write.only")
def test_a_letter_is_taken_as_a_write_by_the_peer_into_its_space(world: World, capsys) -> None:
    sent = log(world.out)[-1][0]
    assert take(world) == 0
    page = world.home.read("note")
    assert page.within == "lisbon" and page.fields == LETTER and page.body == "Dear friend.\n"
    (commit, author, found), *_ = arrivals(world.home)
    assert author == "lisbon" and found["Cause"] == sent and found["Kind"] == "write"
    assert signed_by(world.home.path) == "lisbon@conky"
    assert "note" in capsys.readouterr().out
    world.home.verify()


def test_taking_twice_changes_nothing_and_a_new_letter_is_the_only_thing_taken(
    world: World, capsys
) -> None:
    assert take(world) == 0
    after = head(world.home)
    assert take(world) == 0 and head(world.home) == after
    assert "nothing new" in capsys.readouterr().out
    assert say(world.out, "second", {"text": "again"}, by="sender").ok
    send(world)
    assert take(world) == 0
    assert [a[2]["Page"] for a in arrivals(world.home)] == ["note", "second"]


def inbox(world: World, rule: str, **more: Any) -> None:
    assert say(world.home, "inbox", {"rules": [{"each": rule}]}).ok
    pin(world, within="inbox", **more)


@arch.holds("law.refusal.record", "law.post.pinned")
def test_a_letter_a_rule_turns_away_is_a_refusal_recorded_once_and_noticed(
    world: World, capsys
) -> None:
    counting = [{"on": "refusal", "when": "true", "set": {"turned": "event.reason"}}]
    inbox(world, "!has(page.text) || page.text != 'greetings'", watch=counting)
    assert take(world) == 0
    assert "refused" in capsys.readouterr().out
    assert not (world.home.pages_dir / "note.md").exists()
    refused = [c for c in arrivals(world.home) if c[2]["Kind"] == "refused"]
    assert len(refused) == 1
    assert refused[0][2]["Cause"] == log(world.out)[-1][0] and "Reason" in refused[0][2]
    assert "rule" in world.home.read("lisbon").fields["turned"]
    after = head(world.home)
    assert take(world) == 0 and head(world.home) == after
    world.home.verify()


def test_an_inbox_can_say_which_peers_may_write(world: World) -> None:
    assert say(world.home, "peers", {}).ok and say(world.home, "alice", {"within": "peers"}).ok
    inbox(world, "within(event.by, 'peers')")
    assert take(world) == 0 and not (world.home.pages_dir / "note.md").exists()
    assert say(world.home, "lisbon", {"within": ["inbox", "peers"]}).ok
    assert say(world.out, "second", {"text": "again"}, by="sender").ok
    send(world)
    assert take(world) == 0
    assert world.home.read("second").within == "lisbon"


@arch.holds("law.post.pinned")
def test_an_unknown_or_different_key_writes_nothing_and_says_what_to_do(
    world: World, capsys
) -> None:
    other = (world.home.keys_dir / "alice.pub").read_text().split()[:2]
    assert say(world.home, "stranger", {"bundle": str(world.bundle)}).ok
    before = head(world.home)
    assert take(world, "stranger") == 1
    shown = capsys.readouterr().err
    assert world.key in shown and "conky write stranger key=" in shown and "another route" in shown
    assert say(world.home, "lisbon", {"key": " ".join(other)}).ok
    before = head(world.home)
    assert take(world) == 1
    assert "not signed by the key pinned on lisbon" in capsys.readouterr().err
    assert head(world.home) == before
    assert not (world.home.pages_dir / "note.md").exists()


@arch.holds("law.post.pinned")
def test_a_damaged_bundle_and_a_stranger_s_commit_write_nothing(world: World, capsys) -> None:
    before = head(world.home)
    good = world.bundle.read_bytes()
    damaged = bytearray(good)
    damaged[len(damaged) // 2] ^= 0xFF
    world.bundle.write_bytes(bytes(damaged))
    assert take(world) == 1 and head(world.home) == before
    assert "bundle" in capsys.readouterr().err
    world.bundle.write_bytes(b"not a bundle")
    assert take(world) == 1 and head(world.home) == before
    world.bundle.write_bytes(good)
    assert say(world.out, "forged", {"text": "trust me"}, by="stranger").ok
    send(world)
    assert take(world) == 1 and head(world.home) == before
    assert "not signed by the key pinned" in capsys.readouterr().err
    assert not (world.home.pages_dir / "forged.md").exists()


def test_a_letter_cannot_reach_outside_the_space_or_carry_a_secret(world: World, capsys) -> None:
    assert say(world.home, "ledger", {"cash": 5}).ok
    assert say(world.out, "ledger", {"cash": 0}, by="sender").ok
    assert say(world.out, "lisbon", {"rules": []}, by="sender").ok
    assert say(world.out, "keyed", {"secret": "TOKEN"}, by="sender").ok
    assert say(world.out, "memo", {"rules": [{"each": "false"}], "text": "hi"}, by="sender").ok
    send(world)
    assert take(world) == 0
    shown = capsys.readouterr().out
    assert world.home.read("ledger").fields == {"cash": 5}
    assert world.home.read("lisbon").rules == [] and "key" in world.home.read("lisbon").fields
    assert not (world.home.pages_dir / "keyed.md").exists()
    memo = world.home.read("memo")
    assert memo.rules == [] and memo.fields == {"text": "hi"} and memo.within == "lisbon"
    assert "without its rules" in shown and shown.count("refused") == 3
    reasons = [c[2]["Reason"] for c in arrivals(world.home) if c[2]["Kind"] == "refused"]
    assert len(reasons) == 3 and all(r.startswith("limit") for r in reasons)
    world.home.verify()


def listed(root: Path) -> list[str]:
    return [p.name for p in root.rglob("*") if p.is_file() and ".git" not in p.parts]


@arch.holds("law.vault.travel", "law.name.claimed")
def test_after_a_take_the_receiver_travels_alone_and_no_private_key_crosses(
    world: World, tmp_path: Path
) -> None:
    assert take(world) == 0
    copy = tmp_path / "copy"
    git(tmp_path, "clone", "-q", str(world.home.path), str(copy))
    Vault(copy, tmp_path / "none").verify()
    seen = [world.out.path, world.home.path, copy]
    for folder in seen:
        for path in folder.rglob("*"):
            if path.is_file() and ".git" not in path.parts:
                assert b"PRIVATE KEY" not in path.read_bytes(), path
    assert b"PRIVATE KEY" not in world.bundle.read_bytes()
    assert not any(n in listed(world.home.path) for n in ("sender", "alice", "lisbon"))
    assert signed_by(world.home.path) == "lisbon@conky"
    # the arrival is the receiver's attestation: signed by its own key for the peer's name,
    # and the proof of origin is the Cause, a commit of the signed bundle
    assert (world.home.keys_dir / "lisbon").exists() and not (
        world.out.keys_dir / "lisbon"
    ).exists()
    origin = git(world.out.path, "log", "--format=%H", "main").split()
    assert arrivals(world.home)[0][2]["Cause"] in origin


def test_a_letter_a_model_answered_and_one_a_person_wrote_land_as_the_same_page(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    program = tmp_path / "model.py"
    program.write_text(
        "import sys\nsys.stdin.read()\n"
        "print('=== page: note ===\\n---\\nwithin: yard\\ntext: hello\\n---\\nDear friend.\\n"
        "=== end ===')\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("CONKY_COMMAND_STAND", f"{sys.executable} {program}")
    files = []
    for kind in ("person", "model"):
        root = tmp_path / kind
        out = Vault.init(root / "outbox", root / "ka")
        home = Vault.init(root / "home", root / "kb")
        assert say(out, "yard", {}, by="sender").ok
        if kind == "person":
            letter = {"within": "yard", "text": "hello"}
            assert say(out, "note", letter, "Dear friend.", "sender").ok
        else:
            assert say(out, "helper", {"api": "command", "command": "stand"}, by="sender").ok
            assert say(out, "desk", {}, by="sender").ok
            asked = out.ask(
                "desk", writes="yard", provider="helper", prompt="write", actor="sender", at=AT
            )
            assert asked.ok and all(landed.ok for _, landed in asked.pages)
        found = World(root, out, home)
        send(found)
        assert say(home, "lisbon", {"key": found.key, "bundle": str(found.bundle)}).ok
        assert take(found) == 0
        files.append((home.pages_dir / "note.md").read_bytes())
    assert files[0] == files[1]
    assert files[0] == serialize(Vault(tmp_path / "person" / "home").read("note")).encode()


def test_the_local_driver_needs_only_the_bundle_file(world: World, tmp_path: Path) -> None:
    kept = tmp_path / "kept.bundle"
    shutil.copy(world.bundle, kept)
    shutil.rmtree(world.out.path)
    shutil.rmtree(world.bundle.parent)
    assert not world.out.path.exists()
    assert post(world, "connect", "post", "take", "lisbon", "--from", str(kept)) == 0
    assert world.home.read("note").fields == LETTER


def test_a_missing_bundle_and_an_unknown_carrier_say_what_to_do(
    world: World, capsys, tmp_path: Path
) -> None:
    assert say(world.home, "lisbon", {"bundle": str(tmp_path / "gone.bundle")}).ok
    assert take(world) == 1 and "conky connect post publish" in capsys.readouterr().err
    assert say(world.home, "lisbon", {"carrier": "pigeon"}).ok
    assert take(world) == 1 and "use one of local" in capsys.readouterr().err


def test_a_marionette_names_the_carrier_and_refuses_an_unknown_one(world: World, capsys) -> None:
    (world.home.path / "marionette.md").write_text("---\ncarrier: pigeon\n---\n", encoding="utf-8")
    assert take(world) == 1 and "use one of local" in capsys.readouterr().err
    (world.home.path / "marionette.md").write_text("---\ncarrier: local\n---\n", encoding="utf-8")
    assert take(world) == 0
    assert (
        post(world, "theatre") == 0 and "carrier: local (marionette.md)" in capsys.readouterr().out
    )


@dataclass
class Pair:
    """Two theatres, each a vault with its own keys, that know each other by a peer page."""

    root: Path
    a: Vault
    b: Vault

    def theatre(self, name: str) -> Vault:
        return self.a if name == "a" else self.b

    def bundle(self, sender: str) -> Path:
        peer = "b" if sender == "a" else "a"
        return self.root / f"{sender}.outboxes" / f"{peer}.bundle"

    def outbox(self, sender: str) -> Path:
        return self.root / f"{sender}.outboxes" / ("b" if sender == "a" else "a")


def tell(vault: Vault, *args: str) -> int:
    return run("--vault", str(vault.path), "--keys", str(vault.keys_dir), *args)


def carry(pair: Pair, sender: str) -> int:
    """Send from one theatre, then pin the sender's key and its bundle on the other."""
    peer = "b" if sender == "a" else "a"
    here, there = pair.theatre(sender), pair.theatre(peer)
    code = tell(here, "connect", "post", "send", peer)
    if code == 0 and pair.bundle(sender).is_file():
        kind, blob = (here.keys_dir / "post.pub").read_text().split()[:2]
        fields = {"key": f"{kind} {blob}", "bundle": str(pair.bundle(sender))}
        assert say(there, sender, fields).ok
    return code


def pull(pair: Pair, receiver: str) -> int:
    peer = "b" if receiver == "a" else "a"
    return tell(pair.theatre(receiver), "connect", "post", "take", peer)


@pytest.fixture
def pair(tmp_path: Path) -> Pair:
    a = Vault.init(tmp_path / "a", tmp_path / "ka")
    b = Vault.init(tmp_path / "b", tmp_path / "kb")
    assert say(a, "b", {}).ok and say(b, "a", {}).ok
    return Pair(tmp_path, a, b)


def where(vault: Vault, page: str) -> str | list[str] | None:
    return vault.read(page).within


@arch.holds("law.write.only", "law.post.pinned")
def test_a_letter_written_within_a_peer_crosses_and_so_does_the_reply(
    pair: Pair, capsys: pytest.CaptureFixture[str]
) -> None:
    assert say(pair.a, "a-letter", {"within": "b", "text": "hi"}, "Hello B.\n").ok
    before = head(pair.a)
    assert carry(pair, "a") == 0
    shown = capsys.readouterr().out
    assert "a-letter" in shown and "carried" in shown and "key of post: ssh-ed25519" in shown
    assert head(pair.a) == before
    assert pull(pair, "b") == 0
    assert where(pair.b, "a-letter") == "a" and pair.b.read("a-letter").body == "Hello B.\n"
    sent = [c[0] for c in log(pair.a) if c[2].get("Page") == "a-letter"][0]
    made = [c for c in log(Vault(pair.outbox("a"))) if "Cause" in c[2]]
    assert [(c[1], c[2]["Cause"]) for c in made] == [("post", sent)]
    assert signed_by(pair.outbox("a")) == "post@conky"
    arrived = [c for c in log(pair.b) if c[1] == "a" and c[2].get("Page") == "a-letter"]
    assert [c[2]["Cause"] for c in arrived] == [sent]
    assert say(pair.b, "reply", {"within": "a", "text": "hello"}, "Hello A.\n").ok
    assert carry(pair, "b") == 0 and pull(pair, "a") == 0
    assert where(pair.a, "reply") == "b" and pair.a.read("reply").body == "Hello A.\n"
    pair.a.verify()
    pair.b.verify()
    after = (head(pair.a), head(pair.b))
    capsys.readouterr()
    assert tell(pair.a, "connect", "post", "send", "b") == 0
    assert "nothing to send" in capsys.readouterr().out
    assert tell(pair.b, "connect", "post", "send", "a") == 0
    assert pull(pair, "a") == 0 and pull(pair, "b") == 0
    assert (head(pair.a), head(pair.b)) == after


def test_a_rebuilt_outbox_is_never_taken_twice(
    pair: Pair, capsys: pytest.CaptureFixture[str]
) -> None:
    assert say(pair.a, "a-letter", {"within": "b", "text": "hi"}).ok
    assert carry(pair, "a") == 0 and pull(pair, "b") == 0
    taken = [c for c in log(pair.b) if c[1] == "a"]
    shutil.rmtree(pair.root / "a.outboxes")
    capsys.readouterr()
    assert carry(pair, "a") == 0 and "a-letter" in capsys.readouterr().out
    assert pair.bundle("a").is_file()
    assert pull(pair, "b") == 0 and "nothing new" in capsys.readouterr().out
    assert [c for c in log(pair.b) if c[1] == "a"] == taken
    pair.a.verify()


def test_arrivals_are_never_sent_back(pair: Pair, capsys: pytest.CaptureFixture[str]) -> None:
    assert say(pair.a, "a-letter", {"within": "b", "text": "hi"}).ok
    assert carry(pair, "a") == 0 and pull(pair, "b") == 0
    capsys.readouterr()
    assert tell(pair.b, "connect", "post", "send", "a") == 0
    assert "nothing to send" in capsys.readouterr().out
    assert not pair.outbox("b").exists()


def test_an_edit_of_a_sent_letter_is_carried_again_as_an_update(pair: Pair) -> None:
    assert say(pair.a, "a-letter", {"within": "b", "text": "hi"}).ok
    assert carry(pair, "a") == 0 and pull(pair, "b") == 0
    assert say(pair.a, "a-letter", {"text": "hello again"}, by="bob").ok
    assert carry(pair, "a") == 0 and pull(pair, "b") == 0
    assert pair.b.read("a-letter").fields["text"] == "hello again"
    assert [c[2]["Page"] for c in log(pair.b) if c[1] == "a" and "Cause" in c[2]] == [
        "a-letter",
        "a-letter",
    ]


def test_the_rules_of_the_peer_space_say_who_may_send(
    pair: Pair, capsys: pytest.CaptureFixture[str]
) -> None:
    assert say(pair.a, "staff", {}).ok and say(pair.a, "alice", {"within": "staff"}).ok
    assert say(pair.a, "b", {"rules": [{"each": "within(event.by, 'staff')"}]}).ok
    assert not say(pair.a, "a-letter", {"within": "b", "text": "hi"}, by="mallory").ok
    capsys.readouterr()
    assert tell(pair.a, "connect", "post", "send", "b") == 0
    assert "nothing to send" in capsys.readouterr().out and not pair.outbox("a").exists()
    assert say(pair.a, "a-letter", {"within": "b", "text": "hi"}, by="alice").ok
    assert carry(pair, "a") == 0 and pull(pair, "b") == 0
    assert where(pair.b, "a-letter") == "a"


def test_a_character_sends_by_writing(
    pair: Pair, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    program = tmp_path / "stand.py"
    program.write_text(
        "print('=== page: note ===\\n---\\nwithin: b\\ntext: hello\\n---\\nDear B.\\n"
        "=== end ===')\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("CONKY_COMMAND_STAND", f"{sys.executable} {program}")
    assert say(pair.a, "helper", {"api": "command", "command": "stand"}).ok
    assert say(pair.a, "scribe", {}).ok
    done = pair.a.ask(
        "scribe", writes="b", provider="helper", prompt="write", actor="scribe", at=AT
    )
    assert done.ok and all(landed.ok for _, landed in done.pages)
    assert carry(pair, "a") == 0 and pull(pair, "b") == 0
    assert where(pair.b, "note") == "a" and pair.b.read("note").fields["text"] == "hello"
    assert pair.b.read("note").body == "Dear B.\n"
    pair.b.verify()


def test_the_outbox_is_derived_data_beside_the_vault_and_can_be_placed(
    pair: Pair, capsys: pytest.CaptureFixture[str]
) -> None:
    assert say(pair.a, "a-letter", {"within": "b", "text": "hi"}).ok
    assert carry(pair, "a") == 0
    assert pair.outbox("a").is_dir() and not (pair.a.path / "a.outboxes").exists()
    assert {line.split()[2] for line in pair.a.log()} == {"alice"}
    settings = pair.a.path / "marionette.md"
    settings.write_text("---\noutboxes: inside\n---\n", encoding="utf-8")
    capsys.readouterr()
    assert tell(pair.a, "connect", "post", "send", "b") == 1
    assert "inside the vault" in capsys.readouterr().err
    settings.write_text("---\noutboxes: ../tray\n---\n", encoding="utf-8")
    assert tell(pair.a, "connect", "post", "send", "b") == 0
    assert (pair.root / "tray" / "b").is_dir()
    assert tell(pair.a, "theatre") == 0
    assert f"outboxes: {pair.root / 'tray'}" in capsys.readouterr().out
    pair.a.verify()


def test_sending_to_a_peer_with_no_page_says_what_to_write(
    pair: Pair, capsys: pytest.CaptureFixture[str]
) -> None:
    assert tell(pair.a, "connect", "post", "send", "nobody") == 1
    assert "no peer page named 'nobody'" in capsys.readouterr().err
