---
kind: project
title: Roadmap
status: current
date: 2026-11-20
source: architect
---

# Roadmap

Ordered steps, each with a stable id and a state: `done`, `next` or `later`. Exactly one step is `next`; `scripts/check_docs.py` checks it. Steps are unbuilt unless `done`; see [status](status.md) for what exists. This page is the single tracker for work.

- R1 (next): Tables as Parquet beside their page, with large data by pointer. Idea: [tables](../ideas/tables.md). Decisions: [0009](../decisions/0009-no-debt-no-down-migrations.md), [0022](../decisions/0022-data-beside-pages.md).
- R2 (done): First slice of measures as self-watches, with pressure as the first use. Idea: [measures](../ideas/measures.md). Decision: [0019](../decisions/0019-measures-are-self-watches.md). Related: [0006](../decisions/0006-size-is-a-rule.md).
- R3 (later): Relief: something that acts on pressure (split or summarise a crowded page). Essay: [pressure-not-walls](../essays/pressure-not-walls.md).
- R4 (later): Model-backed pages: a page that asks a question state cannot answer. Decision: [0008](../decisions/0008-inference-for-real-thinking.md). Idea: [learned-reactions](../ideas/learned-reactions.md).
- R5 (later): Rules that see a group of pages changed in one commit. Several pages changed together are already one commit; what is unbuilt is rules that evaluate the whole group. Idea: [patterns](../ideas/patterns.md). Decision: [0021](../decisions/0021-git-is-the-store.md).
- R6 (later): A pattern maker that turns goldens into patterns, with double-entry accounts as the first thing it is asked to produce. Idea: [patterns](../ideas/patterns.md). Decision: [0018](../decisions/0018-patterns-not-features.md).
- R7 (later): The assimilation test. Idea: [assimilation-test](../ideas/assimilation-test.md). Decision: [0011](../decisions/0011-benchmark-shape.md).
- R8 (later): The harness-neutral benchmark against other agent harnesses. Decisions: [0010](../decisions/0010-evidence-not-scripts.md), [0011](../decisions/0011-benchmark-shape.md).
- R9 (later): Fold further ideas one mechanism at a time, by the rungs in [0012](../decisions/0012-archive-and-rungs.md).
- R10 (later): Vault splitting: a space becomes its own vault when a vault grows too large or too busy. Idea: [vault-splitting](../ideas/vault-splitting.md). Decision: [0021](../decisions/0021-git-is-the-store.md).
- R11 (later): A generated view for people: an index of pages, a workspace over several vaults, openable in a notes application. Idea: [obsidian-view](../ideas/obsidian-view.md).
