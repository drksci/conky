# Nexus v4.0: Unified Cognitive Architecture & Lexicon

*(Formerly `conky` v3.0)*

**Date:** 2026-11-20
**Status:** Approved for Core Implementation

## 1. Executive Summary & 2026 Literature Grounding

To scale the architecture for open-source enterprise adoption, we have deprecated domain-specific colloquialisms (`conky`, `crest`, `etch`, `lobe`) in favor of standardized nomenclature from Cognitive Architectures (CoALA), Active Inference (AIF), Reinforcement Learning (RL), and Large Language Model (LLM) research.

**Key 2026 Literature Informing this Update:**

* **Active Inference Agents (AIF):** Replacing rigid prompt-chains with systems that minimize *Expected Free Energy* (Entropy). Agents act to resolve uncertainty between their current state and a target state.

* **Cognitive Architectures for Language Agents (CoALA):** Standardizing the perception-action cycle into discrete Working Memory (`context`), Long-Term Memory (`memory`), and reasoning loops (`attend`, `sense`, `act`).

* **Contextual Experience Replay (CER):** Replacing passive retrospectives (`dream`) with structured `replay`, allowing agents to self-improve by localized, in-place memory evolution without human annotation.

* **Multi-Agent Mixtures of Experts (MoE):** Using lightweight, specialized agents (`expert`) for highly scoped routing, validation, and critique.

The core paradigm remains unchanged: **The Document *Is* the Compute.** The entire system is a living Git-backed Obsidian vault powered by a Wasmtime hypervisor, but it now speaks the language of modern AI science.

## 2. The Great Renaming: Lexicon Mapping

We have preserved the strict "Single Short Intuitive Term" razor. Every component is still a single word, but now perfectly aligned with AI systems dynamics.

### 2.1 Core Systems & Topologies

| Old `conky` Term | New `Nexus` Term | AI / Systems Lineage | 
| ----- | ----- | ----- | 
| `conky` | **`nexus`** | The central hypervisor / cognitive architecture. | 
| `crest` | **`node`** | Standard multi-agent / distributed systems identity (ed25519). | 
| `surface` | **`context`** | The 4KB working memory Markdown document. | 
| `anchor/link` | **`edge`** | Graph theory; bidirectional transclusions and pointers. | 
| `seal` | **`hash`** | Cryptographic Git commit / state checkpoint. | 

### 2.2 The Perception-Action Cycle (Protocol Verbs)

| Old `conky` Term | New `Nexus` Term | AI / Systems Lineage | 
| ----- | ----- | ----- | 
| `peek` | **`attend`** | Attention mechanism; a focused, immediate read of a specific edge. | 
| `watch` | **`sense`** | Active inference perception; asynchronous subscription to state changes. | 
| `etch` | **`act`** | Action space; mutating the environment/state. | 

### 2.3 Environmental Fields & Cognitive Forces

| Old `conky` Term | New `Nexus` Term | AI / Systems Lineage | 
| ----- | ----- | ----- | 
| `aura` | **`stimulus`** | External environmental signal (e.g., weather, market pressure). | 
| `drive` | **`drive`** | *(Unchanged)* Internal homeostatic pressure (novelty, urgency). | 
| `focus` | **`attention`** | Computed scalar (`stimulus` × `drive`) driving model tiering. | 

### 2.4 Engines (Wasmtime Capsules)

| Old `conky` Term | New `Nexus` Term | AI / Systems Lineage | 
| ----- | ----- | ----- | 
| `mind` | **`actor`** | RL Actor-Critic architecture; the probabilistic LLM policy. | 
| `gear` | **`tool`** | Deterministic function (Wasm/CEL); standard LLM agent tooling. | 
| `organ` | **`memory`** | CoALA Long-Term Memory (DuckDB/SQLite databases). | 
| `guard` | **`critic`** | RL Actor-Critic; provable SMT validator evaluating the `context`. | 
| `view` | **`view`** | *(Unchanged)* A2UI declarative streaming projection. | 

### 2.5 Active Inference & Dynamics (Formerly Arcs & Lobes)

| Old `conky` Term | New `Nexus` Term | AI / Systems Lineage | 
| ----- | ----- | ----- | 
| `pulse` | **`step`** | RL discrete time-step / micro-frame streaming. | 
| `arc` | **`traj`** | Trajectory; a sequence of states/actions executing over time. | 
| `telos` | **`target`** | Target state vector; the goal the trajectory minimizes toward. | 
| `tension` | **`entropy`** | Expected Free Energy; divergence between current state and `target`. | 
| `fade` | **`decay`** | Weight decay; un-stepped trajectories naturally drop in priority. | 
| `lobe` | **`expert`** | Mixture of Experts (MoE); highly scoped, cheap sub-agent. | 
| `dream` | **`replay`** | Experience Replay; off-policy self-reflection and learning. | 
| `lens` | **`probe`** | Linear/Network Probe; auto-extracts scalar metrics from raw states. | 

