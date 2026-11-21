---
kind: reference
title: Design
status: current
date: 2026-11-21
source: src/conky/tokens.json, decisions 0046 and 0048
---

# Design

Everything a person sees on the front page (the schematic figures and the demo recording) is drawn from one token file, `src/conky/tokens.json`; the benchmark charts are drawn with Plotly's own themes (see Charts). Nothing a model is shown is in scope: a prompt is text, not design. The decisions are [0046](../decisions/0046-figures-are-drawn-from-the-shared-tokens.md) for the tokens and [0048](../decisions/0048-charts-are-drawn-by-plotly-and-words-sit-in-markdown.md) and [0057](../decisions/0057-charts-use-plotlys-built-in-themes-and-default-styles.md) for the charts.

By day a figure reads like a page of a printed scientific magazine; by night like a console. It is almost monochrome, and a pen appears only where it carries meaning.

## Ground

| Token | Light | Dark | Used for |
|---|---|---|---|
| `ink` | `#141413` | `#f2f2ef` | text, strokes, axes, frames |
| `mute` | `#595854` | `#a3a7ad` | secondary text, at `small` size or larger |
| `hair` | `#c9c8c3` | `#2c3568` | gridlines and leaders only, never text or data |
| `paper` | `#fbfaf7` | `#030620` | lettering on a pen, a cross on a mark |
| `sunken`, `raised` | `#f1f0ec`, `#ffffff` | `#0b1038`, `#070b2c` | surfaces that own their page |

The dark ink is a neutral near-white because the figures sit on GitHub's own dark page, `#0d1117`, where a neutral white reads best.

## Pens

| Pen | Light | Dark | Means |
|---|---|---|---|
| pink | `#cc2a68` | `#ff7fb2` | a refusal; the focus |
| amber | `#a2600c` | `#ffc95c` | something a character added; a warning, such as a broken rule |
| blue | `#2c4fd0` | `#93aaff` | what is heard; information |
| teal | `#007c84` | `#58efd9` | what was kept or passed; success |
| violet | `#6c46d6` | `#c6acff` | a model's thought |

Five pens only: a pen is retuned, never added. The pens are for diagrams and schematics.

## Charts

Charts are not drawn from the tokens. A benchmark chart is drawn with Plotly's built-in `plotly_white` theme (the light file) or `plotly_dark` theme (the dark file) and Plotly's default style for its chart type: its colours, gridlines, axes, bars, legends and text sizes. Standard charts should look like standard charts, and a maintained theme beats a hand-made one.

One small overlay, `conky` in `bench/kit.py`, sits on top of each theme so a chart can stand on a README page in either mode: a transparent ground, so GitHub's own page colour shows; the faces GitHub renders the page in (`type.embedded_text`); tight margins; and the fixed export width. A chart sets its data mapping and its chart type, and nothing else visual. Harnesses are listed in one order, the subject first, so Plotly's default colour sequence gives the subject its first colour in every chart.

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
- Every colour, weight, dash and size comes from the tokens. A literal colour on a schematic figure fails the audit; a chart takes its colours from its Plotly theme.
- Backgrounds are transparent: a figure paints no paper. Each has a light and a dark file.
- Text is ink by default. A schematic's text clears 4.5 to 1 against the page it is shown on, and a data stroke 3 to 1; the test computes both.
- Charts keep Plotly's default look for the theme: nothing is restyled by hand.
- Words about a chart sit in Markdown beside it: a heading above, one caption sentence below with the conditions of its numbers, and a footer line for method, data and units. The image carries only what Plotly draws by default for its data: axes, axis titles and a legend. A table is a Markdown table, never an image.
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
