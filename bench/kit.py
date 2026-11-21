"""The drawing kit for the benchmark plates: colours, pen weights, dashes, sizes, faces and fills.

Every value is read from `src/conky/tokens.json`, the one token file; nothing here holds a
second copy. A plate names a colour by its token (`ink`, `mute`, `hair`, `paper`, or a pen such
as `pink`) and the kit turns it into the value for the light or the dark look.

A plate shown on GitHub sets its text in the faces GitHub renders the page in (`embedded_text`,
and `embedded_code` for code and tabular numbers), so a plate and the text beside it match.

An area is filled flat, with no outline: with a step of the ink ramp (`ramp1` faint to `ramp4`
full), ink, or a pen at its full value for the one thing a chart is about. Two quiet one-bit
textures, dots and a checker dither, tell bars apart where colour must not.
"""

from __future__ import annotations

import json
from pathlib import Path

TOKENS = json.loads(
    (Path(__file__).resolve().parent.parent / "src" / "conky" / "tokens.json").read_text(
        encoding="utf-8"
    )
)
GROUND = TOKENS["color"]
PEN = TOKENS["pen"]
MEANING = TOKENS["meaning"]
WEIGHT = TOKENS["weight"]
DASH = TOKENS["dash"]
SIZE = TOKENS["size"]
LOOKS = ("light", "dark")


def stack(kind: str) -> str:
    """A font-family list from a token stack."""
    return ", ".join(f"'{x}'" if " " in x else x for x in TOKENS["type"][kind])


TEXT = stack("embedded_text")
CODE = stack("embedded_code")


def palette(look: str) -> dict[str, str]:
    """Every ground colour and pen, by token name, for one look."""
    ramp = {f"ramp{i}": v for i, v in enumerate(TOKENS["ramp"]["ink"][look], start=1)}
    return {k: v[look] for k, v in GROUND.items()} | {k: v[look] for k, v in PEN.items()} | ramp


COLOURS = {v.lower() for look in LOOKS for v in palette(look).values()}

# The two quiet textures: a 4-unit tile of one-pixel squares, crisp on the pixel grid.
PITCH = 4
_SQUARES = {"dots": "M0 0h1v1h-1z", "checker": "M0 0h1v1h-1zM2 2h1v1h-1z"}


def pattern(name: str, kind: str, colour: str) -> str:
    """One texture, in one colour at its full value."""
    return (
        f'<pattern id="{name}" width="{PITCH}" height="{PITCH}" patternUnits="userSpaceOnUse">'
        f'<path d="{_SQUARES[kind]}" fill="{colour}" shape-rendering="crispEdges"/></pattern>'
    )
