---
kind: idea
title: Nothing goes stale
status: idea
date: 2026-11-20
source: maintainers
arch:
  items:
  - kind: archetype
    name: kind.archive
    by: a character
    layer: layer.character
    text: An archived page stays readable and drops out of attention. Whether it is a field or a space is open.
    state: idea
    roadmap: R3
  - kind: stage
    name: stage.attention.stale
    phase: attention
    text: A page can carry a measure of how long it has gone untouched. Past a threshold it is noticed, and an archived page drops out of what others attend to.
    state: idea
    roadmap: R3
---

# Nothing goes stale

## Idea

Every page can carry a measure of how long it has gone untouched, rising as the [clock](clock.md) moves. Past a threshold the page is noticed: summarised, split, handed to its owner to review, or archived. An archived page stays readable and linkable but drops out of what others attend to.

This is pressure applied to age instead of size, and relief is the reaction that acts on either ([pressure, not walls](../essays/pressure-not-walls.md)). Nothing of this is built.

Staleness is one case of [standing](standing.md). A page nobody uses fades from the ordered list of what is within a space and loses nothing: it stays readable, linkable and in history, and it returns to the top as soon as a write or a link uses it. Fading is a change of order, not a deletion.

## Composes from

Watch (a measure), clock, rule.

## Removes

Stale pages that accumulate unnoticed, and manual clean-up.

## Falsifying test

In a long run no page stays untouched and unarchived past its limit, and the routine cases need no refusal or model call. A page that fell to the back of the list and is then linked to is back at the front on the next listing, with its body and history unchanged.

## Open questions

- What relief does when it needs judgement (that needs a [model page](model-pages.md)).
- Whether archived is a field or a space.
