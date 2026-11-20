"""An answer that is pages: a character writes pages through the same write path as anyone.

The model is a small local program that prints a prepared answer. No test reaches a live model.
"""

import json
import sys
from pathlib import Path

import pytest

from conky import Vault, arch
from conky.answer import END, HEADER, instruction, split
from conky.cli import main
from conky.errors import BadInput
from conky.git import trailers
from conky.vault import MAX_DEPTH

from .conftest import AT, git, signed_by

PROGRAM = """import json, pathlib, sys
here = pathlib.Path(__file__).parent
prompt = sys.stdin.read()
with (here / "asked.jsonl").open("a") as log:
    log.write(json.dumps(prompt) + "\\n")
n = len((here / "asked.jsonl").read_text().splitlines())
print((here / "answer.txt").read_text().replace("{n}", str(n)))
"""
TRIGGER = "Tidy up after ![[ticket#text]]"


class Stand:
    """A stand-in model: prints the prepared answer and records every prompt it was sent."""

    def __init__(self, folder: Path) -> None:
        self.folder = folder
        folder.mkdir()
        (folder / "model.py").write_text(PROGRAM, encoding="utf-8")

    def says(self, text: str) -> None:
        (self.folder / "answer.txt").write_text(text, encoding="utf-8")

    @property
    def prompts(self) -> list[str]:
        log = self.folder / "asked.jsonl"
        return [json.loads(line) for line in log.read_text().splitlines()] if log.exists() else []


