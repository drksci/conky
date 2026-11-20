---
kind: decision
title: Autonomy inside limits that hold
status: accepted
date: 2026-11-20
source: maintainers
arch:
  covers:
  - law:pages-capability
  - law:reach-flows-down
  - law:rules-only-tighten
  - law:runtime-is-not-a-page
  items:
  - kind: law
    name: spending-is-conserved
    statement: What a space may spend is shared among what is inside it, so making more characters divides a budget.
    roadmap: R17
  - kind: flow
    name: spending-conserved
    title: Spending conserved down a space
    statement: A space's budget is shared among what lies within it, and a page stops at its budget.
    rank: 3
    steps:
    - frm: Space
      to: Page
      text: a budget is shared among what is inside
    - frm: Page
      to: Runtime
      text: ask, or make another character
    - frm: Runtime
      to: Provider
      text: the call is made
    - frm: Runtime
      to: History
      text: spend is kept as a field and recorded
    - frm: Space
      to: null
      text: more characters divide the budget and never multiply it
    - frm: Runtime
      to: null
      text: at the budget the page stops
    roadmap: R17
---

# 0029 Autonomy inside limits that hold

## Context

- The examples and the first benchmark design prepared structure by hand: a party, its rules and its reactions were built for the model before it started.
- That tests the builder, not the system. The premise of the project is a system that organises and improves itself.
- Self-improvement without limits is the failure everyone fears. Limits that are requests do not hold ([decision 0001](0001-objective.md), [rules, not requests](../essays/rules-not-requests.md)).

## Decision

Autonomy is the point, and it comes from one capability held inside three laws.

**The capability: an answer is pages.** A character reads pages and writes pages ([decision 0028](0028-a-character-writes-pages.md)). Behaviour is already data: a prompt, a reaction and a rule are fields on a page. So a character that can write pages can make notes, other characters, spaces and rules, and can rewrite itself. Nothing else is needed for a system to organise or improve itself, and nothing else is added for it.

**The laws, enforced by the runtime on every write:**

1. **Reach flows down.** A character writes only inside the space it was given. What it creates there can reach no further than it can.
2. **Rules only tighten downwards.** A space's rules bind everything inside it. A member can add a rule and cannot remove or escape one ([decision 0022](0022-leaving-a-space-is-a-write-the-space-can-refuse.md)).
3. **Spending is conserved downwards.** What a space may spend is shared among what is inside it. Making more characters divides a budget and never multiplies it.

Around them, what was already true: every change is signed and says what caused it, so any improvement can be looked at, undone or branched from; the runtime is not a page, so no character can change it; private keys stay outside the vault; a person can hold a vault and step it.

**What grows instead of being built.** A team is a space a character made. A pattern is a space others chose to join, rising by use ([decision 0023](0023-a-pattern-starts-private-and-rises-by-use.md)). Reflection is a page watching itself and rewriting itself when a measure says so. A lens is a page a character keeps about how to read something ([a lens](../ideas/lens.md)). None of these is a runtime feature. The runtime's whole list is: answers that are pages, spaces that hand down rules, context and reactions, time as a write, spending kept as a field, hold and step, files beside pages, and connectors.

## Consequences

- An example or a benchmark arm starts from a seed. Structure prepared by hand is declared as such and is not a result.
- Autonomy is measured, not asserted: every harness starts from one agent and one prompt, and what it does for itself is what is compared.
- Runtime work is ordered by what lets a character do more for itself: writing pages, then spaces that hand down context and reactions, then lenses and patterns.
- What stays with people: the rules of the outermost space, and approvals where a space asks for them.
- Built: the capability, the first law and the second law. Unbuilt: the third law, time, hold and step, files beside pages, and spaces handing down context and reactions. Until the third law exists, only the depth of a cascade bounds what a self-organising character spends.
- Lenses, patterns, go-betweens and background minds stop being runtime work. They are written up as things a character can make, and may be offered on a shelf as writings.
