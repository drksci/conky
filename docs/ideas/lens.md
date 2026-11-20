---
kind: idea
title: "A lens: think once, then keep up by reflex"
status: idea
date: 2026-11-20
source: maintainers
arch:
  items:
  - kind: archetype
    name: lens
    by: a character
    layer: characters
    text: How one shape maps to another, written once by thought and revised on surprise.
    state: idea
    roadmap: R11g
  - kind: flow
    name: lens-revised
    title: A lens written and revised on surprise
    statement: A lens is applied by reflex and rewritten only when a measure says it has stopped explaining what it sees.
    rank: 7
    steps:
    - frm: Outside
      to: Connector
      text: a raw surface changes
    - frm: Connector
      to: Page
      text: the lens page maps it by reflex, with no model call
    - frm: Page
      to: Runtime
      text: a measure of the share explained, written as an event
    - frm: Runtime
      to: Page
      text: the share falls, so pressure rises
    - frm: Runtime
      to: Provider
      text: a capable model is asked to revise the lens page
    - frm: Provider
      to: Runtime
      text: a new lens
    - frm: Runtime
      to: History
      text: the revision, an ordinary signed write
    - frm: Page
      to: null
      text: steady state makes no model call
    roadmap: R11g
    state: idea
---

# A lens: think once, then keep up by reflex

## Idea

A lens is a page that holds, in plain view, how one shape maps to another. It is written once by thought and applied afterwards by reflex, and it is rewritten only when it stops explaining what it sees.

The owner's working name was "perceptor". "Lens" was chosen because the same thing is looked through from either side.

Nothing is built. This page replaces two ideas that had the same mechanism under two names: the compositor and the go-between's reading. "Lens" is an idea word and stays out of the [vocabulary](../reference/vocabulary.md), which lists only what the code exposes.

## Two directions, one mechanism

- Inwards, a lens perceives. It maps a raw surface to pages, so characters read sentences and fields instead of pixels or payloads.
- Outwards, a lens presents and acts. It maps pages to a surface: the composed screen for people ([A2UI](a2ui.md), [the compositor](compositor.md)), or a character's plain words into the input a tool or program expects ([the go-between](tools.md#a-go-between-so-characters-never-call-tools)).

## Forms, cheapest first

A lens uses the cheapest form that explains the change and climbs only on surprise.

0. Nothing available. A plain sentence such as "the screen changed". It always works ([decision 0026](../decisions/0026-it-always-works.md)).
1. Structural. The source already has structure: a tool result, a document tree, an accessibility tree, JSON or a text protocol. The lens is a declarative map of where each fact lives. No model and no recogniser.
2. Textual. A character screen or a log. The lens is a set of regions and patterns learned once: which line is the status, where the choices are.
3. Visual. Pixels. The lens is a set of regions with a recogniser each (fixed text, a number, a bar, an icon), learned once from a few frames. Unchanged regions are skipped by hash.
4. Full look. A capable model reads the whole thing. It writes or repairs a lens and is never the steady state.

## How it stays cheap

- Change detection comes first. When nothing changed, nothing happens.
- A per-region difference means only what moved is read again.
- A budget rule caps how often a lens runs.
- Results are cached by content hash.
- What is passed on is the difference, in a sentence and a few fields.

## Surprise is a measure

A [measure](measures.md) tracks the share of each change the lens explained. When it falls, pressure rises and a capable model is asked to revise the lens page ([learned reactions](learned-reactions.md)). The revision is an ordinary signed write, so a lens has a history and can be compared, rolled back or shared.

A lens is a kind of [pattern](patterns.md): made on demand, born private and rising by use ([decision 0023](../decisions/0023-a-pattern-starts-private-and-rises-by-use.md)). A game or site needs its lens written once per vault, or once ever if it is shared.

## Composes from

Page, watch, measure, rule (as a budget), pattern, and [model pages](model-pages.md) with providers tried in order.

## Removes

The separate notions of compositor and go-between reading, and any prompt that describes a whole screen again each turn.

## Depends on

Files beside pages for images ([decision 0003](../decisions/0003-data-beside-pages.md)), an image-reading provider for form 3 and form 4 on pixels, the [clock](clock.md) for rate, and [budgets](background-minds.md).

## Prior art

Read on 2026-11-20.

- [Playwright MCP](https://raw.githubusercontent.com/microsoft/playwright-mcp/main/README.md): its README says it lets models drive a page through "structured accessibility snapshots", bypassing "the need for screenshots or visually-tuned models". This is form 1 as practised ([browser drivers compared](../research/browser-drivers.md)).
- [Wrapper induction](https://en.wikipedia.org/wiki/Wrapper_induction): the problem of devising extraction procedures "on an automatic basis", building them with as little hand-written rule as possible. A lens is a wrapper that is learned once and repaired when the source changes.
- [A2UI specification v1.0](https://a2ui.org/specification/v1.0-a2ui/): a component holds a `{"@path": ...}` JSON Pointer into the surface's data model. That is the outward map as a declarative binding ([protocols](../research/protocols.md#a2ui-in-detail)).

## Falsifying test

- With a lens in place, steady-state perception makes no model call.
- A changed layout triggers exactly one revision and then returns to reflex.
- The same lens applied twice to the same input gives the same pages.
- With the lens page removed, perception degrades to form 0 and everything carries on.

## Open questions

- How a lens page expresses regions and recognisers without becoming a programming language.
- Who may rewrite a shared lens.
- How an outward lens is checked before its output reaches a tool. A rule on the request page already covers refusal.
