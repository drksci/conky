---
kind: decision
title: Benchmark shape
status: open
date: 2026-11-20
source: maintainers
arch:
  covers:
  - part:benchmark
---

# 0014 Benchmark shape

## Context

Claims about how conky compares with other agent harnesses need a fair test, and a scenario written for one harness favours it.

## Decision

A benchmark scenario is a set of harness-neutral documents: seed prompt, starting state, observables and scoring. It runs through an adapter on the same model and budget for every harness, and includes the assimilation test: hand a fresh consumer only a stopped vault and score whether it resumes correctly. Status is open because none of this is built.

## Consequences

- Scenarios contain no harness-specific steps.
- Comparisons are like for like on model and budget.

See [assimilation-test](../ideas/assimilation-test.md).

## Open questions

- Whether to adopt an existing long-horizon organisation benchmark listed in the [research index](../research/dair-2026.md) (MerchantBench, 1,000 Synthetic Computers) as the shared scenario rather than invent one, so results compare with published numbers.
