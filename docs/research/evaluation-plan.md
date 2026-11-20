---
kind: research
title: "Evaluation plan"
status: draft
date: 2026-11-20
source: maintainers
---

# Evaluation plan

Nothing in this plan has been run. conky has no benchmark results, and model pages have been tested only against stand-in servers on the local machine, with no live provider called ([status](../project/status.md)) ([decision 0013](../decisions/0013-evidence-not-scripts.md), [decision 0014](../decisions/0014-benchmark-shape.md)). The plan is written so that an outside reviewer can criticise it before any run. Outside benchmarks are described in [Benchmarks and evaluations for agent harnesses](benchmarks.md), and the harnesses in [Agent harnesses compared](harnesses.md).

## Principle

Evidence is gathered in the cheapest order first. Each step is decided in writing before it is run, and each result is labelled with what it can and cannot support. A step is run only if the one before it was informative.

## Three kinds of result, kept apart

Every reported result carries exactly one class.

- **Mechanism result.** A property of conky itself that involves no model. Examples: a vault copied elsewhere verifies; a write that breaks a rule is refused and recorded; replaying history gives the same pages. The outcome is deterministic, pass or fail, and attributable to conky alone.
- **Harness result.** The same task, the same model and version, the same task prompt and the same budget, run through different harnesses. A difference is attributable to the harness, within the stated variance.
- **Prompt result.** The same harness and model with different prompts. A difference is attributable to the prompt. It is never reported as a property of conky.

The rule: a claim about conky may cite only mechanism and harness results. A prompt result may guide how conky's prompts are written. It may not appear in a claim about conky.

### The record

Every run stores the following, so that the class of a result can be checked afterwards.

| Field | Content |
|---|---|
| Harness | Name and version |
| Model | Name, version and provider |
| Prompt set | Identifier and content hash |
| Scenario | Identifier and version |
| Seed | Where the harness or scenario accepts one |
| Budget | Tokens and wall time |
| Start state | Hash |
| Trace | Complete, as produced by the harness |
| Class | Mechanism, harness or prompt |

Prompts live in one versioned prompt set shared by all harnesses. Any prompt text a harness adds on its own, such as system prompts and tool descriptions, is recorded and reported as part of that harness, not as part of the prompt set.

### Confounds

| Confound | How it is handled |
|---|---|
| Model | Held fixed: same name and version for every harness in a comparison; version and date recorded |
| Prompt | Held fixed from the shared prompt set; harness-added text recorded and reported with the harness |
| Tools | Held fixed in effect: tools are described neutrally in the scenario, and each adapter maps them with the least change; differences are recorded |
| Budget | Held fixed in tokens and wall time; overruns recorded |
| Scenario wording | Held fixed; scenario version recorded; wording changes make a new version and a new comparison |
| Randomness | Measured: repeated runs, with the number set before the run and uncertainty reported |

## Steps, cheapest first

### Step 0: mechanism checks, no model

- Aim: to find out whether the documented properties of conky hold.
- Run: the existing test suite and `conky verify` over fixture vaults. Properties to list and check: the log is signed and hash-chained; `verify` accepts an untouched vault and rejects a tampered one; `rebuild` reproduces every page byte for byte; a write that breaks a rule is refused and a `refused` event is recorded; the reaction depth limit holds. Which of these the suite already covers is checked and written down before the step is recorded.
- Cost class: none.
- Pass: every property holds, and for each rule or check a test fails when it is removed ([decision 0013](../decisions/0013-evidence-not-scripts.md)).
- Cannot show: anything about models, other harnesses, or whether a consumer can use the vault.

### Step 1: the resume test, mechanical form, no model

