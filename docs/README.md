# Documentation

Three layers. Read down only as far as you need.

1. **The [README](../README.md)** is for anyone, with no jargon.
2. **The guide** in `guide/` explains the ideas plainly, then walks through the command line.
3. **The technical layer** is the reference in `reference/`, [design.md](design.md), the decision records in `decisions/` and the research in `research/`.

Every document starts with frontmatter (`kind`, `title`, `status`, `date`, `source`). `scripts/check_docs.py` checks it and every link.

## Layer 2: the guide

- [guide/concepts.md](guide/concepts.md): Concepts
- [guide/getting-started.md](guide/getting-started.md): Getting started
- [guide/playing-a-program.md](guide/playing-a-program.md): Playing a program
- [guide/topology.md](guide/topology.md): Topology

## Layer 3: technical detail

### Reference

- [reference/vault-format.md](reference/vault-format.md): Vault format
- [reference/cli.md](reference/cli.md): Command line
- [reference/playbooks.md](reference/playbooks.md): Playbooks
- [reference/rules-and-reactions.md](reference/rules-and-reactions.md): Rules and reactions
- [reference/providers.md](reference/providers.md): Providers
- [reference/connectors.md](reference/connectors.md): Connectors
- [reference/vocabulary.md](reference/vocabulary.md): Vocabulary
- [reference/design.md](reference/design.md): Design: the tokens and rules every front-page figure is drawn from
- [reference/architecture.md](reference/architecture.md): Architecture index, generated from the code and the documents

### Design

- [design.md](design.md): the technical model in short

### Decisions

One record per decision: context, decision, consequences.

