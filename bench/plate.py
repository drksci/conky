"""The front-page plates: who got there, where the text went and where the time went.

Drawn from the standard record alone (`bench/record.py`), so it names no scenario and no harness.
The look is a pen-plotter printout on a transparent ground: ink, mute for what is secondary, dot
textures where a tone is wanted, filled and hollow squares for marks. Every colour, weight, dash,
size and type stack comes from the kit (`bench/kit.py`, read from `src/conky/tokens.json`). A pen
appears only where it means something: pink for the harness whose `adapter.json` says `accent`
(the subject and the focus), amber for a broken rule (a warning), and in the flame graphs one pen
for each kind of frame. Other harnesses are told apart by weight and texture, not by hue.
"""

from __future__ import annotations

import math
import statistics
from xml.sax.saxutils import escape

from bench import kit, record

WIDTH = 720
SIZE, WEIGHT, DASH = kit.SIZE, kit.WEIGHT, kit.DASH
# What each colour role draws, by token name: the subject takes the focus pen, a broken rule the
# warning pen. A plate names roles or tokens, never a value.
ROLES = {"accent": "pink", "mark": "amber", "grey": "mute"}
LOOKS = {
    look: kit.palette(look) | {r: kit.palette(look)[t] for r, t in ROLES.items()}
    for look in kit.LOOKS
}
X0, X1 = 172.0, 520.0  # the span every progress axis shares, so the panels line up
SIDE = 548.0  # where the right-hand column starts


class Sheet:
    """A list of SVG parts with the few marks the plate is made of.

    The face is named once, on the root: text inherits the embedded text stack, and code and
    tabular numbers take the one `c` class. An area is filled only with a kit pattern, ink or a
    pen at full value.
    """

    def __init__(self, look: str) -> None:
        self.c = LOOKS[look]
        self.parts: list[str] = []
        self.used: dict[str, str] = {}

    def add(self, text: str) -> None:
        self.parts.append(text)

    def fill(self, kind: str, colour: str) -> str:
        """A kit pattern in a colour, as a paint: `solid` is the colour itself."""
        if kind == "solid":
            return colour
        name = f"{kind}-{colour}"
        self.used.setdefault(name, kit.pattern(name, kind, self.c[colour]))
        return f"url(#{name})"

    def text(
        self,
        x,
        y,
        s,
        size=SIZE["small"],
        fill="ink",
        font="text",
        weight="normal",
        anchor="start",
        gap=0.0,
    ):
        spacing = f' letter-spacing="{gap}em"' if gap else ""
        face = ' class="c"' if font == "code" else ""
        bold = ' font-weight="bold"' if weight == "bold" else ""
        self.add(
            f'<text x="{x:.1f}" y="{y:.1f}"{face} font-size="{size}"{bold} '
            f'text-anchor="{anchor}" fill="{self.c[fill]}"{spacing}>{escape(str(s))}</text>'
        )

    def caps(self, x, y, s, fill="ink", anchor="start", size=SIZE["small"], weight="normal"):
        self.text(x, y, str(s).upper(), size, fill, "text", weight, anchor, 0.1)

    def line(self, x1, y1, x2, y2, width=WEIGHT["fine"], stroke="ink", dash=""):
        extra = f' stroke-dasharray="{dash}"' if dash else ""
        self.add(
            f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{self.c[stroke]}" stroke-width="{width}" stroke-linecap="round"{extra}/>'
        )

    def box(self, x, y, w, h, fill="none", stroke="ink", width=WEIGHT["fine"]):
        paint = fill if fill.startswith("url") or fill == "none" else self.c[fill]
        line = "none" if stroke == "none" else self.c[stroke]
        self.add(
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{max(w, 0):.1f}" height="{max(h, 0):.1f}" '
            f'fill="{paint}" stroke="{line}" stroke-width="{width}"/>'
        )

    def path(self, d, fill="none", stroke="ink", width=WEIGHT["fine"]):
        paint = fill if fill.startswith("url") or fill == "none" else self.c[fill]
        line = "none" if stroke == "none" else self.c[stroke]
        self.add(
            f'<path d="{d}" fill="{paint}" stroke="{line}" stroke-width="{width}" '
            f'stroke-linejoin="round" stroke-linecap="round"/>'
        )

    def svg(self, height: float, title: str) -> str:
        defs = "<defs>" + "".join(self.used[k] for k in sorted(self.used)) + "</defs>\n"
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{height:.0f}" '
            f'viewBox="0 0 {WIDTH} {height:.0f}" role="img" aria-label="{escape(title)}" '
            f'font-family="{escape(kit.TEXT)}">\n'
            f"<title>{escape(title)}</title>\n<style>.c{{font-family:{kit.CODE}}}</style>\n"
            + (defs if self.used else "")
            + "\n".join(self.parts)
            + "\n</svg>\n"
        )


