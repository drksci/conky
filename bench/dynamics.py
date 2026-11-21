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
are grouped in the panels `PANELS`; a step names its subject and the meaning of the pen it takes,
one of the meanings in `src/conky/tokens.json`.
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

from bench.cards import OBSERVATIONS, ROWS, VERDICT, lines, passed
from bench.timeline import timeline
from conky.page import load_value
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
PANELS = ("fields", "rules", "hears", "plugs")  # the panels of a cell, in this order
CROWD = 12  # more pages than this in one space are drawn as small numbered notes
FIELDS_SHOWN = 6  # a cell lists this many fields before "N more"
# Fields that are not rows: `avatar` is drawn in the header; `api`, `url` and `secret` say how a
# provider is reached, which the provider's kind already says (and a secret is never shown).
# Fields ending `_asked` are digests the runtime keeps; the timeline leaves them out already.
HIDDEN = ("avatar", "api", "url", "secret")
PANEL_WORDS = {"fields": "fields", "rules": "rules", "hears": "listens for", "plugs": "reaches"}
PANEL_SYMBOL = {"fields": "fields", "rules": "rule", "hears": "hears", "plugs": "connector"}
HEARD = {"refusal": "a write turned away", "within": "a page put in it", "link": "a link to it"}
STEP_SYMBOL = {"room": "space", "write": "kept", "bulk": "kept", "rule": "rule", "watch": "hears"}
STEP_SYMBOL |= {"reflex": "reflex", "answer": "thought", "refused": "refusal"}
PICTURES = ("dynamics-light.webp", "dynamics-dark.webp", "topology-light.png", "topology-dark.png")


# ---------------------------------------------------------------- the story, from the events


def story(events: list[dict]) -> list[dict]:
    """Group a timeline into steps: the room as given, then one step an event.

    The room as given is everything before the event that set the first model answer off, so a
    trial begins at the moment something is asked. A step has `kind` (`room`, `answer`, `rule`,
    `watch`, `reflex`, `refused`, `bulk` or `write`), `words`, and the `events` it holds.
    """
    answered = next((e for e in events if e["answered"]), None)
    cause = answered["cause"] if answered else None
    first = cause or next((e["n"] for e in events if e["cause"]), None)
    given = [e for e in events if first and e["n"] < first]
    steps = [{"kind": "room", "words": "The room as given.", "events": given}] if given else []
    seen = {e["page"] for e in given}
    rest = events[len(given) :]
    at = 0
    while at < len(rest):
        run = _crowd(rest, at, seen)
        if run:
            fresh = [e for e in run if e["page"] not in seen and e["within"]]
            space = fresh[0]["within"]
            words = f"{fresh[0]['by']} keeps {len(fresh)} more pages in {space}."
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


def _crowd(events: list[dict], at: int, seen: set[str]) -> list[dict]:
    """A run of many pages put in a space, with the reflexes they set off, or nothing.

    Forty notes are one thing said, not forty steps: the run is drawn as one step."""
    run, fresh, known = [], 0, set(seen)
    for e in events[at:]:
        plain = e["kind"] == "write" and not (e["rules"] or e["watch"] or e["answered"])
        new = plain and e["page"] not in known and e["within"]
        reflex = plain and e["cause"] and e["by"] == e["page"]
        if not (new or reflex):
            break
        known.add(e["page"])
        fresh += bool(new)
        run.append(e)
    return run if fresh >= 6 else []


