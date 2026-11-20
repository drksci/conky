---
kind: idea
title: Tables
status: idea
date: 2026-11-20
source: maintainers
arch:
  items:
  - kind: data
    name: file
    text: 'Anything kept beside a page and named by it with a content hash: an image a connector captured, a download.'
    roadmap: R1
  - kind: data
    name: table
    text: Parquet parts in a folder beside a page. A write appends a part and never rewrites one, and the page carries the columns, the row count and the hash of each part.
    roadmap: R1
  - kind: data
    name: engine
    text: A query engine such as DuckDB is an optional reader beside the vault, reached like any tool. The core never embeds one and rules never read rows.
    state: idea
    roadmap: R1
  - kind: data
    name: stream beside a page
    text: A table that only grows, read as it grows. The Git history is the one stream every vault already has.
    roadmap: R1
  - kind: flow
    name: table-append
    title: Appending to a table
    statement: A write appends one Parquet part beside the page and never rewrites one.
    rank: 12
    steps:
    - frm: Person
      to: Runtime
      text: write rows to a table
    - frm: Runtime
      to: Outside
      text: a new Parquet part is written beside the page
    - frm: Runtime
      to: Space
      text: rules judge the page's summary, never the rows
    - frm: Runtime
      to: History
      text: one signed event that carries the part's hash
    - frm: Runtime
      to: Page
      text: the page's columns, row count and part hashes are updated
    roadmap: R1
  - kind: flow
    name: engine-query
    title: A query through an engine
    statement: A query engine reads the Parquet in place, and its result is a page or a new table.
    rank: 13
    steps:
    - frm: Page
      to: Connector
      text: a request to query
    - frm: Connector
      to: Outside
      text: the engine reads the parts in place
    - frm: Connector
      to: Runtime
      text: the result, as a page or a new table, caused by the request
    - frm: Runtime
      to: History
      text: a signed event by the connector
    - frm: Runtime
      to: null
      text: the core never embeds an engine
    roadmap: R1
  - kind: flow
    name: batch-watch
    title: A watch firing on a batch
    statement: A watch on a stream fires once for each new part, not for each row.
    rank: 14
    steps:
    - frm: Runtime
      to: History
      text: a new part of a stream is committed
    - frm: Runtime
      to: Page
      text: a watch entry on the stream's page fires once for the part
    - frm: Runtime
      to: History
      text: the reaction, a signed event with Cause
    - frm: Runtime
      to: null
      text: each row does not fire the watch
    roadmap: R1
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
