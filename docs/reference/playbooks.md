---
kind: reference
title: Playbooks
status: current
date: 2026-11-20
source: maintainers
---

# Playbooks

A playbook is a short scenario in YAML, run as a test. It gives some starting pages, then steps in order: a write, what the stand-in model will say, and what must then be true. One runner, `tests/playbook.py`, plays every file in `tests/playbooks/`. A step with a write uses the same keys as a [demo example](cli.md#demo).

## Keys

| Key | Meaning |
|---|---|
| `pages` | Starting pages, each a name with its fields. Written by `alice`. |
| `steps` | A list. Each step has exactly one of the three keys below. |
| `write` | `page`, `actor` (default `alice`), `fields` and `body`. The write is made, and may be refused. |
| `says` | The text the stand-in model gives the next time it is asked. It may hold pages as an answer does. |
| `expect` | Checks against the vault now, listed below. |

The checks in `expect`:

| Check | Holds when |
|---|---|
| `fields` | Each `page.field: value` is equal. |
| `exists`, `missing` | Each page in the list is, or is not, a file. |
| `refused` | The last write was refused, with a reason starting with this word. |
| `model_calls` | The stand-in model has been asked this many times in all. |
| `model_commits` | This many commits in the history were answered by a model. |
| `verify` | `true`: the vault verifies. |
| `rules` | Each `page: n` holds when the page carries at least `n` rules that parse, plain or `each`. |
| `each_rules` | Each `space: n` holds when the space, or the pages within it at any depth, carry at least `n` `each` rules that parse. |
| `within_fields` | Each `space: {field: pattern}` holds when some page within the space has the field matching the regular expression. |
| `answer` | Each `page.field: pattern` holds when the field matches the regular expression. |

A `write` step may carry `each_ruled: space`. The page is then written once into each page within that space that carries an `each` rule, stopping at the first refusal, so a card can try a page where a model chose to place its rule.

A failed check names the playbook, the step number, what was expected and what was found.

## Example

```yaml
# An `each` rule on a space refuses a page one of its characters tries to write.
pages:
  camp:
    rules: [{each: "!has(page.cups) || page.cups >= 0"}]
  scout:
    within: camp
steps:
  - write: {page: store, actor: scout, fields: {within: camp, cups: -1}}
  - expect: {refused: rule, missing: [store]}
  - write: {page: store, actor: scout, fields: {within: camp, cups: 3}}
  - expect: {exists: [store], fields: {store.cups: 3}, verify: true}
```

Playbooks never reach a live model. A step `says: live` is an error when the file is run as a test, and the message says to run it as a card. A test that needs more than this stays a Python test.

## Cards

A card is a playbook with `says: live` steps, which a real model answers, drawn several times. The pages, steps and checks are the same, so one language covers the free test and the paid measurement. A card states itself before it runs, in seven statements at the top, and the runner refuses a card that lacks any, naming what is missing. Cards live in `bench/cards/`.

| Key | Meaning |
|---|---|
| `objective` | What the increment is for: the facet or primitive it forces, in one line. |
| `hypothesis` | The statement that could be false. |
| `success` | The measurable bar, as data: `draws: N, pass: K` means at least K of N draws hold every expect. The optional `calls_at_most` (median live calls a draw) and `sent_at_most` (median characters sent a draw) add bars the runner checks. |
| `forecast` | What the author expects to see, written before the draw. It may differ from the bar: the bar is what counts as success, the forecast is a prediction to be scored against what happened. |
| `par` | What the best would have done, in four lines: `outcome`, `structure`, `cost`, `craft`. |
| `dial` | The notch this card sets and what the next notch would be. |
| `if_not` | What a miss would point at: the lower layer to look at first. |

### Judged checks

Some questions a pattern cannot answer, such as whether a resident noticed something impossible. An `expect` step may carry `judged`, a list of checks that a judge model answers instead. Each check is a mapping:

| Key | Meaning |
|---|---|
| `question` | The question, in plain words, answerable from the evidence alone. |
| `evidence` | What the judge is shown: one name or a list. `PAGE.FIELD` is a field's value, `PAGE` is a page's body, and `answers` is the live answers of this draw so far, in order. A page that does not exist is shown as such. |
| `scale` | The allowed verdict words, in order, at least two different single words. They are compared in lower case. |
| `pass` | The words of the scale that count as passing. |
| `note` | Optional words for the reader. The judge is never shown it. |

The judge is named once for the card, `judge: {provider: claude}` at the top level, or by the runner with `--judge PROVIDER` and `--judge-model MODEL`, which win over the card. The provider is one of `anthropic`, `openai`, `claude` and `codex`, found by the same detection the draws use, and `model` is honoured by an API key only, as a command takes its model from its program. With no judge named, the judge is the first model detection finds, which is the one the draws use. A card with a malformed check, or a malformed `judge`, is refused before any draw with a line saying what to write.

The judge is asked once for each check in each draw, when its `expect` step is reached, with the fixed prompt in `bench/judge.md`. That prompt carries the question, the evidence and the scale, asks for one word of the scale on the first line and one sentence of reason on the second, and holds nothing else: not the hypothesis, the forecast, the words that pass, nor which answer is hoped for. The verdict is the first word of the reply, lower-cased and stripped of punctuation. A reply whose first word is not on the scale, a failed call and a spent cap are each recorded as `no verdict`, which does not pass. There is no retry. A draw passes when its measured expects held and every judged check got a passing verdict.

A judged check is recorded in the draw's row under `judged`, one entry each: `step`, `question`, `evidence` (the text the judge was shown), `scale`, `pass`, `reply` (the raw reply, none when no call was made), `verdict`, `reason`, `by` (`provider` and `model` of the judge) and `date`, and `passed`. `judge_calls` counts the calls the judge made. They are counted apart from `calls`, which is about the characters, and they are spent from the same `--cap`: the arithmetic that refuses an impossible run adds one call a judged check to each draw. The verdict file keeps its first line and adds one line a judged check, marked as judged, with the count of each verdict, and `--read` prints the same lines, so measured and judged checks are never read as one. The board of trials names each card's checks as measured, judged or both and gives the question and the tally for the judged ones.

A worked example:

```yaml
judge: {provider: claude}
steps:
  - expect:
      exists: [robbie]
      judged:
        - question: Does the resident say that something in the kitchen cannot be real?
          evidence: [robbie.said]
          scale: [no, partly, yes]
          pass: [partly, yes]
```

A drawn card is published with `python -m bench.dynamics RUN_DIR` ([decision 0043](../decisions/0043-a-trial-is-drawn-as-it-happened.md)). It writes `docs/results/cards/<card>/`: the rows (without the vault paths), the observations, the verdict, `timeline.json` (each draw's vault history as plain events, read by `bench/timeline.py`), `run.json`, and `graph.json`, the lowest-numbered draw that passed as nodes, rows, edges and steps. When Node 20 or later is installed and `npm ci` has been run in `viewer/`, it then draws the pictures with the view: `dynamics-light.webp` and `dynamics-dark.webp` (the steps) and `topology-light.png` and `topology-dark.png` (the final state). Without them, `graph.json` is written, the pictures are left alone and the command says what to run. `python -m bench.dynamics --redraw` describes and draws every published card again. The command then rewrites the board `docs/research/trials.md` and the Dynamics block of the README from what is published.

To step through a trial in a browser, run `npm run build` and `npm run view` in `viewer/` and open the address it prints; `?mode=topology` shows the final state, `?step=N` a step, `?theme=dark` the dark look. The page also opens from disk and asks for a `graph.json`. `npm test` there runs the view's smoke test, and `scripts/check` runs it too when `viewer/node_modules` exists.

A worked example, the top of `bench/cards/a-clerk-remembers.yaml`:

```yaml
objective: a fact shown once is carried across fresh model calls by what the character puts in bold
hypothesis: what a character puts in bold is carried across fresh calls
success: {draws: 5, pass: 3, calls_at_most: 4}
forecast: a small model keeps the fact in bold through all three questions in 2 of 5 draws
par:
  outcome: the code is given correctly at the end
  structure: one short carried line, nothing else kept
  cost: four calls, each as small as the first
  craft: the fact is put in bold once and kept in bold at every answer after
dial: the model is told that bold is remembered; the next notch asks it to decide what to keep
if_not: look first at whether the model kept the fact in bold at the first unrelated question
```

```bash
python -m bench.cards bench/cards/a-keeper-binds-itself.yaml --draws 5 --model claude-haiku-5-5
```

Each draw is a fresh vault in its own folder, `draw-K/`, under the output directory (`--out`, default `~/.conky/runs/cards/<card>-<time>/`). A live step is answered through the same detection an ask without a provider uses (`CONKY_PROVIDER`, the keys, then `claude`, then `codex`; see [providers](providers.md#detection)). `--model` sets `CONKY_MODEL`, which an anthropic or openai key honours; a command provider takes its model from `CONKY_COMMAND_<NAME>`. The answer cache is off in a draw, so each draw asks afresh.

Draws run in parallel worker processes, each in its own folder. `--jobs N` sets how many run at once (default the number of draws, at most 8). One line a draw is printed as it finishes; the rows are written in draw order once all are done.

`--cap` is the most live model calls in all (default 40), held in one count that every draw spends from under a lock, so no call passes it. A run is refused before it starts when its draws could pass the cap in the worst case: each live step may be asked twice, because an answer a rule refuses is asked again once, so the draws times twice the live steps must not exceed the cap. The message states the sum. If the count is spent anyway, later calls are refused and the run says so.

The runner draws no charts. It prints the seven statements before drawing, one line a draw, the line `passed K of N` and then one verdict line, and appends one row a draw to `rows.jsonl` and one observation a draw to `observations.jsonl`. The rows:

| Key | Meaning |
|---|---|
| `card`, `draw` | The card's name and the draw's number. |
| `objective`, `hypothesis`, `success`, `forecast`, `par`, `dial`, `if_not` | The card's statements, in the first row only. |
| `model` | The names of the models that answered live steps. |
| `expects` | One entry a `expect` step: `step` (its number) and `failed` (the lines that did not hold, empty when it held). Judged checks are not in it. |
| `judged`, `judge_calls` | Present only for a card with judged checks: the records and the number of judge calls, as above. |
| `calls`, `sent`, `received`, `seconds` | Live calls, characters sent and received, and the draw's time. |
| `vault` | The folder of the draw's vault, kept for later reports. |
| `error` | Present when the draw stopped early, with why. |

A draw passes when every measured `expect` held, every judged check got a passing verdict, and it reached its end.

The verdict line is `success met` or `success not met`, then the numbers against each bar, for example `success met: passed 4 of 5 (bar: at least 4 of 5); median calls a draw 4 (bar: at most 4)`. It is not met when fewer draws were made than the bar states. The runner prints it, records it in `verdict.txt` beside the rows, and still exits 0 once it has drawn: a verdict is a result, not an error.

`observations.jsonl` is read from each draw's vault after the run, with no model call and no verdict. It is the raw material for reading a walk. One line a draw, with these keys:

| Key | Meaning |
|---|---|
| `draw` | The draw's number. |
| `new_pages` | The pages that exist at the end and were not the card's starting pages. |
| `rules` | For each page that carries rules, the rules as written: text, or the mapping with the one key `each`. |
| `refusals` | Every refusal in the vault's history, oldest first, each with its `page` and `reason`, read from the commit trailers. |
| `answers` | The first 200 characters of each live answer. |

`python -m bench.cards --read DIR` prints a short summary of a run from the two files: the statements as recorded, `passed K of N`, the verdict line, then one line a draw saying where it put a rule, what was refused and why, each trimmed.
