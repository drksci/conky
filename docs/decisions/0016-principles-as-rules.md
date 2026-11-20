---
kind: decision
title: Principles as rules
status: accepted
date: 2026-11-20
source: operator
---

# 0016 Principles as rules

## Decision

Every principle in `CLAUDE.md` is written as an imperative rule that states how it is held, either by a named check or by review. A rule held only by review is a gap to close.

## Basis

Operator asked for the paradigms and principles to be encoded as rules. Architect chose the check/review marking so it is visible which rules bite.

## Consequences

- `tests/test_house.py` and `scripts/check_docs.py` hold the vocabulary, fix-later and docs rules.
- Most design rules are still review-only.
