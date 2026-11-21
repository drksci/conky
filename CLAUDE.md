# conky

A Python runtime (`src/conky/`) where every actor is a living Markdown page and the vault's Git history is the authority. Pre-alpha.

## How these rules work

Each rule ends with how it is held. **check** names what fails when the rule is broken. **review** means someone has to judge it, and a rule held only by review is a gap to close: build the check, not the convention.

Any rule can be challenged. Change it here first, with the reason, record it in `docs/decisions/`, then change the code.

```bash
scripts/check
```

Run this before every push. CI runs the same command on every pull request. While working, `scripts/check quick` runs only the tests that changed code can affect.

## Truth

- What is enforced is the code and its passing tests. `docs/design.md` describes the model. Nothing else is a requirement. (review)
- Say plainly what is unbuilt or unverified, in the change and in `docs/project/status.md`. (review)

## The model

- State changes only through a write committed to the vault's Git history. A change that is not in the history did not happen. (check: `tests/test_laws.py`)
- Pages are the committed files. Never edit `pages/` by hand: a stray edit is refused by the next write or discarded by `conky rebuild`. (check: `conky verify`)
- A refused write is recorded as an empty commit, never dropped. (check: `tests/test_laws.py`)
- Anything that must never happen is a rule the runtime evaluates. Never ask a model to obey a constraint. (check: `tests/test_laws.py`)
- Anything that should be noticed rather than forbidden is a pressure that triggers a reaction, not a wall that stops work. (check: `tests/test_laws.py`)
- A measure is a page watching itself. Its value is written as a recorded event, so reading history never evaluates an expression. (check: `tests/test_laws.py`)
- Whatever follows from state happens as a reflex, with no model call, so that thought can go into character, judgement and conversation. Avoiding the model is never the aim. (check: `tests/test_model.py` for the mechanism; review for the balance)
- A provider is a page; a secret is never written to a vault. (check: `tests/test_model.py`)
- A model sees its prompt and nothing else. A program that stands in for a model is started in an empty folder with its tools off. (check: `tests/test_command.py`)
- Rules and measures are pure: no clock, randomness or I/O inside them. (review)
- A vault travels alone: cloned or bundled anywhere, it verifies, and it holds no private key. (check: `tests/test_laws.py`)
- Anything built to make a vault faster or nicer to use is derived data: optional, outside the history, rebuildable from the vault alone, and safe to delete. Nothing reads it as the truth. (review: none built yet)
- Data lives in three primitives in open formats: document (Markdown with frontmatter), table (Parquet), stream (append-only log). A change of shape is a forward re-projection. Never write a down-migration or a migration ladder. (review)
- Anything that runs in the background declares a budget and is metered. (review: not built)
- Runtime output never enters this repository, except the golden vault fixture under `tests/golden/` and published benchmark results under `docs/results/`. (check: `.gitignore`)

## Design

