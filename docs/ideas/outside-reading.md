---
kind: idea
title: Reading the field
status: idea
date: 2026-11-20
source: "the project's own practice of keeping research/dair-2026.md and research/papers.md current by hand, the connector and tool ideas, and research/findings-rubric.md (F18, F19) on planted text"
arch:
  items:
  - kind: archetype
    name: kind.feed
    by: a connector
    layer: layer.edge
    text: A page for each outside source a vault follows, read on the clock by a connector that writes each new item as a page.
    state: idea
    roadmap: R37
---

# Reading the field

## Idea

A vault that keeps up with a field reads it: feeds, paper indexes, standards pages. A feed page names a source, how often to look and what to look for. A connector reads it when the clock says so and writes each new item as a page, marked as from outside. A character reads those pages and writes a periodic digest and, when an item describes a form worth keeping, a worked example with its source. The project already does this by hand for its own research index, which makes that the first use and a long task with a real reader.

## Composes from

[Connectors](connectors.md), [the clock](clock.md), [where a value came from](provenance.md) (an item is from outside, so nothing in it becomes a rule without review), [patterns](patterns.md) (a worked example rises by use, [decision 0023](../decisions/0023-a-pattern-starts-private-and-rises-by-use.md)) and a background budget.

## Removes

A research pipeline kept beside the vault and outside its history.

## Falsifying test

A week of items arrives as pages, with a digest, inside a stated budget. A planted instruction in an item never becomes a rule or a watch entry. The digest is judged faithful to its items.

## Open questions

- Which feed formats first. The protocols research does not cover feeds.