- [decisions/0001-objective.md](decisions/0001-objective.md): Objective
- [decisions/0002-git-is-the-store.md](decisions/0002-git-is-the-store.md): Git is the store
- [decisions/0003-data-beside-pages.md](decisions/0003-data-beside-pages.md): Data beside pages
- [decisions/0004-plain-vocabulary.md](decisions/0004-plain-vocabulary.md): Plain vocabulary
- [decisions/0005-rules-in-cel.md](decisions/0005-rules-in-cel.md): Rules in CEL
- [decisions/0006-size-is-a-rule.md](decisions/0006-size-is-a-rule.md): Size is a rule
- [decisions/0007-inference-for-real-thinking.md](decisions/0007-inference-for-real-thinking.md): Reflexes are free, so thought goes into character
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
- [decisions/0020-everything-is-somebody.md](decisions/0020-everything-is-somebody.md): Everything is somebody
- [decisions/0021-the-outside-arrives-as-pages.md](decisions/0021-the-outside-arrives-as-pages.md): The outside arrives as pages
- [decisions/0022-leaving-a-space-is-a-write-the-space-can-refuse.md](decisions/0022-leaving-a-space-is-a-write-the-space-can-refuse.md): Leaving a space is a write the space can refuse
- [decisions/0023-a-pattern-starts-private-and-rises-by-use.md](decisions/0023-a-pattern-starts-private-and-rises-by-use.md): A pattern starts private and rises by use
- [decisions/0024-a-model-is-reached-by-a-key-or-a-local-program.md](decisions/0024-a-model-is-reached-by-a-key-or-a-local-program.md): A model is reached by a key or by a program already on the machine
- [decisions/0025-the-screen-is-built-in-small-steps.md](decisions/0025-the-screen-is-built-in-small-steps.md): The people's screen is built in small steps, and the trail is the first trial
- [decisions/0026-it-always-works.md](decisions/0026-it-always-works.md): It always works
- [decisions/0027-the-vocabulary-is-what-exists.md](decisions/0027-the-vocabulary-is-what-exists.md): The vocabulary is what exists
- [decisions/0028-a-character-writes-pages.md](decisions/0028-a-character-writes-pages.md): A character writes pages
- [decisions/0029-autonomy-inside-limits-that-hold.md](decisions/0029-autonomy-inside-limits-that-hold.md): Autonomy inside limits that hold
- [decisions/0030-pay-once.md](decisions/0030-pay-once.md): Pay once
- [decisions/0031-build-on-bedrock.md](decisions/0031-build-on-bedrock.md): Build on bedrock
- [decisions/0032-results-publish-themselves.md](decisions/0032-results-publish-themselves.md): Results publish themselves
- [decisions/0033-ahead-or-different-with-each-step.md](decisions/0033-ahead-or-different-with-each-step.md): Ahead or different with each step
- [decisions/0034-a-rule-for-the-pages-within.md](decisions/0034-a-rule-for-the-pages-within.md): A rule for the pages within
- [decisions/0035-a-character-binds-its-own-space.md](decisions/0035-a-character-binds-its-own-space.md): A character binds its own space
- [decisions/0036-a-plain-rule-stays-with-its-page.md](decisions/0036-a-plain-rule-stays-with-its-page.md): A plain rule stays with its page
- [decisions/0037-a-watch-can-fire-on-a-relation.md](decisions/0037-a-watch-can-fire-on-a-relation.md): A watch can fire on a relation
- [decisions/0038-a-rule-is-proven-when-written.md](decisions/0038-a-rule-is-proven-when-written.md): A rule is proven when it is written
- [decisions/0039-an-event-can-be-noticed.md](decisions/0039-an-event-can-be-noticed.md): An event can be noticed
- [decisions/0040-the-runtime-narrates-and-pages-speak.md](decisions/0040-the-runtime-narrates-and-pages-speak.md): The runtime narrates and pages speak
- [decisions/0041-a-character-gives-its-space-reflexes.md](decisions/0041-a-character-gives-its-space-reflexes.md): A character gives its space reflexes
- [decisions/0042-a-space-shows-what-bears-first.md](decisions/0042-a-space-shows-what-bears-first.md): A space shows what bears first
- [decisions/0043-a-trial-is-drawn-as-it-happened.md](decisions/0043-a-trial-is-drawn-as-it-happened.md): A trial is drawn as it happened
- [decisions/0044-a-page-is-known-by-its-phrases.md](decisions/0044-a-page-is-known-by-its-phrases.md): A page is known by its phrases
- [decisions/0045-a-page-may-be-within-several-spaces.md](decisions/0045-a-page-may-be-within-several-spaces.md): A page may be within several spaces
- [decisions/0046-figures-are-drawn-from-the-shared-tokens.md](decisions/0046-figures-are-drawn-from-the-shared-tokens.md): Figures are drawn from the shared tokens
- [decisions/0047-a-character-is-shown-what-its-spaces-say.md](decisions/0047-a-character-is-shown-what-its-spaces-say.md): A character is shown what its spaces say
- [decisions/0048-charts-are-drawn-by-plotly-and-words-sit-in-markdown.md](decisions/0048-charts-are-drawn-by-plotly-and-words-sit-in-markdown.md): Charts are drawn by Plotly and words sit in Markdown
- [decisions/0049-a-cell-shows-the-whole-page.md](decisions/0049-a-cell-shows-the-whole-page.md): A cell shows the whole page, with sockets
- [decisions/0050-a-theatre-knows-itself.md](decisions/0050-a-theatre-knows-itself.md): A theatre knows itself
- [decisions/0051-the-theatre-is-a-page.md](decisions/0051-the-theatre-is-a-page.md): The theatre is a page, the outermost space
- [decisions/0052-wires-attach-to-port-boards-and-parents-broker-crossings.md](decisions/0052-wires-attach-to-port-boards-and-parents-broker-crossings.md): Wires attach to port boards, and a parent brokers what crosses its wall
- [decisions/0053-a-rule-sees-who-acts-and-a-name-cannot-be-borrowed.md](decisions/0053-a-rule-sees-who-acts-and-a-name-cannot-be-borrowed.md): A rule sees who acts, and a name cannot be borrowed
- [decisions/0054-a-letter-crosses-between-two-theatres-over-a-carrier.md](decisions/0054-a-letter-crosses-between-two-theatres-over-a-carrier.md): A letter crosses between two theatres, over a carrier that can be swapped
- [decisions/0055-a-letter-is-a-page-written-within-a-peer.md](decisions/0055-a-letter-is-a-page-written-within-a-peer.md): A letter is a page written within a peer, carried from an outbox that is derived data
- [decisions/0056-a-space-hands-down-reactions.md](decisions/0056-a-space-hands-down-reactions.md): A space hands down reactions: an `each` watch entry is a reflex every page within has
- [decisions/0057-charts-use-plotlys-built-in-themes-and-default-styles.md](decisions/0057-charts-use-plotlys-built-in-themes-and-default-styles.md): Charts use Plotly's built-in themes and default styles
- [decisions/0058-a-budget-the-runtime-holds.md](decisions/0058-a-budget-the-runtime-holds.md): A budget the runtime holds: asks counted from the history, a limit refusal past it, refilled by a write
- [decisions/0059-ports-are-bright-labelled-blocks-on-paired-boards.md](decisions/0059-ports-are-bright-labelled-blocks-on-paired-boards.md): Ports are bright labelled blocks on paired boards
- [decisions/0060-charts-take-the-minty-theme-with-monochrome-text.md](decisions/0060-charts-take-the-minty-theme-with-monochrome-text.md): Charts take the Minty theme with monochrome text
- [decisions/0061-figures-take-the-chart-themes-colours.md](decisions/0061-figures-take-the-chart-themes-colours.md): Figures take the chart theme's colours
- [decisions/0062-an-order-that-fails-says-so.md](decisions/0062-an-order-that-fails-says-so.md): An order that fails says so
- [decisions/0063-a-rule-says-why-in-its-own-words.md](decisions/0063-a-rule-says-why-in-its-own-words.md): A rule says why in its own words
- [decisions/0064-an-embed-inside-an-embed-is-followed.md](decisions/0064-an-embed-inside-an-embed-is-followed.md): An embed inside an embedded page is followed
- [decisions/0065-a-command-provider-page-names-its-model-and-effort.md](decisions/0065-a-command-provider-page-names-its-model-and-effort.md): A command provider page names its model and effort
- [decisions/0066-a-character-is-born-with-a-memory-and-a-sense-for-what-changed.md](decisions/0066-a-character-is-born-with-a-memory-and-a-sense-for-what-changed.md): A character is born with a memory and a sense for what changed

