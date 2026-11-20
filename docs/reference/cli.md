---
kind: reference
title: Command line
status: current
date: 2026-11-20
source: maintainers
---

# Command line

`conky` is installed by `pip install -e '.[dev]'`. The walkthrough in [getting started](../guide/getting-started.md) uses every command except `demo`, which has its own first section there, and `ask`, which needs a provider.

```
conky [--vault DIR] [--keys DIR] <command> ...
```

## Global options

| Option | Meaning |
|---|---|
| `--vault DIR` | The vault directory. Default: the current directory. |
| `--keys DIR` | The directory that holds private keys. Default: `~/.conky/keys`. |

Both go before the command. `init` takes the vault path as its own argument and ignores `--vault`.

## Commands

### demo

```
conky demo [name] [--into PATH] [--list]
```

Builds a small example vault and narrates it. The examples are data files shipped in the package (`stall` is the default; `team` is the other). Each is a title, a one-line summary and ordered steps, and each step has a plain narration line and one write.

- `name` is the example to run. `--list` prints the examples with their summaries and does nothing else.
- `--into PATH` is the folder to create. Default: `./conky-demo-<name>`. It is an error if the path already exists.
- Private keys go in a `keys` directory beside the vault, unless the global `--keys` is given.

Each step prints its number and narration, then an indented line beginning `->` that says what happened: `written: <page>`, or `refused: <page>, because <reason>`, followed by `Then <page> changed by itself` for each reaction. The output ends with what to look at next: the vault path, the Git history command, and the `read` and `verify` commands. The output is plain text, at most 80 columns apart from paths, with no colour codes. The steps use the real write path, so the vault verifies.

Errors, each on one line beginning `error: `:

- `error: <path> already exists: choose another folder with --into PATH`
- `error: no example named '<name>': run conky demo --list to see the examples`

### init

```
conky init <path>
```

Creates an empty vault at `path`, making the directory if needed, with branch `main` and signing configured. It prints `initialised <path>`. It makes no commit and no key. It is an error if `path` is already a vault.

### write

```
conky write <page> [field=value ...] [--body TEXT] --as <actor>
```

Writes fields and a body to a page and makes one signed commit as `actor`. `--as` is required.

- Each `field=value` sets one field. The value is read as YAML, so `stock=40` is a number, `reorder=false` is a boolean, and `'rules=["page.stock >= 0"]'` is a list. Quote values that the shell would change.
- The reserved names `within`, `rules` and `watch` set the page's space, rules and watch entries. Setting one to nothing clears it.
- `--body` replaces the body. Without it the body is left as it is.
- Fields not named are left as they are.

On success it prints `written (commit <id>)`, where the id is the short commit id. If rules refuse the write it prints `refused (commit <id>): <reason>` on standard error, exits 1, and the refusal is still committed. Reactions that follow a write are committed too and are not printed; see `conky log`.

### ask

```
conky ask <page> <into-field> --provider <provider page> --prompt TEXT --as <actor>
```

Asks a model one question and writes the answer to the field `into-field` of `page`, as a signed commit by `actor`. It takes the same path as a watch entry with `ask` ([rules and reactions](rules-and-reactions.md#asking-a-model)). Embeds in the prompt are resolved, and the provider page named by `--provider` says how to reach the model ([providers](providers.md)). The commit records the question and the model ([vault format](vault-format.md#a-model-answer)). `--provider`, `--prompt` and `--as` are required.

The skip rule does not apply: the question is asked every time. The answer is written together with the field `<into-field>_asked`, which later watch entries use to skip a question they would repeat.

On success it prints `written (commit <id>)`. If the answer breaks a rule, or the model cannot be asked, it prints `refused (commit <id>): <reason>` on standard error and exits 1. The refusal is committed, and its reason starts with `model:` when the cause is the provider, the secret or the network. A write by the actor needs the actor's key, as for `write`.

### read

```
conky read <page>
```

Prints the page as stored, with embeds resolved. It is an error if the page does not exist.

### log

```
conky log
```

Prints the history, oldest first, one line per commit: short id, instant in UTC, actor, kind, page, then the reason for a refusal or `cause <id>` for a reaction. A line for a model answer ends with `model <provider page>`. An empty vault prints nothing.

### verify

```
conky verify
```

Checks the vault as described in [vault format](../reference/vault-format.md#what-verify-checks). It prints `ok: <n> commits verified` on success. On failure it prints `error: <first problem>` and exits 1.

### rebuild

```
conky rebuild
```

Restores the working tree to the committed state and prints `restored the working tree from the committed history`.

## Exit codes

| Code | Meaning |
|---|---|
| 0 | The command succeeded. |
| 1 | The write was refused, or the command failed: bad input, a missing page or vault, a missing tool, or a vault that does not verify. |
| 2 | The command line itself could not be parsed, for example a missing `--as`. The usage message is printed. |

## Errors

Every failure of the kinds above prints one line on standard error beginning `error: ` and says what to do next where there is something to do, for example:

- `error: <path> is not a vault: create one with conky init <path>`
- `error: the working tree has changes that were not made through conky: run conky --vault <path> rebuild to discard them`
- `error: no private key for '<actor>' in <dir>: pass --keys <directory>`
- `error: invalid name '<name>': use lowercase letters, digits, '-' and '_'`
- `error: expected field=value, got '<text>'`

A write is not attempted while the working tree has changes made outside conky.

## Time

The command line is the only place the clock is read. It stamps each write with the current time in UTC, to the second. The library takes the instant from its caller.
