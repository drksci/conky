---
kind: idea
title: Ledger
status: idea
date: 2026-11-20
source: maintainers
---

# Ledger

## Idea

Double-entry conservation for money, stock and inference cost: every movement debits one place and credits another, so the total is conserved.

## Composes from

Rules (a conservation check is a rule over a write) and the log.

## Removes

Ad hoc balance fields kept consistent by hand.

## Falsifying test

A sequence of recorded writes in which the total changes without a recorded source or sink and the runtime accepts it.

## Standing

The ledger stays a pattern and is never a runtime feature; cost recorded for model calls would be one use of it.


A built-in ledger was judged a bad idea. Accounting should be a pattern, not a runtime feature; see [patterns](patterns.md). The conservation need survives as the grouped write described there.
