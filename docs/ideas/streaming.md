---
kind: idea
title: Text as it arrives
status: idea
date: 2026-11-20
source: "research/streams-and-trees.md (AG-UI text events in start, content and end pieces; Server-Sent Events with a resume point) and research/gaps.md, which gives streaming no verdict because the harness comparison does not cover it"
arch:
  items:
  - kind: part
    name: part.screen.live
    layer: layer.edge
    text: A model's answer shown to a person while it arrives, as derived data, with only the finished answer written.
    state: idea
    roadmap: R36
---

# Text as it arrives

## Idea

A person watching a screen wants to see an answer form. The history wants one event that holds the whole answer. Both hold when the pieces are derived data. The screen or a connector shows the text as it arrives and keeps none of it, and the runtime writes the finished answer as the one signed write it already is. A stream that stops leaves a refusal starting `model:`, as a failed call does today. No partial answer is ever an event, so replay and the cache are unchanged.

## Composes from

An ask, [the screen](a2ui.md), and derived data ([decision 0017](../decisions/0017-derived-data.md)).

## Removes

Partial state in the history.

## Falsifying test

Cutting a streamed answer short leaves the history exactly as an unanswered ask leaves it. When the stream completes, the text shown and the answer written are the same bytes.

## Open questions

- The stream's format, Server-Sent Events or AG-UI text events, is the screen's choice and belongs with its update step (R11d).
