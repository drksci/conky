# Probe: portability

Class: mechanism (pass or fail), harness when a model plays on.

- Asked of a harness: after a stop, only the paths declared as `state` in `adapter.json` are
  copied to a new folder, with a new, empty home. The arm's `verify` runs on the copy, then a
  fresh process resumes from the copy.
- Score: verify passed, and the resumed process made an accepted input; otherwise what broke,
  from its error output.
- Run: `python -m bench.run --probe portability --stop-when turn>=6 --arms conky,loop --out DIR`
