"""A trial drawn as it happened: the vault's history as a plain graph with steps, for the view.

    python -m bench.dynamics RUN_DIR... [--date YYYY-MM-DD] [--commit SHA]
    python -m bench.dynamics --redraw

Each RUN_DIR is a run of `bench/cards.py` (`rows.jsonl`, `observations.jsonl`, `verdict.txt` and
`draw-N/vault`). For each one this writes, under `docs/results/cards/<card>/`, the rows with the
private vault paths taken out, the observations, the verdict, `timeline.json` (one timeline a
draw, read by `bench/timeline.py`), `run.json`, and `graph.json`: one draw described as nodes,
rows, edges and steps. `--redraw` writes `graph.json` again for every published card from its own
files. The view under `viewer/` draws a `graph.json` (React Flow, laid out by ELK); when Node and
the view's packages are there, it renders the pictures (`dynamics-light.webp` and `-dark`, the
steps, and `topology-light.png` and `-dark`, the final state). When they are not, the pictures
that are there are left alone and the command says so. Then it rewrites the board
`docs/research/trials.md` and the block between the two `dynamics` markers in `README.md`, both
from the published files alone.

The project describes and the view draws: nothing here places or styles anything, and the view
classifies and infers nothing. A node's archetype comes from `bench.timeline.classify`; its rows
are grouped in panels in a fixed order (text, holds, bound by, when and then), its sockets on a
board in the standard order, and every connection runs as hops between sockets of one kind of
signal, through a socket on the board of each space wall it crosses; a step names its
subject and the meaning of the pen it takes, one of the meanings in `src/conky/tokens.json`.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from datetime import UTC, datetime
from importlib import resources
from pathlib import Path

from bench.cards import OBSERVATIONS, ROWS, VERDICT, lines, passed, tally
from bench.expression import lines as expression_lines
from bench.timeline import timeline
from conky.page import Page, load_value, parse
from conky.rules import RuleError, reads

ROOT = Path(__file__).resolve().parent.parent
CARDS = ROOT / "bench" / "cards"
RESULTS = Path("docs") / "results" / "cards"
BOARD = Path("docs") / "research" / "trials.md"
VIEWER = ROOT / "viewer"
FEATURED = ("a-keeper-binds-itself", "a-keeper-hears-the-no", "a-clerk-reads-a-crowded-desk")
START, END = "<!-- dynamics:start -->", "<!-- dynamics:end -->"
TOKENS = json.loads(resources.files("conky").joinpath("tokens.json").read_text(encoding="utf-8"))
PENS = tuple(TOKENS["meaning"])  # what a pen may mean: added, refused, heard, kept, thought
CROWD = 12  # more pages than this in one space are drawn as small numbered notes
CHUNK = 6  # pages that arrive with nothing else happening are drawn this many to a step
HOLDS_SHOWN = 6  # a cell lists this many fields before "N more"
TEXT_LINES = 4  # a cell shows this many lines of a page's text
TEXT_LENGTH = 140  # and at most this many characters of them
VALUE_WIDTH = 100  # characters of a field's value a cell shows
NOTE_WIDTH = 34  # characters of a note's first line a note shown to a space shows
# Where a page's top-level fields are drawn, beside the rows of its holds panel: `avatar` and
# `known_as` in the header, `shows` in a space's footer. `BOOKKEEPING` fields, and fields ending
# `_asked` (digests the runtime keeps), are not part of what a page says and are not drawn.
HEADER_FIELDS = ("avatar", "known_as")
FOOTER_FIELDS = ("shows",)
BOOKKEEPING = ("secret",)
SOCKET = TOKENS["socket"]  # each kind of port: the pen meaning of its signal, word and prefix
BOARD_ORDER = tuple(SOCKET)  # the standard order of sockets on every board: the table's order
WORDS = TOKENS["words"] | {k: v["word"] for k, v in SOCKET.items()}
HEARD = {"refusal": "a write turned away", "within": "a page written within it",
         "link": "a link to it"}  # fmt: skip
PEN = {
    "write": "kept",
    "bulk": "kept",
    "rule": "added",
    "watch": "added",
    "reflex": "heard",
    "answer": "thought",
    "refused": "refused",
}  # the pen meaning of a step's subject
STEP_SYMBOL = {"room": "space", "write": "kept", "bulk": "kept", "rule": "rule", "watch": "hears"}
STEP_SYMBOL |= {"reflex": "reflex", "answer": "thought", "refused": "refusal"}
PICTURES = ("dynamics-light.webp", "dynamics-dark.webp", "topology-light.png", "topology-dark.png")


# ---------------------------------------------------------------- the story, from the events


def story(events: list[dict]) -> list[dict]:
    """Group a timeline into steps: the room as given, then one step an event.

    The room as given is everything before the write that set the first model answer off,
    followed back through the reflexes between them, so a trial begins at the moment something
    is asked. Many pages arriving with nothing else happening are drawn `CHUNK` to a step; the
    write that sets an answer off is always a step of its own. A step has `kind` (`room`,
    `answer`, `rule`, `watch`, `reflex`, `refused`, `bulk` or `write`), `words`, and the
    `events` it holds.
    """
    by_n = {e["n"]: e for e in events}
    eventful: set[int] = set()
    for e in events:
        cause = by_n.get(e["cause"]) if e["answered"] else None
        while cause:
            eventful.add(cause["n"])
            reflex = cause["cause"] and cause["by"] == cause["page"]
            cause = by_n.get(cause["cause"]) if reflex else None
    first = min(eventful, default=None) or next((e["n"] for e in events if e["cause"]), None)
    given = [e for e in events if first and e["n"] < first]
    steps = [{"kind": "room", "words": "The room as given.", "events": given}] if given else []
    seen = {e["page"] for e in given}
    rest = events[len(given) :]
    at = 0
    while at < len(rest):
        run = _crowd(rest, at, seen, eventful)
        if run:
            fresh = [e for e in run if e["page"] not in seen and e["within"]]
            space = fresh[0]["within"]
            many = f"{len(fresh)} more pages" if len(fresh) > 1 else f"{fresh[0]['page']}"
            words = f"{fresh[0]['by']} keeps {many} in {space}."
            steps.append({"kind": "bulk", "words": words, "events": run})
            seen |= {e["page"] for e in run}
            at += len(run)
            continue
        e = rest[at]
        seen.add(e["page"])
        steps.append({**_describe(e, events), "events": [e]})
        at += 1
    for i, step in enumerate(steps):
        step["i"] = i
    return steps


def _crowd(events: list[dict], at: int, seen: set[str], eventful: set[int]) -> list[dict]:
    """A run of pages put in a space with nothing else happening, with the reflexes they set
    off, at most `CHUNK` new pages long, or nothing when fewer than two arrive.

    Forty notes are a few things said, not forty steps."""
    run, fresh, known = [], 0, set(seen)
    for e in events[at:]:
        plain = e["kind"] == "write" and not (e["rules"] or e["watch"] or e["answered"])
        new = plain and e["page"] not in known and e["within"]
        reflex = plain and e["cause"] and e["by"] == e["page"]
        if not (new or reflex) or e["n"] in eventful or (new and fresh == CHUNK):
            break
        known.add(e["page"])
        fresh += bool(new)
        run.append(e)
    return run if fresh >= 2 else []


def _describe(e: dict, events: list[dict]) -> dict:
    page, by = e["page"], e["by"]
    if e["kind"] == "refused":
        rule = re.match(r"rule: (.*) \(from ([^)]*)\) is false", e.get("reason", ""))
        why = f": it breaks a rule {rule[2]} hands down" if rule else ""
        return {"kind": "refused", "words": f"{page} is turned away{why}."}
    if e["rules"]:
        many = "rules" if len(e["rules"]) > 1 else "a rule"
        each = all(r["each"] for r in e["rules"])
        whom = "for every page within it" if each else "for itself"
        return {"kind": "rule", "words": f"{by} gives {page} {many} {whom}."}
    if e["watch"]:
        heard = ", ".join(hears(w["on"], page) for w in e["watch"])
        return {"kind": "watch", "words": f"{by} makes {page} listen for {heard}."}
    if e["answered"] and e["shown"]:
        many = sum(1 for x in events[: e["n"]] if x["within"] == page and x["kind"] == "write")
        pages = len({x["page"] for x in events[: e["n"]] if x["within"] == page})
        many = pages or many
        return {
            "kind": "answer",
            "words": f"{page} is shown {len(e['shown'])} of its {many} "
            f"{'page' if many == 1 else 'pages'}, and answers.",
        }
    if e["answered"]:
        asked = events[e["cause"] - 1]["page"] if e["cause"] else ""
        return {"kind": "answer", "words": f"{page} reads {asked} and answers.".replace("  ", " ")}
    if e["cause"] and e["fields"] and by == page:
        name, (before, value) = next(iter(e["fields"].items()))
        if isinstance(value, int | float) and isinstance(before, int | float) and value > before:
            return {
                "kind": "reflex",
                "words": f"{page} counts it by itself: {name} is now {value:g}.",
            }
        if isinstance(value, int | float):
            return {"kind": "reflex", "words": f"{page} sets {name} by itself to {value:g}."}
        return {"kind": "reflex", "words": f"{page} sets {name} by itself: {plain(value, 40)}"}
    if e["within"]:
        return {"kind": "write", "words": f"{by} keeps {page} in {e['within']}."}
    return {"kind": "write", "words": f"{by} writes {page}."}


# ------------------------------------------------------------------------ the graph


def middle(text: str, width: int) -> str:
    """The text shortened in the middle when it is longer than width."""
    if len(text) <= width:
        return text
    keep = width - 3
    return text[: keep - keep // 2] + "..." + text[len(text) - keep // 2 :]


def plain(value: object, width: int = 24) -> str:
    """A value as a cell shows it: one line, no Markdown emphasis, shortened when it is long."""
    if isinstance(value, bool):
        text = str(value).lower()
    elif isinstance(value, float) and value.is_integer():
        text = str(int(value))
    elif isinstance(value, list):
        text = ", ".join(plain(v, width) for v in value)
    elif isinstance(value, dict):
        text = ", ".join(f"{k} {plain(v, width)}" for k, v in value.items())
    else:
        text = str(value)
    text = " ".join(text.replace("**", "").split())
    if " " in text and len(text) > width:  # a sentence keeps its start
        return text[: width - 3].rstrip() + "..."
    return middle(text, width)


def digits(name: str) -> str:
    found = re.findall(r"\d+", name)
    return str(int(found[-1])) if found else name[:2]


def expression(text: str) -> dict:
    """An expression as the view shows it: a small function of the names it reads, with the
    body as written and laid out in lines by `bench.expression`. Nothing is evaluated."""
    try:
        names = sorted(reads(text)[0])
    except RuleError:
        names = []
    return {"reads": names, "body": text, "lines": expression_lines(text)}


def hears(on: str, page: str) -> str:
    """What a watch entry listens for, in plain words."""
    if on == page:
        return "its own page changing"
    return HEARD.get(on, f"{on} changing")


def then(entry: dict) -> list[dict]:
    """What a watch entry does, a line a thing: each field it sets with the value's function,
    or the model it asks and where the answer goes."""
    if entry["asks"]:
        where = (
            f"writes pages into {entry['writes']}"
            if entry.get("writes")
            else f"puts the answer in {entry.get('into') or 'its page'}"
        )
        who = entry["provider"] or "the default provider"
        return [{"words": f"asks {who}, {where}", "expr": None}]
    sets = entry.get("set") or {k: "" for k in entry["sets"]}
    return [{"words": f"sets {k}", "expr": expression(v) if v else None} for k, v in sets.items()]


def full(state: dict) -> Page:
    """The page as committed, from the source the timeline keeps."""
    return parse(state["source"]) if state.get("source") else Page()


def kinds_of(node: dict, spaces: set[str], crowd: set[str]) -> list[str]:
    """The kind words of a cell's header, from the symbol table: what the page is."""
    out = ["note"] if node["id"] in crowd else []
    if node["id"] in spaces:
        out.append("space")
    if node["archetype"] in ("character", "provider"):
        out.append(node["archetype"])
    if node.get("known_as") and not out:
        out.append("term")
    return out or ["page"]


