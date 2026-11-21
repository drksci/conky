"""The drawing kit for the benchmark charts: Plotly's built-in themes and default styles.

A chart is drawn with Plotly's own `plotly_white` (the light file) or `plotly_dark` (the dark
file) and Plotly's default style for its chart type: colours, gridlines, axes, bars, legends and
text sizes are the theme's. One small overlay, `conky`, is added on top so a chart sits on a
README page in either mode: a transparent ground, so the page's own colour shows, the faces
GitHub renders the page in (`type.embedded_text` in `src/conky/tokens.json`), tight margins and
the fixed export width. Charts are not drawn from the project's colour tokens: a standard chart
should look like a standard chart, and a maintained theme beats a hand-made one.

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
LOOKS = ("light", "dark")
THEMES = {"light": "plotly_white", "dark": "plotly_dark"}
WIDTH = 720  # the width a chart is shown at in the README, so a pixel here is a pixel there


def stack(kind: str) -> str:
    """A font-family list from a token stack."""
    return ", ".join(f'"{x}"' if " " in x else x for x in TOKENS["type"][kind])


TEXT = stack("embedded_text")
OVERLAY = {
    "layout": {
        "paper_bgcolor": "rgba(0,0,0,0)",
        "plot_bgcolor": "rgba(0,0,0,0)",
        "font": {"family": TEXT},
        "margin": {"l": 8, "r": 8, "t": 8, "b": 8},
    }
}


def available() -> bool:
    """Whether Plotly and kaleido are installed, so charts can be drawn and exported."""
    try:
        import kaleido  # noqa: F401
        import plotly  # noqa: F401
    except ImportError:
        return False
    return True


def template(look: str) -> str:
    """The name of the template for a look: the built-in theme with the overlay on top."""
    import plotly.io as pio

    if "conky" not in pio.templates:
        pio.templates["conky"] = OVERLAY
    return f"{THEMES[look]}+conky"


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
