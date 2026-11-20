---
kind: reference
title: Vault format
status: current
date: 2026-11-20
source: maintainers
---

# Vault format

This page is enough to read and check a vault without conky. The format is held stable by the golden vault in `tests/golden/`.

## Layout

A vault is a Git repository on branch `main`.

```
<vault>/                 a Git repository, branch main
  pages/<name>.md        the pages, tracked
  keys/allowed_signers   public keys, tracked, in Git's allowed-signers format
```

Private keys are never inside the vault. They live in a separate key directory (see [Identity and signing](#identity-and-signing)).

## Pages

A page is a line `---`, YAML frontmatter, a line `---`, then a Markdown body. A page name is 1 to 64 characters: lowercase letters, digits, `-` and `_`, starting with a letter or a digit.

Three frontmatter keys are reserved: `within` (the name of a space), `rules` (a list of expressions) and `watch` (a list of watch entries). Every other key is a field. Keys are written in a fixed order: reserved keys first, then fields sorted by name. A page's bytes are therefore a function of its content, and the same content always produces the same file.

A body may contain `![[name#field]]`, an embed. It is resolved when the page is read, not when it is stored: the embed is replaced by the value of that field on that page. A string is inserted as it is, a boolean as `true` or `false`, a missing page or field as nothing, and any other value as compact JSON. The stored file keeps the embed text. See [rules and reactions](rules-and-reactions.md) for the meaning of `within`, `rules` and `watch`.

## Commits

Each event is one commit. Every commit has:

- author and committer name `<actor>` and email `<actor>@conky`;
- both dates equal to the instant the caller supplied (the command line uses the current time in UTC, to the second);
- a signature made with the actor's key;
- a subject, then a body that is a list of trailers. A model answer also has a note between the subject and the trailers (see [A model answer](#a-model-answer)).

### A write

A write commit changes one page. It has subject `write <page>` and these trailers:

| Trailer | Value |
|---|---|
| `Kind` | `write` |
| `Page` | the page name |
| `Cause` | the full id of the triggering commit, only when the write is a reaction |

### A model answer

An answer from a model is a write ([rules and reactions](rules-and-reactions.md#asking-a-model)) by the page that asked. It has the trailers of a write, including `Cause` when a watch entry asked, and these:

| Trailer | Value |
|---|---|
| `Model` | the name of the provider page |
| `Model-Name` | the `model` field of that page, as sent |
| `Tokens-In` | prompt tokens, only when the provider reported them |
| `Tokens-Out` | completion tokens, only when the provider reported them |
| `Read` | a page whose fields were embedded in the prompt, one trailer for each distinct page in order of first use, and none when no page was embedded |

Between the subject and the trailers sits the resolved prompt, exactly as it was sent, so the question is in the history beside its answer. The trailers are always the last paragraph of the message. A refusal of an answer that broke a rule carries the same trailers and note.

`Read` records what the page looked at to ask its question. A page counts as read when an embed in the prompt named it and the named field exists. `conky log` shows the pages as `read a, b`.

The answer is a field of the page like any other. The secret used to reach the provider is never written to the vault, in a page, a trailer or a message. See [providers](providers.md#secrets).

### A refusal

A refused write is an empty commit, signed the same way. It changes no page. It has subject `refused <page>` and these trailers:

| Trailer | Value |
|---|---|
| `Kind` | `refused` |
| `Page` | the page name |
| `Reason` | one line saying why the write was refused |
| `Attempt` | compact JSON of the attempted field changes |
| `Body-Bytes` | the length of the supplied body in bytes, only when a body was supplied |
| `From` | the space whose rule refused the write, only when the rule came from a space above the page and not from the page itself |
| `Cause` | the triggering commit, only when the refused write was a reaction |

The reasons begin with `shape`, `rule`, `cycle`, `watch` or `model`; see [rules and reactions](rules-and-reactions.md#refusals). The reason text names the space too, as in `(from stand)`. `From` repeats it as a trailer so that a reader of the history can find refusals by space without parsing the reason. `conky log` shows it as `from <space>`.

## Identity and signing

An actor is a name made of lowercase letters, digits, `-` and `_`. Its identity is `<actor>@conky`. Its line in `keys/allowed_signers` is:

```
<actor>@conky namespaces="git" ssh-ed25519 AAAA...
```

The line is added in the actor's first commit, whether that commit is a write or a refusal. A page that reacts is itself an actor, so it has its own key and its own line.

Git's native SSH signing is used. `conky init` sets these in the repository's own configuration:

- `gpg.format` is `ssh`;
- `gpg.ssh.allowedSignersFile` is `keys/allowed_signers`, relative to the repository root;
- `commit.gpgsign` is `true`.

The private key of each actor is an OpenSSH ed25519 key file named after the actor, in a key directory outside the vault (`--keys`, default `~/.conky/keys`). It is created on the actor's first write. If the vault already lists an actor and its private key is not in the key directory, the write is an error that asks for `--keys <directory>`.

## What verify checks

`verify` stops at the first problem. It checks, in order:

1. The working tree is clean. A change made outside conky is a failure.
2. `git fsck --strict` passes.
3. Every commit on `main` has a good signature from a key in `keys/allowed_signers`.
4. Every commit has a `Kind` trailer of `write` or `refused`. Other trailers, such as `Read` and `From` and those of a model answer, are accepted and not checked.
5. A write changes only files under `pages/` and `keys/allowed_signers`.
6. A refusal changes nothing except `keys/allowed_signers`, which it changes only in an actor's first commit.

`verify` does not evaluate rules. A commit made outside conky that is signed by a listed key and shaped like a write passes, whatever it says. Rules are enforced when a write goes through conky.

An empty vault, with no commits yet, verifies.

## Rebuild

`rebuild` restores the working tree to the state of `main`. It discards changes to tracked files and removes untracked files under `pages/` and `keys/`.

Before every write the working tree must show no changes (`git status --porcelain` is empty). Otherwise the write is an error that names the command to discard them.

## Reading with plain Git

- `git log` is the history.
- `git log --show-signature` checks the seals.
- `git log --format=%B` shows the trailers.
- `git blame pages/<name>.md` says which commit gave a line its value.
- `git clone`, `git push` and `git bundle` move the vault.

## Requirements and isolation

Git 2.34 or newer and `ssh-keygen` from OpenSSH 8.2 or newer. conky checks for them when a vault is opened. Every Git subprocess runs with `GIT_CONFIG_GLOBAL=/dev/null`, `GIT_CONFIG_NOSYSTEM=1` and `GIT_TERMINAL_PROMPT=0`, so the machine's own Git settings do not change a result.

## Limits of the history

Rewriting history is possible locally. Removing the last commit is detectable only against another copy, such as a remote or a clone. See [decision 0002](../decisions/0002-git-is-the-store.md) and [open questions](../project/open-questions.md).
