# conky

A Python runtime (`src/conky/`) where every actor is a living Markdown page and the event log is the authority. Pre-alpha.

## Truth order

1. Code and passing tests: what is enforced.
2. `docs/design.md`: the model, and what is not built yet.
3. `docs/gemini-osi-stack/`: source material. Read `SUMMARY.md` first. Never edit it or treat it as a requirement.

```bash
ruff check . && ruff format --check . && pytest
```

## The razor

- **The document is the system.** No config registry, no hidden state. If it exists, it has a Markdown + frontmatter page.
- **Pages are present tense and small.** History lives in the log; bulk lives in data primitives. A size limit is an ordinary rule a space sets, never a constant.
- **Few primitives, composed.** A new concept is built from existing primitives or deletes one. Otherwise it does not land.
- **One concept, one short word.** No synonyms, no abbreviations, no two mechanisms for one job.
- **Physics over prompts.** Invariants are enforced by the runtime and fail closed.
- **Evidence over narrative.** Only deterministic or signed facts count. Model claims and scripted output are hypotheses.
- **Inference is for real thinking.** Whatever follows from state just happens in the runtime, with no model call.
- **Pages read naturally**, as if a person wrote them.

Every principle here is open to challenge. Change it in this file first, with the reason, then change the code.

## Hard rules

- **Nothing already built has to stay.** Existing code is reference, not an obligation.

- **No tech debt.** No compatibility shims, deprecated aliases, dead code or "fix later" notes. Replacing something removes the old thing in the same change.
- **No down-migrations, no migration ladders.** Data lives in three simple primitives in open formats: document (Markdown + frontmatter), table (Parquet), stream (append-only log). A change of shape is a forward re-projection from those, never an in-place rewrite with a way back.
- **The vault travels alone.** A cold reader given only the directory can rebuild the running system. Data sits at relative paths named by its page.
- **No stub passes as real.** Name it `stub`, say so in its doc comment, and never let it mint anything shaped like `cert:` or `sig:`. Replacing a stub outranks adding a concept.
- **Runtime output never enters this repo.** Vaults and `seal:` commits live in their own repository.
- **Anything in the background declares a budget** and is metered.
- **A measure is a pure, fuel-bounded function** over pages and streams, like a rule. No clocks, RNG or I/O inside it.

## Folding ideas from the archive

Each idea states its rung wherever it is mentioned:

| Rung | Means |
|---|---|
| idea | Only in the archive. Cite `turn N` or the canvas file. |
| folded | In `docs/design.md`: the law, the primitives it composes from, what it removes, the test that falsifies it. |
| enforced | Runtime code plus a test that fails when the law is broken. |
| proven | Measured in a run that was not scripted. |

- Fold mechanisms, not vocabulary.
- The lexicon: `vault page key link embed rule event seal space error`, verbs `read write watch`. One plain word per concept; a rename is atomic everywhere.
- Contradictions are resolved in writing before folding, not by keeping both.

## Benchmarking

- A scenario is harness-neutral documents: seed prompt, starting state, observables, scoring. No harness-specific steps.
- Every harness runs it through an adapter, on the same model and budget.
- Results come only from unscripted runs, with the run count and raw traces kept.
- The assimilation test is a scenario: hand a fresh consumer only a stopped vault and score whether it resumes correctly.

## Docs

- Everything worth knowing lives under `docs/`, in the repository, and is kept current in the same change as the code it describes.
- `decisions/`: one numbered record per decision, with who decided and why. `ideas/`: one page per candidate, stating its rung. `project/`: roadmap and status.
- `essays/`: every significant idea gets an editorial piece a newcomer can read: what prompted it, the problem, analogues, the idea, what it solves, the hypothesis, and how we would know we are wrong.
- Every document has frontmatter (`kind`, `title`, `status`, `date`, `source`) and every link resolves. `scripts/check_docs.py` enforces this in CI.

## Working here

- The lead thinks, decides and reviews; economical workers edit from a precise brief.
- Build the check, not the convention: every law lands with a test that bites.
- Nothing is built before something consumes it; nothing is referenced that does not resolve.
- Look for prior art and standards before inventing.
- Say plainly what is unbuilt or unverified.
