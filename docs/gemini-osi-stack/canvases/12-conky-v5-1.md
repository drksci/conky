# `conky` v5.1: The Organic Workspace & Lifecycle Dynamics

**Date:** Friday, November 20, 2026
**Status:** Approved for Core Implementation

## 1. Philosophical Pivot: The Organic Workspace

The goal of `conky` is to create a multi-agent system that is indistinguishable from a team of highly organized humans sharing a version-controlled workspace (an Obsidian vault).

To achieve the "pleasure path," we are discarding overly biological or academic terms (cells, membranes, MoE) in favor of intuitive, natural concepts.

* **The `Entity`:** A sovereign actor in the system (e.g., an agent, a department).

* **The `Charter`:** The rules of engagement (replacing "membrane" or "critic"). It defines what an entity is allowed to do financially, logically, and ethically.

* **The `Desk`:** The main working surface of an entity. Where things come into view.

* **The `Faculty`:** A specialized, subconscious capability of an entity (e.g., Doubt, Fact-Checking, Hindsight).

* **The `Head` & `Journal`:** Every faculty maintains its own `head.md` (what it is currently thinking about) and `journal.md` (a chronological log of past conclusions).

## 2. Lifecycle Dynamics: Bloom, Fade, and Tombstone

In an active enterprise, thousands of documents, chat logs, and sub-tasks are generated daily. Without a metabolic lifecycle, the context window drowns, and the graph collapses under its own weight. `conky` v5.1 introduces thermodynamic lifecycle management to all living surfaces.

### 2.1 The Priority Decay Function

Every piece of information (an entry in a journal, a completed trajectory, a chat message) has a priority score $P$. If it is not actively referenced (`attended`) or stimulated by the environment, it naturally fades over time $t$ according to exponential decay:

$$
P_{t} = P_{0} e^{-\lambda t}
$$


*(Where* $\lambda$ *is the decay constant defined by the `charter`.)*

### 2.2 The Three States of Information

1. **Bloom (Active):** High relevance/priority. The hypervisor natively transcludes this information into the agent's `horizon` on their `desk.md`. The agent sees it automatically.

2. **Fade (Subconscious):** Priority drops below the horizon threshold. The document remains in the active folder, but is removed from the agent's immediate view. It can still be explicitly queried.

3. **Tombstone (Archived):** Priority hits absolute zero, or an objective is explicitly completed.

   * The hypervisor physically moves the `.md` file to the `.archive/` (or cold `.iceberg/`) directory.

   * **Graceful Degradation:** Any remaining transclusions (`![[target]]`) across the vault do not break. The hypervisor replaces them with a lightweight, read-only tombstone block: `[Archived: Resolution of Festival Surge Pricing]`.

## 3. The Entity Architecture: Desk, Head, and Journal

An entity (`sol`) should not have its primary `desk.md` cluttered with the anxious micro-thoughts of its `doubt` faculty. Instead, faculties run asynchronously on cheap, fast models.

* The faculty reads the environment and updates its own `head.md` with active concerns.

* When a concern is resolved, it moves to the faculty's `journal.md` and begins to `fade`.

* *Only* if the `head.md` generates a high-priority warning (e.g., "This action will bankrupt us") does the hypervisor project that warning into the main agent's `desk.md` horizon.

### Vault Topology (The Workspace Directory)

```
/sunnyside-workspace
├── charter.md                 # The constitutional rules for the entire vault
├── /treasury                  # The Ledger
│   └── the-till.md
└── /team
    └── /sol                   # The Entity 'Sol'
        ├── desk.md            # Sol's main conscious working surface
        ├── charter.md         # Sol's specific permissions and boundaries
        └── /faculties         # Sol's subconscious experts
            ├── /doubt
            │   ├── head.md    # Active risk assessments
            │   └── journal.md # Historical risk assessments (Fading)
            └── /hindsight
                ├── head.md    # Active strategic analysis
                └── journal.md # Distilled wisdom maxims (Fading)

```

## 4. Exhaustive Boilerplate & Living Surfaces

