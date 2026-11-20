---
kind: idea
title: Trying a change first
status: idea
date: 2026-11-20
source: maintainers
arch:
  items:
  - kind: flow
    name: flow.write.try
    title: Dry run on a branch
    statement: A change is applied on a throwaway branch, the consequences are reported and the branch is discarded.
    rank: 5
    steps:
    - frm: lane.person
      to: lane.runtime
      text: what would this change do
    - frm: lane.runtime
      to: lane.history
      text: a throwaway branch
    - frm: lane.runtime
      to: lane.page
      text: apply the change on the branch, with its reactions
    - frm: lane.runtime
      to: lane.person
      text: the refusals and reactions that would follow
    - frm: lane.runtime
      to: lane.history
      text: discard the branch and record nothing
    roadmap: R13
---

# Trying a change first

## Idea

Before making a change, an actor can ask what would happen: whether rules would refuse it and which reactions would follow. The change is applied on a throwaway branch of the vault's history, the consequences are reported, and the branch is discarded, so nothing is recorded. Nothing of this is built.

## Composes from

Write, event, rule, watch, and Git branches ([decision 0002](../decisions/0002-git-is-the-store.md)).

## Removes

Guesswork, and refused changes that could have been foreseen.

## Falsifying test

A dry run reports exactly the refusals and reactions that the real write then produces, and leaves the history untouched.
