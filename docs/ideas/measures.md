---
kind: idea
title: Measures
status: enforced
date: 2026-11-20
source: maintainers
arch:
  covers:
  - law:pressure-not-walls
  - law:measure-is-a-self-watch
  - flow:measure-and-pressure
  - archetype:measure-bearing page
  items:
  - kind: stage
    name: measures
    phase: attention
    text: One measure mechanism could serve attention, decay and metrics. Only pressure is built.
    state: idea
---

# Measures

## Idea

A measure is a pure function over pages and the log, like a rule that returns a number. One mechanism could serve attention, decay and metrics.

## First candidate: pressure

Size can build pressure instead of raising a wall. A page that grows past what its space finds comfortable is still written, but its pressure rises, and at a threshold a reaction fires (the page is asked to split, or a tidy-up starts) with no model call. Limits then act like friction that is resolved in the background, not a gate that stops work.

A hard rule remains the right tool for what must never happen, such as a negative balance. Pressure is for what should be noticed and dealt with.

Falsifying test: with pressure in place, pages in a long run stay bounded without any refused write and without inference spent on housekeeping.

## Composes from

Rules (pure, over pages) and the log.

## Removes

Separate mechanisms for attention, decay and metrics, if one measure can serve each.

## Falsifying test

A measure that needs a clock, randomness or input outside pages and the log to compute what it was meant to.

## What was built

A measure is a page watching itself: a `watch` entry whose `on` is the page's own name. Watch expressions gained `size` (the byte length of the watching page) and `other_size` (the byte length of the page just written). Pressure is a self-watch such as `size / 400`, with a second entry setting a state when a threshold is passed. Decision: [0008](../decisions/0008-measures-are-self-watches.md). Essay: [pressure-not-walls](../essays/pressure-not-walls.md). Tests in `tests/test_laws.py`: pressure rises without refusing work, a threshold fires a reaction, a self-watch settles, replay needs no expressions, and `other_size` is visible.

## Still open

- Decay over time needs time to pass. It should arrive as an ordinary write to a clock page that others watch, not as a hidden timer.
- What a crowded page should do (split, summarise) needs a deterministic tool or a model-backed page. Neither is built.
