---
kind: research
title: "Browser drivers compared"
status: current
date: 2026-11-20
source: "each project's GitHub page, documentation and protocol pages, fetched 2026-11-20"
---

# Browser drivers compared

## How to read this

Every fact about an outside project below comes from a page fetched on 2026-11-20. The pages are listed under [Sources](#sources). Nothing comes from memory. The fetch tool returns a condensed reading of each page, so wording is paraphrased and only short phrases are quoted. "Not confirmed" means the pages read did not settle the point. It does not mean the feature is absent.

Reach and depth:

- Star counts and licences were read from each repository's front page. Latest releases were read from each repository's releases page. Those pages show a day and month without a year, apart from the Chrome DevTools MCP page, which also shows 2026. Dates are given as shown.
- Playwright (Python) was read from its repository page and its `Mouse` and `Keyboard` API pages. Its repository page does not discuss headless mode.
- The OpenAI computer use guide returned HTTP 403 at its usual address and was read at the Markdown address the search result gave.
- The Anthropic computer use page was read up to character 100,000 of 132,268. The rest was not read.
- A fetch of the game page at https://oregontrail.ws/games/the-oregon-trail-deluxe/play returned only a loading message, so how the page embeds the emulator was not confirmed. That the game draws into a `<canvas>` is the owner's statement, not a finding here.
- Nothing was installed or run. No driver was tested against the game.

The question is practical. [Connectors](../ideas/connectors.md) describes a connector as a process beside a vault, and `conky connect terminal` is built ([reference](../reference/connectors.md)). The owner wants the same for the web, built on a mature driver, and the first consumer is a party of characters playing a DOS game inside a browser emulator. A canvas exposes no useful DOM, so the driver has to return screenshots and send raw keys and clicks.

## The rubric

**(a) What it is, as it says.** The project's own description.

**(b) Language and how it is driven.** Library, command line, or Model Context Protocol (MCP) server, and over which transport.

**(c) Licence.**

**(d) Own model in the loop.** Whether the project needs a language model of its own, or can be driven one call at a time by an outside caller.

**(e) Screenshots.** Whether it can return an image of the page.

**(f) Raw keys.** Whether it can send key presses that are not tied to a DOM element.

**(g) Raw clicks at coordinates.** Whether it can click at an x, y position, which a canvas needs.

**(h) Headless.** Whether it runs without a display.

**(i) Stars and latest release.** As shown on the pages today.

## The matrix

| Driver | (b) Language, driven | (c) Licence | (d) Own model | (e) Screenshot | (f) Raw keys | (g) Click at x, y | (h) Headless | (i) Stars, release |
|---|---|---|---|---|---|---|---|---|
| browser-use | Python; library, CLI (`browser-use --cli-mcp` runs an MCP server), cloud API | MIT | Its `Agent` runs on one; the CLI runs Python, not agent tasks | Page shows screenshots in an optional judge step; as a tool, not confirmed | Not confirmed | Not confirmed | Yes | 121.6k; 1.0.6, 16 Nov |
| Playwright MCP | Node 20+; MCP over stdio by default, HTTP with `--port` | Apache-2.0 | None; the MCP client supplies it | `browser_take_screenshot`; saved to a file by default; inline return not confirmed | `browser_press_key` | `browser_mouse_click_xy`, only with `--caps=vision` | `--headless` flag; headed by default | 39.9k; v0.0.86, 18 Nov |
| Stagehand | TypeScript, Python, Go; SDK, `browse` CLI, hosted MCP | MIT | `act`, `observe`, `extract` need one; `browse` CLI needs no key; the page methods below do not mention one | `screenshot()` | `keyPress(key)`, `type(text)` | `click(x, y)`, `hover`, `scroll`, `dragAndDrop` | Not confirmed | 26.1k; `@browserbasehq/stagehand@3.7.4`, 18 Nov |
| Skyvern | Python and TypeScript SDKs, local API server, cloud API, CLI, MCP | AGPL-3.0 | Required | Not confirmed as an API | Not confirmed | Not confirmed | Not confirmed | 23.5k; v1.0.58, 15 Nov |
| Playwright (Python) | Python; library, sync and async | Apache-2.0 | None; not an agent | `page.screenshot` | `keyboard.press`, `type`, `down`, `up` | `mouse.click(x, y)`, `move`, `dblclick` | Not confirmed on the page read | 15.1k; v1.65.2, 14 Nov |
| Chrome DevTools MCP | Node; MCP via `npx`, and a `chrome-devtools` CLI | Apache-2.0 | None; the client supplies it | `take_screenshot` (png, jpeg, webp) | `press_key` | `click_at`, only with `--experimentalVision=true` | `--headless` flag | 58.5k; chrome-devtools-mcp-v1.13.0, 11 Nov 2026 |
| agent-browser (Vercel Labs) | Rust CLI with a daemon over CDP; MCP over stdio via `agent-browser mcp` | Not confirmed on the page read | None stated; built to be driven by an outside agent | `screenshot` | `keyboard`, `press` listed | `mouse`, `click`, `drag` listed; coordinates not detailed | Appears to be the default; no flag documented | 53.0k; v0.43.0, 12 Nov |
| Anthropic computer use | Tool interface; the caller's code executes each action | Not applicable | The model is the point | `screenshot`, `zoom`; returned as an image block | `key`, `type`, `hold_key` | `left_click` with `coordinate: [x, y]` and variants | Not applicable | Not applicable |
| OpenAI computer tool | Tool interface; the caller's code executes each action | Not applicable | The model is the point | `screenshot` action; returned as a `computer_screenshot` base64 PNG | `keypress`, `type` | `click` with `x`, `y` and variants | Not applicable | Not applicable |

## Per-candidate notes

### browser-use

Its page calls it "the open-source browser agent": a model completes a task in a real browser by writing Python in a persistent REPL, using helper functions and raw Chrome DevTools Protocol (CDP) calls. The page lists the library, a CLI and a hosted API, and says the API key also works with "the CLI and MCP server". The CLI page lists `browser-use --cli-mcp` to run the MCP server and says the CLI "runs Python, not agent tasks". The documentation shows a cloud browser that hands back a `cdpUrl`, to which Playwright can connect, so a caller can drive the page itself. The documentation read does not list the MCP server's tools, so raw keys, raw clicks and inline screenshots are not confirmed. The pages also carry text addressed to AI agents asking for feedback messages. That text is not part of this research and was not acted on.

Sources: [repository](https://github.com/browser-use/browser-use), [releases](https://github.com/browser-use/browser-use/releases/latest), [documentation](https://docs.browser-use.com), [open-source introduction](https://docs.browser-use.com/open-source/introduction), [CLI](https://docs.browser-use.com/open-source/cli).

### Playwright MCP

"A Model Context Protocol (MCP) server that provides browser automation capabilities using Playwright." It runs on Node.js 20 or newer, over stdio by default, or as an HTTP server with `--port`. It is built to work from structured accessibility snapshots, "No vision models needed". Opt-in capability groups add more tools, and the `vision` group adds `browser_mouse_click_xy`, `browser_mouse_move_xy`, `browser_mouse_drag_xy`, `browser_mouse_down`, `browser_mouse_up` and `browser_mouse_wheel`. The core group has `browser_press_key` and `browser_take_screenshot`; the screenshot description says that with the vision capability the coordinates of a screenshot can be used with the mouse tools. There is no coordinate-based keyboard tool, which a canvas game does not need. The page states that the server is not a security boundary. It exposes a `createConnection` function for custom transports, a `--viewport-size` flag and a Docker image that runs headless Chromium only.

Sources: [repository](https://github.com/microsoft/playwright-mcp), [README](https://raw.githubusercontent.com/microsoft/playwright-mcp/main/README.md), [releases](https://github.com/microsoft/playwright-mcp/releases/latest).

### Stagehand

"The SDK to extract data and interact with any site on the web", in TypeScript, Python and Go. Its natural-language methods `act`, `observe` and `extract` need a model. Its Page reference documents direct methods with CSS-pixel coordinates: `click(x, y)`, `hover(x, y)`, `scroll`, `dragAndDrop`, plus `type`, `keyPress`, `screenshot` and `snapshot`. The Page reference does not say whether those methods need a model key. A separate MCP server for Browserbase is archived on its page, uses `act`, `observe` and `extract`, and needs a model; it is not a candidate.

Sources: [repository](https://github.com/browserbase/stagehand), [releases](https://github.com/browserbase/stagehand/releases), [Page reference](https://docs.stagehand.dev/v3/references/page), [Browserbase MCP server](https://github.com/browserbase/mcp-server-browserbase).

### Skyvern

"Automate Browser-based workflows using LLMs and Computer Vision." It needs a model provider, configured in `.env`, and is licensed AGPL-3.0, which constrains embedding. It extends Playwright with `page.act()`, `page.extract()` and similar calls. Nothing read describes raw coordinates or raw key presses. It targets workflow automation by a model of its own and is the weakest fit for a caller that supplies the model.

Sources: [repository](https://github.com/Skyvern-AI/skyvern), [releases](https://github.com/Skyvern-AI/skyvern/releases/latest).

### Playwright (Python)

"A Python library to automate Chromium, Firefox and WebKit browsers with a single API", sync and async. The API pages confirm the pieces a canvas needs: `page.mouse.click(x, y)` with coordinates "relative to the main frame's viewport in CSS pixels", `page.keyboard.press` for named keys such as `ArrowLeft` and `Enter`, and `page.screenshot`. It has no model and no loop, so the caller decides each step. It is the library under Playwright MCP.

Sources: [repository](https://github.com/microsoft/playwright-python), [releases](https://github.com/microsoft/playwright-python/releases/latest), [Mouse](https://playwright.dev/python/docs/api/class-mouse), [Keyboard](https://playwright.dev/python/docs/api/class-keyboard).

### Chrome DevTools MCP

A server that lets "your coding agent ... control and inspect a live Chrome browser", launched with `npx chrome-devtools-mcp@latest`, with a CLI as well. Its tool reference lists `click` by element `uid`, `press_key` with combinations such as `Control+Shift+R`, `take_screenshot` with a format option, and `click_at` taking `x` and `y`. `click_at` requires the `--experimentalVision=true` flag. The page says usage statistics are on by default with an opt-out, and warns that browser content is exposed to MCP clients. It encourages building browser subagents on top of it.

Sources: [repository](https://github.com/ChromeDevTools/chrome-devtools-mcp), [releases](https://github.com/ChromeDevTools/chrome-devtools-mcp/releases/latest), [tool reference](https://github.com/ChromeDevTools/chrome-devtools-mcp/blob/main/docs/tool-reference.md).

### agent-browser

Found by search. "Browser automation for AI agents: open pages, read them as an accessibility tree, and act on elements from the shell." One command at a time against a background daemon over CDP, with an MCP server over stdio. The commands `screenshot`, `keyboard`, `mouse`, `press`, `click` and `drag` are listed without detail, so whether it clicks at coordinates is not confirmed. A search listing named Apache-2.0 for a Homebrew formula, but that page was not fetched and the repository page did not state a licence, so the licence cell stays "not confirmed".

Sources: [repository](https://github.com/vercel-labs/agent-browser), [releases](https://github.com/vercel-labs/agent-browser/releases/latest).

### Anthropic computer use, as a protocol shape

A client toolset, `computer_toolset_20260801`, whose member tools the caller's code executes. Each member is a tool call: `screenshot`, `zoom`, `left_click` with `coordinate: [x, y]`, `mouse_move`, `left_mouse_down`, `left_mouse_up`, `scroll`, `type`, `key` with text such as `"Return"`, `hold_key`, `wait`. A screenshot comes back as an image content block in the tool result. Coordinates are in the pixel space of the screenshots the caller returns, with no display-size parameter, and the page recommends 1280x720 or 1280x800 for web apps. Several calls can arrive in one turn and run in order.

Source: [computer use tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool).

### OpenAI computer tool, as a protocol shape

`{ type: "computer" }` in a Responses request. A `computer_call` carries an ordered `actions` array of `click`, `double_click`, `drag`, `move`, `scroll`, `keypress`, `type`, `wait` and `screenshot`. The caller runs them and returns a `computer_call_output` whose output is a `computer_screenshot` with a base64 PNG data URL. The page also describes exposing the caller's own browser functions as ordinary function tools, and says the computer tool remains supported. Its SDK example wraps a Playwright page in a driver class.

Source: [computer use guide](https://developers.openai.com/api/docs/guides/tools-computer-use.md).

### The two vendor shapes side by side

Both interfaces have the same four parts: the model names an action with coordinates or keys, the caller performs it, the caller returns a screenshot, and the loop repeats. Neither is a driver. Each defines what a model emits and what the caller feeds back, and each leaves the browser to the caller. For a vault, they say what a hands page would contain for a vision model (an action, a coordinate, a key) and what a screen would have to carry (a PNG).

### The protocol under the MCP servers

Four of the candidates are reached as MCP servers: Playwright MCP, Chrome DevTools MCP, agent-browser and browser-use. The MCP specification defines two standard transports: stdio, where "the client launches the MCP server as a subprocess" and exchanges newline-delimited JSON-RPC over stdin and stdout, and Streamable HTTP. A tool result is a list of content items, and an image item has `type: "image"`, base64 `data` and a `mimeType`. A client calls `tools/list` to discover tools and `tools/call` to use one. The specification says there should always be a human in the loop with the ability to deny tool calls. The existing [protocols research](protocols.md) covers MCP as one of its families.

Sources: [MCP tools](https://modelcontextprotocol.io/specification/2025-11-25/server/tools), [MCP transports](https://modelcontextprotocol.io/specification/2025-11-25/basic/transports).

## What this suggests for a web connector

Conky's rules that bear on the choice: a connector sits beside the vault, holds no state and writes through the same rules as anyone; the core gains only general primitives; build nothing before something consumes it. The demo is the first consumer.

### The two shapes

**(a) `conky connect browser`, embedding one driver library.** The nearest fit is Playwright (Python): it is the one candidate here that is a Python library, with no model and no Node process. It confirms `mouse.click(x, y)`, `keyboard.press` and `screenshot`. The connector would mirror the terminal connector: write a screen page, read a hands page, type keys. The cost is that the connector is bespoke. It carries a browser, a Chromium download, and a vocabulary of browser actions that conky must name and maintain, and it reaches nothing else.

**(b) `conky connect mcp -- <server command>`, a general MCP client.** The connector starts the server as a subprocess over stdio and sends `tools/list`. Following [the idea of tools as pages](../ideas/tools.md), it writes one page per tool into a space, so that an agent discovers what it can do by reading that shelf. A call is a write to a tool's page, and the connector performs it and writes the result back with the request as its cause. A browser MCP server is the first shelf. Playwright MCP, with `--caps=vision` and `--headless`, or Chrome DevTools MCP, with `--experimentalVision=true`, covers screenshots, raw keys and clicks at coordinates. The same connector then reaches everything else that has an MCP server. The cost is a Node runtime beside Python for the browser servers, an MCP client dependency in Python (whether to use an official SDK or write the small stdio client was not researched), and a design question the terminal connector never had: a request names a tool and arguments instead of text to type.

### What the evidence favours

The evidence favours (b), and it does not contradict the owner's direction that tools be discoverable by any agent as a general pattern. The browser is the first shelf of tools reached that way, not a special connector. Four of the drivers surveyed that fit a caller-supplied model are reached through MCP, so the first use needs no new driver code and a second shelf costs no new connector. The tool names live in the server, not in the repository. The MCP specification gives both halves the pattern needs, `tools/list` to discover and `tools/call` to act, and the OpenAI and Claude agent SDKs both discover MCP tools through those calls ([tools](../ideas/tools.md) has the references). Option (a) is cheaper to get working for this one demo, because the Playwright calls are direct and need no tool-naming scheme, but it builds a second connector shape for the next protocol to repeat.

The caution is the build-nothing-before-use rule. A general MCP connector is a bigger surface than the demo consumes. The first version should be held to what the demo uses: start one server, write its tool pages, perform named calls, write results. Subscriptions to list changes and the rest of the protocol wait for a consumer.

### What remains unknown

- Whether a browser MCP server can drive this emulator at all. Nothing was run. Whether the page needs focus or a click to capture the keyboard, and whether the game sits behind an advertisement or a start gate, is not confirmed.
- Whether Playwright MCP returns a screenshot inline as an MCP image item or only saves a file and returns its path. Its description says a file is saved by default. Chrome DevTools MCP takes a `filePath`, so the same question applies.
- Whether the experimental vision flag on Chrome DevTools MCP is stable enough to depend on. The flag name says experimental.
- Whether browser-use or agent-browser can send raw clicks and keys. The pages read did not say.
- Which tools the first connector should allow. Both browser servers expose far more than a game needs, and Playwright MCP says it is not a security boundary. A rule on the hands page can limit which tool names a write may carry, since the connector writes through the same rules as anyone, but no such rule exists yet.
- Latency. A browser step through a subprocess and a settle wait is slower than a pseudo-terminal. A game that punishes slow input is a different test from a turn-based one.

## The open problem, either way

A screenshot is an image. A page is Markdown with frontmatter, and the vault's authority is its Git history. Model pages today send text only: a prompt may embed a field of a page, and the [terminal guide](../guide/playing-a-program.md) already notes that it cannot even embed the body of the screen page. The provider documents read for conky mention no image input. So a party cannot yet see a canvas game, whichever shape is chosen. Both vendor shapes above return the screenshot to the model as the result of an action. Conky has no equivalent.

What would have to exist:

1. **A place for the image.** Large data does not belong in a page. [Decision 0003](../decisions/0003-data-beside-pages.md) says large or external data is referenced by a pointer carrying a content hash, and is not built. A screen page could carry a field such as an image path and hash, with the bytes in a file beside the vault. The open choice is whether the bytes enter Git history or sit outside it. In the history they make the vault grow with every frame and fail the clone-quickly aim. Outside it, a replay shows that a screenshot was taken and its hash, but not what the party saw, and a vault that travels alone would not carry the pictures.
2. **A way for the connector to write it.** The write of the screen page must carry the pointer as ordinary fields, so rules apply to it. A rule could limit how often a new image may be recorded, which bears on the open question of streaming fast-changing data in [connectors](../ideas/connectors.md).
3. **A way for a model page to send it.** A prompt would need an embed that reads an image pointer and passes the bytes to the provider as an image. That needs a provider page that declares it accepts images, a request body that carries them, and a refusal that says what to do when a page asks a text-only provider for an image.
4. **A way to keep it affordable.** Images cost tokens at each step. A cap on size and on how many are kept, held as a rule and not as a request to the model, would match the project's own rule that constraints are evaluated by the runtime.
5. **A text fallback.** Playwright MCP and Chrome DevTools MCP also return accessibility snapshots. A canvas has none worth reading, but a game page's menus, scores and dialogs outside the canvas might be. That path needs no image support and can ship first.

None of this is built. Without items 1 and 3, the demo can show the connector working, with a reflex page or a human writing the hands page, but not characters that look at the game.

## Sources

All fetched 2026-11-20.

- https://github.com/browser-use/browser-use
- https://github.com/browser-use/browser-use/releases/latest
- https://docs.browser-use.com
- https://docs.browser-use.com/open-source/introduction
- https://docs.browser-use.com/open-source/cli
- https://github.com/microsoft/playwright-mcp
- https://raw.githubusercontent.com/microsoft/playwright-mcp/main/README.md
- https://github.com/microsoft/playwright-mcp/releases/latest
- https://github.com/browserbase/stagehand
- https://github.com/browserbase/stagehand/releases
- https://docs.stagehand.dev/v3/references/page
- https://github.com/browserbase/mcp-server-browserbase
- https://github.com/Skyvern-AI/skyvern
- https://github.com/Skyvern-AI/skyvern/releases/latest
- https://github.com/microsoft/playwright-python
- https://github.com/microsoft/playwright-python/releases/latest
- https://playwright.dev/python/docs/api/class-mouse
- https://playwright.dev/python/docs/api/class-keyboard
- https://github.com/ChromeDevTools/chrome-devtools-mcp
- https://github.com/ChromeDevTools/chrome-devtools-mcp/releases/latest
- https://github.com/ChromeDevTools/chrome-devtools-mcp/blob/main/docs/tool-reference.md
- https://github.com/vercel-labs/agent-browser
- https://github.com/vercel-labs/agent-browser/releases/latest
- https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool
- https://developers.openai.com/api/docs/guides/tools-computer-use.md
- https://modelcontextprotocol.io/specification/2025-11-25/server/tools
- https://modelcontextprotocol.io/specification/2025-11-25/basic/transports
- https://oregontrail.ws/games/the-oregon-trail-deluxe/play
