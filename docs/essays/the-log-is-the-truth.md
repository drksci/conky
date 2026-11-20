---
kind: essay
title: The log is the truth
status: current
date: 2026-11-20
source: maintainers
---

# The log is the truth

## What prompted it

Open a shared folder a team has used for a year and ask how one page came to say what it says. Usually nobody can tell you. The page is there, and whatever history exists is a side effect of the tool that saved it. A system has to choose what counts as the truth: the documents, or the record of what happened to them. conky takes the record, and the record is the history of a Git repository ([decision 0002](../decisions/0002-git-is-the-store.md)).

## The problem

If documents are the truth, a document can change without a trace of why. Two writers overwrite each other, and a bad edit looks like a good one. When software actors do the work, nobody can say which actor did what, or whether a refused action was refused or never attempted. Changing the shape of the data is worse: the usual remedy is a migration, a script that rewrites the old documents, and the old form is gone afterward.

## Analogues

An accountant keeps a ledger and derives the balance from it; nobody edits the balance. Git keeps a chain of commits, and the files you see are one view of that chain. Event sourcing computes the current state from a stream of events, and a database keeps a write-ahead log so its tables survive a crash. In each, the record is primary and the picture is derived.

## The idea

In conky the authority is the Git history of the vault. Each commit is one event, signed with the SSH key of the actor who made it, and it carries its parent's hash, so altering a commit in the middle changes every id after it. The files in `pages/` are the committed state. A refused write is a commit too, an empty one with a `Kind: refused` trailer, so the refusal is on the record. A transition that is not recorded did not happen.

This is built. `verify` checks that the working tree is clean, that `git fsck` passes, that every commit carries a good signature from a key listed in the vault, and that each commit changed only what its kind allows. `rebuild` restores the working tree to the committed state. A vault moves with `git clone` or a bundle, and still verifies, since it carries its own history and public keys. Tables stored as Parquet are intended and do not exist yet.

The result is that nothing needs migrating: a new shape is a new reading of the same history, in a format everyone can already read. Who did what, and what was refused, can be answered from the record, and a page that differs from the committed state is a failed check, not a mystery.

## Hypothesis

A system that treats signed Git history as its only authority, and restores every page from it, stays correct and recoverable over a long run with no hand repair. A stranger handed only a stopped vault can understand it well enough to carry on.

## How it could be shown wrong

- `verify` passes on a vault whose pages cannot be trusted, or fails on a healthy one, in a real run rather than a constructed one.
- At one signed commit per write, real workloads are too slow to live in pages. Tens of writes per second is the expectation; a workload that needs more belongs in data files.
- A fresh consumer handed a stopped vault cannot resume correctly. This is the [assimilation test](../ideas/assimilation-test.md), and it is not built yet.
- A failure appears that the history cannot show. Two are known: history can be rewritten locally and is detectable only against another copy, and rules are not enforced on commits made outside conky (see [open questions](../project/open-questions.md) and [decision 0002](../decisions/0002-git-is-the-store.md)).
