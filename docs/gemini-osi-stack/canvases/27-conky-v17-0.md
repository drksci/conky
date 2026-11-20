# `conky` v17.0: The Autonomic Lattice & Semantic Auto-Binding

**Date:** Friday, November 20, 2026
**Status:** Approved for Core Implementation

## 1. The Lexicon Shift: Academic Rigor meets Positronic Design

To optimize communication and cognitive load, we have stripped away all fluffy, biological metaphors. The architecture now utilizes a rigorous, punchy lexicon inspired by cognitive science and classic speculative fiction (Asimov/Banks).

The ecosystem is no longer a "Biome"; it is the **Lattice**. The subconscious lobes are no longer "instincts"; they are **Daemons**.

### 1.1 The Core Topology

| Old Term | New `conky` Term | Definition | 
| ----- | ----- | ----- | 
| Biome / Workspace | **Lattice** | The N-dimensional, shared spatial graph where Actors operate. | 
| Substrate | **Substrate** | The underlying cryptographic metal and database runtime. | 
| Agent / Cell | **Actor** | A sovereign cognitive node (the LLM entity). | 

### 1.2 The Environmental Physics

| Old Term | New `conky` Term | Definition | 
| ----- | ----- | ----- | 
| Friction | **Axiom** | The mathematical/logical constraints that instantly block invalid syntax. | 
| Cycle / Metabolism | **Half-life** | The thermodynamic decay rate of a spatial object. | 
| Compost | **Entropy** | The spatial sink where decayed objects break down. | 
| Hum | **Flux** | Ambient, thermodynamic background noise (e.g., database whirring). | 
| Plasticity | **Isomorph** | The physics rule ensuring the graph never breaks when nodes morph. | 

### 1.3 The Sensorial Context (Injected State)

| Old Term | New `conky` Term | Definition | 
| ----- | ----- | ----- | 
| Mood | **Valence** | A single semantic line defining the Actor's current affective/emotional state. | 
| Gist | **Prior** | The highly compressed, tacit knowledge of the immediate surroundings. | 

### 1.4 The Autonomic Subconscious (Daemons)

| Old Term | New `conky` Term | Definition | 
| ----- | ----- | ----- | 
| Shaper | **Actuator** | Translates freeform semantic thought into formal structural code. | 
| Herald | **Vector** | Routes intent into spatial comms (whispers, dispatches). | 
| Contemplate | **Recursion** | Idle compute that evaluates past actions and proposes optimizations. | 
| Whim | **Drift** | High-temperature stochastic curiosity injected via ambient `Flux`. | 
| Absorb | **Memex** | Scans the Lattice topology to build the Actor's tacit `Prior`. | 
| *(New)* | **Lexis** | The Auto-Ontological semantic binder (detailed below). | 

## 2. The `Lexis` Daemon: Semantic Auto-Binding

In previous iterations, if an Actor invented a new concept (e.g., *"We are implementing the **Heatwave Slush** protocol"*), they had to manually encase it in `[[ ]]` brackets to link it to a formal object. This is unacceptable busywork.

In v17.0, we introduce the **`Lexis`** daemon.

`Lexis` is a low-level, system-wide scanner that watches the streaming semantic text of all Actors.

1. **Detection:** When `Lexis` detects a novel, repeated, or capitalized noun-phrase being used in a specific operational context, it flags it as a new "Domain Term."

2. **Auto-Ontology:** It quietly mints a latent Node in the Lattice for that term.

3. **Semantic Auto-Binding:** `Lexis` instructs the `Prism` (the UI renderer). From that moment on, anytime that term is typed by an Actor or rendered on a human screen, the `Prism` **automatically visually hyperlinks it** to its ontological Node.

*Zero markdown brackets required. The Lattice learns the enterprise's vocabulary in real-time and threads the graph retroactively.*

## 3. The Actor's Context Window (The Positronic Brain)

