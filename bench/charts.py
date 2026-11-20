"""Draw a benchmark results directory as six SVG charts, with the data behind them.

    python -m bench.charts RESULTS_DIR --out DIR

Writes `trail`, `progress`, `spend`, `where`, `rules` and `board`, each as `NAME.light.svg` (ink on
transparent, for light pages) and `NAME.dark.svg`. One ink, one yellow accent (the Conky row of
`trail`, and `rules`), arms told apart by line style and direct labels. Every chart carries, bottom
right, `DATA` or `SCRIPTED: NOT A RESULT` from the runs' backend, and bottom left the scenario,
model, seeds and date. Beside them it writes `runs.csv` and `runs.json`, one row per run, so the
same data can be drawn another way. It reads the run files (run.json, meter.jsonl,
transcript.jsonl) that bench.run writes. Standard library only.
"""

from __future__ import annotations

import argparse
import csv
import json
import statistics
import sys
from dataclasses import dataclass, field
from pathlib import Path
from xml.sax.saxutils import escape

from bench.envs import textenv
from bench.envs.oregon_trail_1975 import parse
from bench.scenarios.trail import score

WIDTH = 880
GOAL = score.GOAL_MILES
YELLOW = "#F4C430"
INKS = {"light": "#1E1E1E", "dark": "#EDEDED"}
FONT = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"
DASHES = ("", "7 3", "1.5 3", "7 3 1.5 3")
BUDGET_EXITS = ("budget-exhausted", "wall-clock", "stalled")
LAYERS = (
    ("task", "TASK TEXT"),
    ("screen", "SCREEN"),
    ("scaffold", "SCAFFOLDING"),
    ("other", "OTHER"),
)


@dataclass
class Run:
    """One run, as plain turn-indexed series read from its files."""

    arm: str
    seed: int
    backend: str
    model: str
    scenario: str
    date: str
    budget_calls: int
    ending: str  # arrived, lost, budget, crashed or the raw exit
    turns: int
    miles: float
    left: dict[int, float]  # turn -> miles left to the goal, at the end of that turn
    calls: list[dict] = field(default_factory=list)  # turn, bytes by layer, chars, tokens
    breaks: list[tuple[int, str]] = field(default_factory=list)
    proposed: list[tuple[int, str]] = field(default_factory=list)
    wall: float = 0.0
    tokens_known: bool = True


def _jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x]


def load_run(folder: Path) -> Run:
    record = json.loads((folder / "run.json").read_text(encoding="utf-8"))
    events = textenv.read(folder / "transcript.jsonl")
    decisions, _, ended = parse.walk(events)
    decisions = [d for d in decisions if d.get("by") != "opening"]
    found = score.outcome(events)
    at = {e["n"]: e["t"] for e in events if e["kind"] == "in"}
    times = [(at.get(d["n"], 0.0), d["state"]["turn"]) for d in decisions]
    arrived = found["arrived"]
    miles = float(GOAL if arrived else found["mileage"])
    left: dict[int, float] = {}
    for d in decisions:
        left[d["state"]["turn"]] = max(0.0, GOAL - float(d["state"]["mileage"] or 0))
    left[found["turns"]] = 0.0 if arrived else max(0.0, GOAL - miles)
    exit_ = record.get("exit") or ""
    if arrived:
        ending = "arrived"
    elif ended.get("outcome") == "crashed" or exit_ == "crashed":
        ending = "crashed"
    elif exit_ in BUDGET_EXITS:
        ending = "budget"
    elif found["outcome"] == "died":
        ending = "lost"
    else:
        ending = exit_ or found["outcome"]
    calls = []
    proposed = []
    for c in _jsonl(folder / "meter.jsonl"):
        if c.get("status") != 200:
            continue
        # a call belongs to the turn of the decision its answer was typed for
        later = [turn for t, turn in times if t >= c["t_start"]]
        turn = later[0] if later else (times[-1][1] if times else 0)
        known = bool(c.get("tokens_known"))
        calls.append(
            {
                "turn": turn,
                "task": c.get("pack_bytes", 0),
                "screen": c.get("screen_bytes", 0),
                "scaffold": c.get("scaffold_bytes", 0),
                "other": c.get("image_bytes", 0),
                "chars": c.get("chars_in", 0) + c.get("chars_out", 0),
                "tokens": (c.get("tokens_in") or 0) + (c.get("tokens_out") or 0),
                "tokens_known": known,
            }
        )
        if (c.get("note") or {}).get("proposed"):
            proposed.append((turn, c["note"]["proposed"]))
    breaks = [(v["turn"], v["rule"]) for v in score.violations(decisions)]
    start = record.get("start", "")
    return Run(
        arm=record["arm"],
        seed=record["seed"],
        backend=record.get("backend", "?"),
        model=record.get("model", "?"),
        scenario=record.get("scenario", "?"),
        date=start[:10],
        budget_calls=(record.get("budget") or {}).get("calls", 0),
        ending=ending,
        turns=found["turns"],
        miles=miles,
        left=left,
        calls=calls,
        breaks=breaks,
        proposed=proposed,
        wall=sum(s["end"] - s["start"] for s in record.get("segments", []) if "end" in s),
        tokens_known=all(c["tokens_known"] for c in calls),
    )


