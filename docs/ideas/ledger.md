---
kind: idea
title: Ledger
status: idea
date: 2026-11-20
source: maintainers
---

# Ledger

## Idea

Every movement of money, stock or inference cost debits one place and credits another, so the total is conserved.

## Composes from

Rules (a conservation check is a rule over a write) and the log.

## Removes

Ad hoc balance fields kept consistent by hand.

## Falsifying test

A sequence of recorded writes in which the total changes without a recorded source or sink and the runtime accepts it.

## Standing

A built-in ledger was judged a bad idea. The ledger stays a pattern, never a runtime feature, and the cost of model calls would be one use of it. See [patterns](patterns.md), where the conservation need survives as the grouped write.
