"""The shape of a harness at the start and at the end of a run: its parts and how they connect.

    shape(folder)   one dict: harness, seed, kind, start, end, facts

`start` and `end` are each `{nodes: [{id, kind, size}], edges: [{from, to, kind}]}`. `facts` is a
short ordered list of `{name, value}` in plain words. What a harness's shape is comes from its
`adapter.json` (`shape`): `vault` (with `path`, the vault's folder inside the run), `conversation`
or `policy`. Nothing here names a harness or a scenario. Standard library and the page parser.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

from bench import record
from conky.page import parse
from conky.page import spaces as page_spaces


def _git(vault: Path, *args: str) -> str:
    done = subprocess.run(
        ["git", "-C", str(vault), *args], capture_output=True, text=True, check=True
    )
    return done.stdout


def _pages(vault: Path, rev: str) -> dict:
    """The pages committed at `rev`, by name, read without touching the working tree."""
    names = _git(vault, "ls-tree", "-r", "--name-only", rev, "pages/").split()
    return {
        Path(n).stem: parse(_git(vault, "show", f"{rev}:{n}")) for n in names if n.endswith(".md")
    }


def _asks(page) -> list[dict]:
    return [w["ask"] for w in page.watch if isinstance(w.get("ask"), dict)]


def _graph(pages: dict) -> dict:
    spaces = {s for p in pages.values() for s in page_spaces(p.within)}
    nodes, edges = [], []
    for name, page in sorted(pages.items()):
        kind = "page"
        if name in spaces:
            kind = "space"
        if "api" in page.fields:
            kind = "provider"
        if _asks(page):
            kind = "character"
        nodes.append({"id": name, "kind": kind, "size": len(page.body)})
        for space in page_spaces(page.within):
            edges.append({"from": name, "to": space, "kind": "within"})
        for entry in page.watch:
            edges.append({"from": name, "to": entry["on"], "kind": "watch"})
        for ask in _asks(page):
            if ask.get("provider"):
                edges.append({"from": name, "to": ask["provider"], "kind": "ask"})
            if ask.get("writes"):
                edges.append({"from": name, "to": ask["writes"], "kind": "writes"})
    ids = {n["id"] for n in nodes}
    return {"nodes": nodes, "edges": [e for e in edges if e["to"] in ids]}


def _vault(folder: Path, path: str) -> tuple[dict, dict, list[dict]]:
    vault = folder / path
    end = _pages(vault, "HEAD")
    first = _git(vault, "log", "--reverse", "--format=%H", "-G", "ask:", "--", "pages").split()
    start = _pages(vault, first[0]) if first else end
    messages = _git(vault, "log", "--format=%B%x00").split("\x00")
    refused = sum(1 for m in messages if "Kind: refused" in m)
    commits = len(_git(vault, "rev-list", "HEAD").split())
    facts = [
        {"name": "pages at start", "value": len(start)},
        {"name": "pages at end", "value": len(end)},
        {"name": "pages it wrote", "value": len(set(end) - set(start))},
        {"name": "signed changes", "value": commits - refused},
        {"name": "refused", "value": refused},
    ]
    return _graph(start), _graph(end), facts


def _conversation(folder: Path) -> tuple[dict, dict, list[dict]]:
    answered = [c for c in record._jsonl(folder / "meter.jsonl") if c.get("status") == 200]
    last = answered[-1].get("chars_in", 0) if answered else 0

    def graph(size: int) -> dict:
        return {
            "nodes": [
                {"id": "model", "kind": "model", "size": 0},
                {"id": "conversation", "kind": "conversation", "size": size},
            ],
            "edges": [{"from": "model", "to": "conversation", "kind": "reads"}],
        }

    facts = [
        {"name": "messages", "value": len(answered)},
        {"name": "characters in the last call", "value": last},
        {"name": "kept after it stops", "value": 0},
    ]
    return graph(0), graph(last), facts


def _policy() -> tuple[dict, dict, list[dict]]:
    only = {"nodes": [{"id": "policy", "kind": "policy", "size": 0}], "edges": []}
    return only, only, []


def shape(folder: Path) -> dict:
    """What the harness was at the start and what it had become at the end of this run."""
    meta = record._meta(folder)
    harness = meta["arm"]
    declared = record.manifest(harness).get("shape") or {}
    kind = declared.get("kind", "policy")
    if kind == "vault":
        start, end, facts = _vault(folder, declared["path"])
    elif kind == "conversation":
        start, end, facts = _conversation(folder)
    else:
        start, end, facts = _policy()
    return {
        "harness": harness,
        "seed": meta["seed"],
        "kind": kind,
        "start": start,
        "end": end,
        "facts": facts,
    }
