# The cli arm's scaffolding

A stock agent command line is run once and left to play however it likes. This adapter builds
only what is listed here. Byte counts are of the files as they are today.

## The command line

Default, `DEFAULT_AGENT` in `adapter.py` (230 bytes), with `{model}` filled in from `--model`:

```
claude -p --model {model} --output-format json --permission-mode dontAsk
  --tools Bash,Read,Write,Edit
  --allowedTools "Bash(./game:*),Read,Write,Edit"
  --no-session-persistence --disable-slash-commands --max-budget-usd 5
```

Flags as `claude --help` lists them for version 2.1.329; none was run live.

- `-p`: print mode, one run, then exit. The prompt arrives on standard input.
- `--model`: the run's model name, the same as every metered arm.
- `--output-format json`: one result object at the end, with the command line's own account of
  turns, cost and tokens.
- `--permission-mode dontAsk`: anything not allowed below is denied without asking.
- `--tools` and `--allowedTools`: the built-in tools offered are Bash, Read, Write and Edit;
  Bash is allowed only for `./game`, the file tools for the working directory.
- `--no-session-persistence` and `--disable-slash-commands`: nothing kept outside the working
  directory, no skills or commands.
- `--max-budget-usd 5`: the command line's own dollar cap. It is not the meter's budget.

`--agent COMMAND` on the runner replaces all of it. `HOME` is the run's own folder, so no user
settings are read; a key for the command line must be in the environment.

This version of `claude --help` lists no flag for a turn limit. The limit is the adapter's: at
most 150 lines typed into the game (`--turn-limit`, set in `adapter.json`). The next `./game "<line>"`
past it is refused, the command line is stopped and the adapter exits with code 4.

## The working directory

`workdir/agent/` is the command line's directory. It holds `game` (the helper, 1186 bytes,
`game.py` copied and made executable) and, when the run offers the shelf, `shelf/`, a copy of the
scenario's shelf folder as plain files (15771 bytes in six files).
The helper reaches the adapter through `.game.sock` in the same folder.

## The prompt

On standard input, in order: the prompt pack's `task.md` (645 bytes) and `rules.md` (253
bytes) verbatim, then two declared lines (359 bytes together):

```
The game is already running. Type one line into it by running ./game "<line>" in your working directory, which prints the new screen; ./game with no argument prints the current screen. Your reply is not typed into the game: only ./game types.
Files in your working directory are yours to read and write; the shelf, if there is one, is the folder shelf/ there.
```

No marker is placed around any of it: no meter reads it.

## What is recorded

- `workdir/session.jsonl`: the first screen, then each line `./game` typed with the screen it
  printed. The game's own `transcript.jsonl` stays the ground truth.
- `workdir/report.json`: the command, its exit code, why the session ended, the lines typed and
  the command line's own account of itself (`self_reported`), copied into `run.json`.
- `workdir/agent.out`, `agent.err`: its standard output and error.