def end_mark(s: Sheet, x: float, y: float, ending: str, colour: str) -> None:
    """A filled square reached the goal; a hollow one did not."""
    s.box(x - 3, y - 3, 6, 6, colour if ending == "reached" else "none", colour, WEIGHT["fine"])


def short(number: float) -> str:
    return f"{number / 1000:,.0f}k" if number >= 1000 else f"{number:,.0f}"


def _setup(rows: list[dict]) -> tuple[list[str], dict, dict, list[str]]:
    """Harnesses in drawing order (no model first, the accent arm last), their rows, who is
    accented, and which use a model."""
    order: list[str] = []
    for uses in (False, True):
        for row in rows:
            if (row["model"] != "none") == uses and row["harness"] not in order:
                order.append(row["harness"])
    accent = {h: bool(record.manifest(h).get("accent")) for h in order}
    order.sort(key=lambda h: accent[h])
    arms = {
        h: sorted((r for r in rows if r["harness"] == h), key=lambda r: r["seed"]) for h in order
    }
    return order, arms, accent, [h for h in order if arms[h][0]["model"] != "none"]


def _head(s: Sheet, title: str, right: str = "") -> None:
    s.text(24, 30, title, SIZE["display"], "ink", "text")
    if right:
        s.caps(WIDTH - 24, 30, right, "grey", "end")


def _state(rows: list[dict], words: str) -> str:
    """The right-hand note, led by the warning when the runs used a scripted stand-in."""
    scripted = any(r["backend"] == "scripted" for r in rows)
    return f"scripted: not a result · {words}" if scripted else words


def _median_run(rs: list[dict], key: str) -> dict:
    """The run nearest the median on key, among those that reached the goal when any did."""
    pool = [r for r in rs if r["ending"] == "reached"] or rs
    middle = statistics.median(r[key] for r in pool)
    return min(pool, key=lambda r: abs(r[key] - middle))


