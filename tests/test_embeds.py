"""An embed inside the text an embed brings in is followed, to a stated depth."""

import os
import stat
import sys
from pathlib import Path

import pytest
from bench import cards

from conky import Vault, arch, page, voice
from conky.page import EMBED_DEPTH, Page, embedded, resolve_text

from .conftest import AT, git


def pages(**made: Page) -> dict[str, Page]:
    return dict(made)


def chain() -> dict[str, Page]:
    return {
        "a": Page(body="a<![[b]]>"),
        "b": Page(body="b<![[c]]>"),
        "c": Page(body="c<![[d]]>"),
        "d": Page(body="d"),
    }


@arch.holds("law.embed.followed")
def test_an_embed_in_a_body_that_is_embedded_brings_in_the_field_it_names() -> None:
    found = pages(
        ear=Page(fields={"heard": "the parcel is on shelf 12"}),
        senses=Page(body="What is sensed: ![[ear#heard]]"),
    )
    assert (
        resolve_text("Clerk: ![[senses]]", found)
        == "Clerk: What is sensed: the parcel is on shelf 12"
    )
    assert embedded("Clerk: ![[senses]]", found) == ["senses", "ear"]


def test_a_text_whose_embedded_pages_hold_no_embeds_resolves_as_it_always_did() -> None:
    found = pages(
        log=Page({}, body="first line\nsecond line\n"),
        ticket=Page(fields={"text": "printer jams", "n": 2, "ok": True}),
    )
    text = "Log: ![[log]] / ![[ticket#text]] ![[ticket#n]] ![[ticket#ok]] ![[ghost]] ![[ticket#no]]"
    assert resolve_text(text, found) == "Log: first line\nsecond line\n / printer jams 2 true  "
    assert embedded(text, found) == ["log", "ticket"]


@arch.holds("law.embed.followed")
def test_an_embed_is_followed_to_the_depth_and_cut_past_it_with_a_line_saying_so() -> None:
    found = chain()
    shown = resolve_text("![[a]]", found)
    assert shown == "a<b<c<" + voice.told("embed-depth", page="d", cap=EMBED_DEPTH) + ">>>"
    assert "d" not in embedded("![[a]]", found)
    assert embedded("![[a]]", found) == ["a", "b", "c"]


def test_the_depth_lives_in_one_place(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(page, "EMBED_DEPTH", 4)
    assert resolve_text("![[a]]", chain()) == "a<b<c<d>>>"
    assert embedded("![[a]]", chain()) == ["a", "b", "c", "d"]
    monkeypatch.setattr(page, "EMBED_DEPTH", 1)
    assert embedded("![[a]]", chain()) == ["a"]


@arch.holds("law.embed.followed")
def test_a_loop_is_cut_where_it_closes_and_said() -> None:
    found = pages(a=Page(body="a<![[b]]>"), b=Page(body="b<![[a]]>"))
    assert resolve_text("![[a]]", found) == "a<b<" + voice.told("embed-loop", page="a") + ">>"
    assert embedded("![[a]]", found) == ["a", "b"]
    own = pages(me=Page(body="I am ![[me]]"))
    assert resolve_text("![[me]]", own) == "I am " + voice.told("embed-loop", page="me")


def test_a_page_that_embeds_another_field_of_itself_is_not_a_loop() -> None:
    found = pages(a=Page(fields={"x": "ex"}, body="body ![[a#x]]"))
    assert resolve_text("![[a]]", found) == "body ex"
    assert embedded("![[a]]", found) == ["a"]
    assert resolve_text("![[a]] ![[a]]", found) == "body ex body ex"


def test_members_and_context_text_is_shown_as_written_but_an_embed_of_them_is_resolved() -> None:
    found = pages(
        den=Page(body="The den says ![[ear#heard]]"),
        ear=Page(fields={"heard": "shelf 12"}),
        kid=Page(within="den", body="kid text ![[ear#heard]]"),
        list=Page(body="Within: ![[den#members]]"),
        talk=Page(body="Told: ![[kid#context]]"),
    )
    assert resolve_text("![[den#members]]", found) == "kid: kid text ![[ear#heard]]"
    assert resolve_text("![[list]]", found) == "Within: kid: kid text ![[ear#heard]]"
    assert resolve_text("![[talk]]", found) == "Told: den says:\nThe den says ![[ear#heard]]"
    assert embedded("![[list]]", found) == ["list", "den"]


def test_a_nested_tally_of_asks_reads_as_it_does_at_the_top(vault: Vault) -> None:
    assert vault.write("desk", {"budget": {"asks": 3}}, "", actor="alice", at=AT).ok
    assert vault.write("gauge", {}, "Left: ![[desk#asks]]", actor="alice", at=AT).ok
    left = voice.line("asks-left", left=3, asks=3)
    found = vault._all()
    assert resolve_text("![[gauge]]", found, vault._asks_left(found)).strip() == f"Left: {left}"
    assert embedded("![[gauge]]", found, vault._asks_left(found)) == ["gauge"]
    assert resolve_text("![[desk#asks]]", found, vault._asks_left(found)) == left


def test_a_read_resolves_the_nested_text_and_the_stored_page_keeps_the_embed(
    vault: Vault,
) -> None:
    assert vault.write("ear", {"heard": "shelf 12"}, "", actor="alice", at=AT).ok
    assert vault.write("senses", {}, "Heard: ![[ear#heard]]", actor="alice", at=AT).ok
    assert vault.write("clerk", {}, "![[senses]]", actor="alice", at=AT).ok
    assert vault.read("clerk").body.strip() == "Heard: shelf 12"
    stored = (vault.path / "pages" / "clerk.md").read_text(encoding="utf-8")
    assert "![[senses]]" in stored
    assert "![[ear#heard]]" in (vault.path / "pages" / "senses.md").read_text(encoding="utf-8")


@arch.holds("law.embed.anonymous")
def test_what_a_nested_embed_shows_says_nothing_about_who_wrote_it(vault: Vault) -> None:
    assert vault.write("ear", {"heard": "shelf 12"}, "", actor="alice", at=AT).ok
    assert vault.write("senses", {}, "Heard: ![[ear#heard]]", actor="alice", at=AT).ok
    shown = resolve_text("![[senses]]", vault._all())
    assert shown.strip() == "Heard: shelf 12"
    for mark in ("Model", "Model-Name", "alice", "provider"):
        assert mark not in shown
    assert "alice" in git(vault.path, "log", "--format=%an %B")


def test_a_clerk_is_shown_the_fact_through_its_senses_page(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    program = tmp_path / "claude"
    program.write_text(f"#!{sys.executable}\nimport sys\nprint(sys.stdin.read())\n")
    program.chmod(program.stat().st_mode | stat.S_IEXEC)
    monkeypatch.setenv("PATH", f"{tmp_path}{os.pathsep}{os.environ['PATH']}")
    monkeypatch.setenv("CONKY_PROVIDER", "claude")
    monkeypatch.setenv("CONKY_COMMAND_CLAUDE", str(program))
    card = (
        Path(__file__).parent.parent / "bench" / "cards" / "a-clerk-reads-through-its-senses.yaml"
    )
    out = tmp_path / "out"
    assert cards.main([str(card), "--draws", "1", "--out", str(out)]) == 0
    row = (out / "rows.jsonl").read_text(encoding="utf-8")
    assert '"failed": []' in row
