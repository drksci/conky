"""The markers describe the code and write the evidence of a judged check."""

import subprocess

import pytest

from conky import arch


def test_a_marker_returns_what_it_marks_and_registers_a_fact():
    @arch.law("a-test-law", "A statement.", doc="vault-format.md")
    def marked() -> int:
        return 3

    assert marked() == 3
    assert any(e.facts.get("name") == "a-test-law" for e in arch.ENTRIES)
    arch.ENTRIES[:] = [e for e in arch.ENTRIES if e.facts.get("name") != "a-test-law"]


def test_a_bundle_holds_the_question_and_never_invents_a_verdict(tmp_path):
    vault = tmp_path / "vault"
    (vault / "pages").mkdir(parents=True)
    subprocess.run(["git", "init", "-q", str(vault)], check=True)
    (vault / "pages" / "ma.md").write_text("---\n---\nHello.\n", encoding="utf-8")
    made = arch.bundle("character-organised-itself", vault, tmp_path / "out")
    text = made.read_text(encoding="utf-8")
    assert "Question:" in text and "Scale:" in text and "## Page ma" in text
    assert "not given" in text


def test_a_verdict_is_recorded_with_who_gave_it(tmp_path):
    made = arch.bundle(
        "page-format-with-a-real-model", tmp_path, tmp_path / "out", verdict="3 usable", by="maya"
    )
    assert "3 usable (given by maya)" in made.read_text(encoding="utf-8")
    with pytest.raises(ValueError, match="together"):
        arch.bundle("page-format-with-a-real-model", tmp_path, tmp_path / "o", verdict="3")
    with pytest.raises(KeyError, match="no judged check"):
        arch.bundle("nothing", tmp_path, tmp_path / "o")
