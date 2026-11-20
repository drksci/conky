---
kind: idea
title: Tables
status: idea
date: 2026-11-20
source: maintainers
---

# Tables

## Idea

Tabular data lives as Parquet beside its page, queryable, so the data travels with the vault. Small tables are committed and travel by clone or bundle. Large or external data is referenced by a pointer with a content hash, using Git LFS where a remote supports it ([decision 0003](../decisions/0003-data-beside-pages.md)). High-frequency data belongs in a table, not in page writes, because each write is a commit.

## Composes from

The table primitive of [decision 0010](../decisions/0010-no-debt-no-down-migrations.md); a page names the data beside it by relative path; Git as the store ([decision 0002](../decisions/0002-git-is-the-store.md)).

## Removes

Bulk data inside pages, which should stay small and in the present tense.

## Falsifying test

A vault copied elsewhere with its tables fails to answer the same queries, or a table cannot be re-projected from the committed history.
