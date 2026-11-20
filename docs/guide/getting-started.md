---
kind: guide
title: Getting started
status: current
date: 2026-11-20
source: maintainers
---

# Getting started

A short demo, then a walkthrough of the command line. The walkthrough builds a small market, breaks a rule on purpose, watches a page react, and then checks and repairs the vault. The ideas are explained in [concepts](concepts.md); every command is described in the [command line reference](../reference/cli.md).

## The demo

One command builds a small market in a new folder and shows it running itself. It needs [uv](https://docs.astral.sh/uv/), Git 2.34 or newer and `ssh-keygen` from OpenSSH 8.2 or newer.

```bash
uvx --from git+https://github.com/drksci/conky conky demo
```

It makes seven writes across four pages, narrating each step in plain words: a market space with a rule that stock is never negative, a stall inside it, and a depot that watches the stall. A write that breaks the rule is refused. A write that lowers the stock makes the depot mark a reorder by itself. A journal page then keeps its own measure of its size.

The vault is left in `./conky-demo-stall`, with private keys in `./keys`. The closing lines say what to look at next: `git -C conky-demo-stall log --oneline` for the history, and `conky read depot`, `conky verify` for the pages and the checks, which need conky installed as described below. `conky demo team` runs a second example about tasks and a board, and `conky demo --list` lists the examples. In a terminal the output is styled with boxes and badges, and piped output stays plain text. The full output and options are in the [command line reference](../reference/cli.md#demo).

## Taking over a stopped vault

One command takes over a vault that has stopped, using nothing but its folder.

```bash
uvx --from git+https://github.com/drksci/conky conky assimilate
```

With no argument it uses a small stopped market stall that ships in the package. The command clones the folder into `./conky-assimilated`, checks every signature, lists each page with its rules and watches, and then carries on as a new actor called `newcomer`, with a key made for the occasion in `./keys`. The stall sells down to 4 loaves, the depot reacts by itself, and the vault is checked again. To take over a vault of your own, give its directory, a Git bundle or a URL as the first argument, and add `--then PAGE FIELD=VALUE` for each write to make. The options are in the [command line reference](../reference/cli.md#assimilate).

This shows that the folder alone is enough to check a vault's history and to continue it, with no key from the original author. It shows nothing about behaviour, because no model is involved: it is the mechanical half of the [assimilation test](../ideas/assimilation-test.md).

The rest of this page does the same things by hand.

## Before starting

- Python 3.11 or newer.
- Git 2.34 or newer.
- `ssh-keygen` from OpenSSH 8.2 or newer.

From a copy of the repository, install conky:

```bash
pip install -e '.[dev]'
```

Private keys are created in `~/.conky/keys`, never in the vault. The output below was produced by running these commands for real, with `HOME` set to an empty scratch directory. Commit ids and times differ on every run.

## A vault and a space

`init` makes an empty vault. The first `write` makes a space called `market`, whose rules its members inherit: stock may not go below zero, and a page may not exceed 2000 bytes. `--as alice` says who is writing.

```console
$ conky init demo
initialised demo
$ cd demo
$ conky write market 'rules=["page.stock >= 0", "size <= 2000"]' stock=0 --as alice
written (commit 1a61a7a)
```

## A member, and a broken rule

A page joins a space with `within`. The next write breaks the inherited rule. The refusal is a commit of its own, it changes nothing, and the command exits with status 1.

```console
$ conky write stall within=market stock=40 --body 'Fresh bread.' --as alice
written (commit 1280223)
$ conky write stall stock=-1 --as alice
refused (commit 7c73641): rule: page.stock >= 0 (from market) is false
```

## A page that reacts

The page `depot` watches `stall`. When the stall's stock drops below 10, `depot` sets `reorder` to true. The next write drops the stock, and `depot` changes itself in a commit signed with its own key.

```console
$ conky write depot reorder=false 'watch=[{on: stall, when: "other.stock < 10", set: {reorder: "true"}}]' --as alice
written (commit 063c6b5)
$ conky write stall stock=4 --as alice
written (commit b78adec)
$ conky read depot
---
watch:
- on: stall
  when: other.stock < 10
  set:
    reorder: 'true'
reorder: true
---
```

## A measure

A measure is a page that watches itself. Here `journal` keeps a `pressure` number equal to its size divided by 400. A large write is not refused. The page records its own pressure in a commit of its own.

```console
$ conky write journal pressure=0 'watch=[{on: journal, when: "true", set: {pressure: "size / 400"}}]' --as alice
written (commit 4aa3ee2)
$ conky write journal --body "$(python -c 'print("x" * 1000)')" --as alice
written (commit 8c91bbe)
$ conky read journal | head -8
---
watch:
- on: journal
  when: 'true'
  set:
    pressure: size / 400
pressure: 2
---
```

## Asking a model

This part needs a provider and a secret, and nothing above does. Without them the rest of the vault works as shown. A provider is a page that says where a model is and which one to use. The page names a secret, never the secret itself. The secret is read from the environment variable `CONKY_SECRET_<NAME>`, or from `<name>.secret` in the key directory. The values below are placeholders to replace with those of a real service. See [providers](../reference/providers.md).

```console
$ conky write helper api=openai url=https://api.example.com/v1/chat/completions model=model-name secret=example --as alice
$ export CONKY_SECRET_EXAMPLE=the-secret-from-the-provider
$ conky ask stall note --provider helper --prompt 'Describe this stall in one sentence: ![[stall#stock]] loaves left.' --as alice
```

The `ask` command resolves the embed, sends the prompt to the provider once, and writes the answer to the `note` field of `stall` as a commit signed by `alice`. The commit holds the resolved prompt, the name of the provider page and the model, and the token counts when the provider reports them. If the secret is missing or the provider cannot be reached, nothing is written to `note`, and a refusal is recorded with a reason that starts `model:` and says what to do next. A watch entry with `ask` does the same when a page changes; see [asking a model](../reference/rules-and-reactions.md#asking-a-model).

## The history

`conky log` prints the history, oldest first. Lines for a reaction end with `cause` and the id of the commit that triggered them. The `depot` commit is by `depot`, and the `journal` commit is by `journal`. The refusal is in the history with its reason.

```console
$ conky log
1a61a7a 2026-11-20T12:50:59Z alice write market
1280223 2026-11-20T12:50:59Z alice write stall
7c73641 2026-11-20T12:50:59Z alice refused stall rule: page.stock >= 0 (from market) is false
063c6b5 2026-11-20T12:51:00Z alice write depot
b78adec 2026-11-20T12:51:00Z alice write stall
fff4baa 2026-11-20T12:51:00Z depot write depot cause b78adec
4aa3ee2 2026-11-20T12:51:00Z alice write journal
8c91bbe 2026-11-20T12:51:01Z alice write journal
824fc7d 2026-11-20T12:51:01Z journal write journal cause 8c91bbe
```

The vault is a Git repository, so plain Git reads the same history (newest first):

```console
$ git log --oneline
824fc7d write journal
8c91bbe write journal
4aa3ee2 write journal
fff4baa write depot
b78adec write stall
063c6b5 write depot
7c73641 refused stall
1280223 write stall
1a61a7a write market
```

## Check, damage, repair

`verify` checks the signatures and the history. Deleting the pages by hand is damage that `verify` notices. `rebuild` restores the pages from the history, and `verify` passes again. The nine commits are six writes by `alice`, one refusal and two reactions.

```console
$ conky verify
ok: 9 commits verified
$ rm -r pages
$ conky verify
error: the working tree has changes that were not made through conky: run `conky --vault . rebuild` to discard them
$ conky rebuild
restored the working tree from the committed history
$ conky verify
ok: 9 commits verified
```

## Where next

- [Concepts](concepts.md), for the ideas behind each step.
- [Command line](../reference/cli.md), for every command, option and exit code.
- [Rules and reactions](../reference/rules-and-reactions.md), for the expression language and the variables in scope.
- [Vault format](../reference/vault-format.md), for reading a vault without conky.
