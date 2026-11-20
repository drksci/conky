---
kind: idea
title: Standing
status: idea
date: 2026-11-20
source: maintainers
arch:
  items:
  - kind: unplaced
    name: standing
    text: A measure of how much each page matters now, which orders what is listed within a space. It needs the members list ordered by a field.
---

# Standing

## Idea

What is shown first is decided by a measure. Every page has a standing, how much it matters now, derived by reflex from what the history already holds: what links to it, what was written within it lately, when it was last written, and an urgency field its author may set. No page has to declare anything, so there is no mandatory port and no score to keep up. A page with nothing to say about itself still has a standing.

Standing is a [measure](measures.md), a page watching itself, so its value is a recorded event and reading history never evaluates an expression ([decision 0008](../decisions/0008-measures-are-self-watches.md)). The picture is a desk: what matters is on top, what nobody touches slides to the back, and nothing is thrown away.

## What it gives

Standing adds no new word. It gives five things that are otherwise separate ideas, each a pattern on the same measure:

- The list of what is within a space ([context that flows down](cascading-context.md)) ordered by a field that a measure keeps, so a character sees the urgent page first without looking for it.
- Suggestions that fade because nothing took them up, and old pages that return only when something uses them ([nothing goes stale](staleness.md)).
- A background mind's allowance set by how much of what it wrote was used ([background minds](background-minds.md)).
- Reflection that stays quiet while a plain trend measure is good, and a forecast that missed acted on regardless.
- A new notion entering attention only if something uses it.

## The one runtime change

The members embed lists pages sorted by name. Ordering it by a named field is the only change to the runtime. Everything else is a pattern made from a measure, a rule and a reaction.

## Composes from

Measure, watch, link, the clock, and the members embed.

## Removes

A declared priority on every page, and a separate attention subsystem.

## Depends on

The [clock](clock.md) for anything that rises or fades with time, and the members embed for the ordered list.

## Falsifying test

A trial with five pages on the desk, one urgent and none ordered by name. With the ordering on, a character acts on the urgent page first at no extra cost. With it off, the same character does so less often on the same card. If the ordered list does not beat the name-sorted one, standing is not worth its field.

## Open questions

- Whether fading is an ordering or a threshold.
- Which of the four inputs earns its place; a trial can drop any of them.
