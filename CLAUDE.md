# conky

Rust runtime (`crates/`, `wit/`) where every actor is a living Markdown document, plus SunnySide (`vault/`), the lemonade-stand benchmark. This file obeys the law it states: it stays under 4096 bytes.

## Truth order

1. Code and passing tests: what is enforced.
2. `BLUEPRINT.md`: what is specified (v2.0).
3. `docs/gemini-osi-stack/`: source material only. Read `SUMMARY.md` first. Never edit it, never treat it as a requirement.

```bash
cargo build --workspace && cargo test --workspace
```

## The razor (applies to code, docs and vault alike)

- **The document is the system.** No config registry, no hidden state. If it exists, it has a Markdown + frontmatter surface.
- **Surfaces are present tense and at most 4096 bytes.** History lives in Git; bulk lives below the waterline (`.iceberg/`).
- **Few primitives, composed.** A new concept must be expressed with existing primitives, or delete one. If it does neither, it is not folded.
- **One concept, one short word.** No synonyms, no abbreviations, no two mechanisms doing the same job.
- **Physics over prompts.** Invariants are enforced by the runtime and fail closed. Nothing depends on a model behaving.
- **Evidence over narrative.** Only deterministic or signed facts count. Model claims and scripted output are hypotheses.
- **Busywork belongs to the runtime.** Agents think; links, validation, decay and bookkeeping happen underneath.
- **Surfaces read naturally.** A person should not be able to tell a surface was written by a machine.

## Folding ideas from the Gemini archive

An idea moves up one rung at a time, and its rung is stated wherever it is mentioned:

| Rung | Means |
|---|---|
| idea | Only in the archive. Cite it as `turn N` or the canvas file. |
| folded | In `BLUEPRINT.md` with: the law, the primitives it composes from, what it removes, the test that would falsify it. |
| enforced | Runtime code plus a test that fails when the law is broken. |
| proven | Measured in a run that was not scripted. |

- **Fold mechanisms, not vocabulary.** The archive renames the same ideas four times. Take the mechanism; the last name standing (v18) is an alias until ratified.
- **The lexicon in code is v2.x**: `crest surface link slot seal guard view pulse proof settle`, verbs `peek watch etch`, engines `mind gear organ`. A rename is one atomic change across `wit/`, `crates/`, `vault/` and `BLUEPRINT.md`, never partial.
- **Contradictions are resolved before folding**, in writing, not by keeping both.
- **Anything that runs in the background declares a budget** and is metered. No unmetered daemon.
- **A measure is a pure, fuel-bounded function over surfaces and pulses**, like a guard. No clocks, RNG or I/O inside it.

## Honesty about stubs

Much of the runtime is scaffold: guard certification and SMT checks are string matches, capsules do not run in Wasmtime, signing keys are ephemeral, and `scenarios.rs` prints fixed numbers.

- Never present a stub as the real thing. Name it `stub`/`sim` and say so in its doc comment.
- A stub must not mint anything shaped like `cert:` or `sig:` that a reader could take for a proof.
- Never cite simulated or scripted output as benchmark evidence, and never design from it.
- Replacing a stub with the real mechanism outranks adding any new concept.

## Vault rules

- Every surface has its `guard-` and `view-` companions, or the triad law is changed first. Do not add surfaces that break it.
- The vault travels alone: a cold reader given only the directory must be able to rebuild the running system. Bulk data sits in open formats (Parquet) at relative paths named by its surface. (rung: idea)
- `seal:` commits are runtime output. Do not hand-write them or mix them with source changes.
- Do not edit a sealed surface by hand to make a test pass.

## Working here

- Small diffs. Every new law lands with the test that proves it bites.
- When something is unbuilt or unverified, say so plainly in the change.
