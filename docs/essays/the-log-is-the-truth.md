---
kind: essay
title: The log is the truth
status: current
date: 2026-11-20
source: architect
---

# The log is the truth

## What prompted it

Open a shared folder that a team has used for a year and ask a simple question: how did this page come to say what it says? Usually nobody can tell you. The page is there, and the history, if there is any, is a side effect of whatever tool saved it. When we started conky we had to choose what would count as the truth: the documents, or the record of what happened to them. The lesson came from an earlier project, the Alphaville agency, and we took it seriously enough to make it the first law (see [decision 0003](../decisions/0003-log-is-authority.md)).

## The problem

If documents are the source of truth, then a document can change without leaving a trace of why. Two writers can overwrite each other. A bad edit and a good edit look the same once saved. Worse, a system whose work is done by software actors needs to know which actor did what, and whether a refused action was refused or simply never attempted. If the only evidence is the present state of the pages, those questions have no answer.

Structure changes make this harder. When the shape of the data changes, the usual remedy is a migration: a script that rewrites old documents into the new form. Each migration is a chance to lose something, and the old form is gone afterward.

## Analogues

The idea is old and well known. Accountants keep a ledger of entries and derive balances from it; nobody edits a balance directly. Version control systems such as Git keep a chain of commits, and the files you see are one view of that chain. Event sourcing, a common pattern in software, stores every change as an event and treats current state as something computed from them. Database systems keep a write-ahead log so that tables can be recovered after a crash. In each case the record of changes is primary and the current picture is derived.

## The idea

In conky, the authority is `log/events.jsonl`. Each line is one event. Each event is signed by the key of the actor who made it, and carries the hash of the line before it, so removing or altering an event in the middle breaks the chain. Pages in `pages/` are projections: the result of replaying the log from empty. A refused write is also an event, a `refused` entry, and it changes no page. A transition that is not recorded did not happen.

This is built. `verify` checks the chain, the seals, and that replaying the log reproduces every page file byte for byte. `rebuild` deletes the pages directory and regenerates it from the log. What is not built is anything beyond documents and the log: tables stored as Parquet are intended but do not exist yet.

## What it solves

- There is no migration. A new shape is a new projection of the same events.
- A vault can be copied to another machine and still verify, because it carries its own log and public keys.
- Who did what, and what was refused, is answerable from the record.
- Corruption is detectable: a page that does not match its replay is a failed check, not a mystery.

## Hypothesis

A system that treats the signed log as the only authority, and rebuilds every page from it, stays correct and recoverable over a long run without any hand repair of pages. We also expect that a stranger given only a stopped vault can understand it well enough to carry on.

## How we would know we are wrong

- `verify` passes on a vault whose pages cannot actually be trusted, or fails on a healthy vault, in a real run rather than a constructed one.
- Rebuilding takes so long on a long log that people stop doing it, which would make the guarantee decorative.
- A fresh consumer handed a stopped vault cannot resume correctly. This is the [assimilation test](../ideas/assimilation-test.md), and it is not built yet.
- We find a failure the log cannot show. One is already known: removing the final event is not detected when that event is a refusal (see [decision 0015](../decisions/0015-open-questions.md)).
