---
kind: design
title: Design
status: current
date: 2026-11-20
source: architect
---
# Design

## The model

A vault is a plain Git repository. Its pages are Markdown files under `pages/`, and its history is the authority: every change to a page is one signed commit, and a write that is refused is recorded as an empty signed commit. What is not in the history did not happen. conky keeps no log, hash chain or key format of its own. Git already provides tamper-evident history, signed commits, exact restore, transport by clone, push or bundle, and atomic multi-file changes, with tools that exist everywhere. conky is what sits on top: rules, reactions, measures and a few conventions.

An event is a commit. A seal is its signature. The vault holds public keys only; private keys live in a separate directory. A cold reader given only the vault can verify it and read it with nothing but Git.

## The vault format

This section is enough to read a vault without conky.

Layout:

```
<vault>/                 a Git repository, branch main
  pages/<name>.md        the pages, tracked
  keys/allowed_signers   public keys, tracked, in Git's allowed-signers format
```

A page is `---`, YAML frontmatter, `---`, then a Markdown body. Reserved frontmatter keys are `within`, `rules` and `watch`; every other key is a field. Keys are written in a fixed order, so a page's bytes are a function of its content.

Identity. An actor is a name made of lowercase letters, digits, `-` and `_`. Its identity is `<actor>@conky`. Its line in `keys/allowed_signers` is `<actor>@conky namespaces="git" ssh-ed25519 AAAA...`. The line is added in the commit that is the actor's first, whether that commit is a write or a refusal.

Signing. Git's native SSH signing is used (`gpg.format ssh`). `conky init` sets, in the repository's own config, `gpg.format ssh`, `gpg.ssh.allowedSignersFile keys/allowed_signers` (relative to the repository root) and `commit.gpgsign true`. The private key of each actor is an OpenSSH ed25519 key file named after the actor, in a key directory outside the vault (`--keys`, default `~/.conky/keys`), created on the actor's first write.

A write is one commit:

- author and committer name `<actor>`, email `<actor>@conky`, and both dates equal to the instant the caller supplied;
- signed with the actor's key;
- subject `write <page>`;
- trailers `Kind: write`, `Page: <page>`, and `Cause: <full commit id>` when the write is a reaction.

A refused write is an empty commit, signed the same way, with subject `refused <page>` and trailers `Kind: refused`, `Page: <page>`, `Reason: <one line>`, `Attempt: <compact JSON of the attempted field changes>`, `Body-Bytes: <n>` when a body was supplied, and `Cause:` when it was a reaction. It changes no page.

Reading with plain Git: `git log` is the history, `git log --show-signature` checks the seals, `git log --format=%B` shows the trailers, `git blame pages/<name>.md` says which commit gave a line its value, and `git clone`, `git push` and `git bundle` move the vault.

## Rules and spaces

A page may carry CEL expressions that must be true after every write. A page inherits the rules of every space up its `within` chain. Rules are pure: they see `page` (the resulting fields) and `size` (the byte length of the resulting serialised page). A size limit is an ordinary rule a space sets, for example `size <= 2000`. A write that breaks a rule is refused with reason `rule`; a malformed page is refused with `shape`.

## Reactions

A page can watch another page, or itself. When the watched page changes and the `when` expression is true, the runtime writes the watching page as a commit signed by that page's own key, with `Cause` set to the triggering commit. Watch expressions see `page`, `other`, `size` and `other_size`. Reactions cascade to depth 12, then are refused with reason `cycle`. A reaction that would change nothing is skipped, so stable states end.

## Measures

A measure is a page watching itself: a `watch` entry whose `on` is the page's own name, setting a field computed from the page's state. No new concept is added. For a self-watch `size` and `other_size` are equal. The computed value is recorded as an ordinary commit, so reading history never evaluates an expression and stays reproducible even if the expression language changes. The skip-when-unchanged rule and the depth cap still apply, so a self-watch settles when its fields stop changing.

Pressure is the first use. A page with no size rule can take a large write; a self-watch such as `{on: <itself>, when: "true", set: {pressure: "size / 400"}}` records a rising number, and a second entry with `when: "page.pressure >= 2"` can set a state that other pages watch. Walls stay for what must never happen. Nothing yet acts to relieve the pressure. The checks are in `tests/test_laws.py`.

Think of a spreadsheet: pages are like cells, a self-watch is like a formula, and the history is the signed record of every recalculation.

## Verify and rebuild

State is the committed state. Before a write, `git status --porcelain` must show nothing; otherwise the write is refused with an input error that gives the command to discard the changes.

`verify` raises on the first problem it finds. It checks that the working tree is clean, that `git fsck` passes, that every commit on `main` has a good signature from a key in `keys/allowed_signers`, that every commit carries a `Kind` trailer of `write` or `refused`, that a write changes only files under `pages/` and `keys/allowed_signers`, and that a refusal changes nothing except, for an actor's first commit, `keys/allowed_signers`.

`rebuild` restores the working tree to the committed state, discarding stray edits and untracked files under `pages/` and `keys/`.

`log` prints the history oldest first, one line per commit: short id, instant, actor, kind, page, and the cause or the reason.

Git and `ssh-keygen` are required: Git 2.34 or newer and OpenSSH 8.2 or newer. conky checks for them when a vault is opened. Every subprocess runs with `GIT_CONFIG_GLOBAL=/dev/null`, `GIT_CONFIG_NOSYSTEM=1` and `GIT_TERMINAL_PROMPT=0`, so the machine's own Git settings do not change a result.

Rewriting history is possible locally and is detectable only against another copy, such as a remote or a clone. See [decision 0021](decisions/0021-git-is-the-store.md) and [decision 0015](decisions/0015-open-questions.md).

## Not built yet

In this order:

1. Tables stored as Parquet beside their page, with large data by pointer ([decision 0022](decisions/0022-data-beside-pages.md)).
2. Model-backed pages: a page that asks a question state cannot answer.
3. Rules that see a group of pages changed in one commit, and a pattern maker (accounting as a pattern, not a runtime feature).
4. The assimilation test: hand a fresh consumer only a stopped vault and score whether it resumes correctly.
5. The harness-neutral benchmark against other agent harnesses.
