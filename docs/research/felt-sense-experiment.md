---
kind: research
title: "Felt-sense experiment: does placing a magnitude help a model"
status: draft
date: 2026-11-20
source: maintainers
---

# Felt-sense experiment: does placing a magnitude help a model

This protocol is fixed before any run. No model has been called for it and it has no results. It tests the hypothesis in [a felt sense of magnitude](../ideas/felt-sense.md), which the [source digest](where-am-i.md) does not demonstrate. It is a prompt-class result under the [evaluation plan](evaluation-plan.md): it says whether one way of presenting a magnitude helps a model, and is never a claim about Conky as a harness.

## Question and hypotheses

The question is whether a model decides better when a magnitude is placed among familiar anchors than when it is given a raw number and a unit.

- **H0, the null.** Placing a magnitude among familiar anchors changes nothing compared with a raw number and unit.
- **H1.** Familiar anchors raise accuracy against ground truth.
- **H2.** Part of any gain comes from the structure of an anchored scale and part from the meaning of the anchor names. The source says it never ran the control that separates them, opaque names with the same structure, and this experiment runs it.
- **H3.** Giving the placement and the raw number together is at least as good as either alone.
- **H4.** Any placement misleads beyond the last anchor, at the ends of the scale.

H1 is the primary hypothesis.

## Conditions

One model, one task set, one prompt wrapper, one setting of every parameter. Only the rendering of each magnitude differs. The task sentences contain no unit words, so the unit of a magnitude comes only from its rendering.

| Condition | A magnitude of 259200 seconds is shown as |
|---|---|
| a. Raw number | `259200` |
| b. Raw number with unit | `259200 s` |
| c. Placed, familiar anchors | `between a night and a week, 9 x a night` |
| d. Placed, opaque anchors | `between a dosk and a mirl, 9 x a dosk` |
| e. Placed and raw together | `259200 s (between a night and a week, 9 x a night)` |

A placement is a fixed mapping from a value to an anchor, a pure rule with no model in it. Anchors are listed in a table in the prompt, each with its value in base units, so a placed magnitude can always be checked against numbers. In c, d and e the table comes first. In a and b there is no table.

The rule: with anchors sorted by value, a value between two is shown as `between <lower> and <upper>, <r> x <nearest>`, where the nearest anchor is the one with the smallest `|log(value / anchor)|` and `r` is the value over that anchor to two significant figures. A value below the lowest anchor is shown as `below <lowest>, <r> x <lowest>`, and a value above the highest as `beyond <highest>, <r> x <highest>`. Condition c shows the placement alone, so its precision is two significant figures, and that loss belongs to the condition.

Anchors:

| Dimension | Value in base units | Familiar name (c, e) | Opaque name (d) |
|---|---|---|---|
| Time, seconds | 2 | a moment | a veld |
| | 1800 | a meal | a prin |
| | 28800 | a night | a dosk |
| | 604800 | a week | a mirl |
| | 7889400 | a season | a tave |
| Money, dollars | 4 | a coffee | a kess |
| | 40 | a restaurant meal | a ralm |
| | 1500 | a month's rent | a vonk |
| | 30000 | a car | a brell |
| | 400000 | a house | a sorn |

The opaque names are invented, are set before any run, and are checked by a person for unintended meaning. They are assigned to anchors by a fixed shuffle, so no name hints at order. These anchors are examples for the experiment, as they are on the idea page.

## Tasks

Each task has an exact answer computed from the instance's values. Magnitude matters and nothing else does. Every instance is generated from a seeded template, `random.Random(seed)`, with the seed recorded.

**Strata.** Each instance has a reference magnitude M0, drawn log-uniformly from one band of its dimension, and every other duration or amount in it is M0 times a factor drawn log-uniformly from 1/10 to 10, then rounded to three significant figures. The band sets the stratum.

