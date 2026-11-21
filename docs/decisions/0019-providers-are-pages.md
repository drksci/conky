---
kind: decision
title: Providers are pages
status: accepted
date: 2026-11-20
source: maintainers
arch:
  covers:
  - law.provider.page
  - kind.provider
  - flow.ask.model
  - stage.think.budget
---

# 0019 Providers are pages

## Context

- [Decision 0007](0007-inference-for-real-thinking.md) says a model is asked only what state cannot answer, but not how a page asks.
- The risks are a new word in the vocabulary, provider-specific code scattered through the runtime, a secret leaking into a history meant to be shared, and answers that cannot be read later without calling the model again.
- Two wire formats cover most services: the chat completions format that most hosted providers and local servers accept, and the Anthropic messages format. Both are a single JSON request and a single JSON reply.

## Decision

A model is reached through a provider page, and a question is asked by a watch entry. Nothing is added to the vocabulary.

- A provider is an ordinary page with the fields `api` (`openai` or `anthropic`), `url`, `model`, an optional `secret` and an optional `max_tokens`. A rule can constrain provider pages like any page.
- The `secret` field holds the name of a secret. The value is looked up by name in the environment variable `CONKY_SECRET_<NAME>`, then in the file `<name>.secret` in the key directory. It is never written to the vault.
- A watch entry may carry `ask` (`provider`, `prompt`, `into`) in place of `set`. When it fires, embeds in the prompt are resolved as on read and the provider is called once. The trimmed answer is written to the `into` field of the watching page as an ordinary write by that page, with `Cause`. Rules apply to it, and a refused answer is recorded as a refusal.
- A question is skipped when `into` already holds an answer for the same resolved prompt. A hash of the resolved prompt is kept in `<into>_asked`. This stops a settled question being asked twice and lets loops end. The reaction depth limit of 12 still applies.
- The commit for an answer carries `Model`, `Model-Name` and, when the provider reports them, `Tokens-In` and `Tokens-Out`. The resolved prompt is the commit message body, so the question is in history beside the answer.
- A failure to ask is a refusal on the asking page with a reason that starts `model:` and says what to do next. The write that triggered the entry stands and other reactions run. The call times out after 60 seconds and is not retried.
- `conky ask` is a one-off question by an actor, through the same path.
- The call uses the standard library only, in one small module: one POST per question, with no streaming, no system prompt and no tools.

This builds on the two public formats, which providers and local servers already implement, rather than a client library for each.

## Consequences

- Changing provider is editing one page, and different pages can use different providers.
- Secrets stay outside the history, as private keys do. A cloned vault verifies and reads with no secret and no network.
- An answer is a recorded write, so history is read without a model. A model's output counts as a claim made by a page, not as a checked fact: nothing yet marks the difference.
- Only the two formats are supported. A service with another format needs a new `api` value and a decision.
- The behaviour has been tested against stand-in servers on the local machine. It has not been run against a live provider.
- Cost is recorded as token counts when the provider reports them. Nothing limits it. Because a question is skipped only when its resolved prompt is unchanged, a prompt that embeds its own answer is asked repeatedly until the depth limit.

## Open questions

- How cost is bounded: per page, per period, or per vault.
- How a model's claim is kept from being read as verified fact.
- How richer context is assembled for a question than the embeds of one prompt.

See [pages that ask a model](../ideas/model-pages.md).
