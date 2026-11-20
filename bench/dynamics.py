"""A trial drawn as it happened: the vault's history as D2 text, drawn by D2.

    python -m bench.dynamics RUN_DIR... [--date YYYY-MM-DD] [--commit SHA]

Each RUN_DIR is a run of `bench/cards.py` (`rows.jsonl`, `observations.jsonl`, `verdict.txt` and
`draw-N/vault`). For each one this writes, under `docs/results/cards/<card>/`, the rows with the
private vault paths taken out, the observations, the verdict, `timeline.json` (one timeline a
draw, read by `bench/timeline.py`), `run.json`, and two pictures as D2 text: `dynamics.d2`, the
steps of one draw, and `topology.d2`, its final state. When a `d2` binary is found (on PATH, or
named by `CONKY_D2`) it draws them as `dynamics.svg` and `topology.svg`; when not, the SVGs that
are there are left alone and the command says so. Then it rewrites the board
`docs/research/trials.md` and the block between the two `dynamics` markers in `README.md`, both
from the published files alone.

The project describes the graph and D2 draws it: nested containers, automatic layout (ELK), a
sketched look, light and dark, and the steps packed into one SVG. This module is only the codec
from a timeline to D2 text. The one table from archetype to shape is `SHAPES`; the panels of a
cell in the topology are `PANELS`.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import UTC, datetime
from importlib import resources
from pathlib import Path

from bench.cards import OBSERVATIONS, ROWS, VERDICT, lines, passed
from bench.timeline import timeline
from conky.page import RELATIONS, load_value

ROOT = Path(__file__).resolve().parent.parent
CARDS = ROOT / "bench" / "cards"
RESULTS = Path("docs") / "results" / "cards"
BOARD = Path("docs") / "research" / "trials.md"
FEATURED = ("a-keeper-binds-itself", "a-keeper-hears-the-no", "a-clerk-reads-a-crowded-desk")
START, END = "<!-- dynamics:start -->", "<!-- dynamics:end -->"
WEIGHT = {"room": 1, "answer": 1, "write": 1, "rule": 1, "watch": 1, "refused": 1}
WEIGHT |= {"reflex": 1, "bulk": 1}


# ---------------------------------------------------------------- the story, from the events


def story(events: list[dict]) -> list[dict]:
    """Group a timeline into steps: the room as given, then one step an event.

    The room as given is everything before the event that set the first model answer off, so a
    trial begins at the moment something is asked. A step has `kind` (`room`, `answer`, `rule`,
    `watch`, `reflex`, `refused` or `write`), `words`, and the `events` it holds.
    """
    answered = next((e for e in events if e["answered"]), None)
    cause = answered["cause"] if answered else None
    first = cause or next((e["n"] for e in events if e["cause"]), None)
    given = [e for e in events if first and e["n"] < first]
    steps = [{"kind": "room", "words": "the room as given", "events": given}] if given else []
    seen = {e["page"] for e in given}
    rest = events[len(given) :]
    at = 0
    while at < len(rest):
        run = _crowd(rest, at, seen)
        if run:
            fresh = [e for e in run if e["page"] not in seen and e["within"]]
            space = fresh[0]["within"]
            words = f"{fresh[0]['by']} keeps {len(fresh)} pages in {space}"
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
        step["weight"] = WEIGHT[step["kind"]]
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
        return {"kind": "refused", "words": f"{page} is turned away"}
    if e["rules"]:
        many = f"{len(e['rules'])} rules" if len(e["rules"]) > 1 else "a rule"
        return {"kind": "rule", "words": f"{by} adds {many} to {page}"}
    if e["watch"]:
        heard = [w["on"] for w in e["watch"]]
        ear = "listen for refusals" if heard == ["refusal"] else "listen"
        return {"kind": "watch", "words": f"{by} makes {page} {ear}"}
    if e["answered"] and e["shown"]:
        return {
            "kind": "answer",
            "words": f"{page} reads the {len(e['shown'])} shown to it and answers",
        }
    if e["answered"]:
        asked = events[e["cause"] - 1]["page"] if e["cause"] else ""
        return {"kind": "answer", "words": f"{page} answers {asked}".strip()}
    counted = {k: v for k, v in e["fields"].items() if isinstance(v[1], int | float)}
    if e["cause"] and counted and by == page:
        name, (_, value) = next(iter(counted.items()))
        before = _
        if isinstance(before, int | float) and value > before:
            return {"kind": "reflex", "words": f"{page} counts it by itself: {value:g}"}
        return {"kind": "reflex", "words": f"{page} sets {name} to {value:g} by itself"}
    if e["within"]:
        return {"kind": "write", "words": f"{by} keeps {page} in {e['within']}"}
    return {"kind": "write", "words": f"{by} writes {page}"}


class Cast:
    """What the steps put on stage: pages, spaces, rules, bells and refusals, with their steps."""

    def __init__(self, steps: list[dict]) -> None:
        self.pages: dict[str, dict] = {}
        self.walls: list[dict] = []
        self.bells: list[dict] = []
        self.refusals: list[dict] = []
        self.touches: list[dict] = []
        self.answers: list[dict] = []
        self.edge_label: dict[tuple[str, str, str], str] = {}
        self.values: dict[tuple[str, str], float] = {}
        self.edges: dict[tuple[str, str, str], int] = {}
        self.by_n = {e["n"]: e for step in steps for e in step["events"]}
        for step in steps:
            for e in step["events"]:
                self._add(step, e)
        for step in steps:  # where each page stands among those that arrive with it
            fresh = [n for n, p in self.pages.items() if p["i"] == step["i"]]
            for k, n in enumerate(sorted(fresh, key=lambda n: self.pages[n]["n"])):
                self.pages[n]["pos"] = (k, len(fresh))
        self.spaces = {p["within"] for p in self.pages.values() if p["within"]}
        self.spaces |= {r["within"] for r in self.refusals if r["within"]}

    def _add(self, step: dict, e: dict) -> None:
        i, page = step["i"], e["page"]
        cause = self.by_n.get(e["cause"])
        if cause and cause["page"] != page:
            self.edges.setdefault(("caused", cause["page"], page), i)
            words = "wrote" if e["by"] == cause["page"] else "caused"
            self.edge_label.setdefault(("caused", cause["page"], page), words)
        if e["kind"] == "refused":
            if e["within"]:
                self.edges.setdefault(("stop", page, e["within"]), i)
            lane = len(self.refusals)
            self.refusals.append({"i": i, "page": page, "within": e["within"], "lane": lane})
            return
        known = self.pages.setdefault(page, {"i": i, "setup": step["kind"] == "room", "n": e["n"]})
        known |= {"within": e["within"], "role": e["role"], "state": e["state"]}
        avatar = (e["state"] or {}).get("fields", {}).get("avatar")
        if avatar:
            known["avatar"] = avatar
        for name, (_, new) in e["fields"].items():
            if isinstance(new, int | float) and not isinstance(new, bool):
                self.values[(page, name)] = new
                for bell in self.bells:
                    if bell["page"] == page and name in bell["sets"]:
                        bell["counts"].append((i, new))
                        bell["rings"].append(i)
        for other in e["links"]:
            self.edges.setdefault(("link", page, other), i)
        for entry in e["watch"]:
            if entry["hears"]:
                self.edges.setdefault(("watches", entry["hears"], page), i)
            if entry["provider"]:
                self.edges.setdefault(("link", page, entry["provider"]), i)
        for rule in e["rules"]:
            self.walls.append({"i": i, "page": page, "quiet": step["kind"] == "room", **rule})
        for entry in e["watch"]:
            field = next(iter(entry["sets"]), None)
            counts = [(i, self.values[(page, field)])] if (page, field) in self.values else []
            self.bells.append(
                {
                    "i": i,
                    "page": page,
                    "quiet": step["kind"] == "room",
                    "on": entry["on"],
                    "sets": entry["sets"],
                    "counts": counts,
                    "rings": [],
                }
            )
        if e["answered"]:
            said = [
                v[1]
                for k, v in e["fields"].items()
                if isinstance(v[1], str) and not k.endswith("_asked")
            ]
            self.answers.append(
                {"i": i, "page": page, "shown": e["shown"], "said": said[0] if said else ""}
            )
            self.touches.append({"i": i, "page": page, "big": True})
            for bell in self.bells:
                if bell["page"] == page:
                    bell["rings"].append(i)
        elif step["kind"] == "write" and e["page"] in self.pages and known["n"] != e["n"]:
            self.touches.append({"i": i, "page": page, "big": False})


# ------------------------------------------------------------------------ the D2 text


def q(text: object) -> str:
    """A D2 string: quoted, with the characters D2 reads inside quotes escaped."""
    text = str(text).replace("\\", "\\\\").replace('"', '\\"').replace("$", "\\$")
    return '"' + text.replace("\n", "\\n") + '"'


TOKENS = json.loads(resources.files("conky").joinpath("tokens.json").read_text(encoding="utf-8"))
INTERVAL = 1500  # milliseconds a step stays on screen in the animated SVG
CROWD = 12  # more pages than this within a space are drawn as a grid of small notes
SHAPES = {  # archetype -> D2 shape: the one table. A space is a container, not a shape.
    "character": "person",
    "provider": "hexagon",
    "measure": "circle",
    "reflex": "oval",
    "screen": "rectangle",
    "hands": "rectangle",
    "page": "page",
}
PANELS = ("fields", "rules", "hears", "plugs")  # in a cell, in this order


def ground(look: str, name: str) -> str:
    return TOKENS["color"][name][look]


def pen(meaning: str) -> str:
    """The pen that carries a meaning, as its light value: D2 takes one colour for a style set in
    the text, so the same pen is used in both looks."""
    return TOKENS["pen"][TOKENS["meaning"][meaning]]["light"]


INK, MUTE = ground("light", "ink"), ground("light", "mute")
ADDED, REFUSED, HEARD = pen("added"), pen("refused"), pen("heard")
KEPT, THOUGHT = pen("kept"), pen("thought")
WEIGHT_OF = {k: max(1, round(v)) for k, v in TOKENS["weight"].items()}  # D2 takes whole numbers
SIZE = {k: max(8, round(v)) for k, v in TOKENS["size"].items()}  # D2 takes 8 to 100
DASH = {k: int(v.split()[0]) for k, v in TOKENS["dash"].items()}


def theme(look: str) -> dict[str, str]:
    """The plates' ground in D2's theme variables: ink for lines and text, hair for rules, the
    paper for every fill."""
    g = {name: ground(look, name) for name in TOKENS["color"]}
    return {
        "N1": g["ink"], "N2": g["ink"], "N3": g["mute"], "N4": g["hair"], "N5": g["hair"],
        "N6": g["sunken"], "N7": g["paper"], "B1": g["ink"], "B2": g["ink"], "B3": g["hair"],
        "B4": g["raised"], "B5": g["raised"], "B6": g["raised"], "AA2": g["ink"],
        "AA4": g["paper"], "AA5": g["paper"], "AB4": g["paper"], "AB5": g["paper"],
    }  # fmt: skip


def style(**given: object) -> str:
    """A style map in D2: each key with its value, text kept as written."""
    return "{" + "; ".join(f"{k.replace('_', '-')}: {v}" for k, v in given.items()) + "}"


FINE, BASE, SMALL, LARGE = WEIGHT_OF["fine"], WEIGHT_OF["base"], SIZE["base"], SIZE["large"]
LOOK = {"text-transform": "none"}
CLASSES = {  # shared by both pictures
    **{
        kind: f"shape: {shape}; style: {style(stroke_width=FINE, font_size=LARGE, **LOOK)}"
        for kind, shape in SHAPES.items()
    },
    "character": "shape: person; style: "
    + style(stroke_width=FINE, font_size=LARGE, fill="transparent", **LOOK),
    "note": f"shape: square; style: {style(stroke_width=FINE, font_size=SIZE['micro'], **LOOK)}",
    "room": "style: "
    + style(stroke_width=BASE, border_radius=0, font_size=LARGE, bold="false", **LOOK),
    "added": f"shape: text; style: {style(font_color=q(ADDED), font_size=LARGE, **LOOK)}",
    "given": f"shape: text; style: {style(font_size=LARGE, **LOOK)}",
    "bell": "shape: oval; style: "
    + style(stroke_width=FINE, font_size=SMALL, stroke=q(ADDED), **LOOK),
    "bellq": f"shape: oval; style: {style(stroke_width=FINE, font_size=SMALL, **LOOK)}",
    "refusal": "style: "
    + style(
        stroke=q(REFUSED),
        font_color=q(REFUSED),
        stroke_width=WEIGHT_OF["bold"],
        font_size=SMALL,
        **LOOK,
    ),
    "edge": f"style: {style(stroke_width=WEIGHT_OF['hair'], font_size=SMALL, **LOOK)}",
    "title": f"shape: text; style: {style(font_size=SIZE['display'], **LOOK)}",
    "caption": f"shape: text; style: {style(font_size=LARGE, **LOOK)}",
    "panel": f"shape: sql_table; style: {style(stroke_width=FINE, font_size=SMALL, **LOOK)}",
}


def decl(path: str, label: str, *attrs: str) -> str:
    """A D2 node: its path, its label and its attributes."""
    return f"{path}: {q(label)} {{{'; '.join(attrs)}}}"


def link(a: str, b: str, label: str, *attrs: str) -> str:
    """A D2 edge from a to b."""
    return f"{a} -> {b}: {q(label)} {{{'; '.join(attrs)}}}"


def middle(text: str, width: int) -> str:
    """The text shortened in the middle when it is longer than width."""
    if len(text) <= width:
        return text
    keep = width - 3
    return text[: keep - keep // 2] + "..." + text[len(text) - keep // 2 :]


def digits(name: str) -> str:
    found = re.findall(r"\d+", name)
    return str(int(found[-1])) if found else name[:2]


def head(card: str, still: bool) -> list[str]:
    """The shared preamble: ELK layout, the plates' inks for light and dark, thin lines with
    square corners, the shared classes and the title."""

    def overrides(look: str) -> list[str]:
        return [f"      {k}: {q(v)}" for k, v in theme(look).items()]

    return [
        "vars: {",
        "  d2-config: {",
        "    layout-engine: elk",
        "    pad: 24",
        "    theme-id: 301",
        "    dark-theme-id: 301",
        "    theme-overrides: {",
        *overrides("light"),
        "    }",
        "    dark-theme-overrides: {",
        *overrides("dark"),
        "    }",
        "  }",
        "}",
        "direction: right",
        "classes: {",
        *[f"  {name}: {{{body}}}" for name, body in CLASSES.items()],
        "}",
        f"title: {q(card.replace('-', ' ') + (' topology' if still else ''))} "
        "{class: title; near: top-center}",
    ]


class Graph:
    """What both pictures draw, read from a timeline: pages by archetype, the spaces that hold
    them, rules, watches, refusals and the edges between pages."""

    def __init__(self, events: list[dict], still: bool) -> None:
        self.steps = story(events)
        self.cast = Cast(self.steps)
        cast = self.cast
        self.still = still
        self.left = {n for n, p in cast.pages.items() if p["role"] == "provider" and not still}
        self.pages = {n: p for n, p in cast.pages.items() if n not in self.left}
        self.spaces = {s for s in cast.spaces if s not in self.left}
        for s in self.spaces - set(self.pages):
            made = [p["i"] for p in self.pages.values() if p["within"] == s]
            made += [r["i"] for r in cast.refusals if r["within"] == s]
            self.pages[s] = {"i": min(made), "within": None, "role": "page", "n": 0, "state": None}
        self.refused = {r["page"]: r for r in cast.refusals}
        self.crowd = {}
        for space in sorted(self.spaces):
            members = sorted(
                n
                for n, p in self.pages.items()
                if p["within"] == space and p["role"] == "page" and n not in self.spaces
            )
            if len(members) > CROWD:
                self.crowd[space] = members
        self.edges = {
            k: i
            for k, i in cast.edges.items()
            if k[0] != "stop" and k[1] in self.pages | self.refused and k[2] in self.pages
        }

    def arrive(self, space: str) -> int:
        """The step a space appears: its own write, or its first member's."""
        made = [p["i"] for p in self.pages.values() if p["within"] == space]
        made += [r["i"] for r in self.cast.refusals if r["within"] == space]
        return min([self.pages[space]["i"], *made])

    def holds(self, outer: str, inner: str) -> bool:
        up = self.pages.get(inner, {}).get("within")
        while up:
            if up == outer:
                return True
            up = self.pages.get(up, {}).get("within")
        return False

    def path(self, name: str) -> str:
        """The D2 path of a page: its spaces' names, outermost first, then its own."""
        chain = [name]
        up = self.pages.get(name, {}).get("within")
        while up:
            chain.insert(0, up)
            up = self.pages.get(up, {}).get("within")
        if name in self.crowd_of:
            chain.insert(-1, "desk")
        return ".".join(chain)

    @property
    def crowd_of(self) -> dict[str, str]:
        return {n: s for s, members in self.crowd.items() for n in members}

    def kind(self, name: str) -> str:
        return self.pages[name]["role"] if name in self.pages else "page"

    def edge_words(self, key: tuple[str, str, str]) -> str:
        kind = key[0]
        return {"watches": "heard", "link": "links"}.get(kind) or self.cast.edge_label.get(key, "")

    def visible_edges(self) -> list[tuple[str, str, str]]:
        out = []
        for key in self.edges:
            kind, a, b = key
            if a == b or a in self.refused or self.holds(a, b) or self.holds(b, a):
                continue
            if kind == "link" and self.pages[b]["role"] == "provider":
                continue
            if kind == "caused" and (
                ("watches", a, b) in self.edges or ("link", a, b) in self.edges
            ):
                continue
            out.append(key)
        return out


