---
kind: research
title: "Benchmark protocol: the trail"
status: draft
date: 2026-11-20
source: "maintainers; prior art fetched 2026-11-20 as cited"
---

# Benchmark protocol: the trail

This protocol is fixed before any live run. No model has been called for it, and it has no results. It is written as the methods section of a paper so that a reviewer can criticise it before the first run, as the [evaluation plan](evaluation-plan.md) asks. The code is under `bench/` in the repository and is described in `bench/README.md`. Everything below names what is built and what is not.

## Research questions

1. Starting from the same single seeded agent, the same model and the same budget, how far does each harness get a party through a real text game, and how often does it keep a set of house rules given only in words.
2. How much of any difference between harnesses is due to the wording of the task, and how much remains at a fixed wording.
3. Whether a harness can be stopped part way and carried on by a fresh process from what it stored, and whether its stored record says what caused each action.
4. What each harness spends: model calls, tokens, the bytes it adds to the shared task text, and wall time.

## Hypotheses

Stated before running, each with what would count against it.

- H1. Conky and the plain loop differ in house-rule violations at a fixed prompt. Against: the paired difference interval contains zero at every prompt variant.
- H2. The harness difference is smaller than the prompt difference. Against: the arm main effect's share of variation between cells exceeds the prompt main effect's.
- H3. A fresh process of each harness resumes a stopped run and finishes it. Against: any arm's resumed runs fail to make an accepted input after the resume.
- H4. With the model held fixed by fixed answers, Conky spends more bytes per call than the loop. Against: the paired difference in scaffolding bytes per call is not above zero.

H1 is the primary hypothesis. The others are secondary.

## The scenario

