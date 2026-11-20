---
kind: research
title: "Benchmarks and evaluations for agent harnesses"
status: current
date: 2026-11-20
source: "each benchmark's own paper or site, fetched 2026-11-20"
---

# Benchmarks and evaluations for agent harnesses

## How to read this

Every page listed under [Sources](#sources) was fetched on 2026-11-20. Search was used to find candidates; no claim below rests on a search result alone. Pages were read through a fetch tool that returns a condensed reading, so wording is paraphrased and only short phrases are quoted. Numbers are given "as reported" by the page, and none is restated from memory or checked against the full paper. Most pages are arXiv abstract pages, which carry less detail than the papers.

"Not confirmed" means the page read did not settle the question. It does not mean the answer is no. In the map, an empty finding on cost, variance or code release is written "not confirmed" for that reason.

The sources use several words for the software around a model (framework, agent product and others). This document uses "harness" throughout and keeps the source's own term only where a title requires it.

Twenty-nine sources were read: twenty-four benchmarks or leaderboards (the map) and five papers on evaluation method (see [Methodology worth adopting](#methodology-worth-adopting)). Every address in Sources was reached. Some sites named by the papers (for example the SWE-bench and OSWorld project sites) were not fetched, and their contents are not claimed here.

conky has no results, so nothing here says how it would score. The plan for gathering evidence is [Evaluation plan](evaluation-plan.md).

## A taxonomy

| Unit under test | Held fixed | Scored | Examples in the map |
|---|---|---|---|
| Model | Harness, tools, task set | Task success | SWE-bench, OSWorld, METR time horizon |
| Model and harness together | Task set; often nothing else | Task success, sometimes cost | Terminal-Bench, tau2-bench, AutoLab, Vending-Bench |
| Harness | Model, tools, task set, budget | Task success, cost, resume behaviour | No entry read isolates the harness this way; HAL varies model, harness and benchmark together |
| Whole system over time | Starting state, then the system runs on | Reliability or coherence across sessions or simulated days | MerchantBench, E-Commerce Bench, AgingBench |
| Substitution of a part | State carried across a swap of model, harness or host | Whether state and tasks continue | Runtime-Independent Persistent Agents |
| Evaluation method | Not applicable | Properties of the evaluation, such as ranking stability or judge agreement | Efficient Benchmarking, Universal Verifier |

## The map

Horizon is stated as the source states it. "Resume" means the benchmark tests continuing work from stored state. Cost and variance columns say whether the page read reports them. "Open" is yes, partly, no or not confirmed, judged from the page read.

| Name | What it measures | Unit under test | Horizon | Resume or handoff | Cost reported | Variance over runs | Open and runnable | Link |
|---|---|---|---|---|---|---|---|---|
| SWE-bench | Resolving real GitHub issues by editing a codebase | Model | Single task | No | Not confirmed | Not confirmed | Yes (data, code, leaderboard stated at swebench.com) | [arXiv 2310.06770](https://arxiv.org/abs/2310.06770) |
| SWE-EVO | Long-horizon software evolution from release notes | Model and harness (headline uses GPT-5.4 with OpenHands) | Single task, multi-file | No | Not confirmed | Not confirmed | Not confirmed | [arXiv 2512.18470](https://arxiv.org/abs/2512.18470) |
| Terminal-Bench | Hard terminal tasks with tests | Model and agent pairs | Single task | No | Yes on the site (cost and tokens columns) | Yes on the site (95% intervals shown) | Yes (dataset and harness stated in abstract) | [arXiv 2601.11868](https://arxiv.org/abs/2601.11868), [site](https://www.tbench.ai/) |
| LongCLI-Bench | Long command-line programming tasks, with step-level scoring | Agent | Single task, long | No | Not confirmed | Not confirmed | Not confirmed | [arXiv 2602.14337](https://arxiv.org/abs/2602.14337) |
| PRDBench | Project-level code generation from requirement documents, judged by a model | Code agent | Single task, project | No | Not confirmed | Not confirmed | Not confirmed | [arXiv 2510.24358](https://arxiv.org/abs/2510.24358) |
| OSWorld | Open-ended computer tasks in real environments | Model-based agent | Single task | No | Not confirmed | Not confirmed | Yes (stated at os-world.github.io) | [arXiv 2404.07972](https://arxiv.org/abs/2404.07972) |
| AutoLab | Iterative improvement of a baseline within a wall-clock budget | Model as agent | Single task, budgeted; length not stated | No | Not confirmed | Not confirmed | Yes (benchmark, harness, tasks open-sourced) | [arXiv 2606.05080](https://arxiv.org/abs/2606.05080) |
| tau-bench | Tool-agent-user conversations, scored by final database state | Agent | Single conversation | No | Not confirmed | Yes by design (pass^k over trials) | Not confirmed | [arXiv 2406.12045](https://arxiv.org/abs/2406.12045) |
| tau2-bench | Dual-control conversations where agent and simulated user both act | Agent and user simulator | Single conversation | No | Not confirmed | Partly (a trials option in the repository; reporting not confirmed) | Yes (repository, frozen task sets, leaderboard) | [arXiv 2506.07982](https://arxiv.org/abs/2506.07982), [repository](https://github.com/sierra-research/tau2-bench) |
| Gaia2 | Agents in environments that change on their own | LLM agent | Not confirmed | No | Not confirmed (cost mentioned only in words) | Not confirmed | Partly (released with an open platform; no link on the page) | [arXiv 2602.11964](https://arxiv.org/abs/2602.11964) |
| AlphaEval | Tasks from seven companies, scored several ways | Complete agent products | Not confirmed | No | Not confirmed | Not confirmed | Not confirmed | [arXiv 2604.12162](https://arxiv.org/abs/2604.12162) |
| Agents' Last Exam | Economically valuable long-horizon work, living task pool | Harness and backbone configurations | Long horizon; length not stated | No | Not confirmed | Not confirmed | Yes (repository and site listed) | [arXiv 2606.05405](https://arxiv.org/abs/2606.05405) |
| Vending-Bench | Running a simulated vending business | LLM agent | Over 20M tokens per run | Not confirmed | Not confirmed | Described in words: runs differ, all models have runs that derail | Not confirmed | [arXiv 2502.15840](https://arxiv.org/abs/2502.15840) |
| MerchantBench | Coherence across a simulated e-commerce year | Eight LLMs under two agent frameworks | 365 simulated days | Not confirmed | Not confirmed | Not confirmed (48 runs) | Not confirmed | [arXiv 2607.28956](https://arxiv.org/abs/2607.28956) |
| E-Commerce Bench | Autonomous operation of several online stores, seven dimensions | 18 frontier models in an agent loop | 365 simulated days | Partly (the loop layer keeps persistent memory; no handoff test stated) | Not confirmed | Not confirmed | Yes (repository stated) | [paper summary](https://academy.dair.ai/papers/e-commerce-bench-evaluating-llm-agents-on-long-horizon-autonomous-business-opera-2608.30730) |
| 1,000 Synthetic Computers | Long simulated productivity work on synthetic user computers | The agent acting as user | Over 8 hours of runtime, 2,000+ turns on average | Not confirmed | Not confirmed | Not confirmed | Not confirmed | [arXiv 2604.28181](https://arxiv.org/abs/2604.28181) |
| VERA | Verifiable, restartable environments for long-horizon agents | Model and agent together | Long-horizon; length not stated | Partly (sandboxes are restartable; mechanism not described) | Not confirmed | Not confirmed | Partly (open corpus stated; repository not named) | [paper summary](https://academy.dair.ai/papers/vera-scaling-verifiable-environments-for-agentic-co-evolution-2610.05923) |
| LoCoMo | Long-term conversational memory by question answering | Models with long context or retrieval | Up to 35 sessions per conversation | No (memory across sessions, not resume) | Not confirmed | Not confirmed | Not confirmed (project page named) | [arXiv 2402.17753](https://arxiv.org/abs/2402.17753) |
| LongMemEval | Five long-term memory abilities of chat assistants | Chat assistants with memory | Sustained histories; counts not on the abstract page | No (memory across sessions, not resume) | Not confirmed | Not confirmed | Yes (repository stated) | [arXiv 2410.10813](https://arxiv.org/abs/2410.10813) |
| Retrieval vs utilization study | Where agent memory fails, on LoCoMo | Write strategy and retrieval method | Not confirmed | No | Qualitative only (raw storage needs no model calls) | Not confirmed | Yes (repository stated) | [arXiv 2603.02473](https://arxiv.org/abs/2603.02473) |
| AgingBench | Reliability of deployed agents over many sessions | Full harness including its memory pipeline | 50 to 200 sessions | Partly (state accumulates across sessions; no swap of consumer) | Not confirmed | Not confirmed (400 runs) | Not confirmed | [arXiv 2605.26302](https://arxiv.org/abs/2605.26302) |
| Runtime-Independent Persistent Agents | Whether identity, memory and code survive a swap of model, harness or host | A persistent agent and its substitutions | Bounded workflows | Yes (quiesce, checkpoint, validate, bind, rehydrate, resume) | Not confirmed | Partly (five round trips with five same-runtime controls) | Not confirmed | [arXiv 2609.00546](https://arxiv.org/abs/2609.00546) |
| METR time horizon | Task length, in human time, that a model completes at 50% | Model | Single task, human-timed | No | Not confirmed | Not confirmed | Not confirmed | [arXiv 2503.14499](https://arxiv.org/abs/2503.14499) |
| Holistic Agent Leaderboard | Cross-benchmark leaderboard, reports accuracy against cost | Model, harness and benchmark combinations | Per benchmark | No | Yes | Not confirmed | Yes (standardised harness; logs published) | [arXiv 2510.11977](https://arxiv.org/abs/2510.11977), [site](https://hal.cs.princeton.edu/about) |

## Notes per benchmark

**SWE-bench.** Poses 2,294 problems drawn from GitHub issues and pull requests across 12 Python repositories. As reported, the best model at the time, Claude 2, resolved 1.96% of issues. The paper is from October 2023. Its unit is the model given a codebase and an issue.

**SWE-EVO.** Forty-eight tasks built from release notes of seven open-source Python projects, averaging 21 files and a test suite of 874 tests. It adds a partial-progress metric, Fix Rate. As reported, GPT-5.4 with OpenHands reaches 25%, against 72.80% for GPT-5.2 on SWE-Bench Verified. The harness is named in the headline result, but no comparison across harnesses is stated.

**Terminal-Bench.** The arXiv page describes 89 tasks, each with its own environment, a human-written solution and tests, and reports that frontier models and agents score "less than 65%". The site read on the same day lists a newer version, 4.1, as a leaderboard of model and agent pairs (Claude Code, Codex, mini-swe-agent and others) with columns for tokens and cost and 95% confidence intervals. The paper and the site describe different versions, so the 65% figure belongs to 2.0 only. How runs are submitted was not stated on the site page read.

**LongCLI-Bench.** Twenty long tasks from over 1,000 computer science assignments and real workflows, in four categories (from scratch, feature addition, bug fixing, refactoring). It scores requirement fulfilment, regression avoidance and individual steps. As reported, pass rates are below 20% and most tasks stall at under 30% completion.

**PRDBench.** Fifty Python projects across 20 domains, each with a structured requirements document and criteria, scored by a judge model, PRDJudge, built on Qwen3-Coder-30B. As reported, the judge reaches "over 90% human alignment in fixed-interface scenarios." The research index cites 84.67% on PRDBench for another paper, OneManCompany; that figure was not checked here.

**OSWorld.** Three hundred and sixty-nine computer tasks with execution-based checks and an initial-state configuration per task. As reported, humans accomplish over 72.36% and the best model in the paper 12.24%.

**AutoLab.** Thirty-six tasks in four domains (system optimisation, puzzles, model development, CUDA kernels), 17 models, iterative improvement of a correct but slow baseline under a wall-clock budget. The authors report that persistence in measuring, editing and using feedback predicts success, and that most models stop early or exhaust the budget with little progress.

**tau-bench.** Agents hold simulated conversations with a user while using domain tools and following policy; success compares the final database state with an annotated goal. It introduces pass^k as a measure of reliability over multiple trials. As reported, agents succeed on under 50% of tasks and pass^8 is under 25% in retail. The page gives no formula for pass^k.

**tau2-bench.** Adds a telecom domain in which agent and simulated user both act on a shared system, so that errors in reasoning can be separated from errors in coordination. The abstract reports no figures. The repository lists domains (airline, retail, telecom, banking knowledge, intake), states that task sets are frozen so runs compare, and exposes a trials option. The repository README does not mention pass^k.

**Gaia2.** Scenarios in which the environment changes independently of the agent, with a write-action verifier for action-level scoring. As reported, GPT-5 (high) reaches 42% pass@1 and fails on time-sensitive tasks; Kimi-K2 leads open models at 21%.

**AlphaEval.** Ninety-four tasks from seven companies deploying agents, in six occupational domains, scored by several methods (model judge, reference metrics, formal verification, rubrics, interface testing). Its unit is the complete agent product, such as Claude Code or Codex, evaluated "as commercial systems" and not as models.

**Agents' Last Exam.** A living benchmark of over 1,000 tasks in 55 sub-fields across 13 industry clusters, built with over 250 industry experts, whose task pool grows. As reported, the average full pass rate on the hardest tier is below 1%. It is evaluated across harness and backbone configurations, which are not defined on the page.

**Vending-Bench.** An agent runs a simulated vending business over more than 20M tokens per run. The abstract states that all models have runs that derail, for example by forgetting orders or looping, even where most runs turn a profit. This is the only entry whose abstract describes run-to-run variation as a finding.

**MerchantBench.** A seller-side e-commerce simulation over 365 simulated days with 98,843 real product records and 26 tools. As reported, eight models under two agent frameworks over 48 runs, with the best configuration at 27.3% of the mean final net assets of human participants. Variance and cost are not stated on the page read.

**E-Commerce Bench.** A 365-day simulation in which an agent manages several stores, negotiates with suppliers and faces shocks such as supplier bankruptcy. Seven dimensions are scored, including year-end assets and fraud avoidance. Both market sides are deterministic for reproducibility. As reported, 18 frontier models were run; one grew a stake of 100,000 into 1,431,425 while ranking 16th of 18 on fraud avoidance. The page read is a summary, not the paper.

**1,000 Synthetic Computers.** Generates synthetic user computers with realistic folders and files, on which one agent defines goals and another acts as the user. As reported, runs take over 8 hours and average over 2,000 turns, with goals that need about a month of human work. The paper calls itself a preview; the abstract gives no metric values.

**VERA.** Turns trajectories into over 9,000 restartable sandboxes, each with rubrics and executable checks verified by a judge, and reports results on two benchmarks (AutoCoWorkBench, AutoMedBench). The restart mechanism is not described on the page read.

**LoCoMo.** Conversations of about 300 turns and 9K tokens over up to 35 sessions, with question answering, event summarisation and dialogue generation. It tests recall across sessions, not continuing work.

**LongMemEval.** Five abilities (information extraction, multi-session reasoning, temporal reasoning, knowledge updates, abstention) over 500 curated questions. As reported, "a 30% accuracy drop on memorizing information across sustained interactions".

**Retrieval vs utilization study.** A three-by-three grid of memory write strategies and retrieval methods on LoCoMo. As reported, accuracy spans 57.1% to 77.2% across retrieval methods and only 3 to 8 points across write strategies. Raw chunked storage is stated to need no model calls.

**AgingBench.** Tracks reliability after deployment through 6 scenarios, 10 memory systems and 6 models from two families, over 400 runs of 50 to 200 sessions. It classes degradation into four mechanisms (compression, interference, revision, maintenance). The unit is the whole harness including its memory pipeline.

**Runtime-Independent Persistent Agents.** Proposes a persistent substrate (identity, durable memory, versioned code) separate from a replaceable binding (model, harness, host), six continuity invariants and a six-step handoff. Tested cases: an agent kept identity, memory, code revision and task identifiers across a host change, a Codex to Claude model and harness change, and a chat-surface change; a task resumed from a verified checkpoint on another host; five round trips against five same-runtime controls; and recovery from a planned interruption. The authors state the evidence shows "mechanical continuity for the tested deployments and bounded workflows" and does not establish behavioural equivalence. The DAIR.AI summary page adds one clean-room run passing 833 core tests and 92 provider and library tests. Code location was not confirmed from either page.

**METR time horizon.** A metric defined as the human time taken by tasks that a model completes with 50% success. As reported, about 50 minutes for Claude 3.7 Sonnet, with the horizon doubling roughly every seven months since 2019. The latest revision on the page is dated 10 July 2026.

**HAL.** A standardised harness run in parallel across hundreds of virtual machines, reporting accuracy together with cost. As reported, 21,730 rollouts across 9 models and 9 benchmarks for about $40,000, with all agent logs (2.5B tokens) published, and a finding that higher reasoning effort reduced accuracy in most runs. The site page states that the harness needs no change to agent code and that cost-controlled evaluation is the default. What is held fixed was not stated on either page.

## Closest to the assimilation test

The [assimilation test](../ideas/assimilation-test.md) hands a fresh consumer only a stopped system's stored state and scores whether it resumes correctly. No entry read does exactly this. Four come near, each on a different side.

- **Runtime-Independent Persistent Agents** is the only entry that tests continuing from stored state after a swap of the part that runs the system. It checks that state (identity, memory, code lineage, task identifiers) is preserved and that a task resumes from a verified checkpoint, and it compares round trips with same-runtime controls. It leaves behavioural invariance open. This split between state continuity and behavioural continuity is the one the assimilation test needs to score separately. Its stored state is the agent's own substrate, not a vault read by an unrelated consumer.
- **AgingBench** keeps one system running across 50 to 200 sessions and measures how reliability changes as state accumulates. The same system continues; no new consumer is handed the state.
- **VERA** builds environments that can be restarted at a stage and scored from observable evidence. This resembles starting from stored state, but the page does not describe the mechanism, and the purpose is training data, not testing a consumer.
- **LoCoMo and LongMemEval** test whether facts from earlier sessions are recalled. They test retrieval from history, not continuation of unfinished work.

E-Commerce Bench and MerchantBench keep one simulated business going for a year, and the first states that its loop layer holds persistent memory. Neither page read describes stopping and handing the state to another consumer.

## Gaps

These are observations about the 24 entries read, not claims about the whole field.

- No entry read isolates the harness while holding model, prompt, tools and budget fixed and varying only the harness. HAL varies model, harness and benchmark together, and its page does not say what is held fixed.
- No entry read tests resuming from a stored state by a different harness or a fresh instance and scores state and behaviour separately, apart from the persistent-agents paper, whose behavioural question is explicitly open.
- Among the long-horizon simulations (MerchantBench, E-Commerce Bench, 1,000 Synthetic Computers, Vending-Bench), the pages read do not report cost, and only Vending-Bench describes variation across runs.
- Which stored artefact counts as "the state", and whether a person can read it, is not a variable in any entry read.
- No entry read reports refused or invalid actions as a measure, or checks that a rule held on every write.
- Terminal-Bench is the only entry whose page showed both cost and confidence intervals.

## Methodology worth adopting

Each practice below is stated by the source named. None has been tried in this project.

- **Report cost beside accuracy.** *AI Agents That Matter* argues that a narrow focus on accuracy has made agents needlessly complex and costly and proposes optimising cost and accuracy jointly ([arXiv 2407.01502](https://arxiv.org/abs/2407.01502)). HAL reports accuracy against cost by default ([site](https://hal.cs.princeton.edu/about)). Terminal-Bench shows cost and tokens per entry ([site](https://www.tbench.ai/)).
- **Report uncertainty.** Terminal-Bench shows 95% confidence intervals ([site](https://www.tbench.ai/)). tau-bench defines pass^k to measure reliability over repeated trials ([arXiv 2406.12045](https://arxiv.org/abs/2406.12045)). Vending-Bench reports that every model has derailing runs ([arXiv 2502.15840](https://arxiv.org/abs/2502.15840)).
- **Standardise the harness and release traces.** HAL runs one standardised harness and publishes all agent logs ([arXiv 2510.11977](https://arxiv.org/abs/2510.11977)).
- **Use holdout tasks.** *AI Agents That Matter* reports that many agent benchmarks have inadequate or no holdout sets, which produces agents that overfit, and prescribes a framework against it ([arXiv 2407.01502](https://arxiv.org/abs/2407.01502)).
- **Check for contamination.** A study of SWE-Bench-Verified gave two models incomplete input and compared results with two other datasets; as reported, models did "3 times better" on SWE-Bench-Verified and "6 times better" at finding edited files, which the authors read as possible training exposure ([arXiv 2512.10218](https://arxiv.org/abs/2512.10218)). Agents' Last Exam grows its task pool continuously ([arXiv 2606.05405](https://arxiv.org/abs/2606.05405)).
- **Freeze task sets and name the user simulator.** tau2-bench freezes task sets so that runs compare and records the user simulator per domain ([repository](https://github.com/sierra-research/tau2-bench)).
- **Attribute failures to model or harness.** *Model or Harness* proposes a taxonomy of 41 failure modes that assigns each failure to an interaction and a fault side (model, harness, environment or grader), and reports independent judges reaching Cohen's kappa 0.76 against human labels at best ([arXiv 2607.28802](https://arxiv.org/abs/2607.28802)).
- **Validate any model used as a judge.** The Universal Verifier for computer-use trajectories is checked against human labels, and the authors report agreement with humans as often as humans agree with each other ([arXiv 2604.06240](https://arxiv.org/abs/2604.06240)). PRDBench reports judge alignment with humans ([arXiv 2510.24358](https://arxiv.org/abs/2510.24358)).
- **Reduce evaluation cost by selecting tasks.** Efficient Benchmarking keeps tasks with historical pass rates of 30 to 70%, cutting the number of tasks by 44 to 70% across eight benchmarks, 33 agent harnesses and over 70 model configurations, while rankings hold under harness and time shifts, as reported ([arXiv 2603.23749](https://arxiv.org/abs/2603.23749)).
- **Separate state continuity from behavioural continuity.** The persistent-agents paper claims only the first ([arXiv 2609.00546](https://arxiv.org/abs/2609.00546)).
- **Fix the model when comparing harnesses.** Not found stated as a practice in a page read; the persistent-agents study uses same-runtime controls, which serves a related purpose.

## Sources

All fetched 2026-11-20. Search queries were used for discovery only.

- https://arxiv.org/abs/2310.06770
- https://arxiv.org/abs/2512.18470
- https://arxiv.org/abs/2601.11868
- https://www.tbench.ai/
- https://arxiv.org/abs/2602.14337
- https://arxiv.org/abs/2510.24358
- https://arxiv.org/abs/2404.07972
- https://arxiv.org/abs/2606.05080
- https://arxiv.org/abs/2406.12045
- https://arxiv.org/abs/2506.07982
- https://github.com/sierra-research/tau2-bench
- https://arxiv.org/abs/2602.11964
- https://arxiv.org/abs/2604.12162
- https://arxiv.org/abs/2606.05405
- https://arxiv.org/abs/2502.15840
- https://arxiv.org/abs/2607.28956
- https://academy.dair.ai/papers/e-commerce-bench-evaluating-llm-agents-on-long-horizon-autonomous-business-opera-2608.30730
- https://arxiv.org/abs/2604.28181
- https://academy.dair.ai/papers/vera-scaling-verifiable-environments-for-agentic-co-evolution-2610.05923
- https://arxiv.org/abs/2402.17753
- https://arxiv.org/abs/2410.10813
- https://arxiv.org/abs/2603.02473
- https://arxiv.org/abs/2605.26302
- https://arxiv.org/abs/2609.00546
- https://academy.dair.ai/papers/runtime-independent-persistent-agents-preserving-identity-memory-and-code-across-2609.00546
- https://arxiv.org/abs/2503.14499
- https://arxiv.org/abs/2510.11977
- https://hal.cs.princeton.edu/about
- https://arxiv.org/abs/2607.28802
- https://arxiv.org/abs/2407.01502
- https://arxiv.org/abs/2603.23749
- https://arxiv.org/abs/2604.06240
- https://arxiv.org/abs/2512.10218

Related project documents: [Paper register](papers.md), [Agent harnesses compared](harnesses.md), [DAIR.AI index](dair-2026.md), [decision 0014](../decisions/0014-benchmark-shape.md).
