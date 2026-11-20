---
kind: decision
title: Patterns, not features
status: accepted
date: 2026-11-20
source: maintainers
---

# 0009 Patterns, not features

## Context

Domain structures such as double-entry accounting are tempting to build into the runtime. A built-in ledger is one domain's structure, and building it in would break the rule that a new concept is composed from existing words or removes one.

## Decision

Domain structures are never built into the runtime. They are patterns: recipes that compose the existing words. The runtime only gains general primitives. Patterns are not shipped as a catalogue; they are made on demand from worked examples by a pattern maker. See [patterns](../ideas/patterns.md) and [ledger](../ideas/ledger.md).

## Consequences

- A built-in ledger is not on the roadmap.
- A grouped write (several pages changed together, all or nothing) and a pattern maker take its place.

## Open questions

- Where made patterns are kept: inside the vault that made them, or shared between vaults.
- How a working structure is promoted into a pattern.
