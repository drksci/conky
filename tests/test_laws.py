import json
import subprocess
from datetime import datetime
from pathlib import Path

import pytest

from conky import BadInput, Vault, VerifyFailed, arch
from conky.git import trailers

from .conftest import AT, git, signed_by


def w(vault: Vault, page: str, changes: dict, body: str | None = None, actor: str = "alice"):
    return vault.write(page, changes, body, actor=actor, at=AT)


def message(vault: Vault, revision: str = "HEAD") -> tuple[str, dict[str, str]]:
    text = git(vault.path, "log", "-1", "--format=%B", revision)
    return text.splitlines()[0], trailers(text)


def commits(vault: Vault) -> list[str]:
    return git(vault.path, "log", "--reverse", "--format=%H", "main").split()


def pages(vault: Vault) -> dict[str, bytes]:
    return {p.name: p.read_bytes() for p in sorted(vault.pages_dir.glob("*.md"))}


@arch.holds("law.write.only", "law.event.seal", "flow.write.accept")
def test_write_is_a_signed_commit_with_trailers_and_dates(vault: Vault) -> None:
    result = w(vault, "cooler", {"stock": 40}, "Fresh bread.")
    assert result.ok and result.id == commits(vault)[-1]
    subject, found = message(vault)
    assert subject == "write cooler" and found == {"Kind": "write", "Page": "cooler"}
    shown = git(vault.path, "log", "-1", "--format=%an|%ae|%cn|%ce|%at|%ct")
    stamp = str(int(datetime.fromisoformat(AT).timestamp()))
    assert shown.strip() == "alice|alice@conky|alice|alice@conky|" + "|".join([stamp] * 2)
    assert signed_by(vault.path) == "alice@conky"
    assert (vault.pages_dir / "cooler.md").read_text() == "---\nstock: 40\n---\nFresh bread.\n"
    assert git(vault.path, "show", "HEAD:pages/cooler.md") == "---\nstock: 40\n---\nFresh bread.\n"
    vault.verify()


@arch.holds("flow.write.accept")
def test_first_write_registers_the_key_in_the_same_commit(vault: Vault) -> None:
    w(vault, "cooler", {"stock": 1})
    w(vault, "cooler", {"stock": 2})
    first = git(vault.path, "show", "--name-only", "--format=", commits(vault)[0]).split()
    second = git(vault.path, "show", "--name-only", "--format=", commits(vault)[1]).split()
    assert sorted(first) == ["keys/allowed_signers", "pages/cooler.md"]
    assert second == ["pages/cooler.md"]
    line = (vault.path / "keys" / "allowed_signers").read_text()
    assert line.startswith('alice@conky namespaces="git" ssh-ed25519 ')


@arch.holds("law.vault.travel")
def test_init_sets_the_repository_up_for_plain_git(vault: Vault) -> None:
    w(vault, "cooler", {"stock": 1})
    assert git(vault.path, "config", "--get", "gpg.format").strip() == "ssh"
    assert git(vault.path, "config", "--get", "commit.gpgsign").strip() == "true"
    assert git(vault.path, "branch", "--show-current").strip() == "main"
    out = git(vault.path, "log", "--show-signature", "-1")
    assert 'Good "git" signature for alice@conky' in out


@arch.holds("law.refusal.record", "flow.write.refuse")
def test_refused_write_is_an_empty_signed_commit(vault: Vault) -> None:
    assert w(vault, "cooler", {"rules": ["page.stock >= 0"], "stock": 5}).ok
    before = pages(vault)
    result = w(vault, "cooler", {"stock": -1}, "some body")
    assert not result.ok and result.id == commits(vault)[-1]
    subject, found = message(vault)
    assert subject == "refused cooler" and found["Kind"] == "refused"
    assert found["Reason"] == result.reason and "page.stock >= 0" in found["Reason"]
    assert found["Attempt"] == '{"stock":-1}' and found["Body-Bytes"] == "9"
    assert git(vault.path, "show", "--name-only", "--format=", "HEAD") == ""
    assert signed_by(vault.path) == "alice@conky"
    assert pages(vault) == before
    vault.verify()


@arch.holds("flow.write.refuse")
def test_refusal_by_a_new_actor_registers_its_key(vault: Vault) -> None:
    result = w(vault, "supplier", {"watch": [{"on": "cooler"}]}, actor="carol")
    assert not result.ok and result.reason.startswith("shape")
    assert signed_by(vault.path) == "carol@conky"
    vault.verify()


