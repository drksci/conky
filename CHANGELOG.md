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
- A documentation system with frontmatter, decisions, ideas and essays, and checks for it.