### Research

Outside work, compared on a fixed basis, with the depth of reading stated.

- [research/browser-drivers.md](research/browser-drivers.md): Browser drivers compared, and what they suggest for a web connector
- [research/dair-2026.md](research/dair-2026.md): DAIR.AI papers of the week, 2026: relevance index
- [research/harnesses.md](research/harnesses.md): Agent harnesses compared
- [research/findings-rubric.md](research/findings-rubric.md): What the research says a harness must do, and where Conky stands
- [research/gaps.md](research/gaps.md): What others have that Conky lacks: skip, covered or rethought
- [research/papers.md](research/papers.md): Paper register
- [research/discovery.md](research/discovery.md): How worlds could be found: discovery, registries and federation compared
- [research/observability.md](research/observability.md): Observability standards for an agent runtime
- [research/pkms.md](research/pkms.md): Personal and team knowledge tools compared on how they hold, link, serve and stream pages
- [research/protocols.md](research/protocols.md): Protocols for agents, tools and interfaces
- [research/streams-and-trees.md](research/streams-and-trees.md): Standards for trees, paths, patches and streams
- [research/anxiety-kernels.md](research/anxiety-kernels.md): Anxiety kernels: warnings that reach someone who will act
- [research/felt-sense-experiment.md](research/felt-sense-experiment.md): Felt-sense experiment: does placing a magnitude help a model
- [research/where-am-i.md](research/where-am-i.md): MARCO: a shared word for where an agent is
- [research/benchmarks.md](research/benchmarks.md): Benchmarks and evaluations for agent harnesses
- [research/evaluation-plan.md](research/evaluation-plan.md): Evaluation plan (draft): three kinds of result kept apart, and steps from cheapest first
- [research/results.md](research/results.md): Benchmark results, generated from the run files
- [research/trials.md](research/trials.md): Every trial card with its latest verdict and its drawn history, generated
- [research/benchmark-protocol.md](research/benchmark-protocol.md): Benchmark protocol (draft): the trail, fixed before any live run

## Beyond the layers

### Essays

One idea per essay, each able to stand alone.

- [essays/pressure-not-walls.md](essays/pressure-not-walls.md): Pressure, not walls
- [essays/rules-not-requests.md](essays/rules-not-requests.md): Rules, not requests
- [essays/the-log-is-the-truth.md](essays/the-log-is-the-truth.md): The log is the truth
- [essays/things-that-just-happen.md](essays/things-that-just-happen.md): Things that just happen

### Ideas

Candidates, not requirements. Each states its rung.

