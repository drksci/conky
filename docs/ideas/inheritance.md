---
kind: idea
title: What a space hands down
status: idea
date: 2026-11-20
source: maintainers
---

# What a space hands down

## Idea

A space hands down its rules today. It should hand down two more things: its context and its reactions. Context is the space's fields, readable by members in rules, reactions and embeds. Reactions are the space's watch entries, which then run for every member.

A page may join more than one space, so it can sit in a team and also follow a practice. Nothing beyond rules is built.

Consequences, each of which needs no new mechanism:

- A pattern is a space, and applying a pattern is joining it.
- A rule that nothing may go stale is one measure on the top space.
- A team's way of working is the same thing at a smaller depth.
- An actor is a space whose notes and helpers live inside it and share its budget.
- Promoting a practice is moving a space up the chain.

## Composes from

Space, rule, watch, embed.

## Removes

A separate pattern mechanism, per-page mandatory settings and repeated context.

## Falsifying test

A staleness measure written once on the top space applies to every page with no page edited. A page that joins a second space gains that space's rules and reactions, and loses them on leaving.

## Open questions

- The order of evaluation when several spaces apply.
- Whether a page can leave a space by itself.
- Conflicts between two spaces' rules. The stricter rule must win.

Related: [context that flows down](cascading-context.md), [patterns](patterns.md), [staleness](staleness.md).
