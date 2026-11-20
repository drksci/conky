# conky

<p align="center">
  <img src="docs/assets/conky-hero.jpg" alt="A ventriloquist puppet in a sweater that reads conky, with the caption: You just remember I call the shots here, Bubbles." width="800">
</p>
<p align="center"><sub>The name comes from Conky, the puppet in the television series <em>Trailer Park Boys</em>. The still and the quote belong to the show's owners and are not covered by this repository's licence.</sub></p>

*Pre-alpha · built and tested: log, rules, reactions, measures · not built: tables, model-backed pages, benchmark*

**A folder of Markdown pages that behaves like a living system: every change is signed into its history, and most of what happens needs no model at all.**

Most agent systems keep their truth in several places at once: prompts, tool schemas, a database, an orchestration script. conky keeps it in one. A vault is a directory of pages. Each page is a Markdown document with a few fields at the top, and it can stand for anything the system contains: a person, an agent, a team, a tool, a process, a store of data, a rule. Nothing changes a page except a write, and every write is appended to a log and signed by whoever made it. Delete the pages and they can be rebuilt from the log, byte for byte.

Rules are checked by the runtime, not requested in a prompt. A write that breaks one is refused, and the refusal is recorded too. Pages watch each other and react, so a stock level falling below ten raises a reorder flag without anyone, human or model, deciding to. Inference is kept for the questions that state cannot answer.

The name comes from a puppet who reminds his operator who calls the shots. Anything that can be written down as pages can live here, from one agent's memory to a whole business. The first aim is in the puppet's spirit: an organisation that runs, delivers and improves without its builders. That is not built. What exists is the core, in 722 lines of Python with 31 tests, and no model attached yet.

## Sixty seconds

Python 3.11 or newer. Private keys land in `~/.conky/keys`, never in the vault.

```bash
pip install -e '.[dev]'
```

A vault, and a space called `market` whose rules its members inherit:

```console
$ conky init demo
initialised demo
$ cd demo
$ conky write market 'rules=["page.stock >= 0", "size <= 2000"]' stock=0 --as alice
written (seq 0)
```

A member page, then a write that breaks the inherited rule. The refusal takes a sequence number of its own and changes nothing.

```console
$ conky write stall within=market stock=40 --body 'Fresh bread.' --as alice
written (seq 1)
$ conky write stall stock=-1 --as alice
refused (seq 2): rule: page.stock >= 0 (from market) is false
```

A page that watches `stall`. The next write drops the stock below 10, and `depot` changes itself, signed with its own key, as event 5.

```console
$ conky write depot reorder=false 'watch=[{on: stall, when: "other.stock < 10", set: {reorder: "true"}}]' --as alice
written (seq 3)
$ conky write stall stock=4 --as alice
written (seq 4)
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

A measure: a page that watches itself. A large write is not refused; the page records its own pressure as event 8.

```console
$ conky write journal pressure=0 'watch=[{on: journal, when: "true", set: {pressure: "size / 400"}}]' --as alice
written (seq 6)
$ conky write journal --body "$(python -c 'print("x" * 1000)')" --as alice
written (seq 7)
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

Verify, destroy the pages, rebuild them from the log, verify again. Nine events: six writes, one refusal and two reactions.

```console
$ conky verify
ok: 9 events verified
$ rm -r pages
$ conky rebuild
rebuilt pages/ from the log
$ conky verify
ok: 9 events verified
```

## How it holds together

**The log is the authority.** `log/events.jsonl` holds one signed line per event, each carrying the hash of the line before it. Pages in `pages/` are projections of that log. Nobody edits them by hand.

**Rules and spaces.** A page may carry expressions in CEL (Common Expression Language, a small side-effect-free language) that must be true after every write. A page inherits the rules of every space up its `within` chain. Rules see `page` and `size`, so a size limit is an ordinary rule. A broken rule yields a recorded `refused` event.

**Reactions.** A page can watch another. When the watched page changes and the `when` expression is true, the runtime writes the watching page, signed by that page's own key, with `cause` set to the triggering event. Reactions cascade to depth 12, then are refused as a cycle. A reaction that would change nothing is skipped, so stable states end.

**Measures.** A measure is a page watching itself. The computed value is written as an ordinary event, so replaying the log never evaluates an expression. Pressure is the first use: a rising number instead of a wall. Walls stay for what must never happen. Nothing yet acts to relieve pressure.

**Verify and rebuild.** `verify` checks the hash chain, every seal against the public keys in the vault, and that replaying the log from empty reproduces every page byte for byte. A copied vault stands on its own. Private keys are never inside it. Two open design questions are recorded without answers in [decision 0015](docs/decisions/0015-open-questions.md).

## Words

| Word | Meaning |
|---|---|
| vault | The directory that holds everything and travels alone. |
| page | A Markdown document with YAML frontmatter. |
| key | An actor's ed25519 identity. |
| link | `[[name]]`, a reference to another page. |
| embed | `![[name#field]]`, a live inclusion resolved when the page is read. |
| rule | A pure boolean expression a write must satisfy. |
| event | One entry in the log. |
| seal | The signature on an event. |
| space | A page whose rules its members inherit. |
| error | A refused write. |
| read, write, watch | The verbs. |

## What exists, what does not

| Built and tested | Not built |
|---|---|
| Pages with deterministic serialisation; a write path that is the only way state changes | Tables stored as Parquet beside their page |
| Rules in CEL, inherited through `within` chains | Relief: something that acts on pressure |
| A signed, hash-chained, append-only log that also records refusals | Model-backed pages |
| Reactions: pages that watch pages and write themselves | Grouped writes and a pattern maker |
| Measures: self-watches, with pressure as the first use | The assimilation test on a stopped vault |
| `verify`, `rebuild`, and the commands `init`, `write`, `read`, `log`, `verify`, `rebuild` | The harness-neutral benchmark; no benchmark run has been made |

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
ruff check . && ruff format --check . && pytest && python scripts/check_docs.py
```

## Licence

Dual licensed under [MIT](LICENSE-MIT) or [Apache-2.0](LICENSE-APACHE), at your option. The hero still and its quote are not covered by either.
