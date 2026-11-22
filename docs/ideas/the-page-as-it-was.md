---
kind: idea
title: A rule sees the page as it was
status: idea
date: 2026-11-22
source: "reference/rules-and-reactions.md (what a rule can read), reference/vocabulary.md, ideas/writers.md; outside: optimistic concurrency with a version number (HTTP ETag and If-Match, RFC 9110 section 13.1.1, https://www.rfc-editor.org/rfc/rfc9110#name-if-match), allowed transitions of a state machine (https://www.w3.org/TR/scxml/), a column only its owner may update (SQL GRANT on a column, https://www.postgresql.org/docs/current/sql-grant.html)"
arch:
  items:
  - kind: part
    name: part.rule.was
    layer: layer.reflex
    text: A rule and a watch can read the fields a page had before the write being judged, as event.was, so a constraint on a change is written as a rule.
    state: idea
---

# A rule sees the page as it was

## Idea

Rung: idea. Nothing here is built.

A rule judges a write by the page as it would be afterwards. It cannot say that a total went down, that a status skipped a step, or that a field was changed by somebody who does not own it, because the page as it was is out of its sight. A constraint on state is expressible. A constraint on change is not.

Add one member to `event`: `event.was`, a map of the fields the page had before the write being judged. For a page that does not exist yet it is empty, so `has(event.was.status)` is false. In a watch, `event.was` is what the written page had before the event being reacted to. The old body is not given; it waits for a trial that needs it.

With it, each of these is a rule a character writes, and none is a feature:

- A stale write. Two writers read a page at `rev: 3`. The first writes `rev: 4` and is kept. The second also writes `rev: 4` and is refused by `!has(event.was.rev) || page.rev == event.was.rev + 1`, on the record, and a page watching for refusals hears of it.
- A counter that only goes up: `page.count >= event.was.count`.
- A step that is allowed: a status moves from `pending` to `accepted` and never back.
- A field one actor owns: any actor may write the page, and a change to `code` by anyone but the owner is refused, since `event.by` is already in scope.
- A body that only grows, and a retired page that may not be written again.

## Composes from

`event`, which already says who is writing, and the write path, which already loads the old page to judge the write. A rule already reads `asks` as it stands before the write, so reading the earlier state has a precedent in scope.

## Removes

The need for a separate check of a base named by the writer, a third outcome between kept and refused, a patch form and a rebase. A refused writer reads the page again and writes again, as it does after any refusal.

## Falsifying test

A playbook in which two writers start from the same page and the second is refused by a rule on `event.was`, with the refusal on the record. A second playbook moves a status only along allowed steps and only by a named hand. If either needs anything but `event.was` and the words that exist, the idea is not general. A law test passes when a rule that compares `page` with `event.was` refuses a write that no rule on `page` alone can, and fails when the member is removed.

## Open questions

- Whether the old body is ever needed, or the fields are enough.
- What `event.was` is for a page written for the first time in a watch, and for a refusal, where nothing changed.
- Whether a rule written to apply to pages already within a space should read each of them as its own present fields, since no change is being made to them.
