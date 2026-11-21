---
kind: idea
title: What a space hands down
status: idea
date: 2026-11-20
source: maintainers
arch:
  covers:
  - part.space
---

# What a space hands down

## Idea

A space hands down its rules today, and a write that changes a page's `within` is judged by the rules of the spaces it leaves as well as those it joins ([decision 0022](../decisions/0022-leaving-a-space-is-a-write-the-space-can-refuse.md), built with [decision 0028](../decisions/0028-a-character-writes-pages.md)). It should also hand down its context and its reactions: the space's fields, readable by members in rules, reactions and embeds, and its watch entries, which then run for every member. Built: the rules, the fields as `space` in expressions, leaving as a judged write, and a page within several spaces ([decision 0045](../decisions/0045-a-page-may-be-within-several-spaces.md), tested in `tests/test_spaces.py`). Also built: what the spaces above a page say reaches its prompt as `![[page#context]]` ([decision 0047](../decisions/0047-a-character-is-shown-what-its-spaces-say.md)). Also built: a watch entry written `each: ENTRY` on a space is carried by every page within it, `set` only ([decision 0056](../decisions/0056-a-space-hands-down-reactions.md), tested in `tests/test_handed_down.py`). All three things a space hands down are built. Not built: asks handed down, which wait for budgets, and the fields of a space shown as prose, which its words already do. Rung: enforced for what is built.

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
