---
kind: guide
title: Getting started
status: current
date: 2026-11-20
source: maintainers
---

# Getting started

One command runs a lemonade stand that minds itself. The walkthrough then does the same by hand: break a rule, watch a page react, check and repair the vault. The ideas are in [concepts](concepts.md), the commands in the [command line reference](../reference/cli.md).

## The demo

It needs [uv](https://docs.astral.sh/uv/), Git 2.34 or newer and `ssh-keygen` from OpenSSH 8.2 or newer.

```bash
uvx --from git+https://github.com/drksci/conky conky demo
```

It makes seven writes across four pages and narrates each. Maya sets up the stand with a house rule that the cooler never holds less than nothing, and fills it with 40 cups. The supplier watches the cooler. Sam writes down minus one cup and the house rule turns the write away. A busy hour takes the cooler down to 4 cups and the supplier orders by itself. A daybook measures its own growth. The pages are plain sentences, so reading them afterwards tells the same story as the terminal.

The vault is left in `./conky-demo-lemonade`, with private keys in `./keys`. The closing lines suggest `git -C conky-demo-lemonade log --oneline` for the history, and `conky read supplier` and `conky verify`, which need conky installed as described below. `conky demo team` runs a second example about tasks and a board, and `conky demo --list` lists the examples. In a terminal the output is styled, and piped output stays plain text. See the [command line reference](../reference/cli.md#demo).

## Taking over a stopped vault

One command takes over a stopped vault from its folder alone.

```bash
uvx --from git+https://github.com/drksci/conky conky assimilate
```

With no argument it uses a small stopped lemonade stand that ships in the package. It clones the folder into `./conky-assimilated`, checks every signature, lists each page with its rules and watches, then carries on as a new actor called `newcomer`, with a key made for the occasion in `./keys`. A busy hour takes the cooler down to 4 cups, the supplier orders by itself and the vault is checked again. For your own vault, give its directory, a Git bundle or a URL, and add `--then PAGE FIELD=VALUE` for each write to make. See the [command line reference](../reference/cli.md#assimilate).

The folder alone is enough to check a vault and continue it, with no key from the original author. No model is involved, so this is only the mechanical half of the [assimilation test](../ideas/assimilation-test.md).

## Before starting

- Python 3.11 or newer.
- Git 2.34 or newer.
- `ssh-keygen` from OpenSSH 8.2 or newer.

From a copy of the repository, install conky:

```bash
pip install -e '.[dev]'
```

Private keys are created in `~/.conky/keys`, never in the vault. The output below comes from running these commands for real, with `HOME` set to an empty scratch directory. Commit ids and times differ on every run.

## A vault and a space

`init` makes an empty vault. The first `write` makes a space called `stand`. Its members inherit two rules: a page with `cups` may not hold fewer than zero, and no page may exceed 2000 bytes. `--as maya` says who is writing.

```console
$ conky init demo
initialised demo
$ cd demo
$ conky write stand 'rules=["!has(page.cups) || page.cups >= 0", "size <= 2000"]' --body 'Welcome to the stand.' --as maya
written (commit 6e4e3c5)
```

## A member, and a broken rule

A page joins a space with `within`. The next write breaks the inherited rule. The refusal is a commit of its own, changes nothing, and exits with status 1.

```console
$ conky write cooler within=stand cups=40 --body 'Forty cups this morning.' --as maya
written (commit cf1ea51)
$ conky write cooler cups=-1 --as sam
refused (commit 8346b56): rule: !has(page.cups) || page.cups >= 0 (from stand) is false
```

## A page that reacts

The page `supplier` watches `cooler`. When the cooler drops below 10 cups, `supplier` writes an order to itself in a commit signed with its own key. The `set` values are expressions, so the order is a quoted sentence.

```console
$ conky write supplier 'order=Nothing needed yet.' ordered=false 'watch=[{on: cooler, when: "other.cups < 10", set: {order: "\"Two bags of lemons, please. We are nearly out.\"", ordered: "true"}}]' --as maya
written (commit 024da87)
$ conky write cooler cups=4 --as sam
written (commit e55b218)
$ conky read supplier
---
watch:
- on: cooler
  when: other.cups < 10
  set:
    order: '"Two bags of lemons, please. We are nearly out."'
    ordered: 'true'
order: Two bags of lemons, please. We are nearly out.
ordered: true
---
```

## A measure

A measure is a page that watches itself. Here `daybook` keeps a `pressure` number equal to its size divided by 400. A large write is not refused: the page records its own pressure in a commit of its own.

```console
$ conky write daybook pressure=0 'watch=[{on: daybook, when: "true", set: {pressure: "size / 400"}}]' --as maya
written (commit 8dc1ec1)
$ conky write daybook --body "$(python -c 'print("x" * 1000)')" --as maya
written (commit 8d36ef6)
$ conky read daybook | head -8
---
watch:
- on: daybook
  when: 'true'
  set:
    pressure: size / 400
pressure: 2
---
```

## Asking a model

Only this part needs a provider and a secret. A provider is a page that says where a model is and which one to use. It names a secret, never holds one. The secret is read from the environment variable `CONKY_SECRET_<NAME>`, or from `<name>.secret` in the key directory. The values below are placeholders for those of a real service. See [providers](../reference/providers.md).

```console
$ conky write helper api=openai url=https://api.example.com/v1/chat/completions model=model-name secret=example --as maya
$ export CONKY_SECRET_EXAMPLE=the-secret-from-the-provider
$ conky ask cooler note --provider helper --prompt 'Describe this cooler in one sentence: ![[cooler#cups]] cups left.' --as maya
```

`ask` resolves the embed, sends the prompt to the provider once and writes the answer to the `note` field of `cooler` in a commit signed by `maya`. The commit holds the resolved prompt, the provider page and model names, and the token counts when the provider reports them. If the secret is missing or the provider cannot be reached, a refusal is recorded with a reason that starts `model:` and says what to do next, and the other models Conky can find are tried. With none, a plain sentence is written to `note` and is replaced the next time a model is available.

The provider page is optional. Leave out `--provider` and Conky uses `ANTHROPIC_API_KEY`, or `claude` or `codex` when they are on the PATH, and `conky model` says which. See [detection](../reference/providers.md#detection). A watch entry with `ask` does the same when a page changes; see [asking a model](../reference/rules-and-reactions.md#asking-a-model).

## The history

`conky log` prints the history, oldest first. A reaction's line ends with `cause` and the id of the commit that triggered it. The refusal is there with its reason.

```console
$ conky log
6e4e3c5 2026-11-20T14:47:42Z maya write stand
cf1ea51 2026-11-20T14:47:42Z maya write cooler
8346b56 2026-11-20T14:47:42Z sam refused cooler rule: !has(page.cups) || page.cups >= 0 (from stand) is false
024da87 2026-11-20T14:47:43Z maya write supplier
e55b218 2026-11-20T14:47:43Z sam write cooler
4f244f5 2026-11-20T14:47:43Z supplier write supplier cause e55b218
8dc1ec1 2026-11-20T14:47:44Z maya write daybook
8d36ef6 2026-11-20T14:47:44Z maya write daybook
7119d53 2026-11-20T14:47:44Z daybook write daybook cause 8d36ef6
```

The vault is a Git repository, so plain Git reads the same history (newest first):

```console
$ git log --oneline
7119d53 write daybook
8d36ef6 write daybook
8dc1ec1 write daybook
4f244f5 write supplier
e55b218 write cooler
024da87 write supplier
8346b56 refused cooler
cf1ea51 write cooler
6e4e3c5 write stand
```

## Check, damage, repair

`verify` checks the signatures and the history. It notices when the pages are deleted by hand, and `rebuild` restores them from the history. The nine commits are six writes by `maya` and `sam`, one refusal and two reactions.

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

- [Concepts](concepts.md): the ideas behind each step.
- [Command line](../reference/cli.md): every command, option and exit code.
- [Rules and reactions](../reference/rules-and-reactions.md): the expression language and the variables in scope.
- [Vault format](../reference/vault-format.md): reading a vault without conky.
