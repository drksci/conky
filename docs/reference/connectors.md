---
kind: reference
title: Connectors
status: current
date: 2026-11-20
source: maintainers
---

# Connectors

This page specifies the terminal connector, the only connector built. A connector is a process that runs beside a vault, holds no state, signs its writes with its own key and obeys the same rules as any other actor. Stop it and start another and nothing is lost, because everything it did is in the vault's history. The idea is in [connectors](../ideas/connectors.md).

## The terminal connector

```
conky connect terminal [--vault V] [--keys K] [--as NAME] [--screen PAGE] [--hands PAGE]
                       [--settle SECONDS] [--max-steps N] [--first-line] -- COMMAND [ARGS...]
```

The options are in the [command line reference](cli.md#connect-terminal). The connector starts the command in a pseudo-terminal. It gives the vault eyes by writing what the program shows to the screen page, and hands by typing what the hands page says. Any page can then play the program: a reflex, a person writing by hand, or a page that [asks a model](rules-and-reactions.md#asking-a-model). [Playing a program](../guide/playing-a-program.md) runs one for real.

### The screen page

Default name `screen`. The connector creates it if it does not exist, with a short body that says what it is and the field `turn` set to 0.

| Part | Meaning |
|---|---|
| Body | The text on the screen: the last 60 lines of the program's output, with terminal control sequences removed. |
| `turn` | The number of screens written, counting from 1. |
| `ended` | Empty until the run ends, then a short reason. |

A screen is written when the program's output has been quiet for the settle time (`--settle`, default 0.3 seconds). It is an ordinary signed write by the connector's actor (default `terminal`), so rules apply and it appears in the history. A screen whose text equals the previous one is not written again.

The run ends when the program exits, after `--max-steps` screens (default 200) or on interrupt. The connector then writes `ended` with the reason: `the program exited with status N`, `stopped after N screens` or `interrupted`. The exit code is 0 for each.

### The hands page

Default name `hands`. The connector creates it if it does not exist. It reads these fields:

| Field | Meaning |
|---|---|
| `keys` | Text to send to the program. It must be text, so quote a number: `keys='"1"'` on the command line. |
| `turn` | The number of the screen the keys answer. |
| `enter` | When `false`, no newline follows the keys. Any other value, or no field, sends one. |

The connector sends the keys when the hands page changes, `keys` holds text, and `turn` equals the number of the current screen. A hands write for an old turn is ignored, and so is a second write for a turn already answered. With `--first-line` the connector types only the first non-empty line of `keys`, so a page may write its reasoning after its reply and the program still reads one line. The whole text stays in the page; keys with no non-empty line are not sent. After sending, the connector waits for the next screen.

A page plays the program by reading `screen` and writing `hands` with the turn it is answering. A reaction on the hands page that watches `screen` does this with `turn: other.turn`. A rule refuses a hands write like any other and the refusal is recorded, so the program never receives refused keys: a rule on the hands page, or on its space, limits what can be typed.

The connector finds hands writes by polling the vault's history about twenty times a second. Reactions to a screen write run inside that write, so a hands write made by a reaction is seen as soon as the screen write returns.

### Output

One line for each screen written, one for each set of keys sent and one for the end of the run. Output is plain when piped and styled in a terminal ([colour and styled output](cli.md#colour-and-styled-output)).

## Limits

- POSIX only. The program runs in a pseudo-terminal, which Windows does not offer, and there the command stops with an error that says so.
- Text only. Colour, cursor movement and other control sequences are removed, so a program that draws by moving the cursor shows as the text it leaves behind.
- Polling. A hands write is noticed within a fraction of a second, not at once.
- The screen is the tail of the output, not a model of a terminal window.
- The program gets the terminal on its standard streams but not as its controlling terminal, so a program that opens `/dev/tty` directly may not work.
- One program and one pair of pages per run. To play two programs, run two connectors with different `--screen`, `--hands` and `--as`.
- A rule that refuses writes to the `--screen` page stops the run from recording screens. The refusal is recorded and printed.

## Showing a vault elsewhere

```
conky export obsidian [--out FOLDER]
conky export notion [--out FOLDER]
```

An export writes the vault's present state as a folder another program can open. It is derived data: the notes come only from the pages committed at the latest commit, so a stray edit to `pages/` never reaches them, and nothing is written back. The same vault gives the same bytes. Each run deletes and rewrites its own folder, and refuses a `--out` that is the vault, holds it, or is a folder not made by an earlier export. The default folder is `dist/<form>/` inside the vault. The command adds `dist/` to the vault's `.git/info/exclude`, not to a tracked file, so the history is untouched and `conky verify` still passes. Delete the folder at any time.

### Obsidian

| File | Content |
|---|---|
| `NAME.md` | One note a page: the page as committed, so its frontmatter is the note's properties and its `[[links]]` and `![[embeds]]` are Obsidian's own marks. |
| `SPACE/` | A folder for each space. A page within a space sits in that space's folder, a space within a space in a folder inside it, and the space's own note sits at the top of its folder as `SPACE/SPACE.md`. |
| `spaces.canvas` | The overview to open first: only the spaces, as groups nested as they are within each other, each labelled with its name and the number of pages in it. |
| `conky.canvas` | The full canvas laying out every page, with the relations as edges. |
| `who.md` | Who signed what, generated from the history. |

A note is the page exactly as its author wrote it: nothing is added to its body or its frontmatter. What is within a space is shown by its folder and by the canvases. A page named `who` would share its note's name with `who.md`, so the export would overwrite it: give such a page another name.

For a vault with `kitchen`, `cellar` within `kitchen`, `wine` within `cellar`, `cook` within `kitchen`, a provider `model` and a loose `note`, the tree is:

```
conky.canvas
kitchen/cellar/cellar.md
kitchen/cellar/wine.md
kitchen/cook.md
kitchen/kitchen.md
model.md
note.md
spaces.canvas
who.md
```

Both canvases follow the [JSON Canvas specification](https://jsoncanvas.org/spec/1.0/), version 1.0, read on 2026-11-20. They write the fields that specification lists as required for each node (`id`, `type`, `x`, `y`, `width`, `height`, and `file` for a file node) and for each edge (`id`, `fromNode`, `toNode`), plus the optional `label`. In `conky.canvas` each page is a file node pointing at its note, each space is a group node labelled with its name and drawn around the nodes of the pages within it, and each relation is an edge labelled `within`, `watch`, `ask` or `writes`, between pages that exist. In `spaces.canvas` each space is a group labelled `NAME: N pages`, where N counts every page within the space, directly or through an inner space, and not the space's own page; inner spaces are drawn inside it and there are no edges. Pages outside any space are not shown there. No Obsidian application settings are written.

### Who signed what

`who.md` is a plain Markdown table with a comment at the top that says it is generated from the history. It has one row a page, in name order:

| Column | Content |
|---|---|
| page | A link to the page, `[[name]]`. |
| signed by | The actor of the page's last change. |
| when | The date of that commit as recorded, in UTC. |
| kind | The `Kind` trailer of that commit. |
| cause | The first seven characters of its `Cause` trailer, or `-`. |
| changes | How many commits changed the page. Refusals are not counted. |

It is read from the commits whose `Page` trailer names the page, so the notes carry no attribution of their own. `who.md` is written in both forms.

### Notion

`conky export notion` writes the same tree of notes, without the canvases, to `dist/notion/`, with `who.md` beside them and the whole tree again as `conky.zip`. Each note's frontmatter is moved to a fenced `yaml` block at the top, because Notion's page does not say what it does with frontmatter. Links and embeds stay as written.

Notion's page `https://www.notion.com/help/import-data-into-notion`, read on 2026-11-20, documents importing Markdown files, one at a time or several, and importing a zip of them: "If you want to preserve folder structure, zip a folder and import the ZIP." It warns that anchor links and nonstandard Markdown extensions may not import cleanly, so `[[links]]` and `![[embeds]]` are likely to stay as plain text. It also warns that hidden folders and files can make a zip fail, which is why the zip holds one folder, `conky/`, and nothing hidden. The same page gives size limits and a rate limit for file imports, which are Notion's to change.

To import, open Notion's import dialog, choose Markdown, and select `dist/notion/conky.zip`. For a single note, choose that note's `.md` file instead. The result was not tried in Notion: that the folders become nested pages is Notion's documented behavior for a zipped folder, not something this repository has seen.

### AFFiNE

AFFiNE is not supported because no file import was confirmed: the documentation index `https://docs.affine.pro/` and the repository's docs folder `https://github.com/toeverything/AFFiNE/tree/canary/docs` name none, and `https://docs.affine.pro/import` could not be fetched (the server answered 402), all on 2026-11-20.
