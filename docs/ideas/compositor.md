---
kind: idea
title: "The compositor: a screen that is asked for once"
status: idea
date: 2026-11-20
source: maintainers
---

# The compositor: a screen that is asked for once

## Idea

A compositor is the outward [lens](lens.md) for people: a page that asks a model once how a page should be laid out, records the answer as a layout page, and from then on draws the screen from the layout with no model call. The vault can then be shown as one composed screen through an interface protocol such as A2UI. See [a screen from the pages](a2ui.md) and the [protocol research](../research/protocols.md).

The model is asked again only when the shape of a page changes or a person asks for something different. How a lens stays cheap and when it is revised is described in [the lens](lens.md).

A person changes the screen by asking. Each window and element has a small prompt control at its corner that opens a box to type into, for example "show the cooler as a big number with a bar". The request goes to the compositor as an ordinary change, under the same rules and the same gatekeeper, and is recorded in the history beside the layout it produced.

The screen shows the pages' own words. With no model available it falls back to a plain default layout that always works.

A strip of plain-language notices of what the pages did, derived from the history, could sit beside the layout: see [an activity strip](trace.md#an-activity-strip).

Nothing is built.

## Composes from

Page, watch, [pages that ask a model](model-pages.md), derived data ([decision 0017](../decisions/0017-derived-data.md)), the [gatekeeper](gatekeeper.md), and [connectors](connectors.md).

## Removes

Hand-written interface code per page, and a model call on every redraw.

## Falsifying test

After a layout is written, a hundred changes to the page redraw the screen with no model call.

A request typed into a prompt control appears in the history as a change with its author, and the layout changes accordingly or the refusal is recorded.

With the provider unreachable, the default layout still shows every page.

## Open questions

- How a layout is described.
- How much a compositor may rearrange without being asked.
- How layouts are shared between vaults.
