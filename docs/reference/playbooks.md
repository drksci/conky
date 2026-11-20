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
# A rule on a space refuses a page one of its characters tries to write.
pages:
  camp:
    rules: ["!has(page.cups) || page.cups >= 0"]
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

A card is a playbook with `says: live` steps, which a real model answers, drawn several times. The pages, steps and checks are the same, so one language covers the free test and the paid measurement. A card may carry a `claim:` and a `forecast:` as text at the top, and a `par:` of three lines, `outcome`, `structure` and `cost`, saying what an ideal run looks like. Cards live in `bench/cards/`.

```bash
python -m bench.cards bench/cards/a-keeper-binds-itself.yaml --draws 5 --model claude-haiku-5-5
```

Each draw is a fresh vault in its own folder, `draw-K/`, under the output directory (`--out`, default `~/.conky/runs/cards/<card>-<time>/`). A live step is answered through the same detection an ask without a provider uses (`CONKY_PROVIDER`, the keys, then `claude`, then `codex`; see [providers](providers.md#detection)). `--model` sets `CONKY_MODEL`, which an anthropic or openai key honours; a command provider takes its model from `CONKY_COMMAND_<NAME>`. The answer cache is off in a draw, so each draw asks afresh.

`--cap` is the most live model calls in all (default 40). A draw is not started when the calls already made plus the largest draw so far would pass it, and no call passes it.

The runner draws no charts. It prints the claim and the forecast before drawing, one line a draw and a last line `passed K of N`, and appends one row a draw to `rows.jsonl`:

| Key | Meaning |
|---|---|
| `card`, `draw` | The card's name and the draw's number. |
| `claim`, `forecast`, `par` | The card's text, in the first row only. |
| `model` | The names of the models that answered live steps. |
| `expects` | One entry a `expect` step: `step` (its number) and `failed` (the lines that did not hold, empty when it held). |
| `calls`, `sent`, `received`, `seconds` | Live calls, characters sent and received, and the draw's time. |
| `vault` | The folder of the draw's vault, kept for later reports. |
| `error` | Present when the draw stopped early, with why. |

A draw passes when every `expect` held and it reached its end.
