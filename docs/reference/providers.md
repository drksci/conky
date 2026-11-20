---
kind: reference
title: Providers
status: current
date: 2026-11-20
source: maintainers
---

# Providers

This page specifies the provider page, the two wire formats and how secrets are found. A provider is an ordinary page whose fields describe how to reach a model. A watch entry or `conky ask` names it, so changing a vault's model means editing one page ([decision 0019](../decisions/0019-providers-are-pages.md)). How a question is asked is in [rules and reactions](rules-and-reactions.md#asking-a-model).

## The provider page

```yaml
---
api: openai
url: https://openrouter.ai/api/v1/chat/completions
model: some/model-name
secret: openrouter
max_tokens: 400
---
```

| Field | Meaning |
|---|---|
| `api` | The wire format: `openai` or `anthropic`. Required. |
| `url` | The full address that requests are posted to, beginning `http://` or `https://`. Required. |
| `model` | The model's name, sent as it is written. Required. |
| `secret` | The name of a secret, never the secret itself: lowercase letters, digits, `-` and `_`. Optional. Without it no credential is sent. |
| `max_tokens` | The most tokens the model may write, a positive whole number. Optional. |

Other fields and the body are ignored, so a provider page can carry notes. Rules constrain provider pages like any page, for example a space that allows only approved model names.

A missing page or a malformed field refuses the question with a reason that starts `model:` and names the field to correct.

## The two wire formats

The request is a single POST with a JSON body. The prompt is sent as one user message, with no system prompt or tools, and nothing streams. The call times out after 60 seconds of silence and is not retried.

### openai

Chat completions, used by most hosted providers and by local servers.

- Body: `{"model": ..., "messages": [{"role": "user", "content": <prompt>}]}`, plus `"max_tokens"` when the page sets it.
- Header: `Authorization: Bearer <secret>`, only when the page names a secret.
- Answer: `choices[0].message.content`.
- Token counts: `usage.prompt_tokens` and `usage.completion_tokens`, when present.

### anthropic

Messages.

- Body: `{"model": ..., "max_tokens": ..., "messages": [{"role": "user", "content": <prompt>}]}`. `max_tokens` is the page's value, or 1024 when the page sets none.
- Headers: `x-api-key: <secret>`, only when the page names a secret, and `anthropic-version: 2023-06-01`.
- Answer: the first block of `content` whose type is `text`.
- Token counts: `usage.input_tokens` and `usage.output_tokens`, when present.

An answer is its text, trimmed. A reply that is not JSON, or has no answer text or empty text, is a failure.

## Secrets

A secret is looked up by name, in this order:

1. The environment variable `CONKY_SECRET_<NAME>`, where `<NAME>` is the secret's name in upper case. The secret `openrouter` is read from `CONKY_SECRET_OPENROUTER`.
2. The file `<name>.secret` in the key directory, the one that holds signing keys (`--keys`, default `~/.conky/keys`). Surrounding white space is trimmed.

The secret never enters the vault: not a page, a trailer, a commit message or a refusal. A cloned vault carries no secret and verifies and reads without one. If the secret cannot be found, the question is refused with a reason that names both places.

## Example settings

These map the two formats onto common cases. They are examples, not tested integrations: only stand-in servers on the local machine have tested them. Check each value against the service's own documentation.

| Case | `api` | `url` | `model` | `secret` |
|---|---|---|---|---|
| A hosted service that follows the OpenAI chat completions format | `openai` | `https://api.example.com/v1/chat/completions` | the service's model name | the name of the key |
| A local server that follows the OpenAI format, on the same machine | `openai` | `http://localhost:8080/v1/chat/completions` | the name the server was started with | none |
| The Anthropic messages format | `anthropic` | `https://api.anthropic.com/v1/messages` | the model name | the name of the key |

The host in the first row is a placeholder. The port and path in the second row are those of one common local setup and vary by server.
