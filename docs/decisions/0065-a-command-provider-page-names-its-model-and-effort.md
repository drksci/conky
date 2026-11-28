---
kind: decision
title: A command provider page names its model and effort
status: accepted
date: 2026-11-28
source: maintainers
arch:
  covers:
  - part.provider.detect
  - flow.ask.model
---

# 0065 A command provider page names its model and effort

## Context

- A background thought should be cheap and a character's own answer dearer, in one vault and one run. Two pages that ask through two provider pages should be answered by two different models at two different efforts ([model pages](../ideas/model-pages.md): "different pages can use different ones").
- A provider page of `api: command` already carried `model`, but only the built-in `claude` was told it. A configured command was run as written and told nothing, and no setting for effort existed anywhere. The only way to choose a model or an effort for a program was an environment variable that holds for the whole process.
- The cache key held the model but no effort, so once an effort is told, an answer given at one effort would be replayed for another.

## The walk

1. **The image.** A restaurant order slip. The kitchen is not told how the dish is cooked by the table; each slip says how hot and how long, and two slips in one evening are cooked two ways.
2. **The general case.** A caller tells a child program its settings for one call, and the program that cares reads them.
3. **Existing words.** A provider page, a field, a trailer, an environment variable, a constant declared with `arch.constant`. Left over: the word `effort` and two variable names.
4. **The natural gesture.** Writing `effort: low` on the page that already says which model.
5. **Par.** The `claude` program takes `--model` and `--effort` with `low`, `medium`, `high`, `xhigh` and `max` (`claude --help`, read 2026-11-28). The chat completions reference of one hosted service takes `reasoning_effort` with `none`, `minimal`, `low`, `medium`, `high`, `xhigh` and `max`, and says not every model supports every value (read 2026-11-28 from its API reference). The levels differ by program and by model, so no list of levels belongs to the general form. A parent telling a child program its context through environment variables is the convention of Git hooks, which are given `GIT_DIR` and `GIT_PUSH_OPTION_*` ([githooks](https://git-scm.com/docs/githooks), read 2026-11-28).
6. **Who does it.** A character can write a provider page, and so can name an effort for it. The runtime only has to pass it on.
7. **The trial.** The card `a-clerk-has-a-small-ear`: an ear that asks a small model at low effort, and a clerk that asks at medium effort. Forecast 5 of 5; a miss would be the small model keeping another line from the one asked about. It is not drawn live.
8. **How it is seen.** The commit of an answer carries `Model-Name` and `Effort`, so `conky log` shows which model and effort gave each answer.
9. **The smallest step.** Built now: the field, the two variables, the trailer, the cache key. Waiting: the order of providers as data, which is R34.

## Decision

- `effort` is a field of a provider page of `api: command`. It is one plain word of letters, digits and hyphens, and it is optional. Without it nothing about effort is told or recorded.
- The provider page carries it, and the asking page does not: an asking page chooses by naming a provider page in its `ask`, so two models in one run are two provider pages, and no field is added to the asking page or to `ask`.
- Every command provider is started with two variables set for that one process, `CONKY_ASK_MODEL` and `CONKY_ASK_EFFORT`, each only when the page names one. Nothing else of the environment changes. A configured command is still run as written and its argv is unchanged; a program or a wrapper that wants them reads them.
- Each built-in names, in its own entry of `BUILTIN_OPTIONS`, the options it takes for a model and for an effort, and the efforts it accepts. `claude` takes `--model`, and `--effort` with `low`, `medium`, `high`, `xhigh` and `max`. `codex` takes neither (unverified: it is not installed where this was written), so an `effort` on a `codex` page is a `model:` failure at the ask whose reason says what to do. There is no list of levels outside a program's own entry, so the general form carries no one vendor's vocabulary.
- A provider page of `api: command` is checked when it is written, on the page as it would be after the write: `model`, when present, is text that is not empty; `effort`, when present, is one plain word, and for a built-in with a list of levels it is one of them. A page with an `effort` and another `api` is refused. A page with no `api` is not a provider page and may carry any field called `effort`. The rest of a provider page is still checked only at the ask, as before, and `provider()` checks the same at the ask for a page written before this.
- An answer's commit carries a new trailer `Effort` beside `Model-Name`, only when an effort was told.
- The cache key gains the effort only when there is one, so every key of a page without it is the key it was.

## What the old behaviour guaranteed

- A page with no `effort` is started with the argv it always had, and `claude` gets `ANTHROPIC_DEFAULT_MODEL` when no model is named: kept by `tests/test_command.py` and `tests/test_effort.py`.
- A configured command is run as written: kept by `tests/test_command.py`.
- A page never supplies an argv: the options come from the table in code, and the page gives a model name and one word, each passed as one argv word with no shell: kept by `tests/test_command.py`.
- Every existing cache key is unchanged: kept by a test that holds one known key.
- A malformed provider page that is not a command one, or has no `effort`, is written and refused at the ask: kept by `tests/test_model.py` and `tests/test_command.py`.
- A secret never enters a vault: the two variables carry a model's name and an effort, never a secret; kept by `tests/test_effort.py`.

## Consequences

- A cheap page and a dear one answer in one vault in one run, and each answer records what it was given.
- A person who gives a program through `CONKY_COMMAND_<NAME>` is told nothing in its argv; its wrapper reads the variables. A page that names `claude` with a configured command still has its effort checked against the levels of `claude`.
- Not verified: no live call at a named effort. The `codex` form is told neither.
