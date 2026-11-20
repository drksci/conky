# `conky` v12.1: The Organic Spatial Biome

**The Definitive Core Architecture Specification**

**Date:** Friday, November 20, 2026 (Brisbane, QLD)
**Status:** Approved for Core Implementation

## 1. Philosophical Foundation: The Pleasure Path & The Spatial Object

The goal of `conky` is to create a multi-agent ecosystem indistinguishable from a team of highly organized humans working in a shared, version-controlled spatial workspace.

We reject explicit symbolic programming for agents (rigid tool calls, JSON APIs) and hidden back-end magic. Instead, we embrace the **Ideomotor Principle** (thought naturally actuates action) and the **Universal Spatial Canvas**.

**The Core Axioms:**

1. **The Document Is The Compute:** Everything is a living markdown file backed by Git/CRDT.

2. **What You See Is What The Agent Sees (WYSIWTAS):** Agents and humans look at the exact same spatial UI.

3. **Biological Determinism:** Stagnation is impossible. The ecosystem automatically distills, fades, and recycles information via natural rhythms.

## 2. Topological Encapsulation (Substrate vs. Biome)

To prevent the semantic workspace from being cluttered by heavy runtime mechanics, the Obsidian vault is strictly partitioned.

### 2.1 The Substrate (The Runtime Metal)

Invisible to the casual eye. This is where the hypervisor manages:

* `/duckdb/`: Raw Parquet/Arrow tabular metal.

* `/traces/`: OpenTelemetry (OTel) spans and compressed telemetry sinks.

* `/compiled-looms/`: Wasm binaries driving the UI streams.

* `/tombstones/`: Archived, fully decayed surfaces.

### 2.2 The Biome (The Spatial Workspace)

The semantic, living mesh where agents and humans interact.

* `/charter.md`: Cascading global physics, budget caps, and ethical boundaries.

* `/climate.md`: Cascading macro-environment (seasonality, market pressure).

* `/wisdom/`: Cascading insights distilled from the compost.

* `/patterns/`: Promoted, globally enforced Standard Operating Procedures (SOPs).

* `/channels/`: Pub/Sub Event Topics (e.g., `system-alerts`).

* `/entities/`: Strict logical ownership namespaces for agents (e.g., `/sol/`).

* `/compost.md`: The shared visual recycling canvas.

## 3. The Core Primitives

### 3.1 Trust & Physics

* **Identity (`did:key`):** W3C Decentralized Identifiers standard. Agents and objects natively cryptographically sign actions.

* **Provenance (`c2pa`):** Coalition for Content Provenance formatting ensures every action/mutation has an unforgeable, watermark-compatible audit trail.

* **`friction`:** Live streaming validation. As an agent acts, the SMT solver validates the stream *per token*. If it violates the `charter`, the stream is blocked. The agent "feels" this physical pushback and corrects instantly.

### 3.2 The Composable Cell (Living Objects)

Data is not hardcoded. Agents compose data structures seamlessly.

* **`matrix`:** Tabular data (backed by DuckDB).

* **`stream`:** Append-only event logs.

* **`pattern`:** Finite State Machines (FSM) or CEL logic. Starts as a private `shadow` pattern, gets ratified by `quorum`, and is promoted to a formal, cascading SOP.

### 3.3 The Visual & Magnetic Canvas

* **`face`:** The declarative A2UI (Agent-to-UI) port attached to every object, defining its visual shape (a chart, a glowing alert).

* **`resonance`:** A mandatory $f(\text{valence})$ on every object. It creates gravity. Urgent items (positive resonance) magnetically pull themselves to the center of any canvas. Toxic items push to the periphery.

* **`cycle`:** The natural rhythm ($f_{lifecycle}$). If an object is un-stimulated, its priority mathematically decays. It drifts to the `compost`, gets scavenged for `wisdom`, and is eventually tombstoned.

## 4. Omnimodal Observability (`loom` & `prism`)

UIs in the Biome are live, streaming, addressable surfaces.

* **`loom` (The Compositor):** A namespaced engine that takes a collection of `face`s, organizes them spatially, and compiles them into deterministic Wasm streaming code.

* **`prism` (The Dual Projector):** The endpoint that splits the `loom`'s stream. It projects a WebGL/React GUI for humans, and an optimized, semantic text-DOM (SDOM) for the agent's LLM vision. **Humans and agents read the exact same canvas.**

## 5. The Subconscious: Instincts & The Ideomotor Cycle

