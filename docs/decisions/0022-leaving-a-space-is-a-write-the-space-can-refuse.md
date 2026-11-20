---
kind: decision
title: Leaving a space is a write the space can refuse
status: accepted
date: 2026-11-20
source: maintainers
arch:
  covers:
  - law:rules-only-tighten
  - flow:join-and-leave
  - part:space
---

# 0022 Leaving a space is a write the space can refuse

## Context

- A space hands its rules down to the pages within it.
- Today the runtime judges a write against the page as it will be after the write. It follows `within` from that new page and evaluates the rules of each space on the way up. It never looks at the spaces the page was in before.
- So a page can drop a rule by writing a different `within`. A rule that can be walked away from is a request.

## Decision

Joining and leaving are ordinary writes to `within`. A write that changes `within` is judged by the rules of every space the page is in before the write and every space it will be in after it.

- A space that says nothing about leaving lets its members go.
- A space that wants to bind states it as a rule, in the same language as any rule.
- Nothing new is added.

## Consequences

- A house rule binds for as long as the space says so. The default stays the easy one: free to leave.
- A refusal is recorded like any other and names the space that refused.
- A rule about who may move a page waits on rules that can see who signed (R14 in the [roadmap](../project/roadmap.md)).
- Built with [decision 0028](0028-a-character-writes-pages.md): a write that changes the `within` of an existing page is judged by the rules of the spaces it was in as well as those it will be in. A page may still be within one space only, so the several-space part of R22 is unbuilt.
- Removed: the open questions about who may change which space a page belongs to, and whether a page can leave a space by itself.