- [ideas/a2ui.md](ideas/a2ui.md): A screen from the pages
- [ideas/approvals.md](ideas/approvals.md): Approvals as a pattern
- [ideas/arcs.md](ideas/arcs.md): Arcs
- [ideas/assimilation-test.md](ideas/assimilation-test.md): Assimilation test
- [ideas/auto-linking.md](ideas/auto-linking.md): Auto-linking
- [ideas/attention.md](ideas/attention.md): Attention: who hears what, and at which layer
- [ideas/faculties.md](ideas/faculties.md): Faculties
- [ideas/standing.md](ideas/standing.md): Standing
- [ideas/background-minds.md](ideas/background-minds.md): Background minds
- [ideas/character.md](ideas/character.md): A page with a self
- [ideas/cascading-context.md](ideas/cascading-context.md): Context that flows down
- [ideas/clock.md](ideas/clock.md): Time as an ordinary change
- [ideas/compositor.md](ideas/compositor.md): The compositor: a screen that is asked for once
- [ideas/a-minds-desktop.md](ideas/a-minds-desktop.md): A mind's desktop
- [ideas/connectors.md](ideas/connectors.md): Connectors: every protocol is a door, not a room
- [ideas/gatekeeper.md](ideas/gatekeeper.md): Permission that stays out of the way
- [ideas/habit.md](ideas/habit.md): A habit: what recurs is thought about once
- [ideas/direction-and-drift.md](ideas/direction-and-drift.md): Direction and drift
- [ideas/dry-run.md](ideas/dry-run.md): Trying a change first
- [ideas/energy-unit.md](ideas/energy-unit.md): Energy unit
- [ideas/felt-sense.md](ideas/felt-sense.md): A felt sense of magnitude
- [ideas/house-style.md](ideas/house-style.md): Taste is a page
- [ideas/inheritance.md](ideas/inheritance.md): What a space hands down
- [ideas/keys.md](ideas/keys.md): Keys that change hands
- [ideas/learned-reactions.md](ideas/learned-reactions.md): Learned reactions
- [ideas/ledger.md](ideas/ledger.md): Ledger
- [ideas/looks.md](ideas/looks.md): A look: a kind's page says how its pages are drawn
- [ideas/the-page-as-it-was.md](ideas/the-page-as-it-was.md): A rule sees the page as it was
- [ideas/said-beside.md](ideas/said-beside.md): What is happening can be watched
- [ideas/architecture-as-pages.md](ideas/architecture-as-pages.md): The architecture as pages
- [ideas/codec.md](ideas/codec.md): A codec: one tree into another, written once and applied by reflex
- [ideas/measures.md](ideas/measures.md): Measures
- [ideas/model-pages.md](ideas/model-pages.md): Pages that ask a model
- [ideas/model-choice.md](ideas/model-choice.md): Which model answers is a page
- [ideas/obsidian-view.md](ideas/obsidian-view.md): Obsidian view
- [ideas/outside-reading.md](ideas/outside-reading.md): Reading the field
- [ideas/patterns.md](ideas/patterns.md): Patterns
- [ideas/provenance.md](ideas/provenance.md): Where a value came from
- [ideas/rename.md](ideas/rename.md): Renaming without breaking anything
- [ideas/reviewer.md](ideas/reviewer.md): A page that reviews
- [ideas/seeds-and-faces.md](ideas/seeds-and-faces.md): A seed, an identity and a face
- [ideas/staleness.md](ideas/staleness.md): Nothing goes stale
- [ideas/streaming.md](ideas/streaming.md): Text as it arrives
- [ideas/stepping.md](ideas/stepping.md): One step at a time
- [ideas/tables.md](ideas/tables.md): Tables
- [ideas/thought-to-change.md](ideas/thought-to-change.md): Thought to change
- [ideas/tools.md](ideas/tools.md): The outside arrives as pages
- [ideas/trace.md](ideas/trace.md): The history is the trace
- [ideas/vault-splitting.md](ideas/vault-splitting.md): Vault splitting
- [ideas/writers.md](ideas/writers.md): Several writers at once

### Project

- [project/open-questions.md](project/open-questions.md): Open questions
- [project/roadmap.md](project/roadmap.md): Roadmap
- [project/seams.md](project/seams.md): Seams: where each missing capability would land
- [project/status.md](project/status.md): Status
