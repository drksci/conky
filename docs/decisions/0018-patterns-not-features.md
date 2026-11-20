---
kind: decision
title: Patterns, not features
status: accepted
date: 2026-11-20
source: operator
---

# 0018 Patterns, not features

## Decision

Domain structures such as accounting are never built into the runtime. They are patterns: recipes that compose the existing words. The runtime only gains general primitives.

## Basis

The operator proposed replacing the ledger with a pattern library similar to agent skills. The architect agreed: a ledger is one domain's structure, and building it in would break the rule that a new concept is composed from existing words or removes one.

See [patterns](../ideas/patterns.md) and [ledger](../ideas/ledger.md).

## Consequences

- The ledger step leaves the roadmap.
- A grouped write (several pages changed together, all or nothing) and a pattern library take its place.

Link: [patterns](../ideas/patterns.md), [ledger](../ideas/ledger.md).

## Open questions

- Where the pattern library lives: inside each vault, or in a shared vault that others link to.
- How a working structure is promoted into a pattern.
