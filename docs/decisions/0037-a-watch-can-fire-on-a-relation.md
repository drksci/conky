---
kind: decision
title: A watch can fire on a relation
status: accepted
date: 2026-11-20
source: maintainers
arch:
  covers:
  - part.watch
  - stage.notice.relation
---

# 0037 A watch can fire on a relation

## Context

- A trial showed that small models, told that a den must keep a floor of cash, write the limit as an invariant on the den (`page.cash >= 20`) and record each payment as a page within it. For that to work the den must notice what is written within it, so that its cash can be moved by its payments.
- A watch entry names one page (`on: PAGE`). A space cannot notice its members without naming each in advance, and a page cannot notice what links to it. An inbox, a comment thread and a delegation need the same thing.

## Decision

`on` takes a page name or one of two relations.

- `on: within` fires when a page within the watching page, at any depth, is written.
- `on: link` fires when a page whose body or text fields contain a link `[[NAME]]` to the watching page is written.
- `on: PAGE` keeps its meaning.

In the scope of the entry, `other`, `other_text`, `other_size` and `event` mean the page just written, as before. `other_name` is new and holds the name of that page, since a relation does not know it in advance. It is set for named watches too.

`within` and `link` are words the vocabulary already has, so a page named `within` or `link` can no longer be watched by name. Writing such a page is refused with reason `shape`.

Order is unchanged: reactions run in name order of the watching pages, depth first. A page never reacts to its own write through a relation. The depth limit and every other limit apply unchanged.

## Consequences

- A space states its limit as a plain rule on itself and moves its own fields by what is written within it, with no model call.
- The runtime scans every page for each write, as it did for named watches, so a relation adds no cost beyond one look at the written page's place and links.
- A vault with a page named `within` or `link` cannot take new writes to that page. None exists in the repository, the examples or the golden vault.
