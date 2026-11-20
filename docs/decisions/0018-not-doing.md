---
kind: decision
title: What conky will not do
status: accepted
date: 2026-11-20
source: maintainers
---

# 0018 What conky will not do

## Context

A runtime grows by accepting reasonable requests. Some would undo the properties the design depends on: one authority, a vault that travels alone, and a small set of general words.

## Decision

conky will not:

- Batch many changes into one commit to hide them. Each change should be visible in history; high-frequency data goes in data files ([decision 0003](0003-data-beside-pages.md)).
- Add a second authority beside the vault's history, such as a live collaborative-editing store, because two authorities can disagree and only one can be verified.
- Require companion documents for every page, because a page should be enough to read on its own.
- Keep state in a hidden runtime directory. Derived data is allowed because it can be deleted ([decision 0017](0017-derived-data.md)).
- Use instructions to a model as a means of control. Context may be given, but nothing is enforced by asking ([decision 0007](0007-inference-for-real-thinking.md)).
- Build domain features such as a ledger or an economy into the runtime, because those are patterns ([decision 0009](0009-patterns-not-features.md)).

## Consequences

- A request that needs one of these is answered with the pattern or general primitive that serves it, or declined.
- Changing this list needs a new decision record that supersedes this one.