def reached(rows: list[dict], series: list[dict], progress: dict, kind: str, look: str) -> str:
    """Who got there: what was held equal, then every run as a bar from start to goal."""
    s = Sheet(look)
    goal, unit = progress["goal"], progress["unit"]
    steps = {(e["harness"], e["seed"]): e["series"] for e in series}
    order, arms, accent, thinking = _setup(rows)
    seeds = sorted({r["seed"] for r in rows})
    scripted = any(r["backend"] == "scripted" for r in rows)
    state = "scripted: not a result" if scripted else kind
    _head(s, "Who got there", f"{rows[0]['scenario']} · {state} · {rows[0]['date']}")

    def colour(h: str) -> str:
        return "accent" if accent[h] else "ink"

    def fill(h: str) -> str:
        if accent[h]:
            return s.fill("checker", "accent")
        return s.fill("checker" if h in thinking else "dots", "ink")

    def px(value: float) -> float:
        return X0 + (X1 - X0) * min(max(value, 0.0), goal) / goal

    models = sorted({r["model"] for r in rows if r["model"] != "none"}) or ["none"]
    commits = sorted({r["commit"][:7] for r in rows if r["commit"]}) or ["unrecorded"]
    span = f"{seeds[0]} to {seeds[-1]}" if len(seeds) > 1 else f"{seeds[0]}"
    facts = [
        ("model", ", ".join(models)),
        ("runs", f"{len(seeds)} each, seeds {span}"),
        ("budget", f"{max(r['budget_calls'] for r in rows)} calls a run"),
        ("commit", ", ".join(commits)),
    ]
    reasons = record.comparable(rows)
    if reasons:
        facts.append(("not like for like", reasons[0]))
    cell = (WIDTH - 48) / max(len(facts), 4)
    for i, (name, value) in enumerate(facts):
        s.caps(24 + i * cell, 60, name)
        s.text(24 + i * cell, 77, value, SIZE["large"], "ink", "code", "bold")

    top, bar, gap = 116.0, 5.0, 3.0
    lane = max(len(seeds) * (bar + gap) + 14, 50.0)
    s.caps(X0, top - 10, progress["start"])
    s.caps(X1, top - 10, progress["end"], anchor="end")
    bottom = top + lane * len(order)
    for tick in sorted({0.0, goal, *(m["at"] for m in progress.get("milestones", []))}):
        s.line(px(tick), top - 4, px(tick), bottom, WEIGHT["hair"], "grey", DASH["dot"])
        s.caps(px(tick), bottom + 12, f"{tick:,.0f}", anchor="middle")
    for stone in progress.get("milestones", []):
        s.caps(px(stone["at"]), top - 10, stone["name"], anchor="middle")
    s.caps(X0 - 10, bottom + 12, unit, anchor="end")
    for i, h in enumerate(order):
        rs = arms[h]
        y = top + i * lane
        s.caps(24, y + 14, record.label(h), colour(h), size=SIZE["base"], weight="bold")
        s.text(24, y + 29, rs[0]["gloss"], SIZE["base"], "grey", "text")
        first = y + (lane - 8 - len(rs) * (bar + gap) + gap) / 2
        for k, r in enumerate(rs):
            by = first + k * (bar + gap)
            end = px(r["value"])
            s.box(X0, by, max(end - X0, 0.5), bar, fill(h), colour(h))
            for point in steps.get((h, r["seed"]), []):
                at = px(point["progress"] * goal)
                for _ in point["violations"]:
                    s.path(f"M{at - 2.5:.1f},{by - 0.5:.1f} h5 l-2.5,-4.5 Z", "mark", "none")
            end_mark(s, end + 7, by + bar / 2, r["ending"], colour(h))
        got = sum(r["ending"] == "reached" for r in rs)
        mid = y + lane / 2 - 4
        for k, r in enumerate(rs):
            end_mark(s, SIDE + 4 + k * 12, mid - 8, r["ending"], colour(h))
        s.text(SIDE, mid + 14, f"{got} of {len(rs)}", SIZE["large"], colour(h), "code", "bold")
        broken = sum(r["violations"] for r in rs)
        if broken:
            s.text(WIDTH - 24, mid + 14, f"{broken}", SIZE["large"], "mark", "code", "bold", "end")
            s.caps(WIDTH - 24, mid - 5, "rules broken", anchor="end")
        if rs[0]["kept"] is not None:
            s.text(
                WIDTH - 24,
                mid + 14,
                f"{sum(r['kept'] or 0 for r in rs)}",
                SIZE["large"],
                colour(h),
                "code",
                "bold",
                "end",
            )
            s.caps(WIDTH - 24, mid - 5, "pages kept", anchor="end")
    return s.svg(bottom + 26, "Every run drawn as a bar from start to goal, one band per harness.")


SHARES = (("task", "task"), ("screen", "screen"), ("scaffold", "scaffolding"), ("answer", "answer"))
FLAME = (24.0, WIDTH - 24.0)  # a flame graph takes the full width, its harness named above it
ROW = 20.0
# Flame-graph blocks are flat, like a contribution heatmap: a step of the ink ramp, with pink
# only for the subject's run. Blocks are parted by a small gap of empty page, never by a stroke.
TINTS = {
    "total": "ramp4",
    "accent": "accent",
    "step": ("ramp2", "ramp1"),
    "idle": "ramp1",
    "model": "ramp3",
    "screen": "ramp3",
    "task": "ramp2",
    "scaffold": "ramp4",
    "answer": "ramp1",
}
GAP = 2.0  # the empty space between blocks
NAMED = {"step"}  # only the turns carry a name, and only where it fits whole


