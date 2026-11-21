---
kind: reference
title: Vault format
status: current
date: 2026-11-20
source: maintainers
---

# Vault format

This page specifies the files, commits and checks that make a vault, enough to read and verify one without conky. The golden vault in `tests/golden/` holds the format stable.

## Layout

A vault is a Git repository on branch `main`.

```
<vault>/                 a Git repository, branch main
  pages/<name>.md        the pages, tracked
  keys/allowed_signers   public keys, tracked, in Git's allowed-signers format
```

Private keys are never inside the vault. They live in a key directory (see [Identity and signing](#identity-and-signing)).

## Pages

A page is a `---` line, YAML frontmatter, a `---` line, then a Markdown body. A page name is 1 to 64 characters: lowercase letters, digits, `-` and `_`, starting with a letter or a digit.

Three frontmatter keys are reserved: `within` (the name of a space, or a list of distinct names when a page is within several, the first being its home; a list of one is stored as the name), `rules` (a list of expressions, each as text or as a mapping with the one key `each`) and `watch` (a list of watch entries, each with `on` naming a page, `within` or `link`). The page names `within` and `link` are not allowed. A page named `theatre` is the vault's outermost space: every other page lies within it, it lies within nothing, and a `name` field on it must be a page name ([decision 0051](../decisions/0051-the-theatre-is-a-page.md)). Every other key is a field. Keys are written in a fixed order, reserved keys first and then fields sorted by name, so the same content always produces the same file. The meaning of the reserved keys is in [rules and reactions](rules-and-reactions.md).

A body may contain an embed, resolved when the page is read and never when it is stored. The stored file keeps the embed text.

- `![[name#field]]` becomes the value of that field on that page.
- `![[name]]` becomes the body of that page as stored. An embedded body is not itself resolved.
- `![[space#members]]` becomes one line for each page within that space, directly or through spaces (for the page named `theatre`, every other page) (a page within several spaces is listed under each), sorted by name: `name: first line of its body`, or the name alone when the body is empty. At most 20 lines are shown, then `(N more not shown)` counts the rest. `members` is a part every space has, computed and never stored, so a page may not carry a field of that name and a write that tries is refused as a malformed page.
- `![[page#context]]` becomes what the spaces above that page say. Each space above it that has a body gives a line `NAME says:` and then its body as written, less closing blank space, and the blocks are separated by a blank line. The order is nearest first: the spaces the page lists, in the order listed, then the spaces above those, each space once at its nearest distance. A space with no body is skipped, and a page within no space, or whose spaces say nothing, embeds nothing. At most 5 spaces are shown, then `(N more spaces not shown)` counts the rest, and the page named `theatre`, when it has words, is the last block shown whatever the cap cuts; the length of one space's words is not capped. Nothing says who wrote a body. `context` is a part every page has, computed and never stored, so a page may not carry a field of that name and a write that tries is refused as a malformed page.
- A page may carry a field `known_as`, a list of one or more phrases of at least two characters each, that it is known by. Text that uses a phrase, as whole words, without regard to case, with runs of whitespace as one space and a trailing `'s` allowed, counts as linking to the page with no brackets typed and no body changed: `on: link` is told at the write, and the expression function `terms(TEXT)` names the pages a text uses. A page's own name is a phrase only when listed, and a page does not link to itself by its phrases. Nothing is stored: recognition is worked out from the pages as they are, so a page written before a term page existed counts as linking to it once the term page exists, though its watchers are not told late. `known_as` is checked when written: a value that is not a list, an empty list, or a phrase that is empty, shorter than two characters or not text is refused as a malformed page ([decision 0044](../decisions/0044-a-page-is-known-by-its-phrases.md)).
- A space may carry a field `shows`, a mapping with two optional keys. `most` is a whole number from 1 to 20 and says how many lines to show. `first` is an expression that reads `page` (the member's fields), `text` (its body) and `space` (the fields of the space shown) and gives a number. With `first` the lines are ordered by that number, highest first, and a member it cannot score, because a field is missing or the value is not a number, comes after the scored ones; ties and unscored members are ordered by name. The cut at `most` follows the order. Nothing is stored: the order is worked out when the embed is resolved, and the resolved text recorded with an ask shows what was shown. `shows` is checked when written: an unknown key, a `most` outside the range, or a `first` that does not parse or reads another name is refused as a malformed page. Example, which puts first the member that shares a word of more than three letters with what the space last heard: `shows: {most: 8, first: "space.heard.lowerAscii().split(' ').filter(w, w.size() > 3 && text.lowerAscii().contains(w)).size()"}`.

A string is inserted as it is and a boolean as `true` or `false`. A missing page, a missing field, an empty body or a space with no members gives nothing. Any other value is inserted as compact JSON.

## Commits

Each event is one commit. Every commit has:

- author and committer name `<actor>` and email `<actor>@conky`;
- both dates equal to the instant the caller supplied (the command line uses the current time in UTC, to the second);
- a signature made with the actor's key;
- a subject, then trailers. A model answer also has a note between them (see [A model answer](#a-model-answer)).

### A write

A write commit changes one page. It has subject `write <page>` and these trailers:

| Trailer | Value |
|---|---|
| `Kind` | `write` |
| `Page` | the page name |
| `Cause` | the full id of the triggering commit, only when the write is a reaction |

### A model answer

A model answer is a write by the page that asked ([rules and reactions](rules-and-reactions.md#asking-a-model)). It has the trailers of a write, including `Cause` when a watch entry asked, and these:

| Trailer | Value |
|---|---|
| `Model` | the name of the provider page, `detected:<kind>` for a model found from the environment, or `none` when no model answered and a plain sentence was written |
| `Model-Name` | the `model` field of that page, as sent, or the command's name; left out for `none` |
| `Tokens-In` | prompt tokens, only when the provider reported them |
| `Tokens-Out` | completion tokens, only when the provider reported them |
| `Read` | a page whose fields or body were embedded in the prompt, one trailer for each distinct page in order of first use, and none when no page was embedded |
| `Cache` | `hit` when the answer came from the cache. No tokens were spent, so `Tokens-In` and `Tokens-Out` are left out ([the cache](providers.md#cache)) |

The resolved prompt sits between the subject and the trailers, exactly as sent, so the question is in the history beside its answer. The trailers are always the last paragraph of the message. A refusal of an answer that broke a rule carries the same trailers and note.

`Read` records what the page looked at. A page counts as read when an embed in the prompt named it and the named field exists, or, for an embed with no field, when its body is not empty, or, for `#members`, when the space has members, or, for `#context`, when the spaces above the page say something, in which case the spaces shown are the ones named and not the page. The space is the page named, so a changed list changes the prompt and the question is asked afresh. `conky log` shows them as `read a, b`.

When an entry may write pages ([an answer that is pages](rules-and-reactions.md#an-answer-that-is-pages)), each page of the answer is a following write, with the trailers of any reaction: it is by the page that asked, and its `Cause` is the commit of the answer. No new trailer is needed, so the history shows what a character did and why.

The answer is a field like any other. The secret used to reach the provider is never written to the vault, in a page, a trailer or a message ([providers](providers.md#secrets)).

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

The reasons begin with `shape`, `rule`, `cycle`, `watch`, `model` or `limit` ([rules and reactions](rules-and-reactions.md#refusals)). The reason names the space, as in `(from stand)`. `From` repeats it as a trailer so that refusals can be found by space without parsing the reason, and `conky log` shows it as `from <space>`.

## Identity and signing

An actor is a name of lowercase letters, digits, `-` and `_`, with identity `<actor>@conky`. Its line in `keys/allowed_signers` is:

```
<actor>@conky namespaces="git" ssh-ed25519 AAAA...
```

The line is added in the actor's first commit, whether a write or a refusal. A page that reacts is itself an actor, with its own key and line.

Signing is Git's native SSH signing. `conky init` sets these in the repository's own configuration:

- `gpg.format` is `ssh`;
- `gpg.ssh.allowedSignersFile` is `keys/allowed_signers`, relative to the repository root;
- `commit.gpgsign` is `true`.

Each actor's private key is an OpenSSH ed25519 key file named after the actor, in a key directory outside the vault (`--keys`, default `~/.conky/keys`). It is created on the actor's first write. If the vault lists an actor whose private key is not in the key directory, the write is an error that asks for `--keys <directory>`.

## What verify checks

`verify` stops at the first problem. It checks:

1. The working tree is clean. A change made outside conky is a failure.
2. `git fsck --strict` passes.

Then, for each commit on `main`, oldest first:

3. It has a good signature from a key in `keys/allowed_signers`, and the principal of that key is `<author>@conky`, the actor the commit names. A commit signed as one name and made as another fails.
4. It has a `Kind` trailer of `write` or `refused`. Other trailers, such as `Read`, `From` and those of a model answer, are accepted and not checked.
5. A write changes only files under `pages/` and `keys/allowed_signers`.
6. A refusal changes nothing except `keys/allowed_signers`, and only in an actor's first commit.
7. A commit that changes `keys/allowed_signers` only appends lines for names not yet listed. A name is claimed by first use: changing, reordering or removing a line, or listing a name twice, fails. Changing a key is a later step ([decision 0053](../decisions/0053-a-rule-sees-who-acts-and-a-name-cannot-be-borrowed.md)).

A vault made before this check in which two names share one key does not verify; refound it with a key per name. Within one machine the key folder is the credential: whoever holds it can act under the names whose keys are in it. What cannot happen is a history in which a write claims a name its signature does not carry.

`verify` does not evaluate rules. A commit made outside conky, signed by a listed key and shaped like a write, passes whatever it says. Rules are enforced when a write goes through conky.

An empty vault with no commits verifies.

## Rebuild

`rebuild` restores the working tree to the state of `main`. It discards changes to tracked files and removes untracked files under `pages/` and `keys/`.

Before every write the working tree must be clean (`git status --porcelain` is empty). Otherwise the write is an error that names the command to discard the changes.

## Reading with plain Git

- `git log` is the history.
- `git log --show-signature` checks the seals.
- `git log --format=%B` shows the trailers.
- `git blame pages/<name>.md` says which commit gave a line its value.
- `git clone`, `git push` and `git bundle` move the vault.

## Requirements and isolation

Git 2.34 or newer and `ssh-keygen` from OpenSSH 8.2 or newer, checked when a vault is opened. Every Git subprocess runs with `GIT_CONFIG_GLOBAL=/dev/null`, `GIT_CONFIG_NOSYSTEM=1` and `GIT_TERMINAL_PROMPT=0`, so the machine's own Git settings cannot change a result.

## Limits of the history

History can be rewritten locally. Removing the last commit shows only against another copy, such as a remote or a clone. See [decision 0002](../decisions/0002-git-is-the-store.md) and [open questions](../project/open-questions.md).
