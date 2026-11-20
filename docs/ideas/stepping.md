---
kind: idea
title: One step at a time
status: idea
date: 2026-11-20
source: the owner's request for a step or breakpoint primitive, and the prior art below
arch:
  items:
  - kind: law
    name: law.vault.hold
    statement: A person can hold a vault and step it.
    roadmap: R28
  - kind: archetype
    name: kind.hold
    by: a person
    layer: layer.edge
    text: A field held on a page named hold.
    roadmap: R28
  - kind: flow
    name: flow.vault.step
    title: Hold and step
    statement: A held vault still writes and verifies, its reactions wait until asked, and stepping to the end and running freely give the same history.
    rank: 4
    steps:
    - frm: lane.person
      to: lane.runtime
      text: write held on the page hold
    - frm: lane.runtime
      to: lane.history
      text: an ordinary event, so everyone sees it
    - frm: lane.person
      to: lane.runtime
      text: write a page
    - frm: lane.runtime
      to: lane.history
      text: the write lands and reactions wait
    - frm: lane.person
      to: lane.runtime
      text: step
    - frm: lane.runtime
      to: lane.page
      text: run exactly one due reaction, in the usual order
    - frm: lane.runtime
      to: lane.history
      text: its event
    - frm: lane.runtime
      to: lane.provider
      text: a held vault makes no model call
    - frm: lane.runtime
      to: null
      text: a breakpoint expression holds the vault when true
    roadmap: R28
---

# One step at a time

## Idea

A vault can be run one change at a time, stopped on a condition, looked at as it was at any change and branched from there, with no state that is not already in the history. None of this is built.

## Composes from

Every change is already an event with a cause, so what happens next can be computed: the reactions due are those whose `when` holds for the latest write and that have not yet run for that cause. Nothing is queued or stored.

- **Held.** A vault can be held: writes still land, and reactions wait until asked. The hold is an ordinary write, a field `held` on a page named `hold`, so everyone sees it and it survives a restart.
- **Step.** Run exactly one due reaction, in the order the runtime would have used, and stop.
- **Breakpoint.** An expression in the same language as a rule, evaluated on each write. When it is true the vault becomes held. A rule refuses, a breakpoint only pauses.
- **Look back.** The vault as it was at any event is a Git checkout of that commit. Nothing is evaluated, because measures are recorded events.
- **Branch.** An experiment starts from any event as an ordinary Git branch or clone, which is also how a [dry run](dry-run.md) works. The original history is untouched.
- **Outside the vault.** A held vault makes no model call and types no keys. The [terminal connector](../reference/connectors.md) already stops after `--max-steps` screens, but counts screens, not changes.

## Order today

After a commit, the runtime visits every page in order of name, then each `watch` entry in the order written, and runs a reaction at once, including the reactions it causes, before moving to the next entry ([rules and reactions](../reference/rules-and-reactions.md#reactions)). So the order is fixed and depth first. A condition is evaluated when its turn comes, against the pages as they are then, so a list of due reactions made in advance can differ from a free run. Stepping must evaluate at the same moment the runtime does, and that order must be written into the reference before this is built.

## Removes

A debugger state beside the history, a replay log beside the history, and special cases in test and benchmark runners for "stop after turn K".

## Uses

Debugging a cascade, teaching, stepping a benchmark run, comparing two continuations from one point, and the resume form of the [trail trial](../project/roadmap.md) ([assimilation test](assimilation-test.md)).

## Falsifying test

Stepping to the end and running freely give the same history, commit for commit. A held vault passes `verify`. A step never produces a commit that a free run would not.

## Open questions

- How a hold interacts with the [clock page](clock.md), which would otherwise keep writing.
- Whether a hold applies to a whole vault or to a space.
- What a person sees while the vault is held.

## Prior art

- A debugger stops at a breakpoint, and a conditional breakpoint stops only when its expression is true. It offers `step`, `next` and `continue` ([gdb breakpoints](https://sourceware.org/gdb/current/onlinedocs/gdb.html/Set-Breaks.html), [gdb stepping](https://sourceware.org/gdb/current/onlinedocs/gdb.html/Continuing-and-Stepping.html)). Here the condition is a rule expression and the stop is a recorded write.
- rr records a run once and replays it deterministically, and runs gdb backward through the recording ([rr](https://rr-project.org/)). A vault already is the recording, in plain Git.
- LangGraph pauses with `interrupt_before` and `interrupt_after` and resumes from a checkpoint ([interrupts](https://docs.langchain.com/oss/python/langgraph/interrupts)). Its replay re-runs later nodes, so model calls may differ, and its fork changes state and continues on a new branch ([time travel](https://docs.langchain.com/oss/python/langgraph/use-time-travel)). Here the checkpoint is a commit and the branch is Git's. Both pages were read through a fetch tool on 2026-11-20 and are paraphrased.
- [Decision 0002](../decisions/0002-git-is-the-store.md) makes Git the store, and [decision 0026](../decisions/0026-it-always-works.md) requires that a hold never break anything: a held vault still writes, verifies and travels.
