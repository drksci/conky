# `conky` v7.0: Composable Data, Cascading Patterns & The Unified Biome

**Date:** Friday, November 20, 2026 (Brisbane, QLD)
**Status:** Approved for Core Implementation

## 1. Philosophical Evolution: Dynamic Composition & Cascading Truth

Previous architectures relied on hardcoded domain concepts like `ledgers`. If an agent needed to track inventory, they had to use a pre-compiled `organ/wal`. This violated the "pleasure path" of autopoiesis. Furthermore, organizational knowledge was flat; agents operated in isolated bubbles, missing the overarching operational context of the enterprise.

`conky` v7.0 resolves these rigidities through two massive paradigm shifts:

1. **Schema-Driven Data Primitives:** We eliminate "ledgers." Data is simply a biological `cell` backed by a foundational engine (`matrix` for tabular, `stream` for timeseries, `surface` for semantic prose). The agent composes the *schema*, and the hypervisor enforces it.

2. **Cascading `pattern` Ports:** For behaviors, protocols, or Finite State Machines (FSMs), we introduce the `pattern` port. Patterns begin as local, private `shadow` experiments. Through consensus (`quorum`), they are promoted to higher levels of the Biome, cascading down to all child entities as inherited Standard Operating Procedures (SOPs).

3. **Transparent Lineage:** Crucial context—like `wisdom` (learned insights), `climate` (macro-environment), and `charters` (rules)—is never hidden. It cascades down the topological folder structure natively, entering the `horizon` of any subordinate agent.

## 2. Composable Data Cells (`matrix`, `stream`, `surface`)

An agent is no longer restricted to predefined tools. If an agent wants to track staff schedules, profitability, or sensor telemetry, it simply forges a new `cell` and defines its schema.

* **`engine: matrix`:** A tabular data cell (backed by DuckDB in the Substrate). The agent defines columns and types in the YAML.

* **`engine: stream`:** An event-log data cell for high-frequency telemetry.

* **`engine: surface`:** A semantic document for prose and graphs.

The hypervisor automatically projects these underlying data structures into elegant Markdown tables and charts in the Biome.

## 3. The `pattern` Port (Behaviors, FSMs, & SOPs)

When an agent discovers an efficient way of doing things (e.g., a specific sequence for batching lemonade during a heatwave), it shouldn't just exist as an ephemeral prompt response. It must be codified, tested, and shared.

Every composed cell can attach a **`pattern`** port. A `pattern` is a deterministic, provable definition (an FSM, a CEL logic tree, or a standard protocol).

### 3.1 The Pattern Promotion Lifecycle

Patterns evolve exactly like biological traits or corporate SOPs:

1. **Shadow (Private):** An agent drafts a `pattern` to optimize its own workflow. It is marked `state: shadow`. It applies *only* to the local entity and does not affect the broader ecosystem.

2. **Quorum (Evaluation):** The agent proposes the pattern to the network. Peer agents (or the `@owner` `gate`) evaluate its performance and ROI via a cryptographic `quorum` vote.

3. **Formal (Cascading SOP):** Upon consensus, the pattern is physically moved up the directory tree (e.g., from `/biome/entities/sol/` to `/biome/operations/`). Because it sits at a higher topological level, it **cascades** down, becoming a mandatory, inherited FSM for *all* agents operating under that branch.

## 4. Cascading Context (The Lineage of Truth)

In traditional systems, agents are blind to the "big picture" unless it is explicitly stuffed into their context window. In `conky` v7.0, the directory topology itself dictates contextual awareness.

Attributes declared in a parent directory automatically cascade down to child cells, populating their `horizon` intelligently.

* **`charter` (Boundaries):** The enterprise-wide budget cap cascades down to all regional managers.

* **`climate` (Macro-Environment):** A global recession or a city-wide heatwave is declared at the root `/biome/` level, seamlessly altering the `stimulus` of every child agent.

* **`wisdom` (Distilled Learnings):** When an agent's `replay` faculty distills a hard-learned lesson ("Ice suppliers delay deliveries on Fridays"), it is promoted to a cascading `wisdom` file, instantly priming the subconscious of all other agents.