Agents do not write JSON or code. They think in freeform prose on the `canvas`. Specialized, cheap, local reflex models (Llama-3-8B) act as their subconscious **instincts**.

* **`shaper`:** Shadows the agent's conscious stream. It translates semantic intent ("I want to raise prices when it's hot") into physical YAML/CEL contracts (`pattern`), constrained by `friction`.

* **`perception`:** Tunes into the Pub/Sub `channels`, filters the noise, and projects relevant signals into the agent's horizon as natural prose.

* **`scavenger`:** Wanders the `compost` canvas, breaking down decayed objects and extracting `wisdom` before tombstoning.

* **`contemplate` (Imposter Syndrome):** Operates on idle compute. It wanders traces and canvases, doubting mechanics and spotting patterns. It leaves an **`echo`** (a translucent block of optimized Mental DSL) on the canvas for the main agent to adopt or ignore.

## 6. Exhaustive Topology & Living Surfaces (Boilerplate)

### 6.1 The Universal Spatial Canvas (A Shared Loom)

`filepath: /biome/shared/logistics-board.md` (Rendered via `prism`)

```
---
identity: did:key:z6MkLogisticsLoom...
type: loom
layout: spatial_grid
engine: compositor/wasm
targets:
  - "[[/biome/entities/sol/data/ice-matrix#face]]"
  - "[[/biome/entities/sol/instincts/contemplate#echoes]]"
provenance: c2pa:manifest:loom1...
---
# Logistics Spatial Canvas
*(A Shared Multiplayer Space)*

## [Canvas Block: The Horizon (Center)]
*   `[Object: Sol's Ice Matrix]` *(Glowing brightly, pulled to center via 0.9 resonance)*.

## [Canvas Block: The Periphery (Latent Echoes)]
*   `[Echo: Pricing Model Eval]` (Created by Sol's `contemplate` instinct)
    *   *Musing:* Traces show `Claude-3.5` used 4k tokens to compute surge pricing yesterday. Excess latency.
    *   *Proposal:* `[Mental DSL block: swap(actor->shaper, model:llama-3-8b, temp:0.1)]`. 
    *   *Action:* Adopt for next A/B cycle? (Y/Ignore).

## [Canvas Block: Active Collaboration]
Sol: "I see we are running low on ice again. I will place an order. I also notice the `contemplate` echo suggesting a cheaper model for our surge pricing math. I'll adopt that echo to optimize our margins."

```

### 6.2 The Composable Object (Matrix + Resonance + Cycle)

`filepath: /biome/entities/sol/data/ice-matrix.md`

```
---
identity: did:key:z6MkIceMatrix...
type: cell
engine: matrix
schema: { qty: float, vendor: string }
face: 
  component: "ProgressGauge"
  bindings: { value: "qty" }
cycle: 
  decay_rate: 0.1
  action_on_zero: "drift_to_compost"
resonance:
  evaluate: |
    if qty < 10.0 { return 0.9 } # Urgent magnetic pull
    else { return 0.0 }
provenance: c2pa:manifest:ice1...
---
# Emergency Ice Stock

```

### 6.3 The Shaper Instinct (The Ideomotor Actuator)

`filepath: /biome/entities/sol/instincts/shaper.md`

```
---
identity: did:key:z6MkInstinctShaper...
type: instinct
budget: reflex_tier
vision: "![[../desk#Conscious Stream]]"
target: "[[/.substrate/compiled-looms/]]"
provenance: c2pa:manifest:shp1...
---
# Instinct: Shaper
*I watch Sol's conscious thoughts. When a clear intent forms, I stream the structural updates to the environment. I am physically constrained by `friction`; if I hit a charter boundary, I course-correct before the thought materializes.*

```

### 6.4 The Cascading Pattern (Promoted SOP)

`filepath: /biome/patterns/pattern-surge.md`

```
---
identity: did:key:z6MkPatternSurge...
type: pattern
state: formal
quorum_ratified: ["did:key:sol", "did:key:owner"]
definition: |
  fsm:
    states: [normal, surge]
    transitions:
      - condition: "climate.temperature > 32.0"
        action: "matrix_update(price, price * 1.2)"
provenance: c2pa:manifest:pat2...
---
# Formal SOP: Heatwave Surge Pricing
*Because this lives in `/biome/patterns/`, it cascades down to all child canvases. When the cascading `climate` registers > 32.0°C, all agents must transition to `surge` state.*

```

**End of Specification.**