def _frames(s: Sheet, node: tuple, x: float, y: float, scale: float) -> float:
    """Draw one block and everything under it; return the lowest edge reached."""
    label, value, tint, children = node
    w = value * scale
    if w < 0.4:
        return y
    s.box(x, y, max(w - GAP, 0.4), ROW - GAP, tint, "none", 0)
    if label.startswith("turn") and w > len(label) * 6.2 + 10:
        s.text(x + 4, y + ROW - 8, label, SIZE["base"], "ink")
    low, at = y + ROW, x
    for child in children:
        low = max(low, _frames(s, child, at, y + ROW, scale))
        at += child[1] * scale
    return low


def _key(s: Sheet, y: float, kinds: tuple[tuple[str, str], ...]) -> None:
    x = FLAME[0]
    for tint, word in kinds:
        s.box(x, y - 9, 10, 10, tint, "none", 0)
        s.caps(x + 15, y, word, "ink")
        x += 15 + len(word) * 7.2 + 20


def _flames(s: Sheet, trees: dict[str, tuple], accent: dict, unit: str) -> float:
    """One flame graph a harness, root on top, all on one scale so a narrower one spent less."""
    most = max((tree[1] for tree in trees.values()), default=1) or 1
    scale = (FLAME[1] - FLAME[0]) / most
    y = 86.0
    for h, tree in trees.items():
        colour = "accent" if accent[h] else "ink"
        s.caps(FLAME[0], y, record.label(h), colour, size=SIZE["base"], weight="bold")
        s.text(
            FLAME[1], y, f"{short(tree[1])} {unit}", SIZE["large"], colour, "code", "bold", "end"
        )
        y = _frames(s, tree, FLAME[0], y + 8, scale) + 24
    return y - 12


def text(rows: list[dict], calls: list[dict], look: str) -> str:
    """Where the text went, as flame graphs: the run, each turn, each call, its sources."""
    s = Sheet(look)
    order, arms, accent, thinking = _setup(rows)
    made = {(e["harness"], e["seed"]): e["calls"] for e in calls}
    thinking = [h for h in thinking if any(made.get((h, r["seed"])) for r in arms[h])]
    _head(s, "Where the text went", _state(rows, "characters · median run"))
    _key(s, 62, tuple((TINTS[k], word) for k, word in sorted(SHARES, key=lambda kw: TINTS[kw[0]])))
    trees = {}
    for h in thinking:
        cs = made.get((h, _median_run(arms[h], "chars")["seed"]), [])
        turns: dict[int, list[dict]] = {}
        for c in cs:
            turns.setdefault(c["step"], []).append(c)
        steps = []
        for n, (step, group) in enumerate(sorted(turns.items())):
            leaves = [(word, sum(c.get(k, 0) for c in group), TINTS[k], []) for k, word in SHARES]
            steps.append(
                (f"turn {step}", sum(leaf[1] for leaf in leaves), TINTS["step"][n % 2], leaves)
            )
        root = TINTS["accent"] if accent[h] else TINTS["total"]
        trees[h] = ("the run", sum(step[1] for step in steps), root, steps)
    bottom = _flames(s, trees, accent, "characters")
    return s.svg(bottom, "Flame graphs of the text each harness sent: run, turn, call, source.")


def time(rows: list[dict], calls: list[dict], look: str) -> str:
    """Where the time went, as flame graphs: the run, each turn, then the model or the harness."""
    s = Sheet(look)
    order, arms, accent, thinking = _setup(rows)
    made = {(e["harness"], e["seed"]): e["calls"] for e in calls}
    thinking = [h for h in thinking if any(made.get((h, r["seed"])) for r in arms[h])]
    _head(s, "Where the time went", _state(rows, "seconds · median run"))
    _key(s, 62, ((TINTS["model"], "in the model"), (TINTS["idle"], "in the harness")))
    trees = {}
    for h in thinking:
        cs = made.get((h, _median_run(arms[h], "wall_s")["seed"]), [])
        turns: dict[int, list[tuple]] = {}
        clock = 0.0
        for c in cs:
            parts = turns.setdefault(c["step"], [])
            if c["at"] - clock > 0.05:
                parts.append(("", c["at"] - clock, TINTS["idle"], []))
            parts.append(("model", c["seconds"], TINTS["model"], []))
            clock = c["at"] + c["seconds"]
        steps = [
            (f"turn {step}", sum(part[1] for part in parts), TINTS["step"][n % 2], parts)
            for n, (step, parts) in enumerate(sorted(turns.items()))
        ]
        root = TINTS["accent"] if accent[h] else TINTS["total"]
        trees[h] = (f"the run · {len(cs)} model calls", sum(step[1] for step in steps), root, steps)
    bottom = _flames(s, trees, accent, "seconds")
    return s.svg(bottom, "Flame graphs of the time each harness took: run, turn, model or harness.")


