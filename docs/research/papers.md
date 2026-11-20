---
kind: research
title: "Paper register"
status: current
date: 2026-11-20
source: "research/dair-2026.md and the papers' own pages"
---

# Paper register

## How to read this

This register lists outside papers the project has considered, with how far each was read. It starts with the fifteen papers in the "Top 15 to read first" section of [dair-2026.md](dair-2026.md), the DAIR.AI index. On 2026-11-20 the abstract page of each was fetched. The register is compiled from the list's own entries, and the depth of reading is stated for each paper. It does not rank the papers beyond that index.

Columns:

- **Week listed**: the DAIR.AI weekly issue that listed the paper, as given in the index.
- **Depth**: how far the project has read. `listed` means only the DAIR.AI entry was read. `abstract` means the abstract page was fetched and read. `read` means the paper itself was read. A depth is never marked higher than what was reached. No paper here has reached `read`.
- **Relation to conky**: one of prior art, supports, challenges, benchmark candidate, caution. These are the reader's judgement about how the idea relates to conky's design, not a finding of the paper.
- **The idea**: one line.
- **What conky should do**: one line, or "nothing yet".
- **Link**: the page that was fetched.

Notes on the fetched pages. Pages on arxiv.org are the abstract pages. Pages on academy.dair.ai are DAIR.AI Academy summary pages that reproduce the abstract and add a curator's take and key points; they are not the paper. Pages were read through a fetch tool that condenses them, so abstracts are paraphrased here and only short phrases are quoted. Where a number below came from a summary page's key points instead of the abstract, the entry says so. Two papers (AI-Native Design Docs, ReHarness) have no link in the index; they were identified by web search from the index's description and the fetched arXiv page is linked. That match rests on title and description agreeing, and is stated as such in the entries.

## The register

