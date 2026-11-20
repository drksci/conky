---
kind: idea
title: Energy unit
status: idea
date: 2026-11-20
source: maintainers
---

# Energy unit

## Idea

A synthetic unit of value flow, which conserves only if the conversion into it is itself recorded.

Energy and cost become measures once [model pages](model-pages.md) report them. Token counts are recorded on each model answer, but nothing yet turns them into a measure. The unit stays a pattern over the ledger, not a runtime feature.

## Composes from

The [ledger](ledger.md) and the log.

## Removes

Not yet worked out.

## Falsifying test

Value enters or leaves the unit without a recorded conversion and the totals still balance.
