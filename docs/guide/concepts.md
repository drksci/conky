---
kind: guide
title: Concepts
status: current
date: 2026-11-20
source: maintainers
---

# Concepts

The ideas behind conky in plain language. Each section ends with a link to the technical page for that idea. For a hands-on version, see [getting started](getting-started.md).

## Pages

A page is a short document with a few labelled facts at the top and ordinary text underneath. Think of an index card: a title, some fields filled in, and a note. A page can stand for anything the system contains: a person, a team, a tool, a process, a store of data, a set of rules.

Everything is a page, so everything can be opened and read in the same way. There is no hidden database and no part of the system that only a program can see.

In detail: [vault format](../reference/vault-format.md#pages).

## Spaces

A space is a page that other pages belong to. A page names its space, and the page then follows the space's rules, much as the stalls in a market follow the market's rules. A space can itself belong to a larger space, and a page follows the rules of every space above it.

In detail: [rules and spaces](../reference/rules-and-reactions.md#rules-and-spaces).

## Rules

A rule is a statement that must be true after every change, such as "stock is never below zero". It is checked by the system each time, not left to the good behaviour of whoever is making the change. A change that would break a rule is refused. The refusal is recorded, and nothing else changes.

This is the difference between a rule and a request. A request in a note on the wall depends on people remembering it. A rule is like a turnstile: it does not argue and it does not need reminding.

In detail: [rules and refusals](../reference/rules-and-reactions.md#refusals).

## Reactions

A page can be set to watch another page. When the watched page changes and a stated condition is true, the watching page updates itself. A stall's stock falls below a threshold, and the depot's page marks a reorder, with nobody deciding to. This works like a spreadsheet, where changing one cell updates the cells that depend on it.

Reactions need no thinking, by a person or by an AI model. Thinking is meant for the questions that state cannot answer. That part is not built yet: no page can ask a model anything today.

Reactions can set off further reactions. A limit stops this from running forever, and a reaction that would change nothing is skipped.

In detail: [reactions](../reference/rules-and-reactions.md#reactions).

## Measures and pressure

A measure is a page that watches itself and keeps a number up to date, such as how large it has grown. It is the same idea as a reaction, applied to the page's own state.

Pressure is a measure of how crowded something is. A hard limit stops work at the worst moment. Pressure only rises, like a clutter that nudges someone to tidy up, and other pages can react when it passes a threshold. Hard rules stay for what must never happen. Nothing yet acts to relieve the pressure; today it is recorded and noticed.

In detail: [measures](../reference/rules-and-reactions.md#measures).

## History

Every change is kept as an entry in a history. An entry says what changed, who changed it and when. A refused change is kept too, with the reason. Nothing is edited in place and nothing is rewritten, so the pages are only the latest view of the history.

This gives two things. Anyone can see who changed what and why. And any page can be put back as it was: if the pages are deleted or damaged, they can be restored from the history exactly.

The history is an ordinary Git history, readable with the tools that already exist for it. The pages must be changed through conky, not by hand. A hand edit is noticed, and it blocks the next change until it is discarded.

In detail: [vault format](../reference/vault-format.md#commits).

## Keys and signatures

Each author of a change, whether a person or a page that reacts, has a key: a private half that stays with its owner and a public half that is kept in the vault. Every entry in the history is signed with the author's private key. Anyone holding the vault can check the signature against the public half, so a signature shows who made the change and that the entry has not been altered since. It works like a signature on a paper form, checked against a specimen on file.

Private keys are never stored in the vault. By default they live in a folder in the user's home directory.

In detail: [identity and signing](../reference/vault-format.md#identity-and-signing).

## What moving a vault means

A vault is an ordinary folder of ordinary files under version control. It can be copied, sent as a single file, or placed on a Git host, and it can be read on the other side with tools that are already installed. The copy carries its history and the public keys, so it can be checked for tampering without asking the original.

A copy does not carry private keys. To keep writing as the same author in a new place, the author's private key has to be present there too.

One limit applies. Removing the most recent entries from a single copy cannot be detected by that copy alone. It shows up when compared with another copy.

In detail: [what verify checks](../reference/vault-format.md#what-verify-checks) and [decision 0002](../decisions/0002-git-is-the-store.md).