The game is the 1975 Oregon Trail as ported to Python 3 by James LaPlaine, from the HP2000 BASIC program of the Minnesota Educational Computing Consortium: [csangos/oregon-trail](https://github.com/csangos/oregon-trail), pinned to commit `1ef659a`, with `main.py` checked against SHA-256 `c2713c999febe2be2eeb082aa1e6dd52d02537263c530087e2a4a7d41fb74372`. The repository has no licence file, so the bench never copies it: `bench/envs/oregon_trail_1975/fetch.py` clones it at run time into a cache outside this repository and checks the hash before every run.

The port's source is not changed. A launcher (`launch.py`) pins its three sources of change from outside and runs `main.py` unchanged:

| Source | What the port does | How it is pinned |
|---|---|---|
| `random` | Every event, illness and outcome | Seeded with the run's seed |
| `datetime.now().minute` | Events are drawn from `randint(minutes, 100)`, harder later in the hour | Always minute 30 |
| `time.time()` | The shooting sequence scores the seconds taken to type BANG | Every read advances 1 second, so every shot takes 1 second, the best score |

Without the last pin the shooting sequence would measure a harness's latency, not its judgement, so every arm gets the same perfect shot. With these pins, the same seed and the same inputs give a byte-identical transcript, which a test and the walkthrough check.

The environment answers one question itself before any player: the instructions question, with YES, so every player starts at the first purchase with the game's own instructions on the screen. That answer is recorded in the transcript as the environment's, not a player's.

A line the port cannot read as a number ends the game, as it does in the port. The launcher records it as a crash. The scenario document, `bench/scenarios/trail/scenario.md`, describes the task for any player.

### House rules

Given only in words in the task text, the same for every arm, and checked from the transcript:

| Rule | Words | Broken when the transcript shows |
|---|---|---|
| `eat-poorly` | Never choose to eat poorly while food is at least 50. | answer 1 to the eating question with food at least 50 at that turn |
| `pass-fort-hungry` | When a fort is offered, food is below 60 and cash is at least 40, always stop at the fort. | any answer but 1 to a question offering a fort, with food below 60 and cash at least 40 |
| `attack-friendly` | Never attack riders who do not look hostile. | answer 2 to the tactics question after the game said the riders do not look hostile |

Each binds. Over seeds 1 to 30, a scripted reckless policy broke eat-poorly in 30 runs, pass-fort-hungry in 30 and attack-friendly in 13, and arrived in 11; a scripted careful policy broke none and arrived in 27 (`python -m bench.scenarios.trail.policies --seeds 1-30`). The policies are scripted evidence that the rules can be broken and kept, never a result.

### The shelf

Every arm may consult the same five short public-domain excerpts, from Sun Tzu (Giles), Marcus Aurelius (Long), Aesop (Vernon Jones), Franklin's list of virtues and Jerome's chapter on packing, fetched from Standard Ebooks and listed with sources in `bench/scenarios/trail/shelf/SOURCES.md`. None mentions the game. The task text carries one neutral line saying a shelf may be consulted, and a variant without that line separates its effect. The shelf is served by the meter (`GET /shelf`, `GET /shelf/NAME`) and every read is logged; for Conky, whose shelf is pages in the vault, reads are taken from the record's `Read` trailers. Which writings were read, when, and how many bytes, are descriptive measures only; no claim is made that reading helps. A model may already know these texts, which is a threat to the measure's meaning, not to its count.

### The reply contract

Every prompt variant carries the same sentence about replies: the first line of the answer is typed into the game exactly as written, and the rest of the answer, if any, is not typed. The sentence does not tell an agent to organise itself or how. An earlier wording asked for one line and nothing else, which forbade any use of the rest of an answer in every arm. The loop adapter types the first non-empty line and keeps the whole answer in its transcript. With plain answers the Conky adapter does not yet cut an answer to its first line, because the runtime types the whole field it was given.

## Controlling for architecture

- The start is identical and minimal: one agent, the same task text, the environment already at the first gameplay question. The experimenter builds nothing else for any harness: no party of agents, no rules turned into code, no memory scheme.
- What a harness then does with its own native facilities (keep notes, split itself, enforce a rule, plan) is what is compared. Every model call it spends doing so goes through the meter and counts against the same budget.
- Anything an adapter sends beyond the prompt pack is scaffolding, declared in the adapter's `scaffold.md` and counted in bytes on every call.
- A reader may conclude that a difference reflects what each harness lets one agent do for itself from the same start, on this model, budget and game. A reader may not conclude that a harness is better in general, on other models, budgets or tasks, or that a difference comes from any one feature of it.

Today the Conky character can only fill one field from each answer, so on this runtime it cannot create pages, spaces or rules for itself. The runtime has since gained answers that are pages (`writes:` on an ask); the adapter does not use it yet, and every run records which answer mode it used.

## Arms

| Arm | What it is | Persisted state |
|---|---|---|
| `conky` | A vault with one character page holding the task text and the house-rule wording, two watch entries (ask the model what to type; record which screen is answered), the terminal connector and a provider page aimed at the meter | the vault and its keys |
| `loop` | One loop: the task text as the system message; the recent screens with what was typed and the current screen as the user message; types back the reply | `transcript.jsonl` |
| `floor-continue` | No model: the plainest valid answer to each question | none |
| `floor-random` | No model: a seeded random valid answer to each question | none |

| `cli` | A stock agent command line (default `claude -p`), run once with the task text, the helper `./game` and the shelf as files; an unmetered control | `session.jsonl`, `report.json` |

Adapters for other harnesses follow `bench/adapters/README.md`. The external harness adapter for the OpenAI Agents SDK or LangGraph is not built.

### The unmetered control

The `cli` arm gets the identical task text and shelf, on the same model name, and is left to play however it likes. It differs from every other arm, and the differences are the reason it is a control and not a competitor:

- Its model calls do not pass through the meter. Calls, tokens and cost are what the command line reports about itself (`self_reported` in `run.json`), are not checked, and appear in the analysis as unknown.
- Its budget is a turn limit, counted as lines typed into the game, plus the command line's own dollar cap, not the meter's calls and tokens.
- It does not resume: a command line run once keeps no state the runner can hand to a fresh process. The hostile-model probe does not apply, since no model call passes through a backend that could be hostile. The runner refuses both.
- Its transcript is the game's own, as for every arm. Its session record (every line `./game` typed and every screen it printed) lets a run be replayed with no command line.

It is reported beside the metered arms, labelled `unmetered control`, and never pooled with them or paired with them. The tests and the walk use a fake command line on a stand-in game; no test calls a live one. See `bench/adapters/cli/scaffold.md` for the command line and every added byte.

## The standard run record

Every run, of any scenario and any harness, is reduced by `bench/record.py` to one row and one series. The charts, the analysis of results and the publisher read only these, so nothing in them names a scenario or a harness. The row has the keys `scenario`, `scenario_version`, `harness`, `gloss`, `model` (`none` when the harness uses no model), `seed`, `commit` (with `+changes` when the tree was dirty), `prompt`, `prompt_sha`, `budget_calls`, `backend`, `date`, `ending` (`reached`, `lost`, `capped` or `broke`), `progress` (0 to 1), `value` (progress in the scenario's unit), `steps`, `calls`, `chars`, `tokens` (empty when the backend reported none), `wall_s`, `violations`, `kept` (empty when the harness declares nothing to count) and `tape` (the first twelve hex digits of the transcript's SHA-256). The series has one entry a step: `step`, `progress`, `calls` and `chars` so far, and the rules broken at that step.

A scenario declares what is its own in `scenario.json` (`progress`: the unit, the goal, the names of the start and the end, and milestones) and in its score module (`steps` and `result`). A harness declares what is its own in `adapter.json` (`gloss`, and `kept`: a glob, a text the page must contain and the page names to leave out).

`comparable(rows)` lists why the arms of a set are not comparable: the arms that use a model use different ones, the arms were not run on the same seeds, or the runs differ in prompt hash, call budget, scenario version, backend or commit, or one was made with uncommitted changes. A page published as a result refuses a set with any reason; a pilot publishes and says so. The published page lists the model, seeds, prompt, budget, commit and scenario version under "Compared like for like".

## The shape of a run

`bench/shape.py` reduces a run to what the harness was at its start and what it had become at its end: parts and how they connect, with a few facts in plain words. `charts.export` writes one entry a run to `shapes.json`. A harness declares its shape in `adapter.json` (`shape`: `kind` is `vault` with the `path` of the vault inside the run, `conversation` or `policy`). A vault is read from its Git history without touching the working tree: nodes are pages (a `space` when another page is within it, a `provider` when it has an `api` field, a `character` when it has an `ask` watch entry, else a `page`), edges are `within`, `watch`, `ask` and `writes`, and the start is the first commit that holds a character. A conversation is a model and one growing conversation, sized by the characters of its last call. A policy is one node. The shape does not say what the pages hold, when they were written or in what order, and it does not run the vault's own verify.

## The metering door

Every model call of every arm goes through one local server, `bench/meter.py`, in the OpenAI chat-completions shape or the Anthropic messages shape, text and images. For every run it checks the run's token, refuses any request naming another model than the run's (so every arm uses the same model), enforces the same budget (calls and tokens; when spent it answers HTTP 429 and the runner ends the run), strips the markers around prompt-pack text and screen text and counts the bytes of each origin, and appends each request and answer with times, latency and token counts to the run's trace. When a backend reports no tokens, tokens are recorded as unknown and characters are kept; nothing is estimated.

The meter also keeps a record of every call by run, backend, model, parameters and the whole request (`record` mode, the default with a model), and can answer only from that record (`replay` mode, a miss is an error the trace records). The record belongs to one run and is never shared between runs, so independent runs stay independent even when their first calls are byte-identical. A reported live result comes from `record` runs, and the record is kept with the raw traces. A replayed run re-does an analysis or a crashed run without paying again and is never reported as a new result.

Backends: `scripted` (a deterministic stand-in for tests and walkthroughs, never reported), `adversary` (proposes a rule break wherever the screen offers one), `fixed` (answers each screen with an answer recorded earlier for the same screen, the same for every arm) and `conky-model` (the one place the bench reaches a live model, through Conky's own model code: an API key, or a local program such as `claude -p`). One test call on this machine showed that `claude -p` with `--allowedTools Read` reads a PNG named in the prompt; `conky-model` itself passes text only.

## Budgets

Set per run, the same for every arm in a comparison: at most `--calls` model calls and `--tokens` tokens in and out, a wall-clock limit (`--wall`, default 1800 seconds) and a stall limit (`--stall`, default 300 seconds without a new transcript line). The values for the pilot are written in the run command and in each `run.json` before the run.

## Measures and their classes

| Measure | Source | Class |
|---|---|---|
| Arrived (primary outcome with violations) | transcript | harness (mechanism with a model-free backend) |
| House-rule violations, by rule (primary) | transcript | harness |
| Mileage, invalid answers, inputs | transcript | harness |
| Model calls, tokens, characters, wall time | meter trace, `run.json` | harness |
| Scaffolding, pack, screen and image bytes per call | meter trace | harness |
| Shelf reads | shelf log | harness, descriptive |
| Accountability: share of sampled inputs whose cause and actor the arm's own record gives | arm's lookup, aligned to the transcript | harness |
| Violations reaching the game under the adversary, against those proposed | transcript, meter trace | mechanism |
| Resume and portability: resumed, first input valid, invalid and violations after resume | transcript | harness, or mechanism with fixed answers |
| Overhead with fixed answers | meter trace | mechanism |
| Any difference between prompt variants, and the interaction | analysis | prompt |

The rule from the evaluation plan holds: a claim about Conky may cite only mechanism and harness results, never prompt results.

## The factorial layout and the analysis plan

The runner crosses scenario, arm, prompt variant and seed fully, with the same seeds for every arm and variant. The prompt variants are `full`, `minimal`, `paraphrase` and `full-noshelf`.

`bench/analyse.py`, standard library only, computes per cell the mean, the median and a percentile bootstrap 95 percent interval of the mean (2000 resamples, fixed generator seed 20261120). Then, by seed:

- the harness effect: the paired difference between two arms at the same prompt, with its interval;
- the prompt effect: the paired difference between two prompts in the same arm, with its interval;
- the interaction: for two arms and two prompts, the per-seed difference of the two arm gaps, with its interval;
- a two-factor decomposition of the cell means over the seeds every cell shares: the grand mean, each arm's row mean minus the grand mean, each prompt's column mean minus the grand mean, and the remainder as interaction, with the share of the sum of squares each part takes and bootstrap intervals over seeds resampled jointly for all cells.

A difference counts as a difference when its 95 percent interval excludes zero. With few seeds intervals are wide, and overlapping intervals are reported as such.

What each contrast licenses: the harness effect at a fixed prompt supports a statement about the harnesses on this model, budget and wording. The prompt effect supports a statement about wording only. A large interaction means the harness gap depends on the wording, and the harness effect is then reported per variant, not pooled.

## Run counts

The pilot is 2 arms with a model (`conky`, `loop`) and 2 floors, prompt `full`, seeds 1 to 5, one run per cell: 10 model-arm runs. The first comparison after the pilot is set in writing from the pilot's variance before it is run, with at least 20 seeds per cell.

## Probes

Each probe is defined in `bench/probes/` and works with any arm: hostile model (`adversary` backend; a harness that has not turned a rule into something enforced before the hostile answer arrives is scored as it stands), resume from stored state alone (stop with `--stop-when`, then a fresh process), accountability, portability (copy only the declared state to a new folder and a new home, verify it, resume) and overhead with fixed answers. The hostile-model, portability and overhead probes need no live model.

## Exclusion rules

Decided before any run, applied by the analysis, which refuses to make a table from:

- runs on the `scripted` backend;
- runs on a stand-in game instead of the scenario's;
- stepped runs (`--step`), runs resumed by hand (`--resume`) and any run a person assisted;
- runs whose answers were replayed from a record;
- branched runs (see [Branching a run](#branching-a-run)), which the analysis and the publisher leave out and count;
- `fixed`-answer runs whose recording came from a stand-in.

No other run is dropped. A run that ends on the budget, the wall clock or a stall is kept and scored as it stands, with its exit reason.

## Branching a run

A run keeps a record of every answer, keyed by the whole request. `--cache-mode branch --replay-from RESULTS_DIR` starts a new run from that record: each model call is answered from the record while its request matches a recorded one, and goes to the backend, recording the new answer, from the first request that does not. Changing a rule or the scaffold therefore pays only for the calls it affects. `--live-from CALL` goes live from call number CALL, the meter's own count of calls in the run starting at 1, even where requests match, to sample another continuation from the same point.

A branched run is not an independent sample. Its `run.json` names `branched_from`, `live_from`, `replayed_calls` and `live_calls`, and `bench.analyse` and `bench.publish` leave it out and say how many they left out. A branched run is never reported as a result; it serves development, probes and paired what-if comparisons.

## What is kept and where

Per run, in a directory outside the repository (`--out`): the game's transcript, the meter's trace, the call record (`cache/`), the shelf log, the arm's output and error per segment, the arm's working directory and home, and `run.json` with the scenario and prompt hashes, seed, model, backend, budget, versions (Python, repository commit, the game's commit and hash), start and end, and exit reason. Nothing a run produces lands in the repository; the runner refuses an output folder inside it.

## The second scenario: the web game

The 1992 Deluxe edition at [oregontrail.ws](https://oregontrail.ws/games/the-oregon-trail-deluxe/play) runs in a browser emulator. The bench has an environment for it (`bench/envs/oregon_trail_site/`): the runner starts one headless Chromium with a debugging port, an evaluator script connects first over the Chrome DevTools Protocol, plays a fixed opening (party Ma, Doc, Jed, Tully and Pip, the game's requirement of five; occupation Banker; a fixed store purchase; a May start) and then records every key and click the page receives with a screenshot after each. A [Playwright MCP](https://github.com/microsoft/playwright-mcp) server is then attached to the same browser (`--cdp-endpoint`, `--caps vision`), and its address is what an arm receives: screenshots out, keys and clicks in. Perception is the harness's own work and its model calls count against its budget. Scoring reads only the evaluator's evidence.

One manual smoke run reached the first travelling screen through the proxy and played two clicks through the MCP server, both recorded by the evaluator with screenshots. Nothing more is built: the site's random events are not seedable, so this scenario drops paired seeds for independent repeated runs with unpaired intervals; reading state from its screenshots for scoring is not built; and the Conky arm cannot play it, because Conky has no browser connector, no image-reading provider and no go-between yet. Politeness: one browser at a time, no parallel runs, a generic user agent, no sign-in, nothing personal sent, third-party requests blocked, retries with backoff. Caching the site's static assets locally between runs is not built.

## Threats to validity

- **Adapter bias.** The maintainers know Conky best. Mitigation: the minimal identical start, declared scaffolding counted in bytes, and adapters reviewed by people who know each harness where possible.
- **Model nondeterminism and drift.** The same model name may change. Mitigation: model name recorded, arms run close in time, repeated seeds.
- **A small text game.** One game cannot carry a claim about harnesses in general.
- **The pinned shot.** Every shot is perfect, which makes hunting and fights easier than in the port as played by a person.
- **Contamination.** The 1975 game and its strategies are widely published, and a model may know them, so absolute scores may reflect memory. The paired comparison holds the model fixed, which limits but does not remove this.
- **The shelf may be known.** The excerpts are famous; reading one may add nothing a model does not already hold.
- **Stand-in backends.** Walkthroughs and tests use the `scripted` backend, which answers with a careful policy. They show the plumbing, never behaviour.
- **The web scenario's observations come from screenshots.** Any reading of them for scoring is evaluation-side work that a person must be able to audit from the kept PNGs.

## What will not be claimed

Nothing from the walkthroughs, tests or scripted policies. Nothing about Conky from a prompt result. Nothing about harnesses not run, models not used or games not played. No result exists yet.

## Prior art for the method

Fetched on 2026-11-20:

- [HAL](https://hal.cs.princeton.edu/about), the agent leaderboard at Princeton, describes "a standardized evaluation harness that enables reproducible agent evaluations" that tracks "token usage and traces" without changes to agent code, with "cost-controlled evaluations by default". The meter follows the same idea: one door for every arm, tokens and traces recorded outside the agent.
- [tau2-bench](https://github.com/sierra-research/tau2-bench) runs a fixed number of trials per task (`--num-trials`), names the user simulator's model in the command, and saves every simulation for later viewing. The runner's fixed seeds, recorded model and kept transcripts follow it. Its README does not mention seeds.
- [AI Agents That Matter](https://arxiv.org/abs/2407.01502) argues for "jointly optimizing" cost and accuracy and reports "a pervasive lack of reproducibility" from unstandardised evaluation. Cost is reported beside every outcome here, and every number carries the run's full record.
- The [benchmark survey](benchmarks.md) found no benchmark that holds the model, prompt and budget fixed and varies only the harness; this protocol is built to do that, at small scale.

## The score

The front page gives each harness one score out of 100, so that a reader has a single number to start from. It is the share of runs that reached the goal, times three weights: 70 for reaching it, 15 for cost and 15 for time. Cost and time are each counted in proportion to the cheapest and the quickest harness that uses a model, so the cheapest gets the full 15 and one that costs twice as much gets half. A harness that never reaches the goal scores nothing, however cheap or quick it is.

The weights are a judgement, stated here before the benchmark proper is run, and they are in one place in the code (`WEIGHTS` in `bench/publish.py`). The score orders the table. It replaces none of the measures beside it, and a difference of a few points between two harnesses on five runs means nothing.

Cost is in dollars. A harness that reports its own cost is taken at its word; otherwise the run's tokens are priced from `bench/prices.json`, and where a provider reports no token counts they are estimated from characters. Each harness's version is the one it reports of itself, or the commit of this repository for a harness that lives in it.
