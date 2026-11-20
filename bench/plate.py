"""The front-page plates: who got there, where the text went and where the time went.

Drawn from the standard record alone (`bench/record.py`), so it names no scenario and no harness.
The look is a pen-plotter printout: one ink, grey for what is secondary, dot textures where a
tone is wanted, filled and hollow squares for marks. Colour is two neon pens and no more: one
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
    "light": {"ink": "#1E1E1E", "grey": "#8A8A86", "accent": "#E600E6", "mark": "#6400FF"},
    "dark": {"ink": "#EDEDED", "grey": "#8E949C", "accent": "#FF3DF2", "mark": "#00FFFF"},
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

    def caps(self, x, y, s, fill="grey", anchor="start", size=7.5, weight="normal"):
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
        s.caps(24, y + 14, h, colour(h), size=9.5, weight="bold")
        s.text(24, y + 28, rs[0]["gloss"], 8.5, "grey", SANS)
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


def text(rows: list[dict], calls: list[dict], look: str) -> str:
    """Where the text went: one bar a harness, cut by where each character came from."""
    s = Sheet(look)
    order, arms, accent, thinking = _setup(rows)
    made = {(e["harness"], e["seed"]): e["calls"] for e in calls}
    _head(s, "Where the text went", _state(rows, "characters, median run"))
    picks = {h: _median_run(arms[h], "chars") for h in thinking}
    totals = {
        h: {k: sum(c.get(k, 0) for c in made.get((h, picks[h]["seed"]), [])) for k, _ in SHARES}
        for h in thinking
    }
    most = max((sum(t.values()) for t in totals.values()), default=1) or 1
    fills = {"task": "none", "screen": "url(#dots)", "scaffold": "url(#dense)", "answer": "ink"}
    y = 62.0
    named: set[str] = set()
    for h in thinking:
        colour = "accent" if accent[h] else "ink"
        s.caps(24, y + 16, h, colour, size=9.5, weight="bold")
        x = X0
        for key, word in SHARES:
            amount = totals[h][key]
            w = (X1 - X0) * amount / most
            paint = fills[key]
            if accent[h]:
                paint = {"url(#dense)": "url(#dense-accent)", "ink": "accent"}.get(paint, paint)
            s.box(x, y, max(w, 0.5), 24, paint, colour, 1.0)
            if w > 24:
                s.text(x + 4, y + 38, short(amount), 9.5, "ink", SANS, "bold")
            if w > len(word) * 5.6 and key not in named:
                s.caps(x + 4, y - 7, word)
                named.add(key)
            x += w
        s.text(x + 10, y + 17, short(sum(totals[h].values())), 14, colour, SANS, "bold")
        y += 62
    if len(thinking) == 2 and any(accent[h] for h in thinking):
        ours = next(h for h in thinking if accent[h])
        other = next(h for h in thinking if h != ours)
        a, b = (statistics.median(r["chars"] for r in arms[h]) for h in (ours, other))
        if b and a != b:
            change = round(100 * (a / b - 1))
            s.text(SIDE + 56, 96, f"{abs(change)}%", 30, "accent", SANS, "bold")
            s.text(
                SIDE + 56, 114, f"{'less' if change < 0 else 'more'} than {other}", 9, "grey", SANS
            )
    return s.svg(y - 6, "Text sent in the median run of each harness, cut by where it came from.")


def time(rows: list[dict], calls: list[dict], look: str) -> str:
    """Where the time went: the median run of each harness as a flame, steps over calls."""
    s = Sheet(look)
    order, arms, accent, thinking = _setup(rows)
    made = {(e["harness"], e["seed"]): e["calls"] for e in calls}
    _head(s, "Where the time went", _state(rows, "seconds, median run · steps over model calls"))
    picks = {h: _median_run(arms[h], "wall_s") for h in thinking}
    runs = {h: made.get((h, picks[h]["seed"]), []) for h in thinking}
    longest = max((c["at"] + c["seconds"] for cs in runs.values() for c in cs), default=1) or 1

    def px(seconds: float) -> float:
        return X0 + (X1 - X0) * seconds / longest

    y = 60.0
    for h in thinking:
        colour = "accent" if accent[h] else "ink"
        paint = "url(#dense-accent)" if accent[h] else "url(#dense)"
        cs = runs[h]
        s.caps(24, y + 16, h, colour, size=9.5, weight="bold")
        spans: dict[int, list[float]] = {}
        for c in cs:
            lo, hi = spans.setdefault(c["step"], [c["at"], c["at"] + c["seconds"]])
            spans[c["step"]] = [min(lo, c["at"]), max(hi, c["at"] + c["seconds"])]
        for step, (lo, hi) in sorted(spans.items()):
            s.box(px(lo), y, max(px(hi) - px(lo), 0.5), 10, "none", colour, 1.0)
            if px(hi) - px(lo) > 14:
                s.caps(px(lo) + 3, y + 8, step, colour, size=6.5)
        for c in cs:
            s.box(
                px(c["at"]),
                y + 12,
                max(px(c["at"] + c["seconds"]) - px(c["at"]) - 1, 0.5),
                12,
                paint,
                colour,
                0.75,
            )
        end = cs[-1]["at"] + cs[-1]["seconds"] if cs else 0
        s.text(px(end) + 10, y + 17, f"{end:,.0f} s", 14, colour, SANS, "bold")
        s.caps(24, y + 30, f"{len(cs)} calls")
        y += 56
    for tick in range(0, int(longest) + 1, 60):
        s.line(px(tick), 52, px(tick), y - 22, 0.75, "grey", "1 4")
        s.caps(px(tick), y - 10, f"{tick}", anchor="middle")
    return s.svg(
        y + 2, "The median run of each harness along a time axis: steps above, model calls below."
    )