| Stratum | Time band (seconds) | Money band (dollars) |
|---|---|---|
| Below | 0.2 to 2 | 0.05 to 4 |
| Inside | 2 to 7889400 | 4 to 400000 |
| Beyond | 7889400 to 3.2e9 | 400000 to 4e9 |

Each task has 120 instances: 30 below, 60 inside, 30 beyond.

**Margin.** The answer is computed from the rounded values as shown. An instance is redrawn if its deciding ratio is within a factor of 1.3 of the point where the answer flips, so a placement rounded to two significant figures can still decide it.

**T1, supplies last until resupply (time).** A store holds S units, uses one unit every `p`, and the next resupply arrives in `D`. S is an integer from 3 to 400. D is M0. `p = D / (S * rho)` with `log10(rho)` uniform in [-1.5, 1.5], rounded. The answer is `lasts` if `S * p >= D`, else `runs out`.

**T2, which event is most urgent (time).** Four events, A to D, each with a time `e` since it happened and a time `w` it can wait. Urgency is `e / w`. One of the four is M0 for `e`, and the rest follow the strata rule. The answer is the event with the highest urgency, and the reply lists all four in order. Adjacent urgencies differ by at least a factor of 1.3, redrawn if not.

**T3, is a deviation worth correcting (money).** An overrun of size `d` will recur `n` times before the plan ends. Correcting it costs `K` once. `d` is M0, `n` is an integer from 2 to 60, and `K = d * n * rho` with `log10(rho)` uniform in [-1.5, 1.5], rounded. The answer is `correct` if `d * n > K`, else `leave`.

Instances never repeat across the main set and the pilot, which use different seed ranges.

## The prompt wrapper

The same in every condition: the task sentence with its slots filled, then "Work it out briefly. End with two lines: `ANSWER: <your answer>` and `CONFIDENCE: <a whole number from 0 to 100, your chance of being right>`." The output limit is 400 tokens and the sampling setting is the provider default, recorded. A reply with no `ANSWER` line counts as wrong. It is never discarded.

## Measures

