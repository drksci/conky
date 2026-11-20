---
kind: idea
title: Several writers at once
status: idea
date: 2026-11-20
source: "project/status.md (one signed commit per write), the terminal connector, which writes from its own process, and the AutoGen Core and AG2 notes in research/harnesses.md (local and distributed runtimes, a hub with a write-ahead log)"
arch:
  items:
  - kind: part
    name: part.write.serial
    layer: layer.history
    text: Writes from several processes to one vault taken one at a time, each judged against the state the one before it left.
    state: idea
    roadmap: R33
---

# Several writers at once

## Idea

A connector, a person at the command line and a background page can each want to write to one vault at the same moment. Every write reads the pages, judges the rules and commits. Two at once could judge against the same state and both be kept, or one could fail on a lock with an error that does not say what to do next. Neither has been tested. This idea makes the order explicit: one write at a time for each vault, in the order they were accepted, each judged against the state the last one left. A writer that cannot get its turn within a bounded wait is told so with an error that says what to do next. It never reached the runtime's judgement, so no event is lost and none is invented.

## Composes from

The write path, Git's own locking, and the refusal record for everything that was judged.

## Removes

A server in front of the vault as the only safe way to share it.

## Falsifying test

Two processes writing the same page at once give two events in one order, each judged against what the other left, and `verify` passes.

## Open questions

- Whether waiting writes queue only in memory or as a stream beside the vault.
- How this meets [vault splitting](vault-splitting.md), where a busy space becomes its own vault.