def edge_style(kind: str, words: str = "") -> str:
    """What is heard is blue and dashed, what was kept is teal, a cause is only muted."""
    if kind == "watches":
        return f"class: edge; style.stroke: {q(HEARD)}; style.stroke-dash: {DASH['short']}"
    if words == "wrote":
        return f"class: edge; style.stroke: {q(KEPT)}"
    if kind == "caused":
        return f"class: edge; style.stroke: {q(MUTE)}"
    return "class: edge"


# ---------------------------------------------------------------- the animated picture


def dynamics(events: list[dict], meta: dict) -> str:
    """D2 text for the steps picture: every component declared up front where the final layout
    needs it, hidden, then one step an event that shows what that event added."""
    g = Graph(events, still=False)
    steps, cast = g.steps, g.cast
    base = 1 if steps and steps[0]["kind"] == "room" else 0
    out = head(meta["card"], False)

    def seen(i: int) -> str:
        return "1" if i < base else "0"

    def node(path: str, label: str, shape: str, i: int, extra: str = "") -> list[str]:
        icon = f"; icon: {q(extra)}" if extra else ""
        return [f"{path}: {q(label)} {{shape: {shape}; style.opacity: {seen(i)}{icon}}}"]

    def tree(space: str | None, depth: int) -> list[str]:
        pad = "  " * depth
        lines = []
        names = sorted(n for n, p in g.pages.items() if p["within"] == space and n in g.pages)
        for name in names:
            p = g.pages[name]
            if name in g.spaces:
                lines += [
                    f"{pad}{name}: {q(name)} {{",
                    f"{pad}  class: room",
                    f"{pad}  style.opacity: {seen(g.arrive(name))}",
                ]
                if p["role"] == "character":
                    lines += [
                        f"{pad}  who: {q(name)} {{class: character; style.opacity: {seen(p['i'])}}}"
                    ]
                if name in g.crowd:
                    lines += [
                        f"{pad}  desk: {q('')} {{",
                        f"{pad}    grid-columns: 10",
                        f"{pad}    style.stroke-width: 0",
                        f"{pad}    style.fill: transparent",
                    ]
                    for n in g.crowd[name]:
                        opacity = f"style.opacity: {seen(g.pages[n]['i'])}"
                        lines += [f"{pad}    " + decl(n, digits(n), "class: note", opacity)]
                    lines += [f"{pad}  }}"]
                lines += tree(name, depth + 1)
                for k, wall in enumerate(w for w in cast.walls if w["page"] == name and w["each"]):
                    own = "given" if wall["quiet"] else "added"
                    text = middle(wall["text"], 34)
                    lines += [
                        f"{pad}  "
                        + decl(
                            f"rule{k}", text, f"class: {own}", f"style.opacity: {seen(wall['i'])}"
                        )
                    ]
                for k, bell in enumerate(
                    b for b in cast.bells if b["page"] == name and b["on"] in RELATIONS
                ):
                    own = "bellq" if bell["quiet"] else "bell"
                    words = bell_words(bell, None)
                    lines += [
                        f"{pad}  "
                        + decl(
                            f"bell{k}", words, f"class: {own}", f"style.opacity: {seen(bell['i'])}"
                        )
                    ]
                lines += [f"{pad}}}"]
            elif name not in g.crowd_of:
                shape = p["role"] if p["role"] in SHAPES else "page"
                attrs = [f"class: {shape}", f"style.opacity: {seen(p['i'])}"]
                if p.get("avatar"):
                    attrs.append(f"icon: {q(p['avatar'])}")
                lines += [pad + decl(name, name, *attrs)]
        return lines

    out += tree(None, 0)
    for name, r in g.refused.items():
        out += [
            decl(
                name,
                name,
                "class: page",
                f"style.stroke: {q(REFUSED)}",
                f"style.opacity: {seen(r['i'])}",
            )
        ]
    for key in g.visible_edges():
        kind, a, b = key
        words = g.edge_words(key)
        out += [
            link(
                g.path(a),
                g.path(b),
                words,
                edge_style(kind, words),
                f"style.opacity: {seen(g.edges[key])}",
            )
        ]
    for name, r in g.refused.items():
        into = r["within"]
        if into in g.pages:
            out += [
                link(
                    name,
                    g.path(into),
                    "turned away",
                    "class: refusal",
                    f"style.opacity: {seen(r['i'])}",
                )
            ]
    first = steps[0]["words"] if base else ""
    out += [f"caption: {q(first)} {{class: caption; near: bottom-center}}"]
    out += ["steps: {"]
    for i in range(base, len(steps)):
        out += [f"  s{i}: {{", f"    caption: {q(f'{i + 1}/{len(steps)}   ' + steps[i]['words'])}"]
        out += [f"    {line}" for line in reveal(g, i)]
        out += ["  }"]
    return "\n".join([*out, "}", ""])


