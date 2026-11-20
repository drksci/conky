"""The front-page plates: who got there, where the text went and where the time went.

Drawn from the standard record alone (`bench/record.py`), so it names no scenario and no harness.
The look is a pen-plotter printout: one ink, grey for what is secondary, dot textures where a
tone is wanted, filled and hollow squares for marks. Colour is two soft neon pens and no more: one
for the harness whose `adapter.json` says `accent`, one for a broken rule.
"""

from __future__ import annotations

import statistics
from xml.sax.saxutils import escape

from bench import record

WIDTH = 720
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"
SANS = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif"
LOOKS = {
    "light": {
        "ink": "#1E1E1E",
        "grey": "#77777A",
        "accent": "#C99A00",
        "mark": "#0097A7",
        "paper": "#FFFFFF",
    },
    "dark": {
        "ink": "#EDEDED",
        "grey": "#9AA0A8",
        "accent": "#FFE066",
        "mark": "#7DF9FF",
        "paper": "#0D1117",
    },
}
TITLE = (
    "Every run drawn as a bar from start to goal, one band per harness, "
    "with what was held equal above and what it cost below."
)
X0, X1 = 172.0, 520.0  # the span every progress axis shares, so the panels line up
SIDE = 548.0  # where the right-hand column starts


class Sheet:
    """A list of SVG parts with the few marks the plate is made of."""

    def __init__(self, look: str) -> None:
        self.c = LOOKS[look]
        self.parts: list[str] = []

    def add(self, text: str) -> None:
        self.parts.append(text)

    def text(
        self, x, y, s, size=8, fill="ink", font=MONO, weight="normal", anchor="start", gap=0.0
    ):
        spacing = f' letter-spacing="{gap}em"' if gap else ""
        self.add(
            f'<text x="{x:.1f}" y="{y:.1f}" font-family="{font}" font-size="{size}" '
            f'font-weight="{weight}" text-anchor="{anchor}" fill="{self.c[fill]}"{spacing}>'
            f"{escape(str(s))}</text>"
        )

    def caps(self, x, y, s, fill="grey", anchor="start", size=8.5, weight="normal"):
        self.text(x, y, str(s).upper(), size, fill, MONO, weight, anchor, 0.14)

    def line(self, x1, y1, x2, y2, width=0.75, stroke="ink", dash=""):
        extra = f' stroke-dasharray="{dash}"' if dash else ""
        self.add(
            f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{self.c[stroke]}" stroke-width="{width}" stroke-linecap="round"{extra}/>'
        )

    def box(self, x, y, w, h, fill="none", stroke="ink", width=0.75):
        paint = fill if fill.startswith("url") or fill == "none" else self.c[fill]
        line = "none" if stroke == "none" else self.c[stroke]
        self.add(
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{max(w, 0):.1f}" height="{max(h, 0):.1f}" '
            f'fill="{paint}" stroke="{line}" stroke-width="{width}"/>'
        )

    def path(self, d, fill="none", stroke="ink", width=1.2):
        paint = fill if fill.startswith("url") or fill == "none" else self.c[fill]
        line = "none" if stroke == "none" else self.c[stroke]
        self.add(
            f'<path d="{d}" fill="{paint}" stroke="{line}" stroke-width="{width}" '
            f'stroke-linejoin="round" stroke-linecap="round"/>'
        )

    def defs(self) -> str:
        def tile(name: str, size: int, squares: str, colour: str) -> str:
            return (
                f'<pattern id="{name}" width="{size}" height="{size}" '
                f'patternUnits="userSpaceOnUse"><path d="{squares}" fill="{self.c[colour]}" '
                f'shape-rendering="crispEdges"/></pattern>'
            )

        dots, dense = "M0 0h1v1h-1z", "M0 0h1v1h-1zM2 2h1v1h-1z"
        return (
            "<defs>"
            + tile("dots", 4, dots, "ink")
            + tile("dense", 4, dense, "ink")
            + tile("dense-accent", 4, dense, "accent")
            + "</defs>"
        )

    def svg(self, height: float, title: str) -> str:
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{height:.0f}" '
            f'viewBox="0 0 {WIDTH} {height:.0f}" role="img" aria-label="{escape(title)}">\n'
            f"<title>{escape(title)}</title>\n{self.defs()}\n"
            + "\n".join(self.parts)
            + "\n</svg>\n"
        )


