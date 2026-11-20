---
kind: project
title: Open questions
status: current
date: 2026-11-20
source: maintainers
---

# Open questions

Design questions that are known and unresolved, with no answer proposed.

- Rules on a space also apply to the space page itself, so a space must carry the fields its rules mention. See [rules and reactions](../reference/rules-and-reactions.md#rules-and-spaces).
- Removing the last commit is not detectable from one copy of a Git history, only against another clone or remote. See [decision 0002](../decisions/0002-git-is-the-store.md).
- How keys are rotated and revoked.
- How two vaults relate after a split. See [vault-splitting](../ideas/vault-splitting.md).

The first two are known gaps in the current runtime ([status](status.md)). A question that belongs to one decision is kept in that decision's record. Settled: who may move a page between spaces and whether a page can leave by itself ([0022](../decisions/0022-leaving-a-space-is-a-write-the-space-can-refuse.md)), and how a practice is promoted ([0023](../decisions/0023-a-pattern-starts-private-and-rises-by-use.md)).
