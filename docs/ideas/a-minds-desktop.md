---
kind: idea
title: A mind's desktop
status: idea
date: 2026-11-23
source: "ideas/a2ui.md, ideas/compositor.md, ideas/said-beside.md, ideas/trace.md, ideas/looks.md, viewer/; outside: SGI File System Navigator (https://en.wikipedia.org/wiki/Fsn_(file_manager)), OBS Studio scenes and recording (https://obsproject.com/kb/scenes-and-sources), replay files in real-time strategy games, which redraw a match from its recorded inputs rather than from video"
arch:
  items:
  - kind: part
    name: part.screen.desktop
    layer: layer.edge
    text: A desktop drawn from what one character read, said and did, live from the history and the lines said beside it, or replayed from them, or rendered to film.
    state: idea
---

# A mind's desktop

## Idea

Rung: idea. Nothing here is built.

A character at work reads pages, asks, waits and writes. The history already records each of these: a `Read` trailer names every page a change was made from, and a reaction names its cause. The lines said beside the vault name an ask that has started and not ended. Together they say what the character has open at any moment.

Draw that as a desktop. Each page the character reads opens as a window, and the window closes when the character's attention moves on. An ask in flight is a window with text arriving in it. A write lands as the window's page changing, and a refusal shows beside it. When the character is joined to a perceiver, such as a camera, a sensor or a game's view, what the perceiver delivers is one more window, streamed as it arrives. A person can click any window to open the page it shows. The desktop is the same screen a person would have if they did the work by hand.

Views are swapped, not built twice. The perceiver's view and the desktop are two sources on one screen, as scenes in a broadcast mixer are. A person may watch either, or both side by side.

Replay is free. The desktop is derived from the history and the lines beside it, so stepping through a finished run draws the same windows in the same order as watching it live. A run's recording is its record, not a video file.

Film is one more renderer. A page drawn in a browser can be captured frame by frame, so the same replay that a person clicks through can be written to video with no second set of drawings. The look, whether flat windows or pages set out as ground to fly over in three dimensions, is a [look](looks.md): a page that says how the screen is drawn.

## Composes from

The history and its `Read`, `Cause` and `From` trailers ([the trace](trace.md)), and the lines said beside the vault ([what is happening can be watched](said-beside.md)). The [compositor](compositor.md) and [a screen from the pages](a2ui.md) give the layout, a [look](looks.md) gives its drawing, and the whole is derived data ([decision 0017](../decisions/0017-derived-data.md)). The view in `viewer/` already draws a trial from its record.

One thing is left over: which pages a character has open at a moment, its working set. It is derived from the trailers by a stated rule (a page read stays open until a later change of the same character no longer reads it), so it adds no primitive.

## Removes

A separate recorder for watching an agent, a separate screen capture for a film, and hand-made animations of an agent's thinking that the record does not support.

## Falsifying test

- The history of a run is the same with and without the desktop open.
- A replay of a finished run opens and closes the same windows, in the same order, as the live view did.
- A video rendered from a replay matches the interactive replay at the same step, frame for frame.
- Every window on the desktop traces to a trailer or to a line said beside the vault. A window with no such source shows the idea has started inventing.

## Open questions

- The rule for when a window closes: on the next change that does not read the page, after a quiet interval, or when the working set passes a size.
- How a perceiver's stream is said beside the vault, and how much of it is kept for replay, since a moment said beside the vault cannot be rebuilt.
- Whether a person's click on a window is recorded, and if so as what: a read by the person, which is an ordinary write, or nothing.
