---
kind: idea
title: Patterns
status: idea
date: 2026-11-20
source: operator
---

# Patterns

## Idea

The runtime should not contain domain machinery such as a ledger. Instead there is a pattern maker. It is similar to a skill generator, but it works on professional domains and on the dynamics of businesses, organisations and teams. It takes goldens, which are worked examples of good practice: a structure that already works in a vault, a professional method, or a standard process. It distils them into a simple recipe of patterns, practices, methods and processes that can be applied again.

A pattern is a named recipe. It says when to use it and how to compose the existing words (pages, spaces, rules, reactions, tables) into a known structure.

There is no shipped catalogue. Nothing is defined in advance. Profit and loss, double-entry accounts, stock control, approvals, and a clearing house for mutual debts are things the maker could be asked to produce, not things that come built in. Patterns are produced when a need or a good example appears.

Applying a pattern is just a series of ordinary writes. Everything it creates is therefore in the vault's Git history, and it can be changed afterwards like anything else. A pattern is itself a page, so actors can read, apply and write new ones. A structure that works can be promoted into a pattern.

## The maker

The input is one or more goldens plus a statement of the need. The output is a pattern page.

Making a pattern is real thinking, so it is one of the places where a model is asked. Applying a pattern afterwards needs no model.

## Composes from

Page, space, rule, watch, and tables when they exist. Made patterns are pages in a vault.

## Removes

The ledger as a built-in, and any other domain feature that would otherwise be added to the runtime.

## What it exposes

Trying to express double-entry as a pattern shows what the ledger idea was really hiding. There is a general need for one write to change several pages together, all or nothing, with rules able to see the whole group. That makes it possible to check that what leaves one account arrives in another. Changing several pages together is now one commit, because the vault is a Git repository ([decision 0021](../decisions/0021-git-is-the-store.md)). What remains to build is rules that can see the whole group. Accounting is then only a pattern on top of it.

## Falsifying test

Given a golden of double-entry bookkeeping, the maker produces a pattern that, when applied, sets up accounts with conservation enforced, with no accounting-specific code in the runtime. If it needs a runtime change, that change must be a general primitive usable by unrelated patterns.

## Prior art

- Agent skills: named, lazily loaded recipes that an agent reads when it needs them.
- Skill generators: tools that turn examples and intent into a reusable skill.
- The earlier archive idea of patterns promoted by agreement (archive turn 42).