def bell_words(bell: dict, count: float | None) -> str:
    words = f"hears {bell['on']}"
    field = next(iter(bell["sets"]), "")
    if count is not None and field:
        return f"{words}\n{field} {count:g}"
    return words


def reveal(g: Graph, i: int) -> list[str]:
    """What step i shows: the components that arrive with it, the edges, the changed counts."""
    cast, lines = g.cast, []
    show = "style.opacity: 1"
    for name, p in g.pages.items():
        if p["i"] == i and name not in g.spaces:
            lines += [f"{g.path(name)}.{show}"]
    for space in g.spaces:
        if g.arrive(space) == i:
            lines += [f"{g.path(space)}.{show}"]
        if space in g.crowd:
            continue
    for k, wall in enumerate(w for w in cast.walls if w["each"]):
        if wall["i"] == i and wall["page"] in g.pages:
            lines += [f"{g.path(wall['page'])}.rule{k}.{show}"]
    for key in g.visible_edges():
        if g.edges[key] == i:
            kind, a, b = key
            lines += [f"({g.path(a)} -> {g.path(b)})[0].{show}"]
    for name, r in g.refused.items():
        if r["i"] == i:
            lines += (
                [f"{name}.{show}", f"({name} -> {g.path(r['within'])})[0].{show}"]
                if r["within"] in g.pages
                else [f"{name}.{show}"]
            )
    for page in g.spaces | set(g.pages):
        for k, bell in enumerate(
            b for b in cast.bells if b["page"] == page and b["on"] in RELATIONS
        ):
            if page not in g.pages:
                continue
            if bell["i"] == i:
                lines += [f"{g.path(page)}.bell{k}.{show}"]
            for at, value in bell["counts"]:
                if at == i:
                    lines += [f"{g.path(page)}.bell{k}: {q(bell_words(bell, value))}"]
    for ans in cast.answers:
        if ans["i"] == i - 1 and ans["page"] in g.pages:
            lines += [
                f"{g.path(ans['page'])}.style.stroke-width: {FINE}",
                f"{g.path(ans['page'])}.style.stroke: B1",
            ]
        if ans["i"] == i:
            lines += [
                f"{g.path(ans['page'])}.style.stroke-width: {WEIGHT_OF['heavy']}",
                f"{g.path(ans['page'])}.style.stroke: {q(THOUGHT)}",
            ]
            if ans["said"] and ans["page"] in g.pages:
                lines += [
                    decl(
                        f"{g.path(ans['page'])}.said",
                        middle(ans["said"].replace("**", ""), 40),
                        "class: given",
                    )
                ]
            last = ans is g.cast.answers[-1] or not any(
                b["page"] == ans["page"] and b["i"] > ans["i"] for b in cast.answers
            )
            if last and ans["shown"] and ans["page"] in g.crowd:
                for n in g.crowd[ans["page"]]:
                    if n in ans["shown"]:
                        lines += [
                            f"{g.path(n)}.style.stroke: {q(KEPT)}",
                            f"{g.path(n)}.style.stroke-width: {WEIGHT_OF['bold']}",
                            f"{g.path(n)}.style.bold: true",
                        ]
                    else:
                        lines += [f"{g.path(n)}.style.opacity: 0.25"]
    return lines


