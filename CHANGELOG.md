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
- `conky demo`: builds a small example vault, with `stall` and `team` examples, and tells its story step by step.
- Styled terminal output in the Charm manner, with rounded boxes and badges, switched by `--color auto|always|never` and `NO_COLOR`; plain output is unchanged.
