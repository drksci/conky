---
kind: decision
title: Pay once
status: accepted
date: 2026-11-20
source: maintainers
arch:
  covers:
  - part:answer-cache
---

# 0030 Pay once

## Context

- A model call costs money and time. So do a call to an outside service, a download and heavy local computation.
- The same question is easy to pay for twice by accident: a retry after a crash, a rebuild that replays, a cascade that is run again after a failure, a test suite, a benchmark that repeats a step.
- A cache that returns the same words every time would flatten a character. Asking again in a new moment is a new question, and two runs of the same vault should differ the way two days do ([decision 0020](0020-everything-is-somebody.md)).
- Anything built to make a vault cheaper to use is derived data ([decision 0017](0017-derived-data.md)).

## Decision

Nothing costly is paid for twice by accident. Costly means a model call, a call to an outside service or tool, a download, or heavy local computation. Each is cached by content, as derived data: outside the history, deletable at any time with no loss of truth, never read as the truth. A vault verifies and behaves correctly without it.

**Where it lives.** In `~/.conky/cache`, beside the default key directory, and nowhere inside a vault. `--cache-dir` and `CONKY_CACHE_DIR` move it, the way `--keys` moves the keys. A vault that is cloned or bundled never carries it, one cache serves every vault on the machine, and Git has nothing to ignore. This narrows [0017](0017-derived-data.md), which puts derived data in a `.conky/` directory of the vault: a cache of paid answers cannot be rebuilt from the vault alone, only paid for again, and that is the whole cost a deletion has.

**What an entry is.** A small JSON file named by the hash of its key, so a person can read it and delete it. A write is atomic. An entry that cannot be read, or is not the shape expected, is a miss and is replaced by the next live call, never an error ([decision 0026](0026-it-always-works.md)). The cache holds at most `CONKY_CACHE_MAX` megabytes, 64 by default, and drops the oldest entries first. A hit renews an entry.

**The key of a model answer.** The hash of the provider's shape, its endpoint or command name, its model name, the most tokens it may write, the whole prompt as sent (including the instruction that lets the answer hold pages), and the cause of the question. The cause is the event that triggered it: the `Cause` of a reaction, and for `conky ask` the head of the vault. The page's name and the secret's name are not in the key, since neither changes what the model is asked.

So the same question for the same event is paid for once: a retry after a crash, a replay, a failed cascade run again, a test. The same words asked after a new event have another key and are asked afresh.

**How a hit is recorded.** As a live answer is, with the trailer `Cache: hit`. `Tokens-In` and `Tokens-Out` are left out of a hit, because nothing was spent, so a sum of the token trailers over a history is the spend. The first answer keeps its counts.

**Modes.** `CONKY_CACHE` and `--cache-mode` take one of:

| Mode | Meaning |
|---|---|
| `on` | The default. Read before asking, write what is paid for. |
| `off` | Neither read nor write. |
| `refresh` | Ignore existing entries and write new ones. |
| `only` | Never call a provider. A miss falls to the plain sentence. Tests and offline replays use it. |

The plain sentence is never cached, and neither is a failed call.

**Other costly work.** The packaged stopped vault is a file that ships in the package, and `conky assimilate` clones it from disk, so it needs no cache. Cloning a URL given to `assimilate` is a deliberate fresh copy and a cached one would go stale. `connect terminal` runs an interactive program whose output is the point. `scripts/build_stopped_vault.py` is a maintainers' script that makes a few local commits and is checked by a test. Nothing else in `src/` or `scripts/` downloads or recomputes anything large, so none of it is routed through the cache. A new costly step is routed through `conky.cache` in the change that adds it.

**The benchmark.** The benchmark's meter keeps its own record and replay of model calls, under the same rule: pay once, keep the record outside the repository, replay it offline. It does not share this cache, because a benchmark must show what a run spent, and a run that read the cache would hide it.

## Consequences

- A test never reaches a live provider twice, and each test has its own cache directory.
- A character still answers afresh after a new event, so the cache saves cost and not character.
- A cache hit is visible in the history, and its absence of token counts keeps the spend honest.
- A new costly step adds a key to the cache instead of a second mechanism.
- The history records answers whether or not the cache exists, so the cache is never needed to read a vault.

## Open questions

- Whether a cache may be shared between machines. A shared answer would need its provider's identity checked.
- Whether the key should include the content of a command provider's program, which can change under the same name.