def _describe(e: dict, events: list[dict]) -> dict:
    page, by = e["page"], e["by"]
    if e["kind"] == "refused":
        rule = re.match(r"rule: (.*) \(from ([^)]*)\) is false", e.get("reason", ""))
        why = f": it breaks {rule[2]}'s rule {rule[1]}" if rule else ""
        return {"kind": "refused", "words": f"{page} is turned away{why}."}
    if e["rules"]:
        said = ", ".join(r["text"] for r in e["rules"])
        many = "rules" if len(e["rules"]) > 1 else "a rule"
        return {"kind": "rule", "words": f"{by} gives {page} {many}: {said}."}
    if e["watch"]:
        heard = ", ".join(HEARD.get(w["on"], w["on"]) for w in e["watch"])
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
    """A value as a cell shows it: one line, no Markdown emphasis, shortened in the middle."""
    if isinstance(value, bool):
        text = str(value).lower()
    elif isinstance(value, float) and value.is_integer():
        text = str(int(value))
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
    body as written. The names come from `conky.rules.reads`; nothing is evaluated."""
    try:
        names = sorted(reads(text)[0])
    except RuleError:
        names = []
    return {"reads": names, "body": text}


def rows_of(name: str, state: dict) -> list[dict]:
    """The rows of a page's panels, in panel order: plain fields; one row a rule; one row a
    watch entry, reaching the page it hears; and the plugs: the provider it asks, the page it
    writes into, its `shows`. A row id is stable across writes, so a later write changes it."""
    out: list[dict] = []

    def row(panel: str, key: str, label: str, value: str, reach: str | None = None, **more) -> None:
        rid = f"{name}/{panel}/{key}"
        if all(r["id"] != rid for r in out):
            out.append(
                {"id": rid, "panel": panel, "name": label, "value": value, "reach": reach, **more}
            )

    for k, v in state["fields"].items():
        if k not in HIDDEN:
            row("fields", k, k, plain(v, 34))
    for rule in state["rules"]:
        words = "for every page within" if rule["each"] else "for itself"
        row("rules", rule["text"], words, "", expr=expression(rule["text"]))
    for w in state["watch"]:
        does = f"asks {w['provider']}" if w["asks"] else "sets " + ", ".join(w["sets"])
        heard = HEARD.get(w["on"], str(w["on"]))
        row("hears", f"{w['on']}:{does}", heard, does, w["hears"])
        if w["asks"]:
            row("plugs", f"asks:{w['provider']}", "asks", str(w["provider"]), w["provider"])
            if w["writes"]:
                row("plugs", f"writes:{w['writes']}", "writes into", str(w["writes"]), w["writes"])
    if state["shows"]:
        first = state["shows"].get("first")
        row("plugs", "shows", "shows first", f"{state['shows'].get('most')} at most",
            expr=expression(first) if isinstance(first, str) else None)  # fmt: skip
    return out


def graph(events: list[dict], card: str, draw: int) -> dict:
    """The graph of one draw: every page a node with its rows, the edges between them, and the
    steps, each saying what appears, what changes, which elements are its subject and with which
    pen meaning, and what is dimmed. Plain data; the view draws it and adds nothing."""
    steps = story(events)
    by_n = {e["n"]: e for e in events}
    nodes: dict[str, dict] = {}
    rows: dict[str, dict] = {}
    edges: dict[str, dict] = {}
    told: list[dict] = []
    refusals: list[tuple[int, dict]] = []
    for step in steps:
        i, kind = step["i"], step["kind"]
        say: dict = {"i": i, "kind": kind, "words": step["words"], "appear": [], "change": {}}
        say |= {"subject": {}, "dim": []}
        for e in step["events"]:
            page = e["page"]
            new = page not in nodes
            node = nodes.setdefault(page, {"id": page, "name": page, "rows": [], "appears": i})
            if new:
                say["appear"].append(page)
            if e["kind"] == "refused":
                node |= {"archetype": "page", "parent": None, "refused": True}
                refusals.append((i, e))
                say["subject"][page] = "refused"
                continue
            node |= {"archetype": e["role"], "parent": e["within"]}
            avatar = (e["state"] or {}).get("fields", {}).get("avatar")
            if avatar:
                node["avatar"] = str(avatar)
            fresh, moved = [], []
            for r in rows_of(page, e["state"]):
                if r["id"] not in rows:
                    rows[r["id"]] = {**r, "node": page, "appears": i, "first": r["value"]}
                    node["rows"].append(r["id"])
                    fresh.append(r)
                    say["appear"].append(r["id"])
                elif r["value"] != rows[r["id"]]["now"]:
                    say["change"][r["id"]] = r["value"]
                    moved.append(r)
                rows[r["id"]] |= {"now": r["value"], "reach": r["reach"]}
            pen = _pen(kind, new)
            if kind == "room" or not pen:
                continue
            if kind in ("write", "bulk") and new:
                say["subject"][page] = pen
            elif kind in ("rule", "watch"):
                for r in fresh:
                    if r["panel"] == ("rules" if kind == "rule" else "hears"):
                        say["subject"][r["id"]] = pen
            elif kind == "reflex":
                for r in moved:
                    say["subject"][r["id"]] = pen
                    for w in e["state"]["watch"]:
                        if r["name"] in w["sets"]:
                            key = f"{w['on']}:sets " + ", ".join(w["sets"])
                            say["subject"][f"{page}/hears/{key}"] = pen
            elif kind == "answer":
                say["subject"][page] = pen
                for r in moved:
                    say["subject"][r["id"]] = pen
            elif kind == "write":
                for r in moved + fresh:
                    say["subject"][r["id"]] = pen
                if not moved + fresh:
                    say["subject"][page] = pen
        told.append(say)
    spaces = {n["parent"] for n in nodes.values() if n.get("parent")}
    for s in sorted(spaces - set(nodes)):  # a space no write named: it still holds its members
        made = min(n["appears"] for n in nodes.values() if n.get("parent") == s)
        nodes[s] = {"id": s, "name": s, "rows": [], "appears": made, "archetype": "page"}
        nodes[s]["parent"] = None
        told[made]["appear"].insert(0, s)
    crowd = set()
    for s in spaces:
        members = [n for n in nodes.values() if n["parent"] == s and n["archetype"] == "page"]
        if len([n for n in members if n["id"] not in spaces]) > CROWD:
            crowd |= {n["id"] for n in members if n["id"] not in spaces}

    def holds(outer: str, inner: str) -> bool:
        up = nodes.get(inner, {}).get("parent")
        while up:
            if up == outer:
                return True
            up = nodes.get(up, {}).get("parent")
        return False

    def apart(a: str, b: str) -> bool:
        return a != b and a in nodes and b in nodes and not holds(a, b) and not holds(b, a)

    def edge(kind: str, a: str, b: str, at: int, **ends: str | None) -> None:
        eid = f"{kind}:{ends.get('sourceRow') or a}->{ends.get('targetRow') or b}"
        if eid not in edges:
            edges[eid] = {"id": eid, "kind": kind, "source": a, "target": b, "appears": at, **ends}

    for r in rows.values():
        if r["reach"] and apart(r["node"], r["reach"]):
            at = max(r["appears"], nodes[r["reach"]]["appears"])
            if r["panel"] == "hears":
                edge("heard", r["reach"], r["node"], at, sourceRow=None, targetRow=r["id"])
            elif r["panel"] == "plugs":
                edge("plugs", r["node"], r["reach"], at, sourceRow=r["id"], targetRow=None)
    heard = {(x["source"], x["target"]) for x in edges.values() if x["kind"] == "heard"}
    step_of = {e["n"]: s["i"] for s in steps for e in s["events"]}
    for e in events:
        cause = by_n.get(e["cause"])
        if not cause or "refused" in (e["kind"], cause["kind"]):
            continue  # a refusal is drawn as turned away, and what hears it by its own row
        if not apart(cause["page"], e["page"]):
            continue
        if (cause["page"], e["page"]) not in heard:
            kind = "wrote" if e["by"] == cause["page"] else "caused"
            edge(kind, cause["page"], e["page"], step_of[e["n"]], sourceRow=None, targetRow=None)
    for i, e in refusals:
        space = e["within"]
        if space not in nodes:
            continue
        wall = next(
            (rid for rid in nodes[space]["rows"] if rid.startswith(f"{space}/rules/")
             and rows[rid]["id"].split("/rules/", 1)[1] in e.get("reason", "")),
            None,
        )  # fmt: skip
        edge("turned-away", e["page"], space, i, sourceRow=None, targetRow=wall)
        told[i]["subject"][f"turned-away:{e['page']}->{wall or space}"] = "refused"
        if wall:
            told[i]["subject"][wall] = "refused"
    for x in sorted(edges.values(), key=lambda x: (x["appears"], x["id"])):
        told[x["appears"]]["appear"].append(x["id"])
    for say in told:
        answer = next((e for e in steps[say["i"]]["events"] if e["answered"]), None)
        if say["kind"] != "answer" or not answer or not answer["shown"]:
            continue
        page = answer["page"]
        for name in answer["shown"]:
            if name in nodes:
                say["subject"][name] = "kept"
        if f"{page}/plugs/shows" in rows:
            say["subject"][f"{page}/plugs/shows"] = "kept"
        say["dim"] = sorted(
            n for n in crowd if nodes[n]["parent"] == page and n not in answer["shown"]
        )
    providers = {n for n, node in nodes.items() if node["archetype"] == "provider"}
    key = {k for say in told for k in [*say["subject"], *say["change"]]}
    key |= {
        x[end]
        for x in edges.values()
        for end in ("sourceRow", "targetRow")
        if x.get(end) and not {x["source"], x["target"]} & providers
    }  # the rows that matter to the steps: a subject, a change, or the end of an edge drawn
    out_nodes = []
    for name in _ordered(nodes):
        node = nodes[name]
        kinds = ["note"] if name in crowd else []
        kinds += ["space"] if name in spaces else []
        if node["archetype"] in ("character", "provider") or not kinds:
            kinds.append(
                node["archetype"] if node["archetype"] in ("character", "provider") else "page"
            )
        panels, more = [], 0
        for panel in PANELS:
            mine = [rows[rid] for rid in node["rows"] if rows[rid]["panel"] == panel]
            if panel == "fields":
                kept = [r for k, r in enumerate(mine) if k < FIELDS_SHOWN or r["id"] in key]
                more = len(mine) - len(kept)
                mine = kept
            if mine:
                panels.append(
                    {
                        "kind": panel,
                        "title": PANEL_WORDS[panel],
                        "symbol": PANEL_SYMBOL[panel],
                        "more": more if panel == "fields" else 0,
                        "rows": [
                            {"id": r["id"], "name": r["name"], "value": r["first"],
                             "key": r["id"] in key, "expr": r.get("expr")}
                            for r in mine
                        ],
                    }
                )  # fmt: skip
        out_nodes.append(
            {
                "id": name,
                "name": name,
                "archetype": node["archetype"],
                "kind": " · ".join(kinds),
                "symbol": kinds[-1] if kinds[-1] in ("character", "provider") else kinds[0],
                "form": "note" if name in crowd else "space" if name in spaces else "cell",
                "label": digits(name) if name in crowd else name,
                "parent": node.get("parent"),
                "avatar": node.get("avatar"),
                "refused": bool(node.get("refused")),
                "modes": ["topology"] if name in providers else ["dynamics", "topology"],
                "panels": [] if name in crowd else panels,
            }
        )
    out_edges = [
        {
            "id": x["id"],
            "kind": x["kind"],
            "label": {"plugs": "asks"}.get(x["kind"], x["kind"].replace("-", " ")),
            "source": x["source"],
            "sourceRow": x.get("sourceRow"),
            "target": x["target"],
            "targetRow": x.get("targetRow"),
            "modes": ["topology"]
            if {x["source"], x["target"]} & providers
            else ["dynamics", "topology"],
        }
        for x in sorted(edges.values(), key=lambda x: x["id"])
    ]
    return {
        "card": card,
        "title": card.replace("-", " "),
        "draw": draw,
        "pens": list(PENS),
        "nodes": out_nodes,
        "edges": out_edges,
        "steps": [
            {
                "i": say["i"],
                "kind": say["kind"],
                "symbol": STEP_SYMBOL[say["kind"]],
                "caption": say["words"][0].upper() + say["words"][1:]
                if say["kind"] == "room"
                else say["words"],
                "appear": say["appear"],
                "change": [{"row": k, "value": v} for k, v in say["change"].items()],
                "subject": [{"id": k, "pen": v} for k, v in say["subject"].items()],
                "dim": say["dim"],
            }
            for say in told
        ],
    }


def _pen(kind: str, new: bool) -> str | None:
    """The meaning of the pen a step's subject takes, by what the step is."""
    return {
        "write": "kept",
        "bulk": "kept" if new else None,
        "rule": "added",
        "watch": "added",
        "reflex": "heard",
        "answer": "thought",
        "refused": "refused",
    }.get(kind)


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
        line = (folder / VERDICT).read_text(encoding="utf-8").strip() if info else ""
        found.append(
            {
                "name": path.stem,
                "plan": plan,
                "info": info,
                "line": line,
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
        "cell: a small line saying what it is, its name, then its rows, grouped as fields, rules, "
        "what it hears and what it plugs into. A space is a frame holding its members. Ink is "
        "the structure; a colour marks only the subject of a step: amber is what a character "
        "added, pink is a write turned away, blue is what is heard, teal is what was kept or "
        "shown and violet is a model's thought.",
        "",
    ]
    for c in found:
        plan, info = c["plan"], c["info"]
        parts += [
            f"## {c['name'].replace('-', ' ')}",
            "",
            f"- Objective: {plan['objective']}",
            f"- Bar: {bar(plan['success'])}",
            f"- Latest verdict: {c['verdict']}",
        ]
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
        "one cell with its rows, a space is a frame around its members, and a colour marks only "
        "what a step is about: amber for what a character added, blue for what is heard, pink "
        "for a write turned away, teal for what was kept or shown, violet for a model's thought.",
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
