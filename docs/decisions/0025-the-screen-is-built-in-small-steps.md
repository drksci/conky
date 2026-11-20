---
kind: decision
title: The people's screen is built in small steps, and the trail is the first trial
status: accepted
date: 2026-11-20
source: maintainers
arch:
  covers:
  - part:screen
  - flow:screen-and-prompt
  items:
  - kind: part
    name: trail-trial
    layer: edge
    text: 'The exploratory trail trial: a party plays a text Oregon Trail through the terminal connector, run by Conky and by a plain single-loop baseline.'
    roadmap: R27
---

# 0025 The people's screen is built in small steps, and the trail is the first trial

## Context

- The screen ([a screen from the pages](../ideas/a2ui.md), [the compositor](../ideas/compositor.md), the activity strip) is designed and unbuilt. A large build before the Rust core would be a large refactor later.
- The [evaluation plan](../research/evaluation-plan.md) has no first case anyone can run.

## Decision

Build the screen as a ladder. Every step is derived data, can be deleted, has a golden test and leaves the checks green.

1. A text outline of a vault.
2. The same as A2UI messages for one surface.
3. One static page that renders those messages, with no server.
4. Updates as the history grows.
5. The activity strip, from the record's trailers.
6. A prompt button that makes an ordinary write.
7. The compositor, which thinks once about layout and then keeps up by reflex.

The Rust core may begin after step 3.

The first trial of the whole system is exploratory and not a benchmark result. A party plays a text Oregon Trail through the terminal connector.

- The scenario is harness-neutral: the seed prompt "You just woke up in a parallel universe and you're on the Oregon Trail", a fixed game and seed, observables, and a scoring note. The observables are miles reached, who survived, turns, model calls, tokens and refusals.
- It is run by Conky and by one plain single-loop baseline, on the same model and budget, with raw traces kept.
- A second form stops the party mid-trail and hands the vault to a fresh consumer, as in the [assimilation test](../ideas/assimilation-test.md).

## Consequences

- Nothing is claimed from the trial until runs are unscripted and repeated.
- It needs [decision 0024](0024-a-model-is-reached-by-a-key-or-a-local-program.md) first.
- Results are kept in the three classes of the evaluation plan: mechanism, harness and prompt.
- The roadmap carries the ladder as R11a to R11g and the trial as R27.
