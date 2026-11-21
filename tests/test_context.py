"""A character is shown what its spaces say: the words of the spaces above it, nearest first."""

from conky import Vault, arch
from conky.page import CONTEXT_CAP, Page, resolve_text

from .conftest import AT
from .test_pages import Stand, history, stand, w  # noqa: F401

PROMPT = "Rules of the house:\n![[keeper#context]]\nNow: ![[ticket#text]]"


def said(vault: Vault, space: str, words: str) -> None:
    assert vault.write(space, {}, words, actor="alice", at=AT).ok


def test_a_space_is_shown_as_its_name_then_its_words() -> None:
    found = {
        "keeper": Page(["night", "hall"]),
        "night": Page(None, [], [], {}, "Decline large payments.\n"),
        "hall": Page(None, [], [], {}, ""),
    }
    assert resolve_text("![[keeper#context]]", found) == "night says:\nDecline large payments."
    assert resolve_text("![[night#context]]", found) == ""
    assert resolve_text("![[missing#context]]", found) == ""


def test_a_context_stops_at_the_cap_and_counts_the_rest() -> None:
    found = {"keeper": Page("s0")}
    for i in range(CONTEXT_CAP + 2):
        found[f"s{i}"] = Page(f"s{i + 1}", [], [], {}, f"word {i}")
    shown = resolve_text("![[keeper#context]]", found).split("\n\n")
    assert len(shown) == CONTEXT_CAP + 1 and shown[-1] == "(2 more spaces not shown)"
    assert shown[0] == "s0 says:\nword 0"


@arch.holds("law.embed.context")
def test_joining_a_space_changes_what_is_asked_and_leaving_takes_it_away(
    vault: Vault,
    stand: Stand,  # noqa: F811
) -> None:
    assert w(vault, "helper", {"api": "command", "command": "stand"}).ok
    said(vault, "night", "Decline any large payment.")
    assert w(vault, "ticket", {"text": "one"}).ok
    ask = {"provider": "helper", "prompt": PROMPT, "into": "said"}
    watch = [{"on": "ticket", "when": "true", "ask": ask}]
    assert w(vault, "keeper", {"watch": watch}).ok
    stand.says("Noted.")
    assert w(vault, "ticket", {"text": "two"}).ok
    assert "night says:" not in stand.prompts[-1]
    assert w(vault, "keeper", {"within": "night"}).ok
    assert w(vault, "ticket", {"text": "three"}).ok
    assert "night says:\nDecline any large payment.\nNow: three" in stand.prompts[-1]
    asked = len(stand.prompts)
    assert w(vault, "ticket", {"note": "unrelated"}).ok
    assert len(stand.prompts) == asked
    said(vault, "night", "Decline everything.")
    assert w(vault, "ticket", {"note": "again"}).ok
    assert len(stand.prompts) == asked + 1
    assert "Decline everything." in stand.prompts[-1]
    assert w(vault, "keeper", {"within": None}).ok
    assert w(vault, "ticket", {"text": "five"}).ok
    assert "night says:" not in stand.prompts[-1]
    assert "Rules of the house:\n\nNow: five" in stand.prompts[-1]
    log = [tags for _, tags in history(vault)]
    read = [t["Read"] for t in log if "Model" in t]
    assert read[1] == "night, ticket" and read[-1] == "ticket"
    vault.verify()
