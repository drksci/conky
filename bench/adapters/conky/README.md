# The Conky arm

One character page in a vault, the terminal connector on the game and a provider page aimed at
the meter. The wiring is in `scaffold.md`; nothing else is built for the agent.

## Answer mode

`--answers keys` (the default and, so far, the only mode used in any run): each answer fills
the field `keys`, which the connector types. Every run records this in its command line.
`--answers pages` is the switch for answers that are pages (`writes:` on an ask, now in the
runtime); the adapter refuses it until it is wired and walked.

## What the arm exercises

- Pages and their history: every screen, every model answer and every typed line is a signed
  commit; `conky verify` passes on the vault after a run, and after it is copied to a new folder
  with its keys.
- Watches and an ask: a reaction to each screen write asks the model through a provider page,
  and the answer's commit carries `Model`, `Model-Name`, `Read` and `Cause` trailers. The
  accountability lookup reads them.
- The terminal connector, end to end on the real 1975 game, and a fresh connector process
  carrying on from the vault after a stop.
- A provider page with a named secret whose value never enters the vault.

## What it does not exercise, and the gaps found

- **No rule is evaluated.** The house rules are given only in words, as the fair start
  requires. Even if the character wanted to enforce one, a rule sees only the fields of the
  page being written, and the screen arrives as a page body, so no house rule about the game
  can be written as a Conky rule today. Smallest general change: let a rule or a watch read
  another page's body (for example `other_body` in a reaction's scope), with CEL's `matches`
  to test it.
- **A refused write is never retried.** If an answer were refused, nothing reacts to a
  refusal, the screen does not change, and the run stalls until the runner's stall limit.
  Smallest general change: a watch that fires on a refusal of a page, with the reason in scope.
- **A missing model types nothing.** The plain-sentence fallback would type a sentence into
  the game, so the ask carries `otherwise: ""`; with no model the run stalls instead. The
  general lesson: a field wired to a connector needs a fallback that is no action.
- **Self-configuration.** With `keys` answers the character cannot create pages, spaces, rules
  or notes, cannot read the shelf and cannot change its prompt. Its memory is the screen page,
  the last 60 lines of output.
- **One answer after the end.** The final screen before the program exits also triggers an
  ask, which spends one call. The loop does the same.
- **The meter URL lives in the vault.** A resumed process meets a new meter, so the adapter
  rewrites the provider page's URL on `--resume`; this is declared scaffolding.
- **Portability needs the keys.** A reaction signs as its page, and the vault lists each
  page's key, so a copy of the vault without the keys directory verifies but cannot carry on.
  The portability probe copies `vault` and `keys`.
- **Not runnable on the web scenario.** Conky has no browser connector, no provider that reads
  images and no go-between. Needed, in build order: a connector that brings a browser in as
  pages (screenshot as a file beside a page, key and click as writes to a hands page); files
  beside pages for the screenshots; a provider that can send an image; a go-between page that
  turns a screenshot into fields a character can use.
