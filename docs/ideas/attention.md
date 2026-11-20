---
kind: idea
title: 'Attention: who hears what, and at which layer'
status: idea
date: 2026-11-20
source: maintainers
arch:
  items:
  - kind: unplaced
    name: attention
    text: Every page hears what it chose to hear, at the cheapest layer that can deal with it, and a thinking page is shown only what its own household passed up. It needs an event a watch can read and an ordered, budgeted list of members.
---

# Attention: who hears what, and at which layer

## The image

A ship at night. A bell rings and the cabin boy deals with it. What he cannot deal with goes to the mate. The captain is woken for the one thing in a hundred that needs a captain, and is told it in a sentence. Nobody tells the captain how the bells are wired.

## Idea

Every page hears what it chose to hear, at the cheapest layer that can deal with it, and a thinking page is shown only what its own household passed up.

## The general case

Getting each event to the cheapest thing that can deal with it, and passing only the residue upward. It is the same problem as interrupts, exception propagation, triage and supervision. The history is already the bus: every commit is an event, and nothing else carries one.

## What exists

| Element | In conky's words | State |
|---|---|---|
| Bus | the vault's history; every commit is an event | built |
| Emit | any write or refusal; a connector's write is the same | built |
| Subscribe | a watch entry on the listener, written by the listener; a character can write the entry for the space it works in, by reflex only ([decision 0041](../decisions/0041-a-character-gives-its-space-reflexes.md)) | built |
| Where | `on`: a name, `within`, `link`; and `on: refusal` | built ([decision 0039](../decisions/0039-an-event-can-be-noticed.md)) |
| What happened | `event.kind`, `event.by`, `event.reason` readable in a watch | built |
| Layer | `set` is a reflex, `ask` of a small provider is a faculty, `ask` of the character's own provider is thought | built; a faculty is a convention with no golden yet ([faculties](faculties.md)) |
| Household | a character is a space and its faculties are pages within it | composable now; untested |
| Bubble up | a faculty writes a field and the character's prompt embeds it | built (embed); untested as a pattern |
| Escalate | a higher entry's `when` reads a lower layer's field | built; trial T3 |
| Adapt | thresholds and order are fields a reflex recomputes | measures built; [standing](standing.md) not built |
| Order and cut | members shown in order of a field, cut to a budget | not built |
| Budget | every layer declares its allowance and is metered | not built |
| Walls | `each` rules on the household; the depth limit | built |
| Outside | a connector is a listener and emitter beside the vault ([connectors](connectors.md)) | terminal only |

## The layers, read sideways

The same table read across is a stack of communication layers. Each talks only to the next, through pages.

- Transport: the connector.
- Event: the commit.
- Relation: `on`, who is told about what.
- Attention: order and cut, what is shown first and how much.
- Cognition: the layer that answers, reflex, faculty or thought.

## Encapsulation rules

- A thinking page never reads raw events. It reads fields its household wrote. Trial T2 measures this: the prompt of the thinking page holds no word about the mechanism.
- A faculty writes only within its household, by the `writes:` limit that exists.
- What crosses a household's wall is a page written into a shared space, under that space's `each` rules ([approvals](approvals.md) is one such crossing).
- Every layer has a budget. Exceeding it is a refusal, which is itself an event the household hears.

## Prior art looked at

- Erlang links and supervision: a process that wants to hear of another's failure links to it, and a supervisor decides what a failure means.
- Interrupt priority levels: a handler at a low level is not woken by what a lower-level handler already took.
- Brooks's subsumption architecture: lower layers act, and higher layers inhibit or redirect.
- Selective receive in actor mailboxes: a receiver takes the messages it matches and leaves the rest.
- Triage: the cheapest competent person sees each case first, and only the residue reaches the specialist.

## Trial ladder

Each trial has one dial, and the measure is how many events reach the top layer for the same outcome.

- T1, a keeper hears the no. A refused payment in the den is counted by a reflex and nobody is asked. Dial: the entry present or absent. It waits on `on: refusal`.
- T2, the clerk's notes. A notes faculty within the clerk keeps what matters in a sentence with its meaning, and the clerk's prompt says nothing about keeping. Evidence that prompted it: in a walked draw a small model put a bare number in bold, the number was kept and shown, and it still could not say what the number was. Dial: faculty present or absent. Shown when the clerk answers and its prompt holds no instruction about memory.
- T3, the mate and the captain. Ten events: a reflex handles those a condition can, a faculty handles those a sentence can, and the captain is asked at most once. Dial: the number of calls to the top layer.
- T4, the crowded desk. Thirty pages within; the character is shown the five that standing puts first and still acts on the right one. Dial: the budget.
- T5, the neighbour. An offer crosses between two households through a shared space and is taken up or left. Dial: the shared space present or absent.

An arc over T1 to T4 would show the cost of each round falling.

## Falsifying test

If the thinking page must be told how keeping works for the clerk's notes to pass, the encapsulation claim is lost. If the ten events of T3 reach the top layer as often with the layers as without, the layering is not worth its pages.

## Few on purpose

The idea needs two additions to the runtime: an event a watch can read, and members shown in order of a field and cut to a budget. Everything else is composed from existing words. What is left to characters is the rest: which events matter to them, which faculties they keep, what their thresholds are and how those adapt.

## Depends on

[Standing](standing.md) for the order, [faculties](faculties.md) for the middle layer, and [measures](measures.md) for thresholds that adapt.
