---
kind: reference
title: "The view"
status: draft
date: 2026-11-21
source: "viewer/"
---

# The view

One small app that draws a trial from its record: a `graph.json` written by `bench/dynamics.py` beside a card's published files under `docs/results/cards/<card>/`. It draws what the file says and adds nothing ([decision 0043](../docs/decisions/0043-a-trial-is-drawn-as-it-happened.md)).

```bash
npm ci            # once
npm run view      # serves the repository and prints an address to open
npm run render    # writes the pictures of every published card
npm test          # builds, then a headless smoke test
```

The address takes `?graph=<url>&mode=dynamics|topology&step=N&theme=light|dark&bare=1`. `bare=1` is the picture alone, as the README shows it.

## Restyling

Edit only `src/view.css` or the token file `src/conky/tokens.json`. Every colour, weight, dash, size, space and symbol is a token; the build turns them into CSS variables (`--ds-color-ink`, `--ds-pen-pink`, `--ds-size-base` and so on, see `tokens.mjs`), switched for light and dark by `prefers-color-scheme` or `data-theme`. A meaning (`.is-added`, `.is-refused`, `.is-heard`, `.is-kept`, `.is-thought`) sets `--pen` to its pen, and the stylesheet colours a subject with `var(--pen)`.

## Parts

- `src/components/`: the cell and its header, panels (text, holds, bound by, when and then) and footer of slots; the socket; the space, the note and the region a crowded space draws its notes in; the function block of an expression; a symbol; the connector; the caption, the legend, the scrubber and the side panel, one file each.
- `src/graph.ts`: the shape of `graph.json` and what one frame and one density (compact in the steps, detailed in the final state) show of it.
- `src/node-types.ts`: the one table of node types, keyed by the archetypes the Python side emits. Adding an archetype is one entry there and one class in the stylesheet.
- `src/layout.ts`: the graph in ELK's terms and back. Sockets are fixed-side ports at the positions React Flow measured, with their labels as ELK port labels; only ELK's options are tuned there.
- `scripts/render.mjs`: the headless pictures, with Playwright's Chromium already on the machine and ffmpeg.
- `test/smoke.mjs`: every published card, both densities and both looks, checked for overflow, overlap, containment, socket kinds and contrast.

Clicking a cell in the interactive view opens the page as of the current step, rendered or as its highlighted source.
