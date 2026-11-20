# conky

A small Python runtime in which every actor, tool, data store and rule is a living Markdown page.

> [!WARNING]
> Pre-alpha. This builds the first thin path only. Interfaces and file formats will change.

## Why

- The document is the system: a vault of Markdown pages, nothing hidden elsewhere.
- The log is the authority: pages are projections of a signed, append-only event log.
- Rules are enforced by the runtime, not requested in a prompt.
- Inference is for real thinking. Everything that follows from state just happens.

## Sixty seconds

```bash
pip install -e '.[dev]'   # Python 3.11 or newer
```

```console
$ conky init demo
initialised demo
$ cd demo
$ conky write market 'rules=["page.stock >= 0", "size <= 2000"]' stock=0 --as alice
written (seq 0)
$ conky write stall within=market stock=40 --body "Fresh bread." --as alice
written (seq 1)
$ conky write stall stock=-1 --as alice
refused (seq 2): rule: page.stock >= 0 (from market) is false
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
$ conky verify
ok: 6 events verified
$ rm -r pages
$ conky rebuild
rebuilt pages/ from the log
$ conky verify
ok: 6 events verified
```

`market` is a space: `stall` is `within` it and inherits its rules. The refused write is
recorded in the log and changes nothing. Writing `stall` with a stock below 10 made `depot`
change by itself, signed by the key of `depot`, with no model involved. The two extra events
are the refusal and the reaction. Private keys are kept in `~/.conky/keys`, never in the vault.

## Vocabulary

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

## What exists

- Pages with deterministic serialisation, and a write path that is the only way state changes.
- Rules in CEL, inherited through `within` chains, with `page` and `size` in scope.
- A signed, hash-chained, append-only event log that also records refused writes.
- Reactions: pages that watch other pages and write themselves, with no model call.
- `verify` and `rebuild`, and a command line: `init`, `write`, `read`, `log`, `verify`, `rebuild`.

## Not built yet

1. Tables stored as Parquet beside their page.
2. Model-backed pages: a page that asks a question state cannot answer.
3. Grouped writes and a pattern library (accounting as a pattern, not a runtime feature).
4. The assimilation test: hand a fresh consumer only a stopped vault and score whether it resumes correctly.
5. The harness-neutral benchmark against other agent harnesses.

See [docs/design.md](docs/design.md). The documentation index is [docs/README.md](docs/README.md).

## Layout

```
src/conky/   the runtime: page, log, keys, rules, vault, cli
tests/       one test per law, each fails if the law is removed
docs/        design.md, decisions, ideas, essays, project (index: docs/README.md)
<vault>/     pages/  log/events.jsonl  keys/  (public keys only)
```

## Contributing

Read [CLAUDE.md](CLAUDE.md) and [CONTRIBUTING.md](CONTRIBUTING.md). Run `ruff check .`,
`ruff format --check .` and `pytest` before opening a pull request.

## Licence

Dual licensed under [MIT](LICENSE-MIT) or [Apache-2.0](LICENSE-APACHE), at your option.
