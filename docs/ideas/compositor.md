---
kind: idea
title: "The compositor: a screen that is asked for once"
status: idea
date: 2026-11-20
source: maintainers
---

# The compositor: a screen that is asked for once

## Idea

The whole vault can be shown as one composed screen, through an interface protocol such as A2UI. See [a screen from the pages](a2ui.md) and the [protocol research](../research/protocols.md).

Deciding how pages become a screen is a matter of judgement, so a compositor does it. A compositor is a page that asks a model how a given page should be laid out and writes the answer down as a layout, itself an ordinary page. From then on the screen is drawn from the layout with no model call, on every change. The model is asked again only when the shape of a page changes or a person asks for something different.

This is the same move as elsewhere in Conky: think once, record the result, then let it happen. See [learned reactions](learned-reactions.md).

A person can change the screen by asking. Each window and each element carries a small prompt control at its corner. Using it opens a box to type into, for example "show the cooler as a big number with a bar". The request goes to the compositor as an ordinary change, subject to the same rules and the same gatekeeper, and is recorded in the history beside the layout it produced.

The words shown on the screen are the pages' own words. With no model available the screen falls back to a plain default layout that always works.

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
