---
kind: decision
title: What lands in this repository
status: accepted
date: 2026-11-28
source: maintainers
arch:
  items:
  - kind: unplaced
    name: what lands here
    text: This repository holds conky and what is about conky. An experiment built on it lives elsewhere, and a change it prompted is said here without it.
---

# 0068 What lands in this repository

## Context

- Experiments are built on conky in other repositories. Some bring a world of their own: a vendored engine, data that cannot be published, a heavy build.
- The rules already say that nothing internal is committed and that conky depends on nothing built on it. They did not say, in one place, what belongs here and what does not, so each change had to be judged afresh.
- Two changes on 28 November 2026 were prompted by an experiment and were sayable without it: an embed inside an embed ([0064](0064-an-embed-inside-an-embed-is-followed.md)) and a character born with a memory ([0066](0066-a-character-is-born-with-a-memory-and-a-sense-for-what-changed.md)). Each landed with a card that shows the need in conky's own terms. That is the form to keep.

## Decision

- This repository holds conky and what is about conky: the runtime, its documents, its benchmarks and their published results.
- An experiment built on conky lives in a repository of its own. None of it lands here: not its code, its records, its documents or its words.
- A change an experiment prompted is said here in conky's own vocabulary, with a card that shows the need without the experiment. If it cannot be said without the experiment's words, it is not a change to conky.
- A benchmark belongs here: it states itself before it runs, compares conky with something else on the same model and budget, and publishes its results. An experiment does not: it explores, and it may bring a world of its own.

## Consequences

- A reviewer of a change here asks one more question: could this be read by somebody who has never heard of the experiment that prompted it.
- The rule is held by review. A check that searched for named strings would be a list of what is banned, which the rules refuse; no property has been found yet that a check could assert.
- An exploratory trial that later grows a baseline and published results can move here as a benchmark, written again for this repository.
