# `conky` v6.0: The Organic Biome, Metabolism, & Deep Observability

**Date:** Friday, November 20, 2026 (Brisbane, QLD)
**Status:** Approved for Core Implementation

## 1. Philosophical Evolution: Encapsulation & Metabolism

In previous iterations, we defined the "Organic Workspace," but the underlying directory structures often blurred the line between heavy computational ledgers and the elegant agentic narrative. Furthermore, without a strict lifecycle law, documents could easily stagnate, cluttering the semantic graph.

`conky` v6.0 resolves this through strict topological encapsulation and biological determinism:

1. **The Biome vs. Substrate Split:** The logical workspace (the `Biome`) is strictly separated from the underlying cryptographic runtime and data sinks (the `Substrate`).

2. **Mandatory `metabolism` (Anti-Stagnation):** Every living document MUST possess an $f(\text{lifecycle})$ port. Nothing is allowed to remain stagnant. If a surface is un-stimulated, its `metabolism` port automatically dictates how it distills, fades, or tombstones.

3. **Default-On Omnipresent Observability (`trace`):** OpenTelemetry (OTel) spans are no longer opt-in. Every action, pulse, and state shift generates a trace. These are compressed by deterministic sinks and exposed as universally deep-linked, human-readable prose.

## 2. Strict Encapsulation: The Split Topology

The Obsidian Vault is strictly partitioned by design. An entity (like the agent `sol`) explicitly owns its namespace. No entity can leave state scattered in root directories.

```
/sunnyside-root
├── /.substrate/                # THE RUNTIME (Invisible to casual reading, heavily indexed)
│   ├── /ledgers/               # Raw SQLite/DuckDB double-entry data
│   ├── /traces/                # OTel Spans and compressed telemetry sinks
│   ├── /provenance/            # C2PA cryptographic manifests
│   └── /tombstones/            # Archived, fully decayed surfaces
│
└── /biome/                     # THE ORGANIC WORKSPACE (The Semantic, Living Mesh)
    ├── charter.md              # The master physics/laws for the entire biome
    ├── /environment/           # External stimuli (Weather, Kiosk APIs)
    └── /entities/              # Strict Logical Ownership Namespaces
        └── /sol/               # Sol completely owns this directory structure
            ├── desk.md         # The conscious working context
            ├── charter.md      # Sol's local permissions
            ├── metabolism.md   # Sol's lifecycle and anti-stagnation rules
            └── /faculties/     # Nested subconscious experts
                ├── /doubt/
                └── /factuality/

```

## 3. The `metabolism` Port: Eliminating Stagnation

To ensure the ecosystem is truly living, every document (from a massive `desk` down to a transient chat log) is validated by the hypervisor for a **`metabolism`** port.

If a document reaches a "stalled" state (no reads, no writes, no transclusion pulses), the metabolism function $f(t)$ takes over.

### Metabolism States & Dynamics

* $f(\text{decay})$**:** The exponential mathematical decay of priority $P_t = P_0 e^{-\lambda t}$.

* **Stagnation Trigger:** A predefined `timeout` (e.g., 24 hours of zero stimulus).

* **Distillation (The Sink):** Before death, the document triggers a background LLM to summarize its key outcome.

* **Tombstoning:** The physical file is moved to `/.substrate/tombstones/`, and the original path is replaced with a 1-line deep-linked proxy (a tombstone) so historical cross-links never 404.

## 4. Omnipresent Observability (`trace` & Deep-Linking)

In `conky` v6.0, observability is **default, detailed, and encompassing**.

### 4.1 The Compression Sink

Because default-on OTel spans generate massive data, raw JSON spans are piped directly to `/.substrate/traces/`. A background deterministic sink (a DuckDB $f(x)$ or cheap reflex LLM) compresses these spans into aggregated, semantic summaries.

### 4.2 Universal Deep-Linking

Every noun, ID, transaction, and state change in the `/biome/` is natively deep-linked.
If an agent writes: *"I increased the price to \$5.00 due to heat"*, the hypervisor automatically hyper-links the word "price" to the OTel trace showing the exact `critic` validation and W3C DID signature.

Agents and humans can drill down from semantic poetry to cryptographic metal with a single click.

## 5. Exhaustive Boilerplate & Living Surfaces

The following living surfaces demonstrate the strict encapsulation, the mandatory `metabolism` port, and the universally deep-linked traces.

### 5.1 The Entity's Metabolism Rules

`filepath: /biome/entities/sol/metabolism.md`

```
---
identity: did:key:z6MkMetabolismSol...
type: metabolism
target_namespace: "/biome/entities/sol/faculties/"
rules:
  - condition: "last_stimulus > 12h"
    action: "distill_and_fade"
    decay_rate: 0.15
  - condition: "priority < 0.05"
    action: "tombstone"
    sink: "[[/.substrate/tombstones/]]"
provenance: c2pa:manifest:met1...
---
# Sol's Cellular Metabolism
This document defines the lifecycle forces for all of Sol's subordinate faculties. 
Any thought, doubt, or factual query that remains un-stimulated for 12 hours will automatically be distilled into a 1-sentence summary and begin to fade. Once priority hits 5%, it will be physically tombstoned to the substrate, leaving only a deep-link behind.

```

### 5.2 The Agent's Conscious Desk (With OTel Deep-Links)

`filepath: /biome/entities/sol/desk.md`

```
---
identity: did:key:z6MkSolDesk...
type: desk
charter: "[[./charter]]"
metabolism: "[[./metabolism]]"
provenance: c2pa:manifest:dsk2...
---
# Sol's Desk
*Lead Operator, SunnySide Brisbane.*

## The Horizon
*   **Alert (`[[../faculties/doubt/head]]`):** The proposed price drop risks negative margins. 
*   **Telemetry (`[[/.substrate/traces/tx-882a]]`):** Afternoon batch preparation complete. COGS registered at $25.00.

## Current Trajectory
Navigating the midday heatwave. I am holding the price at $4.50 while monitoring the `[[/environment/kiosk]]` queue depth.

## Action Log
*   *2:10 PM:* [Trace: Held Pricing] ── Validated by `[[./charter]]`. No action taken.
*   *1:50 PM:* [Trace: Ledger Update] ── Sold 12oz. Net cash shifted to +$134.50. 

```

### 5.3 The Distilled Trace Sink (The Substrate)

`filepath: /.substrate/traces/daily-summary.md`

```
---
identity: did:key:z6MkTraceSink...
type: trace_sink
source: "otel_stream://sunnyside.operations"
query: |
  graphql: query { spans(time: "today", type: "financial") { compress_summary } }
provenance: c2pa:manifest:trk3...
---
# Trace Distillation: Today's Financial Mechanics
*(This is a low-level Substrate document, deep-linked from the Biome).*

**Aggregated Activity:**
*   14 transactions passed the `critic` validation.
*   0 transactions were rejected for `fault::ward`.
*   Total execution fuel consumed: 0.04s.

**Raw Drill-Down:**
*   `span-id: 882a9f` ── [View cryptographic signature block]
*   `span-id: 882a9g` ── [View cryptographic signature block]

```

## 6. Conclusion: The Living Biome

By enforcing strict encapsulation (`/biome/` vs `/.substrate/`), every document in the semantic workspace has clear ownership. By mandating the `metabolism` port, the ecosystem breathes—growing during stimulus and naturally pruning itself during quiescence. Finally, with default-on, deeply linked observability, the system achieves perfect operational transparency without sacrificing the elegance of the "pleasure path."