---
kind: decision
title: A character gives its space reflexes
status: accepted
date: 2026-11-20
source: maintainers
arch:
  covers:
  - law.rule.tighten
  - law.event.notice
---

# 0041 A character gives its space reflexes

## Context

- [Decision 0035](0035-a-character-binds-its-own-space.md) let an answer add rules to the space it writes into and nothing else. [Decision 0039](0039-an-event-can-be-noticed.md) let a watch entry hear a refusal. A character asked to have its space count what it turns away could not do it: a space listens through a watch entry, and an answer could not write one to the space. One walked draw wrote the entry as a rule on a new page, where it heard nothing.
- A tenant may fit a doorbell but not knock down a wall. A rule is a wall that holds the space still; a watch entry is an ear that lets it notice. Both are the space's own, and the character that works in it is the one who knows what the space should hear.
- Prior art: a standing rule that reacts to an event, such as a mail filter rule or a database trigger, is written by the owner of the mailbox or table, not by whoever delivers to it.

## Decision

A block that names the space an answer writes into may hold `rules`, `watch` or both, and no other field, no `within` and no body. Entries are added after what the space has, an entry already there is kept once, and nothing is removed or replaced.

An added watch entry must be a reflex: it carries `set`, and an entry that carries `ask` is refused with reason `limit`. The reason says a space can be given reflexes this way and not asks, because nothing meters an ask yet. A model call started by a space with no budget would be a background cost with no declared limit. The wall stays until budgets exist.

Added entries are checked as any watch entry is when written, names included, and the write is judged by the rules of the spaces above, as any write is. The write is signed by the asker and recorded like any other.

The page instruction says so in one clause and one worked block that holds a rule and a counter of refusals.

## What the old behaviour guaranteed

- An answer never removes or replaces what its space has. Kept, under `test_an_answer_cannot_remove_or_replace_what_its_space_has`.
- An answer changes nothing of its space but what is added. Kept for every field, the body and `within`, under `test_an_answer_cannot_set_a_field_or_a_body_on_its_space` and the wrong examples under `tests/invalid/`.
- An answer adds rules and nothing else. Given up in writing: nothing else now includes reflex watch entries, and only those.
- A space spends nothing on its own. Kept: an `ask` cannot be added, so a space gains no model call from an answer.

## Consequences

- A character can make its space notice, with no model call per event, by writing the entry itself. A space can count refusals, and a second reflex can read the count.
- A space can be given a reflex that writes its own fields on every event. The rules of the space and of the spaces above still judge each of those writes, and the history shows each one.
- Not built: an added `ask` entry, which waits for a budget that is metered. A reflex that fires for every write in a large space costs a scan of pages each time, as any watch does.
- Whether a small model writes the entry is a forecast on the card `a-keeper-hears-the-no`, not yet drawn.
