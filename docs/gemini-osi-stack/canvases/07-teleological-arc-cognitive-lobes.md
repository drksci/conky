# `conky` v3.0: The Teleological `Arc`, Cognitive `Lobe`s, & Active Inference

**Date:** 2026-11-20
**To:** conky Core Engineering
**From:** Architecture & Systems Design
**Concept Credit:** Antigravity Mesh Operations

## 1. The Paradigm Shift: From Rigid Plans to Biological Cognition

Current state-of-the-art agent frameworks (LangChain, AutoGen, Tree of Thoughts) model execution as **discrete, rigid task chains**. If step 3 of a 10-step plan fails, the agent often loops infinitely or abandons the objective entirely. Furthermore, these agents "think" using a single, monolithic, expensive LLM call for every action.

**The `conky` v3.0 Solution:**

1. **The `Arc` Primitive:** Replaces brittle "plans" with biological, vector-based trajectories of any scale (from a 5-minute barter to building a 10-year enterprise). Arcs apply geometric elastic tension to the agent's behavior.

2. **Cognitive `Lobe`s:** Replaces monolithic thinking with a localized "brain center" architecture. Ultra-cheap, highly-scoped reflex agents (`lobe`s) run asynchronously in the background, providing inputs like "self-doubt," "factual grounding," or "hindsight" without burning frontier-model `$cpu`.

## 2. Distilled Lexicon Addition

| Primitive | Form | Runtime Semantics | 
| ----- | ----- | ----- | 
| **`arc`** | `[[arc-<name>]]` | A teleological trajectory surface. Represents a living plot/mission with a defined `telos`. | 
| **`telos`** | `![[anchor]]` | The ultimate state vector or goal the `arc` is pulling toward. | 
| **`tension`** | `0.0 - 1.0` | Computed dynamically based on geometric graph distance / state divergence from the `telos`. | 
| **`fade`** | `decay_rate` | Biological decay. If an `arc` is starved of `pulse` streams, its tension drops and it naturally archives. | 
| **`lobe`** | `[[lobe-<trait>]]` | A specialized `mind` cell running on ultra-cheap reflex models, restricted to a tiny Field of View (`fov`). | 
| **`dream`** | `state: quiescent` | The retrospective background state where completed/failed `arc`s are distilled into permanent wisdom. | 

## 3. Cognitive `Lobe`s: The Subconscious Brain Centers

An autonomous enterprise operator (`[[sol]]`) should not burn expensive reasoning tokens (e.g., GPT-4o or Claude 3.5 Sonnet) just to double-check its own math or scan for hallucinations.

Instead, `[[sol]]` is supported by **`lobe`s**—cheap, single-purpose agents that `watch` specific `![[slots]]` of the main agent's context and inject feedback via `pulse` streams.

* **`[[lobe-doubt]]` (The Amygdala):** Runs purely to find flaws. It watches `[[sol]]`'s proposed `etch` patches. If it calculates high risk, it radiates a `strain` aura, causing the main agent to pause and reconsider.

* **`[[lobe-fact]]` (The Grounding Center):** A highly scoped RAG/Search lobe. Its sole `fov` is currency and factuality. It asynchronously flags outdated pricing or hallucinated supplier names before `[[sol]]` commits them.

* **`[[lobe-wisdom]]` (The Prefrontal Cortex):** Projects historical `maxim`s into the active context only when the current `telos` closely matches a past `arc`.

**Cost Economics:** Because `lobe`s are strictly bounded by their `fov` (they only "see" a 500-token slice of the world) and run on local/cheap models, they cost fractions of a cent per `breath`, enabling continuous, multi-threaded subconscious processing.

## 4. Fractal Arcs & Active Inference

Arcs are fractal. A root arc (`[[arc-build-sunnyside-empire]]`) can span simulated years. It spawns intermediate sub-arcs (`[[arc-secure-lemons-today]]`, `[[arc-hire-manager]]`).

### 4.1 Subconscious Pragma Injection (`tension`)

As `conky-airlock` calculates the geometric divergence from the `telos`, it generates `tension`. This scalar directly modulates the `mind` capsule *before* inference:

* **Low Tension (0.0 - 0.3) \[Parasympathetic\]:** Temperature increases. The agent is encouraged to branch, forge new tools, explore, and spawn creative sub-arcs.

* **High Tension (0.7 - 1.0) \[Sympathetic\]:** Temperature drops to `0.0`. `conky-airlock` injects a rigid system pragma:
  `> [PRAGMA: TENSION CRITICAL (0.85). Diverging from [[telos]]. Collapse intermediate arcs or abort immediately.]`

### 4.2 Evolution, Forces, & Hindsight (`dream`)

Arcs do not just succeed or fail; they evolve under environmental pressures.

* **Fading:** If an `arc` (e.g., negotiating with a cart) stalls, its `pulse` stream runs dry. The `fade` coefficient slowly drops its priority until it is silently tombstoned. No explicit "cancel" logic is required.

* **The `dream` Retrospective:** When `[[sol]]` enters a `quiescent` state (e.g., night time, no active customers), `[[lobe-dream]]` activates. It performs **Hindsight Analysis** on all `arc`s that closed or faded that day. It extracts structural lessons, mints new `maxim`s into `[[realm]]`, and permanently archives the raw `arc` to `.iceberg/`.

## 5. Implementation: The Bonded Triad Update

An `Arc` and a `Lobe` are simply living `.md` surfaces in the Obsidian Vault.

### 5.1 The Living Arc Surface (`vault/arc-festival-surge.md`)

```
---
crest: "[[arc-festival-surge]]"
engine: "arc"
telos: "[[wal#usd]] >= 1000.0"
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
- ![[arc-surge-pricing]] (Tension: 0.2, Status: Settled)

```

### 5.2 The Subconscious Doubt Lobe (`vault/lobe-doubt.md`)

```
---
crest: "[[lobe-doubt]]"
engine: "mind"
model: "reflex-tier-fast"
fov: "![[sol#proposed_etch]]" # Only sees the impending action
watch: ["[[sol]] ? status == 'proposing'"]
seal: "sig:ed25519:11b2c..."
---
# Cognitive Lobe: Self-Doubt
Analyze `![[sol#proposed_etch]]` purely for edge-case risks, margin destruction, or physical impossibility. Emit `strain` aura if risk > 0.7.

```

## 6. Architectural Next Steps (v3.0 Integration)

To integrate this biological architecture into the `conky` harness:

1. **Vector/Graph Math in Airlock:** Update `conky-airlock` to evaluate `telos` conditions and calculate graph/state divergence, emitting the continuous `tension` float.

2. **`fov` Slicing Engine:** Ensure the compiler strictly enforces the `fov` transclusions for `lobe`s so they cannot accidentally consume the parent's full context window, preserving `$cpu` efficiency.

3. **The `dream` Cron:** Implement the background `dream` coalescing loop that triggers when overall mesh `bustle` drops to near-zero, triggering hindsight distillation on aged arcs.