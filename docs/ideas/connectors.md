---
kind: idea
title: "Connectors: every protocol is a door, not a room"
status: idea
date: 2026-11-20
source: maintainers
arch:
  covers:
  - part.connect.terminal
  - place.beside.connector
  items:
  - kind: part
    name: part.connect.protocol
    layer: layer.edge
    text: Connectors for the protocols people already use, each a door and not a room.
    roadmap: R25
---

# Connectors: every protocol is a door, not a room

## Idea

Conky speaks the protocols people already use through connectors, and none of them lives inside it.

A connector is a small process beside a vault. It reads the vault and presents it in a protocol's terms: pages as resources or components, changes as a stream of updates. It turns what arrives through the protocol into ordinary writes, signed with the connector's own key, so the same rules and the same [gatekeeper](gatekeeper.md) apply as to anyone else.

A connector holds no state. Stop it, delete it, start another, and nothing is lost. Streaming comes from the history: a connector follows new commits and pushes each change out as it lands.

The protocols fall into four families. The examples were read in [protocols for agents, tools and interfaces](../research/protocols.md), which also says how far each was read.

- **Tools and context.** The Model Context Protocol serves a host application with resources, prompts and tools.
- **Agent to agent.** Agent2Agent describes tasks, messages and artifacts between independent agents.
- **Interfaces.** A2UI describes a screen as data a renderer draws, and AG-UI streams events between an agent backend and an application. See [a screen from the pages](a2ui.md) and [the compositor](compositor.md).
- **Clients.** The Agent Client Protocol connects a code editor to a coding agent.

Apart from the terminal connector below, nothing is built. The mappings in the research page are proposals. How a connector to a tool server would make its tools discoverable and callable as pages is in [tools](tools.md), and the drivers a first browser shelf could use are compared in [browser drivers compared](../research/browser-drivers.md).

## What was built

One connector exists: `conky connect terminal`, which gives a vault eyes and hands on a terminal program. It writes what the program shows to a screen page and types what a hands page says, both as ordinary signed writes by the connector's own actor. It holds no state, and the vault verifies with it stopped. Any page can play the program, by reaction or by asking a model. The pages, fields and limits are in the [connectors reference](../reference/connectors.md), and a run is shown in [playing a program](../guide/playing-a-program.md). It is tested in `tests/test_connect.py` against a small game.

This covers the first part of the falsifying test: a change made through the connector appears as a signed commit by the connector's key, and a rule can refuse it. Everything else here is not built: no protocol from the families above, no streaming of fast-changing data, and no way yet to grant and limit a connector's key.

## Composes from

Page, key, seal, rule, the [gatekeeper](gatekeeper.md), and derived data ([decision 0017](../decisions/0017-derived-data.md)).

## Removes

Protocol-specific code in the core, and a second copy of the state per protocol.

## Falsifying test

With a connector running, a change made through the protocol appears in the vault as a signed commit by the connector's key, and is refused when a rule forbids it.

With the connector stopped and its files deleted, the vault verifies and nothing is missing.

Two different connectors can serve the same vault at once without knowing about each other.

## Open questions

- Which protocols first.
- How a connector's key is granted and limited.
- How fast-changing data is streamed without flooding the history.
