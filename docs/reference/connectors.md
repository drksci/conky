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
conky export affine [--out FOLDER]
```

An export writes the vault's present state as a folder another program can open. It is derived data: it reads only the pages committed at the latest commit, so a stray edit to `pages/` never reaches it, and it writes nothing back. The same vault gives the same bytes. Each run deletes and rewrites its own folder, and refuses a `--out` that is the vault, holds it, or is a folder not made by an earlier export. The default folder is `dist/obsidian/` inside the vault. The command adds `dist/` to the vault's `.git/info/exclude`, not to a tracked file, so the history is untouched and `conky verify` still passes. Delete the folder at any time.

### Obsidian

| File | Content |
|---|---|
| `NAME.md` | One note a page: the page as committed, so its frontmatter is the note's properties and its `[[links]]` and `![[embeds]]` are Obsidian's own marks. |
| `SPACE/` | A folder for each space. A page within a space sits in that space's folder, a space within a space in a folder inside it, and the space's own note sits at the top of its folder as `SPACE/SPACE.md`. |
| `conky.canvas` | One canvas laying out the pages. |

A note is the page exactly as its author wrote it: nothing is added to its body. What is within a space is shown by its folder and by the canvas.

For a vault with `kitchen`, `cellar` within `kitchen`, `wine` within `cellar`, `cook` within `kitchen`, a provider `model` and a loose `note`, the tree is:

```
conky.canvas
kitchen/cellar/cellar.md
kitchen/cellar/wine.md
kitchen/cook.md
kitchen/kitchen.md
model.md
note.md
```

The canvas follows the [JSON Canvas specification](https://jsoncanvas.org/spec/1.0/), version 1.0, read on 2026-11-20. It writes the fields that specification lists as required for each node (`id`, `type`, `x`, `y`, `width`, `height`, and `file` for a file node) and for each edge (`id`, `fromNode`, `toNode`), plus the optional `label`. Each page is a file node pointing at its note. Each space is a group node, with its `label` set to the space's name, drawn around the nodes of the pages within it. Each relation is an edge labelled `within`, `watch`, `ask` or `writes`, between pages that exist. No Obsidian application settings are written.

### AFFiNE

Nothing is written. On 2026-11-20 the AFFiNE documentation index (`https://docs.affine.pro/`) and its blog index (`https://affine.pro/blog`) were read. Neither names a Markdown or folder import. The one import page found, `https://affine.pro/blog/import-your-data-from-notion-into-affine`, was seen only as a summary in the blog index: it covers importing a zip of Notion HTML. The import page of the documentation (`https://docs.affine.pro/import`) could not be fetched (the server answered 402), so no claim is made about it. `conky export affine` says this and exits with an error. To get the pages into AFFiNE, run `conky export obsidian` and look in AFFiNE's own import dialog for a Markdown option. Build the AFFiNE export when a documented import that fits is read.
