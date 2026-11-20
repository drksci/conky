---
kind: essay
title: Things that just happen
status: current
date: 2026-11-20
source: maintainers
---

# Things that just happen

## What prompted it

Consider a bakery's stall that runs low on bread. In a well-run shop, someone notices and the depot reorders. Nobody holds a meeting. Now picture the same thing built from AI agents: one agent notices the stock, asks another to think about it, which reasons about whether to reorder, and writes a message. Every step costs a model call, takes time, and can go wrong in a new way. Most of an organisation's activity looks like the bakery, not like a research problem ([decision 0007](../decisions/0007-inference-for-real-thinking.md)).

## The problem

Chains of model reasoning are slow, expensive and unpredictable. A decision that follows directly from state, such as "stock below ten, so reorder", does not need an opinion. Using a model for it adds cost and variance, and makes the system harder to audit, because the reason for an action is buried in generated text.

## Analogues

Spreadsheets recalculate dependent cells when an input changes, and no one asks a model. Database triggers fire when a row changes. Build systems rebuild only what depends on what changed. The immune system and reflexes respond to conditions without deliberation, which leaves slower thinking for situations that need it. In each case consequences follow state automatically, and judgment is saved for what cannot be automated.

## The idea

A conky page can watch another page. When the watched page changes and a `when` expression is true, the runtime writes the watching page, signed by that page's own key, and records the triggering event as the cause. Reactions cascade to a depth of 12 and are then refused as a cycle; a reaction that would change nothing is skipped, so stable states end. No model is called.

This is built and shown in the [getting started](../guide/getting-started.md) walkthrough: writing a stall with stock below 10 makes the depot change by itself. Inference is meant to be reserved for pages that pose a question state cannot answer. That part is not built: model-backed pages are on the [roadmap](../project/roadmap.md).

## What it solves

- Cost: routine consequences carry no inference bill.
- Determinism: the same state gives the same result, so behaviour can be replayed and checked.
- Auditability: each reaction is an event in the history with its cause named.
- Focus: model capacity is spent where it is actually needed.

## Hypothesis

Most of the activity of a running organisation can be expressed as deterministic reactions to state, so that model calls are rare and each one is a deliberate act of thinking rather than plumbing.

## How we would know we are wrong

- When a real organisation is modelled, the share of activity that truly needs judgment is large, and reactions cover only a small corner.
- Reaction rules grow so numerous and tangled that they are harder to maintain than the reasoning they replaced.
- Cascades or cycles become common in practice, rather than the rare edge the depth limit is meant for.
- A run that is not scripted shows model-driven pages doing routine work faster or more reliably than reactions. No such run has been made yet, so this is a hypothesis, not a finding.
