---
kind: idea
title: Measures
status: enforced
date: 2026-11-20
source: maintainers
---

# Measures

## Idea

A measure is a pure function over pages and the log, like a rule that returns a number. It could unify attention, decay and metrics.

## First candidate: pressure

Size can be treated not as a wall that refuses work but as a pressure that builds. A page that grows past what its space considers comfortable is still written, but its pressure rises, and at a threshold a reaction fires (for example the page is asked to split, or a tidy-up is triggered) with no model call and without the actor having to think about it. The aim is that limits act like friction that is felt and resolved in the background, rather than a gate that stops work.

A hard rule remains the right tool for things that must never happen (a negative balance). Pressure is for things that should be noticed and dealt with.

Falsifying test: with pressure in place, pages in a long run stay bounded without any refused write, and without spending inference on housekeeping.

## Composes from

Rules (pure, over pages) and the log.

## Removes

Separate mechanisms for attention, decay and metrics, if one measure can serve each.

## Falsifying test

A measure that needs a clock, randomness or input outside pages and the log to compute what it was meant to.

## What was built

A measure is a page watching itself: a `watch` entry whose `on` is the page's own name. Watch expressions gained `size` (the byte length of the watching page) and `other_size` (the byte length of the page just written). Pressure is a self-watch such as `size / 400`, with a second entry setting a state when a threshold is passed. Decision: [0008](../decisions/0008-measures-are-self-watches.md). Essay: [pressure-not-walls](../essays/pressure-not-walls.md). Tests in `tests/test_laws.py`: pressure rises without refusing work, a threshold fires a reaction, a self-watch settles, replay needs no expressions, and `other_size` is visible.

## Still open

- Decay over time needs a notion of time passing. It should arrive as an ordinary write to a clock page that others watch, not as a hidden timer.
- What a crowded page should then do about it (split, summarise) needs either a deterministic tool or a model-backed page. Neither is built.
