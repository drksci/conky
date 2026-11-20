---
kind: research
title: "What others have that Conky lacks: skip, covered or rethought"
status: draft
date: 2026-11-20
source: "harnesses.md matrix and notes, findings-rubric.md, and the project's own ideas and decisions"
---

# What others have that Conky lacks: skip, covered or rethought

Conky does not copy what other frameworks do. For each capability they document, it has one of three answers: leave it out, point to the part that already does it, or rebuild it from pages, spaces, rules, watches and the three laws in [decision 0029](../decisions/0029-autonomy-inside-limits-that-hold.md). Some of these answers go against convention, and the page says where.

Every capability below comes from a row or note in [harnesses.md](harnesses.md), which cites its own source pages. None comes from memory. Nothing here is built unless the row says so, and no row claims Conky does better.

## How to read this

- **Skip.** Conky does without, and the reason is stated.
- **Covered.** An existing part does it, and the row names the part.
- **Rethink.** Conky would build it from its own parts, never from the other design. An idea page is named where one exists. Every idea is at the rung "idea" and unbuilt unless the row says otherwise.

## Capabilities and verdicts

| Capability | Source in harnesses.md | Verdict | Conky's answer |
|---|---|---|---|
| Checkpoints, replay and fork | (e) and (f) rows for LangGraph, CrewAI and Microsoft Agent Framework | Covered | Every write is a signed event, so any state can be rebuilt and any commit branched from ([decision 0029](../decisions/0029-autonomy-inside-limits-that-hold.md)). `conky rebuild` restores the committed state. |
| Durable execution after a crash | Temporal note (Event History, replay) | Covered | The log is the state, and `conky assimilate` takes a stopped vault over from its folder alone. Retries are skipped: a failed write is a recorded refusal, and a reaction can write again. |
| Memory stores | (a) row for LangGraph, Microsoft Agent Framework and Letta | Covered | Memory is pages in the vault, which is the form Letta's MemFS note describes (Markdown with frontmatter, history in git). Whether organised pages help is open ([findings-rubric](findings-rubric.md), F8). |
| Sub-agents and handoffs | OpenAI Agents SDK and Claude Agent SDK notes | Covered | A character writes pages, so it can make another character and a space for it ([decision 0028](../decisions/0028-a-character-writes-pages.md)). A handoff is a write to another page. |
| Agent definitions in files | (g) row for CrewAI and Claude Agent SDK | Covered | A page already is the definition, and its prompt, reaction and rules are fields on it. |
| Typed state | CrewAI note (dict or Pydantic flow state) | Covered | A CEL rule on the page, handed down by its space, refuses a write that breaks the shape. |
| Tracing and observability | OpenAI Agents SDK note (built-in tracing); Microsoft Agent Framework harness note | Covered | The history is the trace, with `Read` and `From` trailers. Summaries over it are unbuilt ([trace](../ideas/trace.md), R11). |
| Evaluation hooks and metrics | (d) and (i) rows; Microsoft Agent Framework loop evaluators | Covered | A measure is a page watching itself, recorded as an event. The benchmark harness is `bench/`, run only against a stand-in so far. |
| Guardrails written as code | OpenAI Agents SDK and CrewAI notes | Covered | Rules are the guardrail, run by the runtime on every write. The Claude Agent SDK hooks note says a crashing hook lets a call proceed, which a rule cannot do. |
| Guardrails that judge meaning with a model | CrewAI note (LLM-judged guardrail); OpenAI Agents SDK note | Rethink | Rules stay pure. A reviewing model page writes a verdict page, and a rule refuses the change until a signed verdict is there ([decision 0005](../decisions/0005-rules-in-cel.md), [approvals](../ideas/approvals.md)). The answer is pages, not a hook. No idea page covers the reviewer. |
| Human approval and interrupts | Microsoft Agent Framework harness note (tool approval); Temporal note (Signals) | Rethink | An approval is a signed page a rule counts, and the held change is applied by a reaction. No pause state exists, because a change that lacks its approvals is simply refused ([approvals](../ideas/approvals.md), R14). |
| Tool calling | OpenAI Agents SDK run-loop note; Claude Agent SDK hooks note | Rethink | There is no tool call. A connector writes what it perceives as pages, and a character writes the page that says what to do ([tools](../ideas/tools.md)). The terminal connector is built. Calling a tool, a function or a handoff is the same write, which goes against the convention of a typed call. |
| Cost bounds and turn caps | (i) row; Claude Agent SDK note (`max_turns`, `max_budget_usd`) | Rethink | A space's budget is shared among what lies inside it, so more characters divide spend and never multiply it, and a page stops at its budget ([decision 0029](../decisions/0029-autonomy-inside-limits-that-hold.md), [background minds](../ideas/background-minds.md), R17). Only the depth cap of 12 exists. |
| Context compaction | Microsoft Agent Framework harness note (compaction) | Rethink | Pressure notices size, and relief is a reaction that summarises, splits or archives, so compaction is a visible write that can be undone from history ([staleness](../ideas/staleness.md), [pressure, not walls](../essays/pressure-not-walls.md), R3). |
| Resume across machines | Claude Agent SDK note (session file on one machine); Microsoft Agent Framework note (same topology) | Rethink | The vault is the whole state, so resume is a clone. The mechanical form is built; whether a model continues correctly is not ([assimilation test](../ideas/assimilation-test.md), R7). |
| Scale and distributed runtimes | AutoGen Core note (local and distributed runtimes); AG2 note | Rethink | One signed commit per write limits throughput to tens per second ([status](../project/status.md)). The plan is to split a space into its own vault that the parent links to ([vault splitting](../ideas/vault-splitting.md)), not to add a second authority ([decision 0018](../decisions/0018-not-doing.md)). |
| Planning and todo lists | Microsoft Agent Framework harness note | Skip | A plan is a page and a todo is a line on it. A runtime planner would be a second way to write a page. |
| Choice of session backend | OpenAI Agents SDK note (SQLite, Redis, SQL, Mongo, Dapr) | Skip | One store, Git ([decision 0002](../decisions/0002-git-is-the-store.md)). A second backend means two authorities that can disagree. |
| Hosted offering and integrations | Where conky is behind, last item of [harnesses.md](harnesses.md) | Skip | A vault is a folder anyone can clone, so hosting is somebody else's job. Integrations arrive as connectors beside the vault ([connectors](../ideas/connectors.md)). |
| Streaming | Not in harnesses.md | Not sourced | The harness page does not cover it, so no verdict is given. |

## Counts

Covered 9, rethink 7, skip 3, not sourced 1.

## The rethinks

| Capability | The rethink | Idea | Roadmap |
|---|---|---|---|
| Cost bounds | Spending is conserved down a space | [background minds](../ideas/background-minds.md) | R17 |
| Human approval | A proposal, signed approvals and a rule that counts them | [approvals](../ideas/approvals.md) | R14 |
| Tool calling | A connector's pages are its senses and hands | [tools](../ideas/tools.md) | built for the terminal |
| Guardrails that judge meaning | A reviewing page and a rule that waits for its verdict | no idea yet | R17 and R18 touch it |
| Context compaction | Relief acts on pressure | [staleness](../ideas/staleness.md) | R3 |
| Resume across machines | The vault is the state | [assimilation test](../ideas/assimilation-test.md) | R7 |
| Scale | A space becomes its own vault | [vault splitting](../ideas/vault-splitting.md) | none yet |

## What this page does not settle

The verdicts are the maintainers' judgement and have not been tested. A skip is a bet that the pages cover it, and a benchmark could show otherwise ([findings-rubric](findings-rubric.md) lists where the research cuts against the design).
