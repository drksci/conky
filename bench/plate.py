"""The front-page plate: one printout that says who got there, what it cost and what was equal.

Drawn from the standard record alone (`bench/record.py`), so it names no scenario and no harness.
The look is a pen-plotter printout: one ink, grey for what is secondary, dot textures where a
tone is wanted, filled and hollow squares for marks. Colour is two neon pens and no more: one
for the harness whose `adapter.json` says `accent`, one for a broken rule.
"""

from __future__ import annotations

import statistics
from xml.sax.saxutils import escape

from bench import record

WIDTH = 880
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
X0, X1 = 204.0, 632.0  # the span every progress axis shares, so the panels line up
SIDE = 664.0  # where the right-hand column starts


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


def plate(rows: list[dict], series: list[dict], progress: dict, kind: str, look: str) -> str:
    """The whole plate as SVG text. rows and series are the standard record of one set of runs."""
    s = Sheet(look)
    goal, unit = progress["goal"], progress["unit"]
    steps = {(e["harness"], e["seed"]): e["series"] for e in series}
    order: list[str] = []
    for uses in (False, True):
        for row in rows:
            if (row["model"] != "none") == uses and row["harness"] not in order:
                order.append(row["harness"])
    order.sort(key=lambda h: bool(record.manifest(h).get("accent")))  # the accent arm goes last
    arms = {
        h: sorted((r for r in rows if r["harness"] == h), key=lambda r: r["seed"]) for h in order
    }
    accent = {h: bool(record.manifest(h).get("accent")) for h in order}
    thinking = [h for h in order if arms[h][0]["model"] != "none"]
    seeds = sorted({r["seed"] for r in rows})
    reasons = record.comparable(rows)
    scripted = any(r["backend"] == "scripted" for r in rows)

    def colour(h: str) -> str:
        return "accent" if accent[h] else "ink"

    def fill(h: str) -> str:
        if accent[h]:
            return "url(#dense-accent)"
        return "url(#dense)" if h in thinking else "url(#dots)"

    def px(value: float) -> float:
        return X0 + (X1 - X0) * min(max(value, 0.0), goal) / goal

    # ---- heading
    s.text(24, 30, "Who got there", 16, "ink", SANS, "bold")
    state = "scripted: not a result" if scripted else kind
    s.caps(24, 46, f"{rows[0]['scenario']} · {state}")
    s.caps(WIDTH - 24, 30, rows[0]["date"], "grey", "end")
    s.line(24, 58, WIDTH - 24, 58)

    # ---- what was held equal
    models = sorted({r["model"] for r in rows if r["model"] != "none"}) or ["none"]
    commits = sorted({r["commit"][:7] for r in rows if r["commit"]}) or ["unrecorded"]
    span = f"{seeds[0]} to {seeds[-1]}" if len(seeds) > 1 else f"{seeds[0]}"
    facts = [
        ("model", ", ".join(models)),
        ("runs", f"{len(seeds)} each, seeds {span}"),
        ("budget", f"{max(r['budget_calls'] for r in rows)} calls a run"),
        ("commit", ", ".join(commits)),
    ]
    if reasons:
        facts.append(("not like for like", reasons[0]))
    cell = (WIDTH - 48) / max(len(facts), 4)
    for i, (name, value) in enumerate(facts):
        x = 24 + i * cell
        s.caps(x, 78, name)
        s.text(x, 96, value, 13, "ink", SANS, "bold")

    # ---- every run, as a bar along the way
    top = 136.0
    bar, gap = 5.0, 3.0
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

    # ---- what it cost
    ptop = bottom + 44
    height = 118.0
    s.text(24, ptop + 2, "Text sent", 12, "ink", SANS, "bold")
    sent = {h: statistics.median(r["chars"] for r in arms[h]) for h in thinking}
    if thinking:
        most = max(r["chars"] for h in thinking for r in arms[h]) or 1

        def py(value: float) -> float:
            return ptop + height - height * value / most

        s.line(X0, ptop + height, X1, ptop + height, 1.2)
        for h in sorted(thinking, key=lambda h: -sent[h]):
            best = min(arms[h], key=lambda r: abs(r["chars"] - sent[h]))
            points = steps.get((h, best["seed"]), [])
            if not points:
                continue
            d = f"M{X0:.1f},{ptop + height:.1f}"
            last = ptop + height
            for point in points:
                at, up = px(point["progress"] * goal), py(point["chars"])
                d += f" L{at:.1f},{last:.1f} L{at:.1f},{up:.1f}"
                last = up
            end = px(points[-1]["progress"] * goal)
            s.path(d + f" L{end:.1f},{ptop + height:.1f} Z", fill(h), "none")
            s.path(d.replace(f"M{X0:.1f},{ptop + height:.1f} L", "M", 1), "none", colour(h), 1.4)
            s.text(end + 5, last + 4, short(best["chars"]), 10, colour(h), SANS, "bold")
        if len(thinking) == 2 and any(accent[h] for h in thinking):
            ours = next(h for h in thinking if accent[h])
            other = next(h for h in thinking if h != ours)
            change = round(100 * (sent[ours] / sent[other] - 1)) if sent[other] else 0
            if change:
                s.text(24, ptop + 44, f"{abs(change)}%", 26, "accent", SANS, "bold")
                word = "less" if change < 0 else "more"
                s.text(24, ptop + 60, f"{word} than {other}", 8.5, "grey", SANS)

        # ---- seed by seed
        s.text(SIDE, ptop + 2, "Seed by seed", 12, "ink", SANS, "bold")
        room = WIDTH - 24 - SIDE - 22
        thick = min(7.0, (height - 16) / (len(seeds) * (len(thinking) + 0.6)))
        y = ptop + 18
        for seed in seeds:
            s.caps(SIDE, y + thick * len(thinking) / 2 + 3, seed)
            for h in thinking:
                r = next((r for r in arms[h] if r["seed"] == seed), None)
                if r is not None:
                    w = room * r["chars"] / most
                    s.box(SIDE + 14, y, max(w, 0.5), thick, fill(h), colour(h))
                    if r["ending"] != "reached":
                        end_mark(s, SIDE + 14 + w + 7, y + thick / 2, r["ending"], colour(h))
                y += thick
            y += thick * 0.6

    # ---- what it kept, the key and the stamp
    base = ptop + height + 30
    x = 24.0
    for h in order:
        if arms[h][0]["kept"] is not None:
            count = sum(r["kept"] or 0 for r in arms[h])
            s.text(x, base + 4, f"{count}", 14, colour(h), SANS, "bold")
            s.text(x + 16 + 8 * (len(str(count)) - 1), base + 4, "pages kept", 8.5, "grey", SANS)
            x += 110
    key = WIDTH - 24.0
    for word, ending in (("did not", "lost"), ("reached", "reached")):
        s.caps(key, base + 3, word, anchor="end")
        key -= len(word) * 5.7 + 8
        end_mark(s, key, base, ending, "ink")
        key -= 14
    s.caps(key, base + 3, "rule broken", anchor="end")
    key -= 11 * 5.7 + 6
    s.path(f"M{key - 2.5:.1f},{base + 3:.1f} h5 l-2.5,-4.5 Z", "mark", "none")
    return s.svg(
        base + 20,
        TITLE,
    )
