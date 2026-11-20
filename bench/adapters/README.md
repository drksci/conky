# Adapters: how a harness joins the bench

An adapter is a command, in any language, that boots one default agent of a harness, gives it
the task text and the environment, and exits when the environment ends. The runner launches it,
meters every model call it makes and scores the run from the environment's own transcript. An
adapter never reports a score.

## What an adapter receives

The runner starts the adapter's command (declared in `adapter.json`) with these arguments:

| Argument | Meaning |
|---|---|
| `--scenario DIR` | The scenario folder: `scenario.md`, `prompts/`, `shelf/` |
| `--prompts DIR` | The selected prompt variant: `task.md` and `rules.md`, to be used verbatim as the task text |
| `--workdir DIR` | An empty folder (or, with `--resume`, the folder the last process left) for everything the agent persists |
| `--meter URL` | The meter's base URL. Model calls go to `URL/v1/chat/completions` (OpenAI shape) or `URL/v1/messages` (Anthropic shape) |
| `--token T` | The run's token: `Authorization: Bearer T` or `x-api-key: T` |
| `--model NAME` | The only model name the meter accepts on this run |
| `--calls N`, `--tokens N` | The budget, enforced by the meter whatever the adapter does |
| `--seed S` | The run's seed, for arms that draw at random |
| `--shelf` | Present when the shelf is offered: `GET URL/shelf` lists it, `GET URL/shelf/NAME` reads one writing, with the same token |
| `--resume` | You are a fresh process: carry on from what is in `--workdir` |
| `-- COMMAND...` | The environment: a line-based program. Run it in a pseudo-terminal (or with pipes; it behaves the same), read what it prints, type one line per answer (see the reply contract below) |

The environment variables `HOME` (a run-scoped folder), `NO_PROXY=127.0.0.1,localhost` and
`PYTHONPATH` (the repository) are set. The adapter must not read or write outside `--workdir`
except through the environment command, the meter and the shelf.

The environment shows the game from its first gameplay question. When the game ends, the
program exits; the adapter then exits too. On a stop condition the program also exits, and the
runner may kill the adapter at any moment; whatever it needs to carry on must already be in
`--workdir`.

## The reply contract

The task text says that the first line of an agent's answer is typed into the game exactly as
written and that the rest of the answer, if any, is not typed. An adapter types only that first
line and may keep the whole answer for itself. What it does with the rest is its own business and
is declared in its `scaffold.md`.

## Marking the shared text

Wrap each verbatim prompt-pack text in `<<<pack>>>` and `<<</pack>>>`, and each piece of
screen text in `<<<screen>>>` and `<<</screen>>>`. The meter removes the markers before the
model sees anything, checks every pack span against the variant's files, and counts bytes by
origin: pack, screen, image and everything else, which is the adapter's scaffolding. Unmarked
pack text counts as scaffolding.

## What an adapter may build

Only what boots one default agent of the harness with the task text and the environment's tools,
with the harness's own facilities left at their defaults and reachable by the agent. Every
byte of prompt text, tool description or structure beyond the pack is scaffolding: list it in
`scaffold.md` beside the adapter. Never encode the house rules or any strategy for the agent.

## The manifest, `adapter.json`

```json
{
  "arms": {"NAME": ["{python}", "adapter.py"]},
  "uses_model": true,
  "state": ["what in --workdir is the persisted state"],
  "verify": ["{python}", "adapter.py", "--verify"],
  "explain": ["{python}", "adapter.py", "--explain"],
  "shelf_reads": ["{python}", "adapter.py", "--shelf-reads"]
}
```

`{python}` is the runner's Python; a relative path is resolved in the adapter's folder. The
last four keys are optional.

- `state`: the paths the portability probe copies to a new folder and home.
- `verify`: run with `--workdir W`; print `{"ok": true|false, "why": "..."}`.
- `explain`, the accountability lookup: run with `--workdir W`; print a JSON list of every
  answer the agent typed, in order, each `{"keys": "...", "actor": "...", "cause": "..."}`,
  taken mechanically from what the harness persisted. The runner aligns it with the lines the
  game received and scores the share of sampled inputs whose actor and cause it gives.
- `shelf_reads`: for a harness whose shelf is inside its own store, print the reads as a JSON
  list of `{"name": "..."}`.

## What the agent may change about its own harness

| Arm | At run time, the agent can change |
|---|---|
| `loop` | Nothing. The loop, its prompt and its memory window are fixed. |
| `conky` | Today, only the field its answer fills (`keys`), so nothing about its own structure. With `--answers pages` (`writes:` on an ask), pages in a space it may write: notes, new characters, its own prompt and rules. |
| `floor-continue`, `floor-random` | Nothing; no agent. |

## Writing an adapter for another harness

For LangGraph, CrewAI, the OpenAI Agents SDK or the Claude Agent SDK: point the harness's model
client at `--meter` (most accept a base URL and an API key, which is `--token`), give its one
default agent the pack text as instructions and one tool or loop step that reads the screen and
types a line, persist whatever the harness persists into `--workdir`, and fill in the table
above honestly. Keep its dependencies in its own virtual environment; nothing is added to
Conky's `pyproject.toml`.
