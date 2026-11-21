"""The front-page plates are drawn from the shared tokens and read on both page colours.

Measured: agreements between sources and computed contrast. The drawing code the plates use names
no colour of its own; every colour in the published plates is a token value; each plate names its
text face once and its code face once; and every text colour and data stroke clears the WCAG
contrast ratio against the page it is shown on.
"""

from __future__ import annotations

import re
from pathlib import Path

from bench import kit, plate, publish

ROOT = Path(__file__).resolve().parent.parent
COLOUR = re.compile(r"(?<![\w(])#(?:[0-9a-fA-F]{6}|[0-9a-fA-F]{3})\b|\brgba?\(")
PAINT = re.compile(r'(?:fill|stroke|stop-color)="([^"]+)"')
TEXT_FILL = re.compile(r'<text [^>]*fill="([^"]+)"')
STROKE = re.compile(r'<(?:line|path|rect) [^>]*stroke="(#[0-9a-fA-F]{6})" stroke-width="([\d.]+)"')
PAGE = {"light": "#ffffff", "dark": "#0d1117"}  # GitHub's page colours


def shown() -> list[Path]:
    names = (*publish.PLATES, publish.BOARD)
    found = [
        p
        for p in sorted((ROOT / "docs" / "results").glob("*/*.svg"))
        if p.name.split(".")[0] in names
    ]
    assert found, "no plates found under docs/results"
    return found


def luminance(colour: str) -> float:
    def channel(v: int) -> float:
        c = v / 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

    r, g, b = (int(colour[i : i + 2], 16) for i in (1, 3, 5))
    return 0.2126 * channel(r) + 0.7152 * channel(g) + 0.0722 * channel(b)


def ratio(a: str, b: str) -> float:
    hi, lo = sorted((luminance(a), luminance(b)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


def test_the_plate_code_names_no_colour():
    for module in (plate, kit):
        source = Path(module.__file__).read_text(encoding="utf-8")
        assert not COLOUR.findall(source), f"{module.__name__} holds a colour literal"


def test_every_colour_in_the_plates_is_a_token_at_full_value():
    for svg in shown():
        text = svg.read_text(encoding="utf-8")
        assert "opacity" not in text, f"{svg.name}: a colour is drawn at reduced opacity"
        for found in COLOUR.findall(text):
            assert found.lower() in kit.COLOURS, f"{svg.name}: {found} is not a token"
        for paint in PAINT.findall(text):
            if paint == "none" or paint.startswith("url(#"):
                continue
            assert paint.lower() in kit.COLOURS, f"{svg.name}: {paint} is not a token"


def test_a_plate_names_its_faces_once():
    for svg in shown():
        text = svg.read_text(encoding="utf-8")
        named = re.findall(r'font-family[=:]"?([^;}"]+)', text)
        assert named.count(kit.TEXT.replace("'", "&#x27;")) + named.count(kit.TEXT) == 1, svg.name
        assert named.count(kit.CODE) <= 1, svg.name
        assert len(named) <= 2, f"{svg.name}: a face is named on a text node"


def test_text_and_data_strokes_clear_the_contrast_ratio():
    for svg in shown():
        page = PAGE[svg.name.split(".")[-2]]
        text = svg.read_text(encoding="utf-8")
        for colour in set(TEXT_FILL.findall(text)):
            got = ratio(colour, page)
            assert got >= 4.5, f"{svg.name}: text in {colour} is {got:.2f} to 1 on {page}"
        for colour, width in set(STROKE.findall(text)):
            if float(width) < kit.WEIGHT["fine"]:
                continue  # a hair line is a gridline or leader, not data
            got = ratio(colour, page)
            assert got >= 3, f"{svg.name}: a stroke in {colour} is {got:.2f} to 1 on {page}"


def test_the_kit_reads_the_one_token_file():
    assert kit.palette("light")["pink"] == kit.TOKENS["pen"]["pink"]["light"]
    assert kit.palette("dark")["ink"] == kit.TOKENS["color"]["ink"]["dark"]
    assert set(plate.LOOKS) == set(kit.LOOKS)
