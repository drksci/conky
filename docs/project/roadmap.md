---
kind: project
title: Roadmap
status: current
date: 2026-11-20
source: architect
---

# Roadmap

Ordered next steps. Each is unbuilt unless marked done; see [status](status.md) for what exists.

1. Tables as Parquet beside their page, with large data by pointer. Idea: [tables](../ideas/tables.md). Decisions: [0009](../decisions/0009-no-debt-no-down-migrations.md), [0022](../decisions/0022-data-beside-pages.md).
2. Done, first slice: measures as self-watches, with pressure as the first use. Idea: [measures](../ideas/measures.md). Decision: [0019](../decisions/0019-measures-are-self-watches.md). Related: [0006](../decisions/0006-size-is-a-rule.md).
3. Relief: something that acts on pressure (split or summarise a crowded page). Essay: [pressure-not-walls](../essays/pressure-not-walls.md).
4. Model-backed pages: a page that asks a question state cannot answer. Decision: [0008](../decisions/0008-inference-for-real-thinking.md). Idea: [learned-reactions](../ideas/learned-reactions.md).
5. Rules that see a group of pages changed in one commit. Several pages changed together are already one commit; what is unbuilt is rules that evaluate the whole group. Idea: [patterns](../ideas/patterns.md). Decision: [0021](../decisions/0021-git-is-the-store.md).
6. A pattern maker that turns goldens into patterns, with double-entry accounts as the first thing it is asked to produce. Idea: [patterns](../ideas/patterns.md). Decision: [0018](../decisions/0018-patterns-not-features.md).
7. The assimilation test. Idea: [assimilation-test](../ideas/assimilation-test.md). Decision: [0011](../decisions/0011-benchmark-shape.md).
8. The harness-neutral benchmark against other agent harnesses. Decisions: [0010](../decisions/0010-evidence-not-scripts.md), [0011](../decisions/0011-benchmark-shape.md).
9. Fold further ideas one mechanism at a time, by the rungs in [0012](../decisions/0012-archive-and-rungs.md).
