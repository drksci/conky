---
kind: decision
title: Reflexes are free, so thought goes into character
status: accepted
date: 2026-11-20
source: maintainers
arch:
  covers:
  - law.reflex.free
  - stage.think.ask
---

# 0007 Reflexes are free, so thought goes into character

## Context

- A decision that follows directly from state, such as reordering when stock is low, needs no opinion.
- Asking a model to make it adds cost, delay and variance, and buries the reason for the action in generated text.
- That does not make the model something to avoid. The question is where thought is worth spending.
- This record was first titled as if inference were reserved for rare, serious cases; [decision 0020](0020-everything-is-somebody.md) corrects that reading.

## Decision

Whatever follows from state happens as a reflex in the runtime, with no model call, so that model calls can be spent on character, judgement, conversation and curiosity. A model is asked when a page poses a question state cannot answer, or when a page writes in its own voice. Avoiding the model is never the aim.

## Consequences

- Reflexes are deterministic and need no model. Bookkeeping never costs a thought.
- A page asks a model through a provider page and a watch entry with `ask` ([decision 0019](0019-providers-are-pages.md)).
- Model calls are bounded by budgets, not by reluctance.
- Pages may write in their own voice; see [everything is somebody](0020-everything-is-somebody.md).

See [things-that-just-happen](../essays/things-that-just-happen.md).