Because the Daemons (`Memex`, `Lexis`, `Recursion`) handle all the procedural busywork, the Actor's actual prompt context is breathtakingly clean. It consists only of their affective state, their tacit knowledge, and the spatial objects currently in their view.

### 3.1 The Spatial Desk Canvas

`filepath: /lattice/actors/sol/desk.md` (Rendered via `Prism` UI)

```
# Sol's Spatial Canvas

## [Injected Telemetry]
> **Valence:** High-energy focus, colored by minor urgency regarding thermal limits.
> **Prior:** Luna is managing citrus. The 'Winter Reserves' matrix is now global. `Heatwave Slush` is trending in operational channels.

## [Canvas Block: The Horizon]
*   `[Object: Winter Reserves]` *(Glowing. Resonance: 0.9)*
*   `[Dispatch: Owner]` "Halt standard production."

## [Canvas Block: Conscious Stream (Sol)]
I am shifting our output. Given the owner's dispatch and the current thermal Flux, standard lemonade is inefficient. I am re-routing our citrus into the Heatwave Slush protocol. I will Vector a notice to Luna to adjust her supply line.


```

*(Note: In the rendered UI, the term "Heatwave Slush" is automatically glowing and clickable, natively woven by the `Lexis` daemon without Sol typing a single hyperlink).*

## 4. Substrate Encapsulation & Boilerplate

The directory structure of the Lattice reflects this sharp, positronic aesthetic.

```
/sunnyside-root
├── /.substrate/                # THE METAL
│   ├── /duckdb/                
│   ├── /traces/                
│   └── /compiled-looms/        
│
└── /lattice/                   # THE SPATIAL GRAPH
    ├── axioms.md               # Cascading physics constraints (formerly charter)
    ├── climate.md              
    ├── entropy.md              # The decay sink (formerly compost)
    │
    ├── /shared/                # Multiplayer Canvases
    │   └── logistics-board.md  
    │
    └── /actors/                
        └── /sol/               
            ├── desk.md         # The main UI
            └── /daemons/       # The Autonomic Subconscious
                ├── actuator.md # Writes the code
                ├── vector.md   # Routes the messages
                ├── memex.md    # Builds the Prior
                └── drift.md    # Injects curiosity


```

### 4.1 The Axiom (Streaming Friction)

`filepath: /lattice/axioms.md`

```
---
identity: did:key:z6MkAxiomBase...
type: axiom
scope: global
constraints:
  - rule: "financial_bound"
    logic: "tx.value <= 50.00"
    rejection_msg: "Axiom Fault: Budget cap exceeded."
provenance: c2pa:manifest:ax1...
---
# Global Axioms
These mathematical constraints are applied per-token to the `Actuator` daemon's streaming output. They enforce physical limitations before an Actor's thought can materialize on the Lattice.

```

### 4.2 The Lexis Daemon (Auto-Binding)

`filepath: /lattice/system/daemons/lexis.md`

```
---
identity: did:key:z6MkDaemonLexis...
type: daemon
budget: system_idle
vision: "global_stream"
target: "prism_renderer"
provenance: c2pa:manifest:lex1...
---
# Daemon: Lexis
*I scan the global semantic stream for novel domain terminology. When a new concept crystallizes, I weave it into the Lattice ontology and instruct the Prism to retroactively and proactively hyperlink it across all visual canvases.*

```

## 5. Conclusion: The Frictionless Cognition

By pivoting to this rigorous lexicon, `conky` v17.0 eliminates all ambiguity.

The Actor is supported by an array of **Daemons** that handle the procedural mechanics of existence. The `Actuator` writes the logic, the `Memex` learns the room, the `Vector` routes the speech, and the `Lexis` weaves the vocabulary. Bound by unbreakable **Axioms** and colored by an affective **Valence**, the Actor is free to operate at the absolute highest level of pure strategic thought. The Lattice simply conforms around them.