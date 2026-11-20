---
kind: decision
title: Benchmark shape
status: open
date: 2026-11-20
source: operator
---

# 0011 Benchmark shape

## Decision

A benchmark scenario is harness-neutral documents: seed prompt, starting state, observables and scoring. It runs through an adapter on the same model and budget for every harness. It includes the assimilation test: hand a fresh consumer only a stopped vault and score whether it resumes correctly.

## Basis

Operator. Status is open because none of this is built.

## Consequences

- Scenarios contain no harness-specific steps.
- Comparisons are like for like on model and budget.

See [assimilation-test](../ideas/assimilation-test.md).
