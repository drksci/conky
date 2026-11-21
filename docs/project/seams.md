---
kind: project
title: Seams
status: current
date: 2026-11-20
source: "research/harnesses.md, research/gaps.md, research/findings-rubric.md, research/observability.md, research/streams-and-trees.md, the roadmap, the architecture index and the code under src/conky/"
---

# Seams

A seam is the place a missing capability would land: the parts it composes from, the law or decision that constrains it, and the idea, roadmap step and architecture row that hold its place now. This page lists the capabilities worth placing before they are built, so that none of them later forces a rewrite of what already works. Nothing on this page is built unless it says so. Each idea named here is at the rung `idea` unless the [architecture index](../reference/architecture.md) shows otherwise.

An entry earns its place only if ignoring it could cost a refactor or miss a difference. The harnesses are those compared in [harnesses.md](../research/harnesses.md). Where the comparison is silent, the entry says "not recorded in the comparison". Where the present design already has the seam, the entry says so and asks for nothing more.

## All entries

| # | Entry | Standing | Seam today |
|---|---|---|---|
| 1 | Files, images and sound as input | optional | partly: `data.file` placed, the ask cannot carry it |
| 2 | Codecs between trees | core | exists |
| 3 | Spending bounds | core | placed, strains the record |
| 4 | Context built for each call | core | placed, strains the request |
| 5 | Which model answers | optional | new idea |
| 6 | A page that reviews | optional | new idea |
| 7 | Where a value came from | core | new idea |
| 8 | Keys that change hands | core | new idea, strains `verify` |
| 9 | A page in several spaces | core | placed (R22, `next`), strains the page format |
| 10 | Several pages in one commit | core | placed (R24), strains the write path |
| 11 | Patterns and worked examples | core | exists |
| 12 | The clock and background minds | core | exists |
| 13 | Reactions that survive a crash | core | placed in stepping, strains reactions |
| 14 | Tables, files and streams beside a page | core | placed (R1), strains `verify` |
| 15 | Traces in standard names | optional | placed in trace, strains the trailers |
| 16 | Approvals and holding a vault | core | exists |
| 17 | The screen | optional | exists, one choice open |
| 18 | Text as it arrives | optional | new idea |
| 19 | Tool servers and protocols | optional | exists |
| 20 | Reading the field | optional | new idea |
| 21 | Several writers at once | core | new idea |
| 22 | Throughput and size | core | placed (R10, R11), strains reactions |
| 23 | A core without Git | optional | exists |
| 24 | Resume, benchmark and repeated runs | core | exists |
| 25 | A second backend, a runtime planner, hosting | out of scope | none wanted |
| 26 | Standing | core | new idea, strains the members list |
| 27 | Being told | core | built as the `refusal` relation, with the `event` map in watch scope |
| 28 | Faculties | optional | new idea |

Core means the design's claims depend on it. Optional means a vault works fully without it and gains when it is there. Out of scope means it is left out on purpose.

## Perception and codecs

### 1. Files, images and sound as input

