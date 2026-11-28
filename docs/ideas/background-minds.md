---
kind: idea
title: Background minds
status: idea
date: 2026-11-20
source: maintainers
arch:
  items:
  - kind: law
    name: law.spend.meter
    statement: Anything that runs in the background declares a budget and is metered.
    roadmap: R17
  - kind: archetype
    name: kind.mind
    by: a character
    layer: layer.character
    text: Doubt, curiosity, tidying and orientation, each a budgeted model page.
    roadmap: R17
  - kind: stage
    name: stage.attention.mind
    phase: attention
    text: 'Four budgeted pages: doubt reviews what was done, curiosity notices something nearby worth a look, tidying relieves crowded or stale pages, orientation summarises what matters now for an actor about to act.'
    state: idea
    roadmap: R17
---

# Background minds

## Idea

Cheap [model pages](model-pages.md) with a declared budget do a character's quiet thinking: the doubting, curiosity, tidying and orientation a page does when nobody is asking it for anything. They belong to its inner life, not to housekeeping. See [a page with a self](character.md). The four minds are:

- Doubt: review what was done.
- Curiosity: notice something nearby worth a look.
- Tidying: relief for crowded or stale pages ([staleness](staleness.md)).
- Orientation: a short summary of what matters now, for an actor about to act.

Each is an ordinary page in the actor's space that watches and writes. Each has a measure of what it has spent and stops at its budget, as the rule for anything that runs in the background requires. The budget is built: a page may carry `budget: {asks: N}`, the runtime counts its asks from the history and refuses an ask past it, and a space hands a default down ([decision 0058](../decisions/0058-a-budget-the-runtime-holds.md)). The four minds, tokens, money, a time window and a pool shared by a space are not built.

The first two pages of this kind exist as the starting pages of a card, one that keeps what matters and one that says what changed ([decision 0066](../decisions/0066-a-character-is-born-with-a-memory-and-a-sense-for-what-changed.md)); doubt and orientation are not built.

## Allowance follows use

A mind's allowance is set by [standing](standing.md): the share of what it wrote that was later used, by a link or a write within. A mind whose notes are taken up keeps its allowance, and one whose notes nobody uses gets less. Reflection stays quiet while a plain trend measure is good, since a mind that has nothing to doubt needs no turn. A forecast that missed is evidence and is acted on regardless of that quiet. The two triggers differ on purpose: doubt on success is optional, a miss is not.

## Composes from

Page, space, watch, write, a measure of spend, and the clock. It depends on model pages and the clock being built first.

## Removes

Housekeeping done by the acting page itself, and unmetered background work.

## Falsifying test

A background page stops writing when its budget is spent, every write it made is in history with its cause, and removing it leaves the vault verifying and every other page unchanged. A mind whose writes are never used is given a smaller budget on the next period than one whose writes are, and a missed forecast triggers its reaction while the trend measure is good.
