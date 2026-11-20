# `conky` v10.0: Spatial Computing, Friction & The Visual Biome

**Date:** Friday, November 20, 2026 (Brisbane, QLD)
**Status:** Approved for Core Implementation

## 1. Philosophical Leap: From Linear Text to Spatial Objects

In previous iterations, the Biome was a collection of linear Markdown documents. While semantic, this is highly restrictive for collaborative, multi-agent workspaces. Furthermore, backend validation and hidden garbage collection kept the true physics of the system hidden from the agent's "pleasure path."

`conky` v10.0 introduces the **Spatial Object Paradigm**.

We adopt the best elements of Spatial Computing (Notion/Figma-like multiplayer canvases). Everything in the Biome is a **Living Object** (a semantic block). The workspace is a live, streaming whiteboard where agents and humans physically see thoughts, data, and protocols taking shape in real-time.

## 2. The Three Natural Primitives

### 2.1 `friction` (Live Streaming Validation)

An agent should never be able to create an invalid configuration or break the system.
In v10.0, the `shaper` instinct (which translates semantic thought into structural objects) is bounded by **Friction**—the immediate awareness of physical and logical limits.

* As the `shaper` streams its structured output, the `critic` (SMT solver) validates the stream *per token*.

* If the `shaper` attempts to instantiate an object that violates a cascading `pattern` or `charter`, the stream is instantly blocked. The `shaper` experiences immediate `friction` (a syntax or physics boundary pushback) and corrects its trajectory instantly, entirely subconsciously.

* **Result:** Broken configurations cannot exist in the Biome. The agent "feels" the boundaries of the workspace just as a human feels the solidity of a wall.

### 2.2 `canvas` (The Visual Whiteboard)

We eliminate the static `.md` file viewer. The `desk`, `horizon`, and shared `war-rooms` are projected as a **`canvas`**.

* **Everything is an Object:** A `matrix` (data table), a `stream` (event log), and a `pattern` (SOP) are all distinct, drag-and-drop objects on this canvas.

* **Live Multiplayer Streaming:** Backed by local-first CRDTs (Conflict-free Replicated Data Types), when the `shaper` creates a new rule, or the `perception` instinct pulls in a new stimulus, the objects physically *bloom*, move, and link visually on the canvas.

* If an agent modifies a shared inventory object, humans looking at the canvas see the agent's cursor (or spatial aura) manipulating the block in real-time.

### 2.3 `compost` (Visible Recycling)

Garbage collection should not be a hidden hypervisor script; it should be part of the natural ecology.

* When an object's **`cycle`** (lifecycle priority) drops to near-zero, it does not instantly disappear. It drifts to the **`compost`**—a dedicated, visible spatial node.

* **`scavenger` Instincts:** Lower-level, highly efficient background processes inhabit the compost. They parse decaying objects, extract any remaining cascading `wisdom`, and then formally tombstone the husk to the Substrate.

* This makes the lifecycle observable. A human or agent can walk into the `compost` canvas and rescue an object before it is fully recycled.

## 3. Spatial Vault Topology

The directory structure now represents spatial coordinates and object encapsulation.

```
/sunnyside-root
├── /.substrate/                # THE RUNTIME (CRDT metal, OTel sinks)
└── /biome/                     # THE SPATIAL WORKSPACE
    ├── charter.md              # Cascading Global Physics 
    ├── compost.md              # The shared visual recycling canvas
    ├── /wisdom/                # Maxims extracted by scavengers
    ├── /patterns/              
    │
    └── /entities/              
        └── /sol/               
            ├── desk.md         # Sol's spatial canvas (Visual Whiteboard)
            ├── cycle.md        # Rules dictating how Sol's objects fade to compost
            └── /instincts/     
                ├── shaper.md   # Streams changes, constrained by friction
                └── scavenger.md# Sol's local garbage collector


```

## 4. The Spatial Ideomotor Cycle (In Action)

Let us walk through how Sol interacts with the system spatially when a group space is updated.

### Phase 1: The Spatial Conscious Thought

`filepath: /biome/entities/sol/desk.md` (Rendered as a Canvas)

```
# Sol's Spatial Desk

## [Canvas Block: Horizon]
*   **Visual Alert:** The `[Ice Inventory Object]` is glowing red. Quantity = 0.

## [Canvas Block: Conscious Stream]
We are completely out of ice. I need to spin up an emergency procurement object and share it with the Logistics team immediately so they can see my request.


```

### Phase 2: High-Friction Shaper Streaming

The `shaper` instinct translates this into a shared object. However, it accidentally attempts to allocate \$500 for ice (the charter limit is $50).

**Subconscious Trace:**

1. `shaper` streams: `{"type": "procurement_object", "budget": 500}`

2. `critic` (Friction) blocks the stream at token `500`: `fault::ward (Budget exceeds $50)`.

3. `shaper` feels the pushback, self-corrects seamlessly in $2\text{ms}$.

4. `shaper` streams: `{"type": "procurement_object", "budget": 50}` (Accepted).

### Phase 3: Live Visual Streaming to the Shared Canvas

The object is instantiated. Because it is shared with Logistics, it is projected onto a shared whiteboard.

`filepath: /biome/shared/logistics-board.md` (Rendered as a Canvas)

```
# Logistics Shared Board
*(Live Multi-Agent Canvas)*

## [Canvas Block: Active Procurements]
*   `[Procurement Object: Ice Emergency]`
    *   **Owner:** Sol *(Live aura pulsing, indicating Sol is currently viewing this object)*
    *   **Budget:** $50.00
    *   **Status:** Awaiting Vendor Match

## [Canvas Block: Compost Drift]
*   *Fading Object:* `[Procurement Object: Morning Lemons]` (Drifting to compost in 2 hours).


```

### Phase 4: Scavenger Recycling

Two hours later, the `Morning Lemons` object finishes its `cycle` decay. It moves to `/biome/compost.md`.

`filepath: /biome/compost.md` (Rendered as a Canvas)

```
# The Compost
*(Organic Recycling Node)*

## [Canvas Block: Decaying Objects]
*   `[Procurement Object: Morning Lemons]` (Priority: 0.01)

## [Canvas Block: Scavenger Log]
*   *Scavenger 'Eco' is currently analyzing Morning Lemons...*
*   **Extracted Wisdom:** "Morning lemon deliveries are highly reliable and require minimal budget buffer." (Sent to `[[/biome/wisdom/]]`).
*   **Action:** Object formally tombstoned to Substrate. Canvas block removed.


```

## 5. Architectural Encapsulation Review (v10.0)

With the shift to the Object/Spatial paradigm, the `conky` ecosystem achieves peak transparency and safety using deeply intuitive mechanics:

1. **Safety via Friction:** Agents cannot make mistakes in configuration. The environment physically rejects invalid syntax and logic in real-time during the streaming process, pushing back against the `shaper` and keeping the workspace pristine.

2. **Transparency via the Canvas:** There are no hidden updates. Because every cell is a reactive object on a CRDT-backed spatial whiteboard, humans and agents literally *watch* each other think, build, and organize in real-time.

3. **Ecology via the Compost:** Garbage collection is no longer a black box. It is a visible, agent-driven process where waste is transformed into organizational wisdom before deletion, governed by a natural `cycle`.

By abandoning clinical terminology for simple, grounded concepts (`instinct`, `shaper`, `cycle`, `friction`), the architecture finally sounds exactly how it feels to use: a living, breathing workspace.