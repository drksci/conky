---
kind: decision
title: Charts take the Minty theme with monochrome text
status: accepted
date: 2026-11-21
source: maintainers
arch:
  items:
  - kind: unplaced
    name: charts take the Minty theme with monochrome text
    text: A benchmark chart is drawn with the Minty figure templates (minty for the light file, minty_dark for the dark file) in Plotly's default style, and everything that is not a data mark (text, axis lines, ticks, grid, the goal line) is one neutral a look.
---

# 0060 Charts take the Minty theme with monochrome text

## Context

[0057](0057-charts-use-plotlys-built-in-themes-and-default-styles.md) drew the benchmark charts with Plotly's built-in `plotly_white` and `plotly_dark` themes and default styles. That held up: the charts are standard, and nothing about them is maintained by hand. What they lacked was a character of their own on the front page.

Prior art, read before building:

- `dash-bootstrap-templates` (MIT licence, version 3.0.1 read) ships a Plotly figure template for each Bootswatch theme in a light and a dark file. Its documented entry is `load_figure_template(["minty", "minty_dark"])`, which registers both names in `plotly.io.templates`.
- Minty is a pastel theme. Both of its files carry the same five series colours. Its light file sets text in a mid grey and its dark file in a pale grey, and each sets its own page ground and gridlines, none of them GitHub's.

## Decision

- A chart is drawn with the Minty templates: `minty` for the light file and `minty_dark` for the dark file, in Plotly's default style for its chart type. The colours of the marks, the layout, the legends and the text sizes are the template's. This replaces the built-in themes of 0057.
- Everything that is not a data mark is monochrome. An overlay a look in `bench/kit.py` sets every word (axis titles, tick values, legend names, annotations, the label on the goal line) and the goal line itself in the look's `color.ink`, and every axis line, tick and gridline in its `color.mute`. Colour is carried only by the marks.
- The two neutrals are existing tokens in `src/conky/tokens.json`; none is added. This takes back one line of 0057, that a chart uses no project token: it now uses two, for what is not data.
- The overlay also keeps what 0057 set: a transparent paper and plot ground, tight margins, and the faces GitHub renders Markdown in. The template names a system stack of its own; the GitHub stack is kept so a chart's words match the page around it.
- A bar is a plain fill in its series colour with no outline. The template gives a bar a thin dark outline; the overlay sets its width to nothing.
- The templates are an optional dependency, declared with Plotly and kaleido under `bench` in `pyproject.toml`, never a dependency of the runtime. Without them the data files are still written and the charts on disk are kept.

## Consequences

- The package costs more than its templates. It requires `dash`, `dash-bootstrap-components` and `numpy`, and importing it imports Dash, because its last line imports its theme-switch components. The JSON files sit inside the package, but reading them directly is not a documented path, so the documented function is used. `load_figure_template` also sets Plotly's default template; `kit.template` puts the default back. Dash registers a pytest plugin, which prints one deprecation warning on a test run where the `bench` extras are installed.
- Minty's five series colours are pastels. On GitHub's white page the light green is 1.3 to 1 and the yellow 1.4 to 1, so those marks are pale; the mint is 2.0, the coral 2.7 and the teal 3.2. On GitHub's dark page (`#0d1117`) every one is 5.9 or more. This is accepted, not fixed: changing the series colours would be the hand-made palette 0057 removed. The scores table beside the charts is Markdown, so no number depends on a pale mark.
- With the neutrals, what the two Minty files still give a chart is the series colours and the layout defaults, and those are the same in both. The two files are kept by name so a later version of the template that parts them is taken up without a change here.
- `tests/test_bench_charts.py` holds the properties, not names: each figure agrees with the installed template for its file in its colour sequence and layout; every colour a word is given anywhere in the figure's template is the look's ink, every axis line its mute, and the figure sets none itself; a trace names no colour, so its fill is the template's; and a bar has no outline. `tests/test_bench_kit.py` still holds that the drawing code names no colour literal.
- What 0057 kept still holds: words in Markdown, a light and a dark file a chart, charts regenerated from the run files alone, byte-stable exports, and the chart type chosen for the data.
- The bet could be shown lost by a reader who cannot find the green or the yellow marks on the white front page. The test is the rendered README on a white page; if those marks fail there, the light file takes a template whose colours were made for a light page and keeps the neutrals.
