---
kind: project
title: Status
status: current
date: 2026-11-20
source: maintainers
---

# Status

conky is early: the core works and is tested, and much is still to be built. This page says what exists and what is unverified. The unbuilt work is on the [roadmap](roadmap.md).

## What exists

From [design](../design.md) and the [reference](../reference/vault-format.md):

- Pages with deterministic serialisation, and a write path that is the only way state changes.
- Rules in CEL, inherited through `within` chains, with `page` and `size` in scope.
- A vault that is a Git repository: every write is a signed commit with trailers, and a refused write is an empty signed commit. Git and `ssh-keygen` are required.
- Reactions: pages that watch other pages and write themselves, with no model call.
- Model pages: a provider is a page (`openai` or `anthropic` wire format, secret by name, never in the vault), and a watch entry with `ask`, or `conky ask`, asks it one question. The answer is a signed write by the asking page, and the commit records the prompt, the model and the tokens. A failure is a refusal that starts `model:`. Tested only against stand-in servers on the local machine.
- Measures: a page can watch itself, with `size` and `other_size` in watch expressions. Pressure is the first use. Nothing yet acts on pressure to relieve it.
- `verify` (clean tree, `git fsck`, signatures from `keys/allowed_signers`, trailers, files changed), `rebuild` (restore the committed state), and a command line: `init`, `write`, `ask`, `read`, `log`, `verify`, `rebuild`, `demo`, `assimilate`, `connect`.
- `conky demo`: builds a small example vault (`lemonade` or `team`, shipped as data in the package) with the real write path and narrates each step, including a refused write and a reaction.
- `conky assimilate`: takes over a stopped vault from its folder alone (a directory, a bundle or a URL, or a small one that ships in the package), checks it, reads its pages, carries on as a new actor with a new key, and checks again. It is the mechanical form of the [assimilation test](../ideas/assimilation-test.md): a mechanism result with no model, so it shows that state travels and resumes and nothing about behaviour. The packaged vault is built reproducibly by `scripts/build_stopped_vault.py`.
- `conky connect terminal`: the first [connector](../reference/connectors.md). It starts a terminal program in a pseudo-terminal, writes its screen to a page and types what a hands page says, as ordinary signed writes by its own actor. POSIX only and text only, tested against a small game in `tests/games/`. A page can play the program by reaction. A page that asks a model can too, but its prompt cannot yet embed the screen text, because an embed reads a field and the screen is the body of a page. No connector for an outside protocol is built. See [playing a program](../guide/playing-a-program.md).
- Two trailers that make activity readable from the history: `Read` on a model answer, naming the pages embedded in the prompt, and `From` on a refusal by a rule that came from a space. `conky log` shows them. The summaries and the activity strip that would use them are not built ([trace](../ideas/trace.md)).
- A golden vault under `tests/golden/` that every version must keep verifying and reading.
- CI that runs `scripts/check` on every pull request and on pushes to `main`.

## Unverified

- No live provider has been called. The two wire formats are tested against stand-in servers that follow them as documented, so a real service may differ in ways the tests cannot show.
- Cost is recorded as token counts when a provider reports them. Nothing bounds it, and a model's answer is stored like any other field, with nothing yet marking it as unchecked.
- No claim here comes from an unscripted benchmark run; none has been made.
- Nothing in the project has been audited for security. See [SECURITY.md](../../SECURITY.md).

## Known gaps

- Two open design questions, recorded without answers in [open questions](open-questions.md): rules on a space also apply to the space page itself, and removing the last commit is not detectable from one copy alone.
- Rules are not enforced on commits made outside conky or pushed from elsewhere; `verify` catches unsigned or unlisted-key commits, not rule violations ([decision 0002](../decisions/0002-git-is-the-store.md)).
- Write throughput is limited by one signed commit per write, in the order of tens per second.
- Temperament and voice for pages are not built. Pages in the example vaults carry human-written content, and nothing yet gives a page a generated temperament or voice ([a page with a self](../ideas/character.md)).
- Everything on the [roadmap](roadmap.md) is unbuilt except the first slice of measures, the demo, model pages, the mechanical form of the resume test and the terminal connector.
- The resume test with a model is not built, so nothing yet shows that a consumer other than conky's own commands can resume from a stopped vault.
