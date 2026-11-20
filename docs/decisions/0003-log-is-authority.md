---
kind: decision
title: The log is the authority
status: superseded
date: 2026-11-20
source: architect
---

# 0003 The log is the authority

Superseded by [0021](0021-git-is-the-store.md). The principle (history is the authority, state is a projection, what is not recorded did not happen) stands; the store changed.

## Decision

The append-only signed event log is the authority. Pages are projections that can be rebuilt from it byte for byte. A transition that is not recorded did not happen, and refused writes are recorded too.

## Basis

Architect, drawing on a lesson recorded in the Alphaville agency project.

## Consequences

- No migrations are needed: a new shape is a new projection of the same log.
- `verify` and `rebuild` are possible.
- A vault can be copied and still verify.

See [the-log-is-the-truth](../essays/the-log-is-the-truth.md).