def load(results: Path) -> list[Run]:
    return [load_run(p.parent) for p in sorted(results.rglob("run.json"))]


def by_arm(runs: list[Run]) -> dict[str, list[Run]]:
    arms: dict[str, list[Run]] = {}
    for run in runs:
        arms.setdefault(run.arm, []).append(run)
    return {arm: sorted(rs, key=lambda r: r.seed) for arm, rs in sorted(arms.items())}


def cumulative(run: Run, turn: int, key: str) -> float:
    """Total of a call measure over the calls made up to the end of this turn."""
    if key == "calls":
        return float(sum(1 for c in run.calls if c["turn"] <= turn))
    return float(sum(c[key] for c in run.calls if c["turn"] <= turn))


def band(runs: list[Run], value) -> list[tuple[int, float, float, float]]:
    """Per turn: (turn, median, lowest, highest) over the runs still going at that turn."""
    out = []
    for turn in range(max((r.turns for r in runs), default=0) + 1):
        values = [value(r, turn) for r in runs if turn <= r.turns]
        if values:
            out.append((turn, statistics.median(values), min(values), max(values)))
    return out


def total(run: Run, key: str) -> float:
    return float(sum(c[key] for c in run.calls))


def left_at(run: Run, turn: int) -> float:
    known = [t for t in run.left if t <= turn]
    return run.left[max(known)] if known else float(GOAL)


# ---------------------------------------------------------------- drawing


class Canvas:
    def __init__(self, height: int, ink: str) -> None:
        self.height = height
        self.ink = ink
        self.parts: list[str] = []

    def add(self, text: str) -> None:
        self.parts.append(text)

    def line(self, x1, y1, x2, y2, width=1.0, dash="", opacity=1.0, color=None) -> None:
        extra = f' stroke-dasharray="{dash}"' if dash else ""
        self.add(
            f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color or self.ink}" stroke-width="{width}" opacity="{opacity}"{extra}/>'
        )

    def path(self, points, width=1.5, dash="", opacity=1.0, fill="none", close=False) -> None:
        if not points:
            return
        d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in points) + (" Z" if close else "")
        extra = f' stroke-dasharray="{dash}"' if dash else ""
        stroke = "none" if fill != "none" else self.ink
        self.add(
            f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{width}" '
            f'opacity="{opacity}" stroke-linejoin="round"{extra}/>'
        )

    def text(
        self, x, y, s, size=10, anchor="start", opacity=1.0, weight="normal", fill=None
    ) -> None:
        self.add(
            f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" text-anchor="{anchor}" '
            f'opacity="{opacity}" font-weight="{weight}" fill="{fill or self.ink}">'
            f"{escape(s)}</text>"
        )

    def rect(self, x, y, w, h, fill="none", opacity=1.0, stroke="none", sw=1.0) -> None:
        self.add(
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{max(w, 0):.1f}" height="{max(h, 0):.1f}" '
            f'fill="{fill}" opacity="{opacity}" stroke="{stroke}" stroke-width="{sw}"/>'
        )

    def circle(self, x, y, r, fill="none", sw=1.2, opacity=1.0) -> None:
        self.add(
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{fill}" stroke="{self.ink}" '
            f'stroke-width="{sw}" opacity="{opacity}"/>'
        )

    def svg(self, title: str) -> str:
        head = (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{self.height}" '
            f'viewBox="0 0 {WIDTH} {self.height}" font-family="{FONT}" '
            f'stroke-linecap="round" letter-spacing=".06em" role="img" '
            f'aria-label="{escape(title)}">\n<title>{escape(title)}</title>\n'
        )
        return head + "\n".join(self.parts) + "\n</svg>\n"


