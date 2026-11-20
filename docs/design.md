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

## Asking a model

A model is reached through a provider page, and a question is asked by a watch entry. The answer is an ordinary signed write by the asking page, so the history holds the question, the model and the answer, and reading it needs no model. The secret for a provider is looked up by name outside the vault. The detail is in [providers](reference/providers.md) and [decision 0019](decisions/0019-providers-are-pages.md). Only stand-in servers have been used to test it.

## Derived data

Anything built to make a vault faster or nicer to use is derived data: indexes, caches, snapshots and generated views. It is optional, lives outside the history in a directory that Git ignores, and can be rebuilt from the vault alone. It can be deleted at any time without losing anything, and nothing reads it as the truth ([decision 0017](decisions/0017-derived-data.md)).

## The parts

- **Pages and the vault format.** Layout, commit conventions and trailers, signing and identity, and what `verify` checks: [vault format](reference/vault-format.md).
- **Rules, reactions and measures.** The expression language, variables in scope, inheritance through spaces, refusal reasons, the reaction depth limit, and measures built from self-watches: [rules and reactions](reference/rules-and-reactions.md).
- **Providers.** The page that says how to reach a model, the two wire formats and where secrets live: [providers](reference/providers.md).
- **The command line.** Each command, its options, exit codes and error behaviour: [command line](reference/cli.md).

## Decisions

Each choice has a record in [decisions](decisions/). Those that shape the whole design:

- [Git is the store](decisions/0002-git-is-the-store.md)
- [Rules in CEL](decisions/0005-rules-in-cel.md)
- [Inference is for real thinking](decisions/0007-inference-for-real-thinking.md)
- [Providers are pages](decisions/0019-providers-are-pages.md)
- [Measures are self-watches](decisions/0008-measures-are-self-watches.md)
- [Patterns, not features](decisions/0009-patterns-not-features.md)

## Known gaps

Two design questions are open and recorded in [open questions](project/open-questions.md). Rules are not enforced on commits made outside conky. Write throughput is limited by one signed commit per write. See [status](project/status.md).

## Not built yet

In roadmap order:

1. The clock: time as an ordinary write.
2. Staleness and relief: something that acts on pressure from size or age.
3. Dry run, approvals as a pattern, rename with link repair, and cascading context.
4. Background minds, and direction and drift.
5. Tables stored as Parquet beside their page, with large data by pointer ([decision 0003](decisions/0003-data-beside-pages.md)).
6. The pattern maker, and rules that see several pages changed in one commit.
7. Trace summaries and a view for people, as derived data.
8. The resume test and the harness-neutral benchmark.
9. Vault splitting.
10. A core in Rust that runs without Git and in a browser ([decision 0012](decisions/0012-rust-core-planned.md)).

The full list, with identifiers, is the [roadmap](project/roadmap.md).
