"""Show a vault's present state as a folder another program can open. Derived data, never truth.

    obsidian(vault, out)   one note a page in a folder tree of spaces, and one JSON Canvas file
    affine()               says what is known of AFFiNE's file import, and writes nothing

The output is a pure function of the pages committed at HEAD: the same vault gives the same bytes.
Each call deletes and rewrites its own folder. Nothing reads the output back.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from conky import arch, git
from conky.errors import BadInput
from conky.page import Page, parse, serialize
from conky.vault import Vault

DIST = "dist"
CANVAS = "conky.canvas"
NODE = (300, 120)
GAP = 40
COLUMNS = 3
KINDS = ("within", "watch", "ask", "writes")
AFFINE_SAID = (
    "no AFFiNE file import that fits could be confirmed, so nothing was written. Its documentation "
    "was fetched on 2026-11-20: the docs index at https://docs.affine.pro/ and the blog index at "
    "https://affine.pro/blog name no Markdown or folder import, and the one import post found "
    "(https://affine.pro/blog/import-your-data-from-notion-into-affine) covers a zip of Notion "
    "HTML. Instead run `conky export obsidian`, which writes plain Markdown, and look in AFFiNE's "
    "own import dialog for a Markdown option."
)


def committed(vault: Vault) -> dict[str, Page]:
    """Return the pages committed at HEAD by name, read without the working tree."""
    if not vault._has_commits():
        return {}
    listing = git.run(["ls-tree", "-r", "--name-only", "HEAD", "pages/"], vault.path)
    found = {}
    for line in sorted(listing.splitlines()):
        if line.endswith(".md"):
            found[Path(line).stem] = parse(git.run(["show", f"HEAD:{line}"], vault.path))
    return found


def _chain(name: str, pages: dict[str, Page]) -> list[str]:
    """Return the spaces a page sits in, outermost first. A loop of spaces stops at the repeat."""
    chain: list[str] = []
    space = pages[name].within
    while space in pages and space not in chain and space != name:
        chain.append(space)
        space = pages[space].within
    return chain[::-1]


def _spaces(pages: dict[str, Page]) -> set[str]:
    return {p.within for p in pages.values() if p.within in pages}


def _path(name: str, pages: dict[str, Page], spaces: set[str]) -> str:
    """Return where a page's note goes: a space's own note sits at the top of its folder."""
    folders = _chain(name, pages)
    if name in spaces:
        folders.append(name)
    return "/".join([*folders, f"{name}.md"])


def _note(name: str, pages: dict[str, Page]) -> str:
    """A note is the page exactly as its author wrote it: nothing is added to its body."""
    return serialize(pages[name])


def _relations(pages: dict[str, Page]) -> list[tuple[str, str, str]]:
    """Return (kind, from, to) for within, watch, ask and writes, among pages that exist."""
    found = []
    for name in sorted(pages):
        page = pages[name]
        if page.within:
            found.append(("within", name, page.within))
        for entry in page.watch:
            found.append(("watch", name, entry["on"]))
            ask = entry.get("ask")
            if isinstance(ask, dict):
                if ask.get("provider"):
                    found.append(("ask", name, ask["provider"]))
                if ask.get("writes"):
                    found.append(("writes", name, ask["writes"]))
    return [r for r in found if r[1] in pages and r[2] in pages and r[1] != r[2]]


def _block(items: list[dict]) -> tuple[int, int]:
    """Place items in rows of COLUMNS from the origin; return the width and height they fill."""
    x = y = row = width = 0
    for index, item in enumerate(items):
        if index and index % COLUMNS == 0:
            x, y, row = 0, y + row + GAP, 0
        _shift(item, x - item["x"], y - item["y"])
        x += item["width"] + GAP
        row = max(row, item["height"])
        width = max(width, x - GAP)
    return width, y + row


def _shift(item: dict, dx: int, dy: int) -> None:
    item["x"] += dx
    item["y"] += dy
    for inner in item.get("inside", []):
        _shift(inner, dx, dy)


def _flat(item: dict) -> list[dict]:
    out = [item]
    for inner in item.pop("inside", []):
        out.extend(_flat(inner))
    return out


def _layout(space: str | None, pages: dict[str, Page], spaces: set[str], seen: set[str]) -> dict:
    """Return a group for the space, holding its note, its pages and its inner spaces."""
    seen.add(space or "")
    own = [] if space is None else [space]
    members = [n for n in sorted(pages) if pages[n].within == space and n != space]
    items: list[dict] = []
    for name in own + [n for n in members if n not in spaces]:
        items.append(
            {
                "id": f"page-{name}",
                "type": "file",
                "file": _path(name, pages, spaces),
                "x": 0,
                "y": 0,
                "width": NODE[0],
                "height": NODE[1],
            }
        )
    for name in (n for n in members if n in spaces and n not in seen):
        items.append(_layout(name, pages, spaces, seen))
    width, height = _block(items)
    pad = GAP if space is not None else 0
    for item in items:
        _shift(item, pad, pad)
    group = {
        "id": f"space-{space}" if space else "root",
        "type": "group",
        "x": 0,
        "y": 0,
        "width": width + 2 * pad,
        "height": height + 2 * pad,
        "inside": items,
    }
    if space:
        group["label"] = space
    return group


def _canvas(pages: dict[str, Page], spaces: set[str]) -> str:
    """Return the JSON Canvas 1.0 text: groups for spaces, file nodes, edges for relations."""
    seen: set[str] = set()
    top = _layout(None, pages, spaces, seen)
    nodes = [n for item in top["inside"] for n in _flat(item)]
    shown = {n["id"] for n in nodes}
    missing = [n for n in sorted(pages) if f"page-{n}" not in shown]
    if missing:
        base = max((n["y"] + n["height"] for n in nodes), default=-GAP) + GAP
        extra = [
            {
                "id": f"page-{n}",
                "type": "file",
                "file": _path(n, pages, spaces),
                "x": 0,
                "y": 0,
                "width": NODE[0],
                "height": NODE[1],
            }
            for n in missing
        ]
        _block(extra)
        for item in extra:
            item["y"] += base
        nodes += extra
    edges = []
    for number, (kind, source, target) in enumerate(_relations(pages)):
        edges.append(
            {
                "id": f"edge-{number}-{kind}",
                "fromNode": f"page-{source}",
                "toNode": f"page-{target}",
                "label": kind,
            }
        )
    return json.dumps({"nodes": nodes, "edges": edges}, indent=2, ensure_ascii=False) + "\n"


def _exclude(vault: Vault, out: Path) -> None:
    """Keep the output out of the vault's tree without a tracked ignore file."""
    here = vault.path.resolve()
    try:
        rel = out.resolve().relative_to(here)
    except ValueError:
        return
    pattern = f"{DIST}/" if rel.parts[:1] == (DIST,) else f"{rel.as_posix()}/"
    exclude = here / ".git" / "info" / "exclude"
    exclude.parent.mkdir(parents=True, exist_ok=True)
    lines = exclude.read_text(encoding="utf-8").splitlines() if exclude.exists() else []
    if pattern not in lines:
        exclude.write_text("\n".join([*lines, pattern]) + "\n", encoding="utf-8")


