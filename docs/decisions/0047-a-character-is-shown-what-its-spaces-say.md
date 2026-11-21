---
kind: decision
title: A character is shown what its spaces say
status: accepted
date: 2026-11-21
source: maintainers
arch:
  covers:
  - law.embed.context
  - part.embed
---

# 0047 A character is shown what its spaces say

## Context

- A space hands down its rules and its fields ([decision 0036](0036-a-plain-rule-stays-with-its-page.md), [decision 0045](0045-a-page-may-be-within-several-spaces.md)), but a prompt could not see what the space says. A keeper who joins a night shift is bound by the shift's rules and is still not told what the shift's note says.
- The general case is standing words that apply to everyone in a place. A notice board in a staff room does it: a person reads it because they work there, and a night shift pins its own sheet on top.
- Prior art, one line each. Cascading configuration (CSS, editor and version-control settings files): the nearest setting is read first and the farther ones fill in. House style sheets and per-team onboarding notes: standing words kept in one place and read by whoever belongs. Hierarchical instruction files for coding agents are a case of the same idea, read in order of nearness.

## Decision

A new embed part, `![[NAME#context]]`, resolves to what the spaces above the page NAME say.

- Format. For each space above the page that has a non-empty body, a line `NAME says:` and then the body as written, less its closing blank space. The blocks are separated by a blank line. A page with no space, or whose spaces all have empty bodies, embeds nothing.
- Order. Nearest first: the spaces the page lists, in the order listed, then the spaces above those, each space once at its nearest distance. This is the order `space` is merged in for conditions ([decision 0045](0045-a-page-may-be-within-several-spaces.md)), read the other way, and one function orders both.
- Cap. The nearest 5 spaces are shown, then a line `(N more spaces not shown)`. The length of one space's words is not capped in this step.
- Reserved. `context` is a part every page has, computed and never stored, so a page cannot carry a field of that name. A write that tries is refused for shape with a reason in `voice.md`. No page, example, fixture or playbook used the name.
- Reads. The embed is resolved on read and when a prompt is built, so a change to a space's body or to the page's `within` changes the resolved prompt and the skip rule asks again. The `Read` trailer names the spaces whose words were shown and not the page that embeds them.
- Nobody-can-tell holds: nothing about who wrote a space's body is shown. Nothing is written.

## What the old behaviour guaranteed

- `![[page]]`, `![[page#field]]` and `![[space#members]]` resolve as before. Kept, held by the existing tests passing unchanged.
- A page could have a field named `context`. Given up in writing: the name is now taken.
- The order of the spaces above a page was held in `Vault._above`. Kept: it moved to `conky.page.above` so that the embed and the merge share one function, and `tests/test_spaces.py` holds it.

## Consequences

- Whoever keeps a space writes its body, and a character that wants to be told it embeds the part once. Nothing else is built for shifts, houses or styles.
- Not built: the fields of a space shown as prose, summaries of long bodies, a budget in tokens, and reactions handed down. The trial of a keeper on a night shift that declines a large payment, and is paid when taken off the shift, is not yet written.
