---
kind: decision
title: A space shows what bears first
status: accepted
date: 2026-11-20
source: maintainers
arch:
  covers:
  - law.embed.shows
---

# 0042 A space shows what bears first

## Context

- `![[space#members]]` lists the pages within a space sorted by name and cut at a fixed twenty. A character with more on its desk than fits is shown the names that sort first, which has nothing to do with the matter in hand.
- A good secretary puts what is needed on top of the desk and keeps the rest in the drawer. The general case is a view of a space under a budget: an order and a cut.
- Prior art: relevance-ordered search results, where the page shown first is the one that scores highest against the query; an inbox sorted by priority; and the limit of working memory, which holds a few things at once. [Decision 0039](0039-an-event-can-be-noticed.md) lets a space hear what happens to it and [decision 0041](0041-a-character-gives-its-space-reflexes.md) lets it keep what it heard in a field, so a space already has the query in hand.

## Decision

A space may carry a field `shows`, a mapping with two optional keys.

- `most` is a whole number from 1 to `MEMBERS_CAP`, and defaults to `MEMBERS_CAP`.
- `first` is an expression that gives a number for each member, and has no default.

`![[space#members]]` then orders its lines by `first`, highest first, and cuts to `most`, with the same `(N more not shown)` line. A member that `first` cannot score, because it reads a field the member lacks or gives something that is not a number, comes after the scored ones. Ties and unscored members are ordered by name. Nothing is refused for it.

`first` reads `page` (the member's fields), `text` (the member's body) and `space` (the fields of the space shown, the field `heard` of a listening space for one). These are names rules already have, and no other name is added. It is the same expression language, with the same text functions, so word overlap needs nothing new: `space.heard.lowerAscii().split(' ').filter(w, size(w) > 3 && text.lowerAscii().contains(w)).size()` scores a member by how many words of more than three letters it shares with what the space heard.

`shows` is a field, not a reserved key. It is proven when written: an unknown key, a `most` outside its range, a `first` that does not parse or that reads another name is refused for shape, with the sentence in `voice.md` saying what to write. The line format of a member does not change.

Whoever makes the space sets `shows`. Letting an answer add it to the space it writes into is not part of this step.

## Purity

The order is worked out when an embed is resolved, on read and when a prompt is built, from the pages as they are. Nothing is written. The resolved prompt is recorded in the commit of the ask, so the record shows exactly the lines that were shown, and reading history evaluates nothing. The cache key hashes the resolved text, so a change of order asks afresh.

## What the old behaviour guaranteed

- Members are listed sorted by name, at most `MEMBERS_CAP`, with a count of the rest. Kept as the behaviour of a space with no `shows`, held by `test_a_space_that_does_not_show_lists_by_name_at_the_cap` and the playbook for the cap.
- A page may not carry a field named `members`. Kept.
- Reading evaluates nothing that is stored: held by `test_reading_a_space_that_shows_writes_nothing`.

## Consequences

- A character can be shown what bears on the matter in hand with no model call and nothing stored, and the order changes as soon as what the space heard changes.
- Each embed of a space that shows costs one expression evaluation per member. The members are bounded by the pages in the vault, not by the cap, so a very large space pays for its size; a cache of the order is not built.
- Not built: an order by use, where standing is kept by a measure; a `shows` added by a character's answer; an order on more than one key.