def _vault(s: Sheet, x: float, y: float, w: float, shape: dict, colour: str) -> None:
    """A vault's end state: spaces as frames holding their pages, loose pages above, links."""
    end, start = shape["end"], {n["id"] for n in shape["start"]["nodes"]}
    inside: dict[str, list[dict]] = {}
    by_id = {n["id"]: n for n in end["nodes"]}
    homed = set()
    for e in end["edges"]:
        if e["kind"] == "within" and e["to"] in by_id and e["from"] in by_id:
            inside.setdefault(e["to"], []).append(by_id[e["from"]])
            homed.add(e["from"])
    spaces = [n for n in end["nodes"] if n["kind"] == "space"]
    loose = [n for n in end["nodes"] if n["id"] not in homed and n["kind"] != "space"]
    at: dict[str, tuple[float, float]] = {}

    def page(n: dict, px_: float, py_: float, named: bool, drop: float = 17) -> None:
        fresh = n["id"] not in start
        ink = kit.MEANING["added"] if fresh else "ink"  # a page the character added
        side = 12 if n["kind"] == "character" else 9
        paint = ink if n["kind"] == "character" else s.fill("checker" if fresh else "dots", ink)
        if n["kind"] == "provider":
            s.path(f"M{px_:.1f},{py_ - 6:.1f} l6,6 l-6,6 l-6,-6 Z", "none", ink, WEIGHT["fine"])
        else:
            s.box(px_ - side / 2, py_ - side / 2, side, side, paint, ink, WEIGHT["fine"])
        at[n["id"]] = (px_, py_)
        if named or fresh or n["kind"] != "page":
            tone = kit.MEANING["added"] if fresh else "grey"
            s.caps(px_ - 5, py_ + drop, n["id"][:16], tone, "start", SIZE["micro"])

    gap = w / (len(loose) + 1)
    for i, n in enumerate(sorted(loose, key=lambda n: (n["kind"] != "character", n["id"]))):
        page(n, x + gap * (i + 1), y + 14, True)
    sx = x
    each = (w - 12 * (len(spaces) - 1)) / max(len(spaces), 1)
    for space in spaces:
        s.add(
            f'<rect x="{sx:.1f}" y="{y + 56:.1f}" width="{each:.1f}" height="64" '
            f'fill="none" stroke="{s.c["ink"]}" stroke-width="{WEIGHT["fine"]}" '
            f'stroke-dasharray="{DASH["dot"]}" stroke-linecap="round"/>'
        )
        s.caps(sx + 8, y + 70, space["id"], "ink", weight="bold")
        at[space["id"]] = (sx + each / 2, y + 56)
        members = sorted(inside.get(space["id"], []), key=lambda n: n["id"])
        step = min(22.0, (each - 16) / max(len(members), 1))
        for i, n in enumerate(members):
            page(n, sx + 14 + i * step, y + 86, False, 16 + 10 * (i % 2))
        sx += each + 12
    for e in end["edges"]:
        if e["kind"] != "within" and e["from"] in at and e["to"] in at:
            (ax, ay), (bx, by) = at[e["from"]], at[e["to"]]
            s.line(
                ax,
                ay + 7,
                bx,
                by - (0 if e["to"] in {n["id"] for n in spaces} else 7),
                WEIGHT["hair"],
                colour,
                DASH["dot"],
            )