def stamp(runs: list[Run]) -> tuple[str, str]:
    """The footer: scenario, model, seeds and date on the left; the data class on the right."""
    seeds = sorted({r.seed for r in runs})
    span = f"{seeds[0]}-{seeds[-1]}" if len(seeds) > 1 else f"{seeds[0]}"
    models = ",".join(sorted({r.model for r in runs}))
    date = max(r.date for r in runs)
    left = f"{runs[0].scenario} / model {models} / seeds {span} / {date}"
    stand_in = any(r.backend == "scripted" for r in runs)
    return left, ("SCRIPTED: NOT A RESULT" if stand_in else "DATA")


def frame(height: int, ink: str, title: str, subtitle: str, runs: list[Run]) -> Canvas:
    c = Canvas(height, ink)
    c.text(24, 26, title.upper(), 13, weight="bold")
    c.text(24, 43, subtitle, 10, opacity=0.65)
    left, right = stamp(runs)
    c.line(24, height - 28, WIDTH - 24, height - 28, 0.6, opacity=0.35)
    c.text(24, height - 12, left, 9, opacity=0.65)
    c.text(WIDTH - 24, height - 12, right, 9, anchor="end", weight="bold")
    return c


def nice(top: float) -> float:
    """A round axis top at or above top."""
    if top <= 0:
        return 1.0
    mag = 10 ** (len(str(int(top))) - 1)
    for step in (1, 2, 2.5, 5, 10):
        if step * mag >= top:
            return step * mag
    return 10 * mag


def axes(
    c: Canvas, x0, x1, y0, y1, xmax, ymax, ylabel, xlabel=None, ticks=None, fmt="{:,.0f}"
) -> None:
    """Thin axes with faint ticks. y0 is the top of the plot, y1 the bottom."""
    c.line(x0, y1, x1, y1, 0.8)
    c.line(x0, y0, x0, y1, 0.8)
    for value in ticks or round_ticks(ymax):
        y = y1 - (y1 - y0) * value / ymax
        c.line(x0 - 3, y, x1, y, 0.5, opacity=0.18)
        c.text(x0 - 7, y + 3, fmt.format(value), 9, anchor="end", opacity=0.7)
    step = 1 if xmax <= 16 else 2 if xmax <= 32 else 5
    for t in range(0, int(xmax) + 1, step):
        x = x0 + (x1 - x0) * t / xmax
        c.line(x, y1, x, y1 + 3, 0.8)
        c.text(x, y1 + 14, str(t), 9, anchor="middle", opacity=0.7)
    c.text(x0, y0 - 8, ylabel.upper(), 9, opacity=0.8)
    if xlabel:
        c.text(x1, y1 + 27, xlabel.upper(), 9, anchor="end", opacity=0.8)


def round_ticks(top: float) -> list[float]:
    """Five ticks for a top of 25 or 5 times a power of ten, four otherwise."""
    lead = top / 10 ** (len(str(int(top))) - 1)
    n = 5 if lead in (2.5, 5) else 4
    return [top * i / n for i in range(n + 1)]


def dodge(ys: list[float], gap: float, low: float, high: float) -> list[float]:
    """Spread label positions so none are closer than gap, keeping order and the bounds."""
    order = sorted(range(len(ys)), key=lambda i: ys[i])
    placed: dict[int, float] = {}
    last = low - gap
    for i in order:
        last = max(ys[i], last + gap)
        placed[i] = last
    over = last - high
    if over > 0:
        for i in order:
            placed[i] -= over
    return [placed[i] for i in range(len(ys))]


