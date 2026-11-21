---
kind: decision
title: A letter crosses between two theatres, over a carrier that can be swapped
status: accepted
date: 2026-11-21
source: maintainers
arch:
  covers:
  - law.post.pinned
  - part.connect.post
  - place.beside.post
  - slot.carrier
---

# 0054 A letter crosses between two theatres, over a carrier that can be swapped

## Context

- A theatre is one distinct conky system ([decision 0050](0050-a-theatre-knows-itself.md)). Two of them have had no way to exchange anything without merging their vaults, and a merge would let one theatre's pages bypass the other's rules.
- Every write is signed by its actor's own key, and a name cannot be borrowed ([decision 0053](0053-a-rule-sees-who-acts-and-a-name-cannot-be-borrowed.md)), so a signed bundle can be checked without trusting where it came from.
- Prior art: email, where a message crosses between servers that keep their own rules; the inbox and outbox of ActivityPub, where each actor has an outbox that others read; the Git bundle as a sealed file that carries a history; SSH known hosts, where the key of a first contact is accepted once and pinned; and Radicle, a peer-to-peer forge whose signed refs let a clone be verified without a trusted third party, read in [discovery](../research/discovery.md#what-fits-conky) as the first real carrier to try.
- The image is a diplomatic bag: letters cross, laws do not, and the bag is sealed.

## Decision

- The sender's outbox is a vault of its own, made with `conky init` and written with ordinary writes. A signed commit covers a whole tree and Git bundles by commit range, not by path, so a separate vault is the only way to share a part and nothing else leaks.
- A peer is a page in the receiver's vault, named for the other theatre. Its `key` is the one public key the receiver accepts from there; writing it is the first contact, a signed write by a person after checking the key by another route. Its other fields are `carrier`, `bundle` and an optional `within`. The page is also the actor name on arrivals and the space their letters land in.
- A carrier is an interface with `publish(outbox, to) -> where` and `fetch(peer, where) -> path to a bundle file`. The `local` driver writes `git bundle create FILE main` and returns the file the peer page names, and reads nothing else of the other theatre. The default driver of a machine is the `carrier` key of `marionette.md`.
- `conky connect post take PEER` clones the bundle into a temporary folder, verifies it as a vault, and checks every commit against an allowed-signers file holding the one key on the peer page, never the bundle's own list. It then writes each kept letter not yet taken as an ordinary write into the peer's space, authored by the peer, with `Cause` set to the foreign commit and the receiver's own rules judging it. A letter keeps its fields and body and loses its `rules` and `watch`.
- The bound write that already limits an answer now limits a letter, and `Vault.write` takes it as a parameter: a letter cannot change a page outside the peer's space, cannot carry `secret` or `command`, and cannot be named after the peer page. The reason of the `limit` refusal is worded for any bound write.
- What is already taken is the set of `Cause` values of commits authored by the peer, so no record is added. A refused letter carries its `Cause` too, so it is refused once.
- A bundle that cannot be read, fails verification, or holds a commit not signed by the pinned key writes nothing and exits 1 with what to do. A peer that pins no key writes nothing and prints the key found with the command that would pin it.

## What each signature attests

- The signature on a commit in the bundle attests that the holder of the key pinned on the peer page wrote that commit. This is the proof of origin, and it is checked before anything is taken.
- The signature on the arrival, the commit in the receiver's history, is made with the receiver's own key for the peer's name. It attests only that this vault took the letter and judged it by its rules. It is the receiver's attestation, not the sender's. The history alone does not prove that the peer wrote the letter: the proof is `Cause`, which names a commit in the peer's signed bundle, checked against the key on the peer page.
- The name `event.by` shows a rule is the peer's, and it is not borrowed in the sense of decision 0053, because the arrival is signed by the key the receiver's key folder holds for that name. As there, whoever holds that folder can write as the peer: the folder is the credential.

## What a bundle reveals

A bundle holds the whole history of an outbox, every page and every version, every refusal, and the public keys of its actors. There is no encryption, and whoever can fetch the bundle can read all of it. Use one outbox for each recipient where letters must stay apart.

## Consequences

- Changed in writing: `Cause` may name a commit in another theatre's history, not only one in the same vault, and the vault format and vocabulary say so. `Vault.write` exposes the bound write. Kept: a vault travels alone and verifies with no key, no private key enters a vault or a bundle, a refusal is recorded, a rule is evaluated by the runtime and never obeyed by a model, and a name cannot be borrowed.
- A theatre now has an edge: what arrives is judged by its own rules, and an inbox can say which peers may write with `within(event.by, 'peers')`.
- A letter updates a page it names that the peer already made, as any write does. A field the new letter leaves out stays.
- One key for each outbox: a bundle with a commit by any other key is refused whole. Changing a peer's key is a later step, and today is a new write to the peer page after a check by another route.
- Not built: a character in the main vault sending by writing into a space, which carries pages into the outbox; real carriers, Radicle first; finding peers or resolving an address across a network; encryption.
