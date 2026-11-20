---
kind: decision
title: Evidence, not scripts
status: accepted
date: 2026-11-20
source: maintainers
---

# 0013 Evidence, not scripts

## Context

A scripted demonstration shows only the cases its author chose, so it can look exactly like a real measurement. A number printed by a script is a hypothesis, not a result.

## Decision

Benchmark results come only from unscripted runs, with the run count and raw traces kept. A rule or check counts as real only if a test fails when it is removed.

## Consequences

- Model claims and scripted output are hypotheses, not results.
- A result without its run count and traces is not reported.
- No benchmark run has been made.

See [rules-not-requests](../essays/rules-not-requests.md).
