# conky

A runtime where every agent, tool, data store and rule is a living Markdown document in a Git-backed vault.

[![CI](https://github.com/drksci/conky/actions/workflows/ci.yml/badge.svg)](https://github.com/drksci/conky/actions/workflows/ci.yml)

> [!WARNING]
> conky is a pre-alpha research scaffold. The interfaces are sketched and several enforcement paths are stand-ins. It is not usable for real work yet.

## Why

- **The document is the system.** No config registry and no hidden state: everything has a Markdown and frontmatter surface.
- **Small, present-tense surfaces.** A surface is at most 4096 bytes. History lives in Git.
- **Physics over prompts.** Invariants are enforced by the runtime and fail closed, not requested in a prompt.
- **Few primitives, composed.** New ideas are built from existing pieces rather than added beside them.

## Core ideas

| Term | Meaning |
|---|---|
| crest | Self-certifying identity |
| surface | A Markdown document, at most 4096 bytes |
| link / slot | A reference / a live transclusion of another surface |
| seal | A signed Git commit |
| guard | A pre-commit validator bound to a surface |
| view | A declarative UI port |
| pulse | A streamed delta |

Verbs: `peek`, `watch`, `etch`. Engines: `mind` (LLM), `gear` (deterministic logic), `organ` (data store).

## What works today

| Area | State |
|---|---|
| Frontmatter parsing and link graph (`conky-graph`) | Implemented, with tests |
| Recursive slot transclusion with the 4096-byte limit | Implemented, with tests |
| Double-entry parity check | Implemented, with tests |
| Git commit per etch via libgit2 | Implemented |
| Guard certification and SMT subsumption | Stub (string matching) |
| Wasmtime capsule execution | Stub |
| ed25519 signing | Real signatures, but keys are in memory per run, so seals cannot be verified later |
| Benchmark scenarios | None yet |

## Quick start

```bash
git clone https://github.com/drksci/conky.git
cd conky
cargo build --workspace
cargo test --workspace
cargo run --bin conky -- --help
```

Commands that etch create Git commits in the Git repository of the current working directory, so run them from a separate scratch directory with `--vault` pointing there, not from this checkout.

## Repository layout

```text
crates/
  conky-airlock/   patch validation pipeline, taint fence, guard certification stub, parity checks
  conky-daemon/    the `conky` binary: Git backend, signer, pulse streams, file watcher
  conky-engines/   CEL evaluation, SQLite ledger and projections, gear tool forging
  conky-graph/     frontmatter parsing, backlink index, slot transclusion
  conky-wasm/      capsule host (stub for Wasmtime execution)
wit/conky.wit      component interface definitions
docs/blueprint.md  the v2.0 specification, partly historical
docs/gemini-osi-stack/  design conversation archive, source material only
CLAUDE.md          rules for contributors and coding agents
```

## Roadmap

1. Make v2.0 real: persistent keys and verifiable seals, real guard evaluation, a Wasmtime host.
2. A transportable vault with table and stream data in open formats, plus the assimilation test.
3. A harness-neutral benchmark run identically against other agent harnesses.
4. Fold later ideas from the archive, one mechanism at a time.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) and [CLAUDE.md](CLAUDE.md).

## License

Dual-licensed under [MIT](LICENSE-MIT) or [Apache-2.0](LICENSE-APACHE), at your option.
