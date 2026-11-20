---
kind: design
title: Design
status: current
date: 2026-11-20
source: maintainers
---
# Design

A short technical overview. The detail is in three reference pages and in the decision records. For the ideas in plain language, start with [concepts](guide/concepts.md).

## The model

A vault is a plain Git repository. Its pages are Markdown files under `pages/`, and its history is the authority: every change to a page is one signed commit, and a write that is refused is recorded as an empty signed commit. What is not in the history did not happen.

conky keeps no log, hash chain or key format of its own. Git already provides tamper-evident history, signed commits, exact restore, transport by clone, push or bundle, and atomic multi-file changes, with tools that exist almost everywhere. conky is what sits on top: rules, reactions, measures and a few conventions ([decision 0002](decisions/0002-git-is-the-store.md)).

An event is a commit. A seal is its signature. The vault holds public keys only; private keys live in a separate directory. A reader given only the vault can verify it and read it with nothing but Git.

## Derived data

Anything built to make a vault faster or nicer to use is derived data: indexes, caches, snapshots and generated views. It is optional, lives outside the history in a directory that Git ignores, and can be rebuilt from the vault alone. It can be deleted at any time without losing anything, and nothing reads it as the truth ([decision 0017](decisions/0017-derived-data.md)).

## The parts

- **Pages and the vault format.** Layout, commit conventions and trailers, signing and identity, and what `verify` checks: [vault format](reference/vault-format.md).
- **Rules, reactions and measures.** The expression language, variables in scope, inheritance through spaces, refusal reasons, the reaction depth limit, and measures built from self-watches: [rules and reactions](reference/rules-and-reactions.md).
- **The command line.** Each command, its options, exit codes and error behaviour: [command line](reference/cli.md).

## Decisions

Each choice has a record in [decisions](decisions/). Those that shape the whole design:

- [Git is the store](decisions/0002-git-is-the-store.md)
- [Rules in CEL](decisions/0005-rules-in-cel.md)
- [Inference is for real thinking](decisions/0007-inference-for-real-thinking.md)
- [Measures are self-watches](decisions/0008-measures-are-self-watches.md)
- [Patterns, not features](decisions/0009-patterns-not-features.md)

## Known gaps

Two design questions are open and recorded in [open questions](project/open-questions.md). Rules are not enforced on commits made outside conky. Write throughput is limited by one signed commit per write. See [status](project/status.md).

## Not built yet

1. Tables stored as Parquet beside their page, with large data by pointer ([decision 0003](decisions/0003-data-beside-pages.md)).
2. Relief: something that acts on pressure.
3. Model-backed pages: a page that asks a question state cannot answer.
4. Rules that see a group of pages changed in one commit, and a pattern maker (accounting as a pattern, not a runtime feature).
5. The assimilation test: hand a fresh consumer only a stopped vault and score whether it resumes correctly.
6. The harness-neutral benchmark against other agent harnesses.
7. A core in Rust that runs without Git and in a browser ([decision 0012](decisions/0012-rust-core-planned.md)).

The full list, with identifiers, is the [roadmap](project/roadmap.md).
