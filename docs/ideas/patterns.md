---
kind: idea
title: Patterns
status: idea
date: 2026-11-20
source: operator
---

# Patterns

## Idea

The runtime should not contain domain machinery such as a ledger. Instead there is a library of patterns, much like agent skills. Each pattern is a named recipe. It says when to use it and how to compose the existing words (pages, spaces, rules, reactions, tables) into a known structure, for example profit and loss, double-entry accounts, stock control, an approval step, or a clearing house for mutual debts.

Applying a pattern is just a series of ordinary writes. Everything it creates is therefore in the log, and it can be changed afterwards like anything else. A pattern is itself a page, so actors can read, apply and write new ones. A structure that works can be promoted into a pattern.

## Composes from

Page, space, rule, watch, and tables when they exist. The pattern library is a vault of pages.

## Removes

The ledger as a built-in, and any other domain feature that would otherwise be added to the runtime.

## What it exposes

Trying to express double-entry as a pattern shows what the ledger idea was really hiding. There is a general need for one write to change several pages together, all or nothing, with rules able to see the whole group. That makes it possible to check that what leaves one account arrives in another. This grouped write is the primitive worth building. Accounting is then only a pattern on top of it.

## Falsifying test

Double-entry bookkeeping, with conservation enforced, can be set up entirely by applying a pattern, with no accounting-specific code in the runtime. If it needs a runtime change, that change must be a general primitive usable by unrelated patterns.

## Prior art

- Agent skills: named, lazily loaded recipes that an agent reads when it needs them.
- The earlier archive idea of patterns promoted by agreement (archive turn 42).
