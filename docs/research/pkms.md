---
kind: research
title: "Personal and team knowledge tools compared on how they hold, link, serve and stream pages"
status: current
date: 2026-11-22
source: "each tool's own documentation or repository page, and the CommonMark, GFM, YAML, JSON Canvas and MCP pages, fetched 2026-11-22; conky's own page form from this repository"
---

# Personal and team knowledge tools compared on how they hold, link, serve and stream pages

A page in a conky vault is a Markdown file with YAML frontmatter, `[[links]]` and `![[embeds]]`. This digest compares that form with the leading knowledge tools on one fixed rubric, so that the form is judged against what the field does and not against what one reader happened to know.

## How to read this

Every fact about an outside tool comes from a page fetched on 2026-11-22. The pages were read through a fetch tool that returns a condensed reading of each page, so wording is paraphrased. Where a page did not say, the cell reads "not stated" and the item is listed in [Not confirmed](#not-confirmed). Nothing comes from memory. The fetch tool gave no release date for most repositories, so versions are given only where a page showed one.

The rubric was fixed before reading:

1. Storage: plain files or a database, the format, and whether pages survive outside the tool.
2. Identity and address: page name, path, id, block id, and rename behaviour.
3. Links: wikilinks, backlinks, aliases, embeds, block references, unlinked mentions.
4. Structure: typed properties, schemas, templates, tags, folders.
5. Views and queries: query language, saved views, canvas or graph.
6. History: versioning, Git use, who changed what, signing.
7. Agent access: API, MCP server, CLI, and the auth model.
8. UI and live update: how a client hears of a change.
9. Collaboration and concurrency.
10. Self-documentation: whether the tool documents its own types, templates or plugins as pages.
11. Openness: licence, open specification, export.

## Summary table

Columns are the rubric items that separated the tools. A cell reads "not stated" where the page read did not say.

| Tool | Storage | Links and identity | Structure and views | History | Agent access | Live update | Licence |
|---|---|---|---|---|---|---|---|
| [Obsidian](https://obsidian.md/help/links) | Markdown files in a folder | `[[Note]]` default, Markdown links optional; `[[Note#^id]]` block links; aliases; links rewritten on rename by default | YAML properties with 7 types fixed per name across the vault; Bases views (`.base`) as table, list, cards, kanban, map | Not in the core pages read; Obsidian Git plugin | Local REST API plugin: HTTPS, bearer key, built-in MCP server | Local REST API streams vault events as SSE | Not stated on the help pages; plugins read are MIT |
| [Logseq](https://github.com/logseq/logseq) | Markdown or Org files; DB graphs in beta use SQLite | Not read | Not read | Not read | Plugin API | RTC for DB graphs, alpha | AGPL-3.0 |
| [SilverBullet](https://silverbullet.md/) | Plain Markdown files in a folder | `[[links]]`, linked mentions | Space Lua queries over tags and frontmatter | Git mentioned for a docs folder | HTTP file API, `sb` CLI, an `mcp` directory | "show up as they happen"; mechanism not stated | MIT (server) |
| [Foam](http://docs.foam.md/) | Standard Markdown files, in VS Code | `[[note]]`, `[[note#^id]]`, `![[note]]`, backlinks | Tags, templates, graph | Git-based | Not stated | Not stated | Not stated |
| [Dendron](https://wiki.dendron.so/) | Plain text in a Git-backed folder | Not stated | Schemas, templates | Git blame | Not stated | Not stated | AGPL-3.0 |
| [TiddlyWiki](https://tiddlywiki.com/) v5.4.1 | One HTML file, or a Node.js folder of tiddler files | Transclusion keeps a single copy | Not read | Not read | HTTP or JavaScript APIs | Not stated | Not stated |
| [Notion](https://developers.notion.com/reference/intro) | Hosted database; Markdown read and write through the API | Page ids; links not read | Databases; not read in detail | Not read | REST API with bearer tokens; MCP server | Webhooks over HTTPS POST, ids only | Not stated |
| [Confluence](https://developer.atlassian.com/cloud/confluence/rest/v2/intro/) | Hosted | Page ids | Not read | Page version endpoints | REST v2: JWT or OAuth 2.0, basic auth | Not read | Not stated |
| [AFFiNE](https://github.com/toeverything/AFFiNE) | Not stated | Not read | Docs, whiteboard, tables | Not read | Neither API nor MCP mentioned | Yjs CRDT sync | MIT (Community) |
| [Anytype](https://github.com/anyproto/any-sync) | Encrypted DAGs per space | Objects | Not read | Every change signed | API v2 pre-release | any-sync CRDT sync | MIT |
| [Tana](https://outliner.tana.inc/learn/features/intro-to-tana) | Not read | Not read | Not read | Not read | Not read | Not read | Not read |
| [Quartz](https://quartz.jzhao.xyz/) v5.2.0 | Markdown in `content/` | Wikilinks, transclusions, backlinks plugin | Graph view, search | Not applicable | Not applicable | Incremental rebuild on a dev server | Not stated |

## Obsidian

Read at obsidian.md/help on 2026-11-22. The help pages carry no version or date, and one says deprecated properties were dropped in Obsidian 1.9.

**Storage.** Notes are Markdown files. Properties are YAML at the top of the file, and JSON input is converted and saved as YAML. Obsidian Flavored Markdown combines CommonMark, GitHub Flavored Markdown and LaTeX and adds wikilinks, `![[embeds]]`, `^id` block ids, `%%comments%%`, callouts and `==highlights==` ([syntax page](https://obsidian.md/help/obsidian-flavored-markdown)).

**Address and links.** The default link is `[[Three laws of motion]]`, with folder paths from the vault root (`[[Projects/Three laws of motion]]`) and display text after a pipe. A link to a missing note creates it. Headings are addressed as `[[Note#Heading]]`. A block is addressed as `[[Note#^blockid]]`, with ids of letters, digits and dashes written at the end of a paragraph or on their own line after a list, quote or table. The page says block references are Obsidian-specific. An alias is a reusable alternate name for a note. Renaming a file updates internal links automatically unless the setting is changed. The page read does not discuss backlinks or unlinked mentions ([links page](https://obsidian.md/help/links)).

**Structure and views.** Properties have seven types: text, list, number, checkbox, date, date and time, tags. Once a name has a type, every property of that name in the vault has it ([properties page](https://obsidian.md/help/properties)). Bases is a core plugin giving database-like views over files and properties, saved as a `.base` file or embedded in a code block, with table, list, cards, kanban and map layouts. The formula language was not described on the page read ([bases page](https://obsidian.md/help/bases)).

**Canvas.** JSON Canvas spec 1.0, dated 2024-03-11, has node types `text`, `file`, `link` and `group`, and edges with required `id`, `fromNode` and `toNode`. The page names no licence and no maintainer, though it links to a repository under `obsidianmd` ([spec](https://jsoncanvas.org/spec/1.0/)).

**Agent access.** The Local REST API plugin, MIT licensed, offers create, read, update and delete on vault files, PATCH edits aimed at a heading, block reference or frontmatter key, simple full-text search, JsonLogic queries on note metadata, and commands. It uses an API key as a bearer token over HTTPS on port 27124, with its own certificate authority limited to local hosts. It also runs a built-in MCP server at `/mcp/` with 20 tools on Streamable HTTP, supporting revision `2026-07-28` and revisions from `2024-10-07` to `2025-11-25`. The page lists no release version ([repository](https://github.com/coddingtonbear/obsidian-local-rest-api)).

**Live update.** The same plugin states that it streams vault events as Server-Sent Events. The event names and payload were not read.

**History.** The Obsidian Git plugin, MIT licensed, commits, pulls and pushes on a schedule, with a history view, a diff view and conflict resolution in the editor. The page does not state the commit author and does not mention signing. On mobile it runs on isomorphic-git and is described as highly unstable ([repository](https://github.com/Vinzent03/obsidian-git)).

## Logseq

Read from the GitHub README on 2026-11-22. The documentation site returned a page over 10 MB that the fetch tool refused, so block references, queries and the file format were not read from Logseq's own documentation.

The README describes a privacy-first open-source platform with Markdown and Org-mode support, a Plugin API, and DB graphs. The DB version is in beta, the new mobile app and real-time collaboration (RTC) are in alpha, and the README warns that data loss is possible and recommends SQLite backups. The licence is AGPL-3.0 ([repository](https://github.com/logseq/logseq)).

## SilverBullet

Read at silverbullet.md and its repository on 2026-11-22. No version was shown.

Notes are "a folder with markdown files". Links use double brackets, and pages show backlinks as Linked Mentions. Space Lua builds queries from tagged or frontmatter data and adds commands, widgets and templates. The repository describes a Rust server that serves a TypeScript client built on CodeMirror 6, the file and space HTTP API, and an `sb` CLI; it lists an `mcp` directory that the page does not describe. The server is MIT licensed. The page says the tool supports single-user and multi-player editing but does not explain how edits merge or conflict ([site](https://silverbullet.md/), [repository](https://github.com/silverbulletmd/silverbullet)).

## Foam

Read at docs.foam.md on 2026-11-22. No version or date shown.

Notes are standard Markdown files edited in VS Code. Links are `[[note]]`, block anchors `[[note#^id]]` and embeds `![[note]]`, with automatic backlinks, tags, templates and a graph view. It is described as Git-based, with a separate guide on syncing through source control. The licence is called free and open source without naming one ([site](http://docs.foam.md/)).

## Dendron

Read at wiki.dendron.so on 2026-11-22.

Notes are plain text in a Git-backed folder, and `git blame` shows who edited what. Schemas keep a knowledge base consistent, give autocomplete hints and apply templates on creation. Notes can be renamed or restructured without breaking links, including by regex. The page does not say whether the project is maintained, names no version, and does not mention ids in frontmatter. The licence is AGPL-3.0 and the site repository is MIT ([site](https://wiki.dendron.so/)).

## TiddlyWiki

Read at tiddlywiki.com on 2026-11-22. The version shown in the header is v5.4.1.

The main page loaded as a script and returned only the version. The Node.js page says individual tiddlers are stored in separate files and that the running server cannot have those files edited directly: the server must be restarted for file changes to take effect. The recommended way to interact with a running wiki is the HTTP or JavaScript APIs. Transclusion is defined as keeping a single copy of content with an instruction marking where it appears. The Philosophy of Tiddlers page says to split information into the smallest semantically meaningful units. Link syntax, fields, filters, change notification and plugins as tiddlers were not read ([Node.js](https://tiddlywiki.com/static/TiddlyWiki%2520on%2520Node.js.html), [Transclusion](https://tiddlywiki.com/static/Transclusion.html), [Philosophy](https://tiddlywiki.com/static/Philosophy%2520of%2520Tiddlers.html)).

## Notion

Read at developers.notion.com on 2026-11-22. The pages carry no date. The newest `Notion-Version` named is 2026-03-11, and the versioning page leaves the "latest" value as an unfilled placeholder.

**Access.** The API is JSON over HTTPS with a bearer token and a `Notion-Version` header. Pagination is by cursor. The markdown guide describes `POST /v1/pages` with a `markdown` body, `GET /v1/pages/:page_id/markdown` and `PATCH /v1/pages/:page_id/markdown` with commands such as `update_content`, which needs each `old_str` to match exactly once. A `markdown_version` of `v2` (Notion-flavored Markdown) is recommended and `v1` is deprecated. A write of more than 5,000 blocks is refused, and a read stops at about 20,000 records with `truncated: true` ([API intro](https://developers.notion.com/reference/intro), [versioning](https://developers.notion.com/reference/versioning), [markdown](https://developers.notion.com/guides/data-apis/working-with-markdown-content)).

**MCP.** The Notion MCP server lets assistants search a workspace, create and edit pages and manage databases. Its URL, transport, auth and tool list were not on the page read ([guide](https://developers.notion.com/guides/mcp/mcp)).

**Live update.** Webhooks are HTTP POSTs to a public SSL endpoint, signed with an HMAC-SHA256 in `X-Notion-Signature`. Events such as `page.content_updated` carry ids and metadata, not content, and are batched so that they may arrive a minute or two late ([webhooks](https://developers.notion.com/reference/webhooks)).

## Confluence

Read at developer.atlassian.com on 2026-11-22. Only the REST v2 overview and the version operations list were readable; the page shows a 2026 copyright and no version.

The v2 API is for Cloud. Apps authenticate with JWT or OAuth 2.0, direct calls may use basic auth, and pagination is by cursor with a `Link` header. Page versions have `GET /pages/{id}/versions` and `GET /pages/{page-id}/versions/{version-number}`. The version object's fields, the body representations and the update rules were not read ([overview](https://developer.atlassian.com/cloud/confluence/rest/v2/intro/), [versions](https://developer.atlassian.com/cloud/confluence/rest/v2/api-group-version/)).

## AFFiNE

Read from the GitHub page on 2026-11-22. No version or date shown.

AFFiNE is an open-source workspace combining docs, whiteboard and tables, and says users own their data on disk. It names y-octo (a Yjs-compatible CRDT in native code), OctoBase (a Rust local-first database), Yjs and BlockSuite. The Community Edition is MIT licensed. Storage format, export, API and MCP were not stated ([repository](https://github.com/toeverything/AFFiNE)).

## Anytype

Read at the any-sync repository and developers.anytype.io on 2026-11-22.

any-sync is a protocol for synchronising encrypted "spaces". Data is held as encrypted directed acyclic graphs, changes are merged as CRDTs, and "every change in the DAGs is cryptographically signed" and verified by each device. Node types are sync, file, consensus (which validates ACL changes) and coordinator. The licence is MIT ([any-sync](https://github.com/anyproto/any-sync)). The developer page calls API v2 a pre-release whose latest listed update is 2025-11-08 (anytype-heart v0.50.7), and describes objects as editable JSON documents. The local REST API, auth and MCP were not on the page ([developers.anytype.io](https://developers.anytype.io/)).

## Tana

Not read. The intro page at outliner.tana.inc was fetched twice and returned an error the first time and an unusable result the second. Every Tana cell is NOT VERIFIED.

## Quartz

Read at quartz.jzhao.xyz on 2026-11-22. The footer shows Quartz v5.2.0.

Quartz is a static-site generator that turns Markdown in `content/` into a website. It lists Obsidian compatibility, wikilinks, transclusions, backlinks as a plugin, search and graph view. `npx quartz build --serve` serves on port 8080 with incremental rebuilds on content edits. It is a publisher: it reads files and holds no state of its own ([site](https://quartz.jzhao.xyz/)).

## Shared standards

| Standard | Version as read | What it defines | What it leaves out |
|---|---|---|---|
| [CommonMark](https://spec.commonmark.org/) | 0.31.2, 2024-01-28 (index page) | Markdown syntax | Frontmatter and wikilinks are not in the index page's version listing; the specification text was not read |
| [GitHub Flavored Markdown](https://github.github.com/gfm/) | 0.29-gfm, 2019-04-06 | A strict superset of CommonMark: tables, task lists, strikethrough, autolinks, disallowed raw HTML | Neither frontmatter nor wikilinks appears in its table of contents |
| [YAML](https://yaml.org/spec/1.2.2/) | 1.2.2, 2021-10-01 | Mapping, sequence and scalar forms; mapping keys must be unique | Which frontmatter fence a Markdown tool recognises; what the first 100,000 characters read did not say about booleans |
| Wikilink syntax | No specification found in this reading | Each tool above defines it for itself; Obsidian and Foam both write `[[note#^id]]` for a block | A shared grammar |
| [Obsidian Flavored Markdown](https://obsidian.md/help/obsidian-flavored-markdown) | Not stated | Wikilinks, embeds, block ids, comments, callouts, highlights | Block references are Obsidian-specific by its own account |
| [JSON Canvas](https://jsoncanvas.org/spec/1.0/) | 1.0, 2024-03-11 | Nodes and edges of a canvas | Licence and status not stated |
| [MCP](https://modelcontextprotocol.io/specification/latest) | Revision 2026-07-28 | JSON-RPC 2.0; resources, prompts and tools; optional extensions including Tasks and Skills over MCP | Page content format |

## Where conky stands

Stated against the rubric. Conky's page form is from `docs/reference/vault-format.md` and `src/conky/page.py`, read on 2026-11-22.

1. Storage. A page is a Markdown file with YAML frontmatter in a Git repository, parsed with YAML 1.2 booleans, so a vault opens in any editor. A name is 1 to 64 characters of lowercase letters, digits, `-` and `_`, and pages sit flat in `pages/` with no folders.
2. Identity and address. The page name is the identity. There is no block id and no rename that rewrites links; a rename is not described in the vault format.
3. Links. `[[name]]` links and `![[name]]` embeds exist. The link pattern accepts a `#` or `|` suffix after the name and links to the page. In an embed, `#` selects a field, `members` or `context`, and not a heading. A page may list phrases in `aka`, and text that uses a phrase counts as a link, which is a form of unlinked mention that the Obsidian help pages read did not describe. There are no block references and no display text rendering in the vault format.
4. Structure. Frontmatter fields are untyped YAML with three reserved keys. `within` makes a page part of a space. There are no declared property types, templates or tags.
5. Views and queries. A space's `members` embed lists its pages, with `shows` to cap and order them by an expression. There is no saved table, board or canvas view, and the Obsidian view idea is marked as an idea.
6. History. Every write is one Git commit, signed with the actor's key, with the actor as author, and a refused write is an empty commit. In the readings above, the only signed change history is any-sync's, which signs each change inside an encrypted DAG and not in Git.
7. Agent access. The vault format and the terminal connector are the interface. No MCP server or HTTP API for pages was read in this repository for this digest.
8. UI and live update. Not described in the vault format. Obsidian's Local REST API states an SSE stream of vault events, and Notion sends signed webhooks with ids only.
9. Collaboration and concurrency. Writes are commits to one history. Merge and conflict behaviour between clones was not read for this digest.
10. Self-documentation. `docs/reference/vocabulary.md` lists the runtime's names and a test checks it against the code. Whether pages describe their own kinds inside a vault was not read.
11. Openness. The vault format is specified in `docs/reference/vault-format.md` and held stable by a golden vault. The licence was not read for this digest.

## Forecasts

Each was written before reading, in the spec for this digest.

| Forecast | Result |
|---|---|
| Plain Markdown with YAML frontmatter, wikilinks and embeds is the common core of the file-based tools, and conky's page form matches it. 80% | Hit on the core. Obsidian, Foam, SilverBullet and Quartz read as Markdown files with wikilinks, and Obsidian and Quartz with embeds; conky writes `[[name]]`, `![[name]]` and YAML frontmatter. The match is narrower than stated: names are flat and lowercase, with no block ids or heading links. Logseq, Dendron and TiddlyWiki were not read far enough to count |
| None signs who changed a page and none keeps history in Git as the authority; Obsidian Git and Foam come nearest. 75% | Partly a miss. Anytype's any-sync states that every change is signed, though outside Git. Among Git users, Obsidian Git, Foam and Dendron use Git as storage, and no page read made it the authority or mentioned signing |
| Live update is file watching or a private sync protocol in all of them, and none streams changes in an open documented event format. 70% | Partly a miss. The Obsidian Local REST API states it streams vault events as Server-Sent Events, a documented standard framing; the event payload was not read. Notion uses signed webhooks. any-sync and Yjs are sync protocols |
| At least one rubric item shows a form conky lacks and a professional would expect; block references or a typed query view. 65% | Hit. Block references (`[[Note#^id]]`) appear in Obsidian and Foam, typed properties and saved views in Obsidian, and conky has neither |

## Not confirmed

- Tana was not read. Logseq's documentation was not read: its site exceeded the fetch tool's size limit.
- Logseq, Dendron, TiddlyWiki, Notion and Confluence were not read for links, structure or queries. TiddlyWiki's main page loaded as a script.
- No release version or date was shown for Obsidian, Foam, SilverBullet, Logseq, AFFiNE, any-sync or the two Obsidian plugins. Where the plugin pages showed an empty Releases list, that is all that was read.
- The Obsidian Local REST API's SSE event names and payload were not read. Whether Obsidian Git signs commits is not stated on its README, not stated to be absent.
- Which YAML frontmatter fence and which YAML version each tool's parser accepts was not read. For YAML 1.2.2 only the first 100,000 characters were read, which excluded the core schema section. The CommonMark and GFM specification texts were not read past their index and, for GFM, the first 100,000 characters.
- No specification for wikilink syntax was found, and the Obsidian help pages were not compared with the Foam documentation beyond the block-anchor form.
- Confluence body representations, the version object's fields and its update rules were not read. The Notion MCP server's URL, transport and authentication were not read.
- Whether any tool documents its own types, templates or plugins as pages (rubric item 10) was not settled. SilverBullet's documentation site was seen to have pages such as Frontmatter and Space Lua, and the page does not say whether they ship inside the app.
- Merge and conflict behaviour was not read for any tool, so rubric item 9 is open except for the CRDT systems named by their own pages.
- No live tool was run, and no model was called.

## Sources

- [Obsidian: links](https://obsidian.md/help/links), [properties](https://obsidian.md/help/properties), [Bases](https://obsidian.md/help/bases) and [Obsidian Flavored Markdown](https://obsidian.md/help/obsidian-flavored-markdown)
- [JSON Canvas 1.0](https://jsoncanvas.org/spec/1.0/)
- [Obsidian Local REST API](https://github.com/coddingtonbear/obsidian-local-rest-api) and [Obsidian Git](https://github.com/Vinzent03/obsidian-git)
- [Logseq repository](https://github.com/logseq/logseq)
- [SilverBullet](https://silverbullet.md/) and its [repository](https://github.com/silverbulletmd/silverbullet)
- [Foam](http://docs.foam.md/)
- [Dendron](https://wiki.dendron.so/)
- [TiddlyWiki](https://tiddlywiki.com/)
- [Notion API](https://developers.notion.com/reference/intro), [versioning](https://developers.notion.com/reference/versioning), [markdown guide](https://developers.notion.com/guides/data-apis/working-with-markdown-content), [webhooks](https://developers.notion.com/reference/webhooks) and [MCP guide](https://developers.notion.com/guides/mcp/mcp)
- [Confluence Cloud REST API v2](https://developer.atlassian.com/cloud/confluence/rest/v2/intro/)
- [AFFiNE](https://github.com/toeverything/AFFiNE)
- [any-sync](https://github.com/anyproto/any-sync) and [Anytype developers](https://developers.anytype.io/)
- [Quartz](https://quartz.jzhao.xyz/)
- [CommonMark](https://spec.commonmark.org/), [GFM](https://github.github.com/gfm/), [YAML 1.2.2](https://yaml.org/spec/1.2.2/) and [MCP](https://modelcontextprotocol.io/specification/latest)
- Conky: [vault format](../reference/vault-format.md), [vocabulary](../reference/vocabulary.md) and [Obsidian view](../ideas/obsidian-view.md)
