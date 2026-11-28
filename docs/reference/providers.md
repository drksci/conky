---
kind: reference
title: Providers
status: current
date: 2026-11-20
source: maintainers
---

# Providers

This page specifies the provider page, the three shapes, how secrets and commands are found, how a model is detected when none is named, and what happens when no model answers. A provider is an ordinary page whose fields describe how to reach a model. A watch entry or `conky ask` names it, so changing a vault's model means editing one page ([decision 0019](../decisions/0019-providers-are-pages.md)). How a question is asked is in [rules and reactions](rules-and-reactions.md#asking-a-model).

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
| `api` | The shape: `openai`, `anthropic` or `command`. Required. |
| `url` | The full address that requests are posted to, beginning `http://` or `https://`. Required for `openai` and `anthropic`. |
| `model` | The model's name, sent as it is written. Required for `openai` and `anthropic`. |
| `command` | For `command` only: the name of a program, never a command line. See [command](#command). |
| `effort` | For `command` only: how hard the model is to try, one plain word of letters, digits and hyphens, as in `effort: low`. Optional. See [command](#command). |
| `secret` | The name of a secret, never the secret itself: lowercase letters, digits, `-` and `_`. Optional. Without it no credential is sent. |
| `max_tokens` | The most tokens the model may write, a positive whole number. Optional. |

A page of `api: command` is checked when it is written: `model`, when present, must be text that is not empty, and `effort`, when present, must be one plain word, and for a built-in program it must be one the program accepts. A page of another `api` that has an `effort` is refused, because only a program is told one. The rest of a provider page is checked when it is asked. Other fields and the body are ignored, so a provider page can carry notes. Rules constrain provider pages like any page, for example a space that allows only approved model names.

A missing page or a malformed field is recorded as a refusal with a reason that starts `model:` and names the field to correct. What happens next is in [when no model answers](#when-no-model-answers).

## The wire formats

The `openai` and `anthropic` shapes send a request is a single POST with a JSON body. The prompt is sent as one user message, with no system prompt or tools, and nothing streams. The call times out after 60 seconds of silence and is not retried.

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

### command

A program on the machine, for people who already have a model client installed. The page names the program, never a command line:

```yaml
---
api: command
command: claude
---
```

- `command` must be a plain name: lowercase letters, digits, `-` and `_`, starting with a letter or digit. Anything else, such as `rm -rf /`, `/bin/sh` or a list, is a malformed page. A page never supplies an argument list, so a vault cannot make a machine run anything. Other fields on the page are ignored.
- The prompt is written to the program's standard input. The answer is its standard output with trailing white space trimmed.
- The program and its arguments come from outside the vault, resolved like a secret: the environment variable `CONKY_COMMAND_<NAME>` (the name in upper case), then the file `<name>.command` in the key directory. The text is split into words with shell quoting rules and run directly, never through a shell. `CONKY_COMMAND_ECHO='python3 /path/echo.py'` runs `python3` with one argument.
- Two names are built in and need no setup when the program is on the PATH: `claude` runs `claude -p --no-session-persistence` with its tools, its tool servers, its commands and the machine's own settings (hooks and plugins) switched off, and saves no session and its own instructions replaced by one line saying the prompt is all there is, and `codex` runs `codex exec`. The `claude` form is given `--model` with `ANTHROPIC_DEFAULT_MODEL`, or with the model the page names, and `codex` is given none. Every command provider is started in an empty folder, so the program finds no project files or instructions where it starts: a model sees its prompt and nothing else. A program given through the environment variable or the file is run as written, so anyone who sets one is responsible for switching its tools off. The environment variable and the file win over them. The `claude` form was checked against `claude --help` and a live call, see [status](../project/status.md). The `codex` form is unverified: it was not installed where it was written.
- `model` is optional. For the built-in `claude` it is passed as `--model`, and `ANTHROPIC_DEFAULT_MODEL` is passed when none is named. For any other program it is used only as the name recorded in the commit. `max_tokens` is ignored.
- `effort` is optional and names how hard the model is to try. Each built-in names its own options: `claude` takes `--effort` with `low`, `medium`, `high`, `xhigh` or `max`, and `codex` takes none, so an `effort` on a `codex` page is a `model:` failure whose reason says to remove it or to give the program through `CONKY_COMMAND_CODEX`. A program given through the environment variable or the file takes any one plain word. Without an `effort` nothing about effort is told or recorded.
- Every command provider is started with two variables set for that one process and no other change to its environment: `CONKY_ASK_MODEL`, the page's `model`, and `CONKY_ASK_EFFORT`, the page's `effort`, each only when the page names one. A program or a wrapper run as written, which is given no option for either, reads them. Two pages that name two models or two efforts are answered by two different runs, so a cheap page and a dear one answer in one vault in one run. Nothing else is passed to the program.
- The call times out after 120 seconds and is not retried. A non-zero exit, an empty answer, a timeout and a program that cannot be started are failures. A name that cannot be resolved is a failure whose message says which variable to set.
- Token counts are not known, so `Tokens-In` and `Tokens-Out` are left out.

An answer is its text, trimmed. A reply that is not JSON, or has no answer text or empty text, is a failure.

## Secrets

A secret is looked up by name, in this order:

1. The environment variable `CONKY_SECRET_<NAME>`, where `<NAME>` is the secret's name in upper case. The secret `openrouter` is read from `CONKY_SECRET_OPENROUTER`.
2. The file `<name>.secret` in the key directory, the one that holds signing keys (`--keys`, default `~/.conky/keys`). Surrounding white space is trimmed.

The secret never enters the vault: not a page, a trailer, a commit message or a refusal. A cloned vault carries no secret and verifies and reads without one. If the secret cannot be found, the question is refused with a reason that names both places.

## Detection

When a watch `ask` or `conky ask` names no provider, Conky detects one from the environment and the PATH. It never reads the vault. The order is:

1. `CONKY_PROVIDER`, when it is `anthropic`, `openai`, `claude` or `codex`: that model goes first. `none` turns detection off. Any other value is ignored, and `conky model` says so.
2. `ANTHROPIC_API_KEY` set: the `anthropic` shape with model `claude-sonnet-5-5`, or `CONKY_MODEL` when set.
3. `OPENAI_API_KEY` set and `CONKY_MODEL` set: the `openai` shape against `https://api.openai.com/v1/chat/completions`. No default OpenAI model id has been verified, so without `CONKY_MODEL` this step is skipped and `conky model` says why.
4. `claude` on the PATH: the `claude` command.
5. `codex` on the PATH: the `codex` command.

The default Anthropic model id is the constant `ANTHROPIC_DEFAULT_MODEL` in `src/conky/model.py`, taken from the current model table of the Claude API documentation. A key is read straight from `ANTHROPIC_API_KEY` or `OPENAI_API_KEY`, so it is never copied anywhere. `CONKY_MODEL` does not change a command.

The commit of a detected answer records `Model` as `detected:<kind>`, for example `detected:claude`, and `Model-Name` as the model passed to the built-in `claude`, or else the model or command name, and `Effort` when the page named one. `conky model` prints the order that applies now and calls nothing.

### What conky model found

After that order, `conky model` prints what this machine offers, one finding to a line with where it was seen: `ANTHROPIC_API_KEY is set (the environment, by name)`, `claude is on the PATH (PATH)`. The look is read-only. It asks whether `ANTHROPIC_API_KEY` or `OPENAI_API_KEY` is set (by name, never the value), whether `claude`, `codex`, `llm`, `ollama`, `bwrap`, `docker` or `podman` is on the PATH, whether `CLAUDECODE` is set, and whether `127.0.0.1:11434`, the default address of `ollama`, answers within 0.3 seconds. It installs nothing, starts nothing, sends nothing off the machine and writes no file. The list is the constant `PROBE` in `src/conky/model.py`. Findings are shown as found: `llm`, `ollama` and the sandbox programs are not used, and the order above does not change. With nothing found it says so.

## When no model answers

Asking never blocks work. These are the cases:

| Case | What happens |
|---|---|
| A provider page is named and answers | Its answer is written. Detection is not used. |
| A provider page is named and fails: page missing, malformed, secret or command not found, network error, timeout, non-zero exit, empty answer | A refusal with reason `model: ...` is recorded against the asking page, as before. Then the detected models are tried in order. |
| No provider is named, and a detected model fails | The next detected model is tried. Nothing is recorded for the failed one. |
| Every model failed, or none is available (nothing configured, no key, no client on the PATH, or `CONKY_PROVIDER=none`) | A plain sentence is written to the `into` field. The watch entry's `otherwise` text is used when it has one, with embeds resolved. Otherwise the built-in sentence is used. |

The built-in sentence is `No model was around to answer "<question>", so <page> keeps this line in <field> until one is.` The question is the resolved prompt on one line, cut to 60 characters at a word boundary with `...` when longer.

A plain sentence is written as an ordinary signed write with the trailer `Model: none`, the resolved prompt as the commit body and the usual `Read` trailers, and no `Model-Name`. The field `<into>_asked` is not written, so the question is not settled: the next time the entry fires and a model is available, it is asked for real and the answer replaces the sentence. `conky ask` with no model prints the sentence on standard output and a one-line hint listing the ways to give Conky a model on standard error, and exits 0.

A key directory that does not exist means no secret and no command file, not an error. A secret or command file that cannot be read as text is a failure with a message that names the file.

## Cache

A question is paid for once. Before any provider is called, Conky looks for the answer in a cache of costly answers ([decision 0030](../decisions/0030-pay-once.md)). The cache is derived data: it lives in `~/.conky/cache` beside the keys, never inside a vault and never in its history, and it can be deleted at any time. A vault verifies and behaves the same without it, and only the cost of asking again changes.

The key of an entry is the hash of:

- the provider's shape, its `url` or `command` name, its `model`, its `effort` when it names one, and the most tokens it may write (1024 for `anthropic` when the page sets none);
- the whole prompt as sent, including the instruction added when the entry may write pages;
- the cause of the question: the commit that made a watch entry react, or for `conky ask` the latest commit of the vault.

The page's name and the secret's name are not in the key. Because the cause is in it, the same words asked after a new event are asked afresh, and a character does not repeat itself. The same question for the same event is not paid for twice, as in a retry after a crash, a replay or a test. The plain sentence and a failed call are never cached.

A commit made from a hit has the usual trailers and one more, `Cache: hit`. It has no `Tokens-In` or `Tokens-Out`, since nothing was spent, so a sum of the token trailers over a history is what was spent.

An entry is a JSON file named by its hash. A write is atomic, and an entry that cannot be read is a miss that the next live call replaces. The cache keeps at most 64 megabytes, or `CONKY_CACHE_MAX` megabytes, and drops the oldest entries first; a hit renews an entry.

| Setting | Meaning |
|---|---|
| `CONKY_CACHE_DIR`, `--cache-dir` | Where the cache is. The option wins. |
| `CONKY_CACHE_MAX` | The most megabytes to keep. |
| `CONKY_CACHE`, `--cache-mode` | `on` reads and writes (the default). `off` does neither. `refresh` ignores existing entries and writes new ones. `only` never calls a provider, so a miss falls to the plain sentence. |

[`conky cache`](cli.md#cache) shows the cache and `conky cache clear` empties it.

## Example settings

These map the formats onto common cases. They are examples, not tested integrations: only stand-in servers on the local machine have tested them. Check each value against the service's own documentation.

| Case | `api` | `url` | `model` | `secret` |
|---|---|---|---|---|
| A hosted service that follows the OpenAI chat completions format | `openai` | `https://api.example.com/v1/chat/completions` | the service's model name | the name of the key |
| A local server that follows the OpenAI format, on the same machine | `openai` | `http://localhost:8080/v1/chat/completions` | the name the server was started with | none |
| The Anthropic messages format | `anthropic` | `https://api.anthropic.com/v1/messages` | the model name | the name of the key |

The host in the first row is a placeholder. The port and path in the second row are those of one common local setup and vary by server.
