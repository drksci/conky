---
kind: decision
title: Figures take the chart theme's colours
status: accepted
date: 2026-11-21
source: maintainers
arch:
  items:
  - kind: unplaced
    name: the five pens are the chart theme's five colours
    text: The five pens in the token file are the five series colours of the Minty chart template, in its order; the dark value of a pen is the colour itself and the light value is that colour darkened by one stated rule, and a pen draws marks and lines only, never words.
  - kind: unplaced
    name: a port with nothing plugged in is a bar
    text: In a drawn trial a port with nothing plugged in is no block, only a solid bar in its kind's colour along the edge that touches the cell, a fixed share of the port's depth, with its name in ink beside it.
---

# 0061 Figures take the chart theme's colours

## Context

[0060](0060-charts-take-the-minty-theme-with-monochrome-text.md) gave the benchmark charts the Minty figure templates: five series colours for the data marks, and one neutral a look for everything else. The other figures kept the five pens of [0046](0046-figures-are-drawn-from-the-shared-tokens.md), a second hand-made palette beside the first. A reader met two sets of colours on one front page, and the pens had to be maintained by hand.

Prior art, read before building:

- The installed templates (`dash-bootstrap-templates` 3.0.1) give `minty` and `minty_dark` the same colourway of five: a mint, a coral, a light green, a yellow and a teal. They follow the roles of the Bootswatch theme they are made from: primary, danger, success, warning and info.
- OKLCH, from CSS Color 4, separates a colour's lightness from its hue and chroma, so one number can darken five colours evenly and leave each recognisable.
- WCAG 2 asks 3 to 1 of a graphical mark against its ground and 4.5 to 1 of text.

## Decision

- The five pens in `src/conky/tokens.json` are Minty's colourway, in its order: `mint`, `coral`, `green`, `yellow`, `teal`. The old names (pink, amber, blue, teal, violet) are gone with the old colours.
- A pen keeps its meaning, and the mapping follows the theme's own roles: a refusal is `coral` (danger); what was kept or passed is `green` (success); something a character added, and a warning, is `yellow` (warning); what is heard, information, is `teal` (info); a model's thought is `mint`, the theme's primary and the one colour left.
- The dark value of a pen is the template's colour itself. On GitHub's dark page (`#0d1117`) every one is 5.9 to 1 or more.
- The light value is derived, never picked. Two of the five are about 1.3 to 1 on white, which no thin line survives. The rule, recorded in the token file as `pen_light`, is: the colour in OKLCH with its lightness multiplied by 0.67, its hue kept, and its chroma lowered in steps of 0.001 only until the colour is inside sRGB. At that factor the lightest pen, the green, clears 3 to 1 with a margin on every light ground: 3.6 on white, 3.5 on the paper token and 3.2 on the sunken ground. A multiplier is used and not one fixed lightness for all, because at one lightness the mint and the green cannot be told apart.
- A pen draws marks and lines that carry meaning: an edge, a rule beside a row, a line under a name, a frame, a filled mark, a symbol. All text is `color.ink`, or `color.mute` for secondary text. Frames, rules and grid stay neutral. Words that were set in a pen, and words that were lettered in the ground colour on a block of a pen, are now ink: a verdict in the terminal figure is ink in a frame of its pen, and the subject of a step in a drawn trial is marked by its edge, by a line under its name or by a bar beside its row. The `paper` token is left with one use, the cross on a filled mark.
- The floor in `docs/reference/design.md` holds unchanged: text 4.5 to 1 and a data stroke 3 to 1 against the page a figure is shown on. Every pen clears the stroke floor in both looks.
- The port colours of [0059](0059-ports-are-bright-labelled-blocks-on-paired-boards.md) are a deliberate carve-out and stay as they are: nine kinds have to be told apart at a very small size and carry a white name at 4.5 to 1, which five pastels cannot do. Cables keep the colour of the port they leave.
- A port with nothing plugged in changes shape. 0059 drew it hatched in its colour with a dotted edge and its name on a patch of ground. It is now no block: no fill, no hatch and no edge on three sides, only a solid bar in its kind's colour along the edge that touches the cell, with its name in ink in the room left. The bar is `port.idle_bar` of the port's depth, 0.2. The chip that names such a port in a row, a footer, the side panel or the key is the same: a bar on its leading edge and the name in ink. A plugged port is unchanged.
- Two layout faults in the view are mended with this. A space no longer grows far taller than what it holds: the band above its members was given to ELK twice, as padding and as room around its ports, so the member a port connects to sat that much too low. A cable whose port the view set in its row away from ELK's end no longer doglegs just outside the board: its last stretch is slid onto the port along the turn behind it.

## Consequences

- Charts and figures share one palette from one source. In the dark look the colours are identical. In the light look a chart's marks are Minty's pastels as 0060 accepted them, and a figure's pens are the same hues darkened, because a figure draws thin lines where a chart draws bars.
- `tests/test_bench_kit.py` holds the agreements, not named colours: the pens' dark values are the installed template's colourway in order, for both template files (skipped, and said so, where the chart extras are not installed); every light value is its dark value under the rule in `pen_light`; every meaning names a pen and every pen carries one; and every pen clears 3 to 1 on each ground it is drawn on. A new version of the template that changes a colour fails the first test until the token file follows.
- `npm test` in `viewer/` holds the bar: a port with nothing plugged in has no fill, no edge on three sides, and a bar of the token's share in its kind's colour on the side that touches the cell.
- What 0046 guaranteed is kept: every colour on a schematic is a token, a light and a dark file, a transparent ground, the contrast floors, and five pens only. What is given up is a palette tuned by hand for each look, and with it pen text: a figure can no longer colour a word.
- The light pens are darker and less pastel than the chart marks beside them, so the kinship is by hue, not by exact colour.
- The mint and the green are neighbours in hue. In the light look they differ mostly in lightness. The bet is that a model's thought and what was kept are rarely the subject of the same step, and that the symbol beside each says which it is. It would be shown lost by a reader who confuses the two in a drawn trial; the remedy would be a different meaning on one of the two pens, not a sixth colour.
- This amends 0046 (the pens and their names, and what a pen may draw), 0060 (the series colours are now also the pens, and the token file follows the template) and 0059 (the look of a port with nothing plugged in).