The following files represent exactly how this architecture looks in the repository. Note how the YAML handles the raw systems physics (provenance, models, queries), leaving the Markdown body beautifully natural and readable.

### 4.1 The Charter (The Boundary/Physics)

`filepath: /sunnyside-workspace/team/sol/charter.md`

```
---
identity: did:key:z6MkCharterSol...
type: charter
target: "[[./desk]]"
grants:
  - action: mutate
    target: "[[/treasury/the-till]]"
    condition: "evaluate: shift.usd >= -50.00"
provenance: c2pa:manifest:abc1...
---
# Sol's Charter & Boundaries
This document defines the physical and financial bounds of Sol's operations. 
Sol is authorized to operate the SunnySide stand, adjust pricing, and authorize expenses up to $50.00 USD per transaction. Any action violating these physics will be cryptographically rejected.

```

### 4.2 The Main Agent Desk (The Conscious Workspace)

`filepath: /sunnyside-workspace/team/sol/desk.md`

```
---
identity: did:key:z6MkSolDesk...
type: desk
model: claude-3.5-sonnet
charter: "[[./charter]]"
provenance: c2pa:manifest:def2...
---
# Sol's Desk
*Role: Lead Operator, SunnySide Brisbane.*

## The Horizon
*(Things naturally drifting into view based on relevance and stimulus)*
*   **Alert (`[[./faculties/doubt/head]]`):** You are about to price lemonade at $1.00. This yields a negative margin based on current citrus costs.
*   **Environment:** Current temperature is 35°C. 

## Current Focus
I am reviewing our pricing strategy for the afternoon rush. Given the heat, demand is highly inelastic, but the `doubt` faculty has flagged that my proposed discount is too aggressive. 

## Actions Taken
*   *2:10 PM:* Paused proposed price drop. Initiating review of wholesale citrus costs.

```

### 4.3 The Faculty Head (Active Concerns)

`filepath: /sunnyside-workspace/team/sol/faculties/doubt/head.md`

```
---
identity: did:key:z6MkFacultyDoubt...
type: faculty-head
model: llama-3-8b-reflex
vision: "![[../../desk#Current Focus]]"
priority: 0.95
provenance: c2pa:manifest:ghi3...
---
# Faculty: Doubt (Active Concerns)
*Role: I evaluate Sol's current focus for catastrophic financial or logical risk.*

**Current Active Concern:**
Sol is considering a price drop to $1.00 to capture volume. However, I have queried `[[/treasury/the-till]]` and wholesale lemons currently cost $1.20 per yield. This action will result in immediate negative margins. 

**Recommendation:** Halt the price drop. Signal high priority to the Horizon.

```

### 4.4 The Faculty Journal (Fading Historical Log)

`filepath: /sunnyside-workspace/team/sol/faculties/doubt/journal.md`

```
---
identity: did:key:z6MkDoubtJournal...
type: journal
decay_rate: 0.1
provenance: c2pa:manifest:jkl4...
---
# Faculty Journal: Doubt

### Resolved Concerns (Fading)

**Date:** Thursday, Nov 19
**Priority:** 0.15 *(Fading)*
**Concern:** Sol attempted to buy 500lbs of ice during a thunderstorm. 
**Resolution:** Flagged as high risk for inventory spoilage. Sol successfully aborted the transaction.

**Date:** Monday, Nov 16
**Priority:** 0.00 *(Tombstoned)*
![[Archive: Resolved supplier dispute over damaged cups.]]

```

## 5. Architectural Lifecycle Operations

To support this living system, the `conky-hypervisor` natively runs a background cron process: **The Gardener**.

1. **The Gardener** wakes up during quiescent periods (e.g., when message volume drops).

2. It applies the $P_{t} = P_{0} e^{-\lambda t}$ math to all `journal` entries, completed `trajectories`, and resolved `head` concerns.

3. Items that cross the tombstone threshold ($P < 0.05$) are surgically moved to the `.archive/` directory.

4. The Gardener rewrites active transclusions to point to the tombstone, ensuring the graph remains intact and error-free, but highly compressed and lightweight for the active agent's context window.