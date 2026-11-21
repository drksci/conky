---
kind: decision
title: Charts are drawn by Plotly and words sit in Markdown
status: accepted
date: 2026-11-21
source: maintainers
arch:
  items:
  - kind: unplaced
    name: charts are drawn by Plotly from one template
    text: Every benchmark chart is drawn by Plotly from one template built on src/conky/tokens.json, black and white with one spot colour, and its heading, caption and conditions are written beside it in Markdown.
---

# 0048 Charts are drawn by Plotly and words sit in Markdown

## Context

After [0046](0046-figures-are-drawn-from-the-shared-tokens.md) the benchmark charts took their colours from the tokens but were still drawn by hand in `bench/plate.py` and `bench/charts.py`: about a thousand lines of SVG arithmetic, two drawing styles, and a scoreboard drawn as a picture of a table. Readers found them garish (solid pink bars), noisy and slow to read. Each image carried its own title, conditions, source and footnotes, set small enough to land below 11 pixels at README width, and none of it could be selected, searched or read by a screen reader.

## Decision

- Standard charts are drawn by Plotly's Python library from one template, `kit.template(look)` in `bench/kit.py`, built on the tokens: transparent ground, the faces GitHub renders the page in, text at 12 pixels, no gridlines, no chart border, no tick marks. A chart sets nothing visual beyond its data mapping and the role of each mark.
- A chart is black and white first: ink outlines and text, fills in ink, the page and the grey steps of `ramp.ink`, with a one-bit pattern (`marker.pattern`) only where two greys would be hard to tell apart. Colour is added only where it helps: the subject of a chart, or one notable thing such as a broken rule. Bars are flat, square, outlined in one pixel of ink and parted by a small gap.
- Charts are a carve-out from the five pens. The pens and their meanings stay for diagrams and schematics; charts read their colours from the `chart` section of `src/conky/tokens.json` only: `subject`, four `categorical` colours in a fixed order, a three-step `sequential` ramp for shaded grids, and `quiet` (a step of the ink ramp) for whatever is not singled out. A chart with several categories needs a palette built for telling series apart, and readers expect chart colour by convention.
- The chart palette is the reference palette of the data-visualisation method the maintainers use, with its stepped values for a light and a dark page. Neighbours in its order stay at least 15 apart in OKLab for normal vision and at least 8 under simulated protanopia and deuteranopia.
- Forms by convention: how far each run got as one thin bar a run, grouped in one row a harness; what each harness left behind, what a run cost, where the time went and where the text came from as horizontal bars, stacked where a run splits into parts; distance and calls by turn as step lines; broken rules as squares on a line a run; the board as a grid of shaded cells drawn as vector shapes (a Plotly heatmap exports as a raster image). Every chart lists harnesses in one order: the subject, then those that use a model, then those that do not.
- Words sit in Markdown. `bench/publish.py` writes a heading above each chart, one caption sentence below it with the conditions of its numbers (model, runs, that it is a pilot), the scores as a Markdown table with the subject's row in bold, and one footer line of method, data, protocol, code and prices. A chart image carries only row labels, a few direct values and a small legend.
- Plotly and kaleido are an optional dependency group, `bench`. Publishing without them writes the data, the page and the README block, leaves the charts on disk as they are, and says so.

Prior art: Plotly's own guidance draws flame graphs as icicle charts, and `go.Icicle` takes pattern fills; with one level of parts, a stacked horizontal bar says the same with fewer marks, so it is used here. Early Macintosh interface charts for the outlined, patterned black and white look. The categorical order and its distinguishability gates come from the same data-visualisation method, which simulates colour-vision deficiency with Machado, Oliveira and Fernandes (2009).

## Consequences

- `bench/plate.py` and the hand-drawn charts in `bench/charts.py` are removed, with the `where` chart, which no page showed. `bench/charts.py` keeps loading runs and exporting `runs.csv`, `runs.json`, `series.json` and `shapes.json`, and now builds Plotly figures.
- `kit.tidy` makes each exported SVG byte-stable: Plotly's random ids are replaced by the chart's name and a count, colours are written as hex, and the face is named once on the root.
- `tests/test_bench_kit.py` audits the published charts: no colour outside the tokens, no raster image, one face, no text below 11 pixels, text at 4.5 to 1 and data strokes at 3 to 1 on `#ffffff` and `#0d1117`, and the palette's neighbours apart. `tests/test_bench_charts.py` checks each figure's data and layout without a browser, the README block's headings, captions, table and footer, and that publishing twice gives the same bytes.
- What the hand-drawn charts guaranteed and is kept: a light and a dark file per chart, charts regenerated from the run files alone, the same runs giving the same bytes, a run marked when it used a scripted stand-in (now in the caption, not the image), and hollow marks for a breaking input a model proposed that never reached the game. Given up: the per-turn flame graphs (each harness's median run is now split into parts on one bar) and the drawing of each vault's final shape (now counted as pages handed to it and pages its own).
- In the light look three categorical colours sit below 3 to 1 on the page as fills; every such chart carries direct labels and the scores table, which is the relief the method allows.
