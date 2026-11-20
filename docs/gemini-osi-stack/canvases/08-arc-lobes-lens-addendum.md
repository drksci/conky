# `conky` v3.0: Arcs, Lobes, and the Universal `lens` $f(x)$

**Date:** 2026-11-20
**To:** conky Core Engineering
**From:** Architecture & Systems Design
**Concept Credit:** Antigravity Mesh Operations

## 1. The Paradigm Shift: Biological Cognition & Measurement

Current state-of-the-art agent frameworks (LangChain, AutoGen) model execution as rigid task chains and force massive, monolithic LLMs to do everything: plan, execute, calculate math, and evaluate success. This is fragile and computationally devastating.

**The `conky` v3.0 Solution introduces three new primitives:**

1. **The `arc` (Teleology):** Replaces brittle plans with biological, vector-based trajectories. Arcs apply geometric elastic tension to the agent's behavior.

2. **The `lobe` (Subconscious):** Replaces monolithic thinking. Ultra-cheap, highly-scoped reflex agents (`lobe`s) run asynchronously in the background, providing inputs like "self-doubt" or "factuality."

3. **The `lens` (Universal** $f(x)$**):** Replaces agent-driven calculation. A `lens` is a living metric document that automatically distills raw state into measurable scalars, triggers, or structured observations that cause the ecosystem to "tick."

## 2. The `lens` Primitive: Universal $f(x)$

Everything in the ecosystem must be measurable, and measurement must be a distinct physical property of the mesh, not a task the agent performs during a reasoning `breath`.

A **`lens`** is a living document that defines a function $f(x)$. It automatically "ticks" (recalculates) whenever its inputs receive a `pulse`.

### 2.1 The Three Lenses (Engines)

Because a `lens` is just a document, an agent can dynamically `[[forge]]` and tune it using whatever evaluation grammar fits the need:

* **`engine: lens/cel` (Deterministic Math):** Evaluates fast Common Expression Language rules. *Example: Calculating real-time margin thresholds.*

* **`engine: lens/sql` (Aggregated Data):** Evaluates DuckDB queries over cold `.iceberg/` storage. *Example: Hourly P&L grouping.*

* **`engine: lens/mind` (Semantic Evaluation):** Uses a cheap, heavily quantized model (e.g., Llama-3-8B) with a strict structured output schema (JSON) to quantify qualitative data. *Example: Reading `[[chat]]` to calculate a `customer_joy` score from 0.0 to 1.0.*

### 2.2 The "Qualifier Subtask" (Auto-Priming)

The agent (`[[sol]]`) does not waste context window reading raw logs to figure out if customers are happy or if costs are too high. The `conky-airlock` automatically ticks the `lens` surfaces in the background. The agent simply transcludes the scalar output (`![[lens-customer-joy#score]]`) into its HUD. The ecosystem is continuously quantified and primed for the agent.

## 3. Distilled Lexicon Update

| Primitive | Form | Runtime Semantics | 
| ----- | ----- | ----- | 
| **`arc`** | `[[arc-<name>]]` | A teleological trajectory surface with a defined `telos` (goal vector). | 
| **`telos`** | `![[anchor]]` | The ultimate state vector the `arc` is pulling toward. | 
| **`tension`** | `0.0 - 1.0` | Scalar computed dynamically based on geometric graph distance from the `telos`. | 
| **`lobe`** | `[[lobe-<trait>]]` | A specialized `mind` cell running on cheap reflex models, restricted to a tiny `fov`. | 
| **`dream`** | `state: quiescent` | The retrospective background state where completed/failed `arc`s are distilled into permanent wisdom. | 
| **`lens`** | `[[lens-<name>]]` | A universal $f(x)$ document. Auto-calculates metrics, triggers, and ecosystem factors. | 

## 4. Fractal Arcs & Active Inference

Arcs are fractal. A root arc (`[[arc-build-sunnyside-empire]]`) can span simulated years. It spawns intermediate sub-arcs (`[[arc-secure-lemons-today]]`).

