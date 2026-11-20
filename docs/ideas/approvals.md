---
kind: idea
title: Approvals as a pattern
status: idea
date: 2026-11-20
source: maintainers
arch:
  covers:
  - part.seal.signer
  items:
  - kind: part
    name: part.seal.signer
    layer: layer.reflex
    text: Rules that can see who signed a change and how it arose.
    roadmap: R14
  - kind: archetype
    name: kind.proposal
    by: a character or a person
    layer: layer.character
    text: A page that gathers approvals, with a reaction that applies the change.
    roadmap: R14
  - kind: flow
    name: flow.proposal.approve
    title: Approval of a proposal
    statement: A change that needs several parties is a proposal, signed approvals, a rule that counts them and a reaction that applies it.
    rank: 12
    steps:
    - frm: lane.page
      to: lane.runtime
      text: a proposal page names the change
    - frm: lane.person
      to: lane.runtime
      text: an approval, signed by the approver
    - frm: lane.runtime
      to: lane.history
      text: the approval is an event with its signer
    - frm: lane.space
      to: lane.runtime
      text: a rule counts the approvals and can see who signed
    - frm: lane.runtime
      to: lane.page
      text: a reaction applies the change once the rule is met
    - frm: lane.runtime
      to: lane.history
      text: the change, caused by the last approval
    - frm: lane.space
      to: null
      text: one approval is refused where two are needed
    roadmap: R14
---

# Approvals as a pattern

## Idea

A change that needs several parties to agree is a proposal page, signed agreement from each approver, a rule that counts them, and a reaction that applies the change once the rule is met.

The same shape serves an owner signing off, a practice promoted to a shared pattern ([patterns](patterns.md)) and a dispute being settled. It is a pattern, not a runtime feature ([decision 0009](../decisions/0009-patterns-not-features.md)). Nothing of this is built.

## Somebody is told

A page can be noticed by relation and not only by name. Two relations are built: a page written within, and a page that links. A third is a refusal, built ([decision 0039](../decisions/0039-an-event-can-be-noticed.md), rung: enforced): a write by a page, or to a page within it, was refused, with the reason in scope. A refused write is already an event in history, but nothing can react to it, so the author's space never learns it is stuck. A watch on the refusal relation lets an owner be told, lets a character learn from its own refusals between turns, and lets a stuck page be noticed rather than left. It is a relation for a watch, not a new kind of thing.

The same relation serves an approval: a proposal refused for lack of a second signature tells the proposer why.

## Composes from

Page, rule, watch, seal.

## Removes

A separate approval subsystem.

## Falsifying test

A change that needs two approvals cannot take effect with one, takes effect by itself on the second, and the history shows who approved. Separately, a write refused in a space is followed by a reaction of the owning page, with the refusal's reason readable, and a refusal in an unwatched space causes no reaction.

## Open questions

- Rules that can see who signed a change.