- Everything is somebody. A page is a character with an identity, a temperament and a voice, and the rules exist so it can be lively without being dangerous. Nothing a model is shown says whether another page was written by a person or a model, so every "I" and "you" it reads is somebody's. (check: `tests/test_laws.py` for the property; review: temperament and voice are not built)
- Autonomy is the point. Structure is grown by the characters from a small seed, never installed for them: one character and a prompt is a complete starting state. The runtime supplies limits, not plans, and a character improves the system only by writing pages, so every improvement is signed, visible and reversible. (review; check: `bench/` starts every arm from one agent)
- Few parts, much said. The runtime holds the fewest primitives and fixed behaviours that still let characters compose everything else, and it is judged by how much can be said with how little. A primitive is added only when something a character needs cannot be composed from what exists, shown by a card that fails without it. The same behaviour in fewer parts is the better design. (review; check: a card under `bench/cards/` for each primitive it forced)
- Build a new concept from existing words or remove one. If it does neither, it does not land. (review)
- Domain structures (accounting, stock, approvals) are patterns made on demand from goldens and composed from existing words, never runtime features or a shipped catalogue. The runtime gains only general primitives. (review)
- Outside protocols are reached through connectors beside the vault, never built into the core. A connector holds no state and writes through the same rules as anyone. (check: `tests/test_connect.py` for the terminal connector; review for others)
- The vocabulary is `docs/reference/vocabulary.md`. It lists what exists: the plain words for the concepts, and every name the runtime exposes. The code and the page must agree, and a rename is atomic everywhere. (check: `tests/test_house.py`)
- State what exists and what is allowed, in one place the code is checked against. Never keep a growing list of what is banned, excepted or retired: a list of negative cases is debt, and a thing that is gone needs no memorial. A check asserts a property or an agreement between two sources, not the absence of named strings. (check: `tests/test_house.py` for the vocabulary; review elsewhere)
- Nothing already built has to stay. Existing code is reference, not an obligation. (review)
- No debt: no shims, deprecated aliases, dead code or fix-later notes. Replacing something removes the old thing in the same change. (check: `tests/test_house.py` for fix-later notes; review for the rest)
- No stub passes as real. Name it `stub` and say so where it is defined. (review)
- Pay once. Anything costly (a model call, an outside call, a download, heavy computation) is cached by content as derived data: outside the history, safe to delete, and keyed to the moment so a character still answers afresh after a new event. (check: `tests/test_cache.py`)
- Build nothing before something consumes it. (review)
- Ahead or different with each step. Every roadmap step says what it puts conky ahead on, or makes it meaningfully different in, against the harnesses in `docs/research/harnesses.md`, and how that will be shown. Work that only reaches parity is done when a difference depends on it, and not before. Unbuilt work is ordered by the difference it makes. (review; check: `scripts/check_docs.py` for the line on the step marked `next`)
- Look for prior art and standards before inventing, and cite what you found in the decision. (review)
- A space hands down rules, context and reactions. Prefer handing something down a space to adding a mechanism. (review: only rules are built)
- A page reads as if a person wrote it: reactions and model pages write sentences where a person would. (check: `tests/test_demo.py` for the example; review elsewhere)
- Speech comes from pages; the runtime narrates. The runtime's own lines to a model (the page instruction, the plain line, the note after a refusal, the reason for a refusal) live in `src/conky/voice.md`, read by one function, told in the third person as stage directions that name pages and never say "I" or "you", because a model answers in the voice it is spoken to in. Mechanism words and placeholder syntax are kept to the one example a person would also need. (check: `tests/test_house.py` for the page and the code agreeing, `scripts/check` for the house style on the page)
- Keep people, developers and agents on the easy path: one command to start, nothing to configure before the first write, and every error says what to do next. (review)
- It always works. Every optional part has a default, and anything that can be missing or fail has a fallback that still does something useful. A missing or failing piece lowers the result and says so in the record; it never blocks a write, breaks a vault or stops a run. A fallback is tried in a stated order and ends in one that needs nothing. (check: each part's fallback tests, starting with `tests/test_model.py`; review elsewhere)
- The first thing a newcomer sees is one command that works. The README opens with one line of what conky is, that command, then the five ideas. (review)

## Evidence

- Every law lands with a test that fails when the law is removed. (review)
- A mechanism may be dropped; the property it protected may not, unless a decision says so. Before anything is removed, replaced or simplified, the change states what the old behaviour guaranteed, including what it guaranteed by accident, and each guarantee is kept under a test or given up in writing. (review; check: `tests/invalid/` for what must be refused)
- Nothing malformed lands. Every form a page can declare has examples of it written wrongly under `tests/invalid/`, and each must be refused at the moment it is written, with a reason that says what to write instead. A new form adds its wrong examples in the same change. (check: `tests/test_invalid.py`)
- Every check says whether it is measured or judged. A judged check names its question, its evidence and its scale, and a verdict is recorded with who gave it. (check: `scripts/check_docs.py` via the generated index)
- Every trial states its objective, hypothesis, measurable success, forecast, par, dial and what a miss would mean before it runs, and the runner refuses a card without them. (check: `tests/test_bench_cards.py`)
- Benchmark results come only from unscripted runs, with the run count and raw traces kept. (review)
- Results publish themselves. `bench/publish.py` writes the charts, the data behind them, the results page and the README block from the run files, and nobody edits its output. A pilot says it supports no claim. (check: `tests/test_bench_charts.py`)
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
- Invent freely, build methodically. Ideas are the project's own to make, and research informs them without ruling them: going against a finding or a convention is allowed, and the page says so as a bet with the test that would show the bet lost. Building is the opposite: one walked step at a time, on evidence, so that what is built is trusted and not reworked. (review)

## Thinking an idea through

Every new idea, need or surprise is walked through these steps, in order, before it is planned or specified. The answers are written down, a line each. (review)

The walk widens before it narrows. Steps 1 and 2 expand the scope and are not hurried: the first answer is usually the request restated. Steps 3 to 6 distil it. Steps 7 to 9 make it real. After step 6 the idea is said once more in a single sentence. If that sentence is not shorter and truer than the request was, go round again.

1. **The image.** Say what in the world it is like, and look far from software: a trade, a myth, a household chore, a play. A good image makes the idea obvious and a little funny.
2. **The general case.** Name what it is an instance of. A request for a mailroom is a case of putting something between two things that already talk.
3. **Existing words.** Say it with what the vocabulary already has, then count what is left over. One new thing can be right. Two means the general case has not been found yet.
4. **The natural gesture.** Say what a person would do untaught: bold what matters, write a note that links, type in the editor already open. Prefer that to a mechanism.
5. **Par.** Say what the best team of any kind would do, and which standard or professional form already holds it. Stand on that.
6. **Who does it.** Ask whether a character could add it for itself when it needs it. If so, the runtime leaves room and builds nothing.
7. **The trial.** Say what would show it wrong, as a small trial with one dial and a forecast written before it runs.
8. **How it is seen.** Say how a person would watch it work, and whether watching is a pleasure.
9. **The smallest step.** Place it: what is done next, what waits, and what today's work must not close off.

Ideas that arrive faster than they can be built stop at step 9 and are recorded. Building follows the rules below, one walked step at a time.

## Docs

- Published prose passes the house style in `.vale/styles/conky/`: no stock phrases, no hype, no first person plural, no em dashes, no rhetorical questions. Errors fail the check; warnings are read and judged. (check: `scripts/check`)
- Everything worth knowing lives under `docs/` and is updated in the same change as the code it describes. (review)
- The README is for anyone and stays free of jargon; `docs/guide/` explains the ideas plainly; the technical detail lives a layer below in `docs/reference/`, `docs/design.md` and `docs/decisions/`. (review)
- Nothing internal is committed: no working notes, no account of who said what, no names of private projects. (review)
- `decisions/`: one numbered record per decision, with its context, the decision and its consequences. `ideas/`: one page per candidate. `research/`: indexes and digests of outside work. `project/`: roadmap and status. (check: `scripts/check_docs.py`)
- `research/harnesses.md` compares conky with leading harnesses on a fixed rubric, and `research/papers.md` registers outside papers with how far each was read. Both are updated when the field moves; no claim about another project is made from memory. (review)
- Every significant idea gets an essay in `essays/` a newcomer can read: what prompted it, the problem, analogues, the idea, what it solves, the hypothesis, and how the idea could be shown wrong. An essay stands alone: it motivates the idea from the general problem. (review)
- Explain mechanisms with a figure before a paragraph. Figures are pen-plotter schematics drawn from the shared tokens in `src/conky/tokens.json` (see `docs/reference/design.md`): a monochrome ground, five pens used only where they carry meaning, a transparent background, a light and a dark file, few words, readable in light and dark, each labelled as schematic, example or data. They are generated by the maintainers' tooling and never edited by hand. The README carries at most three, plus the demo recording and the concept icons, and in addition the generated benchmark and dynamics blocks, which publish themselves from run files; trial pictures are drawn by the view in `viewer/` from the record. (review)
- Every document has frontmatter (`kind`, `title`, `status`, `date`, `source`) and every link resolves. (check: `scripts/check_docs.py`)
- The architecture index is generated from annotations in the code (what is built) and from the `arch` frontmatter of ideas and decisions (what is planned). A new part, flow, archetype, slot or law is annotated where it is defined, and nobody edits the generated page by hand. (check: `scripts/check_docs.py`)

## Working here

- Work is taken from the step marked `next` in `docs/project/roadmap.md`; there is exactly one. (check: `scripts/check_docs.py`)
- Run `scripts/check` before every push; the pre-push hook does it for you once enabled. (check: `scripts/hooks/pre-push`)
- Commit subjects are `<type>: <summary>` with type feat, fix, docs, test, refactor or chore. (check: `scripts/check_commits.py`)
- A change is done when the checks pass, the docs and status match the code, a decision is recorded if the design moved, and the changelog has its line. (review)
- Build on bedrock. A new layer is run one step at a time, by hand or under a stop point, and looked at, before anything is built on it. Nothing runs in bulk, and nothing costly runs at all, until a single step has been walked through and seen to be right. (review; check: `bench/walk.py` for the benchmark)
- Small changes, each leaving the checks green.
- Think, then plan, then specify, then delegate, in that order and never in one breath. A new idea or request is first thought through by the architect and placed in the plan: what the increments are, in what order, and why. Only then is each increment written as a spec (one increment, the files it owns, the command that proves it, a step budget, the report wanted back), and only then is it handed to a worker. A task that could fail in two independent ways is two tasks. A worker that reaches its budget stops and reports. (review)
- Spend little. This is a background project: one worker at a time unless the work is truly independent, the cheapest model that can do the job, no live model call that a stand-in or the cache can replace, and nothing in bulk before a single step has been walked. (review)
- Keep the paper index fresh. `docs/research/dair-2026.md` carries the date it was last scanned. An agent starting work here looks at that date first: if it is more than seven days old, rescan the source it names, bring the index and `docs/research/papers.md` up to date, and set the date, before other work. (check: `scripts/check_docs.py` prints a reminder when the date is stale; it does not fail) (check: `scripts/check`)
