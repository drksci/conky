"""What the runtime itself says to a model: one page, read by name."""

from __future__ import annotations

from functools import cache
from importlib import resources


@cache
def _lines() -> dict[str, str]:
    """Return each section of voice.md by name, with its worked-example fences dropped."""
    text = (resources.files("conky") / "voice.md").read_text(encoding="utf-8")
    found: dict[str, list[str]] = {}
    name = None
    fenced = False
    for line in text.split("\n---\n", 1)[-1].splitlines():
        if line.startswith("```"):
            fenced = not fenced
        elif not fenced and line.startswith("## "):
            name = line[3:].strip()
            found[name] = []
        elif name is not None:
            found[name].append(line)
    return {key: "\n".join(lines).strip("\n") for key, lines in found.items()}


def names() -> set[str]:
    """Return the names of the lines the page holds."""
    return set(_lines())


def line(key: str, **values: object) -> str:
    """Return the line called key, with each word in braces filled from values."""
    return _lines()[key].format(**values)


def told(key: str, **values: object) -> str:
    """Return the line called key as a stage direction: how the runtime narrates to a model."""
    return f"*{line(key, **values)}*"
