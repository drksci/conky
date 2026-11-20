"""Cards: a playbook with live steps, drawn several times. A stand-in program is the model."""

import json
import os
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
    assert first["card"] == "a-keeper-binds-itself" and "claim" in first and "forecast" in first
    assert first["par"].keys() == {"outcome", "structure", "cost"}
    assert "claim" not in second and "par" not in second
    assert first["expects"] == [{"step": 3, "failed": []}, {"step": 5, "failed": []}]
    assert (first["draw"], first["calls"], first["model"]) == (1, 1, "claude")
    assert first["sent"] > 0 and first["received"] == len(GOOD.rstrip())
    assert Path(first["vault"]).is_dir() and Path(first["vault"]).parent.name == "draw-1"
    Vault(first["vault"], Path(first["vault"]).parent / "keys").verify()
    said = capsys.readouterr().out
    assert said.index("forecast:") < said.index("par outcome:") < said.index("draw 1:")
    assert said.splitlines()[-1] == "passed 2 of 2"


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
    assert said[0].startswith("claim: ") and any(x.startswith("par outcome: ") for x in said)
    assert "passed 2 of 2" in said
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