def graph(events: list[dict], card: str, draw: int) -> dict:
    """The graph of one draw: every page a cell (header, panels and footer, with its sockets),
    the edges between sockets, the regions a crowded space is drawn in, and the steps, each
    saying what appears, which values change, which elements are its subject and with which pen
    meaning, and what is dimmed. Plain data; the view draws it and adds nothing."""
    steps = story(events)
    by_n = {e["n"]: e for e in events}
    step_of = {e["n"]: s["i"] for s in steps for e in s["events"]}
    nodes: dict[str, dict] = {}
    rows: dict[str, dict] = {}  # every row of every panel, by id, with the step it appears
    values: dict[str, str] = {}  # every text that can change, by id, at its first value
    told: list[dict] = []

    def node_of(page: str, i: int) -> dict:
        if page not in nodes:
            nodes[page] = {"id": page, "rows": [], "appears": i, "archetype": "page",
                           "parent": None, "within": [], "known_as": [], "avatar": None,
                           "versions": [], "changed": [], "state": None, "answers": 0,
                           "refused": 0}  # fmt: skip
        return nodes[page]

    def add_row(node: dict, row: dict, i: int, say: dict) -> tuple[bool, bool]:
        """Add or update a row; say whether it is new and whether its value moved."""
        rid = row["id"]
        if rid not in rows:
            rows[rid] = {**row, "node": node["id"], "appears": i}
            node["rows"].append(rid)
            say["appear"].append(rid)
            if "value" in row:
                values[rid] = row["value"]
                rows[rid]["now"] = row["value"]
            return True, False
        rows[rid] |= {k: v for k, v in row.items() if k != "value"}
        if "value" in row and row["value"] != rows[rid]["now"]:
            say["change"][rid] = rows[rid]["now"] = row["value"]
            return False, True
        return False, False

    for step in steps:
        i, kind = step["i"], step["kind"]
        say: dict = {"i": i, "kind": kind, "words": step["words"], "appear": [], "change": {}}
        say |= {"subject": {}, "dim": []}
        pen = PEN.get(kind)
        for e in step["events"]:
            page = e["page"]
            new = page not in nodes
            node = node_of(page, i)
            if new:
                say["appear"].append(page)
            actor = nodes.get(e["by"]) if e["by"] != page else None
            if e["kind"] == "refused":
                node["refused"] += 1
                times = {1: "once", 2: "twice"}.get(node["refused"], f"{node['refused']} times")
                add_row(node, {"id": f"{page}/record/refused", "panel": "record",
                               "signal": "refused", "value": f"was turned away {times}",
                               "to": e["within"]}, i, say)  # fmt: skip
                say["change"][f"{page}/count/refused"] = str(node["refused"])
                say["subject"][page] = "refused"
                say["subject"][f"{page}/record/refused"] = "refused"
                node["changed"].append(i)
                continue
            state = e["state"] or {}
            whole = full(state)
            node |= {"archetype": e["role"], "parent": e["within"], "state": state}
            node |= {"within": state.get("within", []), "known_as": state.get("known_as", [])}
            node["avatar"] = (state.get("fields") or {}).get("avatar")
            node["versions"].append({"step": i, "source": state.get("source", "")})
            node["changed"].append(i)
            if e["answered"]:
                node["answers"] += 1
                say["change"][f"{page}/count/thought"] = str(node["answers"])
            fresh, moved = [], []
            for row in rows_of(page, state, whole):
                added, changed = add_row(node, row, i, say)
                (fresh if added else moved if changed else []).append(row)
            if actor is not None:  # what the record says the actor did beyond its own page
                if e["rules"]:
                    row = {"id": f"{actor['id']}/record/rule:{page}", "panel": "record",
                           "signal": "wrote", "value": f"added a rule to {page}",
                           "to": page}  # fmt: skip
                elif e["watch"]:
                    heard = ", ".join(hears(w["on"], page) for w in e["watch"])
                    row = {"id": f"{actor['id']}/record/watch:{page}", "panel": "record",
                           "signal": "wrote", "value": f"made {page} listen for {heard}",
                           "to": page}  # fmt: skip
                else:
                    row = {"id": f"{actor['id']}/record/wrote:{page}", "panel": "record",
                           "signal": "wrote", "value": f"wrote {page}", "to": page}  # fmt: skip
                add_row(actor, row, i, say)
                if kind in ("rule", "watch", "write") and pen:
                    say["subject"][row["id"]] = pen
            if kind == "room" or not pen:
                continue
            if kind in ("write", "bulk") and new:
                say["subject"][page] = pen
            elif kind in ("rule", "watch"):
                for r in fresh:
                    if r["panel"] == ("bound" if kind == "rule" else "when"):
                        say["subject"][r["id"]] = pen
            elif kind == "reflex":
                for r in moved:
                    say["subject"][r["id"]] = pen
                    for w in state["watch"]:
                        if r["name"] in w["sets"]:
                            say["subject"][when_id(page, w)] = pen
            elif kind == "answer":
                say["subject"][page] = pen
                say["subject"][f"{page}/slot/asks:{asked_of(state)}"] = pen
                for w in state["watch"]:
                    if w["asks"]:
                        say["subject"][when_id(page, w)] = pen
                for r in moved:
                    say["subject"][r["id"]] = pen
            elif kind == "write":
                for r in moved + fresh:
                    say["subject"][r["id"]] = pen
                if not moved + fresh:
                    say["subject"][page] = pen
        told.append(say)

    spaces = {s for n in nodes.values() for s in [n["parent"], *n["within"]] if s}
    for s in sorted(spaces - set(nodes)):  # a space no write named: it still holds its members
        made = min(n["appears"] for n in nodes.values() if s in (n["parent"], *n["within"]))
        node_of(s, made)
        told[made]["appear"].insert(0, s)
    crowd = set()
    for s in spaces:
        members = [n for n in nodes.values() if n["parent"] == s and n["archetype"] == "page"]
        if len([n for n in members if n["id"] not in spaces]) > CROWD:
            crowd |= {n["id"] for n in members if n["id"] not in spaces}

    # Rules handed down: every `each` rule of a space a page is within is listed in its cell.
    for node in list(nodes.values()):
        for s in node["within"]:
            for rid in [r for r in nodes.get(s, {}).get("rows", []) if rows[r]["panel"] == "bound"]:
                rule = rows[rid]
                if not rule.get("each") or rule.get("from") or node["id"] in crowd:
                    continue
                hid = f"{node['id']}/bound/from:{s}:{rule['expr']['body']}"
                at = max(rule["appears"], node["appears"])
                rows[hid] = {**rule, "id": hid, "node": node["id"], "from": s, "appears": at}
                node["rows"].append(hid)
                told[at]["appear"].append(hid)

    # The footer: the slots a cell's kind can have, filled or hollow, and the space's counts.
    for node in nodes.values():
        state = node["state"] or {"watch": [], "rules": [], "shows": None}
        name = node["id"]
        asks = [w for w in state["watch"] if w["asks"]]
        for w in asks:
            who = w["provider"] or ""
            rows.setdefault(f"{name}/slot/asks:{who}", {
                "id": f"{name}/slot/asks:{who}", "panel": "slot", "slot": "asks", "node": name,
                "value": who or "default provider", "filled": bool(who), "to": who or None,
                "appears": node["appears"]})  # fmt: skip
            where = w.get("writes") or ""
            rows.setdefault(f"{name}/slot/writes:{where}", {
                "id": f"{name}/slot/writes:{where}", "panel": "slot", "slot": "writes",
                "node": name, "value": where or "no space named", "filled": bool(where),
                "to": where or None, "appears": node["appears"]})  # fmt: skip
        if name in spaces:
            each = [r for r in state["rules"] if r["each"]]
            rows[f"{name}/slot/hands"] = {
                "id": f"{name}/slot/hands", "panel": "slot", "slot": "hands", "node": name,
                "value": f"{len(each)} {'rule' if len(each) == 1 else 'rules'}" if each
                else "nothing", "filled": bool(each), "to": None,
                "appears": node["appears"]}  # fmt: skip
            shows = state.get("shows") or {}
            rows[f"{name}/slot/shows"] = {
                "id": f"{name}/slot/shows", "panel": "slot", "slot": "shows", "node": name,
                "value": "every member", "filled": bool(shows), "to": None,
                "most": shows.get("most"), "appears": node["appears"],
                "expr": expression(shows["first"]) if isinstance(shows.get("first"), str)
                else None}  # fmt: skip
        for rid in [r for r in rows if rows[r]["node"] == name and rows[r]["panel"] == "slot"]:
            if rid not in node["rows"]:
                node["rows"].append(rid)
                values[rid] = rows[rid]["value"]
                told[rows[rid]["appears"]]["appear"].append(rid)
    # Counts that move with the steps: members of a space, what its `shows` lets through, the
    # step a page last changed at, the model calls and refusals in its header.
    for say in told:
        i = say["i"]
        for s in spaces:
            have = [n for n in nodes.values() if n["parent"] == s and n["appears"] <= i]
            if not have and nodes[s]["appears"] > i:
                continue
            words = f"{len(have)} {'member' if len(have) == 1 else 'members'}"
            if values.get(f"{s}/members") is None:
                values[f"{s}/members"] = words
            elif words != _now(told, values, f"{s}/members", i):
                say["change"][f"{s}/members"] = words
            most = rows[f"{s}/slot/shows"].get("most") if f"{s}/slot/shows" in rows else None
            if most:
                shown = f"{min(most, len(have))} of {len(have)}"
                if values[f"{s}/slot/shows"] == "every member":
                    values[f"{s}/slot/shows"] = shown
                elif shown != _now(told, values, f"{s}/slot/shows", i):
                    say["change"][f"{s}/slot/shows"] = shown
        for node in nodes.values():
            if i in node["changed"] and node["appears"] < i:
                say["change"][f"{node['id']}/changed"] = f"changed at step {i + 1}"
    for node in nodes.values():
        values[f"{node['id']}/changed"] = f"changed at step {node['appears'] + 1}"
        values.setdefault(f"{node['id']}/count/thought", "0")
        values.setdefault(f"{node['id']}/count/refused", "0")

    def holds(outer: str, inner: str) -> bool:
        up = nodes.get(inner, {}).get("parent")
        while up:
            if up == outer:
                return True
            up = nodes.get(up, {}).get("parent")
        return False

    def apart(a: str | None, b: str | None) -> bool:
        return (
            bool(a and b)
            and a != b
            and a in nodes
            and b in nodes
            and not (holds(a, b) or holds(b, a))
        )

    # Sockets and the connections between them. Every port a cell has is a socket, whether or
    # not anything plugs in: a slot, filled or empty, and every watch entry's input and output.
    # Inputs sit on the first board of a cell's pair, outputs and slots on the second; a socket
    # on a wall is an input where a connection enters the space and an output where it leaves.
    # A connection runs from an output socket to an input
    # socket of the same kind of signal as a list of hops: nothing crosses a space's wall
    # directly. A hop ends at a socket on the board of each space the connection leaves or
    # enters, and the next hop, a jumper, goes on from the inside of that socket. A write into a
    # space is judged there by the space's rules for every page within it, as they stood at that
    # write, and a write turned away ends at the board of the space whose rule refused it.
    sockets: dict[str, dict] = {}

    def socket(node: str, kind: str, face: str, row: str | None = None, at: int = 0) -> str:
        sid = f"{row or node}#{kind}:{face}"
        sockets.setdefault(sid, {"id": sid, "node": node, "kind": kind, "face": face,
                                 "pair": "first" if face == "in" else "second",
                                 "row": row, "appears": at, "rules": []})  # fmt: skip
        return sid

    def chain(page: str) -> list[str]:
        """The spaces a page is in, the innermost first."""
        out, up = [], nodes.get(page, {}).get("parent")
        while up:
            out.append(up)
            up = nodes.get(up, {}).get("parent")
        return out

    def judged(space: str, at: int, why: str | None) -> list[dict]:
        """The space's own rules for every page within it as they stood at a step, each with
        whether it let the write through; `why` is the reason a write was turned away."""
        return [
            {"row": rid, "says": "no" if why and rows[rid]["expr"]["body"] in why else "yes"}
            for rid in nodes[space]["rows"]
            if rows[rid]["panel"] == "bound" and rows[rid].get("each")
            and not rows[rid].get("from") and rows[rid]["appears"] <= at
        ]  # fmt: skip

    edges: dict[str, dict] = {}

    def connect(kind: str, source: str, target: str, at: int, why: str | None = None) -> str:
        """A connection from a socket to a socket, or, for a write turned away (`why`), to the
        board of the space that refused it, named by `target`."""
        a = sockets[source]
        end = target if why is not None else sockets[target]["node"]
        eid = f"{kind}:{source}->{target}"
        if eid in edges:
            return eid
        leave = [s for s in chain(a["node"]) if s not in chain(end) and s != end]
        enter = [s for s in reversed(chain(end)) if s not in chain(a["node"]) and s != a["node"]]
        enter += [end] if why is not None else []
        writes = a["kind"] in ("wrote", "refused")
        ends = [source]
        for s in leave + enter:
            n = sum(1 for x in sockets.values() if x["node"] == s and x["face"] == "wall") + 1
            sid = f"{s}#{a['kind']}:wall:{n}"
            rules = judged(s, at, why if s == end else None) if writes and s in enter else []
            sockets[sid] = {"id": sid, "node": s, "kind": a["kind"], "face": "wall", "row": None,
                            "pair": "first" if s in enter else "second", "appears": at,
                            "rules": rules}  # fmt: skip
            ends.append(sid)
        if why is None:
            ends.append(target)
        shared = next((s for s in chain(a["node"]) if s in chain(end)), None)
        hops = []
        for k, (x, y) in enumerate(zip(ends, ends[1:], strict=False)):
            # the first hops run inside the spaces it leaves, the last inside those it enters,
            # each a jumper from or to the inside of a wall; the one between runs where both are
            jumper = k != len(leave)
            within = shared
            if k < len(leave):
                within = leave[k]
            elif k > len(leave):
                within = enter[k - len(leave) - 1]
            hops.append({"id": f"{eid}/{k}", "source": sockets[x]["node"], "sourceSocket": x,
                         "target": sockets[y]["node"], "targetSocket": y, "within": within,
                         "jumper": jumper})  # fmt: skip
        edges[eid] = {"id": eid, "kind": kind, "signal": a["kind"], "source": a["node"],
                      "sourceSocket": source, "target": end, "targetSocket": ends[-1],
                      "appears": at, "hops": hops}  # fmt: skip
        return eid

    for rid, r in rows.items():
        if r["panel"] == "slot":
            r["socket"] = socket(r["node"], r["slot"], "slot", rid, r["appears"])
    for r in list(rows.values()):
        at = max(r["appears"], nodes.get(r.get("to") or r.get("hears") or "", {}).get("appears", 0))
        if r["panel"] == "when":
            r["in"] = socket(r["node"], "heard", "in", r["id"], r["appears"])
            r["out"] = socket(r["node"], "wrote", "out", r["id"], r["appears"])
        if r["panel"] == "when" and apart(r.get("hears"), r["node"]):
            out = socket(r["hears"], "heard", "out", None, nodes[r["hears"]]["appears"])
            connect("heard", out, r["in"], max(at, nodes[r["hears"]]["appears"]))
        elif r["panel"] == "slot" and r["slot"] == "asks" and apart(r["node"], r.get("to")):
            into = socket(r["to"], "asks", "in", None, nodes[r["to"]]["appears"])
            connect("asks", r["socket"], into, max(at, nodes[r["to"]]["appears"]))
        elif r["panel"] == "record" and r["signal"] == "wrote" and apart(r["node"], r["to"]):
            r["out"] = socket(r["node"], "wrote", "out", r["id"], r["appears"])
            connect("wrote", r["out"], socket(r["to"], "wrote", "in", None, at), at)
        elif r["panel"] == "record" and r["signal"] == "refused" and r["to"] in nodes:
            why = by_reason(events, r["node"])
            said = re.search(r"\(from ([^)]*)\) is false", why)
            space = said[1] if said and said[1] in nodes else r["to"]
            r["out"] = socket(r["node"], "refused", "out", r["id"], r["appears"])
            first = min(step_of[e["n"]] for e in events if e["page"] == r["node"])
            eid = connect("turned-away", r["out"], space, first, why)
            wall = edges[eid]["targetSocket"]
            for e in events:
                if e["page"] == r["node"] and e["kind"] == "refused":
                    subject = told[step_of[e["n"]]]["subject"]
                    subject |= {h["id"]: "refused" for h in edges[eid]["hops"]}
                    subject[wall] = "refused"
                    for rule in sockets[wall]["rules"]:
                        if rule["says"] == "no":
                            subject[rule["row"]] = "refused"
    heard = {(x["source"], x["target"]) for x in edges.values()}
    for e in events:
        cause = by_n.get(e["cause"])
        if not cause or "refused" in (e["kind"], cause["kind"]) or e["by"] == cause["page"]:
            continue  # a refusal is drawn as turned away, and what a page does by its own rows
        if apart(cause["page"], e["page"]) and (cause["page"], e["page"]) not in heard:
            out = socket(cause["page"], "heard", "out", None, nodes[cause["page"]]["appears"])
            connect("caused", out, socket(e["page"], "heard", "in"), step_of[e["n"]])
    for x in sorted(edges.values(), key=lambda x: (x["appears"], x["id"])):
        told[x["appears"]]["appear"].extend(h["id"] for h in x["hops"])
    for s in sockets.values():
        told[s["appears"]]["appear"].append(s["id"])

    # A crowded space is drawn in regions, one arrangement a question it answered.
    terms = sorted(n for n, node in nodes.items() if node["known_as"] and not node["parent"])
    arrangements = [regions(None, nodes, crowd, terms)]
    at = [0] * len(told)
    for say in told:
        answer = next((e for e in steps[say["i"]]["events"] if e["answered"]), None)
        if say["kind"] == "answer" and answer and answer["shown"]:
            page = answer["page"]
            said = cited(answer, nodes)
            for name in said:
                say["subject"][name] = "kept"
            if f"{page}/slot/shows" in rows:
                say["subject"][f"{page}/slot/shows"] = "kept"
            if any(nodes[n]["parent"] == page for n in crowd):
                arrangements.append(regions(answer, nodes, crowd, terms))
                say["dim"] = sorted(
                    n for n in crowd if nodes[n]["parent"] == page and n not in answer["shown"]
                )
        at[say["i"]] = len(arrangements) - 1

    providers = {n for n, node in nodes.items() if node["archetype"] == "provider"}
    key = {k for say in told for k in [*say["subject"], *say["change"]]}
    key |= {f"{n}/text" for e in events for n in e["shown"]}  # a text a model was shown
    key |= {
        sockets[x[end]]["row"]
        for x in edges.values()
        for end in ("sourceSocket", "targetSocket")
        if sockets[x[end]]["row"] and not {x["source"], x["target"]} & providers
    }  # the rows that matter to the steps: a subject, a change, or the end of an edge drawn
    key |= {r["row"] for s in sockets.values() for r in s["rules"] if r["says"] == "no"}
    out_nodes = [
        cell(nodes[name], rows, sockets, key, spaces, crowd, providers) for name in _ordered(nodes)
    ]
    out_edges = [
        {
            "id": x["id"],
            "kind": x["kind"],
            "signal": x["signal"],
            "source": x["source"],
            "sourceSocket": x["sourceSocket"],
            "target": x["target"],
            "targetSocket": x["targetSocket"],
            "modes": ["topology"]
            if {x["source"], x["target"]} & providers
            else ["dynamics", "topology"],
            "hops": x["hops"],
        }
        for x in sorted(edges.values(), key=lambda x: x["id"])
    ]
    return {
        "card": card,
        "title": card.replace("-", " "),
        "draw": draw,
        "pens": list(PENS),
        "ports": {k: {"prefix": v["prefix"], "word": v["word"]} for k, v in SOCKET.items()},
        "nodes": out_nodes,
        "edges": out_edges,
        "values": dict(sorted(values.items())),
        "arrangements": arrangements,
        "steps": [
            {
                "i": say["i"],
                "kind": say["kind"],
                "symbol": STEP_SYMBOL[say["kind"]],
                "caption": say["words"],
                "arrangement": at[say["i"]],
                "appear": say["appear"],
                "change": [{"id": k, "value": v} for k, v in say["change"].items()],
                "subject": [{"id": k, "pen": v} for k, v in say["subject"].items()],
                "dim": say["dim"],
            }
            for say in told
        ],
    }


