---
kind: decision
title: A rule for the pages within
status: accepted
date: 2026-11-20
source: maintainers
arch:
  covers:
  - law.rule.tighten
  - part.space
---

# 0034 A rule for the pages within

## Context

- A small model was asked to keep a floor under every payment. Five of five draws wrote the right condition, `page.amount <= space.cash - 20`. Four of them put it on the payment's own page, where it binds that one payment and not the next.
- A rule on a space applied to the space page too, so a rule about payments needed guards such as `has()` and `int()` to let the space itself through. The binding playbook carried those guards.
- The difference sought: a character states a limit for a whole kind of act in one line and the runtime holds it. No compared harness evaluates a constraint outside the model.
- Prior art: inheritance of constraints down a hierarchy is common in access and policy systems, where a policy on a folder covers what lies inside it. None of the compared harnesses states one as a plain condition the runtime evaluates.

## Decision

A rule entry is a condition as text, as before, or a mapping with the one key `within` whose value is a condition.

A plain condition keeps its meaning: it applies to the page that carries it and to every page within it. A `within` condition applies to every page within the page that carries it, at any depth, and never to that page. The word is the one the vault already uses for that relation. Any other mapping is refused for shape, and the reason says what is allowed.

A write is judged by the plain rules of the page and of every space above it, and by the `within` rules of every space above it. A write that leaves a space is judged by that space's `within` rules as well. A refusal names the condition and the space it came from, as before.

The fixed statement of an ask that may write pages gains one clause, so a character knows it can write such a rule.

The key `within` was renamed `each` by [decision 0035](0035-a-character-binds-its-own-space.md), because a small model read it as the membership field. The text below keeps its original words.

## Consequences

- A space can bind a kind of act without carrying the field, and the binding playbook no longer needs guards.
- A page within the space that lacks the field fails the rule, as any missing field does, so a space page nested under a bound space must carry it.
- Whether a small model writes a `within` rule unprompted is a forecast on the card `a-keeper-binds-itself`, not yet drawn.