@pytest.fixture
def stand(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Stand:
    found = Stand(tmp_path / "stand")
    monkeypatch.setenv("CONKY_COMMAND_STAND", f"{sys.executable} {found.folder / 'model.py'}")
    return found


def w(vault: Vault, page: str, changes: dict, actor: str = "alice"):
    return vault.write(page, changes, None, actor=actor, at=AT)


def entry(**ask: str) -> dict:
    return {
        "on": "ticket",
        "when": "true",
        "ask": {"provider": "helper", "prompt": TRIGGER, "writes": "den", "into": "said", **ask},
    }


@pytest.fixture
def den(vault: Vault, stand: Stand) -> Vault:
    """A provider, a space called den and a character called scribe that lives in it."""
    assert w(vault, "helper", {"api": "command", "command": "stand"}).ok
    assert w(vault, "den", {}).ok
    assert w(vault, "ticket", {"text": "one"}).ok
    assert w(vault, "scribe", {"within": "den", "watch": [entry()]}).ok
    return vault


def trigger(vault: Vault, text: str) -> None:
    assert w(vault, "ticket", {"text": text}).ok


def history(vault: Vault) -> list[tuple[str, dict[str, str]]]:
    """Every commit, oldest first, as its id and trailers."""
    ids = git(vault.path, "log", "--reverse", "--format=%H", "main").split()
    return [(c, trailers(git(vault.path, "log", "-1", "--format=%B", c))) for c in ids]


def refusals(vault: Vault) -> list[dict[str, str]]:
    return [found for _, found in history(vault) if found["Kind"] == "refused"]


def exists(vault: Vault, page: str) -> bool:
    return (vault.pages_dir / f"{page}.md").exists()


TWO = """All tidied.
=== page: note-a ===
---
within: den
topic: one
---
First note.
=== page: note-b ===
---
within: den
---
Second note.
"""


@arch.holds("law.answer.pages", "flow.ask.pages")
def test_an_answer_with_two_pages_writes_both_as_the_asker_caused_by_the_answer(
    den: Vault, stand: Stand
) -> None:
    stand.says(TWO)
    trigger(den, "two")
    assert den.read("scribe").fields["said"] == "All tidied."
    first, second = den.read("note-a"), den.read("note-b")
    assert (first.within, first.fields, first.body) == ("den", {"topic": "one"}, "First note.\n")
    assert (second.within, second.body) == ("den", "Second note.\n")
    log = history(den)
    answer, (a, a_tags), (b, b_tags) = log[-3][0], log[-2], log[-1]
    assert log[-3][1]["Page"] == "scribe" and "Model" in log[-3][1]
    assert (a_tags["Page"], b_tags["Page"]) == ("note-a", "note-b")
    assert a_tags["Cause"] == answer and b_tags["Cause"] == answer
    assert git(den.path, "log", "-1", "--format=%an", b).strip() == "scribe"
    assert signed_by(den.path, a) == "scribe@conky" == signed_by(den.path, b)
    den.verify()


def test_the_instruction_comes_before_the_prompt_in_what_is_sent_and_recorded(
    den: Vault, stand: Stand
) -> None:
    stand.says("Nothing to add.")
    trigger(den, "one")
    sent = stand.prompts[-1]
    assert sent == instruction("scribe", "den", False) + "Tidy up after one"
    assert "=== page: <name> ===" in sent and "within: den" in sent
    body = git(den.path, "log", "-1", "--format=%B")
    assert sent in body
    assert den.read("scribe").fields["said"] == "Nothing to add."
    assert not refusals(den)
    den.verify()


def test_the_instruction_example_is_a_page_the_parser_cuts(den: Vault) -> None:
    text = instruction("scribe", "den", True)
    example = text[text.index(HEADER) : text.index(END) + len(END)].replace("<name>", "note")
    plain, blocks = split("Done.\n" + example)
    assert plain == "Done."
    assert [(b.name, b.problem) for b in blocks] == [("note", None)]
    assert "within: den" in blocks[0].text and "what you want to keep" in blocks[0].text
    assert "scribe" in text and "shown what den holds" in text
    assert "shown what" not in instruction("scribe", "den", False)
    assert w(den, "note", {"within": "den"}).ok


def test_a_note_is_in_the_next_prompt_that_embeds_the_members_and_in_its_read_trailer(
    den: Vault, stand: Stand
) -> None:
    prompt = "Tidy up after ![[ticket#text]]\n![[den#members]]"
    assert w(den, "scribe", {"watch": [entry(prompt=prompt)]}).ok
    stand.says("Kept.\n=== page: note-a ===\n---\nwithin: den\n---\nBuy oxen first.\n")
    trigger(den, "one")
    stand.says("Nothing more.")
    trigger(den, "two")
    first, second = stand.prompts[-2:]
    assert "note-a" not in first
    assert "note-a: Buy oxen first." in second
    assert "shown what den holds" in second
    log = history(den)
    asked = [tags for _, tags in log if tags["Page"] == "scribe" and "Model" in tags]
    assert "den" in asked[-1]["Read"].split(", ")
    den.verify()


def test_an_ask_without_writes_is_sent_as_it_is(den: Vault, stand: Stand) -> None:
    ask = {"provider": "helper", "prompt": "Hi", "into": "x"}
    assert w(den, "plain", {"watch": [{"on": "ticket", "when": "true", "ask": ask}]}).ok
    stand.says("ok")
    trigger(den, "again")
    assert "Hi" in stand.prompts


def test_a_settled_question_is_not_asked_again_and_a_changed_one_is(
    den: Vault, stand: Stand
) -> None:
    stand.says(TWO)
    trigger(den, "two")
    assert len(stand.prompts) == 1
    assert w(den, "ticket", {"note": "unrelated"}).ok
    assert len(stand.prompts) == 1
    trigger(den, "three")
    assert len(stand.prompts) == 2


@arch.holds("law.reach.down", "flow.ask.pages")
def test_a_page_outside_the_space_is_refused_and_recorded_and_the_others_land(
    den: Vault, stand: Stand
) -> None:
    assert w(den, "ledger", {"total": 3}).ok
    stand.says(
        "Mixed.\n"
        "=== page: note-a ===\n---\nwithin: den\n---\nIn.\n"
        "=== page: stray ===\n---\nwithin: elsewhere\n---\nOut.\n"
        "=== page: loose ===\n---\nx: 1\n---\n"
        "=== page: ledger ===\n---\nwithin: den\ntotal: 0\n---\n"
        "=== page: den ===\n---\nwithin: den\n---\n"
        "=== page: note-b ===\n---\nwithin: den\n---\nAlso in.\n"
    )
    trigger(den, "mixed")
    assert exists(den, "note-a") and exists(den, "note-b")
    assert not exists(den, "stray") and not exists(den, "loose")
    assert den.read("ledger").fields == {"total": 3} and den.read("ledger").within is None
    assert den.read("den").within is None
    found = refusals(den)
    assert [r["Page"] for r in found] == ["stray", "loose", "ledger", "den"]
    assert all(r["Reason"].startswith("limit: ") for r in found)
    assert "not within space den" in found[0]["Reason"]
    assert "lies outside space den" in found[2]["Reason"]
    answer = history(den)[-7][0]
    assert all(r["Cause"] == answer for r in found)
    den.verify()


def test_a_page_inside_a_space_it_created_is_within_the_named_space(
    den: Vault, stand: Stand
) -> None:
    stand.says(
        "=== page: shelf ===\n---\nwithin: den\n---\n"
        "=== page: book ===\n---\nwithin: shelf\n---\nA book.\n"
    )
    trigger(den, "shelves")
    assert exists(den, "shelf") and exists(den, "book")
    assert not refusals(den)


@arch.holds("law.rule.tighten")
def test_a_rule_of_a_space_refuses_a_page_that_breaks_it(den: Vault, stand: Stand) -> None:
    assert w(den, "shelf", {"within": "den", "rules": ["size <= 200"]}).ok
    stand.says(
        "=== page: small ===\n---\nwithin: shelf\n---\nShort.\n"
        f"=== page: large ===\n---\nwithin: shelf\n---\n{'long ' * 80}\n"
    )
    trigger(den, "rules")
    assert exists(den, "small") and not exists(den, "large")
    asked, again = refusals(den)
    assert asked["Page"] == again["Page"] == "large" and asked["From"] == "shelf"
    assert asked["Reason"].startswith("rule: size <= 200 (from shelf)")
    den.verify()


@arch.holds("law.rule.tighten")
def test_a_character_can_add_a_rule_to_a_space_it_made_and_the_rule_binds_a_later_write(
    den: Vault, stand: Stand
) -> None:
    stand.says('=== page: shelf ===\n---\nwithin: den\nrules:\n- "size <= 120"\n---\n')
    trigger(den, "make")
    assert den.read("shelf").rules == ["size <= 120"]
    stand.says(
        "=== page: small ===\n---\nwithin: shelf\n---\nShort.\n"
        f"=== page: large ===\n---\nwithin: shelf\n---\n{'long ' * 60}\n"
    )
    trigger(den, "use")
    assert exists(den, "small") and not exists(den, "large")
    asked, again = refusals(den)
    assert asked["Reason"].startswith("rule: size <= 120 (from shelf)")
    assert again["Reason"] == asked["Reason"]
    den.verify()


def test_the_asker_can_rewrite_its_own_watch_and_it_takes_effect_on_the_next_write(
    den: Vault, stand: Stand
) -> None:
    stand.says(
        '=== page: scribe ===\n---\nwatch:\n- on: gate\n  when: "true"\n  set:\n'
        "    seen: \"'yes'\"\n---\n"
    )
    trigger(den, "rewrite")
    scribe = den.read("scribe")
    assert scribe.within == "den" and [e["on"] for e in scribe.watch] == ["gate"]
    assert "seen" not in scribe.fields
    assert w(den, "gate", {"open": True}).ok
    assert den.read("scribe").fields["seen"] == "yes"
    den.verify()


@arch.holds("law.reach.down")
def test_a_watch_entry_cannot_widen_where_a_character_may_write(den: Vault, stand: Stand) -> None:
    assert w(den, "lobby", {}).ok
    stand.says(
        '=== page: scribe ===\n---\nwatch:\n- on: ticket\n  when: "true"\n  ask:\n'
        "    prompt: q\n    writes: lobby\n---\n"
        '=== page: helper-note ===\n---\nwithin: den\nwatch:\n- on: ticket\n  when: "true"\n'
        "  ask:\n    prompt: q\n    writes: den\n---\n"
    )
    trigger(den, "widen")
    assert [e["ask"]["writes"] for e in den.read("scribe").watch] == ["den"]
    assert exists(den, "helper-note")
    (found,) = refusals(den)
    assert found["Page"] == "scribe" and "outside space den" in found["Reason"]
    assert found["Reason"].startswith("limit: ")


@arch.holds("law.runtime.fixed", "flow.ask.pages")
def test_a_character_cannot_write_a_secret_or_a_command_into_a_page(
    den: Vault, stand: Stand
) -> None:
    assert w(den, "known", {"within": "den", "api": "openai", "secret": "mine"}).ok
    stand.says(
        "=== page: own ===\n---\nwithin: den\napi: openai\nsecret: mine\n---\n"
        "=== page: prog ===\n---\nwithin: den\napi: command\ncommand: claude\n---\n"
        "=== page: known ===\n---\nurl: http://127.0.0.1:1/\n---\n"
        "=== page: fine ===\n---\nwithin: den\napi: openai\nurl: http://127.0.0.1:1/\n---\n"
    )
    trigger(den, "providers")
    assert exists(den, "fine") and not exists(den, "own") and not exists(den, "prog")
    assert "url" not in den.read("known").fields
    found = refusals(den)
    assert [r["Page"] for r in found] == ["own", "prog", "known"]
    assert all("secret or a command" in r["Reason"] for r in found)


@arch.holds("flow.ask.pages")
def test_a_malformed_block_is_one_recorded_refusal_and_the_pages_around_it_still_apply(
    den: Vault, stand: Stand
) -> None:
    stand.says(
        "Plain start.\n"
        "=== page: first ===\n---\nwithin: den\n---\n"
        "=== page: Bad Name ===\n---\nwithin: den\n---\n"
        "=== page: ../escape ===\n---\nwithin: den\n---\n"
        "=== page: nofront ===\njust words\n"
        "=== page: open ===\n---\nwithin: den\n"
        "=== page: yaml ===\n---\nwithin: [den\n---\n"
        "=== page: list ===\n---\n- a\n- b\n---\n"
        "=== page: when ===\n---\nwithin: den\nwhen: 2026-01-01\n---\n"
        "=== page: shaped ===\n---\nwithin: den\nrules: nope\n---\n"
        "=== page: last ===\n---\nwithin: den\n---\nLast.\n=== end ===\nPlain end.\n"
    )
    trigger(den, "bad")
    assert exists(den, "first") and exists(den, "last")
    assert den.read("scribe").fields["said"] == "Plain start.\nPlain end."
    found = refusals(den)
    assert len(found) == 8
    assert [r["Page"] for r in found] == [
        "scribe",
        "scribe",
        "nofront",
        "open",
        "yaml",
        "list",
        "when",
        "shaped",
    ]
    assert all(r["Reason"].startswith("shape: ") for r in found)
    assert "does not name a page" in found[0]["Reason"]
    assert "does not start with frontmatter" in found[2]["Reason"]
    assert "not closed" in found[3]["Reason"]
    assert "not valid YAML" in found[4]["Reason"]
    assert "keys with values" in found[5]["Reason"]
    assert "plain data" in found[6]["Reason"]
    assert "rules must be a list" in found[7]["Reason"]
    den.verify()


def test_an_answer_with_no_pages_is_just_text(den: Vault, stand: Stand) -> None:
    stand.says("Only words, no pages.")
    trigger(den, "words")
    assert den.read("scribe").fields["said"] == "Only words, no pages."
    assert not refusals(den)


def test_an_entry_with_only_writes_keeps_the_text_out_and_still_settles(
    den: Vault, stand: Stand
) -> None:
    assert w(
        den,
        "scribe",
        {"watch": [{**entry(), "ask": {"provider": "helper", "prompt": TRIGGER, "writes": "den"}}]},
    ).ok
    stand.says("Words.\n=== page: only ===\n---\nwithin: den\n---\n")
    trigger(den, "solo")
    assert exists(den, "only") and "said" not in den.read("scribe").fields
    assert "writes_asked" in den.read("scribe").fields
    assert w(den, "ticket", {"note": "again"}).ok
    assert len(stand.prompts) == 1


@arch.holds("flow.ask.pages")
def test_a_character_writing_a_page_that_asks_again_stops_at_the_depth_cap(
    den: Vault, stand: Stand
) -> None:
    stand.says(
        '=== page: note-{n} ===\n---\nwithin: den\nwatch:\n- on: note-{n}\n  when: "true"\n'
        "  ask:\n    provider: helper\n    prompt: again {n}\n    writes: den\n---\n"
    )
    trigger(den, "loop")
    assert 2 < len(stand.prompts) <= MAX_DEPTH
    assert any("cycle" in r["Reason"] for r in refusals(den))
    assert exists(den, f"note-{len(stand.prompts)}")
    den.verify()


def test_with_no_model_a_sentence_is_written_and_no_pages(den: Vault, stand: Stand) -> None:
    assert w(den, "scribe", {"watch": [entry(provider="ghost")]}).ok
    trigger(den, "nobody")
    assert den.read("scribe").fields["said"].startswith("No model was around")
    assert not stand.prompts and not any(p.startswith("note") for p in den.log())
    assert refusals(den)[-1]["Reason"].startswith("model: ")
    den.verify()


def test_an_entry_with_only_writes_and_no_model_is_a_recorded_refusal(den: Vault) -> None:
    assert w(
        den,
        "scribe",
        {"watch": [{"on": "ticket", "when": "true", "ask": {"prompt": "q", "writes": "den"}}]},
    ).ok
    trigger(den, "nobody")
    reason = refusals(den)[-1]["Reason"]
    assert reason.startswith("model: no model answered, so no pages were written")
    den.verify()


def test_ask_needs_a_field_or_a_space(den: Vault) -> None:
    with pytest.raises(BadInput, match="a field to write the answer to, a space"):
        den.ask("scribe", None, prompt="q", actor="scribe", at=AT)


def test_conky_ask_writes_pages_and_prints_what_landed_and_what_was_refused(
    den: Vault, stand: Stand, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    stand.says(
        "Told.\n=== page: note-a ===\n---\nwithin: den\n---\nIn.\n"
        "=== page: stray ===\n---\nwithin: elsewhere\n---\n"
    )
    ask = ["ask", "scribe", "said", "--writes", "den", "--provider", "helper", "--prompt", "Go"]
    code = main(
        ["--vault", str(den.path), "--keys", str(tmp_path / "keys"), *ask, "--as", "scribe"]
    )
    seen = capsys.readouterr()
    assert code == 1
    assert seen.out.startswith("written (commit ") and "note-a: written (commit " in seen.out
    assert "stray: refused (commit " in seen.err and "limit: " in seen.err
    assert den.read("note-a").within == "den" and den.read("scribe").fields["said"] == "Told."
    den.verify()
    only = ["ask", "scribe", "--writes", "den", "--provider", "helper", "--prompt", "Go"]
    stand.says("=== page: note-b ===\n---\nwithin: den\n---\n")
    assert (
        main(["--vault", str(den.path), "--keys", str(tmp_path / "keys"), *only, "--as", "scribe"])
        == 0
    )
    assert exists(den, "note-b")


BIND = '=== page: den ===\n---\nrules:\n  - each: "page.amount <= 50"\n---\n'


@arch.holds("law.rule.tighten", "flow.ask.pages")
def test_an_answer_adds_a_rule_to_its_space_signed_by_the_asker(den: Vault, stand: Stand) -> None:
    stand.says("Bound.\n" + BIND)
    trigger(den, "bind")
    assert den.read("den").rules == [{"each": "page.amount <= 50"}]
    assert not refusals(den)
    commit = history(den)[-1][0]
    assert signed_by(den.path, commit) == "scribe@conky"
    assert w(den, "pay", {"within": "den", "amount": 30}).ok
    assert not w(den, "pay-more", {"within": "den", "amount": 90}).ok
    den.verify()


def test_an_answer_keeps_the_rules_its_space_has_and_ignores_a_duplicate(
    den: Vault, stand: Stand
) -> None:
    kept = "!has(page.cash) || page.cash >= 0"
    block = '=== page: den ===\n---\nrules:\n  - each: "!has(page.amount)"\n---\n'
    assert w(den, "den", {"rules": [kept]}).ok
    stand.says(block + block)
    trigger(den, "bind")
    assert den.read("den").rules == [kept, {"each": "!has(page.amount)"}]
    stand.says("=== page: den ===\n---\nrules: []\n---\n")
    trigger(den, "unbind")
    assert den.read("den").rules == [kept, {"each": "!has(page.amount)"}]
    assert not refusals(den)
    den.verify()


def test_an_answer_cannot_set_a_field_or_a_body_on_its_space(den: Vault, stand: Stand) -> None:
    stand.says(
        "=== page: den ===\n---\nrules:\n  - each: page.amount <= 50\ncash: 5000\n---\n"
        "=== page: den ===\n---\nrules:\n  - each: page.amount <= 60\n---\nA body.\n"
        "=== page: den ===\n---\nwithin: scribe\nrules: []\n---\n"
    )
    trigger(den, "widen")
    assert den.read("den").rules == [] and den.read("den").fields == {}
    assert den.read("den").body == "" and den.read("den").within is None
    found = refusals(den)
    assert [r["Page"] for r in found] == ["den", "den", "den"]
    assert all(r["Reason"].startswith("limit: ") for r in found)
    assert "add rules to it and nothing else" in found[0]["Reason"]
    den.verify()


def test_an_answer_cannot_bind_a_space_it_was_not_given(den: Vault, stand: Stand) -> None:
    stand.says("=== page: other ===\n---\nrules:\n  - each: page.amount <= 1\n---\n")
    trigger(den, "bind")
    (found,) = refusals(den)
    assert found["Reason"].startswith("limit: ") and "not within space den" in found["Reason"]
