---
kind: decision
title: Wires attach to port boards, and a parent brokers what crosses its wall
status: accepted
date: 2026-11-21
source: maintainers
arch:
  items:
  - kind: unplaced
    name: a parent brokers what crosses its wall
    text: In a drawn trial every connection is a list of hops, and a hop that crosses a space's wall ends at a socket on that space's port board, where the space's rules judge a write into it.
---

# 0052 Wires attach to port boards, and a parent brokers what crosses its wall

## Context

- [Decision 0049](0049-a-cell-shows-the-whole-page.md) drew sockets inset in a cell's own frame on fixed sides: inputs on the left, outputs on the right, slots on the bottom. Wires wrapped around cells to reach a side that did not face what they connected to, a wire into a page inside a space ran straight through the space's wall, a socket's label was printed at both ends of a wire and could land on a wire passing a space's frame, and a rule's socket was drawn filled before the step whose wire plugged into it.
- The runtime does not let a write pass a wall unseen: every space a page is within judges a write to it by its rules for every page within, and a write it turns away never lands. The picture said otherwise.
- Prior art: a power board or a patch bay, a strip of sockets fixed to an edge with plugs seated in it; a bulkhead connector, which carries a cable through a wall with a socket on each face; ELK's port constraints (free sides, fixed order, fixed positions) and its hierarchical ports, which route an edge into a compound node through a port on its border.

## Decision

- `graph.json` gives every connection as a list of hops. A hop that crosses a space's wall ends at a socket on that space's board, and the next hop, a jumper, goes on from the inside of that socket. A write into a space carries, at that socket, the space's rules for every page within it as they stood at that write, each with whether it let the write through; a write turned away ends at the board of the space whose rule refused it and has no hop past it. It nests: a page two spaces deep is reached through two boards. The Python side works the hops out from the record, and the view draws them and infers nothing.
- A cell's sockets are one list, its board, in the standard order, which is the order of the socket table in `src/conky/tokens.json`. Which edge each socket faces is chosen by ELK: a first layout with free ports turns each socket toward what it connects to, and a second lays the graph out with a board on each edge that has sockets. A socket nothing plugs into (an empty or a standing slot) sits on the bottom board.
- A port board is its own thin rectangle attached outside one edge of the cell, with a hairline frame, so the body stays clean. It runs the whole edge: top and bottom boards the full width, taking the corners, side boards between them. Its thickness is fixed from the token spacing. Sockets and their words live only on boards: a kind word where a wire leaves, none where it arrives, a slot's word and what fills it, and at a wall the rules judged there, as a shield or the refusal symbol and, in the detailed density, the number the rule carries in the space's panel. A row and a socket not beside it share a small number.
- A socket is filled from the step its wire arrives, not before.
- `npm test` checks, on every published card in both densities and both looks, that every wire ends on two sockets on boards, boards keep clear of every body but the spaces that hold them and of each other, a board's sockets are in the standard order, a board runs the whole length of its edge, and no wire enters a space except through a socket on its board, beside the earlier checks. The Python tests check that hops are continuous, that each runs in one place, and that a refused write stops at the refusing board.

## Consequences

- What 0049 guaranteed and what changes: every edge still runs between two sockets of one kind of signal, now hop by hop. A watch entry no longer always has an input and an output socket: a socket is drawn only where a wire plugs in or a slot stands, since an empty input said nothing. The fixed per-side order in the token file is gone; the socket table's order is the one order.
- A write by a page to the space it is in (a keeper adding a rule to its own den) is still not drawn as a wire; the row says it.
- Side boards are thin and words wrap on them, so a long word ("turned away") takes two lines there.
- ELK cannot give a socket two faces: a wall socket is one port with the outer wire ending and the jumper starting on it, and the view draws the jumper's start as passing through the board.
