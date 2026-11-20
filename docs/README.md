# Documentation

The documentation has three layers. Read down only as far as needed.

1. **The [README](../README.md)** is for anyone. It has no jargon and nothing technical.
2. **The guide** in `guide/` explains the ideas in plain language, then walks through the command line.
3. **The technical layer** is the reference in `reference/`, [design.md](design.md), the decision records in `decisions/` and the research in `research/`.

Each document below starts with frontmatter (`kind`, `title`, `status`, `date`, `source`). `scripts/check_docs.py` checks it and every link.

## Layer 2: the guide

- [guide/concepts.md](guide/concepts.md): Concepts
- [guide/getting-started.md](guide/getting-started.md): Getting started

## Layer 3: technical detail

### Reference

- [reference/vault-format.md](reference/vault-format.md): Vault format
- [reference/cli.md](reference/cli.md): Command line
- [reference/rules-and-reactions.md](reference/rules-and-reactions.md): Rules and reactions
- [reference/providers.md](reference/providers.md): Providers

### Design

- [design.md](design.md): the short technical overview

### Decisions

One record per decision, each with context, decision and consequences.

- [decisions/0001-objective.md](decisions/0001-objective.md): Objective
- [decisions/0002-git-is-the-store.md](decisions/0002-git-is-the-store.md): Git is the store
- [decisions/0003-data-beside-pages.md](decisions/0003-data-beside-pages.md): Data beside pages
- [decisions/0004-plain-vocabulary.md](decisions/0004-plain-vocabulary.md): Plain vocabulary
- [decisions/0005-rules-in-cel.md](decisions/0005-rules-in-cel.md): Rules in CEL
- [decisions/0006-size-is-a-rule.md](decisions/0006-size-is-a-rule.md): Size is a rule
- [decisions/0007-inference-for-real-thinking.md](decisions/0007-inference-for-real-thinking.md): Inference is for real thinking
- [decisions/0008-measures-are-self-watches.md](decisions/0008-measures-are-self-watches.md): Measures are self-watches
- [decisions/0009-patterns-not-features.md](decisions/0009-patterns-not-features.md): Patterns, not features
- [decisions/0010-no-debt-no-down-migrations.md](decisions/0010-no-debt-no-down-migrations.md): No debt, no down-migrations
- [decisions/0011-python-reference-implementation.md](decisions/0011-python-reference-implementation.md): Python reference implementation
- [decisions/0012-rust-core-planned.md](decisions/0012-rust-core-planned.md): Rust core planned
- [decisions/0013-evidence-not-scripts.md](decisions/0013-evidence-not-scripts.md): Evidence, not scripts
- [decisions/0014-benchmark-shape.md](decisions/0014-benchmark-shape.md): Benchmark shape
- [decisions/0015-ideas-climb-rungs.md](decisions/0015-ideas-climb-rungs.md): Ideas climb rungs
- [decisions/0016-docs-in-repo.md](decisions/0016-docs-in-repo.md): Docs live in the repository
- [decisions/0017-derived-data.md](decisions/0017-derived-data.md): Derived data sits on top, never underneath
- [decisions/0018-not-doing.md](decisions/0018-not-doing.md): What conky will not do
- [decisions/0019-providers-are-pages.md](decisions/0019-providers-are-pages.md): Providers are pages

### Research

Outside work, compared on a fixed basis, with the depth of reading stated.

- [research/dair-2026.md](research/dair-2026.md): DAIR.AI papers of the week, 2026: relevance index
- [research/harnesses.md](research/harnesses.md): Agent harnesses compared
- [research/papers.md](research/papers.md): Paper register
- [research/benchmarks.md](research/benchmarks.md): Benchmarks and evaluations for agent harnesses
- [research/evaluation-plan.md](research/evaluation-plan.md): Evaluation plan (draft): three kinds of result kept apart, and steps from cheapest first

## Beyond the layers

### Essays

Longer pieces that make the case for one idea each and stand alone.

- [essays/pressure-not-walls.md](essays/pressure-not-walls.md): Pressure, not walls
- [essays/rules-not-requests.md](essays/rules-not-requests.md): Rules, not requests
- [essays/the-log-is-the-truth.md](essays/the-log-is-the-truth.md): The log is the truth
- [essays/things-that-just-happen.md](essays/things-that-just-happen.md): Things that just happen

### Ideas

Candidates that are not yet requirements. Each states its rung.

- [ideas/a2ui.md](ideas/a2ui.md): A screen from the pages
- [ideas/approvals.md](ideas/approvals.md): Approvals as a pattern
- [ideas/arcs.md](ideas/arcs.md): Arcs
- [ideas/assimilation-test.md](ideas/assimilation-test.md): Assimilation test
- [ideas/auto-linking.md](ideas/auto-linking.md): Auto-linking
- [ideas/background-minds.md](ideas/background-minds.md): Background minds
- [ideas/cascading-context.md](ideas/cascading-context.md): Context that flows down
- [ideas/clock.md](ideas/clock.md): Time as an ordinary change
- [ideas/gatekeeper.md](ideas/gatekeeper.md): Permission that stays out of the way
- [ideas/direction-and-drift.md](ideas/direction-and-drift.md): Direction and drift
- [ideas/dry-run.md](ideas/dry-run.md): Trying a change first
- [ideas/energy-unit.md](ideas/energy-unit.md): Energy unit
- [ideas/inheritance.md](ideas/inheritance.md): What a space hands down
- [ideas/learned-reactions.md](ideas/learned-reactions.md): Learned reactions
- [ideas/ledger.md](ideas/ledger.md): Ledger
- [ideas/measures.md](ideas/measures.md): Measures
- [ideas/model-pages.md](ideas/model-pages.md): Pages that ask a model
- [ideas/obsidian-view.md](ideas/obsidian-view.md): Obsidian view
- [ideas/patterns.md](ideas/patterns.md): Patterns
- [ideas/rename.md](ideas/rename.md): Renaming without breaking anything
- [ideas/seeds-and-faces.md](ideas/seeds-and-faces.md): A seed, an identity and a face
- [ideas/staleness.md](ideas/staleness.md): Nothing goes stale
- [ideas/tables.md](ideas/tables.md): Tables
- [ideas/thought-to-change.md](ideas/thought-to-change.md): Thought to change
- [ideas/trace.md](ideas/trace.md): The history is the trace
- [ideas/vault-splitting.md](ideas/vault-splitting.md): Vault splitting

### Project

- [project/open-questions.md](project/open-questions.md): Open questions
- [project/roadmap.md](project/roadmap.md): Roadmap
- [project/status.md](project/status.md): Status