# ---------------------------------------------------------------- the topology picture


def panels(g: Graph, name: str) -> dict[str, list[tuple[str, str, str | None]]]:
    """The rows of a page's panels, as (row, detail, the page the row reaches or None).

    fields: its plain fields. rules: one row a rule. hears: one row a watch entry, reaching the
    page it hears. plugs: the provider it asks, the space it may write into, its `shows`."""
    st = g.pages[name].get("state") or {"fields": {}, "rules": [], "watch": [], "shows": None}
    found: dict[str, list[tuple[str, str, str | None]]] = {p: [] for p in PANELS}
    plain = [(k, v) for k, v in st["fields"].items() if k not in ("avatar", "api", "url", "secret")]
    for k, v in plain[:6]:
        found["fields"].append((k, middle(str(v), 18), None))
    if len(plain) > 6:
        found["fields"].append((f"+{len(plain) - 6} more", "", None))
    for rule in st["rules"]:
        found["rules"].append((middle(rule["text"], 30), "each" if rule["each"] else "rule", None))
    for w in st["watch"]:
        does = ("asks " + str(w["provider"])) if w["asks"] else "sets " + ", ".join(w["sets"])
        found["hears"].append((str(w["on"]), does, w["hears"] if w["hears"] in g.pages else None))
        if w["asks"]:
            found["plugs"].append(
                ("asks", str(w["provider"]), w["provider"] if w["provider"] in g.pages else None)
            )
            if w["writes"]:
                found["plugs"].append(("writes", str(w["writes"]), None))
    if st["shows"]:
        found["plugs"].append(("shows", f"{st['shows'].get('most')} most", None))
    seen: set[tuple[str, str]] = set()
    for panel, rows in found.items():  # one row a name and detail
        found[panel] = [
            r for r in rows if not ((panel, r[0] + r[1]) in seen or seen.add((panel, r[0] + r[1])))
        ]
    return found


