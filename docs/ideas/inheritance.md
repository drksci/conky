---
kind: idea
title: What a space hands down
status: idea
date: 2026-11-20
source: maintainers
arch:
  covers:
  - part.space
  items:
  - kind: part
    name: part.space.context
    layer: layer.space
    text: A space handing down its context and its reactions, and a page within several spaces.
    roadmap: R22
  - kind: flow
    name: flow.space.inherit
    title: A space hands down context and reactions
    statement: A space hands down its context and its reactions as well as its rules.
    rank: 2
    steps:
    - frm: lane.person
      to: lane.runtime
      text: write a field on a space
    - frm: lane.runtime
      to: lane.history
      text: an ordinary event
    - frm: lane.runtime
      to: lane.space
      text: its watch entries, and its fields as context
    - frm: lane.runtime
      to: lane.page
      text: each member sees the context in rules, reactions and embeds
    - frm: lane.runtime
      to: lane.page
      text: the space's reactions run for every member
    - frm: lane.space
      to: null
      text: a page may join several spaces and the stricter rule wins
    roadmap: R22
---

# What a space hands down

## Idea

A space hands down its rules today, and a write that changes a page's `within` is judged by the rules of the spaces it leaves as well as those it joins ([decision 0022](../decisions/0022-leaving-a-space-is-a-write-the-space-can-refuse.md), built with [decision 0028](../decisions/0028-a-character-writes-pages.md)). It should also hand down its context and its reactions: the space's fields, readable by members in rules, reactions and embeds, and its watch entries, which then run for every member. Built: the rules, the fields as `space` in expressions, leaving as a judged write, and a page within several spaces ([decision 0045](../decisions/0045-a-page-may-be-within-several-spaces.md), tested in `tests/test_spaces.py`). Also built: what the spaces above a page say reaches its prompt as `![[page#context]]` ([decision 0047](../decisions/0047-a-character-is-shown-what-its-spaces-say.md)). Not built: reactions handed down, and the fields of a space shown as prose. Rung: idea for what is not built.

A page may join more than one space, which is built, so it can sit in a team and also follow a practice. Each consequence below needs no new mechanism.

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
