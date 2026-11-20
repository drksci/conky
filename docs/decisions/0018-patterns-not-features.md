---
kind: decision
title: Patterns, not features
status: accepted
date: 2026-11-20
source: operator
---

# 0018 Patterns, not features

## Decision

Domain structures such as accounting are never built into the runtime. They are patterns: recipes that compose the existing words. The runtime only gains general primitives. Patterns are not shipped as a catalogue; they are made on demand from goldens by a pattern maker.

## Basis

The operator proposed replacing the ledger with a pattern maker similar to a skill generator. The architect agreed: a ledger is one domain's structure, and building it in would break the rule that a new concept is composed from existing words or removes one.

See [patterns](../ideas/patterns.md) and [ledger](../ideas/ledger.md).

## Consequences

- The ledger step leaves the roadmap.
- A grouped write (several pages changed together, all or nothing) and a pattern maker take its place.

Link: [patterns](../ideas/patterns.md), [ledger](../ideas/ledger.md).

## Open questions

- Where made patterns are kept: inside the vault that made them, or shared between vaults.
- How a working structure is promoted into a pattern.
