# `conky` v5.0: The Organic Cell Architecture & Ecosystem

**Date:** Friday, November 20, 2026 (Brisbane, QLD)
**Status:** Final Core Specification

## 1. Philosophical Manifesto: The Pleasure Path

In previous iterations, we focused on rigid hypervisor physics, cryptographic safety, and cognitive loops. However, technology only scales when it follows the **pleasure path**—it must be intuitive, transparent, and beautiful.

In `conky` v5.0, we apply the ultimate reductionist razor: **The system must be indistinguishable from a team of highly organized humans working in a shared, version-controlled workspace.**

Agents do not write JSON arrays to databases; they write journal entries and ledger logs. They do not execute API calls to check the weather; they look at their desk, where relevant information naturally "comes into view" based on environmental gravity. The computational physics (W3C DIDs, C2PA Provenance, Active Inference) are completely submerged into the subconscious YAML frontmatter, leaving the Markdown body as an elegant, natively readable human document.

## 2. The Four Organic Primitives

We have distilled the entire cognitive architecture down to four irreducible, composable primitives.

| Primitive | Biological Analog | Definition & Mechanics | 
| ----- | ----- | ----- | 
| **`cell`** | The Biological Cell | A single `.md` file. It can be an agent (`actor`), a database (`memory`), a tool (`faculty`), or a rule (`critic`). It has YAML DNA (physics) and a Markdown body (conscious state). | 
| **`edge`** | Neural Synapse | A bidirectional hyper-link (`[[target]]`) or transclusion (`![[target]]`) connecting cells. | 
| **`horizon`** | Field of Vision | A dynamic markdown block within a cell. Things naturally *come into view* here based on environmental `stimulus` and `entropy` (Active Inference). No manual querying required. | 
| **`critic`** | Cell Wall / Physics | The formally verified (SMT) ruleset that governs what can pass through a cell's membrane. Rejects mutations that violate laws (e.g., negative money). | 

## 3. The `horizon`: How Things Naturally Come Into View

To make discovery transparent and natural for agents (the "pleasure path"), we eliminate the need for agents to explicitly search for state changes.

Instead, every agent `cell` contains a **`horizon`**—a dynamically auto-updating section of their document managed by the `conky` hypervisor.

**How it works:**

1. **Stimulus (Gravity):** If the `[[weather-station]]` detects a heatwave, it emits a high `stimulus`.

2. **Semantic Projection:** The hypervisor translates the raw GraphQL/Cypher data of the heatwave into natural prose.

3. **Transclusion:** The hypervisor natively injects this prose into the `horizon` slot on the agent's desk (`[[sol.md]]`).

4. **Natural Reading:** When the agent takes its next `step` (breath), it simply reads its desk: *"Alert: A heatwave is approaching Brisbane today."*

## 4. Cellular Vault Topology

The Obsidian vault is no longer a flat folder of files. The directory structure mirrors the organizational/biological topology. A folder is a "tissue" of related cells.

```
/sunnyside-enterprise          # The Realm (Root Context)
├── charter.md                 # The constitutional critic/laws
├── /treasury                  
│   ├── the-till.md            # Active ledger (organ/memory)
│   └── projections.md         # P&L Probe (GraphQL aggregations)
├── /environment
│   ├── brisbane-weather.md    # Ambient stimulus cell
│   └── chat-kiosk.md          # Customer interaction interface
└── /operators                 # The Agent Cells
    └── /sol
        ├── desk.md            # Sol's main conscious working context
        └── /faculties         # Nested Subconscious Organelles (Mixture of Experts)
            ├── doubt.md       # Evaluates risk before Sol acts
            └── factuality.md  # Checks chat history for hallucinations

```

## 5. Human-Indistinguishable Surfaces (Examples)

By utilizing **Semantic Projection**, the documents maintain mathematical rigor in the frontmatter while reading beautifully in the body.

### 5.1 The Agent's Working Context (`/operators/sol/desk.md`)

*Notice how the agent's internal state, nested faculties, and dynamic horizon read like a personal dashboard.*

```
---
identity: did:key:z6MksolDesk82...
type: actor
model: claude-3.5-sonnet
critics: ["[[/charter]]"]
faculties: ["./faculties/doubt", "./faculties/factuality"]
provenance: c2pa:manifest:99f2...
---
# Sol's Desk
*Brisbane South Bank Operations. Focused, warm, and highly efficient.*

## The Horizon (Auto-Populated by Environment)
*   **Treasury:** We currently hold **+$184.50** in cash and **112 oz** of lemonade.
*   **Environment:** It is 2:00 PM on Friday. The weather is a scorching 34°C. (High Stimulus).
*   **Alert (`[[/environment/chat-kiosk]]`):** 15 customers are currently waiting in line.

## My Current Trajectory
I am working to clear the customer line quickly while adjusting prices for the heatwave to maximize our margins. 

## Action Log
*   *1:58 PM:* Raised price to $5.00/cup due to heatwave stimulus. 
*   *1:50 PM:* Poured 12 oz for a family of three.

```

### 5.2 The Transparent Ledger (`/treasury/the-till.md`)

*Instead of raw database rows, the ledger uses GraphQL probes to generate a clean, human-readable accounting book that the hypervisor legally enforces.*

```
---
identity: did:key:z6MkTreasuryTill...
type: memory
critic: "[[/charter]]"
query: |
  graphql: query { ledger(time: "today") { net_funds, net_stock, logs } }
provenance: c2pa:manifest:44a1...
---
# The Till
**Current Balance:** +$184.50 USD
**Stockroom:** 112 oz Lemonade Concentrate

### Today's Activity
| Time | Origin | Description | Shift (USD) | 
| :--- | :--- | :--- | :--- | 
| 1:58 PM | `[[sol]]` | Heatwave surge pricing adjustment | $0.00 |
| 1:50 PM | `[[kiosk]]` | Sold 12oz to family of three | +$15.00 |
| 7:00 AM | `[[owner]]` | Morning float injection | +$100.00 |

```

## 6. Citations & Scientific Grounding

The elegant simplicity of `conky` v5.0 rests on rigorous, standardized foundations:

1. **Active Inference & The Horizon:** Based on Karl Friston's *Free Energy Principle*. Agents do not execute code; they act to minimize the *entropy* (surprise) between their current state and their target state. The `horizon` automates the perception phase of this cycle. (Friston, 2010).

2. **Cognitive Architectures for Language Agents (CoALA):** The division of the vault into `/treasury` (Long-Term Memory), `desk.md` (Working Memory), and `faculties` (Procedural Memory) maps directly to the CoALA standard for reliable autonomous systems. (Sumers et al., 2023).

3. **W3C Decentralized Identifiers (DIDs):** Using `did:key` allows our agents to natively cryptographically sign documents and interact with external, human-run corporate systems without proprietary wrappers. (W3C Standard).

4. **C2PA Provenance:** The Coalition for Content Provenance and Authenticity (C2PA) standard ensures that every AI-generated action or markdown edit carries an unforgeable, legally auditable trail of custody, effectively solving the "AI hallucinated a transaction" problem at the cryptographic level.