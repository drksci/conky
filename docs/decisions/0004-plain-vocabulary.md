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

- Earlier invented terms were dropped, and `tests/test_house.py` holds the retired words out of the code and the main documents.
- A rename is atomic everywhere.
- A new concept gets a plain word or is not added.