def _now(told: list[dict], values: dict, vid: str, before: int) -> str:
    """A value as it stands just before a step."""
    now = values.get(vid, "")
    for say in told[:before]:
        now = say["change"].get(vid, now)
    return now


def by_reason(events: list[dict], page: str) -> str:
    return " ".join(e.get("reason", "") for e in events if e["page"] == page)


def when_id(page: str, w: dict) -> str:
    does = f"asks {w['provider']}" if w["asks"] else "sets " + ", ".join(w["sets"])
    return f"{page}/when/{w['on']}:{does}"


def asked_of(state: dict) -> str:
    return next((w["provider"] or "" for w in state.get("watch", []) if w["asks"]), "")


def cited(answer: dict, nodes: dict) -> list[str]:
    """The pages the answer names among those it was shown: the ones it answered from."""
    said = " ".join(str(v) for v in full(answer["state"] or {}).fields.values())
    return [n for n in answer["shown"] if n in nodes and re.search(rf"\b{re.escape(n)}\b", said)]


def regions(answer: dict | None, nodes: dict, crowd: set[str], terms: list[str]) -> list[dict]:
    """The regions of one arrangement: the notes of a crowded space as shown to it and not shown
    in its latest answer (all on the desk before any), and the term pages in a group of their
    own. A region lists its members in order; the view packs each in a grid."""
    out = []
    for space in sorted({nodes[n]["parent"] for n in crowd}):
        notes = sorted(n for n in crowd if nodes[n]["parent"] == space)
        if answer is None or answer["page"] != space:
            out.append({"id": f"{space}::desk", "space": space, "kind": "desk",
                        "label": "on the desk", "members": notes})  # fmt: skip
            continue
        shown = [n for n in answer["shown"] if n in notes]
        out.append({"id": f"{space}::shown", "space": space, "kind": "shown",
                    "label": f"shown to {space}", "members": shown})  # fmt: skip
        out.append({"id": f"{space}::hidden", "space": space, "kind": "hidden",
                    "label": "not shown",
                    "members": [n for n in notes if n not in shown]})  # fmt: skip
    if terms:
        out.append({"id": "::terms", "space": None, "kind": "terms", "label": "terms",
                    "members": terms})  # fmt: skip
    return out


