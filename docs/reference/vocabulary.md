---
kind: reference
title: Vocabulary
status: current
date: 2026-11-20
source: maintainers
---

# Vocabulary

This page lists every name Conky has: the plain words that name its concepts, and every name the runtime exposes. It is the one place a new name is introduced ([decision 0027](../decisions/0027-the-vocabulary-is-what-exists.md)). `tests/test_house.py` reads the tables below and compares each with the code in both directions. A name in the code with no row here fails, and a row here that the code no longer has fails. A rename changes the code and this page in the same change.

The runtime also searches the `PATH` for programs and uses the home directory for the default key folder.

## Concepts

| Name | Meaning |
|---|---|
| `vault` | A Git repository whose commits are the history and whose files are the pages. |
| `page` | A Markdown file with frontmatter: a character with fields, rules, watches and a body. |
| `key` | A signing key that belongs to one actor and never enters the vault. |
| `link` | A page name written in a page so that one page points at another. |
| `embed` | `![[page]]`, replaced by a field, a body or, for a space, the list of its members when a page is read. `#` selects the part. |
| `rule` | An expression the runtime evaluates before a write is kept. |
| `event` | A commit: one write or one refusal. |
| `seal` | The signature on an event. |
| `space` | A page that other pages lie within, handing down its rules. |
| `error` | A message that says what went wrong and what to do next. |

## Verbs

| Name | Meaning |
|---|---|
| `read` | Return a page with its embeds resolved. |
| `write` | Commit a change to a page, or commit the refusal of it. |
| `watch` | Name a page whose writes make this page react. |

## Commands

| Name | Meaning |
|---|---|
| `init` | Create an empty vault. |
| `write` | Write fields and a body to a page. |
| `ask` | Ask a model and write the answer to a field of a page. |
| `model` | Print which model an ask without a provider would use. |
| `cache` | Show the cache of costly answers, or clear it. |
| `read` | Print a page with embeds resolved. |
| `log` | Print the history, oldest first. |
| `verify` | Check the tree, the objects, the seals and the history. |
| `rebuild` | Restore the working tree to the committed state. |
| `connect` | Run a connector beside the vault. |
| `demo` | Build a small example vault and show it working. |
| `assimilate` | Take over a stopped vault from its folder alone. |
| `export` | Show a vault's committed pages in another form, under `dist/`. |

## Global options

| Name | Meaning |
|---|---|
| `--vault` | The vault directory. |
| `--keys` | The directory that holds private keys. |
| `--cache-dir` | The directory that holds the cache. |
| `--cache-mode` | What the cache may do: `on`, `off`, `refresh` or `only`. |
| `--color` | Whether output is styled: `auto`, `always` or `never`. |

## Command options

| Name | Meaning |
|---|---|
| `write --body` | The new body of the page. |
| `write --as` | The actor that makes the write. |
| `ask --provider` | The page that describes the model. |
| `ask --writes` | The space the answer may write pages into. |
| `ask --prompt` | The question, with embeds resolved. |
| `ask --as` | The actor that makes the write. |
| `demo --into` | The folder to create. |
| `demo --list` | List the examples and do nothing else. |
| `assimilate --into` | The folder to create. |
| `assimilate --as` | The name of the new actor. |
| `assimilate --then` | A write to make as the new actor, repeatable. |
| `export --out` | The folder to write, in place of `dist/<form>/`. |
| `connect terminal --as` | The connector's actor name. |
| `connect terminal --screen` | The page that receives the screen. |
| `connect terminal --hands` | The page that says what to type. |
| `connect terminal --settle` | Seconds of quiet that end a screen. |
| `connect terminal --max-steps` | The most screens to write. |
| `connect terminal --first-line` | Type only the first non-empty line of the keys. |

## Connectors

| Name | Meaning |
|---|---|
| `terminal` | Gives a vault eyes and hands on a terminal program. |

## Reserved keys

| Name | Meaning |
|---|---|
| `within` | The space a page lies within. |
| `rules` | The list of rules a page and the pages in its space must satisfy. |
| `watch` | The list of watch entries that say how a page reacts. |

## Watch keys

| Name | Meaning |
|---|---|
| `on` | The page whose writes this entry reacts to, or a relation. |
| `when` | The expression that must hold for the entry to act. |
| `set` | Fields to write, each from an expression. |
| `ask` | A question to put to a model, in place of `set`. |

