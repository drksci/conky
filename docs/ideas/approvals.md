---
kind: idea
title: Approvals as a pattern
status: idea
date: 2026-11-20
source: maintainers
---

# Approvals as a pattern

## Idea

A change that needs several parties to agree is a proposal page, signed agreement from each approver, a rule that counts them, and a reaction that applies the change once the rule is met.

The same shape serves an owner signing off, a practice promoted to a shared pattern ([patterns](patterns.md)) and a dispute being settled. It is a pattern, not a runtime feature ([decision 0009](../decisions/0009-patterns-not-features.md)). Nothing of this is built.

## Composes from

Page, rule, watch, seal.

## Removes

A separate approval subsystem.

## Falsifying test

A change that needs two approvals cannot take effect with one, takes effect by itself on the second, and the history shows who approved.

## Open questions

- Rules that can see who signed a change.
