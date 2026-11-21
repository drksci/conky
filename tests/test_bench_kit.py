"""The benchmark charts are drawn from the shared tokens and read on both page colours.

Measured: agreements between sources, computed contrast and computed colour difference. The
drawing code names no colour of its own; every colour in a published chart is a token value; each
chart names its face once, on its root; no text is smaller than about 11 pixels at README width;
every text colour and data stroke clears the WCAG contrast ratio against the page it is shown on;
and the chart palette's neighbours stay apart. The palette check is a colour difference in OKLab
(times 100): at least 15 for normal vision, and at least 8 under protanopia and deuteranopia
simulated with the Machado, Oliveira and Fernandes (2009) matrices at full severity.
"""

from __future__ import annotations

import re
from pathlib import Path

from bench import charts, kit, publish

ROOT = Path(__file__).resolve().parent.parent
HEX = re.compile(r"(?<![\w&])#(?:[0-9a-fA-F]{6}|[0-9a-fA-F]{3})\b")
PAGE = {"light": "#ffffff", "dark": "#0d1117"}  # GitHub's page colours
TEXT_FILL = re.compile(r'<text [^>]*?style="[^"]*?fill: (#[0-9a-f]{6})')
STYLE = re.compile(r'style="([^"]*stroke: #[^"]*)"')
STROKE = re.compile(r"stroke: (#[0-9a-f]{6})")
WIDTH = re.compile(r"stroke-width: ([\d.]+)px")
SIZE = re.compile(r"font-size: ?([\d.]+)px|font-size=\"([\d.]+)\"")


def shown() -> list[Path]:
    names = (*publish.SHOWN, *publish.PAGE_ONLY)
    found = [
        p
        for p in sorted((ROOT / "docs" / "results").glob("*/*.svg"))
        if p.name.split(".")[0] in names
    ]
    assert found, "no charts found under docs/results"
    return found


def linear(colour: str) -> list[float]:
    def channel(v: int) -> float:
        c = v / 255
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

    return [channel(int(colour[i : i + 2], 16)) for i in (1, 3, 5)]


