---
kind: idea
title: A screen from the pages
status: idea
date: 2026-11-20
source: maintainers
arch:
  covers:
  - part.cli.present
  items:
  - kind: part
    name: part.screen
    layer: layer.edge
    text: A screen derived from the pages as A2UI messages, drawn by a renderer.
    roadmap: R11b
  - kind: part
    name: part.screen.page
    layer: layer.edge
    text: One static page that renders the messages, with no server.
    roadmap: R11c
  - kind: part
    name: part.screen.update
    layer: layer.edge
    text: The screen updated as the history grows.
    roadmap: R11d
  - kind: flow
    name: flow.screen.prompt
    title: The screen for people and a prompt coming back
    statement: The screen is derived from the pages and can be deleted, and a request typed into it is an ordinary write.
    rank: 10
    steps:
    - frm: lane.runtime
      to: lane.history
      text: read pages and trailers
    - frm: lane.runtime
      to: lane.outside
      text: 'derive the screen: a text outline, then A2UI messages, deletable'
    - frm: lane.person
      to: lane.outside
      text: read the screen, with a prompt control at each corner
    - frm: lane.person
      to: lane.runtime
      text: a typed request, an ordinary write under the same rules
    - frm: lane.runtime
      to: lane.history
      text: the request is recorded beside the layout it produced
    - frm: lane.page
      to: lane.provider
      text: the compositor is asked once about layout
    - frm: lane.provider
      to: lane.page
      text: a layout page
    - frm: lane.runtime
      to: lane.outside
      text: redraw by reflex, with no model call
    roadmap: R11a
---

# A screen from the pages

## Idea

A page can be shown to people as a screen, described in the A2UI format. Nothing is built, and the wireframe in the [README](../../README.md) is a sketch, not the output of any code.

In the A2UI specification (v1.0, read on 2026-11-20), an interface is declarative JSON, not code: a flat list of components that refer to each other by identifier, drawn by a renderer from a catalog the application chose. Updates arrive as a stream of messages that add components or change bound values. A user action goes back as a message with the event name, the source component and its resolved context. Details are in [protocols for agents, tools and interfaces](../research/protocols.md#a2ui-in-detail).

The screen is derived from the page. Its fields and words decide the components, and it can be regenerated at any time. It shows the page's own words, so it reads as a person's notice, not a dashboard of machine labels.

How a layout is chosen is the subject of [the compositor](compositor.md). How the messages reach a renderer is the subject of [connectors](connectors.md).

## Composes from

Page, derived data ([decision 0017](../decisions/0017-derived-data.md)), and the people's view described in [obsidian-view](obsidian-view.md).

## Falsifying test

The screen for a page can be rebuilt from the vault alone and matches after a change. Deleting it loses nothing.

## Open questions

- Which components.
- How a client is given the output.
