---
kind: reference
title: Design
status: current
date: 2026-11-21
source: src/conky/tokens.json, decisions 0046, 0048 and 0061
---

# Design

Everything a person sees on the front page (the schematic figures and the demo recording) is drawn from one token file, `src/conky/tokens.json`; the benchmark charts are drawn with a maintained Plotly template (see Charts), and the five pens are that template's five colours. Nothing a model is shown is in scope: a prompt is text, not design. The decisions are [0046](../decisions/0046-figures-are-drawn-from-the-shared-tokens.md) and [0061](../decisions/0061-figures-take-the-chart-themes-colours.md) for the tokens and [0048](../decisions/0048-charts-are-drawn-by-plotly-and-words-sit-in-markdown.md) and [0057](../decisions/0057-charts-use-plotlys-built-in-themes-and-default-styles.md) for the charts.

By day a figure reads like a page of a printed scientific magazine; by night like a console. It is almost monochrome, and a pen appears only where it carries meaning, as a mark or a line and never as a word.

## Ground

| Token | Light | Dark | Used for |
|---|---|---|---|
| `ink` | `#141413` | `#f2f2ef` | text, strokes, axes, frames |
| `mute` | `#595854` | `#a3a7ad` | secondary text, at `small` size or larger |
| `hair` | `#c9c8c3` | `#2c3568` | gridlines and leaders only, never text or data |
| `paper` | `#fbfaf7` | `#030620` | a cross on a filled mark |
| `sunken`, `raised` | `#f1f0ec`, `#ffffff` | `#0b1038`, `#070b2c` | surfaces that own their page |

The dark ink is a neutral near-white because the figures sit on GitHub's own dark page, `#0d1117`, where a neutral white reads best.

## Pens

| Pen | Light | Dark | Means |
|---|---|---|---|
| mint | `#2a7763` | `#7bc5af` | a model's thought |
| coral | `#a43000` | `#fa7851` | a refusal; the focus |
| green | `#04996d` | `#83fbc8` | what was kept or passed; success |
| yellow | `#9c7900` | `#fed56b` | something a character added; a warning, such as a broken rule |
| teal | `#025b6a` | `#4c9bad` | what is heard; information |

The pens are the five series colours of the Minty chart template, in its order, so a figure and a chart share one palette ([decision 0061](../decisions/0061-figures-take-the-chart-themes-colours.md)). The dark value is the template's colour. The light value is derived from it by one rule, kept in the token file as `pen_light` and never picked by hand: the colour in OKLCH with its lightness multiplied by 0.67, its hue kept, and its chroma lowered only as far as sRGB needs. The pastels need it: on white the green and the yellow are about 1.3 to 1. A test holds both agreements, the pens with the installed template and each light value with the rule.

Five pens only: a pen is never added, and its colour changes only when the template's does. A pen draws marks and lines that carry meaning: an edge, a frame, a rule beside a row, a line under a name, a filled mark, a symbol. It never colours a word. Every pen clears 3 to 1 on each ground it is drawn on, in both looks.

## Ports

The ports of a drawn trial are a carve-out from the pens ([decision 0059](../decisions/0059-ports-are-bright-labelled-blocks-on-paired-boards.md)): nine bright block colours in the `port` section, one a kind of port, each carrying a white name at 4.5 to 1. They are not Minty's and do not change with it. A port with something plugged in is a solid block with its name in white. A port with nothing plugged in has no fill and no edge on three sides: it is a solid bar in its kind's colour along the edge that touches the cell, `port.idle_bar` (0.2) of the port's depth, with its name in ink in the room left. A chip that names such a port is the same, the bar on its leading edge.

## Charts

A benchmark chart is drawn by Plotly with the Minty figure templates from `dash-bootstrap-templates`: `minty` for the light file and `minty_dark` for the dark file. It keeps Plotly's default style for its chart type. The colours of its marks, its layout, its legends and its text sizes are the template's. A maintained theme beats a hand-made one.

One small overlay a look, in `bench/kit.py`, sits on top of each template so a chart can stand on a README page in either mode: a transparent ground, so GitHub's own page colour shows; the faces GitHub renders the page in (`type.embedded_text`), because the template's first face is not on a reader's machine; tight margins; no outline on a bar; and the fixed export width. Harnesses are listed in one order, the subject first, so the template's colour sequence gives the subject its first colour in every chart.

Words and rules are monochrome. Every word on a chart (axis titles, tick values, legend names, the label on the goal line) is the look's `color.ink`, and every axis line, tick and gridline is its `color.mute`. These are the two tokens a chart takes. Colour is carried only by the marks.

Minty's colours are pastels. On GitHub's white page its light green and yellow marks are pale ([decision 0060](../decisions/0060-charts-take-the-minty-theme-with-monochrome-text.md) gives the numbers). The marks are not held to the contrast floor of a schematic figure; the text is, through the ink token. A chart keeps the template's colours in both looks; only the pens are darkened for the light look, because a pen draws thin lines where a chart draws bars.

## Weights, dashes, sizes

| Weight | hair 0.8 | fine 1.2 | base 1.6 | bold 2.4 | heavy 3.2 |
|---|---|---|---|---|---|

| Dash | dot `1 3` | short `3 3` | long `6 3` |
|---|---|---|---|

| Size | micro 7 | small 8.5 | base 10 | large 12 | display 22 |
|---|---|---|---|---|---|

Radius is 0 and there are no shadows.

## Figure rules

- Text is text. A heading, label or sentence is never an image; images are for figures and marks only.
- Every colour, weight, dash and size comes from the tokens. A literal colour on a schematic figure fails the audit; a chart takes its colours from its Plotly template.
- Backgrounds are transparent: a figure paints no paper. Each has a light and a dark file.
- Text is ink, or mute where it is secondary; no word is set in a pen or lettered on one. A schematic's text clears 4.5 to 1 against the page it is shown on, and a data stroke 3 to 1; the test computes both.
- Charts keep the template's look for their marks: nothing but words, axis lines and grid is restyled, and those are neutral.
- Words about a chart sit in Markdown beside it: a heading above, one caption sentence below with the conditions of its numbers, and a footer line for method, data and units. The image carries only what Plotly draws for its data: axes, axis titles and a legend. A table is a Markdown table, never an image.
- No text on a schematic figure is smaller than about 11 pixels at the width the README shows it. A figure sets its sizes as classes on its root, so the test reads the smallest class, the figure's width and the width the README gives it.
- Words about a schematic sit in Markdown too: the heading it sits under, one caption line below it that opens with "Schematic" or "Example", and alt text that describes the picture. The image keeps short names on its parts.
- Separate with space, not rules. Lines appear only inside tables and charts.
- A caption says what a figure shows, not what kind of figure it is. No heading or figure title opens with "The". A number keeps its conditions beside it.
- Brand marks are not restyled and keep their own colours: the sponsor wordmark and the three-band ornament are exempt from the colour audit, by name.

## On GitHub

A README image cannot load a web font, so a front-page figure sets its text in the faces GitHub renders the page in: `type.embedded_text` for text and `type.embedded_code` for code and tabular numbers, each named once on the figure's root. The serif and dot-matrix stacks (`type.text`, `type.label`) belong to surfaces that own their page, such as the docs site. Light and dark files are switched by `<picture>` with `prefers-color-scheme`, and each is checked on `#ffffff` and `#0d1117`.

## Deferred

- The docs site and the viewer's interface rules.
- Embedded fonts.
- Figures that stay legible at a phone width of about 360 pixels, where the schematics' smallest text lands near 5 pixels.
