"""The benchmark charts take a maintained template; the schematic figures keep their audit.

The five pens are the chart template's five series colours: the dark value of each is the
colour itself, and the light value is that colour darkened by the one rule the token file
states, so a figure and a chart share a palette from one source.

Measured: agreements between sources, computed contrast. A chart is drawn with an installed
Plotly template and takes its colours from it, so what is asserted of the published charts is
that they hold no raster image, name their face once and set no text below 11 pixels, and that
the drawing code holds no colour literal. The README's schematic figures are held to a stricter
audit: no text below 11 pixels at the width the README gives them, and their text and strokes
clear the WCAG contrast ratio against the page they are shown on.
"""

from __future__ import annotations

import math
import re
from pathlib import Path

import pytest
from bench import charts, kit, publish

ROOT = Path(__file__).resolve().parent.parent
HEX = re.compile(r"(?<![\w&])#(?:[0-9a-fA-F]{6}|[0-9a-fA-F]{3})\b")
PAGE = {"light": "#ffffff", "dark": "#0d1117"}  # GitHub's page colours
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


def test_the_drawing_code_names_no_colour():
    for module in (charts, kit, publish):
        source = Path(module.__file__).read_text(encoding="utf-8")
        assert not HEX.findall(source), f"{module.__name__} holds a colour literal"
        paints = set(re.findall(r"rgba?\([^)]*\)", source))
        assert paints <= {"rgba(0,0,0,0)"}, f"{module.__name__} holds a colour literal"


def test_a_chart_names_its_face_once_and_sets_no_small_text():
    for svg in shown():
        text = svg.read_text(encoding="utf-8")
        assert "<image" not in text, f"{svg.name}: a chart holds a raster image"
        assert text.count("font-family") == 1, f"{svg.name}: a face is named on a text node"
        for size in SIZE.findall(text):
            px = float(size[0] or size[1])
            assert px >= 11, f"{svg.name}: text at {px} px"


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


SHOWN_FIGURE = re.compile(r'src="docs/assets/figures/([\w-]+)\.light\.svg"[^>]*?\swidth="(\d+)"')
SIZE_RULE = re.compile(r"font-size:\s*([\d.]+)px")


def readme_figures() -> dict[str, int]:
    """Each drawn figure the README shows, with the width it shows it at."""
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    found = {
        name: int(width) for name, width in SHOWN_FIGURE.findall(readme) if name not in BRAND_MARKS
    }
    assert found, "the README shows no drawn figure"
    return found


def test_the_figures_set_no_text_below_11_px_at_readme_width():
    for name, width in readme_figures().items():
        for look in ("light", "dark"):
            svg = (FIGURES / f"{name}.{look}.svg").read_text(encoding="utf-8")
            assert not re.search(r"<(?:text|tspan)[^>]*\sfont-size=", svg), (
                f"{name}: a text node sets its own size; give it a size class on the root"
            )
            box = float(re.search(r'viewBox="\S+ \S+ ([\d.]+) ', svg).group(1))
            sizes = [
                float(s)
                for s in SIZE_RULE.findall("".join(re.findall(r"<style>(.*?)</style>", svg, re.S)))
            ]
            assert sizes, f"{name}: no size class found"
            px = min(sizes) * width / box
            assert px >= 11, (
                f"{name}: text at {px:.1f} px at README width {width}; say less, or set it larger"
            )


def stroke_colours(svg: str) -> set[str]:
    """The colours of strokes at least one unit wide, resolved through the root variables."""
    style = "".join(re.findall(r"<style>(.*?)</style>", svg, re.S))
    root = dict(re.findall(r"--([\w-]+):(#[0-9a-fA-F]{6})", style.split("}", 1)[0]))
    found = set()
    for _selectors, body in RULE.findall(style):
        paint = re.search(r"(?<![-\w])stroke:\s*var\(--([\w-]+)\)", body)
        width = re.search(r"stroke-width:\s*([\d.]+)", body)
        # paper is the token for a mark drawn on a pen (see the design page): seen against the pen
        if (
            paint
            and paint.group(1) in root
            and paint.group(1) != "paper"
            and (not width or float(width.group(1)) >= 1)
        ):
            found.add(root[paint.group(1)])
    return found


