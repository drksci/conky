---
kind: decision
title: Derived data sits on top, never underneath
status: accepted
date: 2026-11-20
source: maintainers
---

# 0017 Derived data sits on top, never underneath

## Context

- A vault's Git history is the source of truth and is deliberately simple: pages are files, changes are signed commits, state is a view of the history ([0002](0002-git-is-the-store.md)).
- Some uses are slow or awkward against plain files and history: searching, querying across many pages, finding what watches what, showing a view to people, starting up on a long history.

## Decision

Anything built to make a vault faster or nicer to use is derived data: indexes, caches, snapshots, query stores, generated views. Derived data is optional and lives outside the vault's history, in a directory named `.conky/` that Git ignores. It can always be rebuilt from the vault alone and deleted at any time without losing anything. Nothing reads it as the truth, and no rule or reaction depends on it being present.

## Consequences

- A vault still travels as just its pages and history. Derived data is never needed to verify or read it.
- Any engine may be used for derived data, including a database, because it can be thrown away.
- A derived layer that cannot be rebuilt from the vault is a defect.
- The test for any such layer is to delete it and show that the vault still verifies and behaves the same.

## Open questions

- Whether derived data may be shared between copies of a vault as a convenience, or whether every copy builds its own.
- How a derived layer says which commit it was built from, so that a stale layer is recognised rather than trusted.
