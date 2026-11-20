"""An answer that is pages: what a model is told, and how its reply is cut into pages."""

from __future__ import annotations

from dataclasses import dataclass

from conky import arch
from conky.page import NAME

HEADER = "=== page:"
END = "=== end ==="


@arch.step(
    "flow.ask.pages",
    2,
    "lane.runtime",
    "lane.provider",
    "the fixed page instruction, then the prompt",
)
def instruction(page: str, space: str, shown: bool) -> str:
    """Return the fixed text placed ahead of a prompt that lets page write pages into space.

    It comes first so that the author's own question is the last thing the model reads.

    shown says the prompt embeds what space holds, which the text then tells the page.
    """
    seen = (
        f"Each time you are asked, you are shown what {space} holds, so you will see what "
        "you kept. "
        if shown
        else ""
    )
    return (
        f"You are a page called {page}, and {space} is a space you can write into. "
        f"Your reply is whatever you write outside a page. You may write pages into {space}, "
        f"and they are kept. Write one like this:\n\n{HEADER} <name> ===\n---\n"
        f"within: {space}\n---\nwhat you want to keep\n{END}\n\n"
        "A page can be a note to yourself, or it can carry a rule that must stay true from now "
        "on: a line under `rules:`, a CEL condition on `page.FIELD`. "
        f"{seen}You cannot write anywhere else. Writing nothing more is fine.\n\n"
    )


@dataclass(frozen=True)
class Block:
    """One page block of a reply: its name, its text and what was wrong with its header."""

    name: str
    text: str
    problem: str | None = None


def _header(line: str) -> tuple[str, str | None]:
    """Return the name a header line gives and the problem with it, if any."""
    rest = line[len(HEADER) :]
    name = rest[1:-4] if rest.startswith(" ") and rest.endswith(" ===") else ""
    if NAME.match(name):
        return name, None
    shown = name or line
    return name, (
        f"the header {shown!r} does not name a page: write {HEADER} <name> === "
        "with a name of lowercase letters, digits, '-' and '_'"
    )


@arch.part(
    "part.answer.format",
    "layer.character",
    "The reply cut into plain text and page blocks.",
    doc="rules-and-reactions.md#an-answer-that-is-pages",
    roadmap="R29",
)
@arch.step(
    "flow.ask.pages", 3, "lane.runtime", None, "the reply is cut into plain text and page blocks"
)
@arch.judged(
    "check.page.format",
    "State whether a real model asked for pages follows the page format "
    "and writes pages a person would keep.",
    "The prompt as sent, the reply, the pages that landed and the refusals "
    "recorded, in the vault history.",
    "1 unusable, 2 needs repair, 3 usable, 4 good",
    checks=["flow.ask.pages"],
)
def split(reply: str) -> tuple[str, list[Block]]:
    """Return the plain text of a reply and its page blocks, in the order given."""
    plain: list[str] = []
    found: list[tuple[str, str | None, list[str]]] = []
    inside = False
    for line in reply.splitlines():
        stripped = line.rstrip()
        if stripped.startswith(HEADER):
            name, problem = _header(stripped)
            found.append((name, problem, []))
            inside = True
        elif stripped == END:
            inside = False
        elif inside:
            found[-1][2].append(line)
        else:
            plain.append(line)
    blocks = [Block(n, "\n".join(lines).strip("\n") + "\n", p) for n, p, lines in found]
    return "\n".join(plain).strip(), blocks
