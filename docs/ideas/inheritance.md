---
kind: idea
title: What a space hands down
status: idea
date: 2026-11-20
source: maintainers
arch:
  covers:
  - part:space
  items:
  - kind: part
    name: space-context
    layer: spaces
    text: A space handing down its context and its reactions, and a page within several spaces.
    roadmap: R22
  - kind: flow
    name: space-hands-down
    title: A space hands down context and reactions
    statement: A space hands down its context and its reactions as well as its rules.
    rank: 2
    steps:
    - frm: Person
      to: Runtime
      text: write a field on a space
    - frm: Runtime
      to: History
      text: an ordinary event
    - frm: Runtime
      to: Space
      text: its watch entries, and its fields as context
    - frm: Runtime
      to: Page
      text: each member sees the context in rules, reactions and embeds
    - frm: Runtime
      to: Page
      text: the space's reactions run for every member
    - frm: Space
      to: null
      text: a page may join several spaces and the stricter rule wins
    roadmap: R22
---

# What a space hands down

## Idea

A space hands down its rules today, and a write that changes a page's `within` is judged by the rules of the spaces it leaves as well as those it joins ([decision 0022](../decisions/0022-leaving-a-space-is-a-write-the-space-can-refuse.md), built with [decision 0028](../decisions/0028-a-character-writes-pages.md)). It should also hand down its context and its reactions: the space's fields, readable by members in rules, reactions and embeds, and its watch entries, which then run for every member. Only the rules, and leaving as a judged write, are built. Rung: idea. The enforced part is the leaving rule, tested in `tests/test_laws.py`; a page is still within one space.

A page may join more than one space, so it can sit in a team and also follow a practice. Each consequence below needs no new mechanism.

- A pattern is a space, and applying it is joining it.
- A rule that nothing may go stale is one measure on the top space.
- A team's way of working is the same thing at a smaller depth.
- An actor is a space whose notes and helpers live inside it and share its budget.
- Promoting a practice is moving a space up the chain.

## Composes from

Space, rule, watch, embed.

## Removes

A separate pattern mechanism, per-page mandatory settings and repeated context.

## Falsifying test

A staleness measure written once on the top space applies to every page with no page edited. A page that joins a second space gains its rules and reactions, and loses them on leaving.

## Open questions

- The order of evaluation when several spaces apply.
- Leaving a space is settled and built: [decision 0022](../decisions/0022-leaving-a-space-is-a-write-the-space-can-refuse.md).
- Conflicts between two spaces' rules. The stricter rule must win.

Related: [context that flows down](cascading-context.md), [patterns](patterns.md), [staleness](staleness.md).
