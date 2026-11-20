---
kind: idea
title: Learned reactions
status: idea
date: 2026-11-20
source: maintainers
---

# Learned reactions

## Idea

When a model-backed page keeps answering the same question the same way, the answer is promoted to a deterministic reaction, so the model is no longer asked. Unsupported cases still go to the model. Source: the [research index](../research/dair-2026.md).

## Composes from

`watch`, rule, event. The log shows the repeated question and answer with their cause.

## Removes

Repeated inference for settled decisions.

## Falsifying test

Over a long run, model calls per unit of work fall while refused writes and outcome quality do not get worse.
