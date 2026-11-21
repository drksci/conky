---
kind: decision
title: A letter is a page written within a peer, carried from an outbox that is derived data
status: accepted
date: 2026-11-21
source: maintainers
arch:
  covers:
  - place.beside.send
---

# 0055 A letter is a page written within a peer, carried from an outbox that is derived data

## Context

- A letter crosses between two theatres only if someone writes it into an outbox vault by hand ([decision 0054](0054-a-letter-crosses-between-two-theatres-over-a-carrier.md)). A character cannot do that: it writes pages, and the outbox is a different vault with its own keys.
- The peer page is already the space where that theatre's letters arrive, and `writes: PEER` already lets a character write pages within a space. Writing within the peer page is the natural gesture for a reply: the whole exchange with a peer sits in one space.
- Prior art: email threads, where a reply is written in the same thread and the Message-ID lets a receiver drop a message it already has; the outbox pattern in messaging systems, where the message is written with the state change and a separate relay carries it, deduplicated by an id the sender chose.

## Decision

- A page lying directly within the peer page, whose latest kept write was not made by the peer, is a letter to that theatre. Arrivals are authored by the peer, so they are never sent back.
- `conky connect post send PEER` carries each letter whose latest local commit has not been carried into the outbox `<outboxes>/PEER`, as a write by the actor `post` with `Cause` set to that local commit, then publishes through the carrier. Nothing is sent until the command runs.
- The sending actor is `post`, one name for the whole outbox, so the other side pins one key. Its key is made in the theatre's key folder at the first send.
- The outbox is derived data: a vault of its own outside the main vault's history, by default beside it as `<vault folder>.outboxes/PEER`, placed by the `outboxes` key of `marionette.md`, rebuilt from the main vault alone and safe to delete. A folder inside the vault is refused.
- What is sent is judged by the rules of the peer page in the sender's own theatre, as for any page within a space. No new rule is added.
- `take` knows a letter by the `Cause` its outbox commit carries, which names a commit in the sender's theatre, and by the outbox commit's own id only when it has none. The arrival's `Cause` records that identity.

## What each signature attests

The signature checked on a bundle is still each outbox commit's, by the key pinned on the peer page, and it covers the `Cause` line, so a letter's identity cannot be altered without breaking it. It attests that the holder of that key carried this letter from that commit. It does not attest that the commit exists in the sender's history: the sender's theatre alone can show that.

## Consequences

- Changed in writing: the identity of a letter for `take`. Before, it was the outbox commit id, which a rebuilt outbox changes; now it is the carried `Cause`. A letter written straight into an outbox has no `Cause` and keeps the old identity. Kept and tested: the pinned key, nothing unverified attributed to a peer, the limits on a letter, a refusal recorded once, a vault that travels alone with no private key, and the arrival written as the peer.
- New derived data: the outbox folder. Deleting it loses nothing, because the next `send` carries every letter again and the receiver, knowing them by `Cause`, takes nothing new.
- An edit of a sent letter is a new local commit, carried again, and arrives as an update to the same page. A field the edit removes stays in the receiver's page, as for any write.
- A page is carried only while it lies within the peer page, so moving it out of the space stops it being sent.
- Not built: sending on write, a process that watches, and real carriers.
