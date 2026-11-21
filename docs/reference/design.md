---
kind: reference
title: Design
status: current
date: 2026-11-21
source: src/conky/tokens.json, decision 0046
---

# Design

Everything a person sees on the front page (the schematic figures, the demo recording, the benchmark charts and the scoreboard) is drawn from one token file, `src/conky/tokens.json`. Nothing a model is shown is in scope: a prompt is text, not design. The decision is [0046](../decisions/0046-figures-are-drawn-from-the-shared-tokens.md).

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
| pink | `#cc2a68` | `#ff7fb2` | a refusal; the subject of a chart; the focus |
| amber | `#a2600c` | `#ffc95c` | something a character added; a warning, such as a broken rule |
| blue | `#2c4fd0` | `#93aaff` | what is heard; information |
| teal | `#007c84` | `#58efd9` | what was kept or passed; success |
| violet | `#6c46d6` | `#c6acff` | a model's thought |

Five pens only: a pen is retuned, never added. Where a chart separates series rather than events, the subject takes pink and the other series are ink, told apart by weight, dash or texture before any second pen.

## Ramp

`ramp.ink` is one hue in four steps, mixed once from ink into each page colour and written as plain hex so it holds on a transparent ground.

| Step | 1 | 2 | 3 | 4 |
|---|---|---|---|---|
| Light | `#dedede` | `#b4b4b3` | `#777776` | `#141413` |
| Dark | `#2d3035` | `#56595c` | `#929494` | `#f2f2ef` |

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
- Every colour, weight, dash and size comes from the tokens. A literal colour on a figure fails the audit.
- Backgrounds are transparent: a figure paints no paper. Each has a light and a dark file.
- Text is ink by default. Text clears 4.5 to 1 against the page it is shown on, and a data stroke 3 to 1; the test computes both.
- Charts are flat: blocks filled with a ramp step, ink or a pen at full value, parted by a small gap of empty page. No gradients, outlines between blocks, gridlines, boxes, tick marks, rounded corners or shadows. Two quiet one-bit textures, dots and a checker dither, tell bars apart where colour must not.
- Separate with space, not rules. Lines appear only inside tables and charts.
- A caption says what a figure shows, not what kind of figure it is. No heading or figure title opens with "The". A number keeps its conditions beside it.
- Brand marks are not restyled and keep their own colours: the sponsor wordmark and the three-band ornament are exempt from the colour audit, by name.

## On GitHub

A README image cannot load a web font, so a front-page figure sets its text in the faces GitHub renders the page in: `type.embedded_text` for text and `type.embedded_code` for code and tabular numbers, each named once on the figure's root. The serif and dot-matrix stacks (`type.text`, `type.label`) belong to surfaces that own their page, such as the docs site. Light and dark files are switched by `<picture>` with `prefers-color-scheme`, and each is checked on `#ffffff` and `#0d1117`.

## Deferred

- The docs site and the viewer's interface rules.
- Embedded fonts.
- The results-page charts that the README does not show (`progress`, `spend`, `rules`, `board`), still drawn by `bench/charts.py` in its own colours.
- Text of at least about 11 pixels on screen in the schematic figures, whose smallest labels land near 8 pixels at README width.