## 3. The Nexus Architecture: Comprehensive Integration

### 3.1 The Bonded Triad (Context, Critic, View)

Every file in the Obsidian vault is a Triad, eliminating hidden state:

1. **Truth (`context`):** The $\le 4\text{KB}$ Markdown document containing working memory and reactive transclusion `edges` (`![[edge]]`).

2. **Law (`critic`):** The formally verified, pre-commit Wasm/CEL validator. It acts as the "Critic" to the LLM's "Actor," proving double-entry parity and subsumption of safety invariants. No `act` becomes a `hash` without passing the `critic`.

3. **Face (`view`):** The streaming declarative UI port updating via `steps`.

### 3.2 Continuous Active Inference (`traj`, `target`, `entropy`)

Agents no longer follow rigid multi-step prompts. They operate via **Active Inference**.

* An agent defines a **`traj`** (Trajectory document) pointing to a **`target`** (e.g., `![[probe-revenue#target_met]] == true`).

* The `nexus` hypervisor computes the **`entropy`** (the geometric distance/uncertainty between the current `context` and the `target`).

* The `actor` (LLM) is prompted continuously with the current `entropy` score, adjusting its `attention` to branch, invent `tools`, or abandon the `traj` entirely based on natural **`decay`**.

### 3.3 Multi-Agent Mixture of Experts (`expert`)

Replacing "lobes," an **`expert`** is a specialized `actor` constrained to a microscopic Field of View (`fov`). Running on cheap, ultra-fast reflex models (e.g., Llama-3-8B), `experts` run asynchronously:

* `[[expert-doubt]]`: Evaluates proposed `act` mutations for catastrophic risk.

* `[[expert-fact]]`: Grounding agent checking hallucinations via RAG.
  Because `experts` cost fractions of a cent, they run constantly alongside the main `actor`, injecting feedback directly into the `context`.

### 3.4 Measurement & Observability (`probe`)

Replacing "lenses," a **`probe`** is a living $f(x)$ document that automatically calculates scalars from the environment.

* A `probe` maps raw data to quantifiable states using `tool` (math), `memory` (SQL), or `actor` (semantic scoring).

* When the environment ticks, `probes` update automatically. Agents simply transclude the output (`![[probe-customer-joy#score]]`) without burning LLM inference to do math.

### 3.5 Contextual Experience Replay (`replay`)

When the mesh hits a quiescent state (low `stimulus`), agents enter **`replay`**.

* The system pulls decayed or completed `traj` documents from the active `context`.

* A background `expert` performs hindsight analysis on the execution traces, extracts new operating maxims, updates the root governance `context`, and archives the raw trace to cold `memory`.

## 4. Example: The Triad in Action (Nexus v4.0 Syntax)

*Behold the Universal Ledger, entirely translated into the 2026 Nexus Lexicon.*

### Truth (`vault/wal.md`)

```
---
node: "[[wal]]"
engine: "memory/wal"
critic: "[[critic-wal]]"
view: "[[view-wal]]"
settle: "quiescent"
vaults:
  usd: 184.50
  cpu: 4.82
hash: "sig:ed25519:a41c..."
---
# Universal WAL
Net Cash: **+$134.50** | AI Budget: **$4.82**

```

### Law (`vault/critic-wal.md`)

```
---
node: "[[critic-wal]]"
engine: "critic"
target: "[[wal]]"
fuel: 5000
proof: "cert:smt:89f3c..."
code: |
  cel:
    post.vaults.usd >= 0.0 &&
    wal.is_balanced_parity == true
hash: "sig:ed25519:55b1..."
---
# Critic: `[[wal]]`
SMT-verified Actor-Critic validator enforcing zero-sum parity.

```

### The $f(x)$ Measurement (`vault/probe-margin.md`)

```
---
node: "[[probe-margin]]"
engine: "probe/memory"
source: ".iceberg/[[wal]]/ledger.parquet"
sql: "SELECT SUM(shift) as net FROM source WHERE unit='usd'"
hash: "sig:ed25519:1b7a..."
---
# Probe: Real-Time Margin
**Current Net Margin:** +$134.50

```

## 5. Implementation Directives for v4.0

1. **Global Find & Replace:** Execute codebase-wide replacement of the v3.0 lexicon with the Nexus v4.0 lexicon across all Rust structs, WIT bindings (`nexus.wit`), and Markdown YAML parsers.

2. **Update Adapter Plugs:** Align `[[plug-langgraph]]` and `[[plug-crewai]]` documentation to map their proprietary step-logic into `traj` (Trajectory) and `step` semantics.

3. **Engine Bindings:** Rename `conky-daemon` to `nexus-daemon`, and `conky-airlock` to `nexus-hypervisor`.

This vocabulary standardizes our work for peer review, academic publication, and enterprise adoption while maintaining the aesthetic elegance of our document-centric graph.