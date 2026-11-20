---
kind: research
title: "Standards for trees, paths, patches and streams"
status: current
date: 2026-11-20
source: "RFCs 6901, 6902 and 7386, the WHATWG HTML standard, jsonlines.org, and the A2UI, AG-UI, MCP and Playwright pages, fetched 2026-11-20; expressions run in this repository's virtualenv"
---

# Standards for trees, paths, patches and streams

A codec that maps one tree to another needs four things: an address for a node, a form for a change, a framing for a stream of changes and a shape for an interface tree. Standards exist for the first three, and one protocol covers the fourth.

## How to read this

Every fact about an outside standard below comes from a page fetched on 2026-11-20. The three RFCs were read as plain text from rfc-editor.org. The other pages were read through a fetch tool that returns a condensed reading, so wording is paraphrased and only short phrases are quoted. Nothing comes from memory. [Not confirmed](#not-confirmed) lists what the reading did not settle.

The rule language results are not from sources. They are expressions run in this repository's virtualenv, with the version named in each case.

## Summary table

| Standard | Unit of change | Address of a node | Framing of a stream | Version or status, as stated |
|---|---|---|---|---|
| [JSON Pointer](https://www.rfc-editor.org/rfc/rfc6901.txt) | Not a change format; a string that names one value | `/foo/0`; `~1` for `/`, `~0` for `~`; `-` names the member after the last array element | None | RFC 6901, Standards Track |
| [JSON Patch](https://www.rfc-editor.org/rfc/rfc6902.txt) | An array of operations: add, remove, replace, move, copy, test | A JSON Pointer in `path` (and `from`) | None; `application/json-patch+json` | RFC 6902, Standards Track |
| [JSON Merge Patch](https://www.rfc-editor.org/rfc/rfc7386.txt) | A document shaped like the target; `null` removes a member | Position in the patch document itself | None; `application/merge-patch+json` | RFC 7386, October 2014, Standards Track |
| [Server-Sent Events](https://html.spec.whatwg.org/multipage/server-sent-events.html) | One event: fields `event`, `data`, `id`, `retry` | None | Text lines; a blank line ends an event; `text/event-stream` | WHATWG HTML Living Standard |
| [JSON Lines](https://jsonlines.org/) | One JSON value per line | None | UTF-8, one value per line, `\n` terminator | Format description; version not stated |
| [A2UI](https://a2ui.org/specification/v1.0-a2ui/) | One envelope with one key: `createSurface`, `updateComponents`, `updateDataModel`, `deleteSurface` | JSON Pointer into a per-surface data model; component `id` for interface nodes | Transport-agnostic; the transport delimits and orders messages | v1.0, marked current |
| [AG-UI events](https://docs.ag-ui.com/concepts/events) | An event: `StateSnapshot` (whole state) or `StateDelta` (JSON Patch array) | JSON Pointer inside a delta | Events page does not say; protocols page records HTTP with SSE | Events page; version not read |
| [MCP](https://modelcontextprotocol.io/specification/latest/server/tools) | A tool result with `content` and optional `structuredContent`; a resource update notice | A resource `uri` | JSON-RPC; subscription notices arrive on a `subscriptions/listen` stream | Revision 2026-07-28 |
| [Playwright accessibility snapshot](https://playwright.dev/docs/aria-snapshots) | A whole snapshot; no change format read | Role and accessible name in an indented line; element reference format not confirmed | Not applicable | Playwright documentation; version not read |

## Trees and paths

**JSON Pointer.** A pointer is a string of reference tokens, each preceded by `/`. The empty string names the whole document. In the RFC's own example, `/foo/0` is the first element of the array under `foo`, and `/` names the member whose key is the empty string. Array indices are zero-based decimal numbers with no leading zeros. The single character `-` names the position after the last element, which a pointer cannot evaluate to a value and an add operation can use. Evaluation that meets a missing member or a non-numeric array index fails. The standard says nothing about wildcards or searches: a pointer names one value.

**A2UI.** The data model is a plain JSON object for each surface, and bindings use JSON Pointer: `{"@path": "/user/name"}`. A path with a leading `/` resolves from the root. Inside a collection template a path without one is relative to the current array item. The page says the interface itself is a flat list of components, each with a unique `id`, linked by references, with `root` as the top: an adjacency list, rebuilt into a tree by the renderer.

**Accessibility snapshot.** Playwright's documentation says an ARIA snapshot is "a YAML representation of the accessibility tree", written as indented lines with a role, an optional quoted name and optional bracketed attributes, for example `- heading "Title" [level=1]`. The Playwright MCP server's page says it works from accessibility snapshots. It names a `browser_snapshot` tool with `target`, `filename`, `depth` and `boxes` parameters, and shows line patterns such as `- {ROLE} "Accessible Name":` and `- text: {TEXT}`. It does not name the format or show a complete snapshot, so that the MCP server returns the same YAML as the documentation page is read from two pages and not stated on either.

## Changes

**JSON Patch.** A patch is a JSON array of operation objects, applied in order, and each has one `op`: `add`, `remove`, `replace`, `move`, `copy` or `test`. `path` is a JSON Pointer; `move` and `copy` add `from`. `test` checks that the value at a location equals the given value. The RFC says that when an operation fails, including a failed `test`, the whole patch is not applied, so a patch is atomic.

**JSON Merge Patch.** The patch is a JSON document shaped like the target. A member in the patch that is absent from the target is added, a member that is present is replaced, and a `null` removes it. The RFC states two limits: an array is replaced whole, so part of an array cannot be patched, and because `null` means removal a target value cannot be set to `null`. The RFC's example table has `{"a":"b"}` patched by `{"a":null}` giving `{}`.

**A2UI.** `updateDataModel` carries `surfaceId`, an optional `path` (a JSON Pointer, default `/`) and a `value`. The page describes replacement at the path, not a patch format: an omitted or `/` path replaces the whole model, a missing path is created, and a `null` value removes the key. `updateComponents` adds or updates a flat list of components. The page does not say whether a component with an existing `id` is replaced or merged, and describes no way to remove one component: `deleteSurface` removes a surface and everything in it.

**AG-UI.** `StateSnapshot` has one field, `snapshot`, the complete state, which a frontend should use to replace its model. `StateDelta` has one field, `delta`, an array of JSON Patch operations (RFC 6902), applied in sequence, with a fresh snapshot requested if the frontend finds an inconsistency. The page lists other events: `MessagesSnapshot`, `ActivitySnapshot` and `ActivityDelta`, and text and tool events that stream in start, content and end pieces, such as `TextMessageStart`, `TextMessageContent` (a non-empty `delta` to concatenate) and `TextMessageEnd`.

**MCP.** A tool result may carry `content` blocks (text, image, audio, resource links, embedded resources) and `structuredContent`, any JSON value that conforms to the tool's `outputSchema` when one is declared. A tool that returns structured content should also return the JSON as a text block. A resource has a `uri`. A client lists a set of URIs in `subscriptions/listen`, and the server sends `notifications/resources/updated` on that stream carrying the `uri` and a subscription id, not the new content. The client then calls `resources/read`. No change format is defined: a notice says that something changed, not what.

## Streams

**Server-Sent Events.** The stream is `text/event-stream`. Lines end in CRLF, LF or CR. A line is a field and a value separated by a colon; a line that begins with a colon is ignored. The `data` field appends to a buffer, `event` sets the event type, `id` sets the last event id and `retry` sets a reconnection time in milliseconds. A blank line dispatches the event. The client sends a `Last-Event-ID` header when it reconnects, so the standard has a resume point built in.

**JSON Lines.** Three requirements: UTF-8 with no byte order mark, each line a valid JSON value (a blank line is not), and `\n` as the terminator. `\r\n` also parses, since surrounding white space is ignored. The page says it suits log files and message passing between processes. It has no event type, id or resume rule.

**A2UI.** The protocol is a stream of JSON objects with one top-level key each. The transport must delimit the messages and deliver them in order. The page names JSONL lines, WebSocket frames and SSE events as examples and says out-of-order delivery can corrupt interface state. Components may arrive in any order and are buffered until a `root` exists. A surface must exist before updates to it.

**AG-UI.** The events page describes an ordered sequence of events and does not name a wire format. The [protocols page](protocols.md) records HTTP with SSE and a Protobuf binding from the AG-UI introduction.

## What the rule language can do

The rule language is CEL through cel-python. The project requires `cel-python>=0.2` and the virtualenv holds 0.5.0. [`src/conky/rules.py`](../../src/conky/rules.py) builds one `celpy.Environment()` and calls `program()` with no `functions` argument, so only the library's own functions exist today. Each expression below was run with a page as `page`, a nested map such as `{"a":{"b":[{"n":"x"},{"n":"y"}],"s":"hello world 42"},"l":[1,2,3,4]}`.

Worked:

- Indexing nested maps and lists: `page.a.b[1].n` gave `y`; `page.a["b"][0]["n"]` gave `x`. A dynamic key worked: `page.a[page.k][page.i].n` with `k` set to `b` and `i` set to `1` gave `y`. A path held in a string cannot be walked by an expression, because no split function exists.
- Presence: `has(page.a.zz)` gave `false`. A missing member without `has` is an error (`no such member in mapping`), as is an index out of range.
- Comprehensions: `map`, `filter`, `exists`, `all` and `exists_one` over lists, such as `page.l.map(x, x*2)`, `page.a.b.map(i, i.n)` and `page.a.b.filter(i, i.n=="y")[0].n`. They chain, and `map` can build maps: `page.l.map(x, {"v": x})`. Over a map the variable is the key: `page.a.map(k, k)` gave the key list.
- Text tests: `matches` (a boolean test, with the `(?i)` flag working), `contains`, `startsWith`, `endsWith`, `size()` and `string(x)`.
- Concatenating lists with `+`, a conditional with `has` inside `map`, and `timestamp(...)` parsing.
- Extension functions: `program(ast, functions={...})` registered a function called both ways, `up(page.a.s)` and `page.a.s.up()`, and a two-argument `split(page.a.s, " ")` returning a list. This is a property of the library. The runtime does not pass `functions` today, so a registered function would be a change to `rules.py`, and a function that is not pure would break [law.rule.pure](../reference/rules-and-reactions.md#expressions).

## What the rule language cannot do

Each of these failed with `undeclared reference` unless stated:

- No capture. `matches` returns only a boolean: `page.a.s.matches("^hello (?P<w>\\w+)")` gave `true`, with the group lost. `regex.extract` and `regex.captureN` do not exist.
- No `split`, `substring`, `indexOf`, `lastIndexOf`, `replace`, `charAt`, `lowerAscii`, `trim`, `join` or `format`, and no `strings.*`, `math.*` or `base64.*` functions.
- No slice, `sort`, `reverse` or `flatten` on lists, and no `keys()` on maps. A slice with `page.l[1:3]` is a parse error.
- Maps do not add: `{"k": 1} + {"j": 2}` is an error, so an expression cannot build a patched copy of a map.
- A form with a filter in the middle, `page.l.map(x, x>1, x*10)`, raised a `ValueError` from the library, not a CEL error.

The result is that an expression can test and project a tree it already holds, and can answer yes or no about text, but it cannot take text apart or edit a tree. A codec that parses text, extracts a capture, splits a path or produces a patched document is not an expression. It is code outside the language, or an extension function registered into it.

## Table for a codec that maps one tree to another

| Need | Standard that supplies it | Where the standards disagree or leave a gap |
|---|---|---|
| Address of a node | JSON Pointer (RFC 6901). A2UI and AG-UI deltas already use it. | Names one value only: no wildcard, no search, no way to name a node in an accessibility snapshot, which is addressed by role and name. MCP addresses a whole resource by `uri`, not a node inside it. Array positions shift when elements are inserted. |
| Form of a change | JSON Patch (RFC 6902) in AG-UI `StateDelta`; whole-value replacement at a pointer in A2UI. | A2UI chose replacement and AG-UI chose JSON Patch, so the two do not share a change form. Merge Patch cannot patch part of an array or set `null`. MCP has no change form, only a notice. A2UI states no way to remove one component. |
| Framing of a stream | JSON Lines for plain records; SSE where an event type, an id and resume are wanted. | JSON Lines has no resume. SSE carries text, so a JSON value rides in `data`. A2UI leaves the framing to the transport, and AG-UI's events page does not state one. |
| Shape of an interface tree | A2UI: a flat list of components with ids and references, bound to a data model by pointer. | The accessibility snapshot is a nested tree, A2UI is a flat list, and neither maps to the other by a standard. Whether the Playwright MCP server returns the documented YAML is not confirmed. |
| Evaluating the mapping | None of the standards. | Pointer lookup and patch application are not in CEL as read above, so the mapping is code, not an expression, unless extension functions are registered. |

Two gaps carry over to any design that adopts them. Patch operations on arrays address positions, so a delta computed against an older document can land on the wrong element, which `test` operations in JSON Patch exist to guard against. Neither pointer nor patch says how to treat text inside a string value: a change to one line of a long string is a replacement of the whole string.

## Not confirmed

- The last 16,612 characters of the A2UI v1.0 specification page were not read. Whether `updateComponents` replaces or merges a component with an existing `id` is not stated in the 100,000 characters that were.
- The AG-UI events page does not state a wire format. The page was read for event types, `StateSnapshot`, `StateDelta` and `MessagesSnapshot` only. Its version was not read.
- The Playwright MCP page names `browser_snapshot` and shows line patterns but not a complete snapshot, the format name or the element reference format. The YAML format is from the Playwright documentation page. That the two are the same format is not confirmed.
- The MCP tools and resources pages were read at revision 2026-07-28. The `subscriptions/listen` page itself was not fetched.
- No streaming or tree-watching library was evaluated, and no Python implementation of JSON Pointer or JSON Patch was tested. Nothing here says one exists.
- The CEL results are for cel-python 0.5.0 only. The CEL language specification was not fetched, so which missing functions belong to the language and which are cel-python's gap is not confirmed. The `functions` argument was tested on strings and a list only.
- No live model was called.

## Sources

- [RFC 6901, JSON Pointer](https://www.rfc-editor.org/rfc/rfc6901.txt)
- [RFC 6902, JSON Patch](https://www.rfc-editor.org/rfc/rfc6902.txt)
- [RFC 7386, JSON Merge Patch](https://www.rfc-editor.org/rfc/rfc7386.txt)
- [Server-Sent Events, WHATWG HTML Living Standard](https://html.spec.whatwg.org/multipage/server-sent-events.html)
- [JSON Lines](https://jsonlines.org/)
- [A2UI specification v1.0](https://a2ui.org/specification/v1.0-a2ui/)
- [AG-UI events](https://docs.ag-ui.com/concepts/events)
- [MCP tools](https://modelcontextprotocol.io/specification/latest/server/tools) and [MCP resources](https://modelcontextprotocol.io/specification/latest/server/resources)
- [Playwright MCP](https://github.com/microsoft/playwright-mcp) and [Playwright ARIA snapshots](https://playwright.dev/docs/aria-snapshots)