### 4.1 Subconscious Pragma Injection (`tension`)

As `conky-airlock` calculates the geometric divergence from the `telos`, it generates `tension`. This scalar directly modulates the `mind` capsule *before* inference:

* **Low Tension (0.0 - 0.3) \[Parasympathetic\]:** Temperature increases. The agent is encouraged to branch, forge new tools, explore, and spawn creative sub-arcs.

* **High Tension (0.7 - 1.0) \[Sympathetic\]:** Temperature drops to `0.0`. `conky-airlock` injects a rigid system pragma:
  *> \[PRAGMA: TENSION CRITICAL (0.85). Diverging from \[\[telos\]\]. Collapse intermediate arcs or abort immediately.\]*

### 4.2 Evolution, Forces, & Hindsight (`dream`)

Arcs do not just succeed or fail; they evolve.

* **Fading:** If an `arc` stalls, its `pulse` stream runs dry. Biological decay lowers its priority until it is silently tombstoned.

* **The `dream` Retrospective:** When `[[sol]]` enters a `quiescent` state, `[[lobe-dream]]` activates. It performs **Hindsight Analysis** on closed `arc`s, extracts structural lessons, mints new `maxim`s into `[[realm]]`, and permanently archives the raw `arc` to `.iceberg/`.

## 5. Living Triad Examples (Arc, Lobe, Lens)

### 5.1 The Teleological Arc (`vault/arc-festival-surge.md`)

```
---
crest: "[[arc-festival-surge]]"
engine: "arc"
telos: "[[lens-festival-revenue#is_met]] == true"
parent: "[[arc-sunny-operations]]"
tension: 0.85
fade: 0.05
seal: "sig:ed25519:88f3a..."
---
# Arc: Festival Weekend Surge
**Primary Goal:** Capture maximum revenue during the South Bank festival.
**Environmental Forces:** ![[weather#heat]] (High pressure)
**Active Branches:**
- ![[arc-negotiate-ice]] (Tension: 0.8, Status: Critical)

```

### 5.2 The Universal $f(x)$ Primitive (`vault/lens-customer-joy.md`)

```
---
crest: "[[lens-customer-joy]]"
engine: "lens/mind"
model: "reflex-tier-fast"
fov: "![[chat#window]]"
schema: { "joy_score": "float 0.0-1.0", "frustration_trigger": "boolean" }
seal: "sig:ed25519:33d1b..."
---
# Lens: Customer Joy Index $f(x)$
Continuously evaluates the raw chat stream to quantify customer sentiment.
**Current Joy Score:** 0.82
**Frustration Trigger:** false

```

### 5.3 The Subconscious Doubt Lobe (`vault/lobe-doubt.md`)

```
---
crest: "[[lobe-doubt]]"
engine: "mind"
model: "reflex-tier-fast"
fov: "![[sol#proposed_etch]]" # Only sees the impending action
watch: ["[[sol]] ? status == 'proposing'"]
seal: "sig:ed25519:11b2c..."
---
# Cognitive Lobe: Self-Doubt (The Amygdala)
Analyze `![[sol#proposed_etch]]` purely for edge-case risks or margin destruction. 
Emit `strain` aura if `![[lens-margin-safety#score]] < 0.2`.

```

## 6. Architectural Next Steps (v3.0 Integration)

1. **Lens Evaluator Sub-routine:** Update `conky-daemon` so that `lens` documents trigger automatically via topological sorting when their `fov` inputs shift, executing their $f(x)$ and updating their frontmatter output without waking a main `mind` cell.

2. **Vector/Graph Math in Airlock:** Implement the continuous `tension` float based on the geometric state-space distance between the current `![[lens]]` outputs and the `arc`'s defined `telos`.

3. **The `dream` Cron:** Implement the background `dream` coalescing loop that triggers when overall mesh `bustle` drops to near-zero.