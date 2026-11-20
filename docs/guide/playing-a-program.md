---
kind: guide
title: Playing a program
status: current
date: 2026-11-20
source: maintainers
---

# Playing a program

A connector gives a vault eyes and hands on a terminal program: the screen is written to one page, and whatever a second page says to type is typed back. Every screen and key press is a signed change in the history. This page runs one for real. See [connectors](../reference/connectors.md) and the [command line reference](../reference/cli.md#connect-terminal).

The connector needs a POSIX system such as Linux or macOS. The program is a small trail game in `tests/games/trail.py`: five stretches of road, a few numbered choices at each, no randomness. It reads a line at a time and prints to standard output.

The output below comes from running these commands for real, from a folder that holds a copy of `tests/games`, with `HOME` set to an empty scratch directory. Commit ids and times differ on every run.

## A reflex that always pushes on

The page `hands` says what to type. Its one watch entry reacts to every write to `screen` by setting `keys` to `1`, the first choice at every stretch, and `turn` to the number of the screen it is answering. It is a reflex, not a mind: it never reads the screen and would type `1` whatever the game showed.

```console
$ conky init ../trail-vault
initialised ../trail-vault
$ conky --vault ../trail-vault write hands 'watch=[{on: screen, when: "true", set: {keys: "\"1\"", turn: "other.turn"}}]' --as maya
written (commit 8a81c65)
```

## Starting the connector

Everything after `--` is the program. The connector creates the `screen` page, starts the game and writes a screen each time the game goes quiet. Each screen triggers the reflex, which writes `hands`, and the connector types the keys. It prints a line for each screen and each set of keys.

```console
$ conky --vault ../trail-vault connect terminal -- python tests/games/trail.py
screen 1 written (commit 3a85420)
keys sent for screen 1: 1
screen 2 written (commit 794f669)
keys sent for screen 2: 1
screen 3 written (commit f539e8b)
keys sent for screen 3: 1
screen 4 written (commit 3dd7128)
keys sent for screen 4: 1
screen 5 written (commit 24be8d7)
keys sent for screen 5: 1
screen 6 written (commit e8d03eb)
ended: the program exited with status 0
```

The game ends after the fifth stretch, so the program exits and the connector writes `ended` to the screen page. The first screen is the opening text, and each later screen answers one set of keys.

## The history

Each screen is a write by `terminal`, the connector's actor. Each reply is a write by `hands` and names the screen that caused it. The first screen write, before any keys, is the connector creating the page. The reflex answers that too, with turn 0. It belongs to no screen, so nothing is typed.

```console
$ conky --vault ../trail-vault log
8a81c65 2026-11-20T15:15:43Z maya write hands
ccc3825 2026-11-20T15:15:44Z terminal write screen
fd2c59d 2026-11-20T15:15:44Z hands write hands cause ccc3825
3a85420 2026-11-20T15:15:44Z terminal write screen
f359b49 2026-11-20T15:15:44Z hands write hands cause 3a85420
794f669 2026-11-20T15:15:44Z terminal write screen
0858a12 2026-11-20T15:15:44Z hands write hands cause 794f669
f539e8b 2026-11-20T15:15:45Z terminal write screen
d558ac9 2026-11-20T15:15:45Z hands write hands cause f539e8b
3dd7128 2026-11-20T15:15:45Z terminal write screen
5132bf1 2026-11-20T15:15:45Z hands write hands cause 3dd7128
24be8d7 2026-11-20T15:15:46Z terminal write screen
f056ca2 2026-11-20T15:15:46Z hands write hands cause 24be8d7
e8d03eb 2026-11-20T15:15:46Z terminal write screen
fa3ae22 2026-11-20T15:15:46Z hands write hands cause e8d03eb
4da1c92 2026-11-20T15:15:46Z terminal write screen
```

The last line is the `ended` write. The reflex answered the final screen after the program had gone, and nothing read it.

## The final screen

The body is the text the program last showed. The fields say which screen it is and why the run ended.

```console
$ conky --vault ../trail-vault read screen
---
ended: the program exited with status 0
turn: 6
---
THE LONG ROAD WEST
A wagon, four people, thirty sacks of supplies and five stretches of road.

Stretch 1 of 5: The farm road. Fences, fields and a dog that follows the wagon for a mile.
Day 0, supplies 30. The party is comfortable.
  1. Push on
  2. Rest a day
  3. Hunt
> 1
Push on. The wagon keeps moving and so does everyone's temper.

Stretch 2 of 5: The dry hills. The road climbs. The water barrel does not.
Day 3, supplies 26. The party is comfortable.
  1. Push on
  2. Rest a day
  3. Hunt
> 1
Push on. The wagon keeps moving and so does everyone's temper.

Stretch 3 of 5: The wide river. Brown, fast and wider than the map claimed.
Day 6, supplies 22. The party is comfortable.
  1. Ford the river
  2. Wait for the water to drop
  3. Hunt along the bank
> 1
Ford the river. The wagon crosses. One sack of flour does not.

Stretch 4 of 5: The salt flats. Flat, white and without a single tree to complain under.
Day 7, supplies 17. The party is comfortable.
  1. Push on
  2. Rest a day
  3. Hunt
> 1
Push on. The wagon keeps moving and so does everyone's temper.

Stretch 5 of 5: The high pass. Cold wind, thin air and the last hill of the journey.
Day 10, supplies 13. The party is comfortable.
  1. Push on
  2. Rest a day
  3. Hunt
> 1
Push on. The wagon keeps moving and so does everyone's temper.

Journey's end. 13 days on the road, 9 sacks of supplies left.
The party arrived on time and fed. The oxen expect a raise.
The journal reads: push on, push on, ford the river, push on, push on.
```

It is an ordinary vault, so `verify` passes on it, and on a clone of it.

```console
$ conky --vault ../trail-vault verify
ok: 16 commits verified
```

## What this shows and what it does not

The reacting page is a reflex, so it plays the same move whatever the screen says, which makes the dullest possible journey. What the run shows is the mechanism: a program's screen becomes a page, a page's words become keys, and both directions pass through the same rules and history as any other write.

A page that asks a model can play the same way once a provider is set up. It watches `screen`, asks the model what to type and writes the answer into `keys` with the `turn` it answers. See [pages that ask a model](../reference/rules-and-reactions.md#asking-a-model) and [providers](../reference/providers.md). The prompt embeds the screen text with `![[screen]]`, which reads the body of a page the way `![[screen#turn]]` reads a field:

```yaml
watch:
- on: screen
  when: "true"
  ask:
    provider: helper
    prompt: "The program shows:\n![[screen]]\nWhich key should be typed next?"
    into: keys
```

The model sees each new screen, and is asked again only when the screen text changed. A test with a stand-in provider checks this. No model was called for this page, and no output of one is shown.

A rule can also limit the hands. A rule on `hands`, or on a space it belongs to, that forbids a particular `keys` value turns that write away. The refusal is recorded and the program never receives the key.
