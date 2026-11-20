---
kind: idea
title: Where a value came from
status: idea
date: 2026-11-20
source: "research/findings-rubric.md (F18, F19, F20 and gap 6), project/status.md (a model's answer is stored with nothing marking it as unchecked), and the dependency stated on the habit page"
arch:
  items:
  - kind: part
    name: part.rule.origin
    layer: layer.reflex
    text: 'Rules that can see where a page''s content came from: a person, a character, a model or a connector, and what a model read.'
    state: idea
    roadmap: R31
---

# Where a value came from

## Idea

The history already says how every value arrived: the signer of the event, its `Kind`, a `Model` trailer when a model answered and a `Read` trailer for each page the model saw. A rule sees none of it. This idea hands the rule an `origin` for the write it judges, computed by the runtime before the rule runs, so the rule stays pure. Origin travels: a page written from a model answer takes the origins of the pages in its `Read` trailers, so text copied from a connector's page keeps the mark of the outside. A space can then refuse a rule, a watch entry or a habit whose origin is outside or an unchecked answer until a person or a [reviewer](reviewer.md) has signed it. Marked content stays readable; it is only kept from becoming something that acts.

## Composes from

Trailers, signers ([`part.seal.signer`](../reference/architecture.md#part.seal.signer)), rules and the reviewer.

## Removes

Trust by position in a prompt, and any separate store of tainted text.

## Falsifying test

A watch entry copied from a connector's page is refused in a space that forbids outside origins, on every write path. A planted payload copied by a character into a new page keeps its origin. Replaying the history gives every write the same origin.

## Open questions

- Whether origin is kept per page or per field.
- Whether it is carried on the page as a reserved key or derived from the history at each write, which costs a read of the history.
