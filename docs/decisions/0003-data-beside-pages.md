---
kind: decision
title: Data beside pages
status: accepted
date: 2026-11-20
source: maintainers
---

# 0003 Data beside pages

## Context

Pages are meant to stay small and to describe the present. Tables and large or external data do not fit in them, and a vault that holds bulk data would clone slowly. High-frequency data cannot be written as page commits at one signed commit per write ([0002](0002-git-is-the-store.md)).

## Decision

Small tables live in the vault as Parquet beside their page. Large or external data is referenced by a pointer carrying a content hash, using Git LFS where a remote supports it. LFS is optional, and a vault without large data never needs it. LFS is the existing standard for this, so nothing is invented. Not built.

## Consequences

- A vault stays small and clones quickly.
- A pointer names data by its hash, so a reader can tell whether the data it fetched is the data the page meant.
- See [tables](../ideas/tables.md).
