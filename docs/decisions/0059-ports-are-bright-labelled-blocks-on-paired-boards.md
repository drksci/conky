---
kind: decision
title: Ports are bright labelled blocks on paired boards
status: accepted
date: 2026-11-21
source: maintainers
arch:
  items:
  - kind: unplaced
    name: a port is a named block on a pair of boards
    text: In a drawn trial every port a cell has is a block coloured by its kind and named by a prefix and an index, on a pair of boards on one axis, inputs on the first and outputs and slots on the second, solid when plugged in and hatched when not.
---

# 0059 Ports are bright labelled blocks on paired boards

## Context

- [Decision 0052](0052-wires-attach-to-port-boards-and-parents-broker-crossings.md) drew a small square socket with words beside it on a board on any edge that had one, and only where something plugged in. A socket was tied to its row by a small number when the two were apart. The pictures read as words and numbers rather than as a frame of ports: a cell could carry one board on its left and one below, a side board wrapped its words onto two lines, and what a cell could take in but had not yet was invisible.
- Prior art: the back of a home router or a network switch, where every port is a bright, coloured, labelled socket in a neat row, some with a cable plugged in and some empty; interface names (`eth0`, `wlan1`), a fixed prefix by kind and an index, used in every tool that refers to the port; colour-coded cables that keep the colour of what they leave. Colour-vision checks follow the simulation matrices of Machado, Oliveira and Fernandes (2009) and distances in OKLab.

## Decision

- A cell with any port has a pair of boards on one axis: left and right, or top and bottom, never a mix. The axis is the one most of its connections run along in a first layout with free ports; a space always takes left and right, so a jumper never crosses its own rows. Both boards are drawn, each the whole length of its edge, a plain one too, so the pair reads as one frame.
- `graph.json` says which board of the pair each port sits on (`pair`): inputs on the first (left or top), outputs and slots on the second; a port on a wall is an input where a connection enters the space and an output where it leaves. Within a board the ports keep the standard order, in a row an even gap apart.
- A port is a flat square block as wide as its board is thick (`space.wide + space.fine`), in a bright colour for its kind from the new `port` section of `src/conky/tokens.json`, with its short name in tiny white code type. The colours are a carve-out from the five pens, as the chart palette is: ports have to be told apart at a glance at a very small size. Every colour keeps white at a contrast of at least 4.5, and `npm test` checks that every two kinds stay apart in OKLab with normal vision and with protanopia, deuteranopia and tritanopia simulated. A dark-page value is lifted where the cable it colours needs a contrast of 3 on the dark ground.
- A port's short name is a fixed prefix for its kind and its index among the cell's ports of that kind, from 0 in the standard order (`hr0`, `wr0`, `as0`). The prefixes sit in the socket table of the token file beside the words, and the Python side emits the table into `graph.json` (`ports`) and each port's `name`. The same name is on the block, as a chip at the end of the row the port belongs to (a watch entry's input after its "when" and output after its "then", a record row, a slot in the footer, and a rule on the walls it judged at), in the side panel and in the legend, which lists each prefix with its word and colour. The small row numbers and the fixed one-letter marks are gone.
- Every port a cell has is drawn, plugged in or not: every watch entry now has an input and an output port, and every slot its port. A port with something plugged in is solid; one with nothing is the same block hatched in its colour with a dotted edge, its name in ink on a patch of ground. A port turns solid at the step its cable arrives.
- Cables take the colour of the port they leave and plug into the block's outer face; a jumper goes on from the inner face of a wall port. A wall still shows the rules it judged, a shield or the refusal symbol, on a line above the port.
- ELK keeps the order of a compound node's ports only among those with a connection and puts the rest after them, and does not keep fixed positions on a compound node laid out with its members. A space's connected ports are therefore given to ELK in their order, and the view then sets every port of the space in its row, placed where the connected ones come closest to where ELK routed them; a cable whose end moved turns onto its port with square corners just outside the board.

## Consequences

- What 0052 guaranteed and what changes: every hop still runs between two ports of one kind of signal, a crossing still goes through a port on the wall, the standard order still holds on every board, a board still runs its whole edge, and a port still fills at the step its wire arrives. A port is no longer chosen to face its connection one by one: the pair faces the way most of them run, and a cable may turn round a cell to reach the other board. The words beside a socket are gone from the boards; what a slot holds is written in the footer beside its port's name.
- A port's name in a hatched block is ink, not its kind's colour: a colour dark enough to carry white text cannot also carry its own text on the dark page at 4.5.
- The prose of the trials board, written by `bench/dynamics.py` into `docs/research/trials.md`, still describes small sockets coloured by the pens. It is not updated in this change.
