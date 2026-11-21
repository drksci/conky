"""Cards: a playbook with live steps, drawn several times. A stand-in program is the model."""

import json
import os
import re
import stat
import sys
from pathlib import Path

import pytest
from bench import cards

from conky import Vault

from . import playbook
from .test_pages import Stand

CARD = Path(__file__).parent.parent / "bench" / "cards" / "a-keeper-binds-itself.yaml"
RULE = "page.amount <= space.cash - 20"
GOOD = (
    f'=== page: den ===\n---\nrules:\n  - each: "{RULE}"\n---\n'
    "=== page: baker ===\n---\nwithin: den\namount: 30\n---\n"
)


@pytest.fixture
def canned(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Make detection find a program that prints the text in answer.txt, so no model is reached."""
    answer = tmp_path / "canned.txt"
    program = tmp_path / "claude"
    program.write_text(f"#!{sys.executable}\nimport sys\nprint(open({str(answer)!r}).read())\n")
    program.chmod(program.stat().st_mode | stat.S_IEXEC)
    monkeypatch.setenv("PATH", f"{tmp_path}{os.pathsep}{os.environ['PATH']}")
    monkeypatch.setenv("CONKY_PROVIDER", "claude")
    monkeypatch.setenv("CONKY_COMMAND_CLAUDE", str(program))
    return answer


def rows(out: Path) -> list[dict]:
    return [json.loads(line) for line in (out / "rows.jsonl").read_text().splitlines()]


def test_a_card_whose_live_step_is_answered_passes_and_writes_its_row(
    canned: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    canned.write_text(GOOD)
    out = tmp_path / "out"
    assert cards.main([str(CARD), "--draws", "2", "--out", str(out)]) == 0
    first, second = rows(out)
    assert first["card"] == "a-keeper-binds-itself"
    assert {k for k in first if k in cards.STATEMENTS} == set(cards.STATEMENTS)
    assert first["par"].keys() == set(cards.PAR)
    assert first["success"] == {"draws": 5, "pass": 4}
    assert "hypothesis" not in second and "par" not in second
    assert first["expects"] == [{"step": 3, "failed": []}, {"step": 5, "failed": []}]
    assert (first["draw"], first["calls"], first["model"]) == (1, 1, "claude")
    assert first["sent"] > 0 and first["received"] == len(GOOD.rstrip())
    assert Path(first["vault"]).is_dir() and Path(first["vault"]).parent.name == "draw-1"
    Vault(first["vault"], Path(first["vault"]).parent / "keys").verify()
    said = capsys.readouterr().out
    assert said.index("forecast:") < said.index("par outcome:") < said.index("draw 1:")
    assert said.index("objective:") < said.index("hypothesis:") < said.index("success draws:")
    assert said.index("par craft:") < said.index("dial:") < said.index("if_not:")
    assert "passed 2 of 2" in said.splitlines()
    assert said.splitlines()[-1] == (
        "success not met: passed 2 of 2 (bar: at least 4 of 5); drew 2 of the 5 stated"
    )


def test_a_draw_where_no_each_rule_is_written_fails_its_expects_and_is_kept(
    canned: Path, tmp_path: Path
) -> None:
    canned.write_text("Paid 30.\n")
    out = tmp_path / "out"
    cards.main([str(CARD), "--draws", "1", "--out", str(out)])
    (row,) = rows(out)
    assert not cards.passed(row)
    failed = row["expects"][0]["failed"][0]
    assert "den and the pages within it carry at least 1 each rules that parse" in failed


def test_says_live_in_an_ordinary_playbook_is_refused_with_what_to_do(
    vault: Vault, tmp_path: Path
) -> None:
    with pytest.raises(playbook.Failed, match="run this file as a card"):
        playbook.run(CARD, vault, Stand(tmp_path / "stand"))


def test_the_cap_refuses_a_run_whose_draws_could_pass_it_and_says_the_sum(
    canned: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    canned.write_text(GOOD)
    out = tmp_path / "out"
    assert cards.main([str(CARD), "--draws", "3", "--out", str(out), "--cap", "5"]) == 1
    assert "3 x 2 = 6 calls" in capsys.readouterr().out
    assert not (out / "rows.jsonl").exists()
    assert cards.main([str(CARD), "--draws", "3", "--out", str(out), "--cap", "6"]) == 0


def test_the_shared_count_gives_out_no_more_calls_than_it_holds(tmp_path: Path) -> None:
    budget = tmp_path / "budget.txt"
    budget.write_text("2")
    assert [cards._spend(budget) for _ in range(3)] == [True, True, False]
    assert budget.read_text() == "0"


def test_parallel_draws_give_the_same_rows_and_observations_as_serial_ones(
    canned: Path, tmp_path: Path
) -> None:
    canned.write_text(GOOD)
    for jobs in (1, 3):
        out = tmp_path / f"jobs-{jobs}"
        assert cards.main([str(CARD), "--draws", "3", "--out", str(out), "--jobs", str(jobs)]) == 0

    def bare(out: Path) -> list[dict]:
        return [
            {k: v for k, v in row.items() if k not in ("seconds", "vault")} for row in rows(out)
        ]

    assert bare(tmp_path / "jobs-1") == bare(tmp_path / "jobs-3")
    assert [r["draw"] for r in rows(tmp_path / "jobs-3")] == [1, 2, 3]
    assert observations(tmp_path / "jobs-1") == observations(tmp_path / "jobs-3")


def observations(out: Path) -> list[dict]:
    return [json.loads(line) for line in (out / "observations.jsonl").read_text().splitlines()]


def test_observations_hold_the_new_pages_the_rules_and_the_refusal_reasons(
    canned: Path, tmp_path: Path
) -> None:
    canned.write_text(GOOD)
    out = tmp_path / "out"
    cards.main([str(CARD), "--draws", "1", "--out", str(out)])
    (seen,) = observations(out)
    assert seen["draw"] == 1 and seen["new_pages"] == ["baker"]
    assert seen["rules"] == {"den": [{"each": RULE}]}
    (refusal,) = seen["refusals"]
    assert refusal["page"] == "landlord-payment" and refusal["reason"].startswith("rule")
    assert seen["answers"] == [GOOD.strip()[:200]]


def test_read_prints_the_claim_the_pass_count_and_what_each_draw_did(
    canned: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    canned.write_text(GOOD)
    out = tmp_path / "out"
    cards.main([str(CARD), "--draws", "2", "--out", str(out)])
    capsys.readouterr()
    assert cards.main(["--read", str(out)]) == 0
    said = capsys.readouterr().out.splitlines()
    assert any(x.startswith("hypothesis: ") for x in said) and any(
        x.startswith("par outcome: ") for x in said
    )
    assert "passed 2 of 2" in said and any(x.startswith("success not met: ") for x in said)
    draw = next(x for x in said if x.startswith("draw 2:"))
    assert f"rule on den: {RULE}" in draw and "refused landlord-payment: rule" in draw


def test_a_rule_on_a_page_within_the_den_does_not_refuse_a_payment_written_directly_in_it(
    canned: Path, tmp_path: Path
) -> None:
    canned.write_text(
        f'=== page: payments ===\n---\nwithin: den\nrules:\n  - each: "{RULE}"\n---\n'
        "=== page: baker ===\n---\nwithin: payments\namount: 30\n---\n"
    )
    out = tmp_path / "out"
    cards.main([str(CARD), "--draws", "1", "--out", str(out)])
    (row,) = rows(out)
    assert row["expects"][0]["failed"] == [] and row["expects"][1]["failed"]


def test_a_card_missing_a_statement_is_refused_naming_what_is_missing_and_draws_nothing(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    text = CARD.read_text()
    bare = "\n".join(x for x in text.splitlines() if not x.startswith(("dial:", "  craft:")))
    card = tmp_path / "bare.yaml"
    card.write_text(bare.replace("success: {draws: 5, pass: 4}", "success: {draws: 5}"))
    out = tmp_path / "out"
    assert cards.main([str(card), "--draws", "1", "--out", str(out)]) == 1
    said = capsys.readouterr().out
    for line in ("dial: write", "par craft: write", "success pass: write"):
        assert line in said
    assert not out.exists()


def test_both_cards_state_the_seven_statements_and_their_bars_are_data() -> None:
    from conky.page import load_value

    for name, bar in (
        ("a-keeper-binds-itself", {"draws": 5, "pass": 4}),
        ("a-clerk-remembers", {"draws": 5, "pass": 3, "calls_at_most": 4}),
    ):
        plan = load_value((CARD.parent / f"{name}.yaml").read_text())
        assert cards.missing(plan) == [] and plan["success"] == bar


def row(wins: bool, calls: int, sent: int = 100) -> dict:
    return {"expects": [{"step": 1, "failed": [] if wins else ["x"]}], "calls": calls, "sent": sent}


def test_the_verdict_is_met_only_when_every_stated_bar_holds_and_gives_the_numbers() -> None:
    bar = {"draws": 3, "pass": 2, "calls_at_most": 4}
    met = cards.verdict(bar, [row(True, 4), row(True, 3), row(False, 4)])
    assert met == (
        "success met: passed 2 of 3 (bar: at least 2 of 3); median calls a draw 4 (bar: at most 4)"
    )
    assert cards.verdict(bar, [row(True, 5), row(True, 5), row(True, 4)]).startswith(
        "success not met"
    )
    assert cards.verdict(bar, [row(True, 1), row(False, 1), row(False, 1)]).startswith(
        "success not met"
    )
    assert cards.verdict({"draws": 1, "pass": 1, "sent_at_most": 50}, [row(True, 1)]).startswith(
        "success not met"
    )


JUDGED = """\
objective: a character says whether the room is strange, and a judge reads what it said
hypothesis: the clerk says the room is strange
success: {draws: 2, pass: 1}
forecast: the judge says yes in both
par: {outcome: o, structure: s, cost: c, craft: f}
dial: none
if_not: look at what the clerk was shown
judge: {provider: claude}
pages:
  helper: {api: command, command: stand}
  clock: {}
  clerk:
    said: ""
    watch:
      - on: clock
        when: "true"
        ask: {provider: helper, into: said, prompt: "Describe the room."}
steps:
  - says: live
  - write: {page: clock, fields: {}, body: "seven"}
  - expect:
      exists: [clerk]
      judged:
        - question: Does the clerk say something in the room is impossible?
          evidence: [clerk.said, answers]
          scale: [No, Partly, yes]
          pass: [partly, yes]
          note: only for the reader
"""


@pytest.fixture
def judged(tmp_path: Path, canned: Path) -> Path:
    """A card with one judged check and a stand-in program that answers the judge from judge.txt."""
    program = canned.parent / "claude"
    program.write_text(
        f"#!{sys.executable}\nimport sys\nprompt = sys.stdin.read()\n"
        f"open({str(tmp_path / 'seen.txt')!r}, 'a').write(prompt + '\\n=====\\n')\n"
        f"name = 'judge.txt' if 'Question:' in prompt else 'canned.txt'\n"
        f"print(open({str(tmp_path)!r} + '/' + name).read())\n"
    )
    canned.write_text("The clock shows seven and the oven is on the ceiling.")
    card = tmp_path / "judged.yaml"
    card.write_text(JUDGED)
    return card


def judge_says(card: Path, text: str) -> None:
    (card.parent / "judge.txt").write_text(text)


def test_a_judged_check_is_asked_once_and_its_record_says_who_gave_the_verdict(
    judged: Path, tmp_path: Path
) -> None:
    judge_says(judged, "Yes.\nThe oven cannot be on a ceiling.")
    out = tmp_path / "out"
    assert cards.main([str(judged), "--draws", "2", "--out", str(out)]) == 0
    first, second = rows(out)
    assert (first["calls"], first["judge_calls"]) == (1, 1) and cards.passed(first)
    (record,) = first["judged"]
    assert record["question"] == "Does the clerk say something in the room is impossible?"
    assert record["scale"] == ["no", "partly", "yes"] and record["pass"] == ["partly", "yes"]
    assert record["step"] == 3 and record["passed"] and record["verdict"] == "yes"
    assert record["reply"] == "Yes.\nThe oven cannot be on a ceiling."
    assert record["reason"] == "The oven cannot be on a ceiling."
    assert record["by"] == {"provider": "claude", "model": "claude"}
    assert re.fullmatch(r"\d{4}-\d\d-\d\d", record["date"])
    assert "[clerk.said]\nThe clock shows seven" in record["evidence"]
    assert "[answers]\nAnswer 1:\nThe clock shows seven" in record["evidence"]
    assert first["expects"] == [{"step": 3, "failed": []}] and second["judge_calls"] == 1
    prompts = (tmp_path / "seen.txt").read_text().split("\n=====\n")
    asked = [p for p in prompts if "Question:" in p]
    assert len(asked) == 2
    assert (
        asked[0].strip()
        == cards.judge_prompt(record["question"], record["evidence"], record["scale"]).strip()
    )
    for hidden in ("hypothesis", "forecast", "only for the reader", "passes"):
        assert hidden not in asked[0]
    assert "Scale, from least to most: no, partly, yes" in asked[0]


def test_a_failing_verdict_fails_the_draw_and_the_tally_is_kept_with_the_verdict(
    judged: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    judge_says(judged, "no\nIt only describes the clock.")
    out = tmp_path / "out"
    cards.main([str(judged), "--draws", "1", "--out", str(out)])
    (row,) = rows(out)
    assert not cards.passed(row) and row["expects"][0]["failed"] == []
    kept = (out / "verdict.txt").read_text().splitlines()
    assert kept[0].startswith("success not met") and len(kept) == 2
    assert kept[1].startswith("judged, Does the clerk say") and "no 1, partly 0, yes 0" in kept[1]
    assert "no verdict 0" in kept[1] and "by claude claude" in kept[1]
    cards.main(["--read", str(out)])
    said = capsys.readouterr().out
    assert kept[1] in said and "judged no (does not pass): It only describes" in said


def test_a_reply_off_the_scale_is_no_verdict_and_does_not_pass(
    judged: Path, tmp_path: Path
) -> None:
    judge_says(judged, "Maybe, it is hard to say.\nNot clear.")
    out = tmp_path / "out"
    cards.main([str(judged), "--draws", "1", "--out", str(out)])
    (row,) = rows(out)
    (record,) = row["judged"]
    assert record["verdict"] == "no verdict" and not record["passed"] and not cards.passed(row)
    assert record["reply"].startswith("Maybe")
    assert "no verdict 1" in (out / "verdict.txt").read_text()


def test_the_verdict_is_the_first_word_lower_cased_and_stripped_of_punctuation() -> None:
    scale = ["no", "partly", "yes"]
    assert cards.verdict_of('  "PARTLY": some of it', scale) == "partly"
    assert cards.verdict_of("Yes, because", scale) == "yes"
    assert cards.verdict_of("yesterday", scale) == "no verdict"
    assert cards.verdict_of("", scale) == "no verdict"


def test_a_spent_cap_makes_the_judge_no_verdict_and_no_call(judged: Path, tmp_path: Path) -> None:
    budget = tmp_path / "budget.txt"
    budget.write_text("0")
    check = {"question": "q?", "evidence": "answers", "scale": ["no", "yes"], "pass": ["yes"]}
    vault = Vault.init(tmp_path / "v", tmp_path / "k")
    (record,) = cards.judge_step([check], 3, vault, [], {}, budget)
    assert record["reply"] is None and record["verdict"] == "no verdict"
    assert "cap is spent" in record["reason"]
    assert record["evidence"] == "[answers]\n(no answers yet)"


@pytest.mark.parametrize(
    ("old", "new", "said"),
    [
        (
            "question: Does the clerk say something in the room is impossible?",
            "question: ''",
            "question: write the question",
        ),
        ("evidence: [clerk.said, answers]", "evidence: [the clerk]", "evidence: name"),
        ("scale: [No, Partly, yes]", "scale: [yes]", "scale: write at least two"),
        ("scale: [No, Partly, yes]", "scale: [no, no, yes]", "scale: write at least two"),
        ("pass: [partly, yes]", "pass: [maybe]", "pass: write the words of the scale"),
        ("pass: [partly, yes]", "pass: [yes]\n          pace: 1", "pace: not a key"),
        ("judge: {provider: claude}", "judge: {provider: gpt}", "judge provider: use one of"),
        (
            "judge: {provider: claude}",
            "judge: {provider: codex, model: x}",
            "judge model: a command",
        ),
    ],
)
def test_a_card_with_a_malformed_judged_check_is_refused_before_any_draw(
    judged: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str], old: str, new: str, said: str
) -> None:
    judged.write_text(JUDGED.replace(old, new))
    out = tmp_path / "out"
    assert cards.main([str(judged), "--draws", "1", "--out", str(out)]) == 1
    assert said in capsys.readouterr().out and not out.exists()


def test_judge_calls_are_in_the_cap_arithmetic_and_reported(
    judged: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    judge_says(judged, "yes\nFine.")
    out = tmp_path / "out"
    assert cards.main([str(judged), "--draws", "2", "--out", str(out), "--cap", "5"]) == 1
    assert "2 x 3 = 6 calls" in capsys.readouterr().out
    assert cards.main([str(judged), "--draws", "2", "--out", str(out), "--cap", "6"]) == 0
    said = capsys.readouterr().out
    assert "1 judge calls" in said and "1 of 1 judged checks passed" in said
    assert (out / "budget.txt").read_text() == "2"  # 2 draws x (1 ask + 1 judge) of 6 spent


def test_a_playbook_test_never_reaches_a_judge(judged: Path, vault: Vault, tmp_path: Path) -> None:
    with pytest.raises(playbook.Failed, match="run this file as a card"):
        playbook.run(judged, vault, Stand(tmp_path / "stand"))
