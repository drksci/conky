---
kind: idea
title: "The outside arrives as pages"
status: idea
date: 2026-11-20
source: maintainers
---

# The outside arrives as pages

## Idea

A connector brings a space into the vault: the pages it writes are what it perceives, and the pages others write to are what it can do.

That is the whole law. A tool server, a terminal program, a browser, a clock and an inbox have the same shape, and the mechanism is only space, page, write, watch and rule. Calling the written pages a connector's senses and the pages written to its hands is plain description, not a new word.

The terminal connector is the first instance and is built. It writes the `screen` page, which is what the program shows, and a character writes the `hands` page, which is what to type ([connectors reference](../reference/connectors.md)). Everything below generalises that pair.

## Tools

When a connector attaches to a tool server, it asks the server what it offers. For the Model Context Protocol (MCP) that is `tools/list`. The connector writes one page for each tool into a space, with the tool's name, description and input shape as fields. The space is a shelf, like the space of a pattern ([patterns](patterns.md)).

Discovery is reading. An agent finds what it can do by reading the shelf, as it reads any page. Nothing is placed in a prompt behind its back. A page that asks a model embeds the shelf, or one tool page, when it wants the tools in view.

A call is a write. A character writes a request to a tool's page: the arguments as fields and a turn. The connector holds no state. It sees the request in the history, performs the call, and writes the result back onto the same page as a signed write caused by the request. A failed call is a result that says so. A call that a rule refuses is recorded as a refusal, and the server never receives it.

## Reach, limits and record

Which shelves a page can see and call follows from the spaces it is within, so a team's tools are handed down as its rules are ([what a space hands down](inheritance.md)). What must never be called is a rule on the tool page or its space, evaluated by the runtime and never a request to a model. Allow once, allow always or ask is the [gatekeeper](gatekeeper.md).

The record already says who called what and why: a signed request and a signed result with the request as its cause. The activity strip in [the history is the trace](trace.md) can show "Ma used browser.screenshot" with nothing added.

## Large results

A screenshot is a file kept beside the page and linked from it. A model page that embeds such a link passes the file to a provider that can read images. None of this is built. The alternatives are bytes in the history, which grows the vault with every frame, and bytes outside it with a content hash in the page, as [data beside pages](../decisions/0003-data-beside-pages.md) proposes, which keeps the vault small but leaves a replay without the pictures.

## Composes from

Page, space, rule, watch, write, event and key. A connector is the process in [connectors](connectors.md) and writes with its own key.

## Removes

A separate tool registry, and tool lists baked into prompts. The shelf is the registry, and the history says when a tool appeared and who called it.

## Depends on

Roadmap step R22: spaces that hand down context and reactions, and a page that may join several spaces. Reach follows `within`, and a shelf is handed down as context.

## Prior art

Read on 2026-11-20.

- [MCP specification, tools](https://modelcontextprotocol.io/specification/2025-11-25/server/tools): `tools/list` returns a name, description and `inputSchema` for each tool, and `tools/call` takes a name and arguments. A failed call is a result marked `isError`, and a result may hold image content. A server may announce a changed list.
- [OpenAI Agents SDK, MCP](https://openai.github.io/openai-agents-python/mcp/): each run calls `list_tools()` unless cached, with `invalidate_tools_cache()` to refresh, allow and block lists, and `require_approval` as a setting.
- [Claude Agent SDK, MCP](https://code.claude.com/docs/en/agent-sdk/mcp): tools are named `mcp__<server>__<tool>` and granted with `allowedTools`. Tool search withholds definitions and loads the ones a turn needs.
- [Agent harnesses compared](../research/harnesses.md): in these harnesses permission to call a tool is code or configuration the developer attaches.

## Falsifying test

With a tool server attached, one page per tool exists, and a page that reads the shelf finds each name and input shape with no prompt change.

A request to a tool page appears in the history signed by the caller, and the result signed by the connector's key with the request as its cause. A rule on the tool page that forbids the request records a refusal, and the server receives nothing.

With the connector stopped and its files deleted, the vault verifies, and a new connector finds the tool pages and carries on. A page outside the space cannot call the tools.

## Open questions

- How large results sit beside a page, as above.
- How a long-running or streaming tool maps to single signed writes without flooding the history.
- How tool pages are refreshed when a server's list changes.
- How a request names its arguments, since a field holds text and arguments have shapes.

## Proposed build order

1. Whole-page embeds, so a prompt can hold a page body.
2. The connector contract restated on the terminal connector.
3. An MCP connector over stdio.
4. Files beside pages, and providers that read images.
5. The browser, through an existing MCP server ([browser drivers compared](../research/browser-drivers.md)).
6. The gatekeeper.
