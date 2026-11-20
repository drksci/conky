# `conky` v4.0: Unified Cognitive Architecture & Open Standards

**Date:** Friday, November 20, 2026
**Status:** Approved for Core Implementation

## 1. Executive Summary & Literature Grounding

To scale the architecture for open-source enterprise adoption, we have refined the `conky` lexicon. We have eliminated cryptic abbreviations, mapped our concepts to standardized cognitive architecture research (such as Active Inference and Cognitive Architectures for Language Agents), and adopted global web standards for identity, provenance, and data querying.

The core paradigm remains unchanged: **The Document *Is* the Compute.** The entire system is a living, version-controlled Obsidian vault powered by a WebAssembly hypervisor, but it now speaks the language of modern cognitive science and enterprise standards.

## 2. The Refined Lexicon: Full Terms, Zero Abbreviations

Every component is named with an intuitive, non-abbreviated term.

### 2.1 Core Systems & Topologies

| Previous Term | New `conky` Term | Origin / Definition | 
| ----- | ----- | ----- | 
| `crest` / `node` | **`identity`** | Adopts the W3C Decentralized Identifier standard (`did:key:...`). | 
| `surface` / `context` | **`context`** | The bounded working memory document (Markdown). | 
| `anchor` / `link` | **`edge`** | Graph theory; bidirectional transclusions and pointers. | 
| `seal` / `hash` | **`provenance`** | Cryptographic state checkpoint using Coalition for Content Provenance formats. | 

### 2.2 The Perception-Action Cycle

| Previous Term | New `conky` Term | Cognitive Lineage | 
| ----- | ----- | ----- | 
| `peek` | **`attend`** | Attention mechanism; a focused, immediate read of a specific edge. | 
| `watch` | **`sense`** | Active inference perception; asynchronous subscription to state changes. | 
| `etch` | **`act`** | Action space; mutating the environment/state. | 

### 2.3 Environmental Fields & Cognitive Forces

| Previous Term | New `conky` Term | Cognitive Lineage | 
| ----- | ----- | ----- | 
| `aura` | **`stimulus`** | External environmental signal (e.g., weather, market pressure). | 
| `drive` | **`drive`** | Internal homeostatic pressure (novelty, urgency). | 
| `focus` | **`attention`** | Computed scalar (`stimulus` × `drive`) driving model tiering. | 

### 2.4 Engines (WebAssembly Capsules)

| Previous Term | New `conky` Term | Cognitive Lineage | 
| ----- | ----- | ----- | 
| `mind` / `actor` | **`actor`** | The probabilistic policy engine (Large Language Model). | 
| `expert` / `lobe` | **`faculty`** | A highly scoped, specialized subconscious cognitive loop. | 
| `gear` | **`tool`** | Deterministic function (WebAssembly). | 
| `organ` | **`memory`** | Long-Term Memory (Graph databases). | 
| `guard` | **`critic`** | Provable validator evaluating the `context`. | 
| `view` | **`interface`** | Declarative streaming projection for human operators. | 

### 2.5 Active Inference Dynamics

| Previous Term | New `conky` Term | Cognitive Lineage | 
| ----- | ----- | ----- | 
| `pulse` | **`step`** | Discrete time-step / micro-frame streaming. | 
| `arc` / `traj` | **`trajectory`** | A sequence of states/actions executing over time. | 
| `telos` | **`target`** | Target state vector; the goal the trajectory minimizes toward. | 
| `tension` | **`entropy`** | Expected Free Energy; divergence between current state and `target`. | 
| `fade` | **`decay`** | Weight decay; un-stepped trajectories naturally drop in priority. | 
| `dream` | **`replay`** | Contextual Experience Replay; off-policy self-reflection and learning. | 
| `lens` | **`probe`** | Auto-extracts scalar metrics from raw states. | 

## 3. Nested `faculty` Cells (Cellular Organelles)

Instead of cluttering the vault with dozens of micro-documents for every subconscious thought, a **`faculty`** is now biologically nested *within* an `actor` cell.

Think of the `actor` document as the biological cell, and the `faculty` definitions as its organelles. They share the same `identity` but run continuous, parallel, cheap reflex loops in the background.

```
# Inside vault/sol.md (The Actor Cell)
faculties:
  - name: "doubt"
    model: "fast-reflex"
    vision: "![[sol#proposed_action]]"
    trigger: "proposing"
  - name: "factuality"
    model: "fast-reflex"
    vision: "![[chat#latest_message]]"
    trigger: "received_stimulus"

```

These nested faculties inject their findings directly into the parent cell's `context`, modulating its `entropy` and `attention` without requiring complex cross-document orchestration.

## 4. Open Standards: Identity & Provenance

Reinventing cryptographic signatures creates friction. `conky` v4.0 natively adopts global standards for verifiable compute.

* **W3C Decentralized Identifiers:** Every document and agent identity is now a standardized DID (e.g., `did:key:z6MkhaXgBZDvotDkL5257faiztiuC2ZXrM`). This allows agents to natively interact with external enterprise systems, sign verifiable credentials, and participate in global federations.

* **Coalition for Content Provenance (C2PA):** Instead of a custom `seal`, every Git commit and state mutation generates a standardized C2PA provenance manifest. This ensures that every action taken by an AI is cryptographically traceable, watermark-compatible, and legally verifiable by third-party auditors.

## 5. Mainstream Graph Querying (GraphQL & openCypher)

Raw SQL (via DuckDB) is misaligned with a document-centric graph ecosystem. We are transitioning `memory` and `probe` primitives to natively support **GraphQL** (for contextual state projection) and **openCypher** (for deep graph traversal).

* **GraphQL:** Agents define `probe` documents using GraphQL to pull exact metric shapes from the mesh. It is naturally understood by Large Language Models, returning clean JSON structures.

* **openCypher:** For complex multi-agent relationships (e.g., tracing a circular debt loop), agents can execute standard Cypher queries: `MATCH (a:Actor)-[:OWES]->(b:Actor) RETURN a, b`.

## 6. Example: The Bonded Triad (v4.0 Syntax)

### Truth (`vault/ledger.md`)

```
---
identity: "did:key:z6MkLedger..."
engine: "memory"
critic: "[[critic-ledger]]"
interface: "[[interface-ledger]]"
settle: "quiescent"
vaults:
  funds: 184.50
  compute: 4.82
provenance: "c2pa:manifest:a41c..."
---
# Universal Ledger
Net Funds: **+$134.50** | Compute Budget: **$4.82**

```

### Law (`vault/critic-ledger.md`)

```
---
identity: "did:key:z6MkCritic..."
engine: "critic"
target: "[[ledger]]"
fuel: 5000
proof: "certificate:satisfiability_modulo_theories:89f3c..."
code: |
  evaluate:
    post.vaults.funds >= 0.0 &&
    ledger.is_balanced_parity == true
provenance: "c2pa:manifest:55b1..."
---
# Critic: `[[ledger]]`
Formally verified validator enforcing zero-sum parity.

```

### The $f(x)$ Measurement (`vault/probe-margin.md`)

```
---
identity: "did:key:z6MkProbe..."
engine: "probe"
source: "[[ledger]]"
query: |
  graphql:
    query {
      ledger {
        transactions(unit: "funds") {
          sum(field: "shift")
        }
      }
    }
provenance: "c2pa:manifest:1b7a..."
---
# Probe: Real-Time Margin
**Current Net Margin:** +$134.50

```