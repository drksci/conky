---
kind: idea
title: Tables
status: idea
date: 2026-11-20
source: archive turn 24
---

# Tables

## Idea

Tabular data stored as Parquet beside its page, queryable, so the data travels with the vault.

## Composes from

The table primitive of [decision 0009](../decisions/0009-no-debt-no-down-migrations.md); a page names the data beside it by relative path.

## Removes

Bulk data inside pages, which should stay small and in the present tense.

## Falsifying test

A vault copied elsewhere with its tables fails to answer the same queries, or a table cannot be re-projected from the log.
