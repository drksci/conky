---
kind: decision
title: A trial is drawn as it happened
status: accepted
date: 2026-11-21
source: maintainers
arch:
  items:
  - kind: unplaced
    name: a trial is drawn as it happened
    text: A card's recorded draw is published as a graph with steps, read from the vault's own history, and one view draws it, in a browser and as the pictures in the README.
---

# 0043 A trial is drawn as it happened

## Context

- A trial's verdict is one line, and a number says little about what a character did. The vault already holds the whole story as signed history, so a picture can be read from it with no model call.
- The README already carries a generated benchmark block ([decision 0032](0032-results-publish-themselves.md)). Trials publish the same way: from the run files, never by hand.
- The same picture should serve two readers: a person stepping through a trial in a browser, and the README, which shows it as an image.
- Prior art considered:
  - Hand-written SVG with a layout of its own: dropped, it reinvents layout and is a diagramming tool to maintain.
  - D2: tried and dropped. Its shapes are fixed, it takes one colour for a style and so one pen for both looks, its steps are whole frames swapped, and it cannot become an interactive view.
  - Mermaid: little control of nesting, ports and style.
  - draw.io: a graphical editor, not text in.
  - React Flow (`@xyflow/react`, MIT) with ELK (`elkjs`, EPL-2.0) layered layout: the standard pairing for node graphs with nested groups and ports. Chosen.

## Decision

The project describes, React Flow with ELK draws.

- `bench/dynamics.py` reads a draw's timeline (`bench/timeline.py`) into `graph.json` beside the card's records: nodes (a page each, with the archetype from the one classifier, its space as parent, and its rows grouped in panels: fields, rules, listens for, reaches; a rule carries its body and the names it reads, from `conky.rules.reads`), edges (heard, wrote, caused, turned away, asks; each may end on a row), and steps (a caption in plain words, what appears, what changes, the subject with the meaning of its pen, what is dimmed). The view classifies and infers nothing.
- `viewer/` is one small app (Vite, React, TypeScript, `@xyflow/react`, `elkjs`, `lucide-react` for line symbols). One cell form for every page; a space is a parent node holding its members; rows are ports. Cells are drawn first and measured by React Flow, ELK lays them out from those sizes with hierarchy and fixed ports, and `fitView` frames the result. Colours, weights, dashes, sizes, spaces and symbols come only from `src/conky/tokens.json`, turned into CSS variables when the view is built. A pen marks only the subject of a step, by its meaning.
- `npm run render` in `viewer/` opens the built view headless (Playwright's Chromium, already on the machine) and writes per card `dynamics-light.webp` and `dynamics-dark.webp` (animated WebP: it plays in a GitHub README and keeps the transparent ground) and `topology-light.png` and `topology-dark.png`. The README block and the board show them with `<picture>` by colour scheme.
- Publishing without Node writes the records and `graph.json`, leaves the pictures alone and says what to run.

## Consequences

- Layout and drawing are libraries; the project keeps the description, the cell components and one stylesheet.
- ELK moves a port on the border of a space it lays out with its members, so an edge into a space's row is turned onto its handle just before the border. The edge is React Flow's `BaseEdge` along ELK's route, with React Flow's own arrowhead: its step and bezier edges draw their own path between handles, which crosses other edges and stacks labels.
- React Flow's attribution is hidden in the rendered images, which its MIT licence allows; the interactive view keeps it.
- The view needs Node 20 or later and its packages (`npm ci`); the Python checks run the view's test only when they are installed.
- Five draws support no claim, and the board says so.
