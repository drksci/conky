---
kind: design
title: Design
status: current
date: 2026-11-20
source: maintainers
---
# Design

The technical model in short. The index of everything is the [architecture index](reference/architecture.md), generated from the code and the documents. The detail is in the reference pages and the decision records. For the ideas in plain language, start with [concepts](guide/concepts.md).

## The model

Everything in a vault is somebody: a page is a character with an identity, a temperament and a voice, not a record with fields. Signed history, rules and reactions are the body, reflexes a creature never thinks about, so characters can be lively without being dangerous. Reflexes are free, so thought goes into character ([decision 0020](decisions/0020-everything-is-somebody.md), [a page with a self](ideas/character.md)). Today a page can ask a model. Nothing yet gives a page a generated temperament or voice.

A vault is a plain Git repository. Its pages are Markdown files under `pages/` and its history is the authority: every change is one signed commit, and a refused write is recorded as an empty signed commit. What is not in the history did not happen.

conky keeps no log, hash chain or key format of its own. Git already gives tamper-evident history, signed commits, exact restore, transport by clone, push or bundle, and atomic multi-file changes. conky adds rules, reactions, measures and a few conventions ([decision 0002](decisions/0002-git-is-the-store.md)).

An event is a commit. A seal is its signature. The vault holds public keys only; private keys live in a separate directory. A reader given only the vault can verify and read it with nothing but Git.

## Asking a model

A model is reached through a provider page, and a watch entry asks the question. The answer is an ordinary signed write by the asking page, so the history holds the question, the model and the answer, and reading it needs no model. A provider's secret is looked up by name outside the vault. See [providers](reference/providers.md) and [decision 0019](decisions/0019-providers-are-pages.md). Only stand-in servers have tested it.

## Derived data

Anything built to make a vault faster or nicer to use is derived data: indexes, caches, snapshots and generated views. It is optional, lives outside the history in a directory Git ignores, and can be rebuilt from the vault alone. Deleting it loses nothing, and nothing reads it as the truth ([decision 0017](decisions/0017-derived-data.md)).

## The whole design in one table

Conky has five parts: page, space, rule, watch and key. Nearly everything proposed for it is those five plus eight general capabilities. The state column says what exists, as recorded in [status](project/status.md).

| # | Capability | State |
|---|---|---|
| 1 | Spaces hand down rules, context and reactions, and a page may join several spaces | Rules, context, reactions with `set` and several spaces are built. Asks handed down are not. |
| 2 | Time as an ordinary change: a clock page | Not built. |
| 3 | Several pages changed in one commit, with rules that can see the whole group | Not built. |
| 4 | Rules that can see who signed a change and how it arose | Not built. |
| 5 | Trying a change on a throwaway branch | Not built. |
| 6 | Pages that ask a model, with a budget | Asking is built. The budget is not built. |
| 7 | Tables beside a page | Not built. |
| 8 | Derived data: indexes, summaries and views that can be deleted | The rule is recorded. None is built. |

Outside the eight is how two vaults relate, which is an open question.

1. **Handing down.** A space hands down its rules, its context and its `set` reactions, and a page may join several spaces. Asks handed down wait for budgets. A pattern is then a space, and permission and identity ride on the same chain. See [what a space hands down](ideas/inheritance.md), [permission that stays out of the way](ideas/gatekeeper.md) and [a seed, an identity and a face](ideas/seeds-and-faces.md).
2. **Time.** There is no hidden timer. Time passes when a clock page is written, and anything that depends on time watches that page. See [the clock](ideas/clock.md) and [staleness](ideas/staleness.md).
3. **Groups.** Git can commit several files together, but a write changes one page per commit today. A write that changes several pages, and a rule over the whole group, which a ledger-like pattern needs, are not built. See [patterns](ideas/patterns.md).
4. **Who signed.** A rule should be able to see who signed a change and what caused it, so approvals and permission need no new mechanism. See [approvals](ideas/approvals.md).
5. **Trying first.** A change is applied on a throwaway branch, the consequences are reported and the branch is discarded. See [dry run](ideas/dry-run.md).
6. **Asking a model.** A page can ask a model and write the answer as an ordinary signed change. Asking is built and tested against stand-in servers. An entry that names a space with `writes` can take an answer that is pages, each an ordinary write by the asking page inside that space ([an answer that is pages](reference/rules-and-reactions.md#an-answer-that-is-pages)). A declared budget that stops spending is not built. Asking is how a page thinks, and budgets bound the cost, not avoidance of the model: reflexes are free, so thought goes into character ([decision 0020](decisions/0020-everything-is-somebody.md), [a page with a self](ideas/character.md)). See [pages that ask a model](ideas/model-pages.md) and [background minds](ideas/background-minds.md).
7. **Tables.** Tabular data sits as Parquet beside its page, so it travels with the vault. See [tables](ideas/tables.md).
8. **Derived data.** Indexes, summaries and views are optional, live outside the history and can be deleted ([decision 0017](decisions/0017-derived-data.md)). Nothing is built. See [the history is the trace](ideas/trace.md), [the people's view](ideas/obsidian-view.md) and [a screen from the pages](ideas/a2ui.md). Connectors for outside protocols and the composed screen belong here too: see [connectors](ideas/connectors.md) and [the compositor](ideas/compositor.md).

## The parts

- **Pages and the vault format.** Layout, commit conventions and trailers, signing and identity, and what `verify` checks: [vault format](reference/vault-format.md).
- **Rules, reactions and measures.** The expression language, variables in scope, the `each` rules spaces hand down, refusal reasons, the reaction depth limit and measures built from self-watches: [rules and reactions](reference/rules-and-reactions.md).
- **Providers.** How a page reaches a model, the two wire formats and where secrets live: [providers](reference/providers.md).
- **The command line.** Each command, its options, exit codes and errors: [command line](reference/cli.md).

## Decisions

Each choice has a record in [decisions](decisions/). These shape the whole design:

- [Git is the store](decisions/0002-git-is-the-store.md)
- [Rules in CEL](decisions/0005-rules-in-cel.md)
- [Reflexes are free, so thought goes into character](decisions/0007-inference-for-real-thinking.md)
- [Everything is somebody](decisions/0020-everything-is-somebody.md)
- [Providers are pages](decisions/0019-providers-are-pages.md)
- [Measures are self-watches](decisions/0008-measures-are-self-watches.md)
- [Patterns, not features](decisions/0009-patterns-not-features.md)

## Known gaps

Two design questions are open, in [open questions](project/open-questions.md). Rules are not enforced on commits made outside conky. Write throughput is limited by one signed commit per write. See [status](project/status.md).

## Not built yet

In roadmap order:

1. Seeds, faces and a self for every page.
2. The clock, then budgets for model pages and the first background mind, then staleness and relief.
3. Several pages in one commit, with rules that see the group.
4. Rules that see who signed, with approvals and the gatekeeper.
5. Dry run.
6. Rename with link repair, then tables stored as Parquet beside their page ([decision 0003](decisions/0003-data-beside-pages.md)).
7. Derived data: trace summaries, the people's view and the A2UI screen.
8. The pattern maker, then direction and drift.
9. The model-backed resume test and the harness-neutral benchmark.
10. A core in Rust that runs without Git and in a browser ([decision 0012](decisions/0012-rust-core-planned.md)).
11. How two vaults relate, after a vault is split.

The full list, with identifiers, is the [roadmap](project/roadmap.md).
