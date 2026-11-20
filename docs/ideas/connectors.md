---
kind: idea
title: "Connectors: every protocol is a door, not a room"
status: idea
date: 2026-11-20
source: maintainers
---

# Connectors: every protocol is a door, not a room

## Idea

Conky should speak the protocols people already use, and none of them should live inside it.

A connector is a small process beside a vault. It does two things. It reads the vault and presents it in a protocol's terms: pages as resources or components, changes as a stream of updates. And it turns what arrives through the protocol into ordinary writes, signed with the connector's own key, so the same rules and the same [gatekeeper](gatekeeper.md) apply as to anyone else.

A connector holds no state of its own. Stop it, delete it, start another, and nothing is lost. Streaming comes from the history: a connector follows new commits and pushes each change out as it lands.

The protocols fall into four families. The examples below were read in [protocols for agents, tools and interfaces](../research/protocols.md), which also says how far each was read.

- **Tools and context.** The Model Context Protocol serves a host application with resources, prompts and tools.
- **Agent to agent.** Agent2Agent describes tasks, messages and artifacts between independent agents.
- **Interfaces.** A2UI describes a screen as data a renderer draws, and AG-UI streams events between an agent backend and an application. See [a screen from the pages](a2ui.md) and [the compositor](compositor.md).
- **Clients.** The Agent Client Protocol connects a code editor to a coding agent.

Nothing is built. The mappings in the research page are proposals.

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
