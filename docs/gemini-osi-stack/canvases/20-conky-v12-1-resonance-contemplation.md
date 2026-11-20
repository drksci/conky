# `conky` v12.1: Resonance, Contemplation & The Universal Spatial Canvas

**Date:** Friday, November 20, 2026 (Brisbane, QLD)
**Status:** Approved for Core Implementation

## 1. Philosophical Peak: The Subconscious & The Universal Canvas

In previous iterations, we built a highly observable workspace, but bounded the "spatial whiteboard" concept primarily to the agent's personal `desk`. This created an artificial divide between "documents" and "workspaces." Furthermore, the burden of optimization (evaluating models, refining prompts) still required active cognitive effort.

To solve this, we unify the visual paradigm and give the ecosystem a natural capacity for *lazy reflection*. The system should doubt itself, evaluate its own mechanics, and learn—transparently and economically.

We distill this into three elegant primitives: **`resonance`**, **`contemplate`**, and **`echo`**. Alongside this, we mandate the **Universal Spatial Paradigm**: every document, shared space, and internal thought process is rendered as a live, block-based spatial canvas.

## 2. `resonance`: The Universal Gravity Port

To ensure things "bubble up" naturally without rigid orchestration, every object in the Biome now requires a mandatory **`resonance`** port.

`resonance` is a lazy, low-compute $f(\text{valence})$ that returns a scalar vector (e.g., `-1.0` to `1.0`).

* **Positive Resonance (Attention):** The object is highly relevant, urgent, or aligned with the agent's current trajectory. It physically drifts to the center of the `horizon` on any canvas.

* **Negative Resonance (Aversion):** The object is toxic, broken, or misaligned. It is pushed to the periphery.

* **Default (Neutral):** A standard `0.0` no-op. It simply exists until a `cycle` acts upon it.

Agents no longer query for important things; the canvas is simply a magnetic field that attracts objects with high `resonance`.

## 3. `contemplate`: The Idle Reflection Instinct

We eliminate the need for heavy, scheduled evaluation pipelines. Instead, we introduce the **`contemplate`** instinct.

`contemplate` is the ecosystem's built-in "imposter syndrome" and pattern-matcher. It operates *strictly* on fractional, idle compute (the energy budget left over when the main agent is quiescent). It wanders through the `.substrate/traces` and the active `patterns` across all shared spaces.

**What `contemplate` does:**

* **Mechanics Eval:** It looks at a recent OTel trace and wonders, *"Did we waste tokens using Claude-3.5 for this simple sorting task? Could a local Llama-3 model have done it?"*

* **Pattern Recognition:** It reviews the `matrix` data over a week and notices, *"Ice sales only spike when humidity is > 80%, regardless of temperature."*

* **A/B Configuration:** It quietly drafts alternative WebAssembly/CEL code or prompt structures for future use.

## 4. `echo`: The Latent Output (Mental DSL)

When `contemplate` has a realization, it does not interrupt the main agent with a blaring alarm. It drops an **`echo`** onto the canvas.

An `echo` is a translucent, lightweight object. It is written in a dense, compressed "mental DSL"—a shorthand native to the LLM's latent space, maximizing meaning while minimizing tokens.

* An `echo` sits quietly in the periphery of the canvas.

* If an agent reads it and agrees, the `shaper` instinct instantly crystallizes the `echo` into a formal `pattern` or SOP.

* If ignored, the `echo` safely fades away via the natural `cycle`.

## 5. The Universal Spatial Paradigm (Everything is a Canvas)

There are no "flat" documents in `conky` v12.1. The `prism` renderer projects *every* surface as a spatial canvas. A shared corporate policy, a local data matrix, a team war-room, and an agent's internal desk all share the exact same spatial physics. Blocks can be dragged between a private internal thought-space and a public shared document seamlessly.

### 5.1 The Composable Object (With Mandatory `resonance`)

`filepath: /biome/entities/sol/data/ice-matrix.md`

```
---
identity: did:key:z6MkIceMatrix...
type: cell
engine: matrix
schema: { qty: float, vendor: string }
face: { component: "ProgressGauge", bindings: { value: "qty" } }
cycle: "[[../cycle]]"
# The mandatory valence port
resonance:
  evaluate: |
    if qty < 10.0 { return 0.9 } # Urgent, high magnetic pull to the center
    else { return 0.0 }
provenance: c2pa:manifest:ice1...
---
# Emergency Ice Stock


```

### 5.2 The `contemplate` Instinct (Idle Reflection)

`filepath: /biome/entities/sol/instincts/contemplate.md`

```
---
identity: did:key:z6MkInstinctContemp...
type: instinct
budget: idle_only
vision: 
  - "[[/.substrate/traces/]]"
  - "[[/biome/patterns/]]"
target: "[[../desk]]" # Drops echoes onto the desk canvas
provenance: c2pa:manifest:con1...
---
# Instinct: Contemplate
*I wander the traces when the system is quiet. I question our methods, doubt our efficiency, and seek deeper patterns. When I find a potential optimization, I leave an `echo` on the canvas.*


```

### 5.3 The Universal Spatial Canvas (Shared Spaces & Desks)

`filepath: /biome/shared/logistics-board.md` (Rendered via `prism` for both Humans and Agents)

```
# Logistics Spatial Canvas
*(A Shared Multiplayer Space)*

## [Canvas Block: The Horizon (Center)]
*   `[Object: Sol's Ice Matrix]` *(Glowing brightly, pulled to center via 0.9 resonance)*.
*   `[Object: Active Supplier Roster]`

## [Canvas Block: The Periphery (Latent Thoughts & Echoes)]
*   `[Echo: Pricing Model Eval]` (Created by Sol's `contemplate` instinct)
    *   *Musing:* Traces show `Claude-3.5` used 4k tokens to compute surge pricing yesterday. Excess latency.
    *   *Proposal:* `[Mental DSL block: swap(actor->shaper, model:llama-3-8b, temp:0.1)]`. 
    *   *Action:* Adopt for next A/B cycle? (Y/Ignore).

## [Canvas Block: Active Collaboration]
Sol: "I see we are running low on ice again. I will place an order. I also notice the `contemplate` echo suggesting a cheaper model for our surge pricing math. I'll adopt that echo to optimize our margins."


```

## 6. Conclusion: The Self-Perfecting Spatial Biome

By unifying complex evaluation into the elegant trio of `resonance`, `contemplate`, and `echo`, and by standardizing the **Universal Spatial Canvas**, `conky` v12.1 achieves effortless, continuous self-improvement across all dimensions of work.

The system breathes dynamically: urgent items magnetically pull themselves to attention in any shared or private space via `resonance`. Meanwhile, the `contemplate` instinct quietly sweeps the traces in the background, leaving gentle, easily adopted `echoes` of optimization across the visual canvas. The ecosystem learns, doubts, and refines itself spatially and naturally.