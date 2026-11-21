---
kind: idea
title: Pages that ask a model
status: enforced
date: 2026-11-20
source: maintainers
arch:
  covers:
  - flow.ask.model
  - kind.provider
  - stage.think.ask
  items:
  - kind: stage
    name: stage.think.context
    phase: think
    text: Context richer than the embeds of one prompt, and a model's answer marked as an unchecked claim, are open questions.
    state: idea
    roadmap: R17
---

# Pages that ask a model

## Idea

A page can pose a question state cannot answer to an AI model and write the answer back as an ordinary signed change, so the answer is recorded, attributable and subject to the same rules as any write. Calls happen only when state cannot answer ([decision 0007](../decisions/0007-inference-for-real-thinking.md)).

A provider is itself a page: it names an endpoint and a model, and its secret key stays outside the vault, like signing keys. A page that needs a model points at a provider page, so changing provider is editing one page, and different pages can use different ones (a cheap one for housekeeping, a strong one for hard questions).

A page may carry a budget of asks, counted from the history, with an ask past it refused for `limit` and refilled by writing the budget again ([decision 0058](../decisions/0058-a-budget-the-runtime-holds.md)). Tokens and money are not metered.

## Composes from

Page, key, write, watch, rule.

## Removes

Provider-specific code paths and prompts scattered in code.

## Falsifying test

The same vault runs unchanged against two providers by editing one page. Every model answer appears in history with the question that caused it. With the provider unreachable, everything that does not need a model still works.

## What was built

- A provider is an ordinary page with `api`, `url`, `model`, an optional `secret` and an optional `max_tokens`. The secret is a name, looked up in the environment or in a file in the key directory, and never enters the vault. See [providers](../reference/providers.md).
- A watch entry may carry `ask` in place of `set`. The resolved prompt is sent once, and the answer is written to a field of the asking page as an ordinary signed write that carries `Cause`. A question already answered for the same resolved prompt is skipped. See [rules and reactions](../reference/rules-and-reactions.md#asking-a-model).
- The commit records `Model`, `Model-Name`, token counts when the provider reports them, and the resolved prompt as its message body ([vault format](../reference/vault-format.md#a-model-answer)).
- A failure to ask is a refusal with a reason that starts `model:`. The write that triggered it stands.
- `conky ask` is the one-off form ([command line](../reference/cli.md#ask)).
- Two wire formats are supported, `openai` and `anthropic`, using the standard library only.

The tests in `tests/test_model.py` run a real HTTP server on the local machine in each wire format. They cover the falsifying test with stand-in servers in place of real providers: the same watch entry is answered in the other wire format after one provider page is edited. No live provider has been called.

Decision: [0019](../decisions/0019-providers-are-pages.md).

## Open questions

- Cost limits. Token counts are recorded when reported, and nothing bounds the spend.
- Treating a model's claim as unverified, so an answer is not read as checked fact.
- Assembling richer context than the embeds of one prompt.
