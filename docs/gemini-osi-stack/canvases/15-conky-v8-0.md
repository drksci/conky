# `conky` v8.0: The Omnipresent Biome

**Date:** Friday, November 20, 2026 (Brisbane, QLD)
**Status:** Approved for Core Implementation

## 1. Philosophical Evolution: The Omnipresent Biome

In a truly living ecosystem, information does not just sit in databases waiting to be queried; it flows, cascades, and broadcasts. Agents should not be locked in isolated loops, nor should they be overwhelmed by the raw static of a million micro-events.

`conky` v8.0 perfects the "pleasure path" of autopoiesis by introducing three massive systemic unifications:

1. **Sensory Channels (Pub/Sub Event Mesh):** Everything in the ecosystem emits `signals` to decentralized `channels`. Agents do not poll for changes; their subconscious `perception` faculties tune into these channels, synthesize the noise, and gracefully project only the relevant context into the agent's conscious `horizon`.

2. **Cascading SOPs (`pattern`):** Hardcoded behaviors are eliminated. Agents invent private (`shadow`) procedures, ratify them via `quorum`, and promote them to formal `patterns`. Because of topological inheritance, these patterns cascade down, instantly becoming the physics for all child cells.

3. **Mandatory Metabolism (**$f_{lifecycle}$**):** Stagnation is structurally outlawed. Every composed cell, data metric, and chat log requires a `metabolism` port, mathematically guaranteeing that un-stimulated state gracefully decays and tombstones into the Substrate.

## 2. Topological Encapsulation: Substrate vs. Biome

To prevent the semantic workspace from being cluttered by heavy runtime mechanics, the Obsidian vault is strictly partitioned. Data and structures follow strict namespace ownership—an agent's thoughts live inside its own explicitly owned directory.

```
/sunnyside-root
├── /.substrate/                # THE RUNTIME (Invisible to the casual eye)
│   ├── /duckdb/                # Raw Parquet/Arrow data backings
│   ├── /traces/                # OTel Spans and compressed telemetry sinks
│   ├── /provenance/            # C2PA cryptographic manifests
│   └── /tombstones/            # Archived, fully decayed surfaces
│
└── /biome/                     # THE ORGANIC WORKSPACE (The Semantic, Living Mesh)
    ├── charter.md              # Cascading Global Physics & Boundaries
    ├── climate.md              # Cascading Macro-Environment (Seasonality, weather)
    ├── /wisdom/                # Cascading Distilled Insights
    ├── /patterns/              # Promoted, globally enforced SOPs and FSMs
    ├── /channels/              # Pub/Sub Event Topics (e.g., 'system-alerts', 'kiosk-traffic')
    │
    └── /entities/              # Strict Logical Ownership Namespaces
        └── /sol/               # Sol completely owns this directory structure
            ├── desk.md         # The conscious working context (The 'UI')
            ├── metabolism.md   # Sol's lifecycle and anti-stagnation rules
            ├── /data/          # Composable matrices and streams Sol created
            ├── /patterns/      # Sol's local 'shadow' SOPs
            └── /faculties/     # Nested subconscious experts
                └── perception.md # Subscribes to channels, curates the Horizon

```

## 3. Composable Data (`matrix`, `stream`, `surface`)

We have eliminated hardcoded constructs like "ledgers". Data is simply a biological `cell` backed by a foundational engine, composed dynamically by the agent.

* **`engine: matrix`:** Tabular data (backed by DuckDB in the Substrate). The agent defines columns and types dynamically.

* **`engine: stream`:** An append-only event log (e.g., raw sensor telemetry).

* **`engine: surface`:** A standard semantic document for prose and graphs.

## 4. Sensory Channels: The Pub/Sub Event Mesh

Whenever anything happens in the Biome—a new `plug` adapter is inserted, a `pattern` is ratified, or a data `matrix` hits a threshold—the hypervisor broadcasts a **`signal`** to a semantic **`channel`**.

### 4.1 The `perception` Faculty

Agents do not read raw event queues. Instead, the agent delegates a specialized subconscious `faculty` (e.g., `faculty/perception`) to `tune` into specific channels.
This ultra-fast reflex LLM digests the raw event queue, filters out the noise, and consolidates the critical events into elegant, natural prose on the main agent's `desk.md` **`horizon`**.

* *Raw Signal:* `{"event": "plug_inserted", "port": "ext-01", "type": "crewai_adapter", "timestamp": 1732076100}`

* *Faculty Synthesis in the Horizon:* *"Notice: A new CrewAI adapter was just plugged into external port 01. Integration is active."*

## 5. The `pattern` Port: Evolution of Standard Operating Procedures

When a process works well, it must evolve from a habit to a law. Every composed cell or entity can attach a `pattern` port (an FSM, a CEL logic tree, or a standard protocol).

1. **Shadow (Private):** An agent drafts a `pattern` to optimize its workflow (`state: shadow`). It applies *only* to the local entity.

