# The Conky arm's scaffolding

Everything this adapter builds, which is its whole contribution. Nothing else is built for the
agent.

## The vault at the start

- `traveller`: the one character. Fields `task` and `house_rules` hold the prompt pack's two
  files verbatim. Its body is one line: "A traveller on the trail. It answers each screen with
  what to type." Two watch entries on `screen`, both when a real screen arrives (turn above 0,
  not ended):
  - ask the provider `meter` with the prompt below, answer into `keys`, and write nothing
    (`otherwise: ""`) when no model answers, so a missing model never types a sentence into
    the game;
  - set `turn` to the screen's turn, which tells the connector which screen is answered.
- `meter`: the provider page, `api: openai`, the meter's URL, the run's model and the secret
  name `bench`. The secret's value is the run token, passed in the environment as
  `CONKY_SECRET_BENCH`, never in the vault. On `--resume` the adapter rewrites the URL if the
  meter has moved.
- `shelf` and `shelf-NAME`: when the shelf is offered, a space page and one page per writing,
  each holding the writing's text. This is the neutral seed, the same writings every arm gets.

## The prompt the character asks with

```
<<<pack>>>![[traveller#task]]<<</pack>>>

<<<pack>>>![[traveller#house_rules]]<<</pack>>>

The shelf is the space `shelf` in this vault, pages: shelf-art-of-war, ... .

The screen:
<<<screen>>>![[screen]]<<</screen>>>
```

The shelf line is present only when the shelf is offered. The scaffolding is the shelf line and
"The screen:", with the blank lines between parts: about 160 bytes a call with the shelf.

## With `--answers pages`

The same vault, with exactly these additions and nothing else:

- `den`: a space page, body "Where the traveller may keep what it writes."
- `traveller` gains the fields `within: den` and `turn: 0` (so it is a page inside the space, and
  its own `turn` exists before the first screen).
- The ask gains `writes: den`, and its `when` gains ` && page.turn != other.turn`, so a screen
  that a case on the page has already answered is not asked about again.
- The prompt starts with one line, "You are the page `traveller` in the space `den`.", and its
  last part reads `The screen, turn ![[screen#turn]]:` in place of `The screen:`. The character
  cannot rewrite its own page without knowing its name, and a case on its own page can key only
  on the screen page's `turn`, which the screen's text does not show.
- The runtime appends its own fixed instruction for pages to the prompt, as it does for every
  ask with `writes`; the adapter does not write it.

A case, when the character makes one, is a watch entry it writes on its own page, in the form
`on: screen`, `when: other.turn == N && <live>`, `set: {keys: '<line>', turn: other.turn}`. The
adapter ships none; the scripted stand-in writes one (`bench/backends.py`).

## The process

The terminal connector (`conky connect terminal --hands traveller`) runs the environment,
writes each screen to the page `screen` and types `keys`. `CONKY_PROVIDER=none` is set so no
model but the meter can answer, and `CONKY_CACHE=off` so Conky's own answer cache never serves a
call: the meter keeps the record of calls for every arm alike, and runs stay independent.

## Reading the shelf

With `--answers keys` the character cannot read a shelf page: its prompt is fixed in its watch
entry and its answer can only fill `keys`. With `--answers pages` it can rewrite its own watch
entry to embed `![[shelf-fables]]`, and the read appears in the record's `Read` trailer, from
which the runner takes the shelf log. Whether it does is left to the model.
