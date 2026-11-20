---
kind: decision
title: Git is the store
status: accepted
date: 2026-11-20
source: operator
---

# 0021 Git is the store

## Decision

A vault is a Git repository. conky keeps no log of its own: no event file, hash chain, seal format, key-file code, canonical JSON or replay. An event is a commit and a seal is its signature, made with Git's native SSH signing. The format is written out in [design](../design.md).

## Basis

Operator proposed handing state to Git. Architect agreed after weighing it: the parts that must travel should rest on a format and tools that already exist everywhere, so there is no private format to version or migrate.

What Git replaces:

| Was | Is |
|---|---|
| Hash-chained log | Commits |
| Seals | Signed commits |
| Rebuild by replay | Checkout |
| Copying a vault | Clone, push, bundle |
| Changing several pages together | One commit |
| Why a field has its value | Log and blame |
| What-if runs | Branches |

## Consequences

- Lower write throughput, in the order of tens of writes per second. High-frequency data belongs in data files ([decision 0022](0022-data-beside-pages.md)).
- Git and `ssh-keygen` are required, and conky checks for them when a vault is opened.
- The `cryptography` dependency is gone.
- Rewriting history is possible locally. It is detectable only against another copy, such as a remote or a clone.
- [Decision 0003](0003-log-is-authority.md) is superseded: its principle stands, the store changed.

## Open questions

- Enforcing rules on commits made outside conky or pushed from elsewhere. Hooks are not cloned, so a rule check in a hook does not travel with the vault.
- Whether each actor should work on its own branch.