def rows_of(name: str, state: dict, page: Page) -> list[dict]:
    """The rows of a page's panels as of one write, in panel order: the text, plain fields, its
    own rules, and one when, then row a watch entry. Ids are stable across writes, so a later
    write changes a row rather than adding one."""
    out: list[dict] = []
    if page.body.strip():
        out.append({"id": f"{name}/text", "panel": "text", "value": excerpt(page.body),
                    "body": page.body.strip()})  # fmt: skip
    for k, v in page.fields.items():
        if k in HEADER_FIELDS or k in FOOTER_FIELDS or bookkeeping(k):
            continue
        out.append({"id": f"{name}/holds/{k}", "panel": "holds", "name": k,
                    "value": plain(v, VALUE_WIDTH)})  # fmt: skip
    for rule in state.get("rules", []):
        out.append({"id": f"{name}/bound/{rule['text']}", "panel": "bound", "each": rule["each"],
                    "from": None, "expr": expression(rule["text"])})  # fmt: skip
    for w in state.get("watch", []):
        when = w.get("when")
        out.append({
            "id": when_id(name, w), "panel": "when", "name": hears(w["on"], name),
            "hears": w["hears"] if w["hears"] != name else None,
            "expr": expression(when) if when and when != "true" else None,
            "then": then(w)})  # fmt: skip
    return out


