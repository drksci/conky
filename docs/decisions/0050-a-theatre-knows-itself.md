---
kind: decision
title: A theatre knows itself
status: accepted
date: 2026-11-21
source: maintainers
arch:
  items:
  - kind: unplaced
    name: a theatre knows itself
    text: A vault and the settings true only on this machine, in an optional marionette.md outside the history, found from any folder in the vault.
---

# 0050 A theatre knows itself

## Context

- A vault says what a system is. Where it runs is a different fact: which key folder, which cache, which model, under what name. Until now every command took those as flags or variables each time, and had to be run from the vault's folder or told where it was.
- Prior art: Git finds its repository from any subfolder by looking up the tree; twelve-factor configuration keeps what varies between deploys in the environment and not in the code; infrastructure tooling keeps per-environment variable files beside a declaration that is the same everywhere.
- The image is a travelling puppet theatre: the play is the same in every town, and the booth is set to suit the square it stands in.

## Decision

- A theatre is one distinct conky system, the outermost thing everything in it lives in. Today it is its vault together with an optional `marionette.md`, the settings true only of the machine it is running on. The split is a general one: a thing has a part that says what it is, which lives in the vault and travels, and a part that says where it is running, which stays on the machine. A provider's page and its secret in the environment already work this way.
- Without `--vault`, a command walks up from the current folder to the nearest folder that holds a Git repository, the test `Vault` already uses, and uses it; if none is found it uses the current folder as before. A folder above the current one is taken for a vault only when it also holds pages, the list of its signers or the mark `conky init` leaves in the repository's own exclude list, so a command run deep inside another project's repository does not write into it.
- `marionette.md` is Markdown with frontmatter at the root of the vault's folder. It is parsed by the page parser and checked when read, and each wrong form is refused with a reason that says what to write instead. It is not a page and is never in the history: `init` and the first read add it to `.git/info/exclude`, and `verify` fails when the history holds it.
- It accepts `name`, `domain`, `keys`, `cache`, `provider`, `model` and `command`, each the same as a flag or variable that exists. An unknown key is refused naming the allowed ones, and a key that looks like a secret is refused with advice to use the environment.
- A setting is the flag, else the environment variable, else the file, else the default. `conky theatre` prints each value and which of the four gave it, and never a secret.
- The file's `provider`, `model` and `command` stand as variables for the length of one command, where the environment sets none, so the code that reads them is unchanged.

## Consequences

- A vault copied to a second folder with another file runs under another name and provider with an identical history. A clone arrives without the file and verifies.
- `name` and `domain` have no consumer except `conky theatre`; a later step may use the full name where one theatre must name another.
- Direction, not built: the theatre is expected to become a page like any other, the outermost space that every page is within, with `marionette.md` as the part of it that stays on the machine. Nothing in this change depends on that.
- Nothing is derived data here: the file is configuration, not a cache, and nothing reads it as the truth about the vault.
- A vault written before this change gains no file and behaves as before. A guarantee changes in one place: `--vault` no longer defaults to the current folder but to the nearest vault above it, which is the same when the current folder is a vault.
- The settings file is read for every command except `init`, `demo` and `assimilate`, so a malformed one stops them with its reason.
