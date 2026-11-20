---
kind: decision
title: Docs live in the repository
status: accepted
date: 2026-11-20
source: operator
---

# 0013 Docs live in the repository

## Decision

Project documentation lives in the repository under `docs/`, structured and checked locally before every push, not in a wiki.

## Basis

Operator asked for maintained formal docs wherever is easiest. Architect chose the repository so docs are versioned and reviewed with the code and can be checked automatically.

## Consequences

- `scripts/check_docs.py` checks frontmatter and links locally before every push.
- Docs change in the same change as the code they describe.