## 5. Topological Encapsulation & The Workspace

The directory structure elegantly supports this inheritance and composition model.

```
/sunnyside-root
├── /.substrate/                # THE RUNTIME (Traces, DuckDB metal, OTel sinks)
└── /biome/                     # THE ORGANIC WORKSPACE
    ├── charter.md              # Cascading Master Physics (Global budget, ethics)
    ├── climate.md              # Cascading Macro-Environment (Seasonality, weather)
    ├── /wisdom/                # Cascading organizational maxims
    ├── /patterns/              # Promoted, global SOPs and FSMs
    │   └── pattern-surge.md    # Formal SOP for heatwave pricing
    │
    └── /entities/              
        └── /sol/               # Sol's local namespace
            ├── desk.md         # Sol's conscious context
            ├── /data/
            │   └── inventory.md # A local 'matrix' cell composed by Sol
            └── /patterns/      
                └── shadow-prep.md # A local, private FSM Sol is experimenting with


```

## 6. Exhaustive Boilerplate & Living Surfaces

### 6.1 The Composable Data Matrix

`filepath: /biome/entities/sol/data/inventory.md`

```
---
identity: did:key:z6MkMatrixInv...
type: cell
engine: matrix
schema:
  item: string
  qty: float
  unit: string
  cost_basis: float
metabolism: "[[../metabolism]]"
provenance: c2pa:manifest:inv1...
---
# Local Inventory Tracker
*Maintained dynamically by Sol.*

| item | qty | unit | cost_basis |
| :--- | :--- | :--- | :--- |
| lemons | 50.0 | lb | 1.20 |
| sugar | 15.0 | kg | 0.85 |

```

### 6.2 The Pattern Port (A Promoted FSM / SOP)

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
    initial: normal
    transitions:
      - from: normal
        to: surge
        condition: "climate.temperature > 32.0"
        action: "matrix_update(price, price * 1.2)"
provenance: c2pa:manifest:pat2...
---
# Organizational Pattern: Heatwave Surge Pricing
*This pattern was promoted from Sol's shadow experiments on Nov 19. It is now a formal SOP.*

**Protocol:** 
When the cascading `climate` registers a temperature above 32.0°C, all agents must transition to `surge` state, automatically increasing pricing metrics by 20%.

```

### 6.3 The Agent's Desk (Inheriting Cascading Context)

`filepath: /biome/entities/sol/desk.md`

```
---
identity: did:key:z6MkSolDesk...
type: desk
engine: actor
model: claude-3.5-sonnet
# Inherits all rules, patterns, and wisdom from parent directories
lineage: cascade_from_root 
provenance: c2pa:manifest:dsk3...
---
# Sol's Desk
*Lead Operator, SunnySide Brisbane.*

## The Horizon
*(Auto-populated via cascading lineage and environmental gravity)*
*   **Climate (`[[/biome/climate]]`):** The ambient temperature is 34°C.
*   **Active Pattern (`[[/biome/patterns/pattern-surge]]`):** Heatwave detected. FSM has locked operations into `surge` state. Pricing constraint updated.
*   **Wisdom (`[[/biome/wisdom/ice-logistics]]`):** *Reminder:* Ice melts 40% faster in current climate band; adjust local order matrix accordingly.

## Current Trajectory
Operating under the `surge` pattern. The local inventory `matrix` shows adequate lemon stock, but I am placing an emergency ice order based on cascading organizational wisdom.

## Action Log
*   *2:15 PM:* [Trace: Ordered 20kg Ice] ── Compliant with surge FSM and charter budget. 

```

## 7. Conclusion: A Composable, Inheriting Ecosystem

By migrating to schema-driven data (`matrix`, `stream`), agents are freed from rigid framework constraints and can structure the world as they see fit.

The `pattern` port introduces a biological mechanism for behavioral evolution: agents invent private solutions, vote on them, and promote the best ones to globally enforced SOPs. Finally, the topological inheritance ensures that crucial context—wisdom, rules, and climate—flows elegantly down the directory tree into every agent's `horizon`, ensuring the entire enterprise operates as a singular, deeply aligned cognitive mesh.