---
kind: decision
title: Working practices
status: accepted
date: 2026-11-20
source: operator
---

# 0024 Working practices

## Decision

Working practices are written down in [CLAUDE.md](../../CLAUDE.md), and each has a check where one is possible:

- One command runs every check: `scripts/check`.
- Commit subjects are `<type>: <summary>` with type feat, fix, docs, test, refactor or chore; the summary starts lower-case, has no trailing full stop, and the subject is at most 72 characters. Checked by `scripts/check_commits.py`.
- A pre-push hook, `scripts/hooks/pre-push`, runs `scripts/check` and blocks the push on failure. It is enabled once with `git config core.hooksPath scripts/hooks`.
- `CHANGELOG.md` follows Keep a Changelog and Semantic Versioning. A test checks that it has an `## [Unreleased]` heading.
- The roadmap is the single tracker. Each step has a stable id and a state of `done`, `next` or `later`, and exactly one step is `next`. Checked by `scripts/check_docs.py`.
- Ruff selects the rule sets E, F, I, B, UP and SIM, with line length 100.
- The pull request template carries a `## Done when` checklist.

## Basis

Operator. There is no hosted CI ([decision 0017](0017-no-hosted-ci-yet.md)), so the practices are held by local checks and a hook rather than by a service.

## Consequences

- Practices that cannot be checked, such as who edits and who decides, stay labelled `(review)` in CLAUDE.md.
- The hook is local configuration and is not cloned with the repository, so each clone enables it once.
