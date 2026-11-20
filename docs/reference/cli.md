---
kind: reference
title: Command line
status: current
date: 2026-11-20
source: maintainers
---

# Command line

`conky` is installed by `pip install -e '.[dev]'`. The walkthrough in [getting started](../guide/getting-started.md) uses every command except `demo` and `assimilate`, which have their own sections there, `ask`, which needs a provider, and `connect`, which is shown in [playing a program](../guide/playing-a-program.md).

```
conky [--vault DIR] [--keys DIR] [--color WHEN] <command> ...
```

## Global options

| Option | Meaning |
|---|---|
| `--vault DIR` | The vault directory. Default: the current directory. |
| `--keys DIR` | The directory that holds private keys. Default: `~/.conky/keys`. |
| `--color WHEN` | `auto`, `always` or `never`. Default: `auto`. |

All go before the command. `init` takes the vault path as its own argument and ignores `--vault`.

## Colour and styled output

In a terminal, conky styles its output with rounded boxes, small coloured badges and the symbols `✓`, `✗`, `↳`, `●` and `○`. The wording is the same as the plain output, with a badge in place of some labels, so no state is shown by colour alone. Styled output needs a terminal that supports 24-bit colour.

- `--color auto` styles output only when it goes to a terminal and the environment variable `NO_COLOR` is not set. This is the default.
- `--color always` styles output even when it is piped or redirected, for example to capture it.
- `--color never` prints plain text.
- `NO_COLOR` set to any value turns styling off under `auto`. An explicit `--color always` overrides it.

Styled output is for people. Plain output is the stable form for scripts: it is what every other section of this page describes, and it has no escape codes. Anything that reads conky output should run it with output piped or with `--color never`. The styled layout can change between releases. Styled lines wrap to the terminal width, at most 88 columns.

## Commands

### demo

```
conky demo [name] [--into PATH] [--list]
```

Builds a small example vault and narrates it. The examples are data files shipped in the package (`lemonade` is the default; `team` is the other). Each is a title, a one-line summary and ordered steps, and each step has a plain narration line and one write.

- `name` is the example to run. `--list` prints the examples with their summaries and does nothing else.
- `--into PATH` is the folder to create. Default: `./conky-demo-<name>`. It is an error if the path already exists.
- Private keys go in a `keys` directory beside the vault, unless the global `--keys` is given.

