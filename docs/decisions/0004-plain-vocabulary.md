---
kind: decision
title: Plain vocabulary
status: accepted
date: 2026-11-20
source: maintainers
---

# 0004 Plain vocabulary

## Context

Invented terms make a system harder to learn and tend to date quickly. A small, fixed vocabulary of ordinary words is easier to hold in mind and to check.

## Decision

One plain word per concept: vault, page, key, link, embed, rule, event, seal, space, error. The verbs are read, write and watch.

## Consequences

- The words and every other name the runtime exposes are listed in [the vocabulary](../reference/vocabulary.md), which the tests compare with the code ([decision 0027](0027-the-vocabulary-is-what-exists.md)).
- A rename is atomic everywhere.
- A new concept gets a plain word or is not added.