def bookkeeping(field: str) -> bool:
    """A field the runtime keeps for itself, not part of what the page says (`BOOKKEEPING`)."""
    return field in BOOKKEEPING or field.endswith("_asked")


def excerpt(body: str) -> str:
    """The start of a body as prose: its first `TEXT_LINES` lines, and no more than
    `TEXT_LENGTH` characters of them, ending at a word."""
    lines_ = [" ".join(line.replace("**", "").split()) for line in body.splitlines()]
    text = "\n".join([x for x in lines_ if x][:TEXT_LINES])
    if len(text) <= TEXT_LENGTH:
        return text
    return text[: TEXT_LENGTH - 3].rsplit(" ", 1)[0].rstrip(",.;:") + "..."


def cell(node: dict, rows: dict, sockets: dict, key: set, spaces: set, crowd: set,
         providers: set) -> dict:  # fmt: skip
    """One node of graph.json: header, panels in their order, footer, and its board: every
    port it has, in the standard order, each with its short name (its kind's prefix and its
    index among the cell's ports of that kind) and the board of the pair it sits on. Whether
    the pair runs left and right or top and bottom is left to the layout."""
    name = node["id"]
    mine = [rows[r] for r in node["rows"]]
    board = sorted(
        (s for s in sockets.values() if s["node"] == name),
        key=lambda s: (BOARD_ORDER.index(s["kind"]),
                       node["rows"].index(s["row"]) if s["row"] else -1, s["id"]),
    )  # fmt: skip
    names: dict[str, str] = {}  # a port's short name: its kind's prefix and its index in kind
    count: dict[str, int] = {}
    for s in board:
        k = count[s["kind"]] = count.get(s["kind"], -1) + 1
        names[s["id"]] = f"{SOCKET[s['kind']]['prefix']}{k}"
    kinds = kinds_of(node, spaces, crowd)
    symbol = next((k for k in ("character", "provider") if k in kinds), kinds[0])
    text = next((r for r in mine if r["panel"] == "text"), None)
    panels = []
    if text:
        panels.append({"kind": "text", "id": text["id"], "body": text["body"],
                       "key": text["id"] in key})  # fmt: skip
    holds = [r for r in mine if r["panel"] == "holds"]
    shown = [r for k, r in enumerate(holds) if k < HOLDS_SHOWN or r["id"] in key]
    if holds:
        panels.append({"kind": "holds", "title": WORDS["holds"], "more": len(holds) - len(shown),
                       "rows": [{"id": r["id"], "name": r["name"], "key": r["id"] in key}
                                for r in shown]})  # fmt: skip
    bound = [r for r in mine if r["panel"] == "bound"]
    if bound:
        panels.append({"kind": "bound", "title": WORDS["bound"], "rows": [
            {"id": r["id"], "label": WORDS["each"] if r["each"] else WORDS["itself"],
             "from": r["from"], "expr": r["expr"], "key": r["id"] in key}
            for r in bound]})  # fmt: skip
    when = [r for r in mine if r["panel"] == "when"]
    record = [r for r in mine if r["panel"] == "record"]
    if when or record:
        panels.append({"kind": "when", "title": WORDS["when"], "then": WORDS["then"], "rows": [
            {"id": r["id"], "when": r["name"], "expr": r["expr"], "then": r["then"],
             "key": r["id"] in key} for r in when
        ], "record": [{"id": r["id"], "key": r["id"] in key} for r in record]})  # fmt: skip
    slots = sorted(
        (r for r in mine if r["panel"] == "slot"), key=lambda r: BOARD_ORDER.index(r["slot"])
    )
    body = text["body"] if text else ""
    return {
        "id": name,
        "name": name,
        "archetype": node["archetype"],
        "form": "note" if name in crowd else "space" if name in spaces else "cell",
        "parent": node.get("parent"),
        "modes": ["topology"] if name in providers else ["dynamics", "topology"],
        "header": {
            "kinds": kinds,
            "symbol": symbol,
            "avatar": str(node["avatar"]) if node.get("avatar") else None,
            "label": digits(name) if name in crowd else name,
            "line": plain(body.splitlines()[0] if body else "", NOTE_WIDTH),
            "within": node["within"],
            "known_as": node["known_as"],
            "thought": f"{name}/count/thought",
            "refused": f"{name}/count/refused",
        },
        "panels": [] if name in crowd else panels,
        "footer": {
            "slots": [
                {
                    "id": r["id"],
                    "slot": r["slot"],
                    "label": WORDS[r["slot"]],
                    "filled": r["filled"],
                    "socket": r["socket"],
                    "expr": r.get("expr"),
                    "key": r["id"] in key,
                }
                for r in slots
            ],
            "members": f"{name}/members" if name in spaces else None,
            "changed": f"{name}/changed",
        },  # fmt: skip
        "board": [
            {
                "id": s["id"],
                "kind": s["kind"],
                "face": s["face"],
                "pair": s["pair"],
                "row": s["row"],
                "order": k,
                "name": names[s["id"]],
                "label": WORDS[s["kind"]],
                "rules": s["rules"],
            }
            for k, s in enumerate(board)
        ],  # fmt: skip
        "versions": node["versions"],
    }