def _clear(vault: Vault, out: Path) -> None:
    """Delete a folder an earlier export wrote, and refuse any other folder."""
    here = vault.path.resolve()
    target = out.resolve()
    if target == here or target in here.parents or (here / ".git") in (target, *target.parents):
        raise BadInput(f"{out} is the vault or holds it: give --out a folder of its own")
    if target.exists():
        if not target.is_dir() or (any(target.iterdir()) and not (target / CANVAS).exists()):
            raise BadInput(
                f"{out} exists and was not made by conky export: give --out a new folder"
            )
        shutil.rmtree(target)


@arch.part(
    "part.export.obsidian",
    "layer.edge",
    "The committed pages as an Obsidian folder of notes and a JSON Canvas, rebuilt each time.",
    doc="connectors.md#showing-a-vault-elsewhere",
)
def obsidian(vault: Vault, out: Path | None = None) -> tuple[Path, int]:
    """Write the vault's pages as notes under out and return the folder and the page count."""
    target = out if out is not None else vault.path / DIST / "obsidian"
    pages = committed(vault)
    _clear(vault, target)
    _exclude(vault, target)
    spaces = _spaces(pages)
    for name in pages:
        note = target / _path(name, pages, spaces)
        note.parent.mkdir(parents=True, exist_ok=True)
        note.write_text(_note(name, pages), encoding="utf-8", newline="\n")
    target.mkdir(parents=True, exist_ok=True)
    (target / CANVAS).write_text(_canvas(pages, spaces), encoding="utf-8", newline="\n")
    return target, len(pages)


@arch.part(
    "part.export.affine",
    "layer.edge",
    "Says that no AFFiNE file import that fits was found, and writes nothing.",
    doc="connectors.md#showing-a-vault-elsewhere",
)
def affine() -> None:
    """Refuse with what was found about AFFiNE's import and what to do instead."""
    raise BadInput(AFFINE_SAID)
