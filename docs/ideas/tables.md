---
kind: idea
title: Tables
status: idea
date: 2026-11-20
source: maintainers
---

# Tables

## Idea

A page can have files beside it, and a table is the first kind. That one mechanism covers every sort of data that does not belong in a page.

- **Document.** The page itself: Markdown with frontmatter. Small, and in the present tense.
- **File.** Anything kept beside a page and named by it with a content hash: an image a connector captured, a download. The page is the small visible face; the file is the bulk.
- **Table.** Files of one type: Parquet parts in a folder beside the page. A write appends a part and never rewrites one, so a table is cheap to grow and easy to verify. The page carries the summary a rule may see: the columns, the row count, the hash of each part.
- **Stream.** A table that only grows, read as it grows. A watch fires once for each new part, not for each row. The Git history is the one stream every vault already has.

Small files are committed and travel by clone or bundle. Large or external ones are referenced by a pointer with a content hash, using Git LFS where a remote supports it ([decision 0003](../decisions/0003-data-beside-pages.md)). High-frequency data belongs in a table, not in page writes, because each write is a signed commit.

Engines stay outside. Parquet is read in place by any tool, so a query engine such as DuckDB is an optional reader beside the vault, reached like any other tool ([the outside arrives as pages](tools.md)), and a query's result is a page or a new table. The core never embeds an engine, and rules never read rows.

Nothing of this is built.

## Composes from

The table primitive of [decision 0010](../decisions/0010-no-debt-no-down-migrations.md); a page names the data beside it by relative path; Git as the store ([decision 0002](../decisions/0002-git-is-the-store.md)).

## Removes

Bulk data inside pages, which should stay small and in the present tense.

## Falsifying test

A vault copied elsewhere with its tables fails to answer the same queries, or a table cannot be re-projected from the committed history.
