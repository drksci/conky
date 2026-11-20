---
kind: decision
title: Inference is for real thinking
status: accepted
date: 2026-11-20
source: maintainers
---

# 0007 Inference is for real thinking

## Context

A decision that follows directly from state, such as reordering when stock is low, does not need an opinion. Asking a model to make it adds cost, delay and variance, and buries the reason for the action in generated text.

## Decision

Whatever follows from state happens in the runtime with no model call. A model is asked only when a page poses a question state cannot answer.

## Consequences

- Reactions are deterministic and need no model.
- Model-backed pages are not built yet; this is the stated direction, not a present feature.

See [things-that-just-happen](../essays/things-that-just-happen.md).