def topology(events: list[dict], meta: dict) -> str:
    """D2 text for the final state: every page a cell with its panels, a space's cell holding its
    members' cells, and edges that leave from the row they belong to."""
    g = Graph(events, still=True)
    out = head(meta["card"], True)
    reach: list[str] = []

    def cell(name: str, depth: int) -> list[str]:
        pad, p = "  " * depth, g.pages[name]
        rows = panels(g, name)
        has = any(rows.values())
        icon = f"; icon: {q(p['avatar'])}" if p.get("avatar") else ""
        if name not in g.spaces and not has:
            shape = p["role"] if p["role"] in SHAPES else "page"
            return [pad + decl(name, name, f"class: {shape}", *([icon[2:]] if icon else []))]
        kind = (
            ("space, " if name in g.spaces else "") + p["role"]
            if p["role"] != "page"
            else "space"
            if name in g.spaces
            else "page"
        )
        lines = [
            f"{pad}{name}: {q(name + '  ·  ' + kind)} {{",
            f"{pad}  class: room",
            f"{pad}  direction: right",
        ]
        if icon:
            lines += [f"{pad}  icon: {q(p['avatar'])}"]
        for panel in PANELS:
            if not rows[panel]:
                continue
            style = f"; style.stroke: {q(ADDED)}" if panel == "rules" else ""
            lines += [f"{pad}  {panel}: {q(panel)} {{class: panel{style}"]
            used: set[str] = set()
            for row, detail, target in rows[panel]:
                key = row
                while key in used:
                    key += " "
                used.add(key)
                lines += [f"{pad}    {q(key)}: {q(detail or ' ')}"]
                if target and target != name and not g.holds(target, name):
                    dashes = (
                        f"{{style.stroke: {q(THOUGHT)}}}"
                        if panel == "plugs"
                        else f"{{style.stroke: {q(HEARD)}; style.stroke-dash: {DASH['short']}}}"
                    )
                    here = f"{g.path(name)}.{panel}.{q(key)}"
                    reach.append(
                        f"{target} -> {here} {dashes}"
                        if panel == "hears"
                        else f"{here} -> {g.path(target)}"
                    )
            lines += [f"{pad}  }}"]
        if name in g.crowd:
            lines += [
                f"{pad}  desk: {q('')} {{",
                f"{pad}    grid-columns: 10",
                f"{pad}    style.stroke-width: 0",
                f"{pad}    style.fill: transparent",
            ]
            for n in g.crowd[name]:
                lines += [f"{pad}    {n}: {q(digits(n))} {{class: note}}"]
            lines += [f"{pad}  }}"]
        for member in sorted(
            n for n, m in g.pages.items() if m["within"] == name and n not in g.crowd_of
        ):
            lines += cell(member, depth + 1)
        return lines + [f"{pad}}}"]

    for name in sorted(n for n, p in g.pages.items() if not p["within"]):
        out += cell(name, 0)
    for name in g.refused:
        out += [f"{name}: {q(name)} {{class: page; style.stroke: {q(REFUSED)}}}"]
    out += reach
    for key in g.visible_edges():
        kind, a, b = key
        if kind == "watches":
            continue
        out += [link(g.path(a), g.path(b), g.edge_words(key), edge_style(kind, g.edge_words(key)))]
    for name, r in g.refused.items():
        if r["within"] in g.pages:
            out += [f"{name} -> {g.path(r['within'])}: {q('turned away')} {{class: refusal}}"]
    return "\n".join([*out, ""])


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
    for line in draw_card(out):
        print(line, file=sys.stderr)
    return out


