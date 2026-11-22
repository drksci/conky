---
kind: idea
title: Patterns
status: idea
date: 2026-11-22
source: maintainers
arch:
  items:
  - kind: part
    name: part.write.group
    layer: layer.history
    text: Several pages changed in one commit, with rules that see the whole group.
    roadmap: R24
  - kind: archetype
    name: kind.pattern
    by: a character, through the pattern maker
    layer: layer.space
    text: A space made on demand from goldens, private at first and rising by use.
    roadmap: R6
---

# Patterns

## Idea

The runtime holds no domain machinery such as a ledger. A pattern maker, much like a skill generator but for professional domains and the dynamics of businesses and teams, takes goldens (worked examples of good practice: a structure that already works in a vault, a professional method, a standard process) and distils them into a recipe that can be applied again.

A pattern is a space: a named recipe that says when to use it and how to compose existing words (pages, spaces, rules, reactions, tables) into a known structure. Applying it is joining its space, and a page may join several ([what a space hands down](inheritance.md)). A pattern is itself a page, so actors can read, apply and write new ones, and a structure that works can be promoted into a pattern. A pattern starts private to the space that made it and rises one space at a time by use ([decision 0023](../decisions/0023-a-pattern-starts-private-and-rises-by-use.md)).

There is no shipped catalogue. Profit and loss, double-entry accounts, stock control, approvals and a clearing house for mutual debts are things the maker could be asked to produce, and they appear when a need or a good example does. Applying a pattern is a series of ordinary writes, so everything it creates is in the vault's Git history and can be changed like anything else. Nothing of this is built.

## The maker

The input is one or more goldens and a statement of the need. The output is a space page holding the pattern's rules, context and reactions. Making a pattern is real thinking, so it is one of the places a model is asked. Applying one needs no model.

## Composes from

Page, space, rule, watch, and tables when they exist. Made patterns are pages in a vault.

## Removes

The ledger as a built-in, and any other domain feature that would otherwise enter the runtime.

## An offer between neighbours

A page that links to a peer is noticed by the built link watch. Taking the offer up is joining the peer's space, and the receiver's space may refuse the join like any write. Rising by use ([decision 0023](../decisions/0023-a-pattern-starts-private-and-rises-by-use.md)) is the count of such joinings, so sideways and upward are one motion counted two ways. No mechanism is added: the link, the join and the refusal all exist.

## What it exposes

Expressing double-entry as a pattern shows what the ledger idea was hiding: a general need for one write to change several pages together, all or nothing, with rules able to see the whole group, so that what leaves one account arrives in another. Git can commit several files together ([decision 0002](../decisions/0002-git-is-the-store.md)), but a write changes one page per commit today. What remains to build is a write that changes several pages together, and rules that can see the whole group. Accounting is then only a pattern on top.

## What a rule on the page as it was makes writable

Rung: idea. Nothing here is built. These are patterns that become writable once a rule can read `event.was` ([a rule sees the page as it was](the-page-as-it-was.md)). Each is a rule a character writes, from words that already exist, so none is a feature:

- A base check by a count. A page carries a `rev`; a write must name the next one, so a write made from an old reading is refused. Composes from: a field, `event.was`, a refusal.
- A counter that only goes up. A write may not lower a number it already held. Composes from: a field, `event.was`.
- Allowed transitions between states. A status moves along the steps listed and never back. Composes from: a field, `event.was`, a list.
- A field one actor owns. Anyone may write the page, and a change to that field by anyone else is refused. Composes from: `event.by`, `event.was`.
- A body that only grows. A write may add to what was there and not cut it. Composes from: `event.was`, which may need to give the body, a question left open on that page.
- A type that holds once set. A field written once keeps its value. Composes from: `has` on `event.was`, a field.
- A retired page. Once a page says it is retired, no later write is kept. Composes from: a field, `event.was`.
- A budget the bound page cannot raise. The page carries its own budget and may spend it and may not enlarge it; only the space that bound it may. Composes from: the `budget` field ([decision 0058](../decisions/0058-a-budget-the-runtime-holds.md)), `event.by`, `event.was`.
- A comment with two writable fields. Of the fields a comment page carries, only two may change after it is written. Composes from: `event.was`, a rule on each other field.

## Falsifying test

Given a golden of double-entry bookkeeping, the maker produces a pattern that, when applied, sets up accounts with conservation enforced and no accounting-specific code in the runtime. If it needs a runtime change, that change must be a general primitive usable by unrelated patterns.

For offers: a page that links to a neighbour's pattern is noticed by that neighbour, an offer taken up appears as a join in history and one refused appears as a refusal, and the count of joinings is the only measure of rising. If a second mechanism is needed for sideways offers, the claim that the two motions are one is lost.

## Prior art

- Agent skills: named, lazily loaded recipes that an agent reads when it needs them.
- Skill generators: tools that turn examples and intent into a reusable skill.
