---
kind: reference
title: Connectors
status: current
date: 2026-11-20
source: maintainers
---

# Connectors

A connector is a process that runs beside a vault. It holds no state of its own, signs its writes with its own key, and is subject to the same rules as any other actor. Stop it, delete it and start another, and nothing is lost: everything it did is in the vault's history. The idea is in [connectors](../ideas/connectors.md). One connector is built, for a terminal program.

## The terminal connector

```
conky connect terminal [--vault V] [--keys K] [--as NAME] [--screen PAGE] [--hands PAGE]
                       [--settle SECONDS] [--max-steps N] -- COMMAND [ARGS...]
```

The options are described in the [command line reference](cli.md#connect-terminal). The connector starts the command in a pseudo-terminal. It gives the vault eyes, by writing what the program shows to the screen page, and hands, by typing what the hands page says. Any page can then play the program: a reflex, a person writing by hand, or a page that [asks a model](rules-and-reactions.md#asking-a-model). The guide [playing a program](../guide/playing-a-program.md) runs one for real.

### The screen page

Default name `screen`. The connector creates it if it does not exist, with a short body that says what it is and the field `turn` set to 0.

| Part | Meaning |
|---|---|
| Body | The text on the screen: the last 60 lines of the program's output, with terminal control sequences removed. |
| `turn` | The number of screens written, counting from 1. |
| `ended` | Empty until the run ends, then a short reason. |

A screen is written when the program's output has been quiet for the settle time (`--settle`, default 0.3 seconds). It is an ordinary signed write by the connector's actor (default `terminal`), so rules apply to it and it appears in the history. A screen whose text equals the previous one is not written again.

The run ends when the program exits, after `--max-steps` screens (default 200), or on interrupt. The connector then writes `ended` with the reason: `the program exited with status N`, `stopped after N screens` or `interrupted`. The exit code of the connector is 0 for each of these.

### The hands page

Default name `hands`. The connector creates it if it does not exist. It reads these fields:

| Field | Meaning |
|---|---|
| `keys` | Text to send to the program. It must be text, so quote a number: `keys='"1"'` on the command line. |
| `turn` | The number of the screen the keys answer. |
| `enter` | When `false`, no newline follows the keys. Any other value, or no field, sends one. |

The connector sends the keys when the hands page changes, `keys` holds text, and `turn` equals the number of the current screen. A hands write for an old turn is ignored, and so is a second write for a turn already answered. After sending, the connector waits for the next screen.

A page plays the program by reading `screen` and writing `hands` with the turn it is answering. A reaction on the hands page that watches `screen` does this with `turn: other.turn`. A rule refuses a hands write like any other, and the refusal is recorded. The program never receives refused keys, so a rule on the hands page, or on a space it belongs to, limits what can be typed.

The connector finds hands writes by polling the vault's history, about twenty times a second. Reactions to a screen write run inside that write, so a hands write made by a reaction is seen as soon as the screen write returns.

### Output

The connector prints one line for each screen written and each set of keys sent, and one for the end of the run. Output is plain when piped and styled in a terminal, as described in [colour and styled output](cli.md#colour-and-styled-output).

## Limits

- POSIX only. The program runs in a pseudo-terminal, which Windows does not offer. On Windows the command stops with an error that says so.
- Text only. Colour, cursor movement and other control sequences are removed, and a program that draws by moving the cursor shows as the text it leaves behind.
- Polling. A hands write is noticed within a fraction of a second, not at once.
- The screen is the tail of the output, not a model of a terminal window.
- The program gets the terminal on its standard streams but not as its controlling terminal, so a program that opens `/dev/tty` directly may not work.
- A prompt cannot embed the screen text. An embed reads a field, and the screen text is the body of the page. A prompt can embed the screen's `turn` and fields of other pages, not the screen itself.
- One program and one pair of pages per run. To play two programs, run two connectors with different `--screen`, `--hands` and `--as`.
- The page named by `--screen` is written to by the connector, so a rule that refuses its writes stops the run from recording screens. The refusal is recorded and printed.
