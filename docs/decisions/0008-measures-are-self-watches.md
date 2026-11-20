---
kind: decision
title: Measures are self-watches
status: accepted
date: 2026-11-20
source: maintainers
---

# 0008 Measures are self-watches

## Context

Some limits are better expressed as a rising signal than as a refusal. That needs a way to compute a number from a page's state and keep it up to date. Adding a new concept for it would break the aim of building from existing words, and a value computed at read time would make history depend on the expression language.

## Decision

No new concept is added for measures or pressure. A measure is a page that watches itself: a `watch` entry whose `on` is the page's own name, which sets a field computed from the page's state. Pressure is a measure. Because the computed value is written as an ordinary recorded event, reading history never evaluates an expression, so history stays reproducible even if the expression language changes.

## Consequences

- Watch expressions can use `size` and `other_size`, the byte lengths of the watching page and of the page just written.
- A measure costs one recorded event each time its value changes. That makes measures visible in the log, and it also means a noisy measure makes a noisy log.

## Open questions

Whether measures that change on every write should be coarsened by convention (for example integer steps) to keep the log quiet.
