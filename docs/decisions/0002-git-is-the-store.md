---
kind: decision
title: Git is the store
status: accepted
date: 2026-11-20
source: maintainers
---

# 0002 Git is the store

## Context

A vault needs a record of every change that cannot be altered unnoticed, that identifies who made each change, that can restore any earlier state exactly, and that can be copied between machines. Building such a record from scratch (an event file, a hash chain, a signature format, key-file code, replay) would create a private format to version and migrate.

Git already provides tamper-evident history, signed commits, exact restore, transport and atomic multi-file changes, with tools that exist on nearly every machine.

## Decision

A vault is a Git repository. conky keeps no log of its own. An event is a commit and a seal is its signature, made with Git's native SSH signing. The history is the authority and state is a projection of it: what is not recorded did not happen, and a refused write is recorded too, as an empty signed commit. The format is written out in [the vault format](../reference/vault-format.md).

What Git replaces:

| Needed | Provided by |
|---|---|
| A chained log | Commits |
| Seals | Signed commits |
| Rebuilding state | Checkout |
| Copying a vault | Clone, push, bundle |
| Changing several pages together | One commit |
| Why a field has its value | Log and blame |
| What-if runs | Branches |

The principle behind this is that history is primary and the current pages are one view of it. See [the-log-is-the-truth](../essays/the-log-is-the-truth.md).

## Consequences

- Write throughput is limited to the order of tens of writes per second, because each write is a signed commit. High-frequency data belongs in data files ([0003](0003-data-beside-pages.md)).
- A Git host is a backup and a way to share, not a live database. A vault commits locally and pushes in batches.
- A vault that grows too large is split; see [vault-splitting](../ideas/vault-splitting.md).
- Git 2.34 or newer and `ssh-keygen` are required, and conky checks for them when a vault is opened.
- No migrations are needed for the history itself. A new shape is a new reading of the same history.
- Rewriting history is possible locally. Removing the last commit is detectable only against another copy, such as a remote or a clone.

## Open questions

- Enforcing rules on commits made outside conky or pushed from elsewhere. Hooks are not cloned, so a rule check in a hook does not travel with the vault.
- Whether each actor should work on its own branch.