def _conversation(s: Sheet, x: float, y: float, w: float, shape: dict, facts: dict) -> None:
    """A conversation's end state: a model and the one list that grew, a line a message."""
    s.add(
        f'<circle cx="{x + 20:.1f}" cy="{y + 60:.1f}" r="11" fill="none" '
        f'stroke="{s.c[kit.MEANING["thought"]]}" stroke-width="{WEIGHT["fine"]}"/>'
    )
    s.caps(x + 20, y + 84, "model", anchor="middle", size=SIZE["micro"])
    left, right = x + 56, x + w - 8
    s.box(left, y + 6, right - left, 110, "none", "ink", WEIGHT["fine"])
    s.line(x + 31, y + 60, left, y + 60, WEIGHT["hair"], "ink", DASH["dot"])
    lines = int(facts.get("messages", 0)) or 1
    step = min(4.0, 100.0 / lines)
    for i in range(lines):
        ly = y + 12 + i * step
        s.line(
            left + 6,
            ly,
            left + 6 + (right - left - 12) * (0.35 + 0.65 * ((i * 37) % 10) / 10),
            ly,
            WEIGHT["fine"],
        )
    s.caps((left + right) / 2, y + 130, "one conversation", anchor="middle", size=SIZE["micro"])


def became(rows: list[dict], shapes: list[dict], look: str) -> str:
    """What each harness had become when its median run stopped, with what the run says of it."""
    s = Sheet(look)
    order, arms, accent, thinking = _setup(rows)
    found = {(e["harness"], e["seed"]): e for e in shapes}
    _head(s, "What it became", _state(rows, "the parts at the end of a run"))
    width = (WIDTH - 48 - 28 * (len(thinking) - 1)) / max(len(thinking), 1)
    for i, h in enumerate(thinking):
        colour = "accent" if accent[h] else "ink"
        x = 24 + i * (width + 28)
        shape = found.get((h, _median_run(arms[h], "chars")["seed"]))
        s.caps(x, 62, record.label(h), colour, size=SIZE["base"], weight="bold")
        if shape is None:
            continue
        facts = {f["name"]: f["value"] for f in shape["facts"]}
        if shape["kind"] == "vault":
            _vault(s, x, 76, width, shape, colour)
        elif shape["kind"] == "conversation":
            _conversation(s, x, 76, width, shape, facts)
        shown = list(facts.items())[:4]
        for k, (name, value) in enumerate(shown):
            fx = x + k * width / len(shown)
            number = f"{value:,}" if isinstance(value, int) else str(value)
            s.text(fx, 238, number, SIZE["large"], colour, "code", "bold")
            line, lines = "", []
            for word in str(name).split(" "):
                if line and len(line) + len(word) > 15:
                    lines.append(line)
                    line = word
                else:
                    line = f"{line} {word}".strip()
            for j, part in enumerate([*lines, line][:2]):
                s.text(fx, 252 + j * 11, part, SIZE["small"], "grey", "text")
    return s.svg(276, "The parts each harness was made of when its median run stopped.")


