---
kind: decision
title: Evidence, not scripts
status: accepted
date: 2026-11-20
source: architect
---

# 0010 Evidence, not scripts

## Decision

Benchmark results come only from unscripted runs, with the run count and raw traces kept.

## Basis

Architect finding: the earlier scripted demo printed hard-coded numbers. It was removed.

## Consequences

- Model claims and scripted output are hypotheses, not results.
- A result without its run count and traces is not reported.

See [rules-not-requests](../essays/rules-not-requests.md).
