# Changelog

All notable changes are recorded here. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). Versions follow [Semantic Versioning](https://semver.org/). The vault format is held stable by the golden vault test in `tests/golden/`.

## [Unreleased]

### Added

- A vault as a Git repository: every write is a signed commit, and a refused write is an empty signed commit.
- Rules in CEL, inherited through spaces.
- Reactions: pages that watch pages and write themselves.
- Measures: pages that watch themselves, with pressure as the first use.
- `verify` and `rebuild`.
- A command line: `init`, `write`, `read`, `log`, `verify`, `rebuild`.
- A documentation system with frontmatter, a guide, a reference, decisions, ideas and essays, and checks for it.
- Continuous integration on GitHub Actions: `scripts/check` runs on every pull request and on pushes to `main`.
- A check that no internal wording appears in tracked text files.
- Explanatory figures in a pen-plotter style, shown in the README and the concepts guide.
- Prose linting with Vale: a house style in `.vale/styles/conky/` whose errors fail `scripts/check`, and `vale .` for every level.
- Pages that ask a model. A provider is a page (`openai` or `anthropic` wire format, secret by name and never in the vault). A watch entry can carry `ask` in place of `set`, and the answer is a signed write that records the prompt, the model and the tokens. Tested against stand-in servers only.
- `conky ask`: a one-off question whose answer is written to a page by an actor.
- Trailers `Model`, `Model-Name`, `Tokens-In` and `Tokens-Out`, and `model <provider>` marks in `conky log`.
- `conky demo`: builds a small example vault, with `lemonade` and `team` examples, written as notes people leave for each other, and tells its story step by step.
- Styled terminal output in the Charm manner, with rounded boxes and badges, switched by `--color auto|always|never` and `NO_COLOR`; plain output is unchanged.
- `conky connect terminal`: a connector that gives a vault eyes and hands on a terminal program. It writes the program's screen to a page and types what a hands page says, as ordinary signed writes by its own actor. POSIX only. Tested against a small game in `tests/games/trail.py`.
- Trailers `Read` on a model answer, naming the pages embedded in the prompt, and `From` on a refusal by a rule that came from a space, with `read` and `from` marks in `conky log`.
- `conky assimilate`: takes over a stopped vault from its folder alone, checks it, reads it and carries on as a new actor with a new key. With no source it uses a small stopped vault that ships in the package, built by `scripts/build_stopped_vault.py`. It is the mechanical form of the assimilation test and involves no model.
