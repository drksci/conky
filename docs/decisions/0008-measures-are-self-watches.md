---
kind: decision
title: Measures are self-watches
status: accepted
date: 2026-11-20
source: maintainers
arch:
  covers:
  - law:measure-is-a-self-watch
  - flow:measure-and-pressure
---

# 0008 Measures are self-watches

## Context

- Some limits are better expressed as a rising signal than as a refusal, which needs a number computed from a page's state and kept up to date.
- A new concept for it would break the aim of building from existing words.
- A value computed at read time would make history depend on the expression language.

## Decision

A measure is a page that watches itself: a `watch` entry whose `on` is the page's own name, which sets a field computed from the page's state. Pressure is a measure. No new concept is added.

## Consequences

- The computed value is written as an ordinary recorded event, so reading history never evaluates an expression and history stays reproducible even if the expression language changes.
- Watch expressions can use `size` and `other_size`, the byte lengths of the watching page and of the page just written.
- A measure costs one recorded event each time its value changes, so measures are visible in the log, and a noisy measure makes a noisy log.

## Open questions

Whether measures that change on every write should be coarsened by convention (for example integer steps) to keep the log quiet.
