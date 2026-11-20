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
- Who may change which space a page belongs to.
- Whether a page can leave a space by itself. See [inheritance](../ideas/inheritance.md).
- How a practice is promoted: by a person, by a vote among pages, or by either, set per space.
- How keys are rotated and revoked.
- How two vaults relate after a split. See [vault-splitting](../ideas/vault-splitting.md).

The first two are known gaps in the current runtime ([status](status.md)). A question that belongs to one decision is kept in that decision's record.