@arch.holds("law.rule.never", "flow.write.refuse")
def test_rule_error_refuses(vault: Vault) -> None:
    result = w(vault, "cooler", {"rules": ["page.missing > 0"]})
    assert not result.ok and result.reason.startswith("rule")


@arch.holds("law.rule.never")
def test_rule_inherited_through_two_level_chain(vault: Vault) -> None:
    w(vault, "stand", {"rules": [{"each": "page.price >= 0"}], "price": 0})
    w(vault, "bazaar", {"within": "stand", "price": 0})
    assert w(vault, "cooler", {"within": "bazaar", "price": 3}).ok
    result = w(vault, "cooler", {"price": -3})
    assert not result.ok
    assert result.reason.startswith("rule") and "page.price >= 0" in result.reason
    assert vault.read("cooler").fields["price"] == 3


@arch.holds("flow.write.refuse")
def test_a_refusal_by_a_rule_from_a_space_names_that_space(vault: Vault) -> None:
    w(vault, "stand", {"rules": [{"each": "!has(page.price) || page.price >= 0"}]})
    w(vault, "bazaar", {"within": "stand"})
    assert w(vault, "cooler", {"within": "bazaar", "rules": ["page.price < 100"], "price": 3}).ok
    assert not w(vault, "cooler", {"price": -3}).ok
    _, found = message(vault)
    assert found["From"] == "stand" and "(from stand)" in found["Reason"]
    assert vault.log()[-1].endswith(" from stand")
    assert not w(vault, "cooler", {"price": 300}).ok
    _, found = message(vault)
    assert "From" not in found and "(from cooler)" in found["Reason"]
    assert not vault.log()[-1].endswith(" from cooler")
    vault.verify()


@arch.holds("law.rule.tighten", "flow.space.move")
def test_leaving_a_space_is_judged_by_the_rules_of_the_space_it_leaves(vault: Vault) -> None:
    w(vault, "club", {"rules": [{"each": "size <= 200"}]})
    w(vault, "street", {})
    assert w(vault, "member", {"within": "club"}, "short").ok
    result = w(vault, "member", {"within": "street"}, "x" * 400)
    assert not result.ok and result.reason.startswith("rule: size <= 200 (from club)")
    _, found = message(vault)
    assert found["Kind"] == "refused" and found["From"] == "club"
    assert vault.read("member").within == "club"
    assert w(vault, "member", {"within": "street"}, "short").ok
    assert w(vault, "member", {}, "x" * 400).ok
    vault.verify()


@arch.holds("law.rule.never")
def test_size_rule_in_a_space_refuses_an_oversized_member(vault: Vault) -> None:
    w(vault, "tight", {"rules": [{"each": "size <= 300"}]})
    assert w(vault, "note", {"within": "tight"}, "short").ok
    before = pages(vault)
    result = w(vault, "note", {}, "x" * 400)
    assert not result.ok and "size <= 300" in result.reason
    assert message(vault)[1]["Kind"] == "refused"
    assert pages(vault) == before


@arch.holds("law.pressure.notice")
def test_page_without_a_size_rule_accepts_a_large_body(vault: Vault) -> None:
    assert w(vault, "note", {}, "x" * 100_000).ok
    assert len(vault.read("note").body) == 100_001


@arch.holds("flow.write.refuse")
def test_malformed_watch_is_refused(vault: Vault) -> None:
    result = w(vault, "supplier", {"watch": [{"on": "cooler"}]})
    assert not result.ok and result.reason.startswith("shape")


def watch_pair(vault: Vault) -> None:
    w(vault, "cooler", {"stock": 40})
    w(
        vault,
        "supplier",
        {
            "reorder": False,
            "watch": [{"on": "cooler", "when": "other.stock < 10", "set": {"reorder": "true"}}],
        },
    )


@arch.holds("law.event.seal", "law.reflex.free", "flow.watch.react")
def test_reaction_is_caused_by_and_signed_by_the_reacting_page(vault: Vault) -> None:
    watch_pair(vault)
    first = w(vault, "cooler", {"stock": 4})
    assert vault.read("supplier").fields["reorder"] is True
    subject, found = message(vault)
    assert subject == "write supplier" and found["Cause"] == first.id
    assert signed_by(vault.path) == "supplier@conky"
    assert signed_by(vault.path, first.id) == "alice@conky"
    vault.verify()


