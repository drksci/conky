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
- A vault that is a Git repository: every write is a signed commit with trailers, and a refused write is an empty signed commit. Git and `ssh-keygen` are required.
- Reactions: pages that watch other pages and write themselves, with no model call.
- Measures: a page can watch itself, with `size` and `other_size` in watch expressions. Pressure is the first use. Nothing yet acts on pressure to relieve it.
- `verify` (clean tree, `git fsck`, signatures from `keys/allowed_signers`, trailers, files changed), `rebuild` (restore the committed state), and a command line: `init`, `write`, `read`, `log`, `verify`, `rebuild`.

## Unverified

- There is no hosted CI; checks are run locally before each push. See [decision 0017](../decisions/0017-no-hosted-ci-yet.md).
- No claim here comes from an unscripted benchmark run; none has been made.

## Known gaps

- Two open design questions, recorded without answers in [decision 0015](../decisions/0015-open-questions.md): rules on a space also apply to the space page itself, and removing the last commit is not detectable from one copy alone.
- Rules are not enforced on commits made outside conky or pushed from elsewhere; `verify` catches unsigned or unlisted-key commits, not rule violations ([decision 0021](../decisions/0021-git-is-the-store.md)).
- Write throughput is limited by one signed commit per write, in the order of tens per second.
- A golden vault under `tests/golden/` must keep verifying in future versions.
- Everything on the [roadmap](roadmap.md) is unbuilt except the first slice of measures.
