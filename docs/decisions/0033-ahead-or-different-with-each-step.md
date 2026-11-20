---
kind: decision
title: Ahead or different with each step
status: accepted
date: 2026-11-20
source: maintainers
arch:
  items:
  - kind: unplaced
    name: ahead or different with each step
    text: Every step states the difference it makes against other harnesses and how that is shown; parity work waits until a difference depends on it.
---

# 0033 Ahead or different with each step

## Context

- The second pilot put a Conky character level with a plain loop on arrivals: four of five each. It sent less text, and that was the only difference shown.
- The parts that make Conky different are known: a signed history, rules the runtime enforces, a refusal that is recorded, a vault that travels, a character that writes pages. Most of the work since has been plumbing those parts share with any harness.
- A project can stay busy on parity for a long time and show nothing a reader could not get elsewhere.

## Decision

Every roadmap step states, in one line, what it puts Conky ahead on or makes it meaningfully different in, measured against the harnesses compared in [the harness comparison](../research/harnesses.md), and how the difference will be shown: a test, a probe or a measure.

Work that only brings Conky level is done when a step that makes a difference depends on it, and not before. Unbuilt work is ordered by the difference it makes, not by how near it is to finished.

A difference is claimed only at the rung it has reached: stated, held by a test, walked once, or measured.

## Consequences

- The order of work changes. A rule that a character wrote and a model cannot break, and notes a character kept and later used, move ahead of further benchmark plumbing, because they are where a plain loop has no answer.
- The step marked next in the roadmap carries its difference line, and the docs check looks for it.
- The harness comparison has to be kept current, since the claim is made against it.
- Some finished work shows no difference alone. It is described as groundwork, not as an advantage.