## Watch relations

| Name | Meaning |
|---|---|
| `within` | Reacts to a write of any page within the watching page, at any depth. |
| `link` | Reacts to a write of a page whose text links to the watching page. |
| `refusal` | Reacts to a refused write to the watching page, by it, or within it. |

## Ask keys

| Name | Meaning |
|---|---|
| `prompt` | The question, with embeds. |
| `into` | The field that receives the answer. |
| `provider` | The provider page to try first. |
| `otherwise` | The text to write when no model answers. |
| `writes` | The space the answer may write pages into. |

## Trailer keys

| Name | Meaning |
|---|---|
| `Kind` | `write` or `refused`. |
| `Page` | The page the event concerns. |
| `Cause` | The event whose reaction this is. |
| `Reason` | Why a write was refused. |
| `Attempt` | The refused change as compact JSON. |
| `Body-Bytes` | The size of the body a refused write tried to set. |
| `From` | The space whose rule refused the write. |
| `Model` | The provider page that answered, or `none`. |
| `Model-Name` | The model's name. |
| `Tokens-In` | Tokens in the prompt, when the provider reports them. |
| `Tokens-Out` | Tokens in the answer, when the provider reports them. |
| `Read` | A page embedded in the prompt. |
| `Cache` | `hit` when the answer came from the cache and was not paid for again. |

## Kinds

| Name | Meaning |
|---|---|
| `write` | An event that changed a page. |
| `refused` | An event that records a write that was not kept. |

## Refusals

| Name | Meaning |
|---|---|
| `cycle` | Reactions nested deeper than the limit. |
| `shape` | A write would give a page a malformed reserved key. |
| `rule` | A rule was false, could not be evaluated or came from a space that is missing or loops. |
| `watch` | A watch expression failed to evaluate. |
| `model` | A named provider could not be asked or did not answer. |
| `limit` | A page written by an answer broke a limit of the space it was given. |

## Errors

| Name | Meaning |
|---|---|
| `BadInput` | The caller passed something that cannot be a name, a value or a page. |
| `VerifyFailed` | The vault does not verify. |
| `ModelError` | A model could not be asked or did not answer. |
| `ShapeError` | A write would give a page a malformed reserved key or field. |
| `RuleError` | A rule or expression could not be evaluated. |

## Cache modes

| Name | Meaning |
|---|---|
| `on` | Read the cache before asking and write what is paid for. |
| `off` | Neither read nor write the cache. |
| `refresh` | Ignore existing entries and write new ones. |
| `only` | Never call a provider: a miss falls to the plain sentence. |

## Provider shapes

| Name | Meaning |
|---|---|
| `openai` | The chat completions wire format. |
| `anthropic` | The messages wire format. |
| `command` | A named program that reads the prompt on standard input. |

## Provider choices

| Name | Meaning |
|---|---|
| `anthropic` | The `anthropic` shape with `ANTHROPIC_API_KEY`. |
| `openai` | The `openai` shape with `OPENAI_API_KEY` and `CONKY_MODEL`. |
| `claude` | The built-in command `claude` on the `PATH`. |
| `codex` | The built-in command `codex` on the `PATH`. |
| `none` | No model, so an ask writes a plain sentence. |

## Built-in commands

| Name | Meaning |
|---|---|
| `claude` | Runs `claude -p`. |
| `codex` | Runs `codex exec`. |

## Environment variables

| Name | Meaning |
|---|---|
| `CONKY_PROVIDER` | Which detected model goes first, or `none`. |
| `CONKY_MODEL` | The model name for a detected `openai` choice, or an override for `anthropic`. |
| `ANTHROPIC_API_KEY` | The key for the detected `anthropic` choice. |
| `OPENAI_API_KEY` | The key for the detected `openai` choice. |
| `CONKY_SECRET_<NAME>` | The secret called `<name>` that a provider page names. |
| `CONKY_COMMAND_<NAME>` | The program and options for the command called `<name>`. |
| `CONKY_CACHE` | The cache mode, the same as `--cache-mode`. |
| `CONKY_CACHE_DIR` | The cache directory, the same as `--cache-dir`. |
| `CONKY_CACHE_MAX` | The most megabytes the cache keeps. |
| `NO_COLOR` | Turns styling off under `--color auto`. |
| `TERM` | Passed to a program run by `connect terminal`. |