- **What.** A connector that captures a picture or a sound, and an ask that shows it to a model.
- **Why.** The MCP tool result carries image and audio blocks ([streams and trees](../research/streams-and-trees.md)). Which compared harnesses accept images is not recorded in the comparison.
- **Seam.** A file kept beside its page and named by a content hash ([`data.file`](../reference/architecture.md#data.file)), written by a connector like the screen text, embedded in a prompt like any page. Constrained by [`law.provider.page`](../reference/architecture.md#law.provider.page) and [decision 0030](../decisions/0030-pay-once.md).
- **Placeholder.** [Tables](../ideas/tables.md), roadmap R1, row [`data.file`](../reference/architecture.md#data.file).
- **Refactor risk.** `model._request` sends one user message whose content is a string, and `model.moment_key` hashes the prompt string. A file in a prompt needs content blocks in the request and the file's hash in the cache key. Both are local changes if made before a second wire format is added.
- **Standing.** Optional.

### 2. Codecs between trees

- **What.** Bindings from one tree to another (a screen to fields, pages to a screen), written once by thought and applied by reflex.
- **Why.** F6 and F29 in the [findings rubric](../research/findings-rubric.md) say small calls and little re-read context pay. Not recorded in the comparison.
- **Seam.** Exists. [`kind.codec`](../reference/architecture.md#kind.codec), with the text functions already in the rule language. The [standards research](../research/streams-and-trees.md) settles addresses (JSON Pointer) and change forms (JSON Patch).
- **Placeholder.** [Codec](../ideas/codec.md), R11g.
- **Refactor risk.** None found. A codec that edits a tree is code or a registered function, never an impure rule ([`law.rule.pure`](../reference/architecture.md#law.rule.pure)).
- **Standing.** Core.

## Thought and economy

### 3. Spending bounds

- **What.** A budget a page or a space declares, metered from recorded tokens, that stops spending when it is used.
- **Why.** The Claude Agent SDK ships `max_turns` and `max_budget_usd`, and the OpenAI Agents SDK raises an error at `max_turns` ([harnesses](../research/harnesses.md)). F28 asks for cost bounded from metered tokens.
- **Seam.** A measure that adds the `Tokens-In` and `Tokens-Out` of each answer into a field, and a rule that refuses an ask past the budget. Conserved down a space by [`law.spend.conserve`](../reference/architecture.md#law.spend.conserve) and metered by [`law.spend.meter`](../reference/architecture.md#law.spend.meter).
- **Placeholder.** [Background minds](../ideas/background-minds.md), R17, row [`kind.mind`](../reference/architecture.md#kind.mind).
- **Refactor risk.** Token counts are written only when a provider reports them, and the command shape reports none, so a budget over trailers alone undercounts. The meter needs a stated fallback count. The only cap today is `MAX_DEPTH` in `vault.py`; a budget refusal is a new refusal reason beside `cycle`, not a change to it.
- **Standing.** Core.

### 4. Context built for each call

- **What.** Each call made from a small, stable context: a fixed part first, then the page, then what just happened, with more pulled on demand and named in `Read`.
- **Why.** F6 (one action per context matched full history), F29 (reading context was up to 73% of cost) and F7 (longer visible history lowered cooperation).
- **Seam.** Embeds, the `Read` trailer and the members list already exist. The planned stage is [`stage.think.context`](../reference/architecture.md#stage.think.context).
- **Placeholder.** [Pages that ask a model](../ideas/model-pages.md), R17.
- **Refactor risk.** `model._request` builds `messages` as one user turn from one string. A fixed prefix that a provider can cache needs the prompt to have parts (fixed, page, moment) all the way from `Vault._ask` to the request, and the cache key to hash the parts. Deciding the parts once, before more wire formats, avoids doing it twice.
- **Standing.** Core.

### 5. Which model answers

- **What.** A page that orders the providers a space may use, cheapest first, with the recorded outcome that moves a question up.
- **Why.** F25, F26 and F27 (cheap deciders fail without calibration, one handoff pays, routers on task text do not). Not recorded in the comparison.
- **Seam.** Provider pages, the detection order of [decision 0024](../decisions/0024-a-model-is-reached-by-a-key-or-a-local-program.md), the ladder in [habit](../ideas/habit.md), context handed down (R22).
- **Placeholder.** [Which model answers is a page](../ideas/model-choice.md), row [`kind.router`](../reference/architecture.md#kind.router). No roadmap step yet.
- **Refactor risk.** `model.detect` returns a fixed order. If the order stays in code, a page cannot change it. The router should read the same `Choice` list rather than add a second path.
- **Standing.** Optional.

### 6. A page that reviews

- **What.** A model page that writes a signed verdict on a proposed change, which a rule counts.
- **Why.** CrewAI and the OpenAI Agents SDK let a guardrail call a model ([harnesses](../research/harnesses.md)). F15, F17 and F22 favour an independent reviewer that can itself change. [Gaps](../research/gaps.md) records that no idea page covered it.
- **Seam.** [Approvals](../ideas/approvals.md) and [`part.seal.signer`](../reference/architecture.md#part.seal.signer). Rules stay pure ([decision 0005](../decisions/0005-rules-in-cel.md)).
- **Placeholder.** [A page that reviews](../ideas/reviewer.md), row [`kind.reviewer`](../reference/architecture.md#kind.reviewer). It waits on R14 and R17.
- **Refactor risk.** None beyond R14's, listed below.
- **Standing.** Optional.

## Constraints and trust

### 7. Where a value came from

- **What.** A rule that can see whether what it judges came from a person, a character, a model or a connector, and what a model read.
- **Why.** F18, F19 and F20 (planted text in memory, payloads copied into self-written skills), ranked sixth of the gaps in the findings rubric with no step. [Status](status.md) records that a model's answer is stored with nothing marking it as unchecked.
- **Seam.** Trailers already hold signer, `Kind`, `Model` and `Read`. The rule receives the origin as data, so [`law.rule.pure`](../reference/architecture.md#law.rule.pure) holds.
- **Placeholder.** [Where a value came from](../ideas/provenance.md), row [`part.rule.origin`](../reference/architecture.md#part.rule.origin). No step yet.
- **Refactor risk.** It shares a scope change with R14. Build both on one decision, listed below.
- **Standing.** Core: [habit](../ideas/habit.md) and self-written rules are unsafe without it.

### 8. Keys that change hands

- **What.** Retiring and revoking a signer as recorded events.
- **Why.** An open question in [open questions](open-questions.md). Not recorded in the comparison.
- **Seam.** `keys/allowed_signers` is already committed, so a change to it is an ordinary event. [`law.vault.travel`](../reference/architecture.md#law.vault.travel) forbids a key server.
- **Placeholder.** [Keys that change hands](../ideas/keys.md), row [`part.key.rotate`](../reference/architecture.md#part.key.rotate). No step yet.
- **Refactor risk.** `Vault.verify` asks Git for `%G?` against the signers file in the working tree, so every past event is judged by today's signers. Removing a line breaks the history behind it.
- **Standing.** Core.

## Spaces and patterns

### 9. A page in several spaces

- **What.** A page within more than one space, taking rules, context and reactions from each.
- **Why.** A pattern lies over existing pages by membership ([patterns](../ideas/patterns.md)). Not recorded in the comparison.
- **Seam.** [`part.space.context`](../reference/architecture.md#part.space.context) and [`law.rule.tighten`](../reference/architecture.md#law.rule.tighten). Constrained by [decision 0022](../decisions/0022-leaving-a-space-is-a-write-the-space-can-refuse.md).
- **Placeholder.** [What a space hands down](../ideas/inheritance.md), R22 (`next`). Several spaces are built ([decision 0045](../decisions/0045-a-page-may-be-within-several-spaces.md)); reactions handed down are not.
- **Refactor risk.** The most serious on this page; see the first item below.
- **Standing.** Core.

### 10. Several pages in one commit

- **What.** One write that changes several pages, with rules that see the whole group.
- **Why.** A ledger-like pattern needs it ([design](../design.md), capability 3). Not recorded in the comparison.
- **Seam.** Git commits several files at once ([decision 0002](../decisions/0002-git-is-the-store.md)). [`part.write.group`](../reference/architecture.md#part.write.group).
- **Placeholder.** [Patterns](../ideas/patterns.md), R24.
- **Refactor risk.** See the second item below.
- **Standing.** Core.

### 11. Patterns and worked examples

- **What.** Domain forms (accounts, stock, checklists) made on demand from worked examples, kept as spaces, rising by use.
- **Why.** [Decision 0009](../decisions/0009-patterns-not-features.md) and [decision 0023](../decisions/0023-a-pattern-starts-private-and-rises-by-use.md).
- **Seam.** Exists: [`kind.pattern`](../reference/architecture.md#kind.pattern), [`kind.shelf`](../reference/architecture.md#kind.shelf) and [`part.pattern.make`](../reference/architecture.md#part.pattern.make). Nothing more is needed until R6, which waits on 9 and 10.
- **Placeholder.** R6.
- **Refactor risk.** None of its own.
- **Standing.** Core.

## Time and background work

### 12. The clock and background minds

- **What.** Time as a write to a clock page, and budgeted pages that run when nothing is waiting.
- **Why.** The OpenAI Agents SDK lists Temporal and others for long waits ([harnesses](../research/harnesses.md)). [`law.spend.meter`](../reference/architecture.md#law.spend.meter).
- **Seam.** Exists: [`kind.clock`](../reference/architecture.md#kind.clock), [`flow.clock.tick`](../reference/architecture.md#flow.clock.tick) and [`kind.mind`](../reference/architecture.md#kind.mind). Who writes the clock is open, and a connector is the shape the documents give it, so it meets entry 21.
- **Placeholder.** [Clock](../ideas/clock.md) R12, [background minds](../ideas/background-minds.md) R17.
- **Refactor risk.** None of its own: every write already takes `at` from its caller, and rules never read the time.
- **Standing.** Core.

### 13. Reactions that survive a crash

- **What.** A reaction that was due when the process stopped runs when the vault is next opened.
- **Why.** Temporal rebuilds state by replay and reuses recorded results ([harnesses](../research/harnesses.md)). [Gaps](../research/gaps.md) marks durable execution as covered; that holds for writes, not for the reactions they were due to cause.
- **Seam.** [Stepping](../ideas/stepping.md) already speaks of a due reaction and [`flow.vault.step`](../reference/architecture.md#flow.vault.step). The `Cause` trailer links a reaction to its write.
- **Placeholder.** R28.
- **Refactor risk.** See the fourth item below.
- **Standing.** Core.

## Data shapes

### 14. Tables, files and streams beside a page

- **What.** Parquet parts, captured files and growing tables kept beside a page and named by it.
- **Why.** [`law.data.three`](../reference/architecture.md#law.data.three). Not recorded in the comparison.
- **Seam.** [`data.table`](../reference/architecture.md#data.table), [`data.file`](../reference/architecture.md#data.file), [`data.stream.beside`](../reference/architecture.md#data.stream.beside), [`data.engine`](../reference/architecture.md#data.engine). A query engine stays optional and rules never read rows.
- **Placeholder.** [Tables](../ideas/tables.md), R1.
- **Refactor risk.** `Vault._check_commit` allows a write to change only `pages/` files and the signers file. Files beside a page must sit under `pages/` or `verify` must learn the new place, and the choice fixes the vault format for the golden vault ([`law.vault.golden`](../reference/architecture.md#law.vault.golden)).
- **Standing.** Core.

## Observability

### 15. Traces in standard names

- **What.** An export of the history as OpenTelemetry spans, written as OTLP JSON lines, with `Cause` as the parent.
- **Why.** The OpenAI Agents SDK has built-in tracing and Microsoft Agent Framework's harness lists observability ([harnesses](../research/harnesses.md)). The mapping is in [observability](../research/observability.md).
- **Seam.** Derived data ([`law.data.derived`](../reference/architecture.md#law.data.derived)) over trailers. [`stage.attention.strip`](../reference/architecture.md#stage.attention.strip) reads the same trailers.
- **Placeholder.** [The history is the trace](../ideas/trace.md), R11. The trace page does not yet name the export.
- **Refactor risk.** No trailer records a call's duration, reasoning tokens (F30) or a tool's name. Adding them is a change to the `Trailer` enum and the vocabulary. Duration differs from run to run and a cached answer has none, so its meaning must be fixed before it is written, or replayed histories will disagree.
- **Standing.** Optional.

## People and screens

### 16. Approvals and holding a vault

- **What.** A change that waits for signed approvals, and a person who holds a vault and steps it.
- **Why.** Microsoft Agent Framework names tool approval and Temporal uses Signals for human approval ([harnesses](../research/harnesses.md)).
- **Seam.** Exists: [`kind.proposal`](../reference/architecture.md#kind.proposal), [`kind.gatekeeper`](../reference/architecture.md#kind.gatekeeper), [`kind.hold`](../reference/architecture.md#kind.hold) and [`law.vault.hold`](../reference/architecture.md#law.vault.hold). No pause state is needed: a change without its approvals is refused.
- **Placeholder.** [Approvals](../ideas/approvals.md) R14, [stepping](../ideas/stepping.md) R28.
- **Refactor risk.** R14's scope change, below.
- **Standing.** Core.

### 17. The screen

- **What.** A screen derived from the pages, in small steps from a text outline to the compositor.
- **Why.** [Decision 0025](../decisions/0025-the-screen-is-built-in-small-steps.md). Not recorded in the comparison.
- **Seam.** Exists: [`part.screen`](../reference/architecture.md#part.screen) and the rows after it.
- **Placeholder.** [A screen from the pages](../ideas/a2ui.md), R11a to R11g.
- **Refactor risk.** One choice is open. A2UI replaces a value at a pointer and AG-UI sends JSON Patch ([streams and trees](../research/streams-and-trees.md)). The update step (R11d) has to pick one change form before anything is built on it.
- **Standing.** Optional.

### 18. Text as it arrives

- **What.** An answer shown while it streams, with only the finished answer written.
- **Why.** AG-UI streams text in start, content and end events ([streams and trees](../research/streams-and-trees.md)). [Gaps](../research/gaps.md) gives streaming no verdict, because the comparison does not cover it.
- **Seam.** An ask and derived data ([decision 0017](../decisions/0017-derived-data.md)).
- **Placeholder.** [Text as it arrives](../ideas/streaming.md), row [`part.screen.live`](../reference/architecture.md#part.screen.live).
- **Refactor risk.** `model.ask` reads the whole reply at once with one timeout. A streamed read is a change inside that one function, and it must never write a partial event ([`law.write.only`](../reference/architecture.md#law.write.only)).
- **Standing.** Optional.

## Outside protocols and tools

### 19. Tool servers and protocols

- **What.** Connectors that present a vault in the terms of MCP, AG-UI and other protocols, with a tool as a page and a call as a write to it.
- **Why.** Every compared harness has tool calling in code ([gaps](../research/gaps.md)). F31 found bash alone beat typed tool catalogues, which the terminal connector already resembles.
- **Seam.** Exists: [`part.connect.protocol`](../reference/architecture.md#part.connect.protocol), [`kind.tool`](../reference/architecture.md#kind.tool), [`flow.tool.call`](../reference/architecture.md#flow.tool.call), and the built [`part.connect.terminal`](../reference/architecture.md#part.connect.terminal). [Decision 0021](../decisions/0021-the-outside-arrives-as-pages.md).
- **Placeholder.** [Tools](../ideas/tools.md), [connectors](../ideas/connectors.md), R25.
- **Refactor risk.** A connector writes from its own process, which meets entry 21.
- **Standing.** Optional.

### 20. Reading the field

- **What.** Feeds and paper indexes followed by a connector on the clock, with each item a page and a periodic digest.
- **Why.** The project keeps its research index current by hand. Not recorded in the comparison.
- **Seam.** Connectors, the clock, entry 7 and patterns. Constrained by [`law.spend.meter`](../reference/architecture.md#law.spend.meter).
- **Placeholder.** [Reading the field](../ideas/outside-reading.md), row [`kind.feed`](../reference/architecture.md#kind.feed). No step yet.
- **Refactor risk.** None of its own, provided entry 7 lands first: unmarked outside text that a character can turn into rules is the risk F19 describes.
- **Standing.** Optional.

## Scale and distribution

### 21. Several writers at once

- **What.** Writes from several processes to one vault taken one at a time, each judged against the state the last one left.
- **Why.** AutoGen Core has local and distributed runtimes, and AG2 a hub with a write-ahead log ([harnesses](../research/harnesses.md)). The terminal connector already writes from its own process.
- **Seam.** The write path and Git's own locking. [`law.write.only`](../reference/architecture.md#law.write.only), [`law.refusal.record`](../reference/architecture.md#law.refusal.record), [`law.fallback.always`](../reference/architecture.md#law.fallback.always).
- **Placeholder.** [Several writers at once](../ideas/writers.md), row [`part.write.serial`](../reference/architecture.md#part.write.serial). No step yet.
- **Refactor risk.** `Vault.write` checks the tree is clean, loads pages, judges and commits with no lock held across the steps. Two writers can judge against the same state. Untested.
- **Standing.** Core.

### 22. Throughput and size

- **What.** A vault that stays usable at many pages and many events.
- **Why.** [Status](status.md) records tens of writes a second. F4 shows a shared repository used by hundreds of workers. "Git as a store under load" is open in the findings rubric.
- **Seam.** A busy space becomes its own vault ([`flow.vault.link`](../reference/architecture.md#flow.vault.link)), and indexes are derived data ([decision 0017](../decisions/0017-derived-data.md)). [Decision 0018](../decisions/0018-not-doing.md) rules out a second authority.
- **Placeholder.** [Vault splitting](../ideas/vault-splitting.md) R10, derived data R11.
- **Refactor risk.** `Vault._react` lists every page file and loads each watcher for every write. A watcher index is derived data and safe to add; reading watchers from it must give the same order as the scan.
- **Standing.** Core.

### 23. A core without Git

- **What.** A core in Rust, run natively and in a browser.
- **Why.** [Decision 0012](../decisions/0012-rust-core-planned.md). Not recorded in the comparison.
- **Seam.** Exists: [`part.core.rust`](../reference/architecture.md#part.core.rust), held to the same golden vault ([`law.vault.golden`](../reference/architecture.md#law.vault.golden)).
- **Placeholder.** R19.
- **Refactor risk.** `git.require_tools` makes Git and `ssh-keygen` mandatory. The golden vault is the contract, so every format choice above (entries 8, 9, 10, 14) binds the second core too.
- **Standing.** Optional.

## Evaluation

### 24. Resume, benchmark and repeated runs

- **What.** The model-backed resume test, the harness-neutral benchmark, repeated runs with a consistency measure, and a long scenario across several domains.
- **Why.** F33 (pass^k), F35 (long horizon), F36 (resume scored as state and behaviour apart), F34 (where a failure belongs).
- **Seam.** Exists: [`part.test.resume`](../reference/architecture.md#part.test.resume), [`part.test.bench`](../reference/architecture.md#part.test.bench), [`part.test.trial`](../reference/architecture.md#part.test.trial). [Decision 0013](../decisions/0013-evidence-not-scripts.md), [decision 0014](../decisions/0014-benchmark-shape.md). Branching a run from a recorded event composes from [dry run](../ideas/dry-run.md) and stepping.
- **Placeholder.** R7, R8, R27.
- **Refactor risk.** None in the runtime. The scenario format is not built, and no pass^k or failure-taxonomy measure exists.
- **Standing.** Core.

## Attention, notice and form

### 26. Standing

- **What.** A measure of how much each page matters now, and lists of what is within a space ordered by it. Nothing is declared by the page.
- **Why.** Fading of unused pages, an allowance that follows use and a quiet reflection all need one ordering, and without it each is a separate mechanism.
- **Seam.** The members embed and a measure that writes a field. Constrained by [decision 0008](../decisions/0008-measures-are-self-watches.md): the value is a recorded event.
- **Placeholder.** [Standing](../ideas/standing.md), with [nothing goes stale](../ideas/staleness.md) and [background minds](../ideas/background-minds.md).
- **Refactor risk.** `page._members_text` now orders by a space's `shows.first` when it has one, with a fallback to name order for members it cannot score and for a space with no `shows` ([decision 0042](../decisions/0042-a-space-shows-what-bears-first.md)). What is left is a stored measure of use for `first` to read, and counting uptake from links (`page.links`) and from joinings in history, so the change of `within` must stay in the record. The line format `name: first line` must stay, since the cache key hashes the resolved text.
- **Standing.** Core.

### 27. Being told

- **What.** A watch that fires when a write by a page, or to a page within it, was refused, with the reason readable.
- **Why.** A refusal is an event in history that nothing can react to. The author's space never learns it is stuck.
- **Seam.** A third relation for a watch beside `within` and `link`, a pattern like [approvals](../ideas/approvals.md). Constrained by [`law.refusal.record`](../reference/architecture.md#law.refusal.record).
- **Placeholder.** [Approvals as a pattern](../ideas/approvals.md), and the offer between neighbours in [patterns](../ideas/patterns.md).
- **Built.** `on: refusal` ([decision 0039](../decisions/0039-an-event-can-be-noticed.md)): `Vault._refuse` records the refusal and then tells the pages in relation through `Vault._tell`, with the depth limit covering loops. Not built: reactions to the refusals of model answers in bulk, and `on: refusal` across mounts.
- **Refactor risk.** A later kind of event adds a value of `event.kind` and a rule for who is told, in `Vault._tell`; the `event` map in the watch scope is the one place a reaction reads what happened.
- **Standing.** Core.

### 28. Faculties

- **What.** A page that watches another and writes the form a sentence asks for, one kind that costs nothing and one that costs a small call.
- **Why.** A thinking character should spend its context on what it wants, not on the syntax of rules and entries.
- **Seam.** Watch, ask, an answer that is pages and the retry on a refused answer. Constrained by [`law.provider.page`](../reference/architecture.md#law.provider.page).
- **Placeholder.** [Faculties](../ideas/faculties.md), with [auto-linking](../ideas/auto-linking.md) as the reflex case. Recognition at the write is built ([decision 0044](../decisions/0044-a-page-is-known-by-its-phrases.md)); minting term pages is the faculty's part and is not.
- **Refactor risk.** Little is closed off today. An answer that is pages is written as a block of pages into a space, which may add rules and reflex watch entries to it, and that is the path a faculty uses. What must stay open is trying a written form aside before it binds, which needs the write path to judge without keeping (the same need as [dry run](../ideas/dry-run.md)), and a field or trailer by which a character is shown in words what a faculty did.
- **Standing.** Optional.

## Out of scope

### 25. A second backend, a runtime planner, hosting

- **What.** A choice of session store, a planner that writes todo lists, a hosted service.
- **Why.** The OpenAI Agents SDK offers several session backends, and Microsoft Agent Framework's harness plans with todos ([gaps](../research/gaps.md)).
- **Seam.** None wanted. One store, Git ([decision 0002](../decisions/0002-git-is-the-store.md)); a plan is a page; a vault is a folder anyone can host. [`law.scope.out`](../reference/architecture.md#law.scope.out).
- **Placeholder.** [Decision 0018](../decisions/0018-not-doing.md).
- **Refactor risk.** Adding any of them would be the refactor.
- **Standing.** Out of scope.

## What today's code would have to change

For the maintainers, most serious first. Nothing here has been changed.

1. **Reactions are not handed down.** `within` is a name or a list ([decision 0045](../decisions/0045-a-page-may-be-within-several-spaces.md)), and `Vault._above` orders the spaces above a page for rules, context and notice. A space's watch entries do not yet run for its members, so handing reactions down (entry 9, R22, the `next` step) needs a rule for whose scope the entry reads, over a graph where a member may hear one space twice.
2. **A write is one page.** `Vault.write` takes one page, `Vault._record` stores one page file, the `Page` trailer names one page, and `_write` runs reactions straight after its own commit. A grouped write (entry 10, R24) needs several pages per event, a refusal of the whole group, and reactions held until the group is kept. An answer that is pages is written today as one commit for each page; under groups it would be one event, which changes what the history of R29 looks like.
3. **Rules see only the page.** `Vault._rule_reason` passes `page`, `space`, `size` and `text`. Rules that see who signed (R14), the origin of content (entry 7) and a reviewer's verdict (entry 6) all add to this scope. One decision should fix the names and shapes of all three, or the scope is redone at each step.
4. **Reactions leave no record of being due.** `Vault._react` runs in the same process right after the commit. A crash between the two loses the reactions, and a reaction whose `when` was false leaves no event, so the history cannot tell "not yet run" from "ran and declined". Stepping (R28), background minds (R17) and entry 13 all need "due" derived from the history alone.
5. **`verify` judges the past by today's signers.** `Vault.verify` checks `%G?` against `keys/allowed_signers` in the working tree. Retiring or revoking a key (entry 8) needs each event judged against the signers in force at its parent.
6. **A prompt is one string.** `model._request` sends a single user message, `model.ask` reads the whole reply, `Answer` holds text and two token counts, and `model.moment_key` hashes the prompt string. Fixed context parts for prompt caching (entry 4), files and images (entry 1), streaming (entry 18) and reasoning tokens (entries 3 and 15) all change these four places.
7. **No lock across a write.** `Vault.write` and `Vault.ask` check, judge and commit without holding a lock, while the terminal connector already writes from its own process (entry 21).
8. **`verify` allows only page files and the signers file.** `Vault._check_commit` refuses any other path in a write. Tables and files beside a page (entry 14) need a place it accepts, fixed in the vault format.
9. **The trailer set is closed.** The `Trailer` enum and the vocabulary list every trailer. Duration, reasoning tokens and tool names (entry 15) are additions, and duration needs a meaning that survives the cache and replay before it is written.
10. **Every write scans every page.** `Vault._react` globs `pages/` and loads each watcher on each write (entry 22). A derived watcher index fixes the cost, and the order of reactions it gives must match the scan's name order.
11. **Detection order is code.** `model.detect` returns a fixed list of choices. A router page (entry 5) should feed that list, not sit beside it.
