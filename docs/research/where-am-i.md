---
kind: research
title: "MARCO: a shared word for where an agent is"
status: current
date: 2026-11-20
source: "https://drksci.com/research-where-am-i"
---

# MARCO: a shared word for where an agent is

## How to read this

The page was fetched on 2026-11-20 and its full text was read, including the method, the measured results and the section titled "What this is not". The link list at the end of the page names evidence files and a plain-text rules page (`llms.txt`). None of those was fetched, and neither was the paper the page replies to. Every number below is the page's own report of its own experiments, labelled there as internal. None has been checked here. Only short phrases are quoted.

## What the page says

Agents know a great deal about their situation (filesystem, tools, permissions, network, who is directing them) and have "no phrase" to tell a peer, or to notice that two of them stand in the same place. The page proposes a short pronounceable word, a locus, that two agents can compute from the same evidence and compare by ear.

The page is about location in a space of situations. It does not treat time, severity, emotion or feeling.

## Key concepts

- **Landmarks, not coordinates.** No two models share an internal geometry, so agreeing on coordinates is "hopeless". The page borrows the GPS shape instead: agree on public landmarks, and a position is the distance from each. The primer publishes 45 checkable statements (anchors) of eight kinds, written by hand, such as `cap/reachable/git`.
- **Markers on every claim.** An agent ticks the anchors that hold and marks each as checked by a repeatable program, measured or estimated, or believed. The word's floor is its weakest marker, and belief may never be written as proof.
- **Fixed pipeline.** Claims are sorted into a canonical set. The set gives an exact commitment (SHA-256) and, separately, a similarity signature (MinHash, 96 hashes) that is quantised, Gray-decoded and spoken as syllables. Similar situations share long prefixes. The commitment is exact and the locus is approximate, kept as separate outputs because a code that preserves nearness leaks neighbourhood.
- **One manifold, many charts.** There is one space of situations and each model draws a private chart of it. The page says the transition maps between charts are never estimated, that the design chose "a partially observed, stratified metric space over a smooth manifold", and that what is measured is only the overlap of ticked landmarks. The manifold language is the picture, not a measured structure.
- **Compliance is not signal.** Asked to rate states on a named dimension, a model gave as wide a spread for a nonsense axis ("glorbiness", 97) as for real ones (96). Repeat consistency separated them better (0.93 against 0.71). Asked about one dimension, models answer in one dimension. Cross-model agreement is hypothesised to depend on whether the dimension varies across the states, which is not yet tested.

## What it establishes

As reported, all small and internal:

- Four model families matched six situations blind with 34 of 36 correct, against a shuffled null of about 11 percent (the headline tile). The 36 matches rest on a shared primer, encoder and seed.
- Sixteen states, two isolated instances of one family: 16 of 16, against a null of 6.5 percent.
- A 1-bit word recovers about 9 of 16 states blind. A 2-bit word recovers all 16.
- A live exchange between two models in one workspace gave identical checked lines, and the words differed only where beliefs differed.
- Replaying a proof in three locations gave the same word with different seals.
- Memory as landmarks decays into its category, not a blurred self: past about 69 percent loss a memory is more like its kind than itself.

## What it does not establish

The page says so itself:

- The samples are small, one pair of agents was tested live, and the families shared anchors, encoder and seed.
- The test that would isolate the anchors, opaque names against shuffled and garbage controls, "is written and has not been run". So it is not known whether the meaning of an anchor's name matters.
- Situations were mostly described in prose and models self-reported. A locus is testimony, not evidence, until anchors come from real probes.
- Hide-and-seek, the demonstration the name promises, "has never been achieved".
- Fibre bundles, holonomy, causal phase, performable bearings and grid-cell codes are conjecture. A literature survey rated most components reinvention, and the claimed novelty is the combination.

## What a Conky design must supply

The source leaves these open. A Conky use of the idea has to build them, or say it does not:

- **A scale for magnitudes.** The anchors are discrete situational facts, not points along a gradient such as time or severity. Nothing in the source places a number on a scale.
- **Anchors that carry meaning.** Whether named, familiar anchors help a model, against opaque ones, is the untested experiment. A design relying on familiar anchors rests on an untested hypothesis.
- **A placement that is not asked of a model.** Section 11 shows ratings measure compliance. A placement computed by a pure rule needs no rating.
- **Who writes and revises the anchors.** The 45 were written by hand, and calibration of their order is named as the next lever.
- **Evidence in place of testimony.** The source asks for anchors derived from real probes. Conky's measures and history are such probes for a vault.
- **Anything about emotion.** The source is silent on it.