def end_mark(s: Sheet, x: float, y: float, ending: str, colour: str) -> None:
    """A filled square reached the goal; a hollow one did not."""
    s.box(x - 3, y - 3, 6, 6, colour if ending == "reached" else "none", colour, 1.0)


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
    s.text(24, 28, title, 15, "ink", SANS, "bold")
    if right:
        s.caps(WIDTH - 24, 28, right, "grey", "end")
    s.line(24, 40, WIDTH - 24, 40)


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
            return "url(#dense-accent)"
        return "url(#dense)" if h in thinking else "url(#dots)"

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
        s.text(24 + i * cell, 77, value, 12.5, "ink", SANS, "bold")

    top, bar, gap = 116.0, 5.0, 3.0
    lane = max(len(seeds) * (bar + gap) + 14, 50.0)
    s.caps(X0, top - 10, progress["start"])
    s.caps(X1, top - 10, progress["end"], anchor="end")
    bottom = top + lane * len(order)
    for tick in sorted({0.0, goal, *(m["at"] for m in progress.get("milestones", []))}):
        s.line(px(tick), top - 4, px(tick), bottom, 0.75, "grey", "1 4")
        s.caps(px(tick), bottom + 12, f"{tick:,.0f}", anchor="middle")
    for stone in progress.get("milestones", []):
        s.caps(px(stone["at"]), top - 10, stone["name"], anchor="middle")
    s.caps(X0 - 10, bottom + 12, unit, anchor="end")
    for i, h in enumerate(order):
        rs = arms[h]
        y = top + i * lane
        s.caps(24, y + 14, h, colour(h), size=10.5, weight="bold")
        s.text(24, y + 29, rs[0]["gloss"], 9.5, "grey", SANS)
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
        s.text(SIDE, mid + 14, f"{got} of {len(rs)}", 14, colour(h), SANS, "bold")
        broken = sum(r["violations"] for r in rs)
        if broken:
            s.text(WIDTH - 24, mid + 14, f"{broken}", 14, "mark", SANS, "bold", "end")
            s.caps(WIDTH - 24, mid - 5, "rules broken", anchor="end")
        if rs[0]["kept"] is not None:
            s.text(
                WIDTH - 24,
                mid + 14,
                f"{sum(r['kept'] or 0 for r in rs)}",
                14,
                colour(h),
                SANS,
                "bold",
                "end",
            )
            s.caps(WIDTH - 24, mid - 5, "pages kept", anchor="end")
    return s.svg(bottom + 26, "Every run drawn as a bar from start to goal, one band per harness.")


SHARES = (
    ("task", "task"),
    ("screen", "screen"),
    ("scaffold", "scaffolding"),
    ("answer", "answers"),
)
FLAME = (24.0, WIDTH - 24.0)  # a flame takes the full width, its harness named above it
ROW = 20.0


def _flame_head(s: Sheet, y: float, name: str, total: str, colour: str) -> None:
    s.caps(FLAME[0], y, name, colour, size=10.5, weight="bold")
    s.text(FLAME[1], y, total, 14, colour, SANS, "bold", "end")


def _cell(s: Sheet, x, y, w, paint, colour, label="", fill_text="ink") -> None:
    """One box of a flame, with its label inside when it fits."""
    s.box(x, y, max(w - 1, 0.5), ROW - 2, paint, colour, 1.0)
    if label and w > len(label) * 5.6 + 8:
        if paint != "none":
            s.box(x + 3, y + 3, len(label) * 5.6 + 4, ROW - 8, "paper", "none")
        s.text(x + 5, y + ROW - 7.5, label, 9.5, fill_text, SANS, "bold")


def text(rows: list[dict], calls: list[dict], look: str) -> str:
    """Where the text went: a flame a harness. The run, then where it came from, then each step."""
    s = Sheet(look)
    order, arms, accent, thinking = _setup(rows)
    made = {(e["harness"], e["seed"]): e["calls"] for e in calls}
    _head(s, "Where the text went", _state(rows, "characters · run, source, step"))
    picks = {h: _median_run(arms[h], "chars") for h in thinking}
    runs = {h: made.get((h, picks[h]["seed"]), []) for h in thinking}
    totals = {h: {k: sum(c.get(k, 0) for c in runs[h]) for k, _ in SHARES} for h in thinking}
    most = max((sum(t.values()) for t in totals.values()), default=1) or 1
    fills = {"task": "none", "screen": "url(#dots)", "scaffold": "url(#dense)", "answer": "ink"}
    span = FLAME[1] - FLAME[0]
    y = 66.0
    for h in thinking:
        colour = "accent" if accent[h] else "ink"
        whole = sum(totals[h].values())
        _flame_head(s, y, h, f"{short(whole)} characters", colour)
        y += 8
        _cell(s, FLAME[0], y, span * whole / most, "none", colour, "the run")
        x = FLAME[0]
        for key, word in SHARES:
            amount = totals[h][key]
            w = span * amount / most
            paint = fills[key]
            if accent[h]:
                paint = {"url(#dense)": "url(#dense-accent)", "ink": "accent"}.get(paint, paint)
            _cell(s, x, y + ROW, w, paint, colour, f"{word} {short(amount)}")
            inner = x
            by_step: dict[int, int] = {}
            for c in runs[h]:
                by_step[c["step"]] = by_step.get(c["step"], 0) + c.get(key, 0)
            for _, part in sorted(by_step.items()):
                pw = span * part / most
                s.box(inner, y + 2 * ROW, max(pw - 1, 0.3), ROW - 8, paint, colour, 0.75)
                inner += pw
            x += w
        y += 3 * ROW + 18
    return s.svg(
        y - 12, "Text sent in the median run of each harness: the run, its sources, each step."
    )