def _ordered(nodes: dict[str, dict]) -> list[str]:
    """Parents before their members, then by the step each appears and by name."""
    out: list[str] = []

    def visit(parent: str | None) -> None:
        for name in sorted(
            (n for n, node in nodes.items() if node.get("parent") == parent),
            key=lambda n: (nodes[n]["appears"], n),
        ):
            out.append(name)
            visit(name)

    visit(None)
    return out


# ------------------------------------------------------------------------- publishing


def shown(rows: list[dict]) -> dict:
    """The draw that is drawn: the lowest-numbered that passed, else the first, saying so."""
    won = [r["draw"] for r in rows if passed(r)]
    return {"draw": min(won) if won else min(r["draw"] for r in rows), "passed": won}


def publish_card(run: Path, root: Path, date: str, commit: str) -> Path:
    """Publish one run of a card under docs/results/cards/<card>/ and return that folder."""
    rows = lines(run / ROWS)
    if not rows:
        raise SystemExit(f"no rows in {run}: draw a card first, python -m bench.cards CARD.yaml")
    card = rows[0]["card"]
    out = root / RESULTS / card
    out.mkdir(parents=True, exist_ok=True)
    clean = [{k: v for k, v in row.items() if k != "vault"} for row in rows]
    (out / ROWS).write_text("".join(json.dumps(r) + "\n" for r in clean), encoding="utf-8")
    (out / OBSERVATIONS).write_text(
        (run / OBSERVATIONS).read_text(encoding="utf-8"), encoding="utf-8"
    )
    (out / VERDICT).write_text((run / VERDICT).read_text(encoding="utf-8"), encoding="utf-8")
    drawn = {str(r["draw"]): timeline(run / f"draw-{r['draw']}" / "vault") for r in rows}
    (out / "timeline.json").write_text(json.dumps(drawn, indent=1) + "\n", encoding="utf-8")
    pick = shown(rows)
    info = {
        "card": card,
        "model": ", ".join(sorted({r["model"] for r in rows})),
        "date": date,
        "draws": len(rows),
        "passed": len(pick["passed"]),
        "shown": pick["draw"],
        "commit": commit,
    }
    (out / "run.json").write_text(json.dumps(info, indent=1) + "\n", encoding="utf-8")
    describe_card(out)
    return out


