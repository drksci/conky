import json
import shutil
from pathlib import Path

import pytest

from conky import Vault, VerifyFailed
from conky.keys import check_seal
from conky.log import canonical

from .conftest import AT


def w(vault: Vault, page: str, changes: dict, body: str | None = None, actor: str = "alice"):
    return vault.write(page, changes, body, actor=actor, at=AT)


def events(vault: Vault) -> list[dict]:
    return vault.log.events()


def test_write_within_limits_lands_in_log_and_page(vault: Vault) -> None:
    result = w(vault, "stall", {"stock": 40}, "Fresh bread.")
    assert result.ok and result.seq == 0
    assert events(vault)[0]["kind"] == "write"
    text = (vault.pages_dir / "stall.md").read_text()
    assert text == "---\nstock: 40\n---\nFresh bread.\n"
    assert vault.read("stall").fields == {"stock": 40}


def test_size_rule_in_a_space_refuses_and_records(vault: Vault) -> None:
    w(vault, "tight", {"rules": ["size <= 300"]})
    assert w(vault, "note", {"within": "tight"}, "short").ok
    before = (vault.pages_dir / "note.md").read_bytes()
    result = w(vault, "note", {}, "x" * 400)
    assert not result.ok
    assert result.reason.startswith("rule") and "size <= 300" in result.reason
    assert events(vault)[-1]["kind"] == "refused"
    assert (vault.pages_dir / "note.md").read_bytes() == before


def test_page_without_a_size_rule_accepts_a_large_body(vault: Vault) -> None:
    assert w(vault, "note", {}, "x" * 100_000).ok
    assert len(vault.read("note").body) == 100_001


def test_page_rule_refuses_and_records(vault: Vault) -> None:
    assert w(vault, "stall", {"rules": ["page.stock >= 0"], "stock": 5}).ok
    result = w(vault, "stall", {"stock": -1})
    assert not result.ok
    assert result.reason.startswith("rule") and "page.stock >= 0" in result.reason
    assert events(vault)[-1]["kind"] == "refused"
    assert vault.read("stall").fields["stock"] == 5


def test_rule_that_errors_refuses(vault: Vault) -> None:
    result = w(vault, "stall", {"rules": ["page.missing > 0"]})
    assert not result.ok and result.reason.startswith("rule")


def test_rule_inherited_through_two_level_chain(vault: Vault) -> None:
    w(vault, "market", {"rules": ["page.price >= 0"], "price": 0})
    w(vault, "bazaar", {"within": "market", "price": 0})
    assert w(vault, "stall", {"within": "bazaar", "price": 3}).ok
    result = w(vault, "stall", {"price": -3})
    assert not result.ok
    assert result.reason.startswith("rule") and "page.price >= 0" in result.reason
    assert vault.read("stall").fields["price"] == 3


def watch_pair(vault: Vault) -> None:
    w(vault, "stall", {"stock": 40})
    w(
        vault,
        "depot",
        {
            "reorder": False,
            "watch": [{"on": "stall", "when": "other.stock < 10", "set": {"reorder": "true"}}],
        },
    )


def test_reaction_fires_without_a_model(vault: Vault) -> None:
    watch_pair(vault)
    first = w(vault, "stall", {"stock": 4})
    assert vault.read("depot").fields["reorder"] is True
    reaction = events(vault)[-1]
    assert reaction["page"] == "depot" and reaction["actor"] == "depot"
    assert reaction["cause"] == first.seq
    unsealed = canonical({k: v for k, v in reaction.items() if k != "seal"}).encode()
    assert check_seal(vault.public_dir, "depot", unsealed, reaction["seal"]) is None
    assert check_seal(vault.public_dir, "alice", unsealed, reaction["seal"]) is not None
    vault.verify()


def test_reaction_that_changes_nothing_is_skipped(vault: Vault) -> None:
    watch_pair(vault)
    w(vault, "stall", {"stock": 4})
    count = len(events(vault))
    w(vault, "stall", {"stock": 3})
    assert len(events(vault)) == count + 1


def test_reaction_cycle_stops_at_depth_12(vault: Vault) -> None:
    for me, other in (("a", "b"), ("b", "a")):
        w(
            vault,
            me,
            {"n": 0, "watch": [{"on": other, "when": "true", "set": {"n": "other.n + 1"}}]},
        )
    before = len(events(vault))
    w(vault, "a", {"n": 100})
    added = events(vault)[before:]
    refused = [e for e in added if e["kind"] == "refused"]
    assert len(refused) == 1 and refused[0]["reason"].startswith("cycle")
    assert len([e for e in added if e["kind"] == "write"]) == 13
    vault.verify()