def luminance(colour: str) -> float:
    r, g, b = linear(colour)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def ratio(a: str, b: str) -> float:
    hi, lo = sorted((luminance(a), luminance(b)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


CVD = {
    "normal": ((1, 0, 0), (0, 1, 0), (0, 0, 1)),
    "protan": (
        (0.152286, 1.052583, -0.204868),
        (0.114503, 0.786281, 0.099216),
        (-0.003882, -0.048116, 1.051998),
    ),
    "deutan": (
        (0.367322, 0.860646, -0.227968),
        (0.280085, 0.672501, 0.047413),
        (-0.011820, 0.042940, 0.968881),
    ),
}


def oklab(rgb: list[float]) -> tuple[float, float, float]:
    r, g, b = (min(max(v, 0.0), 1.0) for v in rgb)
    lms = (
        0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b,
        0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b,
        0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b,
    )
    l_, m_, s_ = (v ** (1 / 3) for v in lms)
    return (
        0.2104542553 * l_ + 0.7936177850 * m_ - 0.0040720468 * s_,
        1.9779984951 * l_ - 2.4285922050 * m_ + 0.4505937099 * s_,
        0.0259040371 * l_ + 0.7827717662 * m_ - 0.8086757660 * s_,
    )


def difference(a: str, b: str, vision: str) -> float:
    m = CVD[vision]

    def seen(colour: str) -> tuple[float, float, float]:
        rgb = linear(colour)
        return oklab([sum(m[i][k] * rgb[k] for k in range(3)) for i in range(3)])

    return 100 * sum((x - y) ** 2 for x, y in zip(seen(a), seen(b), strict=True)) ** 0.5


def test_the_drawing_code_names_no_colour():
    for module in (charts, kit, publish):
        source = Path(module.__file__).read_text(encoding="utf-8")
        assert not HEX.findall(source), f"{module.__name__} holds a colour literal"


def test_every_colour_in_the_charts_is_a_token():
    for svg in shown():
        text = svg.read_text(encoding="utf-8")
        assert "<image" not in text, f"{svg.name}: a chart holds a raster image"
        for found in HEX.findall(text):
            assert found.lower() in kit.COLOURS, f"{svg.name}: {found} is not a token"


def test_a_chart_names_its_face_once_and_sets_no_small_text():
    for svg in shown():
        text = svg.read_text(encoding="utf-8")
        assert text.count("font-family") == 1, f"{svg.name}: a face is named on a text node"
        for size in SIZE.findall(text):
            px = float(size[0] or size[1])
            assert px >= 11, f"{svg.name}: text at {px} px"


def test_text_and_data_strokes_clear_the_contrast_ratio():
    checked = 0
    for svg in shown():
        page = PAGE[svg.name.split(".")[-2]]
        text = svg.read_text(encoding="utf-8")
        for colour in set(TEXT_FILL.findall(text)):
            got = ratio(colour, page)
            assert got >= 4.5, f"{svg.name}: text in {colour} is {got:.2f} to 1 on {page}"
        strokes = set()
        for style in STYLE.findall(text):
            width = WIDTH.search(style)
            if width and float(width.group(1)) >= 1:  # thinner is no stroke, or not data
                strokes.add(STROKE.search(style).group(1))
        checked += len(strokes)
        for colour in strokes:
            got = ratio(colour, page)
            assert got >= 3, f"{svg.name}: a stroke in {colour} is {got:.2f} to 1 on {page}"
    assert checked, "no data stroke was found to check"


def test_neighbours_in_the_chart_palette_stay_apart():
    for look in kit.LOOKS:
        c = kit.palette(look)
        order = [c["subject"], *(c[f"cat{i}"] for i in range(1, len(kit.CHART["categorical"]) + 1))]
        for a, b in zip(order, order[1:], strict=False):
            assert difference(a, b, "normal") >= 15, f"{look}: {a} and {b} look alike"
            for vision in ("protan", "deutan"):
                got = difference(a, b, vision)
                assert got >= 8, f"{look}: {a} and {b} are {got:.1f} apart under {vision}"


def test_the_kit_reads_the_one_token_file():
    assert kit.palette("light")["subject"] == kit.TOKENS["chart"]["subject"]["light"]
    assert kit.palette("dark")["ink"] == kit.TOKENS["color"]["ink"]["dark"]
    assert kit.palette("dark")["quiet"] == kit.TOKENS["ramp"]["ink"]["dark"][1]
    assert set(kit.ROLES) >= {"subject", "other", "model", "harness", "idle"}


def test_the_palette_swatches_on_the_design_page_are_generated():
    for look in kit.LOOKS:
        path = kit.SWATCH_FILE.with_name(f"{kit.SWATCH_FILE.name}.{look}.svg")
        assert path.read_text(encoding="utf-8") == kit.swatches(look), (
            f"{path.name} differs: run python -m bench.kit"
        )


FIGURES = ROOT / "docs" / "assets" / "figures"
BRAND_MARKS = ("mark-drksci", "mark-tri")  # brand marks keep their own colours
RULE = re.compile(r"([^{}]+)\{([^{}]*)\}")


def text_colours(svg: str) -> set[str]:
    """The colours a figure's text is filled with, resolved through its root variables."""
    style = "".join(re.findall(r"<style>(.*?)</style>", svg, re.S))
    root = dict(re.findall(r"--([\w-]+):(#[0-9a-fA-F]{6})", style))
    classes = {c for found in re.findall(r'<(?:text|tspan)[^>]*class="([^"]+)"', svg)
               for c in found.split()}  # fmt: skip
    found = set(re.findall(r'<(?:text|tspan)[^>]*\sfill="(#[0-9a-fA-F]{6})"', svg))
    for selectors, body in RULE.findall(style):
        names = {s.strip().lstrip(".") for s in selectors.split(",")}
        paint = re.search(r"(?<![-\w])fill:\s*var\(--([\w-]+)\)", body)
        if names & classes and paint and paint.group(1) in root:
            found.add(root[paint.group(1)])
    return found


def test_the_figures_text_clears_the_contrast_ratio():
    checked = 0
    for svg in sorted(FIGURES.glob("*.*.svg")):
        if svg.name.split(".")[0] in BRAND_MARKS:
            continue
        page = PAGE[svg.name.split(".")[-2]]
        for colour in text_colours(svg.read_text(encoding="utf-8")):
            checked += 1
            got = ratio(colour.lower(), page)
            assert got >= 4.5, f"{svg.name}: text in {colour} is {got:.2f} to 1 on {page}"
    assert checked, "no figure text was found to check"
