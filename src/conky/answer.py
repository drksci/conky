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
    "the prompt plus the fixed page instruction",
)
def instruction(space: str) -> str:
    """Return the fixed text appended to a prompt that may write pages into space."""
    return (
        f"\n\nYou may write pages into the space {space}. Start each page with a line "
        f"{HEADER} <name> ===, then the page as Markdown with frontmatter between two --- "
        f"lines, with within: {space} (or a space inside it) in the frontmatter. "
        f"A line {END} closes a page. Text before the first page, or after a closed page, "
        "is your plain answer."
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
