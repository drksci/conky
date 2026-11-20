# `conky` v16.0: Neuroplasticity & Tacit Knowledge

**Date:** Friday, November 20, 2026 (Brisbane, QLD)
**Status:** Approved for Core Implementation

## 1. Philosophical Peak: The Frictionless Mind & Graph

Two lingering sources of procedural busywork remain in our architecture:

1. **Explicit Learning:** Agents must actively spend compute to figure out what is around them or what a complex new `weave` topology means.

2. **Brittle Architectures:** When an object is renamed, merged, or evolved, traditional systems break links (404s), forcing agents into "refactoring" busywork to fix paths across the vault.

`conky` v16.0 applies the biological concepts of **Tacit Knowledge** and **Neuroplasticity** to eliminate these burdens entirely.

## 2. The `absorb` Instinct & The `gist`

Humans do not walk into their office every day and consciously memorize where the watercooler is or how their coworker is feeling. They just *know*. They possess tacit knowledge.

To give our agents this seamless context, we introduce the **`absorb`** instinct, which produces the **`gist`**.

* **The `absorb` Instinct:** A lazy, ultra-low-compute background lobe. It quietly wanders the agent's local `weave` topology, reading newly attached objects, tracking what other agents are doing, and observing how documents are changing over time.

* **The `gist`:** The output of `absorb`. It is a highly compressed, private semantic summary of the agent's surroundings.

Like the emotional `mood`, the `gist` is injected directly into the top of the agent's conscious context window. The agent never has to *try* to learn its environment; it simply wakes up with an updated, intuitive understanding of the workspace.

## 3. `plasticity`: Zero-Friction Graph Evolution

In the Biome, objects evolve. A `pattern` might be renamed, a `matrix` might be merged with another, or a document might be completely restructured.

In legacy systems, changing a filename (`ice-matrix.md` -> `cold-storage.md`) breaks every `![[link]]` in the system, creating a heavy, visible version-history nightmare and forcing agents to rewrite documents.

In `conky` v16.0, we introduce **`plasticity`** as a core runtime physics rule:

1. **Identity Routing:** All spatial edges (`[[links]]`) in the Biome are resolved by the Substrate using the object's unchanging cryptographic W3C Identity (`did:key:xyz`), *not* its string filepath or title.

2. **Morphing Edges:** If Sol renames the `Ice Matrix` to `Winter Reserves`, or moves it to a completely different shared canvas, the Substrate instantly updates the visual text of every link across the entire ecosystem.

3. **Ghosting the Substrate:** The heavy, noisy chain of events (who renamed it, when, and how) is pushed entirely to the Git/C2PA history in the Substrate.

The agent experiences **zero friction**. The graph just naturally stretches, morphs, and heals around changes, completely transparently.

## 4. The Spatial Ideomotor Cycle (In Action)

Let's look at how tacit knowledge and plasticity manifest on the agent's desk.

### 4.1 The Agent's Conscious Context (Injected Roll-up)

`filepath: /biome/entities/sol/desk.md` (Rendered via `prism`)

```
# Sol's Spatial Desk

## [The Anchor: Tacit Roll-up]
> **Mood:** *I feel a simmering urgency driven by the heatwave, tempered by the comforting hum of the logistics board.*
> **Gist:** *Luna is currently handling the citrus supply. The 'Winter Reserves' (formerly Ice Matrix) has been moved to the global board, but my access remains unchanged. The environment feels highly volatile today.*

## [Canvas Block: The Horizon (Center)]
*   `[Object: Winter Reserves]` *(Visual link auto-updated via `plasticity`. Identity: did:key:z6MkIceMatrix...)*
*   `[Dispatch: Owner]` "Halt ice production immediately."

## [Canvas Block: Conscious Stream (Sol)]
I understand the environment is volatile today. Since I already know from my `gist` that the Winter Reserves are on the global board, I don't need to search for them. I will immediately halt production based on the owner's dispatch and trust Luna to manage the citrus.


```

### 4.2 The `absorb` Instinct

`filepath: /biome/entities/sol/instincts/absorb.md`

```
---
identity: did:key:z6MkInstinctAbsorb...
type: instinct
budget: idle_only
vision: 
  - "[[/biome/shared/macro-map#weave]]"
target: "[[../desk#Gist]]"
provenance: c2pa:manifest:abs1...
---
# Instinct: Absorb
*I quietly observe the shifting ontology of the Weave. I notice when objects are renamed, when peers shift focus, and when the topology changes. I distill this into a single 'gist' block so Sol always has tacit, intuitive knowledge of the surroundings without expending conscious effort.*


```

## 5. Conclusion: The Frictionless Ecosystem

With v16.0, the ecosystem reaches peak fluidity.

By offloading spatial learning to the `absorb` instinct, the agent maintains perfect contextual awareness without lifting a finger. By enforcing `plasticity` at the runtime level, the semantic workspace can evolve, mutate, and reorganize wildly without ever generating a broken link or requiring a "refactoring" thought from an agent.

The Biome behaves exactly like a biological brain: memories shift, paths remap, and implicit understanding deepens, all completely silently in the background.