---
kind: idea
title: A felt sense of magnitude
status: idea
date: 2026-11-20
source: the owner's request for a shared way to feel time, severity and impact, and the digest in research/where-am-i.md
arch:
  covers:
  - kind.codec
---

# A felt sense of magnitude

## Idea

A magnitude reaches a character placed on something it already understands, not as a bare number. Time passed, how severe, how much is at stake and how far off course are each given as a position among familiar anchors, with the raw value kept in the record beside it. Nothing of this is built.

This is the inward [codec](codec.md) for magnitudes. A [measure](measures.md) produces the number. A codec page holds the map from that number to a place among anchors. A character reads the placed version.

- Time: a moment, a meal, a night, a week, a season.
- Severity: an inconvenience, an injury, a loss.

These anchors are examples for this page. The source gives none for magnitudes.

## The hypothesis

A model reads "3600" and "86400" as tokens, and "an hour" and "a day" as experience, so the placed version should steer it better. This is a hypothesis to test. The source digest does not demonstrate it.

## One frame for several dimensions

Several dimensions placed on the same anchors can be compared: an hour late against a small injury against a lost week. The owner called this a manifold. The [source](../research/where-am-i.md) uses the word as a picture only: it estimated no maps between models and measured only the overlap of shared landmarks. This page borrows the plainer part. Position is stated against anchors that anyone can check, and the anchors are fixed and public, not private coordinates. No geometry is claimed here.

## The source's caution

The source found that a model gives a confident gradient for a nonsense axis as readily as a real one. So the placement is never asked of a model. It is a pure rule over the number, with thresholds written on the codec page.

## What stays strict

- Rules and measures compute on the raw value and stay pure. The placed version is for reading.
- It is derived. Deleting the codec changes no fact and no history.
- With no codec, a character gets the number and a plain unit ([decision 0026](../decisions/0026-it-always-works.md)).
- The map is a page: written once by thought, visible, revisable, shareable as a [pattern](patterns.md), and the same for every character in a space that hands it down.

## Composes from

[Measure](measures.md), the [clock](clock.md), [codec](codec.md), [pattern](patterns.md) and embed (the placed version is embedded where a character reads).

## Removes

Prompts that hand a model raw timestamps and scores and ask it to care.

## Depends on

The clock (time is a write) and codecs.

## Falsifying test

- Characters given placed magnitudes make the same decisions as characters given raw numbers. Then it adds nothing.
- The placement misleads at the ends of a scale, such as a value far beyond the last anchor.
- Two characters with the same codec read the same value differently in ways that matter.
- A prompt-class control for the [evaluation plan](../research/evaluation-plan.md): same harness, same model, same budget, raw against placed. The result is a prompt result and is never cited as a claim about Conky. The source's untested control applies as well: familiar anchor names against opaque ones.
- The protocol for this test, with its conditions, tasks and analysis fixed before any run, is the [felt-sense experiment](../research/felt-sense-experiment.md).

## Open questions

- Who chooses the anchors, and whether they are cultural.
- Emotion is not a measure of the world. The docs give a character a temperament that a model reads as context and that never controls a rule ([a page with a self](character.md)). They say nothing on drive, valence or feeling, and the source is silent too. A character's felt state could be a measure of its own pages, placed the same way, but that is a guess here and not a design.
