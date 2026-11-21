---
kind: research
title: "Agent harnesses compared"
status: current
date: 2026-11-20
source: "project documentation of each harness, fetched 2026-11-20"
---

# Agent harnesses compared

## How to read this

The official documentation pages listed under [Sources](#sources) and, for a few projects, the GitHub README were fetched on 2026-11-20. Every cell in the matrix comes from one of those pages and nothing else: no cell comes from memory. Pages were read through a fetch tool that returns a condensed reading of each page, so wording is paraphrased and only short phrases are quoted. "Not confirmed" means the documentation read did not settle the question. It does not mean the feature is absent. Every site listed in Sources was reached; where a page did not cover a topic, the cell says so. One page did not match its address: the LangGraph `durable-execution` address returned text about persistence and did not discuss durable execution as its own topic.

The harnesses are LangGraph, CrewAI, AutoGen (archived) with its successors AG2 and Microsoft Agent Framework, the OpenAI Agents SDK, the Claude Agent SDK, Letta, and Temporal used as a durable-execution layer for agents. Temporal and Microsoft Agent Framework are the "up to three more" and were chosen because the OpenAI Agents SDK documentation lists Temporal among its durable-execution integrations, and because Microsoft's documentation names Agent Framework as the direct successor of AutoGen. No other harness was researched; a file-first harness beyond Letta's git-backed memory was not examined.

conky is described from its own documents ([design](../design.md), [status](../project/status.md)). It is pre-alpha, has only been run against stand-in model servers, and has no benchmark results. Nothing here says conky performs better than anything else.

## The rubric

**(a) Where state lives.** The place a running system keeps what it knows: process memory, a database, files, an event history. This says what must survive for the system to continue.

**(b) What is authoritative when sources disagree.** If a stored record, a derived view and a model's recollection differ, which one wins. A system with no stated answer is leaving this to the code that happens to run.

**(c) How constraints are enforced.** Whether "this must never happen" is asked of the model in a prompt, validated in application code that the developer writes, or enforced by the runtime on every state change whatever the code does.

**(d) When a model is called.** At every step of a loop, or only when something needs judgment while state-derived decisions run without one.

**(e) History, replay and audit.** Whether past states or events are kept, whether they can be replayed, and whether a refusal or failure leaves a record.

**(f) Resume and portability.** Whether a stopped system can be picked up on another machine from its stored state alone, without the original process or its host.

**(g) How multi-agent structure is expressed.** In code (a program builds the agents and their wiring), in configuration files, or as data the system itself can read and change.

**(h) Readable and editable by a person without tooling.** Whether a person with a text editor can read the running state and change it, or whether it sits behind an API or a binary format.

**(i) How cost is bounded.** What stops a run from spending without limit: turn caps, budgets, rate limits, or nothing.

## The matrix

| Harness | (a) State | (b) Authority | (c) Constraints | (d) Model calls | (e) History | (f) Resume | (g) Structure | (h) Readable | (i) Cost |
|---|---|---|---|---|---|---|---|---|---|
| LangGraph | Checkpointer per thread; separate store for cross-thread data | Not confirmed | Graph in code; no rule layer confirmed | Deterministic and LLM steps mixed in one graph | Checkpoints; history listing; replay and fork | `thread_id` with Postgres or SQLite saver; in-memory lost | Code: nodes and edges | Edited through `update_state`; raw files not confirmed | `recursion_limit` caps super-steps; large default |
| CrewAI | Flow state, dict or Pydantic; `@persist` to SQLite by default | Not confirmed | Task guardrails: function or LLM-judged; retries default 3 | Agents loop up to `max_iter`; flow-level rule not confirmed | Snapshots by state ID; audit trail not confirmed | Resume by ID; fork with `restore_from_state_id` | Code, plus YAML or JSONC agent files | Not confirmed | `max_iter` 20; `max_rpm` and time limit optional |
| AutoGen (archived) | Runtime manages agents; state saving not confirmed | Not confirmed | Not confirmed | Not confirmed | Not confirmed | Not confirmed | Code: message-handling agents on a runtime | Not confirmed | Not confirmed |
| AG2 | Hub holds registry, write-ahead log, audit trail; disk-backed knowledge store | Not confirmed | Not confirmed | Not confirmed | Write-ahead log and audit trail named; replay not confirmed | General resume not described | Code: Network with typed channels | Not confirmed | No turn cap mentioned; conversation channels never auto-close |
| Microsoft Agent Framework | Agent sessions; workflow checkpoints in memory, file or Cosmos DB | Not confirmed | Approval middleware and loop evaluators; judge may be a model | Agent for open-ended tasks; workflow for defined steps | Checkpoint each superstep; Python 1.13 entry checkpoints make runs replayable | Rehydrate new instance from checkpoint; same topology required | Code: graph workflows; declarative agents also exist | Python stores pickle; Go stores JSON; editing not confirmed | Loop default 10 iterations; per-request iteration limit |
| OpenAI Agents SDK | Sessions: SQLite, Redis, SQL, Mongo, Dapr or server-side | Not confirmed | Guardrail functions in code, may call a model; tripwire halts | Model called each turn until final output | Session items kept; built-in tracing; replay not confirmed | `RunState` or same session ID and backend | Code: handoffs and agents as tools | Session API edits; SQLite file can be edited externally | `max_turns` raises error; `None` disables |
| Claude Agent SDK | Transcript files on local disk; optional session-store adapter | Not confirmed | Hooks in code deny tool calls; crashed hook may let call proceed | Model each turn until a reply has no tool calls | Transcript; resume and fork; file checkpointing separate | Same machine by default; store adapter or moved file elsewhere | Code, or markdown files in `.claude/agents/` | JSONL transcripts; editing not confirmed | `max_turns`, `max_budget_usd`; default no limit; cost an estimate |
| Letta | Memory as git repo of Markdown files; other state not confirmed | Not confirmed | Not confirmed | Not confirmed | Every memory edit committed to git | Cloud agents sync by push; local-only agents need own backup | Not confirmed; shared memory between cloud agents | Markdown with YAML frontmatter; human editing not stated | Not confirmed |
| Temporal | Event History; state rebuilt by replay, not snapshot | Event History called the source of truth | Workflow code must be deterministic; rule layer not confirmed | LLM call runs as an Activity chosen by your code | Complete ordered event history; replay reuses recorded results | Any worker with the same code can replay; not stated outright | Code: workflows and activities | Not confirmed | Retries delegated to Temporal; cost bound not confirmed |
| conky | Signed hash-chained event log; pages are projections | The log; pages rebuilt from it | CEL rules enforced by runtime on every write; refusals recorded | State-derived reactions use none; model-backed pages not built | Full signed log; `verify` and `rebuild` byte for byte | Copied vault verifies and rebuilds; resume by a consumer unbuilt | Data: pages, watch entries, `within` chains | Markdown pages readable; by rule never edited by hand | Asks per page counted from the history and refused past a stated budget; tokens and money not metered; reaction depth capped at 12 |

## Per-harness notes

### LangGraph

In its own words it is a low-level orchestration framework and runtime for long-running, stateful agents, where workflows are graphs of shared state, nodes and edges written in code, and it does not prescribe prompts or an agent architecture. Checkpointers hold thread-scoped state; stores hold application data across threads. Time travel can replay from a checkpoint (later nodes run again, so LLM calls and API requests can return different results) or fork by calling `update_state`, which creates a new checkpoint and leaves the original history intact. Interrupts always re-trigger on replay. The recursion limit default stated is 10,007 from version 1.1.4.

Sources: [overview](https://docs.langchain.com/oss/python/langgraph/overview), [persistence](https://docs.langchain.com/oss/python/langgraph/persistence), [time travel](https://docs.langchain.com/oss/python/langgraph/use-time-travel), [graph API](https://docs.langchain.com/oss/python/langgraph/graph-api), [durable execution address](https://docs.langchain.com/oss/python/langgraph/durable-execution). Notable: the documentation read does not say which source wins when a replay differs from the original run, so (b) is not confirmed.

### CrewAI

Flows carry a state object that gets a unique ID, and `@persist` saves it, by default to local SQLite. Calling `kickoff` with an existing ID loads the latest snapshot; `restore_from_state_id` starts a new run from a snapshot under a fresh ID. An unmatched ID falls back silently, which the page states. Agents are defined in code, or in `agents.yaml` and `tasks.yaml` (classic), or in JSONC files (recommended for new crews). Task guardrails check output before it passes on, either as a function or as a natural-language rule judged by the agent's own LLM, with `guardrail_max_retries` defaulting to 3.

Sources: [flows](https://docs.crewai.com/en/concepts/flows), [agents](https://docs.crewai.com/en/concepts/agents), [tasks](https://docs.crewai.com/en/concepts/tasks). Notable: the flows page does not cover guardrails or `max_iter`; those were taken from the agents and tasks pages.

### AutoGen and AG2

The AutoGen README says the project is archived and in maintenance mode, names Microsoft Agent Framework as the successor, and describes three layers: Core (message passing, event-driven agents, local and distributed runtimes), AgentChat and Extensions. The AG2 README describes AG2 as the successor to AutoGen (formerly AutoGen), says v1.0 is not a drop-in upgrade from the classic version, and describes a Hub that manages the registry, a write-ahead log and an audit trail, with agents talking over typed channels. How either handles resume, constraints or cost was not settled by the pages read. The AutoGen Core page fetched did not cover state saving.

Sources: [AutoGen README](https://github.com/microsoft/autogen), [AG2 README](https://github.com/ag2ai/ag2), [AutoGen Core agents page](https://microsoft.github.io/autogen/stable/user-guide/core-user-guide/framework/agent-and-agent-runtime.html). Notable: AG2 names a write-ahead log, the closest idea to conky's log among the harnesses read, but the README does not say what is replayable from it.

### Microsoft Agent Framework

Described by Microsoft as the direct successor of both Semantic Kernel and AutoGen, with four areas: agents, a Harness Agent for long multi-step tasks (planning and todos, compaction, file memory, tool approval, observability), graph workflows, and integrations. Workflow checkpoints are written at the end of each superstep and capture executor state, pending messages, pending requests and shared state; they can be stored in memory, on local disk or in Cosmos DB, and a new workflow instance with the same topology and executor identities can be rehydrated from one. Looping is optional, experimental, and bounded; the default maximum stated is 10 iterations. The documentation advises that if a function can do the task, use a function rather than an agent.

Sources: [overview](https://learn.microsoft.com/en-us/agent-framework/overview/), [checkpoints](https://learn.microsoft.com/en-us/agent-framework/workflows/checkpoints), [harness](https://learn.microsoft.com/en-us/agent-framework/concepts/harness), [looping](https://learn.microsoft.com/en-us/agent-framework/agents/looping). Notable: the checkpoint page warns that checkpoint storage is a trust boundary and that Python's file and Cosmos stores use pickle with a restricted unpickler.

### OpenAI Agents SDK

A lightweight framework described as a production-ready upgrade of an earlier experimental project (Swarm), built on agents, handoffs, guardrails, sessions and tracing. The run loop calls the model, executes tool calls or switches agent on a handoff, and ends when the model produces final output with no tool calls. Exceeding `max_turns` raises an error. Guardrails are functions written by the developer and may call a model; a tripped tripwire raises an exception and halts the run. A paused run resumes from a `RunState`, or by reusing the same session ID and backend. For long waits and restarts the documentation lists Dapr, Temporal, Restate and DBOS integrations.

Sources: [home](https://openai.github.io/openai-agents-python/), [sessions](https://openai.github.io/openai-agents-python/sessions/), [guardrails](https://openai.github.io/openai-agents-python/guardrails/), [running agents](https://openai.github.io/openai-agents-python/running_agents/). Notable: the sessions page warns that `SQLiteSession` does not detect external edits to its database, so editing it by hand is possible but unmanaged.

### Claude Agent SDK

Described as Claude Code's tools, agent loop and context management, programmable in Python and TypeScript. A session is the accumulated conversation history, written to disk automatically, under `~/.claude/projects/` by default. Sessions persist the conversation, not the filesystem. Resume needs the session file on the current machine unless a session-store adapter or a moved file is used. Hooks run in the application's process and can deny a tool call; the page says a hook that crashes lets the call proceed unless `onFailure: "block"` is set. Limits include `max_turns` and `max_budget_usd`, both defaulting to no limit, plus subagent depth and concurrency caps; cost figures are described as client-side estimates, not billing data. Subagents can be defined in code or as markdown files.

Sources: [overview](https://code.claude.com/docs/en/agent-sdk/overview), [sessions](https://code.claude.com/docs/en/agent-sdk/sessions), [agent loop](https://code.claude.com/docs/en/agent-sdk/agent-loop), [hooks](https://code.claude.com/docs/en/agent-sdk/hooks), [subagents](https://code.claude.com/docs/en/agent-sdk/subagents), [cost tracking](https://code.claude.com/docs/en/agent-sdk/cost-tracking). Notable: this project's own working method uses CLAUDE.md, which the same documentation says is re-injected on every request and recommended for persistent rules because compaction can drop early instructions.

### Letta

The documentation describes Letta as a platform for building stateful agents, with Letta Code (an open-source coding harness) and the Letta Agent SDK; the older V1 SDK is described as being deprecated. The MemFS page says an agent's memory is held in a git repository, each memory is a Markdown file with YAML frontmatter, every edit is committed, and cloud-backed agents push to a hosted repo while local-only agents must be backed up by the user. Where the rest of an agent's state lives, how constraints and cost are handled, and whether a person may edit memory directly were not settled by the pages read.

Sources: [docs home](https://docs.letta.com/), [concepts](https://docs.letta.com/concepts/letta), [MemFS](https://docs.letta.com/concepts/memfs), [GitHub README](https://github.com/letta-ai/letta). Notable: the closest of the harnesses read to conky on openness of format (Markdown with frontmatter, history in git).

### Temporal

Workflows are described as resilient and able to continue after the application crashes. Event History is a complete ordered log and the source of truth. On resume Temporal re-runs the workflow code and uses the history to rebuild prior state, reusing recorded Activity results, so the code must be deterministic; anything touching the outside world, including LLM calls, belongs in Activities. The AI cookbook shows an agentic loop where the model call and tool calls are Activities, the OpenAI client is created with retries off because Temporal handles retries, and human approval uses Signals.

Sources: [workflows](https://docs.temporal.io/workflows), [AI cookbook](https://docs.temporal.io/ai-cookbook), [agentic loop recipe](https://docs.temporal.io/ai-cookbook/agentic-loop-tool-call-openai-python). Notable: the workflows page does not state that another worker can resume; the fetch reading marked that as inferred from the design, so it is not claimed here. Timeouts and replay details were not covered by the cookbook index.

## Where conky differs, and why

conky has no results, so none of the following is a claim that its choice is better. Each paragraph says what the other approach gets right.

**The authority is a signed log, and pages are rebuilt from it.** In the harnesses read, state is held as checkpoints, sessions or snapshots (LangGraph, CrewAI, Microsoft Agent Framework, OpenAI Agents SDK), or as a transcript (Claude Agent SDK). Temporal and AG2 name an event history or write-ahead log, but the first re-runs code against it. conky makes every change a signed, hash-chained event and lets `verify` replay the log to reproduce every page byte for byte, so no stored state can disagree with its history. The reasoning is in [decision 0002](../decisions/0002-git-is-the-store.md) and the essay [The log is the truth](../essays/the-log-is-the-truth.md). What the checkpoint approach gets right: a snapshot resumes quickly and needs no replay, and checkpoint tools are mature and run today. conky gives up cheap snapshotting and pays for replay.

**Rules are enforced by the runtime on every write, and refusals are recorded.** Most harnesses read validate in application code (guardrail functions, hooks, evaluators) that the developer must remember to attach, and some of that code can itself call a model. The Claude Agent SDK page states that a crashing hook lets the call proceed unless configured otherwise. conky evaluates CEL rules inherited down a chain of spaces and records a `refused` event. See [decision 0005](../decisions/0005-rules-in-cel.md) and [Rules, not requests](../essays/rules-not-requests.md). What the other approach gets right: code guardrails can express anything a program can, including a model-judged check on meaning; conky rules are pure expressions over the page and its size, so they cannot judge content they cannot compute.

**Whatever follows from state happens with no model call.** The OpenAI Agents SDK and Claude Agent SDK loops call the model each turn; LangGraph and Microsoft Agent Framework can mix deterministic and model steps, and the Microsoft documentation itself says to write a function when a function will do. conky makes the deterministic case the default and reserves inference for questions state cannot answer. See [decision 0007](../decisions/0007-inference-for-real-thinking.md) and [Things that just happen](../essays/things-that-just-happen.md). What the other approach gets right: a model can handle situations nobody wrote a reaction for. conky has no model-backed pages yet, so today it handles only what its rules and reactions anticipate.

**A measure is a page watching itself, recorded as an event.** Where the harnesses read expose metrics, they are observability output (tracing, usage fields). conky writes a computed value as an ordinary event so replay never re-evaluates an expression. See [decision 0008](../decisions/0008-measures-are-self-watches.md). What the other approach gets right: tracing systems capture far more detail than a field on a page, and the cost of a noisy measure is a noisy log, which is a stated open question in that decision.

**Multi-agent structure is data.** Every harness read where the question was settled expresses structure in code (Letta's was not confirmed), sometimes with YAML, JSONC or markdown files for agent definitions. In conky, structure is pages, `watch` entries and `within` chains in the vault, so it travels with the state. See the [design](../design.md). What the other approach gets right: a graph in a typed language gets editor support, type checks and tests that conky's data does not have.

**The vault travels alone.** Resume in the harnesses read depends on a store plus matching code: the Claude Agent SDK needs the session file on the machine unless an adapter is configured, Microsoft Agent Framework needs the same topology and executor identities, and Temporal needs the workflow code. conky's intent is that a copied vault verifies and rebuilds with no private key. The test of whether a fresh consumer resumes correctly is not built; see [Assimilation test](../ideas/assimilation-test.md) and [decision 0014](../decisions/0014-benchmark-shape.md). What the other approach gets right: stored state plus code is enough for those systems to continue running work, while conky has shown only that a vault verifies and rebuilds, not that anything resumes it.

### Where conky is behind

- Pages that ask a model exist but have only been tested against stand-in servers, not a live provider. All the harnesses read run models today.
- Cost bounding is built for asks only: a page may carry a budget of asks, counted from the history ([decision 0058](../decisions/0058-a-budget-the-runtime-holds.md)). Tokens, money and time windows are not metered, and background pages are not yet built. Several harnesses read ship turn and budget caps.
- No benchmark has been run, so no comparison on outcomes is possible; see [decision 0014](../decisions/0014-benchmark-shape.md).
- The resume test is not built, so "a vault travels alone" is verified only as far as `verify` and `rebuild`.
- Two integrity gaps are recorded in [open questions](../project/open-questions.md), including that removing the final event is not detected when it is a refusal.
- No tables, grouped writes or pattern maker yet; see the [roadmap](../project/roadmap.md).
- No ecosystem: the harnesses read have hosted options, integrations and documentation sets that conky does not.

## Sources

All fetched 2026-11-20.

- https://docs.langchain.com/oss/python/langgraph/overview
- https://docs.langchain.com/oss/python/langgraph/persistence
- https://docs.langchain.com/oss/python/langgraph/durable-execution
- https://docs.langchain.com/oss/python/langgraph/use-time-travel
- https://docs.langchain.com/oss/python/langgraph/graph-api
- https://docs.crewai.com/en/concepts/flows
- https://docs.crewai.com/en/concepts/agents
- https://docs.crewai.com/en/concepts/tasks
- https://github.com/microsoft/autogen
- https://microsoft.github.io/autogen/stable/user-guide/core-user-guide/framework/agent-and-agent-runtime.html
- https://github.com/ag2ai/ag2
- https://learn.microsoft.com/en-us/agent-framework/overview/
- https://learn.microsoft.com/en-us/agent-framework/workflows/checkpoints
- https://learn.microsoft.com/en-us/agent-framework/concepts/harness
- https://learn.microsoft.com/en-us/agent-framework/agents/looping
- https://openai.github.io/openai-agents-python/
- https://openai.github.io/openai-agents-python/sessions/
- https://openai.github.io/openai-agents-python/guardrails/
- https://openai.github.io/openai-agents-python/running_agents/
- https://code.claude.com/docs/en/agent-sdk/overview
- https://code.claude.com/docs/en/agent-sdk/sessions
- https://code.claude.com/docs/en/agent-sdk/agent-loop
- https://code.claude.com/docs/en/agent-sdk/hooks
- https://code.claude.com/docs/en/agent-sdk/subagents
- https://code.claude.com/docs/en/agent-sdk/cost-tracking
- https://docs.letta.com/
- https://docs.letta.com/concepts/letta
- https://docs.letta.com/concepts/memfs
- https://github.com/letta-ai/letta
- https://docs.temporal.io/workflows
- https://docs.temporal.io/ai-cookbook
- https://docs.temporal.io/ai-cookbook/agentic-loop-tool-call-openai-python
