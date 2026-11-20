# Changelog

All notable changes are recorded here. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). Versions follow [Semantic Versioning](https://semver.org/). The vault format is held stable by the golden vault test in `tests/golden/`.

## [Unreleased]

### Added

- `![[page]]` with no field embeds the body of a page. A missing page or an empty body embeds nothing, as a missing field does, and a page read this way is listed in the `Read` trailer like one read by field. A page that asks a model can now read a connector's screen text.
- A vault as a Git repository: every write is a signed commit, and a refused write is an empty signed commit.
- Rules in CEL, inherited through spaces.
- Reactions: pages that watch pages and write themselves.
- Measures: pages that watch themselves, with pressure as the first use.
- `verify` and `rebuild`.
- A command line: `init`, `write`, `read`, `log`, `verify`, `rebuild`.
- A documentation system with frontmatter, a guide, a reference, decisions, ideas and essays, and checks for it.
- Continuous integration on GitHub Actions: `scripts/check` runs on every pull request and on pushes to `main`.
- A vocabulary page, `docs/reference/vocabulary.md`, listing the concept words and every name the runtime exposes, and a check that it agrees with the code in both directions. It replaces the lists of retired and internal words, which are removed.
- Explanatory figures in a pen-plotter style, shown in the README and the concepts guide.
- Prose linting with Vale: a house style in `.vale/styles/conky/` whose errors fail `scripts/check`, and `vale .` for every level.
- Pages that ask a model. A provider is a page (`openai` or `anthropic` wire format, secret by name and never in the vault). A watch entry can carry `ask` in place of `set`, and the answer is a signed write that records the prompt, the model and the tokens. Tested against stand-in servers only.
- A third provider shape, `api: command`: the prompt goes to a named program's standard input and the answer is its standard output. The program comes from outside the vault (`CONKY_COMMAND_<NAME>`, `<name>.command` in the key directory, or the built-in `claude` and `codex`), never from a page.
- A model with no provider page: when an ask names none, Conky detects one from `CONKY_PROVIDER`, `ANTHROPIC_API_KEY`, `OPENAI_API_KEY` with `CONKY_MODEL`, then `claude` and `codex` on the PATH. A failing model falls to the next, and with none a plain sentence is written, or the watch entry's `otherwise`, and the question stays unsettled so a later ask with a model replaces it. `conky model` shows the order.
- `conky ask`: a one-off question whose answer is written to a page by an actor.
- An answer that is pages: an `ask` entry, or `conky ask --writes`, names a space, and the model's reply may hold pages (`=== page: <name> ===` then the page), each written as an ordinary signed write by the asker, caused by the answer. A page must be within the space, carry no `secret` or `command`, and may not name a wider space in its own watch entries. Refusals start `limit`. Tested with stand-in models only.
- A write that changes a page's `within` is judged by the rules of the spaces it leaves as well as those it joins ([decision 0022](docs/decisions/0022-leaving-a-space-is-a-write-the-space-can-refuse.md)).
- Trailers `Model`, `Model-Name`, `Tokens-In` and `Tokens-Out`, and `model <provider>` marks in `conky log`.
- `conky demo`: builds a small example vault, with `lemonade` and `team` examples, written as notes people leave for each other, and tells its story step by step.
- Styled terminal output in the Charm manner, with rounded boxes and badges, switched by `--color auto|always|never` and `NO_COLOR`; plain output is unchanged.
- `conky connect terminal`: a connector that gives a vault eyes and hands on a terminal program. It writes the program's screen to a page and types what a hands page says, as ordinary signed writes by its own actor. POSIX only. Tested against a small game in `tests/games/trail.py`.
- Trailers `Read` on a model answer, naming the pages embedded in the prompt, and `From` on a refusal by a rule that came from a space, with `read` and `from` marks in `conky log`.
- `conky assimilate`: takes over a stopped vault from its folder alone, checks it, reads it and carries on as a new actor with a new key. With no source it uses a small stopped vault that ships in the package, built by `scripts/build_stopped_vault.py`. It is the mechanical form of the assimilation test and involves no model.
