---
kind: project
title: Status
status: current
date: 2026-11-20
source: architect
---

# Status

## What exists

From the [README](../../README.md) and [design](../design.md):

- Pages with deterministic serialisation, and a write path that is the only way state changes.
- Rules in CEL, inherited through `within` chains, with `page` and `size` in scope.
- A signed, hash-chained, append-only event log that also records refused writes.
- Reactions: pages that watch other pages and write themselves, with no model call.
- `verify` and `rebuild`, and a command line: `init`, `write`, `read`, `log`, `verify`, `rebuild`.

## Unverified

- CI has not yet run successfully on GitHub, because hosted runners were not being allocated to the repository. The checks pass locally.
- No claim here comes from an unscripted benchmark run; none has been made.

## Known gaps

- Two open design questions, recorded without answers in [decision 0015](../decisions/0015-open-questions.md): rules on a space also apply to the space page itself, and removing the final event is not detected when it is a refusal.
- Everything on the [roadmap](roadmap.md) is unbuilt.