def test_the_figures_strokes_clear_the_contrast_ratio():
    checked = 0
    for name in readme_figures():
        for look in ("light", "dark"):
            svg = (FIGURES / f"{name}.{look}.svg").read_text(encoding="utf-8")
            for colour in stroke_colours(svg):
                checked += 1
                got = ratio(colour.lower(), PAGE[look])
                assert got >= 3, (
                    f"{name}.{look}: a stroke in {colour} is {got:.2f} to 1 on {PAGE[look]}"
                )
    assert checked, "no figure stroke was found to check"


# --- the pens: the chart template's colours, darkened by one rule for the light look -------------

PENS = kit.TOKENS["pen"]


def oklch(colour: str) -> tuple[float, float, float]:
    """A colour as OKLCH lightness, chroma and hue (CSS Color 4)."""
    r, g, b = linear(colour)
    long = (0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b) ** (1 / 3)
    mid = (0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b) ** (1 / 3)
    short = (0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b) ** (1 / 3)
    a = 1.9779984951 * long - 2.4285922050 * mid + 0.4505937099 * short
    b2 = 0.0259040371 * long + 0.7827717662 * mid - 0.8086757660 * short
    light = 0.2104542553 * long + 0.7936177850 * mid - 0.0040720468 * short
    return light, math.hypot(a, b2), math.atan2(b2, a)


def srgb(light: float, chroma: float, hue: float) -> tuple[float, float, float]:
    """An OKLCH colour as linear sRGB, which may lie outside the gamut."""
    a, b = chroma * math.cos(hue), chroma * math.sin(hue)
    long = (light + 0.3963377774 * a + 0.2158037573 * b) ** 3
    mid = (light - 0.1055613458 * a - 0.0638541728 * b) ** 3
    short = (light - 0.0894841775 * a - 1.2914855480 * b) ** 3
    return (
        4.0767416621 * long - 3.3077115913 * mid + 0.2309699292 * short,
        -1.2684380046 * long + 2.6097574011 * mid - 0.3413193965 * short,
        -0.0041960863 * long - 0.7034186147 * mid + 1.7076147010 * short,
    )


def darkened(colour: str) -> str:
    """A pen's light value by the token file's rule: its lightness scaled, its hue kept, and
    its chroma lowered a step at a time only until the colour is inside sRGB."""
    rule = kit.TOKENS["pen_light"]
    assert rule["space"] == "oklch"
    light, chroma, hue = oklch(colour)
    while True:
        rgb = srgb(light * rule["lightness"], chroma, hue)
        if all(-1e-9 <= c <= 1 + 1e-9 for c in rgb):
            break
        chroma -= rule["chroma_step"]

    def channel(c: float) -> int:
        c = min(1.0, max(0.0, c))
        return round(255 * (12.92 * c if c <= 0.0031308 else 1.055 * c ** (1 / 2.4) - 0.055))

    return "#" + "".join(f"{channel(c):02x}" for c in rgb)


def test_the_pens_are_the_chart_templates_colours():
    pytest.importorskip("plotly", reason="the chart extras are not installed")
    pytest.importorskip("dash_bootstrap_templates", reason="the chart extras are not installed")
    import plotly.io as pio

    kit.template("dark")  # registers the templates
    for name in kit.THEMES.values():
        theme = [c.lower() for c in pio.templates[name].layout.colorway]
        assert [pen["dark"] for pen in PENS.values()] == theme, (
            f"the pens are not the colours of {name}, in its order"
        )


def test_a_pens_light_value_is_its_colour_darkened_by_the_stated_rule():
    for name, pen in PENS.items():
        assert pen["light"] == darkened(pen["dark"]), f"pen {name}: light is not the rule's"


def test_every_meaning_names_a_pen_and_every_pen_carries_one():
    assert sorted(kit.TOKENS["meaning"].values()) == sorted(PENS)


def test_a_pen_clears_the_stroke_floor_on_every_ground_it_is_drawn_on():
    for name, pen in PENS.items():
        for look in kit.LOOKS:
            tokens = (kit.TOKENS["color"][g][look] for g in ("paper", "raised", "sunken"))
            grounds = (PAGE[look], *tokens)
            for ground in grounds:
                got = ratio(pen[look], ground)
                assert got >= 3, f"pen {name} ({look}) is {got:.2f} to 1 on {ground}"
