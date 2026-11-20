---
kind: decision
title: Clean slate
status: accepted
date: 2026-11-20
source: operator
---

# 0001 Clean slate

## Decision

Nothing already built has to stay. Existing work is reference, not an obligation.

## Basis

Operator. The earlier Rust code was stand-in scaffolding: guard checks were string matches, nothing ran in a sandbox, and keys were ephemeral. It was deleted and remains in Git history.

## Consequences

- Any earlier design or code can be replaced without a compatibility argument.
- Old work may be consulted through Git history but binds nothing.
