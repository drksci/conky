"""A vault's history as plain events, oldest first.

    from bench.timeline import timeline
    events = timeline(Path("vault"))

Pure reading: the commits of `main` are walked once and each is described by its trailers and by
what it changed in the page it wrote. Nothing is evaluated, no model is called, and the result is
plain data that `json.dumps` accepts. `bench/dynamics.py` draws it.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from conky import git as vault_git
from conky.page import RELATIONS, Page, links, parse

SCALARS = (str, int, float, bool)
LONGEST = 60
PROVIDER = {"api", "url", "model", "secret", "command"}


def _page_at(vault: Path, commit: str, name: str) -> Page:
    return parse(vault_git.run(["show", f"{commit}:pages/{name}.md"], vault))


def _scalar(value: object) -> object:
    return value[:LONGEST] if isinstance(value, str) else value


def classify(name: str, page: Page) -> str:
    """What the page is, from the page itself, by the kinds the code names (`kind.*` in the
    architecture index): `character` when a watch entry asks a model, `measure` when it only sets
    on itself, `reflex` when it only sets on something else, `provider` when it names an `api`,
    `url`, `model`, `secret` or `command`, `screen` and `hands` by their fields, and `page`
    otherwise. A space is a page others are within, so a picture adds that from the members."""
    if any("ask" in entry for entry in page.watch):
        return "character"
    if page.watch:
        return "measure" if any(entry.get("on") == name for entry in page.watch) else "reflex"
    if PROVIDER & set(page.fields):
        return "provider"
    if {"turn", "ended"} <= set(page.fields):
        return "screen"
    if "keys" in page.fields or "enter" in page.fields:
        return "hands"
    return "page"


def _rules(old: Page, new: Page) -> list[dict]:
    """The rules the write added, each saying whether it covers the pages within."""
    out = []
    for rule in new.rules:
        if rule in old.rules:
            continue
        each = isinstance(rule, dict) and "each" in rule
        out.append({"each": each, "text": str(rule["each"] if each else rule)})
    return out


def _watch(old: Page, new: Page) -> list[dict]:
    """The watch entries the write added: what they hear, what they set, whether they ask."""
    return [
        {
            "on": str(entry.get("on")),
            "hears": None if entry.get("on") in RELATIONS else str(entry.get("on")),
            "sets": sorted(entry.get("set") or {}),
            "asks": "ask" in entry,
            "provider": (entry.get("ask") or {}).get("provider"),
            "writes": (entry.get("ask") or {}).get("writes"),
        }
        for entry in new.watch
        if entry not in old.watch
    ]


def _fields(old: Page, new: Page) -> dict[str, list]:
    """The plain fields the write changed, by name, as [before, after]."""
    return {
        name: [_scalar(old.fields.get(name)), _scalar(value)]
        for name, value in new.fields.items()
        if isinstance(value, SCALARS) and old.fields.get(name) != value
    }


SHOWN = re.compile(r"^(?:[A-Za-z ]+: )?([a-z0-9][a-z0-9_-]*): ", re.MULTILINE)


def _shown(message: str, known: set[str]) -> list[str]:
    """The pages whose lines are in the prompt recorded with an answer, in the order they were
    shown. Read from the prompt as sent; nothing is worked out again."""
    prompt = message.split("\n\n\n", 1)[0]
    return [name for name in SHOWN.findall(prompt) if name in known]


def snapshot(name: str, page: Page) -> dict:
    """The whole page after a write, compact: plain fields, rules, watch entries and `shows`."""
    shows = page.fields.get("shows")
    return {
        "fields": {
            k: _scalar(v)
            for k, v in page.fields.items()
            if isinstance(v, SCALARS) and not k.endswith("_asked")
        },
        "rules": _rules(Page(), page),
        "watch": _watch(Page(), page),
        "shows": shows if isinstance(shows, dict) else None,
    }


def timeline(vault: Path) -> list[dict]:
    """Return one event for every commit of the vault's history, oldest first.

    An event has `n` (from 1), `kind` (`write` or `refused`), `page`, `by` (the actor), `cause`
    (the `n` of the event that set it off, or None), `within` (the page's space), `role`, `rules`
    and `watch` it added, `fields` it changed, and for a refusal its `reason`, the space it came
    `from` and the `within` it tried. `answered` says a model's answer was written.
    """
    log = vault_git.run(["log", "--reverse", "--format=%x1e%H%x1f%ae%x1f%B", "main"], vault)
    seen: dict[str, int] = {}
    state: dict[str, Page] = {}
    events: list[dict] = []
    for record in log.split("\x1e")[1:]:
        commit, by, message = record.split("\x1f", 2)
        tags = vault_git.trailers(message)
        name = tags["Page"]
        event = {
            "n": len(events) + 1,
            "kind": tags["Kind"],
            "page": name,
            "by": by.removesuffix("@conky"),
            "cause": seen.get(tags.get("Cause", "")),
            "within": None,
            "role": "page",
            "links": [],
            "state": None,
            "rules": [],
            "watch": [],
            "fields": {},
            "answered": tags.get("Model", "none") != "none" and "Model" in tags,
            "shown": [],
        }
        if event["answered"]:
            event["shown"] = _shown(message, set(state))
        if tags["Kind"] == "refused":
            attempt = json.loads(tags.get("Attempt") or "{}")
            event |= {
                "within": attempt.get("within"),
                "reason": tags.get("Reason", ""),
                "from": tags.get("From"),
            }
        else:
            old = state.get(name, Page())
            new = state[name] = _page_at(vault, commit, name)
            event |= {
                "within": new.within,
                "role": classify(name, new),
                "links": sorted(links(new)),
                "state": snapshot(name, new),
                "rules": _rules(old, new),
                "watch": _watch(old, new),
                "fields": _fields(old, new),
            }
        seen[commit] = event["n"]
        events.append(event)
    return events


def when(vault: Path) -> str:
    """The day of the vault's last commit, as `YYYY-MM-DD`."""
    return vault_git.run(["log", "-1", "--format=%cs", "main"], vault).strip()