@arch.holds("flow.watch.react")
def test_reaction_that_changes_nothing_is_skipped(vault: Vault) -> None:
    watch_pair(vault)
    w(vault, "cooler", {"stock": 4})
    count = len(commits(vault))
    w(vault, "cooler", {"stock": 3})
    assert len(commits(vault)) == count + 1


@arch.holds("flow.watch.react")
def test_reaction_cycle_stops_at_depth_12(vault: Vault) -> None:
    for me, other in (("a", "b"), ("b", "a")):
        w(
            vault,
            me,
            {"n": 0, "watch": [{"on": other, "when": "true", "set": {"n": "other.n + 1"}}]},
        )
    before = len(commits(vault))
    w(vault, "a", {"n": 100})
    added = [message(vault, c)[1]["Kind"] for c in commits(vault)[before:]]
    assert added.count("refused") == 1 and added.count("write") == 13
    assert "cycle" in message(vault)[1]["Reason"]
    vault.verify()


@arch.holds("flow.watch.react")
def test_watch_key_on_is_plain_text_in_frontmatter(vault: Vault) -> None:
    watch_pair(vault)
    assert "- on: cooler\n" in (vault.pages_dir / "supplier.md").read_text()
    assert vault.read("supplier").watch[0]["on"] == "cooler"


MEASURE = [
    {"on": "ledger", "when": "true", "set": {"pressure": "size / 400"}},
    {"on": "ledger", "when": "page.pressure >= 2", "set": {"state": "'crowded'"}},
]


def pressure_sequence(vault: Vault):
    w(vault, "ledger", {"pressure": 0, "state": "calm", "watch": MEASURE})
    w(
        vault,
        "tidy",
        {"watch": [{"on": "ledger", "when": "other.state == 'crowded'", "set": {"seen": "true"}}]},
    )
    return w(vault, "ledger", {}, "x" * 1000)


@arch.holds("law.pressure.notice", "flow.watch.measure")
def test_pressure_rises_without_refusing_work(vault: Vault) -> None:
    w(vault, "ledger", {"pressure": 0, "watch": MEASURE[:1]})
    result = w(vault, "ledger", {}, "x" * 100_000)
    assert result.ok
    assert vault.read("ledger").fields["pressure"] >= 250
    subject, found = message(vault)
    assert subject == "write ledger" and found["Cause"] == result.id
    assert "refused" not in {message(vault, c)[1]["Kind"] for c in commits(vault)}
    vault.verify()


@arch.holds("law.pressure.notice", "flow.watch.measure")
def test_threshold_fires_a_reaction_and_the_sequence_settles(
    vault: Vault, tmp_path: Path, keys_dir: Path
) -> None:
    pressure_sequence(vault)
    assert vault.read("ledger").fields["state"] == "crowded"
    assert vault.read("tidy").fields["seen"] is True
    assert "refused" not in {message(vault, c)[1]["Kind"] for c in commits(vault)}
    again = Vault.init(tmp_path / "again", keys_dir)
    pressure_sequence(again)
    assert len(commits(vault)) == len(commits(again)) < 12
    vault.verify()


@arch.holds("law.measure.watch")
def test_other_size_is_visible_to_a_watcher(vault: Vault) -> None:
    w(vault, "gauge", {"watch": [{"on": "cooler", "when": "true", "set": {"seen": "other_size"}}]})
    w(vault, "cooler", {}, "x" * 500)
    assert vault.read("gauge").fields["seen"] == len((vault.pages_dir / "cooler.md").read_bytes())


def make_history(vault: Vault) -> None:
    w(vault, "stand", {"rules": ["page.stock >= 0"], "stock": 0})
    w(vault, "cooler", {"within": "stand", "stock": 40}, "Bread.")
    w(vault, "cooler", {"stock": -5})
    w(vault, "cooler", {"stock": 7})


@arch.holds("law.page.commit", "flow.vault.rebuild")
def test_hand_edited_page_fails_verify_and_blocks_writes(vault: Vault) -> None:
    make_history(vault)
    vault.verify()
    page = vault.pages_dir / "cooler.md"
    page.write_text(page.read_text().replace("stock: 7", "stock: 8"))
    with pytest.raises(VerifyFailed, match="rebuild"):
        vault.verify()
    with pytest.raises(BadInput, match="rebuild"):
        w(vault, "cooler", {"stock": 9})
    vault.rebuild()
    vault.verify()
    assert page.read_text().count("stock: 7") == 1
    assert w(vault, "cooler", {"stock": 9}).ok


