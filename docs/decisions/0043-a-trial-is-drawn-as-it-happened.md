---
kind: decision
title: A trial is drawn as it happened
status: accepted
date: 2026-11-20
source: maintainers
arch:
  items:
  - kind: unplaced
    name: a trial is drawn as it happened
    text: A card's recorded draw is published with a picture drawn from the vault's own history, by components that follow the page archetypes and a layout that places them.
---

# 0043 A trial is drawn as it happened

## Context

- A trial's verdict is one line, and a number says little about what a character did. The vault already holds the whole story as signed history, so a picture can be read from it with no model call.
- The README already carries a generated benchmark block ([decision 0032](0032-results-publish-themselves.md)). Trials publish the same way: from the run files, never by hand.
- A first version drew the pictures with code of its own: components, a layered layout and an SVG animation. That is a diagramming tool, and the project is not one to maintain.
- Prior art considered: D2 (text in, nested containers, ELK layout, themes, steps packed into one animated SVG, one binary, no browser, MPL-2.0 and used as a program, not vendored); Mermaid (needs a browser to render, little control of nesting and style); draw.io (a graphical editor, not text in); React Flow with ELK (a library inside a web page, so a page to host and keep).

## Decision

The project describes the graph and D2 draws it. `bench/dynamics.py` is a small codec from a timeline to D2 text, and `bench/timeline.py` reads a vault's history into plain events. A card's run is published under `docs/results/cards/<card>/`: the rows (without vault paths), the observations, the verdict, `timeline.json`, `run.json`, and two pictures as text, `dynamics.d2` (one step an event, every component declared up front and revealed at its step, so the layout does not move) and `topology.d2` (the final state, every page a cell with its fields, rules, hears and plugs panels, and edges that leave from the row they belong to). When a `d2` program is found (`CONKY_D2`, or on PATH) it draws `dynamics.svg` and `topology.svg`; when it is not, the text is written, the SVGs are left alone and the command says so.

- One table maps archetype to shape (`SHAPES`, from the `kind.*` archetypes, classified from the page by one function) and one list names the panels (`PANELS`).
- Colours, weights, dashes and sizes come from `src/conky/tokens.json`, the one token file, through D2's theme variables and shared classes. Colour carries a meaning only: amber for what a character added, pink for a refusal, blue for what is heard, teal for what was kept or passed, violet for a model's thought.
- The docs rule that the README carries at most three figures now names the generated benchmark and dynamics blocks as carried in addition, because they publish themselves from run files.

## Consequences

- No layout, drawing or animation code in the project; a better layout or look comes from D2 or its configuration.
- D2 takes one colour for a style set in the text, so the pens are the light values in both looks; the ground, ink and lines follow the viewer's light or dark. D2 also takes whole numbers for stroke widths and font sizes of at least 8, so the weights and sizes in the token file are rounded to them.
- Five draws support no claim, and the board says so.
