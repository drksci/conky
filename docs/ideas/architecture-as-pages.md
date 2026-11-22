---
kind: idea
title: The architecture as pages
status: idea
date: 2026-11-22
source: "reference/architecture.md, scripts/gen_architecture.py, ideas/patterns.md, ideas/the-page-as-it-was.md; outside: Backstage software catalog (https://backstage.io/docs/features/software-catalog/), Architecture Decision Records (https://adr.github.io/)"
arch:
  items:
  - kind: part
    name: part.docs.pages
    layer: layer.edge
    text: Each entry of the architecture index written as a page in a vault of the project's own, by a script outside the runtime, with notes beside it written by anyone.
    state: idea
---

# The architecture as pages

## Idea

Rung: idea. Nothing here is built.

The architecture index is generated from the code and from the frontmatter of ideas and decisions. It is accurate and nobody can talk to it: a row cannot be annotated, argued with or watched.

Keep the index as the facts. A script outside the runtime writes each entry as a page in a vault of the project's own. Only the code's own actor may write those pages, so the facts stay the code's. Notes about a part are ordinary pages, within the part's page or linking to it, written by anyone. A note watches its part and is told when the part changes, by the same watch every page already has.

This is the pattern a software catalog follows, for example Backstage, where an entity is a described record and teams attach what they know to it. Here the record is a page, the owner is a rule, and the telling is a watch.

The rule that only the code's actor may write the fact pages is a rule on the field: anyone may write a note, and a change to a fact by any other hand is refused. It uses `event.by` today, and a field the owner keeps once written is the case the [page as it was](the-page-as-it-was.md) makes simple.

## Composes from

Page, space, watch, a rule on who writes, and link. The generator already exists; this writes its output as pages instead of one document.

## Removes

The gap between a generated index nobody annotates and a hand-written note that goes stale without telling anyone.

## Falsifying test

A playbook in which a note watches a part, the part's page changes, and the note is told, using existing words only. If a new word is needed, the idea is lost.

## Open questions

- Whether the vault of the project's own is a second vault or a space within one.
- How a note that is told of a change records that somebody has looked.
- Whether the fact pages are regenerated whole or changed field by field.