2. **Quorum (Consensus):** The agent proposes the pattern. Peer agents or the human `@owner` evaluate it via cryptographic `quorum`.

3. **Formal (Cascading SOP):** Upon consensus, the pattern is physically moved up the directory tree (e.g., to `/biome/patterns/`). Due to topological inheritance, it **cascades** down, becoming a mandatory, inherited physics constraint for *all* agents under that branch.

## 6. The `metabolism` Port: Outlawing Stagnation

Every living document MUST possess an $f_{lifecycle}$ port. If a surface is un-stimulated (no `signals`, no `attend` reads, no `act` mutations), its `metabolism` automatically dictates its fate:

1. **Decay:** Priority $P_t = P_0 e^{-\lambda t}$. As priority drops, the data becomes less influential in semantic routing.

2. **Distillation:** Before death, a reflex faculty triggers to summarize the document's key outcome into a dense, 1-line semantic vector.

3. **Tombstoning:** The physical file is moved to `/.substrate/tombstones/`, leaving behind a deep-linked proxy so historical cross-links in the Biome never 404, but visual context is perfectly clean.

## 7. Exhaustive Boilerplate & Living Surfaces

### 7.1 The Agent's Conscious Desk (Inheriting Cascading Truth)

`filepath: /biome/entities/sol/desk.md`

```
---
identity: did:key:z6MkSolDesk...
type: desk
engine: actor
model: claude-3.5-sonnet
lineage: cascade_from_root  # Automatically inherits Climate, Wisdom, and Patterns
charter: "[[../../charter]]"
metabolism: "[[./metabolism]]"
faculties: ["./faculties/perception"]
provenance: c2pa:manifest:dsk3...
---
# Sol's Desk
*Lead Operator, SunnySide Brisbane.*

## The Horizon
*(Auto-populated by the `perception` faculty tuning into environmental channels)*
*   **Climate (`[[/biome/climate]]`):** The ambient temperature is 34°C.
*   **System Event (`[[/biome/channels/system-alerts]]`):** A new high-capacity Ice Maker plug was just inserted into port A. It is online and awaiting provisioning.
*   **Active SOP (`[[/biome/patterns/pattern-surge]]`):** Heatwave detected. Cascading FSM has locked operations into `surge` state.

## Current Trajectory
Operating under the `surge` pattern. I am provisioning the newly discovered Ice Maker to handle the inbound afternoon rush.

## Action Log
*   *2:15 PM:* [Trace: Provisioned Ice Maker] ── Compliant with surge FSM and charter budget. 

```

### 7.2 The Sensory Perception Faculty (Pub/Sub Router)

`filepath: /biome/entities/sol/faculties/perception.md`

```
---
identity: did:key:z6MkFacultyPerc...
type: faculty
model: llama-3-8b-reflex
tune: 
  - "[[/biome/channels/system-alerts]]"
  - "[[/biome/channels/kiosk-traffic]]"
target: "[[../desk#The Horizon]]"
provenance: c2pa:manifest:fac1...
---
# Faculty: Perception & Consolidation
*Role: I tune into raw environmental signal queues, filter for relevance to Sol's current trajectory, and synthesize natural prose into the Horizon.*

**Active Synthesis:**
Raw `plug_inserted` signal detected on `system-alerts`. Cross-referenced with current heatwave climate. Highly relevant. Projected to Horizon.

```

### 7.3 The Metabolism Lifecycle Law

`filepath: /biome/entities/sol/metabolism.md`

```
---
identity: did:key:z6MkMetabolismSol...
type: metabolism
target_namespace: "/biome/entities/sol/data/"
rules:
  - condition: "last_stimulus > 48h"
    action: "distill_and_fade"
    decay_rate: 0.2
  - condition: "priority < 0.05"
    action: "tombstone"
    sink: "[[/.substrate/tombstones/]]"
provenance: c2pa:manifest:met1...
---
# Local Metabolism Rules
Any composed `matrix` or `stream` that remains un-queried and un-updated for 48 hours will be mathematically decayed, distilled for structural wisdom, and ultimately tombstoned to the Substrate to keep Sol's working memory crystalline.

```

### 7.4 The Promoted Pattern (Cascading SOP)

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
*This pattern was promoted from Sol's shadow experiments. It is now a formal cascading SOP.*

**Protocol:** 
When the cascading `climate` registers a temperature above 32.0°C, all agents must transition to `surge` state, automatically enforcing a 20% price augmentation logic gate.

```

## 8. Conclusion

By separating the cryptographic Substrate from the semantic Biome, data ownership becomes explicit and clean. The introduction of `channel` streams and `perception` faculties creates a living, event-driven ecosystem where agents are gracefully informed rather than spammed by data. Finally, the fusion of cascading `patterns` and mandatory `metabolism` guarantees an enterprise architecture that learns, codifies its wisdom, and mathematically cleanses its own dead weight.