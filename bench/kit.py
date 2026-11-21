"""The drawing kit for the benchmark charts: the Minty templates, with monochrome words.

A chart is drawn with the Minty figure templates from `dash-bootstrap-templates`: `minty` (the
light file) and `minty_dark` (the dark file), in Plotly's default style for its chart type. The
colours of the marks, the layout, the legends and the text sizes are the template's. One small
overlay a look is added on top so a chart sits on a README page in either mode: a transparent
ground, so the page's own colour shows, the faces GitHub renders the page in
(`type.embedded_text` in `src/conky/tokens.json`; the template's own first face is not on a
reader's machine), tight margins, no outline on a bar, and everything that is not a data mark
in one neutral: all text and the goal line in the look's `color.ink`, and axis lines, ticks and
grid in its `color.mute`. Colour is carried only by the marks, and it is the template's.

Plotly, kaleido and the templates are optional (`pip install -e '.[bench]'`); `available()` says
whether they are installed, and nothing here imports them before a chart is drawn.
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
LOOKS = ("light", "dark")
THEMES = {"light": "minty", "dark": "minty_dark"}
WIDTH = 720  # the width a chart is shown at in the README, so a pixel here is a pixel there


def stack(kind: str) -> str:
    """A font-family list from a token stack."""
    return ", ".join(f'"{x}"' if " " in x else x for x in TOKENS["type"][kind])


TEXT = stack("embedded_text")
INK = TOKENS["color"]["ink"]  # every word on a chart, by look
RULE = TOKENS["color"]["mute"]  # every axis line, tick and gridline, by look


def overlay(look: str) -> dict:
    """What is laid over a look's template: the page's ground and face, and one neutral for
    the words and one for the rules, so that only the marks carry colour; a bar has no outline."""
    ink, rule = INK[look], RULE[look]
    axis = {"gridcolor": rule, "linecolor": rule, "zerolinecolor": rule, "tickcolor": rule}
    return {
        "layout": {
            "paper_bgcolor": "rgba(0,0,0,0)",
            "plot_bgcolor": "rgba(0,0,0,0)",
            "font": {"family": TEXT, "color": ink},
            "margin": {"l": 8, "r": 8, "t": 8, "b": 8},
            "xaxis": axis,
            "yaxis": axis,
            "annotationdefaults": {"font": {"color": ink}, "arrowcolor": ink},
            "shapedefaults": {"line": {"color": ink}},
        },
        "data": {"bar": [{"marker": {"line": {"width": 0}}}]},
    }


def available() -> bool:
    """Whether Plotly, kaleido and the templates are installed, so charts can be drawn."""
    try:
        import dash_bootstrap_templates  # noqa: F401
        import kaleido  # noqa: F401
        import plotly  # noqa: F401
    except ImportError:
        return False
    return True


def template(look: str) -> str:
    """The name of the template for a look: its Minty template with the overlay on top."""
    import plotly.io as pio

    if f"conky-{look}" not in pio.templates:
        from dash_bootstrap_templates import load_figure_template

        default = pio.templates.default
        load_figure_template(list(THEMES.values()))  # registers both, and takes the default
        pio.templates.default = default
        for each in LOOKS:
            pio.templates[f"conky-{each}"] = overlay(each)
    return f"{THEMES[look]}+conky-{look}"


def finish(fig, height: int, **layout):
    """Give a figure the export height and a stable id a trace, so the same data gives the same
    bytes; a chart passes only what its type needs to be correct."""
    fig.for_each_trace(lambda t: t.update(uid=f"t{fig.data.index(t)}"))
    fig.update_layout(width=WIDTH, height=height, **layout)
    return fig


_FACE = re.compile(r"font-family: ?[^;\"]*;? ?")


def tidy(svg: str, name: str) -> str:
    """Make an exported SVG stable: Plotly's random ids replaced by the chart's name, and the
    face named once on the root."""
    uid = re.search(r'id="defs-([0-9a-f]+)"', svg)
    if uid:
        svg = svg.replace(uid.group(1), name)
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
