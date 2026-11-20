---
kind: guide
title: Concepts
status: current
date: 2026-11-20
source: maintainers
---

# Concepts

A vault is a folder of living pages, held together by a body that never has to think. Each section links to its technical page. For the hands-on version, see [getting started](getting-started.md).

## Everything is somebody

Every page is a character, not a record, with an identity, a temperament and a voice. The signed history, the rules and the reactions are its body: reflexes it never thinks about, so a character can be odd without breaking a house rule. Today the example vaults hold human-written content and a page can ask a model. No page yet has a generated temperament or voice.

In detail: [everything is somebody](../decisions/0020-everything-is-somebody.md) and [a page with a self](../ideas/character.md).

## Pages

A page is an index card: a title, a few labelled facts and ordinary text underneath. It can be a person, a tool, a store of data or a set of rules. Everything is a page, so everything reads the same way and nothing is visible only to a program.

In detail: [vault format](../reference/vault-format.md#pages).

## Spaces

A space is a page that other pages belong to. Its members follow its rules, as the cooler and the daybook follow the stand's, and a space can belong to a larger space.

<p align="center"><img src="../assets/figures/fig-2-spaces.svg" alt="A large sheet labelled space holds two pages and a smaller space, which holds two pages of its own. A rule is written once at the top of the large sheet, and thin lines carry it down to every page, including the pages in the smaller space." width="800"></p>

<p align="center"><em>Fig. 2. A rule written once on a space reaches every page in it, including the pages of a space within it. Schematic, not data.</em></p>

In detail: [rules and spaces](../reference/rules-and-reactions.md#rules-and-spaces).

## Rules

A rule is a statement that must be true after every change, such as "the cooler never holds less than nothing". A change that would break it is refused, and the refusal is recorded.

A note on the wall depends on people remembering it. A rule is a turnstile: it does not argue and needs no reminding.

In detail: [rules and refusals](../reference/rules-and-reactions.md#refusals).

## Reactions

A page can watch another. When the watched page changes and a stated condition holds, the watcher updates itself: the cups fall below a threshold and the supplier writes an order, with nobody deciding to. It works like a spreadsheet, where one cell changing updates the cells that depend on it.

A reaction is a reflex, so no one spends thought on it, person or model. The thought goes to what a reflex cannot do: judgement, curiosity and a page's own manner (see [Asking a model](#asking-a-model)).

Reactions can set off further reactions. A limit stops a loop, and a reaction that would change nothing is skipped.

In detail: [reactions](../reference/rules-and-reactions.md#reactions).

## Asking a model

Asking a model is how a page thinks, for questions the facts cannot answer, such as how a tired supplier would word an order. The question is written in a watch entry or given with `conky ask`, and the answer lands in one of the page's own fields. An entry can also let the answer hold pages, written into a space it names, so that a character can make notes, other characters and rules for itself, inside limits the runtime enforces ([an answer that is pages](../reference/rules-and-reactions.md#an-answer-that-is-pages)).

The page that asked signs the answer, and its rules apply. The history keeps the question beside it, with the model's name and the tokens used when the provider reports them. A refused answer is recorded with its reason. Reading the history never calls a model.

Which model answers is one provider page, holding an address, a model name and the name of a secret. Changing provider means editing that page. The secret is never stored in the vault. If the provider cannot be reached, the failure is recorded on the asking page and nothing else is affected.

This works against stand-in servers in the tests. It has not been run against a live provider.

In detail: [asking a model](../reference/rules-and-reactions.md#asking-a-model) and [providers](../reference/providers.md).

## Measures and pressure

A measure is a page watching itself and keeping a number up to date, such as how large it has grown.

Pressure is a measure of how crowded something is. A hard limit stops work at the worst moment. Pressure only rises, like clutter nudging someone to tidy up, and other pages can react when it passes a threshold. Hard rules stay for what must never happen. Nothing yet relieves pressure: today it is recorded and noticed.

<p align="center"><img src="../assets/figures/fig-3-pressure.svg" alt="Two panels. In the first, a page meets a wall and work stops. In the second, a page has a gauge that rises past a marked level, and a dashed line then sets off a tidy-up while work goes on." width="800"></p>

<p align="center"><em>Fig. 3. A wall stops work; pressure only rises, and past a mark it sets off a tidy-up. Schematic, not data.</em></p>

In detail: [measures](../reference/rules-and-reactions.md#measures).

## History

Every change is an entry: what changed, who changed it and when. A refused change is kept too, with the reason. Nothing is edited in place, so the pages are only the latest view, and a deleted or damaged page can be restored exactly.

The history is ordinary Git. Pages must be changed through conky, not by hand: a hand edit is noticed and blocks the next change until it is discarded.

In detail: [vault format](../reference/vault-format.md#commits).

## Keys and signatures

Each author, a person or a reacting page, has a key: a private half that stays with its owner and a public half kept in the vault. Every entry is signed with the private half. Anyone holding the vault can check the signature against the public half, like a signature on a paper form checked against a specimen on file. It shows who made the change and that it has not been altered since.

Private keys are never stored in the vault. By default they live in a folder in the user's home directory.

In detail: [identity and signing](../reference/vault-format.md#identity-and-signing).

## What moving a vault means

A vault is an ordinary folder under version control. Copy it, send it as a single file or put it on a Git host, and read it on the other side with tools already installed. The copy carries its history and the public keys, so it can be checked for tampering without asking the original.

It does not carry private keys. To keep writing as the same author somewhere new, bring that author's private key too.

One limit: removing the most recent entries from a single copy cannot be detected by that copy alone. It shows up when compared with another copy.

<p align="center"><img src="../assets/figures/fig-4-travels.svg" alt="A vault, a folder of pages with its history tape, is copied whole to another place, where it is identical. A dashed line shows the private keys stopped at a bar: they stay behind." width="800"></p>

<p align="center"><em>Fig. 4. A vault is copied whole, history included; private keys stay where they were. Schematic, not data.</em></p>

In detail: [what verify checks](../reference/vault-format.md#what-verify-checks) and [decision 0002](../decisions/0002-git-is-the-store.md).
