---
kind: idea
title: A screen from the pages
status: idea
date: 2026-11-20
source: maintainers
---

# A screen from the pages

## Idea

A page can be shown to people as a composed screen described in the A2UI format. In the A2UI specification (v1.0, read on 2026-11-20), an interface is declarative JSON data, not code: a flat list of components that refer to each other by identifier, drawn by a renderer from a catalog the application chose. Updates arrive as a stream of messages that add components or change bound values. A user action goes back as a message carrying the event name, the source component and its resolved context. The details, and what a renderer must implement, are in [protocols for agents, tools and interfaces](../research/protocols.md#a2ui-in-detail).

How a layout is chosen is the subject of [the compositor](compositor.md). How the messages reach a renderer is the subject of [connectors](connectors.md).

The screen is derived from the page: its fields and its words decide the components, and it can be regenerated at any time. The content shown is the page's own words, so the screen reads as a person's notice, not a dashboard of machine labels.

Nothing is built. The wireframe in the [README](../../README.md) is a sketch, not an output of any code.

## Composes from

Page, derived data ([decision 0017](../decisions/0017-derived-data.md)), and the people's view described in [obsidian-view](obsidian-view.md).

## Falsifying test

The screen for a page can be rebuilt from the vault alone and matches after a change. Deleting it loses nothing.

## Open questions

- Which components.
- How a client is given the output.