- **Primary: accuracy against ground truth.** For each instance and condition, the share of repeats that are right. T2 scores the most urgent event only.
- **Consistency.** For each instance and condition, the share of repeat pairs that give the same answer. The source reports that repeat consistency told real axes from a nonsense one better than a confident spread did (0.93 against 0.71, spread 97 against 96), so consistency is a check on accuracy and a gain that comes with lower consistency is not counted as a gain.
- **Calibration at the ends.** Accuracy and the Brier score of stated confidence in each stratum. Stated confidence is reported as a spread as well, and never taken as evidence of anything.
- **Tokens per decision.** Mean input and output tokens per call from the meter's trace.
- **Secondary.** Order agreement on T2 (Kendall's tau), and each of the above by task and by dimension.

## Design

- **Paired.** Every instance runs under every condition, so the unit of analysis is the instance.
- **Size.** 3 tasks x 120 instances = 360 instances, 5 conditions, 3 repeats: 5400 calls. Repeats are identical prompts, so they test the model's own variation. With a per-instance standard deviation of the paired difference near 0.3, the standard error of the mean difference over 360 instances is about 0.016, so a 95 percent interval is about 3 points wide on each side. That is narrow enough to tell a 5 point difference from none. The 0.3 is an assumption, and the analysis reports the observed value.
- **Randomisation.** Instance generation, the order of instances, and the order of conditions within an instance are fixed by one recorded seed.
- **Pilot.** A separate 30 instances x 5 conditions x 1 repeat checks plumbing only. It tunes nothing. If condition b scores above 0.95 on the pilot, the model leaves no room to improve and the experiment is declared uninformative for it. It is then run with a smaller model named before any run.
- **Analysis.** Paired differences in accuracy, as the mean over instances, with a 95 percent percentile interval from a bootstrap that resamples instances within task, 10000 resamples, seed recorded.
- **Primary contrast.** c minus b, over all 360 instances. Everything else is secondary and is reported with intervals, not tests.
- **What size counts.** A difference counts only if it is at least 5 points and its interval excludes zero. The null is supported when the interval lies inside plus or minus 5 points.
- **Secondary contrasts.** d minus b (structure), c minus d (meaning), e minus c and e minus b, each by task, dimension and stratum.
- **Exclusions.** A call that fails for a reason outside the prompt is retried twice. An instance that still lacks a call under any condition is dropped for all conditions. If more than 5 percent are dropped, the result is flagged. Nothing is excluded for a wrong or unparsable answer.
- **Stopping rule.** The set runs to completion. There is no interim look and no early stop on results.

## How it is run

Through the benchmark's meter, which counts calls and tokens and records and replays every model call, so nothing is paid for twice ([decision 0030](../decisions/0030-pay-once.md), [the bench](../../bench/README.md)).

- Present: `bench.meter.Meter` with `cache_mode` of `record` or `replay`, its own `cache` directory and `replay_from`, a budget of calls and tokens, a trace file, and a model name that it enforces; `bench.backends.ConkyModel`, which reaches a model through `conky.model`; and `--cache-mode replay --replay-from` for a replay that is never reported as a new result. The meter counts repeats of an identical request within a run, so three repeats of one prompt are three recorded calls.
- Needed, and not built: a generator for the three tasks and the renderings above, a runner that posts each prompt to the meter in the seeded order, and an analysis for the paired differences. They are specified here closely enough to implement, and would sit beside the existing runner without changing it.
- One step first ([decision 0031](../decisions/0031-build-on-bedrock.md)): walk one instance of each task under all five conditions by hand with the stand-in backend and read each prompt, then one live instance, before any batch. A walked instance is never a result.
- Raw traces, prompts and recorded answers are kept outside the repository.

## Result class and what each outcome means

This is a prompt result. It may guide how prompts are written and may not appear in a claim about Conky.

| Outcome | Reading | The idea |
|---|---|---|
| c minus b counts, and c minus d counts | Familiar meaning helps beyond structure. | Adopt familiar anchors. |
| c minus b counts, c minus d is within 5 points | Structure helps and the names do not. | Adopt a placed scale. The claim about experience is dropped. |
| The gain holds for one dimension or one stratum only | A narrower effect. | Adopt only there. |
| c minus b is within plus or minus 5 points | The null holds. | Drop the idea. |
| c minus b is below minus 5 points | Placement hurts. | Drop it, and the strata show where. |
| Gain at the ends is lost or reversed beyond the last anchor | The ends mislead. | Adopt only inside the anchors, or with an explicit beyond rule. |
| e matches c or b | Raw and placed are interchangeable. | Keep the raw value beside it only if e is better than c. |

An accuracy gain with lower consistency, or with output tokens more than a quarter higher, is reported as a cost beside the gain.

## Threats to validity

- One model, one prompt wrapper and synthetic tasks. A result need not hold for another model or for a real decision.
- Every task is answerable from the numbers. The test measures whether placement helps a model that could already compute, which is the case that matters least. A condition that helps here may help more where arithmetic is harder, and the reverse.
- The anchor table gives values in c, d and e, so d tests structure with numbers present. It does not test a scale without numbers.
- The anchors are chosen by the maintainers and are a culture's, in English. Other anchors might do differently.
- Familiar names may be present in training data in ways opaque ones are not. That is the meaning effect, and it is not separated from contamination.
- Condition c loses precision by design. A deficit there may be rounding and not placement. e is the control for it.
- A ceiling in b leaves no room, and the pilot rule only declares it, it does not fix it.
- Provider behaviour changes. Model version and date are recorded.

## What will not be claimed

- Nothing about Conky as a harness, and nothing about the other parts of the idea page: the shared frame across dimensions, the lens page, or emotion.
- Nothing about severity or any dimension not run.
- No claim that a placed magnitude is how a model feels anything. The result is about decisions on these tasks.
