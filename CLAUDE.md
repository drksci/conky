# conky

A Python runtime (`src/conky/`) where every actor is a living Markdown page and the event log is the authority. Pre-alpha.

## How these rules work

Each rule ends with how it is held. **check** names what fails when the rule is broken. **review** means someone has to judge it, and a rule held only by review is a gap to close: build the check, not the convention.

Any rule can be challenged. Change it here first, with the reason, record it in `docs/decisions/`, then change the code.

```bash
ruff check . && ruff format --check . && pytest && python scripts/check_docs.py
```

## Truth

- What is enforced is the code and its passing tests. `docs/design.md` describes the model. `docs/gemini-osi-stack/` is source material: never edit it, never treat it as a requirement. (review)
- Say plainly what is unbuilt or unverified, in the change and in `docs/project/status.md`. (review)

## The model

- State changes only through a write appended to the log. A change that is not in the log did not happen. (check: `tests/test_laws.py`)
- Pages are projections of the log. Never edit `pages/` by hand. (check: `conky verify`)
- A refused write is recorded, never dropped. (check: `tests/test_laws.py`)
- Anything that must never happen is a rule the runtime evaluates. Never ask a model to obey a constraint. (check: `tests/test_laws.py`)
- Anything that should be noticed rather than forbidden is a pressure that triggers a reaction, not a wall that stops work. (review: not built)
- Whatever follows from state happens as a reaction, with no model call. Ask a model only what state cannot answer. (review)
- Rules and measures are pure: no clock, randomness or I/O inside them. (review)
- A vault travels alone: copied anywhere, it verifies and rebuilds, and it holds no private key. (check: `tests/test_laws.py`)
- Data lives in three primitives in open formats: document (Markdown with frontmatter), table (Parquet), stream (append-only log). A change of shape is a forward re-projection. Never write a down-migration or a migration ladder. (review)
- Anything that runs in the background declares a budget and is metered. (review: not built)
- Runtime output never enters this repository. (check: `.gitignore`)

## Design

- Build a new concept from existing words or remove one. If it does neither, it does not land. (review)
- One plain word per concept: `vault page key link embed rule event seal space error`, verbs `read write watch`. A rename is atomic everywhere. (check: `tests/test_house.py`)
- Nothing already built has to stay. Existing code is reference, not an obligation. (review)
- No debt: no shims, deprecated aliases, dead code or fix-later notes. Replacing something removes the old thing in the same change. (check: `tests/test_house.py` for fix-later notes; review for the rest)
- No stub passes as real. Name it `stub` and say so where it is defined. (review)
- Build nothing before something consumes it. (review)
- Look for prior art and standards before inventing, and cite what you found in the decision. (review)
- A page reads as if a person wrote it. (review)

## Evidence

- Every law lands with a test that fails when the law is removed. (review)
- Benchmark results come only from unscripted runs, with the run count and raw traces kept. (review)
- A scenario is harness-neutral documents: seed prompt, starting state, observables, scoring. Every harness runs it through an adapter on the same model and budget. (review: not built)
- The assimilation test is a scenario: hand a fresh consumer only a stopped vault and score whether it resumes correctly. (review: not built)

## Ideas

An idea states its rung wherever it is mentioned, and climbs one rung at a time. (check: `scripts/check_docs.py`)

| Rung | Means |
|---|---|
| idea | A page in `docs/ideas/` naming its source. |
| folded | In `docs/design.md`: the law, what it composes from, what it removes, the test that falsifies it. |
| enforced | Runtime code plus a test that fails when the law is broken. |
| proven | Measured in a run that was not scripted. |

- Take the mechanism from a source, not its vocabulary. (review)
- Resolve contradictions in writing before folding, not by keeping both. (review)

## Docs

- Everything worth knowing lives under `docs/` and is updated in the same change as the code it describes. (review)
- `decisions/`: one numbered record per decision, with who decided and why. `ideas/`: one page per candidate. `research/`: indexes and digests of outside work. `project/`: roadmap and status. (check: `scripts/check_docs.py`)
- Every significant idea gets an essay in `essays/` a newcomer can read: what prompted it, the problem, analogues, the idea, what it solves, the hypothesis, and how we would know we are wrong. (review)
- Every document has frontmatter (`kind`, `title`, `status`, `date`, `source`) and every link resolves. (check: `scripts/check_docs.py`)

## Working here

- The lead thinks, decides and reviews. Edits go to economical workers with a precise brief. (review)
- Small changes, each leaving the checks green. (check: CI)
