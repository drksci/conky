---
kind: decision
title: Measures are self-watches
status: accepted
date: 2026-11-20
source: architect
---

# 0019 Measures are self-watches

## Decision

No new concept is added for measures or pressure. A measure is a page that watches itself: a `watch` entry whose `on` is the page's own name, which sets a field computed from the page's state. Pressure is a measure. Because the computed value is written as an ordinary recorded event, replaying the log never re-evaluates an expression, so history stays reproducible even if the expression language changes.

## Basis

Architect. It adds no word and no mechanism (rule: build a new concept from existing words), and it keeps replay independent of expression evaluation.

## Consequences

- Watch expressions can use `size` and `other_size`, the byte lengths of the watching page and of the page just written.
- A measure costs one recorded event each time its value changes. That makes measures visible in the log, and it also means a noisy measure makes a noisy log.

## Open questions

Whether measures that change on every write should be coarsened by convention (for example integer steps) to keep the log quiet.