def time(rows: list[dict], calls: list[dict], look: str) -> str:
    """Where the time went: a flame a harness. The run, then each step, then each model call."""
    s = Sheet(look)
    order, arms, accent, thinking = _setup(rows)
    made = {(e["harness"], e["seed"]): e["calls"] for e in calls}
    _head(s, "Where the time went", _state(rows, "seconds · run, step, model call"))
    picks = {h: _median_run(arms[h], "wall_s") for h in thinking}
    runs = {h: made.get((h, picks[h]["seed"]), []) for h in thinking}
    longest = max((c["at"] + c["seconds"] for cs in runs.values() for c in cs), default=1) or 1
    span = FLAME[1] - FLAME[0]

    def px(seconds: float) -> float:
        return FLAME[0] + span * seconds / longest

    y = 66.0
    for h in thinking:
        colour = "accent" if accent[h] else "ink"
        paint = "url(#dense-accent)" if accent[h] else "url(#dense)"
        cs = runs[h]
        end = cs[-1]["at"] + cs[-1]["seconds"] if cs else 0
        _flame_head(s, y, h, f"{end:,.0f} seconds", colour)
        y += 8
        _cell(
            s, FLAME[0], y, px(end) - FLAME[0], "none", colour, f"the run · {len(cs)} model calls"
        )
        spans: dict[int, list[float]] = {}
        for c in cs:
            lo, hi = spans.setdefault(c["step"], [c["at"], c["at"] + c["seconds"]])
            spans[c["step"]] = [min(lo, c["at"]), max(hi, c["at"] + c["seconds"])]
        for step, (lo, hi) in sorted(spans.items()):
            _cell(s, px(lo), y + ROW, px(hi) - px(lo), "none", colour, f"{step}")
        for c in cs:
            w = px(c["at"] + c["seconds"]) - px(c["at"])
            s.box(px(c["at"]), y + 2 * ROW, max(w - 1, 0.3), ROW - 8, paint, colour, 0.75)
        y += 3 * ROW + 18
    return s.svg(y - 12, "The median run of each harness: the run, its steps, each model call.")


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
        ink = "accent" if fresh else "ink"
        side = 12 if n["kind"] == "character" else 9
        paint = (
            ink if n["kind"] == "character" else ("url(#dense-accent)" if fresh else "url(#dots)")
        )
        if n["kind"] == "provider":
            s.path(f"M{px_:.1f},{py_ - 6:.1f} l6,6 l-6,6 l-6,-6 Z", "none", ink, 1.0)
        else:
            s.box(px_ - side / 2, py_ - side / 2, side, side, paint, ink, 1.0)
        at[n["id"]] = (px_, py_)
        if named or fresh or n["kind"] != "page":
            tone = "accent" if fresh else "grey"
            s.caps(px_ - 5, py_ + drop, n["id"][:16], tone, "start", 7.5)

    gap = w / (len(loose) + 1)
    for i, n in enumerate(sorted(loose, key=lambda n: (n["kind"] != "character", n["id"]))):
        page(n, x + gap * (i + 1), y + 14, True)
    sx = x
    each = (w - 12 * (len(spaces) - 1)) / max(len(spaces), 1)
    for space in spaces:
        s.add(
            f'<rect x="{sx:.1f}" y="{y + 56:.1f}" width="{each:.1f}" height="64" rx="6" '
            f'fill="none" stroke="{s.c["ink"]}" stroke-width="1" stroke-dasharray="1 4" '
            f'stroke-linecap="round"/>'
        )
        s.caps(sx + 8, y + 70, space["id"], "ink", size=8, weight="bold")
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
                0.9,
                colour,
                "1 3",
            )


def _conversation(s: Sheet, x: float, y: float, w: float, shape: dict, facts: dict) -> None:
    """A conversation's end state: a model and the one list that grew, a line a message."""
    s.add(
        f'<circle cx="{x + 20:.1f}" cy="{y + 60:.1f}" r="11" fill="none" stroke="{s.c["ink"]}" '
        f'stroke-width="1"/>'
    )
    s.caps(x + 20, y + 84, "model", anchor="middle", size=7.5)
    left, right = x + 56, x + w - 8
    s.box(left, y + 6, right - left, 110, "none", "ink", 1.0)
    s.line(x + 31, y + 60, left, y + 60, 0.9, "ink", "1 3")
    lines = int(facts.get("messages", 0)) or 1
    step = min(4.0, 100.0 / lines)
    for i in range(lines):
        ly = y + 12 + i * step
        s.line(
            left + 6,
            ly,
            left + 6 + (right - left - 12) * (0.35 + 0.65 * ((i * 37) % 10) / 10),
            ly,
            0.9,
        )
    s.caps((left + right) / 2, y + 130, "one conversation", anchor="middle", size=7.5)


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
        s.caps(x, 62, h, colour, size=10.5, weight="bold")
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
            s.text(fx, 238, number, 14, colour, SANS, "bold")
            line, lines = "", []
            for word in str(name).split(" "):
                if line and len(line) + len(word) > 15:
                    lines.append(line)
                    line = word
                else:
                    line = f"{line} {word}".strip()
            for j, part in enumerate([*lines, line][:2]):
                s.text(fx, 252 + j * 11, part, 8.5, "grey", SANS)
    return s.svg(276, "The parts each harness was made of when its median run stopped.")
