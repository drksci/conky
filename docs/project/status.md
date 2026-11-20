---
kind: project
title: Status
status: current
date: 2026-11-20
source: maintainers
---

# Status

conky is early: the core works and is tested, and much is still to be built. This page says what exists and what is unverified. The unbuilt work is on the [roadmap](roadmap.md).

## What exists

From [design](../design.md) and the [reference](../reference/vault-format.md):

- Pages with deterministic serialisation, and a write path that is the only way state changes.
- Rules in CEL, inherited through `within` chains, with `page` and `size` in scope.
- A vault that is a Git repository: every write is a signed commit with trailers, and a refused write is an empty signed commit. Git and `ssh-keygen` are required.
- Reactions: pages that watch other pages and write themselves, with no model call.
- Measures: a page can watch itself, with `size` and `other_size` in watch expressions. Pressure is the first use. Nothing yet acts on pressure to relieve it.
- `verify` (clean tree, `git fsck`, signatures from `keys/allowed_signers`, trailers, files changed), `rebuild` (restore the committed state), and a command line: `init`, `write`, `read`, `log`, `verify`, `rebuild`, `demo`.
- `conky demo`: builds a small example vault (`stall` or `team`, shipped as data in the package) with the real write path and narrates each step, including a refused write and a reaction.
- A golden vault under `tests/golden/` that every version must keep verifying and reading.
- CI that runs `scripts/check` on every pull request and on pushes to `main`.

## Unverified

- No claim here comes from an unscripted benchmark run; none has been made.
- Nothing in the project has been audited for security. See [SECURITY.md](../../SECURITY.md).

## Known gaps

- Two open design questions, recorded without answers in [open questions](open-questions.md): rules on a space also apply to the space page itself, and removing the last commit is not detectable from one copy alone.
- Rules are not enforced on commits made outside conky or pushed from elsewhere; `verify` catches unsigned or unlisted-key commits, not rule violations ([decision 0002](../decisions/0002-git-is-the-store.md)).
- Write throughput is limited by one signed commit per write, in the order of tens per second.
- Everything on the [roadmap](roadmap.md) is unbuilt except the first slice of measures.
