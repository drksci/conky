"""A character born with a memory and a sense for what changed, as ordinary pages.

The starting pages are read from the card `a-clerk-notices-what-changed`, so they live in one
place. Every model is a small local program written here that answers by what its prompt holds.
No test reaches a live model.
"""

import json
import os
import re
import stat
import sys
from pathlib import Path

import pytest
from bench import cards

from conky import Vault, arch
from conky.git import trailers
from conky.page import load_value

from .conftest import AT, git

CARD = Path(__file__).parent.parent / "bench" / "cards" / "a-clerk-notices-what-changed.yaml"
STAND = """import json, os, pathlib, sys
here = pathlib.Path(__file__).parent
prompt = sys.stdin.read()
told = [os.environ.get("CONKY_ASK_MODEL"), os.environ.get("CONKY_ASK_EFFORT")]
with (here / "asked.jsonl").open("a") as log:
    log.write(json.dumps({"prompt": prompt, "told": told}) + "\\n")
answers = json.loads((here / "answers.json").read_text())
if "can keep pages in book" in prompt:
    print(answers["memory"])
elif "different from before" in prompt:
    print(answers["noticing"])
else:
    print(prompt)
"""
PARCEL = """=== page: parcel-for-mrs-okafor ===
---
within: book
---
Mrs Okafor's parcel is on shelf 12, and a clerk gives that to whoever comes for it.
=== end ==="""
QUIET = "Nothing more."
CHANGED = "A bicycle is on the shelf where Mrs Okafor's parcel was, which is odd."
CLERK = "You are the clerk at this desk."
BARRED = ("remember", "memor", "recall", "notic", "sense")
BARRED_WORDS = ("keep", "kept", "budget", "ask", "asks")


class Moments:
    """The card's pages in a vault, a stand-in program, and the moments the card's steps play."""

    def __init__(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, without: tuple = ()
    ) -> None:
        self.plan = load_value(CARD.read_text(encoding="utf-8"))
        self.folder = tmp_path / "stand"
        self.folder.mkdir(parents=True)
        (self.folder / "stand.py").write_text(STAND, encoding="utf-8")
        self.set(memory=QUIET, noticing="nothing")
        monkeypatch.setenv("CONKY_COMMAND_STAND", f"{sys.executable} {self.folder / 'stand.py'}")
        self.vault = Vault.init(tmp_path / "vault", tmp_path / "keys")
        self.pages = {n: f for n, f in self.plan["pages"].items() if n not in without}
        for name, fields in self.pages.items():
            self.put(name, fields)
        steps = [s["write"] for s in self.plan["steps"] if "write" in s]
        self.put(steps[0]["page"], steps[0]["fields"], steps[0]["body"])
        self.desks = [s["body"] for s in steps[1:]]
        self.done = 0

    def put(self, name: str, fields: dict, body: str | None = None):
        made = self.vault.write(name, fields, body, actor="alice", at=AT)
        assert made.ok, made.reason
        return made

    def set(self, **answers: str) -> None:
        path = self.folder / "answers.json"
        held = json.loads(path.read_text()) if path.exists() else {}
        path.write_text(json.dumps({**held, **answers}), encoding="utf-8")

    def moment(self, **answers: str) -> list[dict]:
        """Play the card's next desk write and return the calls it caused, oldest first."""
        self.set(**answers)
        before = len(self.calls())
        self.put("desk", {}, self.desks[self.done])
        self.done += 1
        return self.calls()[before:]

    def calls(self) -> list[dict]:
        log = self.folder / "asked.jsonl"
        return [json.loads(line) for line in log.read_text().splitlines()] if log.exists() else []

    def history(self) -> list[dict[str, str]]:
        ids = git(self.vault.path, "log", "--reverse", "--format=%H", "main").split()
        return [trailers(git(self.vault.path, "log", "-1", "--format=%B", i)) for i in ids]

    def limits(self, page: str) -> list[dict[str, str]]:
        return [
            t
            for t in self.history()
            if t.get("Reason", "").startswith("limit:") and t.get("Page") == page
        ]


def of(calls: list[dict], mark: str) -> list[str]:
    return [c["prompt"] for c in calls if mark in c["prompt"]]


