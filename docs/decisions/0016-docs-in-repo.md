---
kind: decision
title: Docs live in the repository
status: accepted
date: 2026-11-20
source: maintainers
---

# 0016 Docs live in the repository

## Context

Documentation kept in a wiki drifts from the code and cannot be checked. Documentation kept beside the code is versioned and reviewed with it.

## Decision

Project documentation lives in the repository under `docs/`, structured and checked automatically, not in a wiki. It has three layers: the README for anyone, `docs/guide/` for the ideas in plain language and a walkthrough, and the technical detail in `docs/reference/`, `docs/design.md` and `docs/decisions/`.

## Consequences

- `scripts/check_docs.py` checks frontmatter and links, and runs in CI.
- Docs change in the same change as the code they describe.
