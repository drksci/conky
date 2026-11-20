---
kind: decision
title: An event can be noticed
status: accepted
date: 2026-11-20
source: maintainers
arch:
  covers:
  - law.event.notice
  - stage.notice.refusal
---

# 0039 An event can be noticed

## Context

- A refused write is recorded as an empty commit, so it is an event in history, yet nothing could react to it. The space a payment was refused in never learned that its limit had been met, and a character never learned from its own refusals between turns.
- [Decision 0037](0037-a-watch-can-fire-on-a-relation.md) let a watch notice a kept write by a relation. A refusal is the next case. Other events a character will need to hear, such as a page going stale, a join or a timer, should add a value to a field, not a new mechanism.

Prior art: a bounce message ([RFC 3464](https://www.rfc-editor.org/rfc/rfc3464)) tells the sender and the place it was bound for, a dead-letter queue keeps what could not be delivered for somebody to handle, and an Erlang link or monitor tells a process that another has failed.

## Decision

Every recorded event can be noticed by the pages that stand in relation to it. What picks it up is whatever the entry says: a `set` is a reflex with no model call, an `ask` to a small provider is a faculty, and an `ask` to the character's own provider is the character. Attention goes to the cheapest layer that can deal with it, and a second entry on the same page can read what the first counted, so only a count past a threshold reaches the character.

- `on: refusal` is a third relation beside `within` and `link`. After a refusal is recorded, a page is told when the refused write was to it and it exists, when it was the actor, or when the page written lies within it, by its kept `within` or else the one the write attempted, at any depth.
- Every watch entry reads `event`, a map: `event.id` is the commit reacted to, `event.kind` is `write` or `refused`, as the `Kind` trailer says, `event.by` is the actor and `event.reason` is the refusal reason on one line, and empty for a kept write. A later kind of event adds a value of `event.kind`.
- In a refusal entry `other_name` is the page the write was to, `other` the changes attempted without the body, and `other_text` is empty.
- The reaction is an ordinary write by the watching page, caused by the refusal, one level deeper. A refusal recorded past the depth limit tells nobody. A reaction that is refused is a refusal and may tell others, inside the same limit.
- The scalar `event` of earlier entries is now `event.id`. It is replaced, with no alias, and every playbook that used it is changed.
- A page named `refusal` is refused for shape, as `within` and `link` are.

## What the old behaviour guaranteed

- A refusal never becomes a kept write: the refused write is still an empty commit with the same id and reason and returns the same result. Held by `test_a_refusal_can_be_noticed_and_stays_a_refusal`.
- Reading history evaluates nothing: the reaction is a recorded write, so `conky verify` and `rebuild` agree on a vault with refusal reactions. Held by the same test.
- Loops end: the depth limit covers refusal reactions, held by the playbook for the depth limit.
- `event` named the commit reacted to. That is kept as `event.id`.

## Consequences

- A space or a character can be told when it is turned away, with no model call unless it chooses one.
- A refusal now costs a scan of the pages when it is recorded, as a kept write does.
- Not built: reactions to refusals of model answers in bulk, and `on: refusal` across mounts.
