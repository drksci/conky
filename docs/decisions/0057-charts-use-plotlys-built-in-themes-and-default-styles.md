---
kind: decision
title: Charts use Plotly's built-in themes and default styles
status: accepted
date: 2026-11-21
source: maintainers
arch:
  items:
  - kind: unplaced
    name: charts use Plotly's built-in themes
    text: A benchmark chart is drawn with Plotly's plotly_white (light file) or plotly_dark (dark file) theme and its default style for the chart type, with one small overlay for a transparent ground, the page's font, tight margins and the export width.
---

# 0057 Charts use Plotly's built-in themes and default styles

## Context

[0048](0048-charts-are-drawn-by-plotly-and-words-sit-in-markdown.md) moved the benchmark charts to Plotly but kept a hand-made look: a template built on the project's tokens, a chart palette that was a carve-out from the five pens, outlined flat bars, one-bit patterns, no gridlines and a drawing kit of roles and fills. Every chart was then a custom design to keep in step with the tokens, the palette was audited by hand-written colour-difference maths, and none of it looked like a chart a reader had seen before.

## Decision

- A chart is drawn with Plotly's built-in `plotly_white` theme for the light file and `plotly_dark` for the dark file, and Plotly's default style for its chart type. Colours, gridlines, axis lines, ticks, bar gaps, legends and text sizes are the theme's. Standard charts should look like standard charts, and a maintained theme beats a hand-made one.
- One overlay, `conky` in `bench/kit.py`, is combined with each theme (`plotly_white+conky`). It sets a transparent paper and plot background so GitHub's own page colour shows in either mode, the faces GitHub renders Markdown in (`type.embedded_text`), tight margins, and nothing else. The export width and each chart's height are set on the figure.
- A chart sets its data mapping and its chart type, and nothing visual beyond what the type needs to be correct (orientation, bar mode, category order, the goal as a line, axis titles). Harnesses are listed in one order with the subject first, so Plotly's default colour sequence colours the subject first in every chart; there is no special colour for it.
- The chart type is chosen for what the data is, not kept from before. How far each run got is a bar a run, grouped by harness, with the goal as one line, so every run shows at five runs a harness. What a run cost is a dot a run against how far it got, which shows the trade the scores table only lists. Where the time and the text went, and what each harness ended with, are stacked horizontal bars. Progress and model calls are stepped lines. Broken rules are dots on a row a run, with an empty row for a run that broke none. The shaded board is dropped: the scores table in Markdown holds the same medians.
- Not built from the project's tokens: the `chart` and `ramp` sections of `src/conky/tokens.json` are removed, with the palette swatches and their generator. The schematic figures keep their own audit.
- Types rejected: a strip plot for reach (equal values sit on one another and hide runs, and jitter to part them implies a spread the data does not have); a treemap or sunburst for parts of a whole (areas are harder to compare across harnesses than bar lengths); a Sankey (no flow to show); parallel coordinates or radar for the standings (the Markdown table reads faster). `plotly.express` is not used: it needs numpy, and `graph_objects` takes the same themes.

## Consequences

- This replaces the parts of 0048 that describe the template, the palette, the black-and-white look and the board. What 0048 kept still holds: words in Markdown, a light and a dark file per chart, charts regenerated from the run files alone, byte-stable exports, and hollow marks for a breaking input a model proposed that never reached the game (now an open circle).
- `tests/test_bench_kit.py` no longer requires every colour in a chart to be a token, nor the chart palette's distances and contrast. It holds that the drawing code names no colour, and that a published chart has no raster image, one face and no text below 11 pixels. `tests/test_bench_charts.py` holds that each figure uses the built-in theme named for its file, a transparent ground and the page's font, and sets no colour itself.
- The built-in themes' text and grid colours were checked on `#ffffff` and `#0d1117` with a transparent ground and read without change; no default is altered.
- A harness with no bar in the text and ending charts recorded nothing to count; the caption says so.
