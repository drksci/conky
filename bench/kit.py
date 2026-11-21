"""The drawing kit for the benchmark charts: one Plotly template built on the shared tokens.

Every value is read from `src/conky/tokens.json`, the one token file; nothing here holds a
second copy. A chart is drawn black and white first: ink outlines and text, fills in ink, the
page, and the grey steps of `ramp.ink`, with a classic one-bit pattern only where two greys would
be hard to tell apart. Colour comes from the token file's `chart` section and only where it helps
the reader: the subject of a chart, or one notable thing.

A chart names a role (`subject`, `other`, `model`, `harness`, `idle`, `notable`, and the four
text sources), never a value; `fill(role, look)` gives the Plotly marker for it. Text is set in
the faces GitHub renders the page in (`embedded_text`), named once on the exported file's root.

Plotly and kaleido are optional (`pip install -e '.[bench]'`); `available()` says whether they
are installed, and nothing here imports them before a chart is drawn.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

TOKENS = json.loads(
    (Path(__file__).resolve().parent.parent / "src" / "conky" / "tokens.json").read_text(
        encoding="utf-8"
    )
)
GROUND = TOKENS["color"]
CHART = TOKENS["chart"]
SIZE = TOKENS["size"]
LOOKS = ("light", "dark")
WIDTH = 720  # the width a chart is shown at in the README, so a pixel here is a pixel there
FONT = SIZE["large"]  # 12 px: no text on a chart is smaller


def stack(kind: str) -> str:
    """A font-family list from a token stack."""
    return ", ".join(f'"{x}"' if " " in x else x for x in TOKENS["type"][kind])


TEXT = stack("embedded_text")


def palette(look: str) -> dict[str, str]:
    """Every colour a chart may use, by name, for one look: the ground, the ink ramp and the
    chart section (`subject`, `cat1` to `cat4`, `seq1` to `seq4`, `quiet`)."""
    ramp = {f"ramp{i}": v for i, v in enumerate(TOKENS["ramp"]["ink"][look], start=1)}
    chart = {"subject": CHART["subject"][look]}
    chart |= {f"cat{i}": c[look] for i, c in enumerate(CHART["categorical"], start=1)}
    chart |= {f"seq{i}": v for i, v in enumerate(CHART["sequential"][look], start=1)}
    ground = {k: v[look] for k, v in GROUND.items()} | ramp
    return ground | chart | {"quiet": ground[CHART["quiet"]]}


COLOURS = {v.lower() for look in LOOKS for v in palette(look).values()}

# What each role is drawn with: a paint by palette name, and a one-bit pattern or none. The
# same thing keeps the same treatment in every chart.
ROLES = {
    "subject": ("subject", ""),  # the harness a chart is about: the one spot colour
    "other": ("ramp2", ""),  # every other harness: grey
    "model": ("ramp2", ""),  # time or text in the model
    "harness": ("ink", ""),  # time in the harness itself
    "idle": ("paper", ""),  # nothing: an outline on the page
    "notable": ("cat1", ""),  # one thing worth seeing, such as a broken rule
    "task": ("ramp2", ""),  # text sources: the task, the screen, the scaffolding, the answer
    "screen": ("ramp3", ""),
    "scaffold": ("ink", ""),
    "answer": ("paper", "."),
}
PATTERN = {"size": 5, "solidity": 0.35}  # a dot screen that stays crisp at README width
GAP = 0.18  # the empty page between bars, as a share of a bar's slot


def colour(role: str, look: str) -> str:
    return palette(look)[ROLES[role][0]]


def fill(role: str, look: str) -> dict:
    """A Plotly bar marker for a role: a flat fill with a one-pixel ink outline, square."""
    c = palette(look)
    paint, shape = ROLES[role]
    marker = {"color": c[paint], "line": {"color": c["ink"], "width": 1}}
    if paint == "paper":
        marker["color"] = "rgba(0,0,0,0)"
    if shape:
        marker["pattern"] = {
            "shape": shape,
            "fgcolor": c["ink"],
            "bgcolor": "rgba(0,0,0,0)",
            "fillmode": "overlay",
            **PATTERN,
        }
    return marker


def available() -> bool:
    """Whether Plotly and kaleido are installed, so charts can be drawn and exported."""
    try:
        import kaleido  # noqa: F401
        import plotly  # noqa: F401
    except ImportError:
        return False
    return True


def template(look: str) -> dict:
    """The one template every chart is drawn with: transparent ground, ink text, no grid."""
    c = palette(look)
    axis = {
        "showgrid": False,
        "zeroline": False,
        "showline": False,
        "ticks": "",
        "color": c["ink"],
        "tickfont": {"size": FONT, "color": c["ink"]},
        "title": {"font": {"size": FONT, "color": c["ink"]}, "standoff": 6},
        "automargin": True,
    }
    return {
        "layout": {
            "paper_bgcolor": "rgba(0,0,0,0)",
            "plot_bgcolor": "rgba(0,0,0,0)",
            "font": {"family": TEXT, "size": FONT, "color": c["ink"]},
            "colorway": [c["subject"], c["ramp3"], c["ramp2"], c["ink"]],
            "xaxis": axis,
            "yaxis": axis,
            "bargap": GAP,
            "barmode": "stack",
            "showlegend": False,
            "legend": {
                "orientation": "h",
                "x": 0,
                "xanchor": "left",
                "y": 1.0,
                "yanchor": "bottom",
                "font": {"size": FONT, "color": c["ink"]},
                "bgcolor": "rgba(0,0,0,0)",
                "borderwidth": 0,
                "bordercolor": c["ink"],
                "itemsizing": "constant",
                "traceorder": "normal",
            },
            "margin": {"l": 4, "r": 4, "t": 4, "b": 4, "pad": 4},
            "width": WIDTH,
            "uniformtext": {"minsize": FONT, "mode": "hide"},
        },
        "data": {
            "bar": [{"marker": {"line": {"color": c["ink"], "width": 1}}}],
        },
    }


def figure(look: str, *traces, **layout):
    """A Plotly figure on the template; a chart passes only its data mapping."""
    import plotly.graph_objects as go

    fig = go.Figure(data=list(traces))
    fig.for_each_trace(lambda t: t.update(uid=f"t{fig.data.index(t)}"))  # stable, not random
    fig.update_layout(template=template(look), width=WIDTH)
    fig.update_layout(**layout)
    return fig


_RGB = re.compile(r"rgba?\((\d+), ?(\d+), ?(\d+)(?:, ?([\d.]+))?\)")
_FACE = re.compile(r"font-family: ?[^;\"]*;? ?")


def _hex(match: re.Match) -> str:
    r, g, b, alpha = match.groups()
    if alpha is not None and float(alpha) == 0:
        return "none"
    return f"#{int(r):02x}{int(g):02x}{int(b):02x}"


def tidy(svg: str, name: str) -> str:
    """Make an exported SVG stable and plain: Plotly's random ids replaced by the chart's name,
    colours written as hex, transparent paints as none, and the face named once on the root."""
    uid = re.search(r'id="defs-([0-9a-f]+)"', svg)
    if uid:
        svg = svg.replace(uid.group(1), name)
    found = dict.fromkeys(re.findall(r'id="[^"]*?-([0-9a-f]{6})"', svg))
    for n, mark in enumerate(found, start=1):  # pattern ids, numbered in order of appearance
        svg = re.sub(rf"-{mark}(?=[\")])", f"-{n}", svg)
    svg = re.sub(r"fill: ?rgb\(0, ?0, ?0\); ?fill-opacity: ?0;?", "fill: none;", svg)
    svg = re.sub(r'fill="rgb\(0, 0, 0\)" fill-opacity="0"', 'fill="none"', svg)
    svg = _RGB.sub(_hex, svg)
    svg = re.sub(r"stroke: #[0-9a-f]{6}; stroke-opacity: 0;", "stroke: none;", svg)
    svg = re.sub(r'<rect class="scrollbar"[^>]*/>', "", svg)  # a legend's empty scrollbar
    svg = _FACE.sub("", svg)
    head = svg.index(">", svg.index("<svg"))
    face = TEXT.replace('"', "&quot;")
    svg = svg[:head] + f' font-family="{face}"' + svg[head:]
    return svg if svg.endswith("\n") else svg + "\n"


def export(figures: dict[Path, tuple[object, str]]) -> list[Path]:
    """Write each figure as an SVG at its path, tidied; the name keys its ids."""
    import plotly.io as pio

    paths = list(figures)
    shown = [figures[p][0] for p in paths]
    pio.write_images(  # one browser for all; the size is given, or kaleido takes its default
        shown,
        paths,
        format="svg",
        width=[f.layout.width for f in shown],
        height=[f.layout.height for f in shown],
    )
    for path in paths:
        path.write_text(tidy(path.read_text(encoding="utf-8"), figures[path][1]), encoding="utf-8")
    return paths


SWATCHES = (
    ("subject", "subject"),
    ("cat1", "categorical 1, notable"),
    ("cat2", "categorical 2"),
    ("cat3", "categorical 3"),
    ("cat4", "categorical 4"),
    ("quiet", "quiet, other"),
    ("seq1", "sequential 1"),
    ("seq2", "sequential 2"),
    ("seq3", "sequential 3"),
)


def swatches(look: str) -> str:
    """The chart palette as a row of labelled squares, for the design page."""
    c = palette(look)
    face = TEXT.replace('"', "&quot;")
    each = WIDTH / len(SWATCHES)
    parts = []
    for i, (key, word) in enumerate(SWATCHES):
        x = i * each
        parts.append(
            f'<rect x="{x + 0.5:.1f}" y="0.5" width="{each - 8:.1f}" height="40" '
            f'fill="{c[key]}" stroke="{c["ink"]}" stroke-width="1"/>'
        )
        for k, line in enumerate(word.split(", ")):
            parts.append(
                f'<text x="{x:.1f}" y="{58 + 15 * k}" font-size="{FONT}" fill="{c["ink"]}">'
                f"{line}</text>"
            )
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="82" '
        f'viewBox="0 0 {WIDTH} 82" font-family="{face}" role="img" '
        f'aria-label="The chart palette, light and dark">\n' + "\n".join(parts) + "\n</svg>\n"
    )


SWATCH_FILE = Path(__file__).resolve().parent.parent / "docs" / "reference" / "chart-palette"


def main() -> None:
    """Write the palette swatches beside the design page: `python -m bench.kit`."""
    for look in LOOKS:
        path = SWATCH_FILE.with_name(f"{SWATCH_FILE.name}.{look}.svg")
        path.write_text(swatches(look), encoding="utf-8")
        print(path)


if __name__ == "__main__":
    main()
