# conky

<p align="center">
  <img src="docs/assets/conky-hero.jpg" alt="A ventriloquist puppet in a sweater that reads conky, with the caption: You just remember I call the shots here, Bubbles." width="800">
</p>
<p align="center"><sub>The name comes from Conky, the puppet in the television series <em>Trailer Park Boys</em>. The still and the quote belong to the show's owners and are not covered by this repository's licence.</sub></p>

*Pre-alpha · built and tested: Git-backed vault, rules, reactions, measures · not built: tables, model-backed pages, benchmark*

**A folder of Markdown pages that behaves like a living system: every change is a signed commit, and most of what happens needs no model at all.**

Most agent systems keep their truth in several places at once: prompts, tool schemas, a database, an orchestration script. conky keeps it in one. A vault is a Git repository of pages. Each page is a Markdown document with a few fields at the top, and it can stand for anything the system contains: a person, an agent, a team, a tool, a process, a store of data, a rule. Nothing changes a page except a write, and every write is a signed commit in the vault's Git history, made by whoever wrote it. Delete the pages and they can be restored from that history, byte for byte, and the whole vault moves with `git clone`.

Rules are checked by the runtime, not requested in a prompt. A write that breaks one is refused, and the refusal is recorded too. Pages watch each other and react, so a stock level falling below ten raises a reorder flag without anyone, human or model, deciding to. Inference is kept for the questions that state cannot answer.

The name comes from a puppet who reminds his operator who calls the shots. Anything that can be written down as pages can live here, from one agent's memory to a whole business. The first aim is in the puppet's spirit: an organisation that runs, delivers and improves without its builders. That is not built. What exists is the core, in 747 lines of Python with 40 tests, and no model attached yet.

## Sixty seconds

Python 3.11 or newer, Git 2.34 or newer and `ssh-keygen` (OpenSSH 8.2 or newer). Private keys land in `~/.conky/keys`, never in the vault.

```bash
pip install -e '.[dev]'
```

A vault, and a space called `market` whose rules its members inherit:

```console
$ conky init demo
initialised demo
$ cd demo
$ conky write market 'rules=["page.stock >= 0", "size <= 2000"]' stock=0 --as alice
written (commit 5d97c7e)
```

A member page, then a write that breaks the inherited rule. The refusal is a commit of its own and changes nothing.

```console
$ conky write stall within=market stock=40 --body 'Fresh bread.' --as alice
written (commit 1181d50)
$ conky write stall stock=-1 --as alice
refused (commit 759e7dd): rule: page.stock >= 0 (from market) is false
```

A page that watches `stall`. The next write drops the stock below 10, and `depot` changes itself in a commit signed with its own key.

```console
$ conky write depot reorder=false 'watch=[{on: stall, when: "other.stock < 10", set: {reorder: "true"}}]' --as alice
written (commit e74cb23)
$ conky write stall stock=4 --as alice
written (commit d960602)
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

A measure: a page that watches itself. A large write is not refused; the page records its own pressure in a commit of its own.

```console
$ conky write journal pressure=0 'watch=[{on: journal, when: "true", set: {pressure: "size / 400"}}]' --as alice
written (commit 35a9aa0)
$ conky write journal --body "$(python -c 'print("x" * 1000)')" --as alice
written (commit abc9184)
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

The history, then the same history read with plain Git (newest first). The `depot` commit is signed by `depot`, and its `Cause` trailer names the commit that triggered it.

```console
$ conky log
5d97c7e 2026-11-20T12:43:35Z alice write market
1181d50 2026-11-20T12:43:36Z alice write stall
759e7dd 2026-11-20T12:43:36Z alice refused stall rule: page.stock >= 0 (from market) is false
e74cb23 2026-11-20T12:43:36Z alice write depot
d960602 2026-11-20T12:43:37Z alice write stall
5c4fd6f 2026-11-20T12:43:37Z depot write depot cause d960602
35a9aa0 2026-11-20T12:43:37Z alice write journal
abc9184 2026-11-20T12:43:38Z alice write journal
2782d84 2026-11-20T12:43:38Z journal write journal cause abc9184
$ git log --oneline
2782d84 write journal
abc9184 write journal
35a9aa0 write journal
5c4fd6f write depot
d960602 write stall
e74cb23 write depot
759e7dd refused stall
1181d50 write stall
5d97c7e write market
```