def describe_card(folder: Path) -> Path:
    """Write `graph.json` of a published card from its own files and return its path."""
    info = json.loads((folder / "run.json").read_text(encoding="utf-8"))
    events = json.loads((folder / "timeline.json").read_text(encoding="utf-8"))[str(info["shown"])]
    path = folder / "graph.json"
    drawn = graph(events, info["card"], info["shown"])
    path.write_text(json.dumps(drawn, indent=1) + "\n", encoding="utf-8")
    return path


def render(folders: list[Path], viewer: Path = VIEWER) -> list[str]:
    """Draw the pictures of the given card folders with the view, when Node and the view's
    packages are there. Returns what happened, a line each; never fails a publish."""
    npm = shutil.which("npm")
    if not (npm and shutil.which("node") and (viewer / "node_modules").is_dir()):
        return [
            "the view is not installed, so graph.json is written and the pictures are left as "
            f"they were: install Node 20 or later, run `npm ci` in {viewer.name}/, then publish "
            "again or run `npm run render` there"
        ]
    done = subprocess.run(
        [npm, "run", "--silent", "render", "--", *(str(f.resolve()) for f in folders)],
        cwd=viewer,
        capture_output=True,
        text=True,
        timeout=1800,
        check=False,
    )
    if done.returncode:
        return [f"the view could not draw the pictures: {done.stderr.strip()[-400:]}"]
    return [line for line in done.stdout.splitlines() if line.strip()]


def cards(root: Path) -> list[dict]:
    """Every card under bench/cards with its published verdict, the cards drawn first."""
    found = []
    for path in sorted(CARDS.glob("*.yaml")):
        plan = load_value(path.read_text(encoding="utf-8"))
        folder = root / RESULTS / path.stem
        info = (
            json.loads((folder / "run.json").read_text()) if (folder / "run.json").exists() else {}
        )
        line = (folder / VERDICT).read_text(encoding="utf-8").splitlines()[0] if info else ""
        rows = lines(folder / ROWS) if info else []
        found.append(
            {
                "name": path.stem,
                "plan": plan,
                "info": info,
                "line": line,
                "tally": tally(rows),
                "verdict": "not drawn" if not info else "not met" if "not met" in line else "met",
            }
        )
    return found


def bar(success: dict) -> str:
    text = f"at least {success['pass']} of {success['draws']} draws pass"
    for key, words in (
        ("calls_at_most", "median calls a draw at most"),
        ("sent_at_most", "median characters sent at most"),
    ):
        if key in success:
            text += f", {words} {success[key]}"
    return text


def kinds(plan: dict) -> str:
    """Say whether a card's checks are measured, judged or both."""
    expects = [s["expect"] for s in plan["steps"] if "expect" in s]
    judged = any("judged" in e for e in expects)
    measured = any(set(e) - {"judged"} for e in expects)
    return "measured and judged" if judged and measured else "judged" if judged else "measured"


def judged_line(t: dict) -> str:
    """One judged check as the board says it: the question, the scale and the verdicts so far."""
    counts = ", ".join(f"{word} {n}" for word, n in t["counts"].items())
    return (
        f"- Judged: {t['question']} Scale {', '.join(t['scale'])}; passes on "
        f"{', '.join(t['pass'])}. Verdicts by {', '.join(t['by'])}: {counts}"
    )


