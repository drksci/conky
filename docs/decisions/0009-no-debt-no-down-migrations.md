---
kind: decision
title: No debt, no down-migrations
status: accepted
date: 2026-11-20
source: operator
---

# 0009 No debt, no down-migrations

## Decision

No compatibility shims, dead code or "fix later" notes, and no down-migrations or migration ladders. Data lives in three simple primitives in open formats: document (Markdown with frontmatter), table (Parquet), stream (append-only log). A change of shape is a forward re-projection.

## Basis

Operator.

## Consequences

- Replacing something removes the old thing in the same change.
- Only document and stream exist so far; table is not built (see the [roadmap](../project/roadmap.md)).
