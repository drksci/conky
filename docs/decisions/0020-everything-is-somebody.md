---
kind: decision
title: Everything is somebody
status: accepted
date: 2026-11-20
source: maintainers
arch:
  covers:
  - kind.character
---

# 0020 Everything is somebody

## Context

- The earlier wording, in [decision 0007](0007-inference-for-real-thinking.md) and the pages that cite it, made frugality with the model sound like the aim. Read that way, conky would be a deterministic system that tolerates a model at the edges, and that is not the aim.
- Today the example vault holds human-written content, a page can ask a model, and nothing yet gives a page a generated temperament or a voice of its own.

## Decision

Everything in a vault is somebody. A page is a character with an identity, a temperament and a voice, not a record with fields. Characters notice things, have a manner, take an interest, change their minds and write in their own words. That liveliness is what the AI is for.

The deterministic parts are the body, not the mind. Signed history, rules and reactions are reflexes and physics, the things a living creature never has to think about. No thought is spent on bookkeeping, and characters can be unpredictable without being dangerous: a character may be as odd as it likes and still cannot break a house rule.

The principle is therefore not "call the model as little as possible". Reflexes are free, so thought goes into character. Cost is a constraint to manage with budgets, not a goal. Two runs of the same vault should differ, the way two days do, above a floor that never moves.

## Consequences

- Every page may carry a self (a seed, a face, a temperament, a voice), not only pages that act as agents. See [a page with a self](../ideas/character.md).
- Reactions and model pages write in the page's own voice, with a plain sentence as the fallback when no model is available.
- Behaviour above the rules may vary between runs. The rules, the signed history and the refusals do not.
- Budgets bound cost. A budget stops spending; it does not decide whether a character may think.
- [Decision 0007](0007-inference-for-real-thinking.md) is amended, not withdrawn: what follows from state still happens with no model call, and the reason is now stated as freeing thought for character.

## Open questions

- How a temperament is described.
- How much variety is welcome before a vault becomes hard to follow.
- How character is kept consistent over time.
