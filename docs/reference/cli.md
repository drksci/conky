---
kind: reference
title: Command line
status: current
date: 2026-11-20
source: maintainers
---

# Command line

`conky` is installed by `pip install -e '.[dev]'`. The walkthrough in [getting started](../guide/getting-started.md) uses every command.

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

### read

```
conky read <page>
```

Prints the page as stored, with embeds resolved. It is an error if the page does not exist.

### log

```
conky log
```

Prints the history, oldest first, one line per commit: short id, instant in UTC, actor, kind, page, then the reason for a refusal or `cause <id>` for a reaction. An empty vault prints nothing.

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
