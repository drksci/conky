---
kind: research
title: "Protocols for agents, tools and interfaces"
status: current
date: 2026-11-20
source: "each protocol's own specification or site, fetched 2026-11-20"
---

# Protocols for agents, tools and interfaces

## How to read this

Every fact about an outside protocol below comes from a page fetched on 2026-11-20. The pages are listed under [Sources](#sources). Nothing comes from memory. The fetch tool returns a condensed reading of each page, so wording is paraphrased and only short phrases are quoted.

"Not confirmed" means the pages read did not settle the point. It does not mean the protocol lacks the feature.

Reach and depth:

- Every site in Sources was reached, with one exception: a guessed A2UI specification address returned HTTP 404 and was replaced by the address the A2UI index gives.
- The A2A specification page is long. The first 200,000 of its 257,720 characters were read. The remaining 57,720 were not.
- The A2UI v1.0 specification page was read up to character 100,000 of 116,612. The last 16,612 characters were not read.
- The OpenTelemetry page that used to hold the GenAI conventions says it has moved. The new repository page was read for agent spans only.
- Agent Network Protocol and the Agent Communication Protocol were read from their front pages only, not from their specifications.
- One search result summary named an arXiv survey of four protocols. The survey itself was not fetched, so nothing in this page rests on it.

conky is described from its own pages: [design](../design.md) and [status](../project/status.md). Sections on how each protocol could meet a vault are proposals. Nothing in them is built.

## Summary table

| Protocol | What it connects | Maintained by, as stated | Transport and streaming | Version or status, as stated | Licence | Link |
|---|---|---|---|---|---|---|
| Model Context Protocol (MCP) | Agent application to tools and context | GitHub organization `modelcontextprotocol`; created by two named people; foundation not confirmed | JSON-RPC over stdio or Streamable HTTP; replies as JSON or an SSE stream; subscriptions stream updates | Specification revision 2026-07-28 | MIT (repository) | [spec](https://modelcontextprotocol.io/specification/latest) |
| Agent2Agent (A2A) | Agent to agent | Linux Foundation project, part of the Agentic AI Foundation; contributed by Google | JSON-RPC, gRPC or HTTP+JSON; SSE streaming and webhook push | Latest released version 1.0.0 | Apache 2.0 (repository) | [spec](https://a2a-protocol.org/latest/specification/) |
| A2UI | Agent to interface | GitHub organization `a2ui-project`; no maintainer named on the site | Transport-agnostic JSON messages; bindings named for AG-UI, A2A, MCP, SSE, WebSockets, REST | Specification v1.0, marked current | Apache 2.0 | [spec](https://a2ui.org/specification/v1.0-a2ui/) |
| AG-UI | Agent backend to user-facing application | Created by CopilotKit, developed with the community | HTTP with SSE, and a Protobuf binding; streams events | "AG-UI 1.0" stated as stable | MIT | [docs](https://docs.ag-ui.com/introduction) |
| Agent Client Protocol (ACP) | Code editor (client) to coding agent | GitHub organization `agentclientprotocol`; maintainers not confirmed | JSON-RPC over stdio for local agents; HTTP or WebSocket for remote, in progress; streams `session/update` | Stable protocol version 1 | Apache 2.0 | [docs](https://agentclientprotocol.com/overview/introduction) |
| Agent Network Protocol (ANP) | Agent to agent across the open web, with decentralized identity | Maintainer not named; repository under `agent-network-protocol` | Built on HTTP, TLS and DNS; streaming not confirmed | 1.2 latest; some parts drafts | Not confirmed | [site](https://agent-network-protocol.com) |
| Agent Communication Protocol (BeeAI lineage) | Agent to agent over REST | Linux Foundation; its site says it is now part of A2A | REST over HTTP; streaming not confirmed | Folded into A2A, per its site | Not confirmed | [site](https://agentcommunicationprotocol.dev) |
| OpenTelemetry GenAI semantic conventions | Observability of agents and model calls | OpenTelemetry project | Not applicable: attribute names for spans; delivery is by OpenTelemetry | Status "Development" | Not confirmed | [agent spans](https://github.com/open-telemetry/semantic-conventions-genai/blob/main/docs/gen-ai/gen-ai-agent-spans.md) |

## Model Context Protocol

**What it is.** In its own words, "an open protocol" for integrating LLM applications with external data sources and tools. Messages are JSON-RPC 2.0. Three roles are named: hosts (applications that start connections), clients (connectors inside a host) and servers (services that provide context and capabilities). It says it takes some inspiration from the Language Server Protocol.

**Core objects.** Servers offer resources (context and data), prompts (templated messages and workflows) and tools (functions a model can run). A client may offer elicitation, which lets a server ask the user for more information. Optional extensions are negotiated by capability. Three are named: Tasks (long-running operations), Skills over MCP and MCP Apps (interactive interface elements shown in conversations).

**Resources.** Each resource has a URI. A client calls `resources/list` and `resources/read`, and `resources/templates/list` for URI templates. A resource has `uri`, `name`, optional `title`, `description`, `mimeType` and `size`, and its contents are text or base64 binary. The spec lists `https://`, `file://` and `git://` as standard schemes and allows custom ones.

**Streaming.** This revision says requests are stateless and self-contained, and every request carries its protocol version and client capabilities in `_meta`. Earlier revisions had a connection session with an `initialize` handshake. Two standard transports exist: stdio, and Streamable HTTP, where each message is an HTTP POST and the reply is a JSON object or a request-scoped SSE stream. A client sends `subscriptions/listen` with resource URIs, and the server sends `notifications/resources/updated` on the resulting stream. A server that declares `listChanged` may send `notifications/resources/list_changed`.

**Identity and permission.** Authorization is optional. For HTTP transports the spec is based on OAuth 2.1 (an IETF draft) and related standards: the MCP server acts as a resource server, the client as an OAuth client, and a separate authorization server issues tokens. Tokens must be bound to the server they are for. Servers answer 401 or 403 with scope hints. Over stdio, credentials come from the environment. The resource list may vary with the authorization presented on a request. The overview says MCP itself cannot enforce its consent principles and tells implementors to build consent flows.

**User interaction.** Hosts must obtain explicit user consent before invoking a tool or exposing user data. Resources are application-driven: the host decides how to present them.

## Agent2Agent

**What it is.** "An open standard designed to facilitate communication and interoperability between independent, potentially opaque AI agent systems". Agents discover each other, negotiate how to interact, manage shared tasks and exchange information without sharing internal state. The specification has three layers: a data model, abstract operations and protocol bindings.

**Core objects.** An Agent Card is a JSON document published by a server describing identity, skills, endpoint and authentication needs. A Task is the unit of work with an identifier and a lifecycle, with states including SUBMITTED, WORKING, INPUT_REQUIRED and COMPLETED. A Message is one turn with a role (user or agent) and one or more Parts. A Part holds text, a file reference or structured data. An Artifact is a task output made of Parts; the spec advises putting results in Artifacts, not Messages.

**Operations and bindings.** The operations include `SendMessage`, `SendStreamingMessage`, `GetTask` and `SubscribeToTask`. Bindings are JSON-RPC, gRPC and HTTP+JSON. Custom bindings are allowed. Clients send an `A2A-Version` header.

**Streaming.** Streaming needs `AgentCard.capabilities.streaming` to be true. A stream starts with a Task or Message, delivers events in order and closes at a terminal state. Each streamed event is a `StreamResponse` holding one of `task`, `message`, `statusUpdate` or `artifactUpdate`; over JSON-RPC they arrive as SSE `data:` lines. Push notifications are HTTP POST webhooks to a URL the client registers, with the same payload format. They need `AgentCard.capabilities.pushNotifications`.

**Identity and permission.** The Agent Card declares `securitySchemes` and `security`. The listed schemes are API key, HTTP authentication, OAuth 2.0, OpenID Connect and mutual TLS. Servers must reject missing or invalid credentials and must not reveal resources a client cannot access. Extended Agent Cards can be fetched after authentication.

**User interaction.** The INPUT_REQUIRED state lets a task ask for more input. Anything beyond that was not confirmed in the part of the page read.

## A2UI

The detailed account is in the next section. In short: A2UI describes an interface as declarative JSON data that a renderer draws from a catalog of components the application registered. The GitHub page calls it an "open-source generative UI framework" and says agents describe interfaces "as data rather than executable code". Specification v1.0 is current.

## AG-UI

**What it is.** "An open, lightweight, event-based protocol that standardizes how AI agents connect to user-facing applications", a bi-directional connection between a frontend and an agent backend. CopilotKit created it and it is developed with the community. The repository page says "AG-UI 1.0" is stable with a frozen specification backed by a JSON Schema.

**Events.** The events page groups them:

- Lifecycle: `RunStarted`, `RunFinished`, `RunError`, `StepStarted`, `StepFinished`.
- Text: `TextMessageStart`, `TextMessageContent`, `TextMessageEnd`, `TextMessageChunk`.
- Tool calls: `ToolCallStart`, `ToolCallArgs`, `ToolCallEnd`, `ToolCallResult`, `ToolCallChunk`.
- State: `StateSnapshot`, `StateDelta`, `MessagesSnapshot`.
- Activity: `ActivitySnapshot`, `ActivityDelta`.
- Also reasoning, subagent, special (`Raw`, `Custom`) and draft events.

**Streaming and state.** A message opens with a start event, carries `delta` chunks in order and closes with an end event. `StateSnapshot` replaces the frontend state. `StateDelta` carries an array of JSON Patch operations (RFC 6902). The docs describe shared state as a typed store between agent and app, using "streamed event-sourced diffs".

**Transport.** The spec defines HTTP with SSE and a binary HTTP with Protobuf binding, and says other transports such as WebSockets are possible.

**User interaction.** Human-in-the-loop interrupts let users pause, approve, edit, retry or escalate. A `resume` array on a new run answers open interrupts. Frontend tool calls hand work from agent to app.

**Identity and permission.** Not confirmed. The pages read do not describe them.

## Agent Client Protocol

**What it is.** A standard for communication between code editors and coding agents, local or remote, compared by its own page to the Language Server Protocol. The repository says "A protocol for connecting any editor to any agent". It reuses MCP's JSON representations where possible and adds types such as diffs.

**Methods.** `initialize` negotiates versions and capabilities. `authenticate` is used if the agent requires it. `session/new` creates a session and `session/load` resumes one. `session/prompt` sends the user's message and its response ends the turn with a stop reason. `session/cancel` interrupts. `session/update` is an agent notification carrying message chunks, tool calls, plans and mode changes. `session/request_permission` asks the client to get user authorization for a tool call. Optional `fs/read_text_file`, `fs/write_text_file` and `terminal/*` methods are gated by client capabilities.

**Transport.** Local agents run as subprocesses speaking JSON-RPC over stdio. Remote agents use HTTP or WebSocket, and the page says full support for remote agents is a work in progress. Stable protocol version is `1`; schema folders `v1` and `v2` exist in the repository.

## Agent Network Protocol

Described as an "open protocol stack for the Agentic Web" covering decentralized identity, discovery, messaging and payment. Identity uses `did:wba`, with readable handles mapped to those identities. It builds on HTTP, TLS and DNS. Version 1.2 is latest; 1.1 and 1.0 are archived; a meta-protocol for agent communication and a payment protocol are marked drafts, and group end-to-end encryption is a candidate. Message formats, streaming and licence were not confirmed.

## Agent Communication Protocol

The site of this REST-based protocol says "ACP is now part of A2A under the Linux Foundation" and links a migration guide. BeeAI is named as the reference implementation. It is listed here because older surveys name it as a separate protocol. Its message formats were not read.

## OpenTelemetry GenAI semantic conventions

These define names and attributes for traces of agents and model calls. The old address says the page has moved to the repository `semantic-conventions-genai`. The agent spans page there is marked "Status: Development". It defines operations `create_agent`, `invoke_agent`, `invoke_workflow`, `plan` and a framework entry point form, and refers to a separate document for `execute_tool`. Key attributes include `gen_ai.operation.name`, `gen_ai.provider.name`, `gen_ai.agent.id` and `gen_ai.agent.name`. `create_agent` spans should be CLIENT kind and `invoke_agent` internal spans INTERNAL. This is not a wire protocol between parties. Licence was not confirmed.

## A2UI in detail

All of this is from the A2UI v1.0 specification and concept pages, apart from the repository facts.

**Status and version.** Specification v1.0 is marked "Current". The page gives a creation date of 2025-11-20 and a last update of 2026-06-08. v0.9.1 and v0.9 are listed as previous and v0.8 as deprecated. The GitHub page lists protocol v1.1 as in requirements gathering. The roadmap names no next version or dates and says priorities may change. The licence is Apache 2.0.

**How an interface is described.** An interface is a surface. The agent sends components as a flat list, where relationships are expressed by identifier references such as `children` and `child`, not by nesting. One component must have the id `root`; components that arrive before it are buffered. Each component has an `id`, a `component` name and optional fields such as `@catalogId` and `@accessibility`. A catalog defines which components and functions exist, with `allowedParents` and `allowedChildren` limiting how they nest. The Basic Catalog defines components such as Text, Button, Row and Column. The agent can place only components the application has registered, so the wire format carries no executable code.

**Data and binding.** A surface has a data model, a JSON object. Components bind to values with `{"@path": "..."}` using JSON Pointers (RFC 6901), and call catalog functions with `{"@call": "..."}`. Input components bind two ways, locally. The data model goes to the agent only with an action, or with every message when the surface sets `sendDataModel`.

**How updates are sent.** Every message carries `"version": "1.0"` and exactly one top-level key. Agent to renderer:

- `createSurface`: `surfaceId`, and optionally `catalogId`, `sendDataModel`, `components`, `dataModel`, `metadata`. A duplicate `surfaceId` is an `INTEGRITY_ERROR`.
- `updateComponents`: `surfaceId` and `components`. A component whose `id` exists replaces the stored one.
- `updateDataModel`: `surfaceId`, `value` and optional `path`. A null value removes the key.
- `deleteSurface`: `surfaceId`.
- `callRendererFunction` and `agentFunctionResponse` for function calls.

The page says the client "streams it in as the agent thinks". The messages are asynchronous JSON. The transport must give reliable ordered delivery and message framing, such as JSONL, SSE or WebSocket frames. Two-way transport is optional, and a REST binding without streaming is named.

**How user actions return.** A component's `action.event` makes the renderer send an `action` message with `name`, `surfaceId`, `sourceComponentId`, `timestamp` (ISO 8601) and `context`, plus optional `userMessage` and `metadata`. Before sending, the renderer resolves the bindings in `context` against the current data model. A component's `action.functionCall` instead runs a catalog function, locally if the renderer implements it, otherwise through `callAgentFunction` and the agent's `agentFunctionResponse`. Access is limited by `allowedCallers` (`rendererOnly`, `agentOnly` or `rendererOrAgent`), and `requiresUserActivation` limits a function to direct user gestures.

**What a client must implement.** The v1.0 page lists these requirements: deliver messages in order and validate each against the envelope schema; buffer components until `root` exists and show placeholders for missing references; resolve every component and function through its catalog; apply the coercion rules for conditions; map accessibility attributes to the platform; enforce `allowedCallers`, `requiresUserActivation` and argument checks; and answer every `callRendererFunction` with a `rendererFunctionResponse`. Renderers named on the site are React, Lit, Angular, Flutter, SwiftUI and Jetpack Compose, plus community ones.

**Over A2A.** The A2A extension uses the URI `https://a2ui.org/a2a-extension/a2ui/v1.0`. Messages travel as A2A `DataPart`s with `metadata["mimeType"] = "application/a2ui+json"` and an array of messages as data. The renderer advertises catalogs in `message.metadata["a2uiRendererCapabilities"]`, and an agent must not send A2UI parts in reply to a message without such an entry. Agents may declare support in their Agent Card.

**Errors and security.** Named codes include `INTEGRITY_ERROR`, `INVALID_FUNCTION_CALL`, `EXECUTION_ERROR`, `EXPRESSION_ERROR`, `UNALLOWED_PARENT`, `UNALLOWED_CHILD` and `VALIDATION_FAILED`. Validation feedback is sent back to the model in a prompt, generate and validate loop. Regex patterns are restricted, and `sendDataModel` data goes only to the agent that created the surface.

## How each could meet a vault

These are proposals. None is built. They follow the idea in [connectors](../ideas/connectors.md): a connector beside a vault reads pages and turns what arrives into ordinary signed writes by the connector's own key.

- **MCP.** Pages could be served as resources, with a URI per page, and a change to a page sent as `notifications/resources/updated` to subscribers. A tool call that writes would become one ordinary signed write, refused by a rule like any other. conky lacks a mapping from an OAuth token to a key and to the limits that key has, and a way to hold a tool call for permission, which is the [gatekeeper](../ideas/gatekeeper.md).
- **A2A.** An Agent Card could be written from a page, and an incoming message could become a write to a page that records the task. The task states would be fields of that page, and a status change would be a new commit. conky has no task lifecycle word and no outbound webhooks. It would need a decision on how a task maps to a page and how long streams follow history.
- **A2UI.** A layout page could be turned into `createSurface` and `updateComponents`, and each commit to a page into `updateDataModel`. An `action` message would become a write to a named page. conky lacks a description of a layout, a catalog, and the [compositor](../ideas/compositor.md) that would produce one. See [a screen from the pages](../ideas/a2ui.md).
- **AG-UI.** The history could be replayed as events: a commit to a page as a `StateDelta`, and an answer from a page that asks a model as a text message. User input would come back as writes. conky has no run, no token-level streaming and no interrupt. A model answer is one write when it completes.
- **Agent Client Protocol.** A connector could let an editor read and write pages through `fs/*` style methods, with each write signed and ruled. `session/request_permission` is the nearest match to a held proposal. conky has no session word and no gatekeeper built.
- **Agent Network Protocol.** The `did:wba` identity could in principle be tied to a vault key, but how is not confirmed, because the specification was not read. conky lacks a record of an outside identity beside a key.
- **Agent Communication Protocol.** No separate mapping. Its site says it is part of A2A, so the A2A proposal applies.
- **OpenTelemetry GenAI.** Commits and their `Cause` trailers could be exported as spans, with the history as the source and the export as derived data ([decision 0017](../decisions/0017-derived-data.md)). conky has no span identifiers and no mapping from a commit to an operation name. See [the history is the trace](../ideas/trace.md).

## Sources

All fetched on 2026-11-20.

- https://modelcontextprotocol.io/specification/latest
- https://modelcontextprotocol.io/specification/2026-07-28/basic/transports
- https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization
- https://modelcontextprotocol.io/specification/2026-07-28/server/resources
- https://github.com/modelcontextprotocol/modelcontextprotocol
- https://a2a-protocol.org/latest/specification/ (characters 0 to 200,000 of 257,720)
- https://github.com/a2aproject/A2A
- https://a2ui.org
- https://a2ui.org/llms.txt
- https://a2ui.org/specification/v1.0-a2ui/ (characters 0 to 100,000 of 116,612)
- https://a2ui.org/specification/v1.0-a2ui-extension-specification/
- https://a2ui.org/concepts/messages/
- https://a2ui.org/concepts/actions-and-functions/
- https://a2ui.org/roadmap/
- https://github.com/a2ui-project/a2ui
- https://docs.ag-ui.com/introduction
- https://docs.ag-ui.com/concepts/events
- https://github.com/ag-ui-protocol/ag-ui
- https://agentclientprotocol.com/overview/introduction
- https://agentclientprotocol.com/protocol/overview
- https://github.com/agentclientprotocol/agent-client-protocol
- https://agent-network-protocol.com
- https://agentcommunicationprotocol.dev
- https://opentelemetry.io/docs/specs/semconv/gen-ai/gen-ai-agent-spans/ (moved notice)
- https://github.com/open-telemetry/semantic-conventions-genai/blob/main/docs/gen-ai/gen-ai-agent-spans.md

Fetched and returned HTTP 404: https://a2ui.org/specification/v1.0/ (an address guessed before the index was read).