def mark(c: Canvas, x, y, ending: str) -> None:
    """The small mark that says why a run ended."""
    if ending == "arrived":
        c.circle(x, y, 3.2)
    elif ending == "lost":
        c.line(x - 3, y - 3, x + 3, y + 3, 1.4)
        c.line(x - 3, y + 3, x + 3, y - 3, 1.4)
    elif ending == "budget":
        c.line(x, y - 4, x, y + 4, 1.6)
        c.line(x - 3, y - 4, x + 3, y - 4, 1.6)
    else:
        c.text(x, y + 4, "!", 11, anchor="middle", weight="bold")


MARK_KEY = "ENDS: o ARRIVED  x LOST  T BUDGET  ! CRASHED"


def line_chart(c, arms, box, xmax, ymax, value, label, ends=False) -> None:
    """Median line with a min-to-max band per arm, labelled where its own line ends."""
    x0, x1, y0, y1 = box

    def px(t):
        return x0 + (x1 - x0) * t / xmax

    def py(v):
        return y1 - (y1 - y0) * min(v, ymax) / ymax

    spots = []
    for i, runs in enumerate(arms.values()):
        rows = band(runs, value)
        top = [(px(t), py(hi)) for t, _, _, hi in rows]
        bottom = [(px(t), py(lo)) for t, _, lo, _ in reversed(rows)]
        c.path(top + bottom, fill=c.ink, opacity=0.1, width=0, close=True)
        c.path([(px(t), py(m)) for t, m, _, _ in rows], 1.6, DASHES[i % len(DASHES)])
        if ends:
            for run in runs:
                mark(c, px(run.turns), py(value(run, run.turns)), run.ending)
        spots.append((px(rows[-1][0]), py(rows[-1][1])) if rows else (x0, y1))
    height = dodge([y for _, y in spots], 13, y0 + 4, y1 + 8)
    for (x, y), at, (name, runs) in zip(spots, height, arms.items(), strict=True):
        c.line(x + (6 if ends else 3), y, x1 + 6, at, 0.6, "1 2", 0.6)
        c.text(x1 + 10, at + 3, label(name, runs), 10, weight="bold")


def draw_progress(runs: list[Run], ink: str) -> Canvas:
    arms = by_arm(runs)
    c = frame(
        340,
        ink,
        "Progress: miles left to Oregon",
        "MEDIAN OF SEEDS, BAND LOWEST TO HIGHEST  |  " + MARK_KEY,
        runs,
    )
    x0, x1, y0, y1 = 70, 690, 78, 280
    xmax = max(max(r.turns for r in rs) for rs in arms.values()) or 1
    axes(c, x0, x1, y0, y1, xmax, GOAL, "miles left", "turn", [0, 500, 1000, 1500, GOAL])
    line_chart(
        c,
        arms,
        (x0, x1, y0, y1),
        xmax,
        GOAL,
        left_at,
        lambda name, rs: f"{name} {sum(r.ending == 'arrived' for r in rs)}/{len(rs)} arrived",
        ends=True,
    )
    return c


