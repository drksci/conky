---
kind: decision
title: Build on bedrock
status: accepted
date: 2026-11-20
source: maintainers
---

# 0031 Build on bedrock

## Context

- The benchmark, the connectors and the page-writing capability each stack on the layer below. A fault in a lower layer shows up later as many faults above it.
- A batch of model-backed runs is the most expensive place to find such a fault.
- The system already has what stepping needs: every change is one recorded event, and a run can be stopped on a condition and resumed ([one step at a time](../ideas/stepping.md)).

## Decision

A new layer is run one step at a time, by hand or under a stop point, and looked at, before anything is built on it. Nothing runs in bulk, and nothing costly runs at all, until a single step has been walked through and seen to be right.

For the benchmark this is a walkthrough that advances one stage at a time and stops at the first stage that fails. The same walkthrough is used for the first live model call.

## Consequences

- Each layer lands with its own walk stage, and where it needs no network, a test of that stage.
- Stop points and stepping are built early in a runner, not added after a failure.
- A batch run is started only from a walkthrough that passed on the same code.
- A stepped or hand-resumed run is evidence that a layer works. It is never reported as a result.
