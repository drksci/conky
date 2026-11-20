---
kind: decision
title: No hosted CI yet
status: accepted
date: 2026-11-20
source: operator
---

# 0017 No hosted CI yet

## Decision

There is no hosted CI for now. The checks (`ruff check`, `ruff format --check`, `pytest` and `scripts/check_docs.py`) are run locally with one command before every push:

```bash
ruff check . && ruff format --check . && pytest && python scripts/check_docs.py
```

The GitHub Actions workflow is removed.

## Basis

The operator asked whether CI is needed yet, and the architect agreed it is not. GitHub was not allocating hosted runners to the repository, so every push showed a failure that said nothing about the code. There is one contributor, and the workers already run the checks. This follows the rule to build nothing before something consumes it.

## Consequences

- A push can go out without the checks having been run. Until CI returns, review holds the rule that the checks run before every push.
- The workflow file was removed rather than left failing, so the repository shows no red check that means nothing.

## Open questions

- Bring CI back when hosted runners are available for the repository, or when a second contributor joins.
