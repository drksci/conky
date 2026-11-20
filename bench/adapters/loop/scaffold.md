# The loop arm's scaffolding

The loop is the only structure. Each turn it reads what the game printed until it is quiet,
calls the meter once and types the reply.

- System message: the two pack files, each marked, and, when the shelf is offered, one line:
  "To consult the shelf, reply SHELF to list it or SHELF READ <name> to read one writing; such
  a reply is answered here and not typed into the game."
- User message: "Earlier screens and what was typed:" followed by up to 6000 characters of
  past screens (marked) with "Typed: ..." after each, then "The screen now:" and the current
  screen (marked).
- A reply starting with SHELF is answered from the shelf and asked again, at most three times a
  turn; any other reply has only its first non-empty line typed, after trimming spaces at its ends;
  the rest is not typed and stays in the transcript with the whole answer.
- On a meter error it stops and exits.
- Its persisted state is `transcript.jsonl`: every screen and what was typed, every shelf read.
