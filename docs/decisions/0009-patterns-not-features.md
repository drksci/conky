---
kind: decision
title: Patterns, not features
status: accepted
date: 2026-11-20
source: maintainers
arch:
  items:
  - kind: part
    name: pattern-maker
    layer: characters
    text: Domain structures are never built in. A pattern maker makes them on demand from worked examples.
    roadmap: R6
---

# 0009 Patterns, not features

## Context

Domain structures such as double-entry accounting are tempting to build into the runtime. A built-in ledger is one domain's structure, and it would break the rule that a new concept is composed from existing words or removes one.

## Decision

Domain structures are never built into the runtime. They are patterns, recipes that compose the existing words, and the runtime only gains general primitives. Patterns are not shipped as a catalogue: a pattern maker makes them on demand from worked examples. See [patterns](../ideas/patterns.md) and [ledger](../ideas/ledger.md).

## Consequences

- A built-in ledger is not on the roadmap.
- A grouped write (several pages changed together, all or nothing) and a pattern maker take its place.

## Open questions

- Where made patterns are kept: inside the vault that made them, or shared between vaults.
- How a working structure is promoted into a pattern.
