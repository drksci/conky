---
kind: idea
title: "A habit: what recurs is thought about once"
status: idea
date: 2026-11-20
source: "maintainers; the owner's pages on Telos, anxiety kernels and MARCO, digested under research/"
arch:
  covers:
  - part:answer-cache
  - part:detection
  items:
  - kind: judged
    name: habit-is-faithful
    question: State whether this written habit is a faithful summary of what thought decided.
    evidence: The case on the page, and the answers it replaced, in the vault history.
    scale: 1 misleading, 2 partial, 3 faithful, 4 faithful and sharper than the answers
    checks: []
    state: idea
  - kind: part
    name: habit
    layer: characters
    text: 'A kept conclusion on a page: when a guard holds, then a response, because of a source, expecting what should follow.'
    state: idea
---

# A habit: what recurs is thought about once

## Idea

A habit is a kept conclusion: a case a page wrote down so that it need not think about the same situation twice. One form covers what the design had under five names.

**One ladder.** Every question a page asks is answered by the cheapest thing that can answer it: a habit (a case on the page whose guard holds), then memory (the same moment, seen before), then thought (a model, providers tried in order), then the floor (a plain sentence). The last three are built ([decision 0030](../decisions/0030-pay-once.md), [decision 0024](../decisions/0024-a-model-is-reached-by-a-key-or-a-local-program.md), [decision 0026](../decisions/0026-it-always-works.md)). The first is this idea.

**One case.** A case has four parts, all plain data on the page:

- **when**: a guard, in the rule language, pure.
- **then**: the response. An answer makes it a habit of acting, reading or laying out. An owner and an open episode make it a warning that stays open until someone has handled it ([anxiety kernels](../research/anxiety-kernels.md)).
- **because**: where the conclusion came from and when, and when it was last tested. A case with no source is not adopted.
- **expect**: what should follow if the case is right.

**Two loops.** The fast loop responds by climbing the ladder. The slow loop reflects: when a measure shows the same answer recurring, or a case's forecasts failing, the page thinks about its own cases and rewrites them, using the one capability a character has ([decision 0028](../decisions/0028-a-character-writes-pages.md)).

**One signal.** Each case is a forecast, and forecast against actual gives the reading already described for direction ([direction and drift](direction-and-drift.md)): in phase, keep applying it; drifting, make the smallest correction; out of phase, rethink. Drift that persists is taken up to a slower horizon. A case also goes back to thought when its source is old or untested, which is how a kept conclusion is stopped from becoming a prejudice.

## What it absorbs

A [lens](lens.md) is habits of reading and of laying out. A [learned reaction](learned-reactions.md) is a habit of acting. A [felt sense](felt-sense.md) is a habit of placing a magnitude. A [pattern](patterns.md) is a space of habits others chose to join. A cached answer is the exact case. These pages keep their detail and would point here.

## Composes from

Watch entries tried in order with each guard evaluated at that moment, measures, and an answer that is pages.

**Built by hand, and it works.** The playbooks under `tests/playbooks/` make a habit from those parts with no change to the runtime: a character keeps its cases as watch entries on its own page, asks a model only when no case fits, and the answer adds the case. A situation met twice is thought about once, a new situation still goes to thought, and removing the cases changes only the cost. The model is a stand-in.

**What building it found.** Two things that a slot for cases on an ask would remove, and that composition has to work around:

- A case has to mark which change it handled, so the fallback knows not to ask. Marking by content goes stale. It works when the page being watched carries a turn, as a connector's screen page does. The smallest general change is to put the id of the change being reacted to in scope.
- A question counts as settled when its prompt has not changed, even if another entry has since overwritten the answer. A case and the fallback write the same field, so a stale answer can be left in place. The smallest general change is to treat a question as settled only while its answer is still there.

So the choice between ordered watch entries and a slot is now a real one, with evidence on each side. It is not yet made ([decision 0031](../decisions/0031-build-on-bedrock.md)).

## Removes

Five separate mechanisms for one move. Prompts that re-describe a whole screen every turn. A model call for anything already decided.

## Depends on

A page reading its own recent history, so reflection has something to reflect on. The clock, for horizons. Rules that can see where a write came from: without that, a case learned from untrusted text is indistinguishable from one learned by thought.

## The bet, stated

Some of the research the project has read points the other way: agents that improve themselves have been seen copying planted instructions into what they write, and planted text in memory has been used against later sessions ([findings rubric](../research/findings-rubric.md)). Research informs this design and does not rule it. The bet here is that a self-written reflex is safe when it is a visible page with a source, bound by the rules of its space, checked against what happens, and removable. The tests below are what would show the bet lost.

## Falsifying test

- With a recurring input, model calls fall toward zero, the history shows cases being added, and outcomes do not get worse.
- A world that shifts once produces exactly one correction. A world that changes for good produces one rethink.
- Replaying thought on a sample of inputs a case covers gives the answer the case gives. Where it does not, the case should not have been adopted.
- A case built from planted text is refused. If it is adopted, the idea is unsafe as designed.
- Removing every case changes only the cost.

## Open questions

- The thresholds between in phase, drifting and out of phase are unvalidated guesses.
- How a price is put on a warning in a unit the vault shares, and whether that unit is the same as spending.
- What should never become a habit. A habit makes behaviour repeat, and a character is meant to differ from day to day ([decision 0020](../decisions/0020-everything-is-somebody.md)).

A habit has been made by hand in a test. Forecasts, the slow loop, sources on cases and warnings are not built.