@arch.holds("law.page.commit", "flow.vault.rebuild")
def test_rebuild_discards_stray_files(vault: Vault) -> None:
    make_history(vault)
    before = pages(vault)
    (vault.pages_dir / "ghost.md").write_text("---\n---\n")
    (vault.pages_dir / "cooler.md").unlink()
    vault.rebuild()
    assert pages(vault) == before
    vault.verify()


@arch.holds("flow.vault.verify")
def test_unsigned_commit_fails_verify(vault: Vault) -> None:
    make_history(vault)
    page = vault.pages_dir / "cooler.md"
    page.write_text(page.read_text().replace("stock: 7", "stock: 8"))
    git(vault.path, "-c", "commit.gpgsign=false", "commit", "-qam", "edit")
    with pytest.raises(VerifyFailed, match="signature"):
        vault.verify()


@arch.holds("flow.vault.verify")
def test_commit_signed_by_an_unlisted_key_fails_verify(vault: Vault, tmp_path: Path) -> None:
    make_history(vault)
    stranger = tmp_path / "stranger"
    subprocess.run(["ssh-keygen", "-q", "-t", "ed25519", "-N", "", "-f", str(stranger)], check=True)
    git(
        vault.path,
        "-c",
        f"user.signingkey={stranger}",
        "commit",
        "-qS",
        "--allow-empty",
        "-m",
        "write cooler\n\nKind: write\nPage: cooler",
    )
    with pytest.raises(VerifyFailed, match="signature"):
        vault.verify()


@arch.holds("flow.vault.verify")
def test_commit_without_a_kind_trailer_fails_verify(vault: Vault) -> None:
    make_history(vault)
    git(
        vault.path,
        "-c",
        "user.signingkey=" + str(vault.keys_dir / "alice"),
        "commit",
        "-qS",
        "--allow-empty",
        "-m",
        "x",
    )
    with pytest.raises(VerifyFailed, match="Kind"):
        vault.verify()


@arch.holds("flow.vault.verify")
def test_write_commit_touching_other_files_fails_verify(vault: Vault) -> None:
    make_history(vault)
    (vault.path / "notes.txt").write_text("x")
    git(vault.path, "add", "notes.txt")
    git(
        vault.path,
        "-c",
        f"user.signingkey={vault.keys_dir / 'alice'}",
        "commit",
        "-qS",
        "-m",
        "write cooler\n\nKind: write\nPage: cooler",
    )
    with pytest.raises(VerifyFailed, match="notes.txt"):
        vault.verify()


@arch.holds("flow.vault.verify")
def test_refused_commit_that_changes_a_page_fails_verify(vault: Vault) -> None:
    make_history(vault)
    page = vault.pages_dir / "cooler.md"
    page.write_text(page.read_text().replace("stock: 7", "stock: 8"))
    git(
        vault.path,
        "-c",
        f"user.signingkey={vault.keys_dir / 'alice'}",
        "commit",
        "-q",
        "-S",
        "-a",
        "-m",
        "refused cooler\n\nKind: refused\nPage: cooler",
    )
    with pytest.raises(VerifyFailed, match="refused"):
        vault.verify()


@arch.holds("law.vault.travel", "flow.vault.clone")
def test_vault_travels_alone_by_clone_and_by_bundle(vault: Vault, tmp_path: Path) -> None:
    make_history(vault)
    nowhere = tmp_path / "no-such-keys"
    git(tmp_path, "clone", "-q", str(vault.path), "copy")
    copy = Vault(tmp_path / "copy", nowhere)
    copy.verify()
    assert copy.read("cooler").fields["stock"] == 7
    assert copy.log() == vault.log()
    bundle = tmp_path / "vault.bundle"
    git(vault.path, "bundle", "create", str(bundle), "--all")
    git(tmp_path, "clone", "-q", str(bundle), "from-bundle")
    from_bundle = Vault(tmp_path / "from-bundle", nowhere)
    from_bundle.verify()
    assert pages(from_bundle) == pages(vault)
    assert not nowhere.exists()


