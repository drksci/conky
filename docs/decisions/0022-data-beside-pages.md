---
kind: decision
title: Data beside pages
status: accepted
date: 2026-11-20
source: operator
---

# 0022 Data beside pages

## Decision

Small tables live in the vault as Parquet beside their page. Large or external data is referenced by a pointer carrying a content hash, using Git LFS where a remote supports it. LFS is optional, and a vault without large data never needs it. Not built.

## Basis

Operator. Architect: LFS is the existing standard for this, so nothing is invented.

## Consequences

- A vault stays small and clones quickly.
- A pointer names data by its hash, so a reader can tell whether the data it fetched is the data the page meant.
- See [tables](../ideas/tables.md) and [decision 0021](0021-git-is-the-store.md).