Each step prints its number and narration, then an indented line beginning `->` that says what happened: `written: <page>`, or `refused: <page>, because <reason>`, followed by `Then <page> changed by itself` for each reaction. The output ends with what to look at next: the vault path, the Git history command, and the `read` and `verify` commands. The plain output is at most 80 columns apart from paths, with no colour codes. In a terminal the same content is styled: a box holds the title and summary, each step number is a small badge, results carry `✓ written` and `✗ refused` badges, and a reaction is a line beginning `↳`. See [colour and styled output](#colour-and-styled-output). The steps use the real write path, so the vault verifies.

Errors, each on one line beginning `error: `:

- `error: <path> already exists: choose another folder with --into PATH`
- `error: no example named '<name>': run conky demo --list to see the examples`

### assimilate

```
conky assimilate [source] [--into PATH] [--as ACTOR] [--keys DIR] [--then PAGE FIELD=VALUE ...]
```

Takes over a stopped vault from its folder alone, checks it and carries on from where it stopped. It is the mechanical form of the [assimilation test](../ideas/assimilation-test.md): no model is involved, so it shows that the state travels and resumes, and it says nothing about how an agent behaves. In the [evaluation plan](../research/evaluation-plan.md) it is a mechanism result.

- `source` is the vault to take over: a path to a vault directory, a path to a Git bundle, or a URL that `git clone` accepts. Without it, a small stopped vault that ships in the package is used, so the bare command works anywhere. That vault is the `lemonade` example stopped before the busy hour: the stand, the cooler and the supplier exist, and one write has been refused.
- `--into PATH` is the folder to create. Default: `./conky-assimilated`. It is an error if the path already exists.
- `--as ACTOR` names the newcomer. Default: `newcomer`.
- `--keys DIR` is where the newcomer's new key goes. Default: a `keys` directory beside the new vault. The option also works before the command, like the global `--keys`.
- `--then PAGE FIELD=VALUE ...` is a write to make as the newcomer, with the same field syntax as [write](#write). Repeat it to make several writes, which run in order. Put `source` before the first `--then`.

It reports five numbered steps as they happen.

1. Take the folder. `git clone` copies the source into the new folder. Nothing else is copied: no keys and no settings.
2. Check it. This is [verify](#verify): every commit is signed by a key the vault lists, the trailers are valid and the tree is clean. The step reports the number of commits, pages and spaces, and the last change. A space is a page that other pages lie within.
3. Read the room. Each page is listed with its space, the number of rules that apply to it (its own plus those inherited through its space) and the pages it watches. This reads the files only.
4. Carry on. The newcomer is a new actor with a new key made in the key directory, so the original author's key is never needed. Its public key is added to `keys/allowed_signers` in the same commit as its first write. For the packaged vault the writes come from a data file beside it: a busy hour takes the cooler down to 4 cups, and the supplier must react by itself. For any other source the writes are the `--then` options. With none, the command stops after step 3 and prints the `conky write` command to continue with.
5. Check again. The vault is verified once more, and the commits added by the carry-on are listed, with each reaction and its cause and each refusal and its reason.

A reaction is signed by the page that reacts, as for any write, so it needs that page's key. When the source lists a reacting page whose key stayed with the original author, the write fails with `no private key for '<page>'`, and the fix is to give that key with `--keys`.

The output ends with a short statement of what was shown and what was not. In a terminal it is styled like the demo: a box for the title and the closing, numbered step badges, `✓` and `✗` badges, and `↳` for each reaction. Plain output has no escape codes.

The exit code is 1 if verification fails at step 2 or step 5, or if a write that the packaged vault expects to be kept is refused or draws no reaction. A refused `--then` write is reported with its reason and does not change the exit code. Errors, each on one line beginning `error: `, include:

- `error: <path> already exists: choose another folder with --into PATH`
- `error: cannot take <source>: ...: give a vault directory, a bundle file or a URL that git clone accepts`
- `error: a key named '<actor>' already exists in <dir>: choose another name with --as ACTOR or another folder with --keys DIR`
- `error: '<actor>' is already listed in the vault's keys/allowed_signers: choose a new name with --as ACTOR`

A vault that fails step 2 is reported in the output of the step, with the first problem verify found, and nothing is written to it.

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

Prints the history, oldest first, one line per commit: short id, instant in UTC, actor, kind, page, then the reason for a refusal or `cause <id>` for a reaction. A line for a model answer ends with `model <provider page>`, then `read <pages>` when the prompt embedded pages. A line for a refusal by a rule that came from a space ends with `from <space>`. An empty vault prints nothing.

### verify

```
conky verify
```

Checks the vault as described in [vault format](../reference/vault-format.md#what-verify-checks). It prints `ok: <n> commits verified` on success. On failure it prints `error: <first problem>` and exits 1.

### connect terminal

```
conky connect terminal [--vault V] [--keys K] [--as NAME] [--screen PAGE] [--hands PAGE]
                       [--settle SECONDS] [--max-steps N] -- COMMAND [ARGS...]
```

Runs a [connector](connectors.md) beside the vault that gives it eyes and hands on a terminal program. It starts `COMMAND` in a pseudo-terminal, writes what the program shows to the screen page, and types what the hands page says. POSIX only.

- `COMMAND [ARGS...]` is the program. Put it after `--`, so that its own options are not read as conky's.
- `--vault V` and `--keys K` are the global options of the same names. They work before or after `connect terminal`.
- `--as NAME` is the connector's actor, which signs every write. Default: `terminal`. Its key is made on first use, like any actor's.
- `--screen PAGE` is the page that receives the screen. Default: `screen`.
- `--hands PAGE` is the page that says what to type. Default: `hands`.
- `--settle SECONDS` is how long the output must stay quiet before it is written as a screen. Default: 0.3.
- `--max-steps N` is the most screens to write. Default: 200.

It prints one line for each screen written and each set of keys sent, then a line for the end of the run. The run ends when the program exits, at `--max-steps` screens or on interrupt, and the reason is written to the field `ended` of the screen page. The exit code is 0 for each of these. The pages, fields and limits are in [connectors](connectors.md).

Errors, each on one line beginning `error: `, include:

- `error: cannot start '<program>': <reason>: check the command and that it is on PATH`
- `error: conky connect terminal needs a POSIX system: run it on Linux or macOS`
- `error: --screen and --hands name the same page: give each its own page`
- `error: cannot create the page '<page>': <reason>: create it first, or change the rule`

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
