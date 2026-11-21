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

The address takes `?graph=<url>&mode=dynamics|topology&step=N&theme=light|dark&bare=1&explore=1`. `bare=1` is the picture alone, as the README shows it. `explore=1` is for a large graph: the whole of it fits the frame, three buttons bring the reader closer, further or back to everything, and a cell shows more the closer the reader comes (a name on a box from far off, what it holds and how it is bound nearer, everything close up).

## Restyling

Edit only `src/view.css` or the token file `src/conky/tokens.json`. Every colour, weight, dash, size, space and symbol is a token; the build turns them into CSS variables (`--ds-color-ink`, `--ds-pen-coral`, `--ds-size-base` and so on, see `tokens.mjs`), switched for light and dark by `prefers-color-scheme` or `data-theme`. A meaning (`.is-added`, `.is-refused`, `.is-heard`, `.is-kept`, `.is-thought`) sets `--pen` to its pen, and the stylesheet marks a subject with `var(--pen)`: an edge, a line under a name or a bar beside a row, never the words, which stay ink. A kind of port (`.signal-heard`, `.signal-wrote` and so on) sets `--signal` to its colour from the token file's `port` section (`--ds-port-<kind>`), for the port, the chips that name it and the cables it leaves by.

## Parts

- `src/components/`: the cell and its header, panels (text, holds, bound by, when and then) and footer with its slots; the port board, one of a cell's pair (left and right, or top and bottom), a thin strip outside an edge that runs its whole length; the port, a flat square block as wide as the board is thick, in its kind's colour with its short name (`hr0`, `wr0`, `as0`) in white, solid when something is plugged in and, when nothing is, only a bar in its colour on the edge that touches the cell (`port.idle_bar` of its depth) with its name in ink, and the chip that names it at the end of its row, in the side panel and in the legend; the space, the note and the region a crowded space draws its notes in; the function block of an expression; a symbol; the connector; the caption, the legend, the scrubber and the side panel, one file each.
- `src/graph.ts`: the shape of `graph.json` and what one frame and one density (compact in the steps, detailed in the final state) show of it.
- `src/node-types.ts`: the one table of node types, keyed by the archetypes the Python side emits. Adding an archetype is one entry there and one class in the stylesheet.
- `src/layout.ts`: the graph in ELK's terms and back. A first pass with free ports shows which way a cell's connections run, and the cell takes the pair of boards on that axis (a space always left and right); inputs sit on the first board, outputs and slots on the second, as `graph.json` says, in a row in the standard order. The second pass lays the graph out with the boards as part of each cell. ELK keeps the order of a space's ports only among the connected ones, so a space's ports are set in their row after it, where the connected ones come closest to ELK's routes. Every hop of a connection is one ELK edge, so a connection into a space runs to a port on the space's border and on inside, as the record says. Only ELK's options are tuned there.
- `scripts/render.mjs`: the headless pictures, with Playwright's Chromium already on the machine and ffmpeg.
- `test/smoke.mjs`: every published card, both densities and both looks, checked for overflow, overlap, containment, port kinds, contrast, and the boards: a cell's boards are a left and right or a top and bottom pair, every board runs the whole length of its edge, every port is a square as wide as its board is thick with its name inside it, every port in `graph.json` is drawn with its name, solid when plugged in and a bar on the cell's side when not, white names keep 4.5 to 1 on their block, every wire ends on two ports on boards, boards keep clear of bodies and each other, ports on a board are in the standard order, and no wire enters a space except through a port on its board. It also checks the port colours: white on each, and every two kinds told apart with normal and simulated colour-blind vision.

Clicking a cell in the interactive view opens the page as of the current step, rendered or as its highlighted source.
