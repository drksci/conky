---
kind: idea
title: "A codec: one tree into another, written once and applied by reflex"
status: idea
date: 2026-11-20
source: maintainers
arch:
  items:
  - kind: archetype
    name: kind.codec
    by: a character
    layer: layer.character
    text: A page of bindings from one tree to another, written once by thought and applied by reflex.
    state: idea
    roadmap: R11g
  - kind: flow
    name: flow.codec.revise
    title: A codec written and revised on surprise
    statement: A codec is applied by reflex and rewritten only when a measure says it has stopped explaining what it sees.
    rank: 7
    steps:
    - frm: lane.outside
      to: lane.connector
      text: a raw surface changes
    - frm: lane.connector
      to: lane.page
      text: the codec page maps it by reflex, with no model call
    - frm: lane.page
      to: lane.runtime
      text: a measure of the share explained, written as an event
    - frm: lane.runtime
      to: lane.page
      text: the share falls, so pressure rises
    - frm: lane.runtime
      to: lane.provider
      text: a capable model is asked to revise the codec page
    - frm: lane.provider
      to: lane.runtime
      text: a new codec
    - frm: lane.runtime
      to: lane.history
      text: the revision, an ordinary signed write
    - frm: lane.page
      to: null
      text: steady state makes no model call
    roadmap: R11g
    state: idea
---

# A codec: one tree into another, written once and applied by reflex

## Idea

A codec turns what a driver produces into something a character can read, and what a character intends into what the driver needs. It is written once by thought and applied afterwards with no model call.

The chain, inwards: driver, codec, perception, character. Outwards: character, intention, codec, driver. A connector runs the driver.

The owner's first name for this was "perceptor", then "codec". An earlier page called it a lens. Codec is kept because the thing is two-way by definition and comes one per form.

## One shape

Everything a codec touches is a tree, addressed by path, changed by a stream of patches. A page is such a tree: its fields and its body. So is a surface drawn for a person, a tool's structured result, an accessibility snapshot of a web page, and a screen of text read as lines. What arrives from outside is patches to a tree; what leaves is patches to a tree. Streaming is the native form, because the unit is the patch and not the document.

## What a codec is

A codec is a page holding a table of bindings between two trees. Each binding names a path in the target and gives an expression over the source. The expression is in the rule language, so it is pure and deterministic: no clock, no randomness, no I/O. A codec is therefore not a program in a new language. It is checked, recorded and ported the way rules are.

- **Written once.** A character looks at a source tree and the target it wants and writes the bindings, as an answer that is pages ([decision 0028](../decisions/0028-a-character-writes-pages.md)). That is the only step that thinks.
- **Applied by reflex.** After that, a patch to the source re-evaluates only the bindings whose paths it touches. Nothing else runs. This is what watching a tree means here.
- **Corrected in part.** A binding that stops matching what arrives is a surprise. That one binding goes back to thought; the rest keep working.

A codec is a habit whose cases are bindings ([a habit](habit.md)). It sits at the first rung of the answer ladder: a binding answers when it fits, and thought answers when none does.

## Forms are general

A form is set by the shape of the source tree, never by a particular site or program:

1. **Structured.** A tool result, an event, a document tree. A binding is a path.
2. **Lines.** A character screen or a log, read as a list of lines. A binding finds a line and takes a part of it.
3. **Regions.** Pixels, cut into regions with a recogniser for each. Last, because it needs the recogniser first.

Beneath all three is the floor every answer has: a plain sentence saying that something changed ([decision 0026](../decisions/0026-it-always-works.md)).

Only the bindings are specific to a source, and they are the generated part. The same codec applies to every screen of the same program.

## Standards, not inventions

The pieces already exist and are recorded with their sources in [streams and trees](../research/streams-and-trees.md):

- a node is addressed by a JSON Pointer;
- a change is a JSON Patch, a list of operations applied together;
- a stream is framed as lines of JSON or as server-sent events;
- a surface for a person is A2UI's flat list of components bound to a data model by the same pointers ([A2UI](a2ui.md)).

Inwards and outwards use the same pieces, so the screen composed for people ([the compositor](compositor.md)) is a codec pointed the other way.

## Where commits fit

The raw stream of patches is a stream: a table that only grows ([tables](tables.md)). It is not a commit for each patch. What a codec produces lands on a page as one signed write when it changes, at the points a connector already settles on. One signed commit for each change to a page stays true.

## What building it needs

The rule language as shipped can test and project a tree and answer yes or no about text. It cannot take a number out of a line or split one: the research page lists what was tried. So the lines form needs a small set of pure text functions added to the rule language, named after the standard extension where one exists. That is a general addition, used by rules as well.

## Composes from

Page, watch, rule, measure, an answer that is pages, the answer ladder. Connectors bring the source tree in.

## Removes

The lens, the go-between and the compositor as three separate ideas. Any prompt that re-describes a whole screen on every turn.

## Depends on

Pure text functions in the rule language. A page reading more than itself, so a rule can use what a codec decoded ([inheritance](inheritance.md)). Files beside pages and a recogniser, for the regions form only.

## Falsifying test

- With a codec in place, steady perception makes no model call.
- A changed layout sends one binding back to thought, once, and the others are untouched.
- The same codec applied twice to the same source gives the same page.
- Removing the codec page falls back to the plain sentence and nothing breaks.
- A patch that touches no bound path evaluates nothing.

## Open questions

- How large a table of bindings a small model writes correctly in one answer.
- Who may rewrite a codec that several characters share.
- Whether an outward codec's result should be checked by a rule before it reaches a tool.

Nothing of this is built.
