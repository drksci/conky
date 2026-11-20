---
kind: project
title: Status
status: current
date: 2026-11-20
source: maintainers
---

# Status

conky is early: the core works and is tested, and much is unbuilt. This page says what exists and what is unverified. The unbuilt work is on the [roadmap](roadmap.md).

## What exists

From [design](../design.md) and the [reference](../reference/vault-format.md):

- Pages with deterministic serialisation, and a write path that is the only way state changes.
- Rules in CEL, inherited through `within` chains, with `page` and `size` in scope.
- A vault that is a Git repository. Every write is a signed commit with trailers, and a refused write is an empty signed commit. Git and `ssh-keygen` are required.
- Reactions: pages that watch other pages and write themselves, with no model call.
- Model pages. A provider is a page (`openai` or `anthropic` wire format, secret by name and never in the vault), and a watch entry with `ask`, or `conky ask`, puts one question to it. The answer is a signed write by the asking page, and the commit records the prompt, the model and the tokens. A failure is a refusal that starts `model:`. A third shape, `api: command`, runs a named program with the prompt on standard input (built in: `claude -p` and `codex exec`). With no provider page, a model is detected from the environment and the PATH, a failing model falls to the next, and with none a plain sentence is written that a later model replaces. The HTTP shapes are tested only against stand-in servers on the local machine; the command shape is tested against small local scripts.
- An answer that is pages. A watch entry or `conky ask` with `writes` names a space the asking page may write into. The model's reply is cut into plain text and page blocks (`=== page: <name> ===`), and each page is applied as an ordinary write by the asker, one commit each, caused by the answer. The runtime enforces that a page is within the space before and after, carries no `secret` or `command`, has no watch entry that writes outside the space, and is judged by the rules of every space involved. A write that changes a page's `within` is also judged by the rules of the spaces it leaves. Tested with stand-in models only; no live model has been asked for pages, so how reliably real models produce the format is unmeasured.
- Measures: a page can watch itself, with `size` and `other_size` in watch expressions. Pressure is the first use. Nothing yet acts on pressure to relieve it.
- `verify` (clean tree, `git fsck`, signatures from `keys/allowed_signers`, trailers, files changed), `rebuild` (restore the committed state), and a command line: `init`, `write`, `ask`, `read`, `log`, `verify`, `rebuild`, `demo`, `assimilate`, `connect`.
- `conky demo`: builds a small example vault (`lemonade` or `team`, shipped as data in the package) with the real write path and narrates each step, including a refused write and a reaction.
- `conky assimilate`: takes over a stopped vault from its folder alone (a directory, a bundle, a URL, or a small one in the package), checks it, reads its pages, carries on as a new actor with a new key and checks again. It is the mechanical form of the [assimilation test](../ideas/assimilation-test.md): a mechanism result with no model, which shows that state travels and resumes and nothing about behaviour. `scripts/build_stopped_vault.py` builds the packaged vault reproducibly.
- `conky connect terminal`: the first [connector](../reference/connectors.md). It starts a terminal program in a pseudo-terminal, writes its screen to a page and types what a hands page says, as signed writes by its own actor. POSIX only and text only, tested against a small game in `tests/games/`. A page can play the program by reaction, or by asking a model, since `![[screen]]` embeds the screen text. No connector for an outside protocol is built. See [playing a program](../guide/playing-a-program.md).
- Two trailers that make activity readable from the history: `Read` on a model answer, naming the pages embedded in the prompt, and `From` on a refusal by a rule from a space. `conky log` shows them. The summaries and the activity strip that would use them are not built ([trace](../ideas/trace.md)).
- A vocabulary page that lists every name the runtime exposes, compared with the code in both directions by `tests/test_house.py`. The concept words are stated there and are not derived from code. The one check that cannot be derived, that wording stays plain, is held by review.
- A cache for model answers ([decision 0030](../decisions/0030-pay-once.md)): derived data in `~/.conky/cache`, outside every vault, keyed to the provider, the whole prompt and the event that caused the question, with the modes `on`, `off`, `refresh` and `only`, a size bound and `conky cache`. A hit is recorded as `Cache: hit`. Tested with stand-in providers only. Only model answers are cached: no other step in the code downloads or recomputes anything large, and a new costly step is routed through the cache when it is added.
- A golden vault under `tests/golden/` that every version must keep verifying and reading.
- CI that runs `scripts/check` on every pull request and on pushes to `main`.

## Unverified

- One live model call has been made, outside the test suite: a single ask through the built-in `claude` command provider in a throwaway vault, which returned `hello`, was written and passed `conky verify`. Nothing else was exercised live. The `openai` and `anthropic` HTTP shapes are tested only against stand-in servers that follow them as documented, so a real service may differ in ways the tests cannot show. The default Anthropic model id `claude-sonnet-5-5` was taken from the Claude API documentation and never called. No OpenAI default model id is known, so detection through `OPENAI_API_KEY` needs `CONKY_MODEL`. The `codex exec` form was not run because `codex` is not installed here, and detection by environment key, by `CONKY_PROVIDER` and by `codex` have only been run against fakes.
- Cost is recorded as token counts when a provider reports them. Nothing bounds it, and a model's answer is stored like any other field, with nothing marking it as unchecked.
- Nothing has been benchmarked. No claim here comes from an unscripted run, and none has been made.
- Nothing in the project has been audited for security. See [SECURITY.md](../../SECURITY.md).

## Known gaps

- Two open design questions, recorded without answers in [open questions](open-questions.md): rules on a space also apply to the space page itself, and removing the last commit is not detectable from one copy alone.
- Rules are not enforced on commits made outside conky or pushed from elsewhere. `verify` catches unsigned or unlisted-key commits, not rule violations ([decision 0002](../decisions/0002-git-is-the-store.md)).
- Write throughput is limited by one signed commit per write, in the order of tens per second.
- Temperament and voice for pages are not built. Pages in the example vaults carry human-written content, and nothing gives a page a generated temperament or voice ([a page with a self](../ideas/character.md)).
- Everything on the [roadmap](roadmap.md) is unbuilt except the first slice of measures, the demo, model pages, pages as answers, the mechanical form of the resume test and the terminal connector. A page is still within one space, and a character has no budget on how many pages it writes.
- The resume test with a model is not built, so nothing shows that a consumer other than conky's own commands can resume from a stopped vault.