def picture(name: str, base: str, info: dict, what: str = "dynamics") -> str:
    """A `<picture>` of a card's drawing, dark or light as the reader's page is."""
    alt = f"{name.replace('-', ' ')}, " + (
        "its final state"
        if what == "topology"
        else f"drawn as it happened in draw {info['shown']}"
        + (", the first that passed" if info["passed"] else "")
    )
    kind = "webp" if what == "dynamics" else "png"
    src = f"{base}/{name}/{what}"
    return (
        f'<picture><source media="(prefers-color-scheme: dark)" srcset="{src}-dark.{kind}">'
        f'<img src="{src}-light.{kind}" alt="{alt}" width="720"></picture>'
    )


def board(root: Path) -> str:
    found = cards(root)
    dates = [c["info"]["date"] for c in found if c["info"]]
    parts = [
        "---",
        "kind: research",
        'title: "Trials"',
        "status: draft",
        f"date: {max(dates) if dates else datetime.now(UTC).date().isoformat()}",
        'source: "generated by bench/dynamics.py from docs/results/cards and bench/cards"',
        "---",
        "",
        "# Trials",
        "",
        "This page is generated from the cards and their published runs by `bench/dynamics.py`. "
        "Nobody edits it by hand.",
        "",
        "Each card states its objective and the bar it must clear before it runs. A draw is one "
        "fresh vault and one pass of the card with a real model. Five draws of one small model "
        "support no claim: a met bar is a pilot, and a missed one says where to look. Cards that "
        "have not been drawn are listed with the rest.",
        "",
        "The animation under a card is drawn from one draw's vault history by the view in "
        "`viewer/`, and the picture under it is the same draw's final state. Every page is one "
        "cell: its name and what it is, then its text, the fields it holds, the rules it is "
        "bound by, and what it does when it hears something, then a footer naming who it asks "
        "and where it writes. A space is a frame holding its members. Connections plug into "
        "small sockets on port boards, thin strips along the edges of a cell that face what "
        "they connect to, and are coloured by what flows: blue is heard, amber is written or "
        "added, pink is a write turned away, violet is a model asked, teal is what was kept or "
        "shown. Nothing crosses a space's wall directly: a connection goes to a socket on the "
        "space's board and on inside, and a write into the space is judged there by its rules, "
        "so one turned away stops at that board. Otherwise ink is the structure, and a colour "
        "marks the subject of a step with the same meanings.",
        "",
    ]
    for c in found:
        plan, info = c["plan"], c["info"]
        parts += [
            f"## {c['name'].replace('-', ' ')}",
            "",
            f"- Objective: {plan['objective']}",
            f"- Bar: {bar(plan['success'])}",
            f"- Checks: {kinds(plan)}",
            f"- Latest verdict: {c['verdict']}",
        ]
        parts += [judged_line(t) for t in c["tally"]]
        if info:
            parts += [
                f"- Run: {info['draws']} draws, {info['passed']} passed, model "
                f"`{info['model']}`, {info['date']}, code at `{info['commit'][:10]}`",
                f"- Data: [rows](../results/cards/{c['name']}/{ROWS}), "
                f"[what each draw left](../results/cards/{c['name']}/{OBSERVATIONS}), "
                f"[its history](../results/cards/{c['name']}/timeline.json), "
                f"[the graph drawn](../results/cards/{c['name']}/graph.json)",
                "",
                f'<p align="center">{picture(c["name"], "../results/cards", info)}</p>',
                f'<p align="center">{picture(c["name"], "../results/cards", info, "topology")}</p>',
            ]
        else:
            parts += ["- Run: none yet"]
        parts += [""]
    return "\n".join(parts)


def block(root: Path) -> str:
    drawn = [c for name in FEATURED for c in cards(root) if c["name"] == name and c["info"]]
    parts = [
        START,
        "### Dynamics",
        "",
        "Each trial is drawn from the history of one of its draws, step by step. Every page is "
        "one cell, a space is a frame around its members, and a colour says what flows or what "
        "a step is about: amber for what a character added, blue for what is heard, pink for a "
        "write turned away, teal for what was kept or shown, violet for a model's thought.",
        "",
    ]
    for c in drawn:
        info = c["info"]
        words = c["plan"]["objective"]
        parts += [
            f'<p align="center">{picture(c["name"], "docs/results/cards", info)}</p>',
            f'<p align="center"><sub>{words[0].upper() + words[1:]}. Draw {info["shown"]} of '
            f"{info['draws']}, the first that passed.</sub></p>",
            "",
        ]
    parts += [
        '<p align="center"><a href="docs/research/trials.md">Every trial, red ones included'
        '</a>&nbsp;&nbsp;·&nbsp;&nbsp;<a href="docs/results/cards">the data</a></p>',
        "",
        "<br>",
        END,
    ]
    return "\n".join(parts)


def refresh(root: Path = ROOT) -> list[Path]:
    """Write the board and the README block from what is published."""
    (root / BOARD).parent.mkdir(parents=True, exist_ok=True)
    (root / BOARD).write_text(board(root), encoding="utf-8")
    readme = root / "README.md"
    text = readme.read_text(encoding="utf-8")
    if START not in text or END not in text:
        raise SystemExit(f"README.md has no {START} and {END} markers: add them where it goes")
    head, rest = text.split(START, 1)
    readme.write_text(head + block(root) + rest.split(END, 1)[1], encoding="utf-8")
    return [root / BOARD, readme]


def main(argv: list[str] | None = None) -> int:
    ask = argparse.ArgumentParser(prog="bench.dynamics", description=__doc__.split("\n")[0])
    ask.add_argument("runs", type=Path, nargs="*", help="run directories written by bench.cards")
    ask.add_argument(
        "--redraw", action="store_true", help="describe and draw every published card again"
    )
    ask.add_argument(
        "--date", default=datetime.now(UTC).date().isoformat(), help="day of the draws"
    )
    ask.add_argument(
        "--commit", default=None, help="the code that ran (default: this checkout's HEAD)"
    )
    args = ask.parse_args(argv)
    if not args.runs and not args.redraw:
        ask.error("name a run directory written by bench.cards, or pass --redraw")
    commit = (
        args.commit
        or subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True, check=True
        ).stdout.strip()
    )
    folders = [publish_card(run, ROOT, args.date, commit) for run in args.runs]
    if args.redraw:
        folders += [f for f in sorted((ROOT / RESULTS).iterdir()) if (f / "run.json").exists()]
        for folder in folders:
            describe_card(folder)
    for line in render(folders):
        print(line, file=sys.stderr)
    for path in [*folders, *refresh(ROOT)]:
        print(path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