def draw_spend(runs: list[Run], ink: str) -> Canvas:
    arms = by_arm(runs)
    c = frame(
        470,
        ink,
        "Spend: model calls and tokens",
        "CUMULATIVE, MEDIAN OF SEEDS, BAND LOWEST TO HIGHEST",
        runs,
    )
    x0, x1 = 70, 690
    xmax = max(max(r.turns for r in rs) for rs in arms.values()) or 1
    budget = max(r.budget_calls for r in runs)
    most = max((len(r.calls) for r in runs), default=0)
    off = budget > 2.5 * max(most, 1)
    ymax = nice(most * 1.15) if off or not budget else nice(budget)
    y0, y1 = 78, 245
    axes(c, x0, x1, y0, y1, xmax, ymax, "model calls")
    if budget:
        yb = y0 if off else y1 - (y1 - y0) * budget / ymax
        c.line(x0, yb, x1, yb, 1.2, "2 3")
        c.text(x1 + 8, yb + 3, f"BUDGET {budget}" + (" (OFF SCALE)" if off else ""), 9, opacity=0.8)
    line_chart(
        c,
        arms,
        (x0, x1, y0, y1),
        xmax,
        ymax,
        lambda r, t: cumulative(r, t, "calls"),
        lambda name, rs: f"{name} {statistics.median(len(r.calls) for r in rs):,.0f}",
    )
    known = all(r.tokens_known for r in runs if r.calls)
    key = "tokens" if known else "chars"
    top = max((total(r, key) for r in runs), default=0)
    ymax2 = nice(top * 1.05) if top else 1.0
    y2, y3 = 305, 410
    axes(
        c,
        x0,
        x1,
        y2,
        y3,
        xmax,
        ymax2,
        "tokens" if known else "characters sent and received (tokens unknown)",
        "turn",
    )
    line_chart(
        c,
        arms,
        (x0, x1, y2, y3),
        xmax,
        ymax2,
        lambda r, t: cumulative(r, t, key),
        lambda name, rs: f"{name} {statistics.median(total(r, key) for r in rs):,.0f}",
    )
    return c


