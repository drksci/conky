---
kind: idea
title: Approvals as a pattern
status: idea
date: 2026-11-20
source: maintainers
arch:
  covers:
  - part:who-signed
  items:
  - kind: part
    name: who-signed
    layer: reflexes
    text: Rules that can see who signed a change and how it arose.
    roadmap: R14
  - kind: archetype
    name: proposal
    by: a character or a person
    layer: characters
    text: A page that gathers approvals, with a reaction that applies the change.
    roadmap: R14
  - kind: flow
    name: approval
    title: Approval of a proposal
    statement: A change that needs several parties is a proposal, signed approvals, a rule that counts them and a reaction that applies it.
    rank: 12
    steps:
    - frm: Page
      to: Runtime
      text: a proposal page names the change
    - frm: Person
      to: Runtime
      text: an approval, signed by the approver
    - frm: Runtime
      to: History
      text: the approval is an event with its signer
    - frm: Space
      to: Runtime
      text: a rule counts the approvals and can see who signed
    - frm: Runtime
      to: Page
      text: a reaction applies the change once the rule is met
    - frm: Runtime
      to: History
      text: the change, caused by the last approval
    - frm: Space
      to: null
      text: one approval is refused where two are needed
    roadmap: R14
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
