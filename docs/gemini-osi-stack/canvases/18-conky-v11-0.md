# `conky` v11.0: The Omnimodal Canvas, Loom, & Prism Rendering

**Date:** Friday, November 20, 2026 (Brisbane, QLD)
**Status:** Approved for Core Implementation

## 1. Philosophical Peak: Omnimodal Observability

In previous iterations, we built a spatial whiteboard (the `canvas`), but left the actual rendering mechanics abstract. If every object (from a `matrix` to a `compost` pile) is a living spatial entity, how is it organized into a cohesive interface? Furthermore, if humans get a beautiful, interactive UI, how do agents "see" it? Forcing agents to read raw database tables while humans get dashboards breaks the symmetry of the shared workspace.

`conky` v11.0 introduces **Omnimodal Observability**.

We apply the reductionist razor to UI generation: What You See Is What The Agent Sees (WYSIWTAS). We achieve this through three new structural primitives that compile declarative logic into deterministic, highly optimized streaming code.

## 2. The Three Rendering Primitives

| Primitive | Biological/Physical Analog | Definition & Mechanics | 
| ----- | ----- | ----- | 
| **`face`** | Expression / Appearance | An A2UI (Agent-to-UI) port attached to *every* object in the Biome. It defines the declarative visual shape of the object (e.g., a chart, a glowing alert, a compost bin). | 
| **`loom`** | The Weaver / Compositor | A namespaced compositor engine. It takes a collection of `face`s, organizes them spatially on a `canvas`, and **compiles them into runnable, deterministic WebAssembly streaming code**. | 
| **`prism`** | The Dual Projector | The endpoint that splits the `loom`'s compiled stream. It projects a WebGL/React GUI for humans, and an optimized, semantic text-DOM (SDOM) for the agent's LLM vision. | 

## 3. The `face` Port: Everything is Visible

To ensure encompassing observability, every cell must have a `face`.

* A `matrix` (inventory data) has a `face` that renders as a streaming sparkline or data table.

* The `scavenger` instinct has a `face` that renders as a pulsing activity log showing what it is currently recycling.

* The `friction` physics rule has a `face` that flashes red when an agent hits a boundary constraint.

By default, if an agent authors a new object, the hypervisor automatically infers a default `face` based on its data schema.

## 4. The `loom`: Deterministic UI Compilation

UIs in the Biome are not static HTML files. They are live, streaming, addressable surfaces managed by a **`loom`**.

* **Addressable Namespaces:** A `loom` is just a file (e.g., `/biome/shared/logistics-loom.md`).

* **Compilation & Streaming:** When the `loom` file is updated (e.g., an agent drags a new object onto the canvas), the Substrate instantly intercepts the YAML, frames the components, and compiles optimized, deterministic Rust/Wasm code.

* **Zero-Latency Updates:** This compiled code manages the delta-streaming over WebSockets/WebRTC, ensuring the UI pushes updates at 60fps without overwhelming the network.

## 5. The `prism`: Agents Looking at Screens

The most profound shift is the **`prism`**. To ensure agents are truly grounded in the exact same reality as their human operators, they must perceive the same environment.

When an agent "looks" at a `loom`, the `prism` renders the streaming UI into an optimized **Semantic Document Object Model (SDOM)**.

Instead of reading a raw JSON dump of 10,000 inventory events, the agent "reads" the visual dashboard:
*> \[PRISM VIEW: Logistics Board\]*
*> \[Top Left\] Inventory Sparkline: Trending sharply downwards. Current: 5 units.*
*> \[Center\] Active Procurements: Sol's Emergency Ice Order (Status: Pending).*

Because the agent reads the exact same dashboard the human sees, Hallucination via Translation is eliminated. If a human points to the "Top Left Chart," the agent knows exactly what that means.

## 6. Spatial Topology & Boilerplate

The directory structure seamlessly integrates the `loom` compositors as shared spatial environments.

```
/sunnyside-root
├── /.substrate/                
│   └── /compiled-looms/        # The compiled Wasm binaries driving the UI streams
│
└── /biome/                     
    ├── charter.md              
    ├── compost.md              # Has a default 'face' showing decaying objects
    │
    ├── /shared-spaces/         # Addressable public canvases
    │   └── logistics-loom.md   # The compositor framing the logistics UI
    │
    └── /entities/              
        └── /sol/               
            ├── desk-loom.md    # Sol's personal compositor
            └── /data/          
                └── ice-matrix.md # Contains a 'face' port

```

### 6.1 The Composable Object with a `face`

`filepath: /biome/entities/sol/data/ice-matrix.md`

```
---
identity: did:key:z6MkIceMatrix...
type: cell
engine: matrix
schema: { qty: float, vendor: string }
face:
  component: "ProgressGauge"
  bindings: 
    value: "qty"
    max: 100.0
    color: "gradient(blue, red)"
provenance: c2pa:manifest:ice1...
---
# Emergency Ice Stock

```

### 6.2 The `loom` Compositor (The Frame)

`filepath: /biome/shared-spaces/logistics-loom.md`

```
---
identity: did:key:z6MkLogisticsLoom...
type: loom
layout: spatial_grid
engine: compositor/wasm
targets:
  - "[[/biome/entities/sol/data/ice-matrix#face]]"
  - "[[/biome/entities/luna/data/lemon-matrix#face]]"
  - "[[/biome/compost#face]]"
provenance: c2pa:manifest:loom1...
---
# The Logistics Board
*This compositor automatically stitches together the faces of our primary operational objects and compiles them into a streaming endpoint.*

```

### 6.3 The Agent's View (The `prism` SDOM Output)

When the agent `sol` queries `[[/biome/shared-spaces/logistics-loom]]`, it does not get raw code. The `prism` intercepts the query and feeds this live semantic string to the LLM's context window:

```
[PRISM LIVE RENDER: The Logistics Board]
(Layout: Grid, 3 Active Faces)

[Region: Top-Left | Target: Sol's Emergency Ice Stock]
- Visual: Progress Gauge (Color: Red, Critical)
- Value: 5.0 / 100.0

[Region: Top-Right | Target: Luna's Lemon Matrix]
- Visual: Progress Gauge (Color: Blue, Healthy)
- Value: 85.0 / 100.0

[Region: Bottom-Span | Target: Compost Drift]
- Visual: Fading Activity Log
- Items: 2 objects decaying.

```

## 7. Conclusion

By separating the visual intent (`face`) from the rendering engine (`loom`) and the viewer (`prism`), `conky` v11.0 achieves complete symmetry between human and agent perception. The system autogenerates optimized, deterministic streaming code for human GUIs, while instantly translating those same visual layouts into semantic spatial awareness for the agents. The Biome is now fully observable, fully interactive, and perfectly aligned across carbon and silicon minds.