def d2_binary() -> str | None:
    """The D2 program: the one named by CONKY_D2, else the first `d2` on PATH, else none."""
    named = os.environ.get("CONKY_D2")
    return named if named and Path(named).exists() else shutil.which("d2")


def draw_card(folder: Path) -> list[str]:
    """Write the two D2 files of a published card from its own files, and draw them if D2 is
    there. Returns what happened, a line each."""
    info = json.loads((folder / "run.json").read_text(encoding="utf-8"))
    events = json.loads((folder / "timeline.json").read_text(encoding="utf-8"))[str(info["shown"])]
    meta = {"card": info["card"]}
    pictures = {"dynamics": dynamics(events, meta), "topology": topology(events, meta)}
    binary, said = d2_binary(), []
    for name, text in pictures.items():
        (folder / f"{name}.d2").write_text(text, encoding="utf-8")
        if not binary:
            continue
        flags = ["--animate-interval", str(INTERVAL)] if name == "dynamics" else []
        done = subprocess.run(
            [
                binary,
                "--omit-version",
                *flags,
                str(folder / f"{name}.d2"),
                str(folder / f"{name}.svg"),
            ],
            capture_output=True,
            text=True,
            timeout=180,
            check=False,
        )
        if done.returncode:
            said.append(f"{folder.name}/{name}: d2 refused it: {done.stderr.strip()[:300]}")
    if not binary:
        said.append(
            f"{folder.name}: no d2 found, so the .d2 files are written and the SVGs left as they "
            "were: install D2 (https://d2lang.com) or set CONKY_D2 to its path, then publish again"
        )
    return said


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
    alt = (
        f"{name.replace('-', ' ')}, drawn as it happened in draw {info['shown']}, "
        f"the first that passed"
        if info["passed"]
        else f"{name.replace('-', ' ')}, drawn as it happened"
    )
    return f'<img src="{base}/{name}/{what}.svg" alt="{alt}" width="720">'


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
        "The animation under a card is drawn from one draw's vault history, and the topology "
        "under it is the same draw's final state. A frame is a space, a person is a character, "
        "a page is a page, and a table is one panel of a page: its fields, rules, what it hears "
        "or what it reaches. Amber is what the character added, pink is a write that was turned "
        "away, blue is what is heard, teal is what was kept and violet is a model's thought.",
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
                f"[its history](../results/cards/{c['name']}/timeline.json)",
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
        "Each trial is drawn from the history of one of its draws, step by step: a frame for a "
        "space, a person for a character, amber for a rule or watch a character added, and pink "
        "for a write turned away.",
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
    ask.add_argument("runs", type=Path, nargs="+", help="run directories written by bench.cards")
    ask.add_argument(
        "--date", default=datetime.now(UTC).date().isoformat(), help="day of the draws"
    )
    ask.add_argument(
        "--commit", default=None, help="the code that ran (default: this checkout's HEAD)"
    )
    args = ask.parse_args(argv)
    commit = (
        args.commit
        or subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True, check=True
        ).stdout.strip()
    )
    for run in args.runs:
        print(publish_card(run, ROOT, args.date, commit))
    for path in refresh(ROOT):
        print(path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
