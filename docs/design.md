---
kind: design
title: Design
status: current
date: 2026-11-20
source: architect
---
# Design

## The model

A vault is a directory. Its authority is the event log, `log/events.jsonl`:
one signed line per event, each carrying the hash of the line before it.
Pages in `pages/` are projections of that log. Nobody edits them by hand.
The vault holds public keys only; private keys live in a separate directory.
A cold reader given only the vault can verify it and rebuild every page.

## Laws built so far

- Rules. A page may carry CEL expressions that must be true after every
  write. A page inherits the rules of every space up its `within` chain.
  Rules are pure: they see `page` (the resulting fields) and `size` (the
  byte length of the resulting serialised page). A size limit is an
  ordinary rule a space sets, for example `size <= 2000`.
- Recorded or it did not happen. Every write is a signed event. A refused
  write is also recorded, as a `refused` event, and changes no page.

## Reactions without a model

A page can watch another page. When the watched page changes and the
`when` expression is true, the runtime writes the watching page, signed by
that page's own key, with `cause` set to the triggering event. Reactions
cascade to depth 12, then are refused as a cycle. A reaction that would
change nothing is skipped, so stable states end.

## Measures

A measure is a page watching itself: a `watch` entry whose `on` is the
page's own name, setting a field computed from the page's state. No new
concept is added. Watch expressions can use `page`, `other`, `size` (the
byte length of the watching page as serialised) and `other_size` (the byte
length of the page just written; for a self-watch the two are equal). The
computed value is written as an ordinary recorded event, so replaying the
log never evaluates an expression and history stays reproducible even if
the expression language changes. The skip-when-unchanged rule and the depth
cap still apply, so a self-watch settles when its fields stop changing.

Pressure is the first use. A page with no size rule can take a large write;
a self-watch such as `{on: <itself>, when: "true", set: {pressure: "size / 400"}}`
records a rising number, and a second entry with `when: "page.pressure >= 2"`
can set a state that other pages watch. Walls stay for what must never
happen. Nothing yet acts to relieve the pressure. The checks are in
`tests/test_laws.py`.

Think of a spreadsheet: pages are like cells, a self-watch is like a
formula, and the log is the signed history of every recalculation.

## Verify and rebuild

`verify` checks the hash chain, every seal against the public keys in the
vault, and that replaying the log from empty reproduces every page file
byte for byte. `rebuild` deletes `pages/` and regenerates it from the log.

## Not built yet

In this order:

1. Tables stored as Parquet beside their page.
2. Model-backed pages: a page that asks a question state cannot answer.
3. Grouped writes and a pattern maker (accounting as a pattern, not a runtime feature).
4. The assimilation test: hand a fresh consumer only a stopped vault and
   score whether it resumes correctly.
5. The harness-neutral benchmark against other agent harnesses.