def cost(rows: list[dict], series: list[dict], calls: list[dict], progress: dict, look: str) -> str:
    """What it cost to get this far, in dollars at list price: a line a run."""
    s = Sheet(look)
    order, arms, accent, thinking = _setup(rows)
    goal, unit = progress["goal"], progress["unit"]
    steps = {(e["harness"], e["seed"]): e["series"] for e in series}
    made = {(e["harness"], e["seed"]): e["calls"] for e in calls}
    thinking = [h for h in thinking if any(made.get((h, r["seed"])) for r in arms[h])]
    spent: dict[tuple, float] = {}
    basis = ""
    for h in thinking:
        for r in arms[h]:
            found = record.dollars(r["model"], made.get((h, r["seed"]), []))
            if found:
                spent[(h, r["seed"])], basis = found
    priced = bool(spent) and all((h, r["seed"]) in spent for h in thinking for r in arms[h])
    _head(s, "What it cost", _state(rows, f"{'dollars' if priced else 'characters'}, by {unit}"))

    def worth(h: str, r: dict, chars: float) -> float:
        """Dollars for this many of the run's characters, or the characters when unpriced."""
        if not priced or not r["chars"]:
            return chars
        return spent[(h, r["seed"])] * chars / r["chars"]

    def show(value: float) -> str:
        return f"${value:.4f}" if priced else short(value)

    left, right, top, bottom = 64.0, WIDTH - 96.0, 84.0, 244.0
    if priced:
        listed = record.prices()
        x = 24.0
        for model in sorted({r["model"] for h in thinking for r in arms[h]}):
            price = listed["models"][model]
            words = (
                f"{price['priced_as']} @ ${price['input']:.2f} in · ${price['output']:.2f} out "
                f"per million tokens"
            )
            s.text(x, 62, words, SIZE["small"], "ink", "code")
            x += len(words) * 5.9 + 24
        s.text(WIDTH - 24, 62, basis, SIZE["small"], "grey", "code", anchor="end")
    most = max((worth(h, r, r["chars"]) for h in thinking for r in arms[h]), default=1) or 1
    grid = _nice(most / 4)
    ceiling = grid * (int(most / grid) + 1)

    def px(value: float) -> float:
        return left + (right - left) * min(max(value, 0.0), goal) / goal

    def py(value: float) -> float:
        return bottom - (bottom - top) * value / ceiling

    level = 0.0
    while level <= ceiling + grid / 2:
        s.caps(left - 8, py(level) + 3, show(level) if level else "0", anchor="end")
        level += grid
    for tick in sorted({0.0, goal, *(m["at"] for m in progress.get("milestones", []))}):
        s.caps(px(tick), bottom + 14, f"{tick:,.0f}", anchor="middle")
    s.caps(left - 8, bottom + 14, unit, anchor="end")
    for h in thinking:
        colour = "accent" if accent[h] else "ink"
        middle = _median_run(arms[h], "chars")["seed"]
        for r in arms[h]:
            points = steps.get((h, r["seed"]), [])
            if not points:
                continue
            d, last = f"M{px(0):.1f},{py(0):.1f}", py(0)
            for point in points:
                at, up = px(point["progress"] * goal), py(worth(h, r, point["chars"]))
                d += f" L{at:.1f},{last:.1f} L{at:.1f},{up:.1f}"
                last = up
            end = px(points[-1]["progress"] * goal)
            s.path(d, "none", colour, WEIGHT["bold"] if r["seed"] == middle else WEIGHT["fine"])
            if r["ending"] != "reached":
                end_mark(s, end, last, r["ending"], colour)
        typical = statistics.median(worth(h, r, r["chars"]) for r in arms[h])
        s.text(right + 8, py(typical) + 4, show(typical), SIZE["large"], colour, "code", "bold")
        s.caps(right + 8, py(typical) + 16, f"{record.label(h)}, a run", colour)
    return s.svg(bottom + 26, "What each run cost against progress made, one line for every run.")


def _nice(value: float) -> float:
    """A round step at or above value: 1, 2 or 5 times a power of ten."""
    if value <= 0:
        return 1.0
    scale = 10 ** math.floor(math.log10(value))
    return next(scale * m for m in (1, 2, 5, 10) if scale * m >= value)


def scoreboard(lines: list[dict], look: str) -> str:
    """The scores as a small printed table: one line a harness, best first.

    Each line has `name`, `accent` and `cells`, a list of (text, standing) where standing is
    `best`, `worst` or nothing. Emphasis is by weight, not hue: the best of a column in bold ink,
    the worst in mute; the subject's name in the focus pen.
    """
    s = Sheet(look)
    heads = ("harness", "version", "model", "reached", "cost", "model s", "own s", "score")
    at = (24.0, 164.0, 250.0, 362.0, 452.0, 536.0, 614.0, WIDTH - 24.0)
    ends = ("start", "start", "start", "end", "end", "end", "end", "end")
    for head, x, anchor in zip(heads, at, ends, strict=True):
        s.caps(x, 22, head, anchor=anchor)
    s.line(24, 32, WIDTH - 24, 32, WEIGHT["fine"])
    y = 54.0
    for line in lines:
        s.caps(
            at[0],
            y,
            line["name"],
            "accent" if line["accent"] else "ink",
            size=SIZE["base"],
            weight="bold",
        )
        for k, (words, standing) in enumerate(line["cells"], start=1):
            tone = "grey" if standing == "worst" else "ink"
            last = k == len(heads) - 1
            s.text(at[k], y, words, SIZE["large"] if last else SIZE["base"], tone, "code",
                   "bold" if last or standing == "best" else "normal", ends[k])  # fmt: skip
        s.line(24, y + 11, WIDTH - 24, y + 11, WEIGHT["hair"], "grey", DASH["dot"])
        y += 28
    return s.svg(y - 8, "The scores: one line a harness, best first.")