@arch.holds("law.vault.travel")
def test_no_private_key_material_under_the_vault(vault: Vault, keys_dir: Path) -> None:
    make_history(vault)
    private = (keys_dir / "alice").read_text()
    body = "".join(private.splitlines()[1:-1])
    assert "PRIVATE KEY" in private and body
    assert keys_dir not in vault.path.parents and vault.path not in keys_dir.parents
    for path in vault.path.rglob("*"):
        if path.is_file():
            data = path.read_bytes()
            assert b"PRIVATE KEY" not in data and body.encode() not in data
    assert body not in git(vault.path, "log", "-p", "--all")
    assert not [p for p in vault.path.rglob("*") if p.name == "alice"]


@arch.holds("flow.page.read")
def test_embeds_resolve_on_read(vault: Vault) -> None:
    w(vault, "cooler", {"stock": 40})
    w(vault, "sign", {}, "We hold ![[cooler#stock]] cups.")
    assert vault.read("sign").body == "We hold 40 cups.\n"
    assert "![[cooler#stock]]" in (vault.pages_dir / "sign.md").read_text()
    w(vault, "cooler", {"stock": 12})
    assert vault.read("sign").body == "We hold 12 cups.\n"


@arch.holds("flow.page.read")
def test_missing_embed_target_resolves_to_empty(vault: Vault) -> None:
    w(vault, "cooler", {"stock": 1})
    w(vault, "sign", {}, "a ![[nowhere#x]] b ![[cooler#nofield]] c")
    assert vault.read("sign").body == "a  b  c\n"


@arch.holds("law.measure.watch", "flow.watch.measure")
def test_history_needs_no_expressions(
    vault: Vault, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    pressure_sequence(vault)

    def boom(*args, **kwargs):
        raise AssertionError("an expression was evaluated")

    for target in (
        "conky.vault.evaluate",
        "conky.vault.holds",
        "conky.rules.evaluate",
        "conky.rules.holds",
    ):
        monkeypatch.setattr(target, boom)
    git(tmp_path, "clone", "-q", str(vault.path), "copy")
    copy = Vault(tmp_path / "copy", tmp_path / "no-such-keys")
    copy.verify()
    assert pages(copy) == pages(vault)
    assert copy.read("ledger").fields["state"] == "crowded"


@arch.holds("flow.page.read")
def test_log_lists_history_oldest_first(vault: Vault) -> None:
    first = w(vault, "cooler", {"rules": ["page.stock >= 0"], "stock": 5})
    w(vault, "cooler", {"stock": -1})
    lines = vault.log()
    assert [line.split()[3] for line in lines] == ["write", "refused"]
    assert lines[0].startswith(f"{first.id[:7]} 2026-01-01T00:00:00Z alice write cooler")
    assert lines[1].endswith("rule: page.stock >= 0 (from cooler) is false")


def test_opening_a_directory_that_is_not_a_vault_says_how_to_create_one(tmp_path: Path) -> None:
    with pytest.raises(BadInput, match="conky init"):
        Vault(tmp_path)


GOLDEN = Path(__file__).parent / "golden"


@arch.holds("law.vault.golden", "law.data.three")
def test_golden_vault_still_reads(tmp_path: Path) -> None:
    git(tmp_path, "clone", "-q", str(GOLDEN / "v1.bundle"), "golden")
    golden = Vault(tmp_path / "golden", tmp_path / "no-such-keys")
    golden.verify()
    expected = json.loads((GOLDEN / "v1.pages.json").read_text(encoding="utf-8"))
    found = {p.stem: p.read_text(encoding="utf-8") for p in golden.pages_dir.glob("*.md")}
    assert found == expected and len(found) >= 4


@arch.holds("law.context.down", "law.rule.tighten")
def test_a_changed_space_field_refuses_the_next_member_write(vault: Vault) -> None:
    assert w(vault, "camp", {"limit": 5}).ok
    assert w(
        vault, "scout", {"within": "camp", "rules": ["!has(page.cups) || page.cups <= space.limit"]}
    ).ok
    assert w(vault, "scout", {"cups": 4}).ok
    assert w(vault, "camp", {"limit": 2}).ok
    assert vault.read("scout").fields["cups"] == 4
    refused = w(vault, "scout", {"cups": 4, "note": "again"})
    assert not refused.ok and "space.limit" in refused.reason
    assert message(vault)[1]["Kind"] == "refused"