Verify, destroy the pages, see verify refuse the damaged tree, restore it from the history, verify again. Nine commits: six writes, one refusal and two reactions.

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

## How it holds together

**The history is the authority.** A vault is a plain Git repository on branch `main`. Each event is a commit, signed with Git's native SSH signing, with trailers (`Kind`, `Page`, `Cause`) that say what it was. Pages in `pages/` are the committed files. Nobody edits them by hand: a working tree with changes made outside conky blocks the next write until `conky rebuild` discards them. conky keeps no log, hash chain or key format of its own ([decision 0021](docs/decisions/0021-git-is-the-store.md)).

**Rules and spaces.** A page may carry expressions in CEL (Common Expression Language, a small side-effect-free language) that must be true after every write. A page inherits the rules of every space up its `within` chain. Rules see `page` and `size`, so a size limit is an ordinary rule. A broken rule yields a recorded refusal: an empty signed commit with `Kind: refused` and the reason.

**Reactions.** A page can watch another. When the watched page changes and the `when` expression is true, the runtime writes the watching page, signed by that page's own key, with `Cause` set to the triggering commit. Reactions cascade to depth 12, then are refused as a cycle. A reaction that would change nothing is skipped, so stable states end.

**Measures.** A measure is a page watching itself. The computed value is committed like any write, so reading history never evaluates an expression. Pressure is the first use: a rising number instead of a wall. Walls stay for what must never happen. Nothing yet acts to relieve pressure.

**Verify and rebuild.** `verify` checks that the working tree is clean, that `git fsck` passes, that every commit has a good signature from a key in `keys/allowed_signers`, that every commit carries a valid `Kind` trailer, and that each commit changed only what its kind allows. `rebuild` restores the committed state. A cloned or bundled vault stands on its own. Private keys are never inside it. Rewriting history locally is detectable only against another copy. Two open design questions are recorded without answers in [decision 0015](docs/decisions/0015-open-questions.md).

## Words

| Word | Meaning |
|---|---|
| vault | The Git repository that holds everything and travels alone. |
| page | A Markdown document with YAML frontmatter. |
| key | An actor's ed25519 identity. |
| link | `[[name]]`, a reference to another page. |
| embed | `![[name#field]]`, a live inclusion resolved when the page is read. |
| rule | A pure boolean expression a write must satisfy. |
| event | One commit in the vault's Git history. |
| seal | The signature on a commit. |
| space | A page whose rules its members inherit. |
| error | A refused write. |
| read, write, watch | The verbs. |

## What exists, what does not

| Built and tested | Not built |
|---|---|
| Pages with deterministic serialisation; a write path that is the only way state changes | Tables stored as Parquet beside their page |
| Rules in CEL, inherited through `within` chains | Relief: something that acts on pressure |
| A Git repository as the store: signed commits for writes, empty signed commits for refusals | Model-backed pages |
| Reactions: pages that watch pages and write themselves | Rules that see a group of pages changed in one commit, and a pattern maker |
| Measures: self-watches, with pressure as the first use | The assimilation test on a stopped vault |
| `verify`, `rebuild` (restore the committed state), and the commands `init`, `write`, `read`, `log`, `verify`, `rebuild` | The harness-neutral benchmark; no benchmark run has been made |

There is no hosted CI. The checks are run locally before each push ([decision 0017](docs/decisions/0017-no-hosted-ci-yet.md)).

## Reading further

- [docs/README.md](docs/README.md), the documentation index.
- [docs/design.md](docs/design.md), the laws built so far.
- [docs/essays/](docs/essays/): [pressure-not-walls](docs/essays/pressure-not-walls.md), [rules-not-requests](docs/essays/rules-not-requests.md), [the-log-is-the-truth](docs/essays/the-log-is-the-truth.md) and [things-that-just-happen](docs/essays/things-that-just-happen.md).
- [docs/decisions/](docs/decisions/), one numbered record per choice.
- [docs/project/roadmap.md](docs/project/roadmap.md), the unbuilt work in order.
- [CLAUDE.md](CLAUDE.md), the rules contributors and coding agents work under.

## Running the checks

```bash
pip install -e '.[dev]'
scripts/check
```

## Licence

Dual licensed under [MIT](LICENSE-MIT) or [Apache-2.0](LICENSE-APACHE), at your option. The hero still and its quote are not covered by either.