def median_run(runs: list[Run]) -> Run:
    """The run whose total bytes sent is the median of the arm's seeds."""

    def total(r: Run) -> int:
        return sum(sum(c[k] for k, _ in LAYERS) for c in r.calls)

    ordered = sorted(runs, key=total)
    return ordered[(len(ordered) - 1) // 2]


def draw_where(runs: list[Run], ink: str) -> Canvas:
    arms = by_arm(runs)
    picks = {arm: median_run(rs) for arm, rs in arms.items()}
    c = frame(
        380,
        ink,
        "Where the bytes go",
        "BYTES SENT PER CALL, ONE MEDIAN RUN PER ARM, SHARED SCALE",
        runs,
    )
    top = max(
        (sum(call[k] for k, _ in LAYERS) for r in picks.values() for call in r.calls), default=0
    )
    ymax = nice(top * 1.05) if top else 1.0
    gap, left, right = 22, 70, 740
    width = (right - left - gap * (len(arms) - 1)) / len(arms)
    y0, y1 = 82, 310
    fills = (1.0, 0.5, 0.2, 0.0)
    for i, (arm, run) in enumerate(picks.items()):
        x0 = left + i * (width + gap)
        c.line(x0, y1, x0 + width, y1, 0.8)
        c.text(x0, y0 - 14, arm.upper(), 10, weight="bold")
        c.text(x0, y0 - 3, f"seed {run.seed}, {len(run.calls)} calls", 9, opacity=0.65)
        if i == 0:
            c.line(x0, y0, x0, y1, 0.8)
            for k in range(5):
                y = y1 - (y1 - y0) * k / 4
                c.line(x0 - 3, y, x0 + width * 0 + 3, y, 0.8)
                c.text(x0 - 7, y + 3, f"{ymax * k / 4:,.0f}", 9, anchor="end", opacity=0.7)
        if not run.calls:
            c.text(x0 + width / 2, (y0 + y1) / 2, "NO MODEL CALLS", 9, anchor="middle", opacity=0.6)
            continue
        bar = width / max(len(run.calls), 1)
        for n, call in enumerate(run.calls):
            base = y1
            for (key, _), op in zip(LAYERS, fills, strict=True):
                h = (y1 - y0) * call[key] / ymax
                if h > 0:
                    c.rect(
                        x0 + n * bar,
                        base - h,
                        max(bar - 0.8, 0.8),
                        h,
                        c.ink,
                        op if op else 0.0,
                        stroke=c.ink if op < 0.3 else "none",
                        sw=0.5,
                    )
                base -= h
    mean = (
        {
            k: statistics.fmean(call[k] for r in picks.values() for call in r.calls)
            for k, _ in LAYERS
        }
        if top
        else {}
    )
    if mean:
        kx, base = right + 24, y1
        for (key, name), op in zip(LAYERS, fills, strict=True):
            h = (y1 - y0) * mean[key] / ymax
            c.rect(kx, base - h, 14, h, c.ink, op, stroke=c.ink if op < 0.3 else "none", sw=0.5)
            if mean[key] > 0:
                c.text(kx + 20, base - h / 2 + 3, name, 9)
            base -= h
        c.text(kx, y1 + 14, "MEAN CALL", 9, opacity=0.7)
    c.text(left, y1 + 16, "CALL, IN ORDER", 9, opacity=0.7)
    return c


def draw_rules(runs: list[Run], ink: str) -> Canvas:
    arms = by_arm(runs)
    rows = sum(len(rs) for rs in arms.values())
    height = 110 + rows * 16 + len(arms) * 14 + 30
    c = frame(
        height,
        ink,
        "Rules broken",
        "FILLED: HOUSE RULE BROKEN IN THE GAME  |  HOLLOW: BREAKING INPUT PROPOSED, NOT TYPED",
        runs,
    )
    x0, x1 = 200, 760
    xmax = max(max(r.turns for r in rs) for rs in arms.values()) or 1
    y = 70
    for arm, rs in arms.items():
        c.text(24, y + 11, arm.upper(), 10, weight="bold")
        total = sum(len(r.breaks) for r in rs)
        c.text(WIDTH - 24, y + 11, f"{total} broken", 10, anchor="end", weight="bold")
        for r in rs:
            c.text(x0 - 10, y + 12, f"seed {r.seed}", 9, anchor="end", opacity=0.65)
            c.line(x0, y + 8, x0 + (x1 - x0) * r.turns / xmax, y + 8, 0.8, opacity=0.5)
            typed = set(r.breaks)
            for t, _ in r.breaks:
                x = x0 + (x1 - x0) * t / xmax
                c.rect(x - 1.5, y, 3, 16, YELLOW, stroke=c.ink, sw=0.5)
            for t, rule in r.proposed:
                if (t, rule) not in typed:
                    x = x0 + (x1 - x0) * t / xmax
                    c.rect(x - 2, y + 1, 4, 14, "none", stroke=YELLOW, sw=1.4)
            y += 16
        y += 14
    c.line(x0, y - 6, x1, y - 6, 0.8)
    step = 1 if xmax <= 16 else 2
    for t in range(0, int(xmax) + 1, step):
        x = x0 + (x1 - x0) * t / xmax
        c.line(x, y - 6, x, y - 3, 0.8)
        c.text(x, y + 6, str(t), 9, anchor="middle", opacity=0.7)
    c.text(x1, y + 18, "TURN", 9, anchor="end", opacity=0.8)
    return c


COLUMNS = (
    # key, header, best direction
    ("outcome", "ARRIVED", "high"),
    ("miles", "MILES", "high"),
    ("turns", "TURNS", "low"),
    ("calls", "CALLS", "low"),
    ("tokens", "TOKENS", "low"),
    ("wall", "WALL S", "low"),
    ("broken", "RULES BROKEN", "low"),
)


def board_values(rs: list[Run]) -> dict[str, list[float]]:
    known = all(r.tokens_known for r in rs if r.calls)
    return {
        "outcome": [1.0 if r.ending == "arrived" else 0.0 for r in rs],
        "miles": [r.miles for r in rs],
        "turns": [float(r.turns) for r in rs],
        "calls": [float(len(r.calls)) for r in rs],
        "tokens": [float(sum(c["tokens" if known else "chars"] for c in r.calls)) for r in rs],
        "wall": [r.wall for r in rs],
        "broken": [float(len(r.breaks)) for r in rs],
    }


def draw_board(runs: list[Run], ink: str) -> Canvas:
    arms = by_arm(runs)
    data = {arm: board_values(rs) for arm, rs in arms.items()}
    known = all(r.tokens_known for r in runs if r.calls)
    height = 100 + 46 * len(arms) + 30
    c = frame(
        height,
        ink,
        "Scoreboard",
        "DOT: MEDIAN, LINE: LOWEST TO HIGHEST SEED, RING: BEST ARM, EACH COLUMN ON ITS OWN SCALE",
        runs,
    )
    left, colw = 24, (WIDTH - 24 - 150 - 24) / len(COLUMNS)
    top = 66
    best: dict[str, float | None] = {}
    for key, _, direction in COLUMNS:
        pool = [
            statistics.median(d[key])
            for arm, d in data.items()
            if not (key == "turns" and not any(data[arm]["outcome"]))
        ]
        best[key] = (max(pool) if direction == "high" else min(pool)) if pool else None
    for j, (key, head, _) in enumerate(COLUMNS):
        x = 150 + j * colw
        title = "CHARS" if key == "tokens" and not known else head
        c.text(x + 6, top, title, 9, weight="bold")
    for i, (arm, d) in enumerate(data.items()):
        y = top + 16 + i * 46
        c.line(left, y - 6, WIDTH - 24, y - 6, 0.5, opacity=0.2)
        c.text(left, y + 18, arm.upper(), 10, weight="bold")
        for j, (key, _, _) in enumerate(COLUMNS):
            x = 150 + j * colw + 6
            w = colw - 22
            vals = d[key]
            med = statistics.median(vals)
            if key == "outcome":
                n = len(vals)
                gap = min(11.0, w / max(n, 1))
                for k in range(n):
                    c.circle(x + 4 + k * gap, y + 10, 3.6, c.ink if vals[k] else "none", 1.2)
                c.text(x, y + 30, f"{int(sum(vals))} OF {n}", 9, opacity=0.8)
                if sum(vals) and med == best[key]:
                    c.rect(x - 4, y + 21, 46, 12, "none", stroke=c.ink, sw=0.9)
                continue
            cap = (
                float(GOAL)
                if key == "miles"
                else max(max(x_ for x_ in dd[key]) for dd in data.values()) or 1.0
            )

            def px(v, x=x, w=w, cap=cap):
                return x + w * min(v, cap) / cap

            c.line(x, y + 10, x + w, y + 10, 0.5, opacity=0.25)
            c.line(px(min(vals)), y + 10, px(max(vals)), y + 10, 1.4)
            c.circle(px(med), y + 10, 3.6, c.ink, 1.2)
            if best[key] is not None and med == best[key]:
                c.circle(px(med), y + 10, 7.5, "none", 0.9)
            c.text(
                x,
                y + 30,
                f"{med:,.0f}" if med >= 10 or med == int(med) else f"{med:.1f}",
                9,
                opacity=0.8,
            )
    return c


GLOSS = {
    "floor-continue": "always presses continue",
    "floor-random": "presses keys at random",
    "loop": "one model in a plain loop",
    "cli": "a stock agent CLI, unmetered",
    "conky": "one character in a vault",
}


def draw_trail(runs: list[Run], ink: str) -> Canvas:
    """The one-glance chart: each run is a mark on the road, placed where it ended."""
    arms = by_arm(runs)
    order = [a for a in GLOSS if a in arms] + [a for a in arms if a not in GLOSS]
    row = 52
    height = 96 + row * len(order) + 40
    c = frame(
        height,
        ink,
        "Who reached Oregon",
        "ONE MARK PER RUN, PLACED WHERE IT ENDED | LINE: MEDIAN | " + MARK_KEY,
        runs,
    )
    x0, x1, top = 232, WIDTH - 280, 84
    cols = ((WIDTH - 196, "ARRIVED"), (WIDTH - 110, "MODEL CALLS"), (WIDTH - 24, "RULES BROKEN"))

    def px(miles: float) -> float:
        return x0 + (x1 - x0) * min(max(miles, 0.0), GOAL) / GOAL

    for x, head in cols:
        c.text(x, top - 14, head, 8, anchor="end", opacity=0.65)
    c.text(x0, top - 14, "INDEPENDENCE", 8, opacity=0.65)
    c.text(x1, top - 14, "OREGON", 8, anchor="end", opacity=0.65)
    bottom = top + row * len(order)
    for miles in (0, 500, 1000, 1500, GOAL):
        c.line(px(miles), top - 6, px(miles), bottom - 8, 0.5, dash="1 4", opacity=0.35)
        c.text(px(miles), bottom + 6, f"{miles:,}", 8, anchor="middle", opacity=0.65)
    c.text((x0 + x1) / 2, bottom + 20, "MILES", 8, anchor="middle", opacity=0.5)
    for i, arm in enumerate(order):
        rs = arms[arm]
        y = top + 18 + i * row
        accent = YELLOW if arm == "conky" else None
        c.text(24, y - 1, arm.upper(), 11, weight="bold", fill=accent)
        c.text(24, y + 13, GLOSS.get(arm, ""), 9, opacity=0.65)
        c.line(x0, y, x1, y, 0.6, opacity=0.25)
        c.line(x0, y, px(statistics.median(r.miles for r in rs)), y, 2.2, color=accent)
        spread = 9.0 if len(rs) > 1 else 0.0
        for k, r in enumerate(rs):
            dy = (k - (len(rs) - 1) / 2) * spread / max(len(rs) - 1, 1) * 2
            mark(c, px(r.miles), y + dy, r.ending)
        arrived = sum(r.ending == "arrived" for r in rs)
        calls = statistics.median(len(r.calls) for r in rs)
        broken = statistics.median(len(r.breaks) for r in rs)
        values = (f"{arrived} of {len(rs)}", f"{calls:,.0f}", f"{broken:,.0f}")
        for (x, _), value in zip(cols, values, strict=True):
            c.text(x, y + 4, value, 11, anchor="end", weight="bold", fill=accent)
    return c


CHARTS = {
    "trail": draw_trail,
    "progress": draw_progress,
    "spend": draw_spend,
    "where": draw_where,
    "rules": draw_rules,
    "board": draw_board,
}

TITLES = {
    "trail": "Where each run ended on the road to Oregon, one row per arm",
    "progress": "Miles left to Oregon against turn, one line per arm",
    "spend": "Cumulative model calls and tokens against turn, one line per arm",
    "where": "Bytes sent per call, split by source, one median run per arm",
    "rules": "House rules broken in the game, by turn, per run",
    "board": "Scoreboard, one row per arm",
}


def render(runs: list[Run], out: Path) -> list[Path]:
    out.mkdir(parents=True, exist_ok=True)
    written = []
    for name, draw in CHARTS.items():
        for look, ink in INKS.items():
            path = out / f"{name}.{look}.svg"
            path.write_text(draw(runs, ink).svg(TITLES[name]), encoding="utf-8")
            written.append(path)
    written += export(runs, out)
    return written


FIELDS = (
    "scenario",
    "arm",
    "seed",
    "model",
    "backend",
    "date",
    "ending",
    "miles",
    "turns",
    "model_calls",
    "tokens",
    "chars",
    "wall_s",
    "rules_broken",
)


def rows(runs: list[Run]) -> list[dict]:
    """One plain row per run: everything the charts draw, so they can be drawn another way."""
    return [
        {
            "scenario": r.scenario,
            "arm": r.arm,
            "seed": r.seed,
            "model": r.model,
            "backend": r.backend,
            "date": r.date,
            "ending": r.ending,
            "miles": round(r.miles, 1),
            "turns": r.turns,
            "model_calls": len(r.calls),
            "tokens": sum(c["tokens"] for c in r.calls) if r.tokens_known else None,
            "chars": sum(c["chars"] for c in r.calls),
            "wall_s": round(r.wall, 1),
            "rules_broken": len(r.breaks),
        }
        for r in sorted(runs, key=lambda r: (r.arm, r.seed))
    ]


def export(runs: list[Run], out: Path) -> list[Path]:
    """Write the data behind the charts as `runs.csv` and `runs.json`."""
    data = rows(runs)
    table = out / "runs.csv"
    with table.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(data)
    tree = out / "runs.json"
    tree.write_text(json.dumps(data, indent=1) + "\n", encoding="utf-8")
    return [table, tree]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="bench.charts", description=__doc__.split("\n")[0])
    parser.add_argument("results", type=Path, help="a results directory written by bench.run")
    parser.add_argument("--out", type=Path, required=True, help="where to write the SVG files")
    args = parser.parse_args(argv)
    runs = load(args.results)
    if not runs:
        print(
            f"no runs under {args.results}: run bench.run first, or point at its --out",
            file=sys.stderr,
        )
        return 1
    for path in render(runs, args.out):
        print(path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
