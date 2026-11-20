---
kind: decision
title: No debt, no down-migrations
status: accepted
date: 2026-11-20
source: maintainers
---

# 0010 No debt, no down-migrations

## Context

Compatibility shims, dead code and migration ladders accumulate and make a small system hard to read. A change of data shape is the usual source of them.

## Decision

No compatibility shims, dead code or fix-later notes, and no down-migrations or migration ladders. Data lives in three simple primitives in open formats: document (Markdown with frontmatter), table (Parquet), stream (append-only log). A change of shape is a forward re-projection.

## Consequences

- Replacing something removes the old thing in the same change.
- Only document and stream exist so far; table is not built (see the [roadmap](../project/roadmap.md)).
