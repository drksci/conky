---
kind: idea
title: Patterns
status: idea
date: 2026-11-20
source: maintainers
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

## What it exposes

Expressing double-entry as a pattern shows what the ledger idea was hiding: a general need for one write to change several pages together, all or nothing, with rules able to see the whole group, so that what leaves one account arrives in another. Git can commit several files together ([decision 0002](../decisions/0002-git-is-the-store.md)), but a write changes one page per commit today. What remains to build is a write that changes several pages together, and rules that can see the whole group. Accounting is then only a pattern on top.

## Falsifying test

Given a golden of double-entry bookkeeping, the maker produces a pattern that, when applied, sets up accounts with conservation enforced and no accounting-specific code in the runtime. If it needs a runtime change, that change must be a general primitive usable by unrelated patterns.

## Prior art

- Agent skills: named, lazily loaded recipes that an agent reads when it needs them.
- Skill generators: tools that turn examples and intent into a reusable skill.
