---
kind: project
title: Roadmap
status: current
date: 2026-11-20
source: maintainers
---

# Roadmap

Steps are listed in order, first to last; ids are stable labels, not positions. Each with a stable id and a state: `done`, `next` or `later`. Exactly one step is `next`; `scripts/check_docs.py` checks it. Steps are unbuilt unless `done`; see [status](status.md) for what exists. This page is the single tracker for work.

- R12 (next): The clock: time passes as an ordinary write to a clock page. Idea: [clock](../ideas/clock.md).
- R3 (later): Staleness and relief: something that acts on pressure from size or age (split, summarise or archive). Ideas: [staleness](../ideas/staleness.md), [measures](../ideas/measures.md). Essay: [pressure-not-walls](../essays/pressure-not-walls.md).
- R13 (later): Dry run: ask what a change would do on a throwaway branch of the history. Idea: [dry-run](../ideas/dry-run.md). Decision: [0002](../decisions/0002-git-is-the-store.md).
- R14 (later): Approvals as a pattern, with rules that can see who signed a change. Idea: [approvals](../ideas/approvals.md). Decision: [0009](../decisions/0009-patterns-not-features.md).
- R15 (later): Rename with link repair: one change that also rewrites every link and embed. Idea: [rename](../ideas/rename.md).
- R16 (later): Cascading context: a page sees the shared facts of the spaces above it. Idea: [cascading-context](../ideas/cascading-context.md).
- R17 (later): Background minds: budgeted model pages that doubt, wonder, tidy and orient. Idea: [background-minds](../ideas/background-minds.md). Depends on R4 and R12.
- R18 (later): Direction and drift: read a page's activity against a goal page. Idea: [direction-and-drift](../ideas/direction-and-drift.md). Related: [arcs](../ideas/arcs.md).
- R1 (later): Tables as Parquet beside their page, with large data by pointer. Idea: [tables](../ideas/tables.md). Decisions: [0010](../decisions/0010-no-debt-no-down-migrations.md), [0003](../decisions/0003-data-beside-pages.md).
- R6 (later): The pattern maker, which turns goldens into patterns (double-entry accounts as the first thing it is asked to produce), and rules over several pages changed together in one commit. Several pages changed together are already one commit; what is unbuilt is rules that evaluate the whole group. Idea: [patterns](../ideas/patterns.md). Decisions: [0009](../decisions/0009-patterns-not-features.md), [0002](../decisions/0002-git-is-the-store.md).
- R11 (later): Trace summaries and the view for people, as derived data: summaries per page and period, links from a fact to the change that set it, and a generated index openable in a notes application. Ideas: [trace](../ideas/trace.md), [obsidian-view](../ideas/obsidian-view.md). Decision: [0017](../decisions/0017-derived-data.md).
- R7 (later): The resume test with a model, scoring behavioural continuity apart from state continuity. The mechanical form is done as R21. Idea: [assimilation-test](../ideas/assimilation-test.md). Decision: [0014](../decisions/0014-benchmark-shape.md).
- R8 (later): The harness-neutral benchmark against other agent harnesses. Decisions: [0013](../decisions/0013-evidence-not-scripts.md), [0014](../decisions/0014-benchmark-shape.md).
- R10 (later): Vault splitting: a space becomes its own vault when a vault grows too large or too busy. Idea: [vault-splitting](../ideas/vault-splitting.md). Decision: [0002](../decisions/0002-git-is-the-store.md).
- R19 (later): The Rust core and the browser. Decision: [0012](../decisions/0012-rust-core-planned.md).
- R2 (done): First slice of measures as self-watches, with pressure as the first use. Idea: [measures](../ideas/measures.md). Decision: [0008](../decisions/0008-measures-are-self-watches.md). Related: [0006](../decisions/0006-size-is-a-rule.md).
- R4 (done): Model pages and provider pages: a page that asks a question state cannot answer, with the provider named by a page. Tested against stand-in servers, not a live provider. Idea: [model-pages](../ideas/model-pages.md). Decisions: [0007](../decisions/0007-inference-for-real-thinking.md), [0019](../decisions/0019-providers-are-pages.md). Related: [learned-reactions](../ideas/learned-reactions.md).
- R20 (done): `conky demo`, a narrated example vault built with the real write path. See [status](status.md).
- R21 (done): `conky assimilate`, the mechanical form of the resume test: take over a stopped vault from its folder, check it and carry on, with no model. Idea: [assimilation-test](../ideas/assimilation-test.md). See [status](status.md).
