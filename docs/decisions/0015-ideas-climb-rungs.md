---
kind: decision
title: Ideas climb rungs
status: accepted
date: 2026-11-20
source: maintainers
---

# 0015 Ideas climb rungs

## Context

Candidate ideas are cheap and the code is not. Without a marker, an idea can be mistaken for a requirement or for something proven.

## Decision

An idea climbs one rung at a time: idea, folded, enforced, proven.

- idea: a page in `docs/ideas/` naming its source.
- folded: in the design documents with its law, what it composes from, what it removes, and the test that would falsify it.
- enforced: code plus a test that fails when the law is broken.
- proven: measured in an unscripted run.

## Consequences

- Every idea page states its rung.
- An idea is not a requirement until it is enforced.