- Aim: to find out whether a stopped vault carries its whole state.
- Run: stop a running system, copy the vault by clone or bundle to another location, run `verify` and `rebuild`, continue with further writes, and compare state. Equality is defined before the run as identical pages and identical log head after the same sequence of writes.
- Cost class: none.
- Status: the clone, check and carry-on part now exists as the command `conky assimilate` ([reference](../reference/cli.md#assimilate)). It is a mechanism result. The comparison of identical pages and log heads after the same sequence of writes is not part of the command.
- Informative result: equality holds, or the first difference is located.
- Cannot show: that anything other than conky's own commands can resume. This is the mechanical half of the [assimilation test](../ideas/assimilation-test.md).

### Step 2: one cheap model, conky only

- Aim: to find out whether model pages behave as designed with a live provider ([pages that ask a model](../ideas/model-pages.md)), which so far have been tested only against stand-in servers.
- Run: small tasks with a known right answer. Checks: each answer is recorded with the question that caused it; rules apply to answers like any other write; a settled question is not asked twice; with the provider unreachable, everything that needs no model still works.
- Cost class: cents.
- Pass: every check holds on every run; failures are listed with their traces.
- Cannot show: that conky is better than anything else, or that answers are correct beyond the small tasks used. These are mechanism results where no model judgement is involved, and prompt results where the answer quality is.

### Step 3: first harness result

- Aim: to find out how the same model does through different harnesses on one small scenario with a known ground truth.
- Run: one model, two or three harnesses chosen from [harnesses.md](harnesses.md) before the run, repeated runs of the same scenario. The scenario is kept small enough to rerun often.
- Cost class: dollars. The count of runs and the price per run are set before the run from the provider's published prices at that date.
- Informative result: success rates with intervals that do or do not overlap, and a classified list of failures.
- Cannot show: behaviour on longer horizons, or any result for harnesses not run. A small scenario may favour whichever harness fits it.

### Step 4: the resume test with a model

- Aim: to find out whether a fresh instance, handed only the stored state, can continue a task that was stopped midway.
- Run: a system is stopped mid-task and a fresh instance of each harness is handed only the stored state: for conky the vault, for the others whatever state the harness's own documentation says carries a run (a session store, a checkpoint, a memory directory). Two scores are kept apart: state continuity (the stored state, identity, memory and task identifiers survive and verify) and behavioural continuity (the task is completed correctly from where it stopped). The persistent-agents paper makes this distinction and claims only the first ([paper register](papers.md), [arXiv 2609.00546](https://arxiv.org/abs/2609.00546)). Same-runtime controls, a system stopped and resumed by the same harness, are run alongside, as that paper does.
- Cost class: dollars to tens of dollars.
- Informative result: state continuity and behavioural continuity reported separately, each with a control.
- Cannot show: continuity over days, or resume by harnesses whose stored state could not be located from their documentation (recorded as "not run, with reason").

### Step 5: a longer scenario

- Aim: to find out how conky behaves over a long horizon, beside published numbers.
- Run: preferably an existing benchmark from [Document 1](benchmarks.md), not a new invention, so results sit beside published ones. Candidates, with what each offers and what would decide:
  - E-Commerce Bench: a 365-day simulation, deterministic market sides, repository stated; reports 18 models. Not confirmed: cost, variance.
  - MerchantBench: a 365-day simulation with 48 runs reported across eight models and two frameworks; code release not confirmed.
  - Terminal-Bench: tasks suit a harness that works through files; its site reports cost, tokens and 95% intervals per entry, so results could sit beside published rows. Single tasks, not long horizons.
  - tau2-bench: frozen task sets and a trials option; single conversations.
  - AgingBench: multi-session reliability of a whole harness; code release not confirmed.
- Deciding points: the scenario can be run and scored from released material; the scoring needs no judge model, or the judge is validated; one run is affordable at the budget set; published results exist for the same model; the task can be expressed as harness-neutral documents.
- Cost class: tens of dollars at least; set a ceiling before choosing.
- Cannot show: anything about scenarios not run. If no candidate meets the deciding points, the step is not run.

## The comparison harness

A scenario is a set of documents: the starting state, the task prompt taken from the shared prompt set, tools described neutrally, observables, and scoring. An adapter per harness maps those documents onto that harness with as little added as possible. Whatever an adapter adds is recorded and reported as part of the harness.

Candidate harnesses are taken from [harnesses.md](harnesses.md): LangGraph, CrewAI, the OpenAI Agents SDK, the Claude Agent SDK, Letta, Microsoft Agent Framework, AG2 and Temporal as a durable layer. The ones used are chosen and listed before Step 3. Selection depends on whether the documentation describes resume from stored state and whether the harness can call the chosen model.

Fairness rules:

- Same model and version for every harness in a comparison.
- Same budget in tokens and wall time.
- Same tools, described neutrally.
- Same number of runs.
- Each adapter is reviewed by someone familiar with that harness where possible; where not, the adapter is marked unreviewed.
- Each harness runs in the configuration its maintainers recommend, with the page cited in the run record. Where the maintainers' documentation gives no recommendation, the default is used and recorded.

## Measures

Quantitative:

- Task success against ground truth.
- State continuity after resume (Step 4).
- Refused or invalid actions, counted where the harness records them.
- Model calls and tokens per unit of work.
- Wall time.
- Variance across runs.

Qualitative, for example readability of the stored state to a newcomer, effort to resume, and kinds of failure:

- A fixed rubric written before the run.
- A coding scheme with examples.
- At least two independent raters, with agreement reported.
- Blind rating where possible; stored state is stripped of harness names when it can be.
- A model may act as a rater only alongside a person, and its agreement with the person is reported. A model-only rating is not reported as a result.

## Analysis and reporting

Decided before running, and written into the run record:

- Hypotheses.
- The primary measure.
- The number of runs.
- How uncertainty is reported: intervals, not single numbers.
- What would count against conky.

Negative and null results are published. Raw traces and the exact prompt set are released with any result. A results page carries its class (mechanism, harness or prompt) in its heading.

## Threats to validity

- **Adapter bias.** The authors know conky best, so its adapter may be better tuned than the others. Mitigation: adapter review, recorded additions, maintainers' recommended configurations.
- **Prompt leakage between classes.** A prompt tuned on conky results may then be used in a harness comparison. Mitigation: a versioned prompt set frozen before a comparison; tuning runs labelled as prompt results and kept out of claims.
- **Benchmark overfitting.** Repeated reruns of one scenario invite tuning to it. Mitigation: held-out scenarios, as argued in [AI Agents That Matter](https://arxiv.org/abs/2407.01502).
- **Model nondeterminism and version drift.** The same model name may change behaviour between dates. Mitigation: record version and date, run compared arms close in time, repeat runs.
- **Small samples.** Few runs give wide intervals. Mitigation: report intervals, and state when intervals overlap.
- **Scripted or cherry-picked runs.** A scripted run looks like a measurement ([decision 0013](../decisions/0013-evidence-not-scripts.md)). Mitigation: unscripted runs only, with every run kept and the count stated.
- **Contamination.** A model may have seen a published benchmark, as one study reports for SWE-Bench-Verified ([arXiv 2512.10218](https://arxiv.org/abs/2512.10218)). Mitigation: prefer private or newly written scenarios for claims, and note the risk beside any published benchmark used.
- **Judge error.** A model judge can disagree with people. Mitigation: validate against human labels, as the sources in Document 1 do.

## What is not claimed

conky has no results. Nothing in this plan is evidence that it performs better or worse than any harness, and nothing in it has been run. The outside figures cited are quoted as reported in the sources listed in [Benchmarks and evaluations for agent harnesses](benchmarks.md) and have not been reproduced.