def clerks(calls: list[dict]) -> list[str]:
    return [c["prompt"] for c in calls if c["prompt"].startswith(CLERK)]


def clerk_of(calls: list[dict]) -> str:
    (prompt,) = clerks(calls)
    return prompt


@pytest.fixture
def moments(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Moments:
    return Moments(tmp_path, monkeypatch)


@arch.holds("flow.ask.pages", "law.embed.shows")
def test_a_page_the_memory_wrote_within_the_book_is_signed_by_the_memory(moments: Moments) -> None:
    moments.moment(memory=PARCEL)
    kept = moments.vault.read("parcel-for-mrs-okafor")
    first = kept.body.splitlines()[0]
    assert "12" in first and "Mrs Okafor" in first and kept.within == "book"
    ids = git(moments.vault.path, "log", "--format=%H", "--", "pages/parcel-for-mrs-okafor.md")
    (commit,) = ids.split()
    got = trailers(git(moments.vault.path, "log", "-1", "--format=%B", commit))
    assert git(moments.vault.path, "log", "-1", "--format=%an", commit).strip() == "memory"
    answers = [t for t in moments.history() if t.get("Page") == "memory" and "Model" in t]
    assert got["Cause"] and got["Cause"] in git(moments.vault.path, "log", "--format=%H"), (
        "the cause is a commit of the history"
    )
    assert len(answers) == 1


@arch.holds("flow.ask.model", "law.reflex.down")
def test_a_noticing_that_says_nothing_leaves_the_field_empty_without_a_further_call(
    moments: Moments,
) -> None:
    first = moments.moment(noticing=CHANGED)
    assert moments.vault.read("noticing").fields["noticed"] == CHANGED
    assert CHANGED in clerk_of(first)
    second = moments.moment(noticing="Nothing.")
    assert moments.vault.read("noticing").fields["noticed"] == ""
    assert len(of(second, "different from before")) == 1
    assert CHANGED not in clerk_of(second)
    assert len(second) == 3


def test_the_noticing_page_is_shown_what_is_kept_beside_what_is_in_front_of_the_clerk(
    moments: Moments,
) -> None:
    moments.moment(memory=PARCEL)
    for _ in range(3):
        moments.moment()
    calls = moments.moment(noticing=CHANGED)
    (prompt,) = of(calls, "different from before")
    before, now = prompt.split("What it knew before:")[1].split("In front of it now:")
    assert "parcel-for-mrs-okafor: Mrs Okafor's parcel is on shelf 12" in before
    assert "bicycle" in now and "bicycle" not in before


@arch.holds("flow.ask.model", "law.embed.followed")
def test_the_clerk_is_shown_what_the_pages_wrote_and_is_told_nothing_of_how(
    moments: Moments,
) -> None:
    moments.moment(memory=PARCEL)
    for _ in range(3):
        moments.moment()
    prompt = clerk_of(moments.moment(noticing=CHANGED))
    assert CHANGED in prompt and "Mrs Okafor's parcel is on shelf 12" in prompt
    lowered = prompt.lower()
    for stem in BARRED:
        assert stem not in lowered, stem
    for word in BARRED_WORDS:
        assert not re.search(rf"\b{word}\b", lowered), word
    assert "![[" not in prompt


def test_each_page_that_asks_is_told_the_clerks_voice_and_its_own_model_and_effort(
    moments: Moments,
) -> None:
    voice = moments.plan["pages"]["the-clerk"]["voice"]
    calls = moments.moment(memory=PARCEL)
    assert len(calls) == 3
    for call in calls:
        assert voice in call["prompt"]
    told = {
        "different from before": ["claude-haiku-5-5", "low"],
        "can keep pages in book": ["claude-haiku-5-5", "low"],
        CLERK: [None, "medium"],
    }
    for mark, wanted in told.items():
        (call,) = [
            c
            for c in calls
            if (mark in c["prompt"] and c["prompt"].count(CLERK) <= 1)
            if mark != CLERK or c["prompt"].startswith(CLERK)
        ]
        assert call["told"] == wanted, mark


@arch.holds("law.budget.held", "law.refusal.record")
def test_a_budget_of_one_stops_each_page_at_its_second_moment_and_the_clerk_goes_on(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    held = Moments(tmp_path, monkeypatch)
    for name in ("memory", "noticing"):
        held.put(name, {**held.pages[name], "budget": {"asks": 1}})
    held.moment(memory=PARCEL)
    calls = held.moment()
    assert [c["told"] for c in calls] == [[None, "medium"]]
    assert len(held.limits("memory")) == 1 and len(held.limits("noticing")) == 1
    held.vault.verify()


@arch.holds("law.answer.pages", "law.budget.held")
def test_a_memory_cannot_reach_beyond_the_book_and_a_kept_page_cannot_ask(
    moments: Moments,
) -> None:
    strangers = "\n".join(
        f"=== page: {name} ===\n---\nwithin: book\n---\nmine now\n=== end ==="
        for name in ("desk", "noticing", "front-of-mind")
    )
    before = {n: moments.vault.read(n) for n in ("desk", "noticing", "front-of-mind")}
    moments.moment(memory=strangers)
    for name in before:
        assert moments.limits(name), name
        assert moments.vault.read(name).within == before[name].within
        assert "mine now" not in moments.vault.read(name).body
    chatty = (
        "=== page: chatter ===\n---\nwithin: book\nwatch:\n  - on: desk\n    when: 'true'\n"
        "    ask: {provider: small, into: said, prompt: hello}\n---\nsomething\n=== end ==="
    )
    moments.moment(memory=chatty)
    assert moments.vault.read("chatter").within == "book"
    calls = moments.moment()
    assert not of(calls, "hello")
    assert moments.limits("chatter")
    own = "=== page: intruder ===\n---\nwithin: book\n---\nhere\n=== end ==="
    moments.moment(noticing=own)
    assert moments.vault.read("noticing").fields["noticed"] == own
    assert not (moments.vault.pages_dir / "intruder.md").exists()
    moments.vault.verify()


def test_the_clerk_is_the_same_and_asked_as_often_without_the_two_pages(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    with_them = Moments(tmp_path / "a", monkeypatch)
    first = with_them.moment()
    bare = Moments(tmp_path / "b", monkeypatch, without=("memory", "noticing"))
    only = bare.moment()
    assert clerk_of(first) == clerk_of(only)
    for _ in range(4):
        assert len(clerks(bare.moment())) == 1
    assert len(clerks(bare.calls())) == 5 and len(bare.calls()) == 5
    bare.vault.verify()


@arch.holds("flow.ask.model", "flow.ask.pages")
def test_the_card_drawn_once_with_a_stand_in_passes_every_expect_in_fifteen_calls(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    program = tmp_path / "bin" / "claude"
    program.parent.mkdir()
    program.write_text(
        f"#!{sys.executable}\nimport sys\nprompt = sys.stdin.read()\n"
        f"parcel = {PARCEL!r}\n"
        "if 'can keep pages in book' in prompt:\n"
        "    said = prompt.split('The desk said:')[1][:60]\n"
        "    print(parcel if 'on shelf 12.' in said else 'Nothing more.')\n"
        "elif 'different from before' in prompt:\n"
        "    now = prompt.split('In front of it now:')[1]\n"
        f"    print({CHANGED!r} if 'bicycle' in now else 'nothing')\n"
        "else:\n"
        "    print(prompt)\n",
        encoding="utf-8",
    )
    program.chmod(program.stat().st_mode | stat.S_IXUSR)
    monkeypatch.setenv("PATH", f"{program.parent}{os.pathsep}{os.environ['PATH']}")
    monkeypatch.setenv("CONKY_PROVIDER", "claude")
    monkeypatch.setenv("CONKY_COMMAND_CLAUDE", str(program))
    out = tmp_path / "out"
    assert cards.main([str(CARD), "--draws", "1", "--out", str(out)]) == 0
    (row,) = [json.loads(line) for line in (out / "rows.jsonl").read_text().splitlines()]
    assert not any(e["failed"] for e in row["expects"]) and "error" not in row
    assert len(row["expects"]) == 3 and row["calls"] == 15
