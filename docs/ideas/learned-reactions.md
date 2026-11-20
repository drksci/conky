---
kind: idea
title: Learned reactions
status: idea
date: 2026-11-20
source: maintainers
arch:
  items:
  - kind: unplaced
    name: learned reactions
    text: A repeated model answer becomes a reaction and the model is no longer asked. It is carried by the lens idea.
---

# Learned reactions

## Idea

When a model-backed page keeps giving the same answer to the same question, the answer becomes a reaction and the model is no longer asked. Cases it does not cover still go to the model. Source: the [research index](../research/dair-2026.md).

## Composes from

`watch`, rule, event. The log shows the repeated question and answer with their cause.

## Removes

Repeated inference for settled decisions.

## Falsifying test

Over a long run, model calls per unit of work fall while refused writes and outcome quality do not get worse.
