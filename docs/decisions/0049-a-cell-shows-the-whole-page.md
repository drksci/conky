---
kind: decision
title: A cell shows the whole page, with sockets
status: accepted
date: 2026-11-21
source: maintainers
arch:
  items:
  - kind: unplaced
    name: a cell shows the whole page
    text: Every page in a drawn trial is one cell with a header, panels in a fixed order and a footer of slots, and its connections run between sockets that carry one kind of signal each.
---

# 0049 A cell shows the whole page, with sockets

## Context

- The first view ([decision 0043](0043-a-trial-is-drawn-as-it-happened.md)) drew every page as one cell with grouped rows. It left out a page's text, the rules handed down to it, what a term page is known as and how a space shows its members, and its pictures had faults: values wrapped after layout and spilled out of their cells, code was soft-wrapped by the browser, some labels were cryptic ("clerk" under "listens for" for a page that listens to itself), and forty notes in one space were a grid with no regions.
- Prior art: the rear panel of a computer or a patch bay, where every input and output is a labelled socket in a fixed place and a cable plugs into one; node editors (Blender's shader nodes, Unreal's blueprints, Max/MSP) that colour a socket by the kind of value it carries; Prettier and gofmt for laying out an expression in lines by fixed rules; WCAG 2.1 for contrast (4.5 for text, 3 for graphical objects).

## Decision

- `graph.json` is the whole contract for a node: a header (kind words, symbol, avatar, the spaces it is within, the phrases it is known as, its model calls and writes turned away), panels in a fixed order (its text, the fields it holds, the rules it is bound by including those handed down with the space they come from, and one "when, then" row a watch entry with the rows from the record no watch entry explains), a footer of slots (the provider it asks, the space it writes into, what a space hands down and how it shows its members) and its sockets. Values that move with the steps are named and changed by the steps. Every top-level field of every page is drawn or is bookkeeping (`secret`, fields ending `_asked`), and a test holds that.
- A socket is a small square inset in a cell's edge with a mark in the pen of the signal it carries: heard, wrote, turned away, asks, kept or shown. Inputs sit on the left beside their row, outputs on the right, slots on the bottom, in one fixed order kept in `src/conky/tokens.json` with each kind's mark and word. A connector runs from an output socket to an input socket of the same kind and ends in a plug. Colour is structural here only: a socket and its connector say what flows.
- An expression is laid out in lines by `bench/expression.py` (break before `&&` and `||`, then before the arms of a ternary, then before each chained call after the first; never inside a string, number or name) and printed as laid out, never reflowed.
- The view measures every cell before layout with each value at its longest, hands the sizes and socket positions to ELK, and lays out again when a drawn cell's content outgrew its box. That nothing overflows, nothing overlaps except by containment, members sit inside their space with room, sockets do not overlap, edges end on sockets of their kind and contrast is enough are tested on every published card in both densities and both looks.
- A crowded space is drawn in labelled regions, one arrangement a question it answered: the notes shown to it as small cells with a line of text each, the answering note in teal, and the notes not shown as numbered squares with their count. Term pages sit in a group of their own. Notes that arrive with nothing else happening come several to a step.
- The interactive view opens a side panel on a click: the page as of the current step, rendered by `marked` or as its source highlighted by `highlight.js` in colours from the tokens.

## Consequences

- Sockets are fixed-side ELK ports at the positions React Flow measured. A refinement in which ELK chooses the edge a board of sockets sits on is not built; this form is.
- Socket labels are ELK port labels outside the cell, so they never crowd a row. They can sit near a connector passing a space's frame.
- The README images stay raster (animated WebP and PNG), rendered with the system faces the token file names; see the status page for the SVG trial.
- The timeline keeps each page's source as committed, so published cards were published again from their records.