def make_history(vault: Vault) -> None:
    w(vault, "market", {"rules": ["page.stock >= 0"], "stock": 0})
    w(vault, "stall", {"within": "market", "stock": 40}, "Bread.")
    w(vault, "stall", {"stock": -5})
    w(vault, "stall", {"stock": 7})


def test_tampering_with_any_event_byte_fails_verify(vault: Vault) -> None:
    make_history(vault)
    vault.verify()
    original = vault.log.path.read_bytes()
    for index in range(len(original)):
        changed = bytearray(original)
        changed[index] ^= 1
        vault.log.path.write_bytes(bytes(changed))
        with pytest.raises(VerifyFailed):
            vault.verify()
    vault.log.path.write_bytes(original)
    vault.verify()


def test_editing_a_page_by_hand_fails_verify(vault: Vault) -> None:
    make_history(vault)
    page = vault.pages_dir / "stall.md"
    page.write_text(page.read_text().replace("stock: 7", "stock: 8"))
    with pytest.raises(VerifyFailed, match="stall"):
        vault.verify()


def test_extra_page_file_fails_verify(vault: Vault) -> None:
    make_history(vault)
    (vault.pages_dir / "ghost.md").write_text("---\n---\n")
    with pytest.raises(VerifyFailed, match="ghost"):
        vault.verify()


def test_deleting_an_event_fails_verify(vault: Vault) -> None:
    make_history(vault)
    lines = vault.log.path.read_text().splitlines(keepends=True)
    del lines[1]
    vault.log.path.write_text("".join(lines))
    with pytest.raises(VerifyFailed):
        vault.verify()


def test_rebuild_reproduces_pages_byte_for_byte(vault: Vault) -> None:
    make_history(vault)
    w(
        vault,
        "depot",
        {
            "reorder": False,
            "watch": [{"on": "stall", "when": "other.stock < 10", "set": {"reorder": "true"}}],
        },
    )
    w(vault, "stall", {"stock": 2})
    before = {p.name: p.read_bytes() for p in vault.pages_dir.glob("*.md")}
    shutil.rmtree(vault.pages_dir)
    vault.rebuild()
    after = {p.name: p.read_bytes() for p in vault.pages_dir.glob("*.md")}
    assert before == after and len(before) == 3
    vault.verify()


def test_vault_travels_alone(vault: Vault, tmp_path: Path) -> None:
    make_history(vault)
    elsewhere = tmp_path / "elsewhere" / "copy"
    shutil.copytree(vault.path, elsewhere)
    moved = Vault(elsewhere, tmp_path / "no-such-keys")
    moved.verify()
    assert moved.read("stall").fields["stock"] == 7
    assert not (tmp_path / "no-such-keys").exists()


def test_no_private_key_material_in_the_vault(vault: Vault, keys_dir: Path) -> None:
    make_history(vault)
    private = {p.read_text() for p in keys_dir.glob("*.key")}
    assert private
    for path in vault.path.rglob("*"):
        if path.is_file():
            assert path.suffix != ".key"
            text = path.read_text()
            assert not any(secret in text for secret in private)
    for pub in vault.public_dir.glob("*.pub"):
        assert len(bytes.fromhex(pub.read_text())) == 32


def test_embeds_resolve_on_read(vault: Vault) -> None:
    w(vault, "stall", {"stock": 40})
    w(vault, "sign", {}, "We hold ![[stall#stock]] loaves.")
    assert vault.read("sign").body == "We hold 40 loaves.\n"
    assert "![[stall#stock]]" in (vault.pages_dir / "sign.md").read_text()
    w(vault, "stall", {"stock": 12})
    assert vault.read("sign").body == "We hold 12 loaves.\n"


def test_missing_embed_target_resolves_to_empty(vault: Vault) -> None:
    w(vault, "stall", {"stock": 1})
    w(vault, "sign", {}, "a ![[nowhere#x]] b ![[stall#nofield]] c")
    assert vault.read("sign").body == "a  b  c\n"


def test_malformed_watch_is_refused(vault: Vault) -> None:
    result = w(vault, "depot", {"watch": [{"on": "stall"}]})
    assert not result.ok and result.reason.startswith("shape")


def test_log_lines_are_canonical_json(vault: Vault) -> None:
    w(vault, "stall", {"stock": 1})
    for line in vault.log.lines():
        assert line == canonical(json.loads(line))


def test_watch_key_on_is_plain_text_in_frontmatter(vault: Vault) -> None:
    watch_pair(vault)
    assert "- on: stall\n" in (vault.pages_dir / "depot.md").read_text()
    assert vault.read("depot").watch[0]["on"] == "stall"
