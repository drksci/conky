---
kind: decision
title: A pattern starts private and rises by use
status: accepted
date: 2026-11-20
source: maintainers
arch:
  items:
  - kind: flow
    name: pattern-rises
    title: A pattern rising by use
    statement: A pattern is born private and rises one space at a time, by a measure of use and one write to within.
    rank: 8
    steps:
    - frm: Page
      to: Provider
      text: the pattern maker is asked once, from goldens
    - frm: Provider
      to: Page
      text: a space page, private to the space that made it
    - frm: Page
      to: Space
      text: other pages join it
    - frm: Page
      to: Page
      text: 'a measure of use: joins and distinct owners'
    - frm: Runtime
      to: Page
      text: the measure passes the threshold of the space above
    - frm: Page
      to: Space
      text: a reaction opens a proposal to move up one space
    - frm: Space
      to: Page
      text: approval under that space's own rule
    - frm: Runtime
      to: History
      text: one write to the pattern's within
    roadmap: R6
---

# 0023 A pattern starts private and rises by use

## Context

- A pattern is a space made on demand ([patterns](../ideas/patterns.md)), and a shipped catalogue is ruled out ([decision 0009](0009-patterns-not-features.md)).
- The open question was whether a practice is promoted by a person, by a vote, or by either.

## Decision

A pattern is born inside the actor or space that made it and is visible only there. It rises one space at a time, by use.

- Use is a measure on the pattern page: how many pages have joined it, from how many different owners, and the near-duplicates that a tidying background mind reports.
- When the measure crosses a threshold set by the space above, a reaction opens a proposal to move the pattern up exactly one space.
- The proposal is an ordinary page that gathers approvals under that space's own rule: a person, some of its members, or either. The space decides, and the default is one approval from someone other than the author.
- When approved, the move is one write to the pattern's `within`.
- A pattern nobody uses fades by the same staleness measure as anything else and is archived, not deleted.

## Consequences

- There is no committee and no catalogue.
- Promotion is one rung at a time, like ideas.
- Everything is composed from measure, reaction, proposal page, approval and rule.
- It depends on the clock (R12), signers and approvals (R14), background minds (R17) and the several-space part of R22. The leaving rule of [decision 0022](0022-leaving-a-space-is-a-write-the-space-can-refuse.md) is built ([decision 0028](0028-a-character-writes-pages.md)); the rest are unbuilt.
- Removed: the open question of how a practice is promoted.