| Paper | Week listed | Depth | Relation to conky | The idea | What conky should do | Link |
|---|---|---|---|---|---|---|
| JevAct | Nov 2 - 8 | abstract | supports | A runtime gate checks policy and task completion before consequential tool actions | Nothing yet; revisit when model-backed pages exist | [page](https://academy.dair.ai/papers/think-before-you-act-decision-gate-for-llm-agents-2610.38620) |
| Auton Agentic AI Framework | Mar 1 - 8 | abstract | prior art | A declarative agent specification kept separate from the runtime that executes it | Compare its spec and runtime split with the vault and runtime once read in full | [page](https://arxiv.org/abs/2602.23720) |
| Runtime-Independent Persistent Agents | Aug 31 - Sep 6 | abstract | benchmark candidate | A persistent identity, memory and code layer moves between models, harnesses and hosts by a fixed handoff protocol | Use its handoff steps as input when the assimilation test is designed | [page](https://academy.dair.ai/papers/runtime-independent-persistent-agents-preserving-identity-memory-and-code-across-2609.00546) |
| Filesystem Memory Audited | Jul 27 - Aug 2 | abstract | caution | Markdown-file memory organised by an agent roughly halves retrieval cost but does not improve answers | Do not assume that organising pages improves answers; measure it | [page](https://arxiv.org/abs/2607.26637) |
| AI-Native Design Docs | Sep 7 - 13 | abstract | prior art | A library kept as linked natural-language design documents, with code regenerated from them | Nothing yet | [page](https://arxiv.org/abs/2609.05364) |
| Skills as Verifiable Artifacts | May 4 - 10 | abstract | supports | An agent skill is untrusted until verified, and the runtime enforces that default | Nothing yet; relevant if skills or patterns are ever executed | [page](https://arxiv.org/abs/2605.00424) |
| GitSwarm | Oct 12 - 18 | abstract | prior art | Many agents coordinate through commits in a shared Git repository, each recording what it builds on | Compare commit lineage with the event log's causes when read in full | [page](https://academy.dair.ai/papers/gitswarm-decentralized-compounding-inference-2610.04862) |
| JevAgentHarness | Oct 19 - 25 | abstract | caution | Routine choices go to a small decision model above a fitted confidence threshold, else to the LLM | Nothing yet; note that delegation without a fitted threshold lowered success | [page](https://academy.dair.ai/papers/jevagentharness-benchmarking-deploying-and-training-decision-models-that-share-c-2610.21412) |
| HarnessMM | Oct 26 - Nov 1 | abstract | supports | Settled model decisions are reused under guards; unsupported cases return to the model | Keep as evidence for the learned-reactions idea; build nothing until a model is attached | [page](https://academy.dair.ai/papers/harnessmm-recursive-self-improvement-for-harness-token-efficiency-2610.32813) |
| AgentBaton | Oct 26 - Nov 1 | abstract | benchmark candidate | A detector learns when to hand a long task from a capable model to a cheaper one | Consider as a cost-policy scenario once a model and budgets exist | [page](https://academy.dair.ai/papers/agentbaton-efficient-model-collaboration-in-agentic-tasks-2610.35959) |
| WikiTrace | Nov 9 - 15 | abstract | supports | Each stored lesson links to its source run so an agent can check it before use | Nothing yet; the log already records where a page change came from | [page](https://academy.dair.ai/papers/dont-just-trust-your-memory-evidence-linked-memory-reduces-memory-induced-degrad-2611.14320) |
| ReHarness | Oct 12 - 18 | abstract | challenges | After each task, the finished run is used to revise the reflections retrieved for it | Nothing yet; decide how a revision would be recorded as a new event | [page](https://arxiv.org/abs/2610.12668) |
| 1,000 Synthetic Computers | May 4 - 10 | abstract | benchmark candidate | Synthetic user computers with realistic files host long simulated work by a user agent and a worker agent | Consider as a shared scenario seed for the harness-neutral benchmark | [page](https://arxiv.org/abs/2604.28181) |
| MerchantBench | Aug 3 - 9 | abstract | benchmark candidate | A 365-day simulated e-commerce operation that tests coherence over a long horizon | Consider as a long-horizon scenario; no action until a model is attached | [page](https://arxiv.org/abs/2607.28956) |
| OneManCompany | Apr 26 - May 3 | abstract | prior art | Organisation structure as portable agent identities recruited per task | Compare with spaces, `within` chains and patterns when read in full | [page](https://arxiv.org/abs/2604.22446) |

## Entries

Each entry says what the source says at the depth reached, which conky document it bears on, and any numbers exactly as the fetched page gave them. Every depth below is `abstract`.

### JevAct

Abstract level: LLM agents take consequential actions through tools, often with no independent check of policy or completion. JevAct is a runtime verification framework that intercepts selected actions, compiles domain policies into executable state checks and structured questions, and has a prefill-only decision model answer them, then gives feedback for bounded revision. It needs no change to the agent's model, parameters or tools. Evaluated on tau2-bench Airline and Telecom and BFCL across eleven LLM agents, with consistent gains on Telecom and BFCL and mixed results on Airline. Bears on [Rules, not requests](../essays/rules-not-requests.md) and [decision 0007](../decisions/0007-inference-for-real-thinking.md). Numbers, as reported on the page's key points and not in the abstract: Opus 4.6 success on Telecom "from 39.5% to 80.7%"; all eight agents improve by "16.9 points on average". The page notes these come from a curator summary and should be checked against the paper.

### Auton Agentic AI Framework

Abstract level: a framework for building, running and governing autonomous agents that separates a declarative, language-agnostic agent specification from a platform-specific runtime, for portability, auditability and tool integration through MCP. Also covers a formal model of execution, a memory consolidation architecture, a three-level self-evolution framework and runtime optimisations. Submitted 27 Feb 2026. Bears on [design](../design.md) and [decision 0002](../decisions/0002-git-is-the-store.md): the spec and runtime split resembles pages and the runtime, but whether it has anything like an authoritative log was not settled by the abstract. No numbers quoted.

### Runtime-Independent Persistent Agents

Abstract level: argues that a long-lived agent should be described by a persistent substrate (identity, private durable memory, versioned software body) paired with a replaceable deployment binding (reasoner, harness, host). It defines six continuity invariants and a quiesce, checkpoint, validate, bind, rehydrate, resume protocol. The authors say the evidence supports "mechanical substitutability and authorized system continuity," not behavioural invariance. Bears on [Assimilation test](../ideas/assimilation-test.md) and [decision 0014](../decisions/0014-benchmark-shape.md). Numbers, as reported: a clean-room run passes 833 core tests and 92 provider and library tests, run separately; published Sep 1, 2026.

### Filesystem Memory Audited

Abstract level: the title on arXiv is "Filesystem-Based Memory for LLM Agents: Organization, Evolution, and Sustainability". It studies agents keeping long-term memory as a directory tree of Markdown files, with management, search and execution roles. Organisation's main benefit is search cost; no measured agent turns organisation into better answers; tool choice reshapes the store as strongly as model choice. Bears on [design](../design.md), whose vault is also a directory of Markdown pages. Numbers, as reported: "organized stores roughly halve retrieval cost where material is large"; 59 pages, 12 figures, 18 tables; submitted 29 Jul 2026.

### AI-Native Design Docs

Abstract level: the arXiv title is "Design Docs Are All You Need: An AI-native Machine-Learning Performance Tool". The SMART library's main branch holds almost no code; it holds linked natural-language design documents, from which coding sub-agents regenerate the implementation. Human changes are made as edits to the documents. Reported reliability factors are worked-example docs and a minimal operator representation. The match to the index entry rests on the description (a graph of design docs, regenerated by coding sub-agents), since the index gave no link. Bears on [The log is the truth](../essays/the-log-is-the-truth.md) and [decision 0002](../decisions/0002-git-is-the-store.md): documents as source and code as projection echoes pages as projections. Numbers, as reported: regenerated implementations reproduce hand-audited reference models "to round-off precision"; submitted 4 Sep 2026.

### Skills as Verifiable Artifacts

Abstract level: argues a skill should be treated as untrusted until verified and the runtime should enforce that default. It proposes a trust schema with a verification level on each skill manifest, a capability gate whose human-in-the-loop policy depends on that level, a biconditional correctness criterion for verification procedures, and a runtime profile with ten normative guidelines. Bears on [decision 0005](../decisions/0005-rules-in-cel.md), since gating by runtime rule is the same stance. No numbers quoted beyond the ten guidelines.

### GitSwarm

Abstract level: defines "compounding inference" as organising inference-time computation so that intermediate work persists. Homogeneous agents collaborate through a shared, branchable Git repository, with atomic commits and explicit dependencies linking later work to earlier work. Bears on [decision 0002](../decisions/0002-git-is-the-store.md). Numbers, as reported on the summary page: all 30 IMOProofBench-Advanced problems solved in one run using GPT-5.5; ProgramBench mean 79.4% versus 65.1% for the strongest reported baseline; 94.7% of ProgramBench contributions later built upon; ancestry coverage 82-93% in the abstract, while the key points give 81.6% to 92.6%.

### JevAgentHarness

Abstract level: asks whether routine multiple-choice decisions, such as the next tool, can go to a fast decision model instead of a large LLM. The authors build AgentDecisionBench, and JevAgentHarness fits a confidence threshold per choice and lets the LLM decide below it. They train an open 4B model, AgentDecision-4B. Bears on [decision 0007](../decisions/0007-inference-for-real-thinking.md), [Background minds](../ideas/background-minds.md) and [Learned reactions](../ideas/learned-reactions.md). Numbers, as reported: the most accurate model on isolated questions solved 69.5% of agent tasks; delegating without a fitted threshold lowered success by 19.0 points; on unfamiliar tasks 91.5% with AgentDecision-4B and 82.0% with Jev; on tasks like the training data, cost cut by 81.1-89.0% and up to 2.5 times faster, success within 3 points.

### HarnessMM

Abstract level: harnesses often call the model again after tool feedback even when an earlier call settled the next action. HarnessMM reuses resolved decisions ("guarded decision reuse"): stored decisions run only when observed tool results meet their conditions, and unsupported cases return to the model. Bears on [Learned reactions](../ideas/learned-reactions.md) and [Things that just happen](../essays/things-that-just-happen.md). Numbers, as reported on the summary page: on HumanEval (98 tasks) Codex keeps 90.82% success while tokens per task fall from 66.72k to 47.02k (29.54%); DeepSeek Harness success rises from 71.43% to 85.71% and tokens fall from 96.28k to 11.62k (87.93%). The page notes savings depend on provider cache accounting and that authoring and recovery costs can offset avoided calls.

### AgentBaton

Abstract level: studies handing one long task between a capable model and a cheaper one mid-run. Handoffs from capable to efficient at a suitable point mostly keep or improve accuracy while cutting cost; the reverse underperforms. AgentBaton is a lightweight detector for when to hand off. Bears on [Background minds](../ideas/background-minds.md), which requires budgets for background work. Numbers, as reported: "reduces API costs by 65.9% on average while largely preserving task accuracy", gains up to 8.8 percentage points over capable-only execution, across 11 model pairs and two benchmarks; 338 ms median latency on one H100 (key points).

### WikiTrace

Abstract level: studies memory-induced degradation, where an agent fails on tasks it could solve without memory. WikiTrace links each stored lesson to a diagnosis of its source run and to the raw trajectory so the agent can check a lesson before acting; evaluated on five agentic benchmarks. Bears on [decision 0002](../decisions/0002-git-is-the-store.md), as conky's log already ties every page change to an event. Numbers, as reported in the page's key points and not checked against the paper: "10.7 points above the agent without memory on average"; "3.2 points above the same insights alone"; failure rate on previously solvable tasks from 6.5% to 4.5%.

### ReHarness

Abstract level: the arXiv title is "Recurrent Harness for Agentic Continual Learning". For agents learning from long online streams, ReHarness adds a backward step: after each instance, the resulting trajectory revises the reflections retrieved for it, under a strictly online protocol, across three continual learning benchmarks and three backbones. The match to the index entry rests on the description (backward revision of retrieved reflections), since the index gave no link. Bears on [Learned reactions](../ideas/learned-reactions.md) and [decision 0002](../decisions/0002-git-is-the-store.md), since a revision would be a new event rather than an edit. The abstract gives no numbers. Submitted 8 Oct 2026.

### 1,000 Synthetic Computers

Abstract level: the arXiv title is "Synthetic Computers at Scale for Long-Horizon Productivity Simulation". It generates synthetic user computers with realistic folder trees and business files; one agent defines work goals and another plays the user. Bears on [decision 0014](../decisions/0014-benchmark-shape.md), which wants harness-neutral scenarios. Numbers, as reported: "1,000 synthetic computers", simulations of "over 8 hours of agent runtime" and "more than 2,000 turns on average"; gains on in-domain and out-of-domain productivity benchmarks are reported without figures in the abstract.

### MerchantBench

Abstract level: the arXiv title is "MerchantBench: Benchmarking LLM Agents for Long-Term Coherence in E-Commerce Operations". A seller-side e-commerce simulation covering sourcing, listing and pricing, cash flow and feedback adaptation, with delayed order outcomes. Bears on [decision 0014](../decisions/0014-benchmark-shape.md) and [Direction and drift](../ideas/direction-and-drift.md). Numbers, as reported: 365 simulated days, 98,843 real product records, 26 tools, eight LLMs under two agent frameworks across 48 runs; the best configuration reached 27.3% of the mean final net assets of human participants.

### OneManCompany

Abstract level: the arXiv title is "From Skills to Talent: Organising Heterogeneous Agents as a Real-World Company". It argues multi-agent systems lack an organisational layer and packages skills, tools and runtime configurations into portable agent identities called Talents, recruited on demand from a Talent Market, with an Explore-Execute-Review tree search. Bears on [Patterns](../ideas/patterns.md) and the `within` chains in the [design](../design.md). Numbers, as reported: 84.67% success rate on PRDBench, which the authors report as 15.48 percentage points above the prior state of the art.

## How this register is kept

- New papers are added when the weekly watch of the DAIR.AI list finds relevant ones. Each starts at `listed`.
- An entry's depth only goes up when someone has actually read further. Fetching an abstract page earns `abstract`; reading the paper earns `read`. A depth is never raised on the strength of a summary.
- An entry that changes a decision links to that decision, and the decision links back here.
- Numbers are copied as the source gave them, with "as reported", and are not restated from memory.
- A test in `tests/test_docs.py` fails if any row of the register table has a depth other than `listed`, `abstract` or `read`.
