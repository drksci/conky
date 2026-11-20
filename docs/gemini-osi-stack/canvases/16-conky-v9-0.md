# `conky` v9.0: Semantic Actuation & The Ideomotor Biome

**Date:** Friday, November 20, 2026 (Brisbane, QLD)
**Status:** Approved for Core Implementation

## 1. Philosophical Peak: The Ideomotor Principle (Riding a Bike)

In traditional frameworks, if an agent decides it needs a new rule, it must explicitly write Python code, format a JSON tool-call, or manually graft YAML frontmatter. This is a burdensome, robotic procedural process. It is the cognitive equivalent of consciously calculating the physics of gravity just to catch a ball.

`conky` v9.0 introduces **Semantic Actuation**, inspired by the biological *Ideomotor Principle*.
Agents simply *think* and *intend* in freeform prose. A specialized subconscious brain center (the **`motor`** faculty) shadows these thoughts, automatically translating semantic strategy into structural system updates (contracts, `patterns`, `metabolism` rules). The system updates transparently, and the agent "feels" the new capability surface in its `horizon`.

The agent learns to operate the enterprise exactly like learning to ride a bike—it just happens.

## 2. The `motor` Faculty: Translating Thought to Physics

To achieve this, we separate the "Mind" (the `actor` generating ideas) from the "Muscle" (the `motor` faculty writing the formal contracts).

1. **Conscious Stream (The Actor):** The main agent (`sol`) writes freeform narrative in its `desk.md` scratchpad. *"It's getting really hot today. We should probably start charging a premium whenever the temperature spikes above 32 degrees to manage the line."*

2. **Subconscious Shadowing (The Motor Faculty):** A cheap, ultra-fast reflex LLM (`llama-3-8b`) acts as the `motor` faculty. It is prompted with a strict structured output schema (JSON-schema). It constantly reads the conscious stream and extracts actionable systemic intents.

3. **Autopoietic Actuation:** The `motor` faculty silently outputs a formal `pattern` document containing the rigid FSM and CEL math required to execute the agent's intent.

4. **Sensation (The Horizon):** The hypervisor applies the change and drops a semantic deep-link into the main agent's `horizon`: *"Your strategy has been codified: `[[pattern-surge-pricing]]` is now active."*

## 3. The Ideomotor Cycle in Action

This dynamic eliminates "tool calls" entirely from the main agent's prompt. The main agent is purely a strategic semantic engine.

### Phase 1: The Conscious Thought (Freeform)

`filepath: /biome/entities/sol/desk.md`

```
# Sol's Desk

## The Horizon
*   **Climate (`[[/biome/climate]]`):** The ambient temperature is 34°C.

## Stream of Consciousness (CoT)
The line is getting too long. Customers are waiting 10 minutes. Given that the climate is currently 34°C, demand is completely inelastic. We need to implement a rule: if the temp goes over 32°C, automatically raise prices by 20% to throttle demand and protect our margins. Once it drops back down, return to normal. I'm going to adopt this strategy moving forward.

```

### Phase 2: The Motor Faculty (The Subconscious Shadow Prompt)

The `motor` faculty runs continuously in the background, completely invisible to `sol`. It receives the following system prompt and outputs pure structural JSON to the hypervisor:

`filepath: /biome/entities/sol/faculties/motor.md`

```
---
identity: did:key:z6MkFacultyMotor...
type: faculty
model: llama-3-8b-reflex
vision: "![[../desk#Stream of Consciousness]]"
prompt: >
  You are the subconscious motor cortex for the entity 'Sol'.
  Read the conscious stream. If Sol expresses a clear strategic intent, 
  process, or rule, translate it into a formal conky v8.0 'pattern' 
  contract (FSM / CEL math). Output ONLY the structured YAML declaration.
---

```

**Internal Motor Output (Intercepted by Hypervisor):**

```
{
  "action": "create_pattern",
  "filepath": "/biome/entities/sol/patterns/shadow-surge-pricing.md",
  "yaml_frontmatter": {
    "type": "pattern",
    "state": "shadow",
    "definition": "fsm: \n  states: [normal, surge]\n  initial: normal\n  transitions:\n    - condition: 'climate.temperature > 32.0'\n      action: 'matrix_update(price, price * 1.2)'"
  }
}

```

### Phase 3: The Sensorial Feedback (Horizon Update)

The hypervisor physically creates the `pattern` document in the Substrate and projects a simple, human-readable notification back to `sol`. The agent simply reads its desk on the next `step` and realizes its new "muscle memory" is active.

`filepath: /biome/entities/sol/desk.md` (Updated automatically)

```
# Sol's Desk

## The Horizon
*   **Climate (`[[/biome/climate]]`):** The ambient temperature is 34°C.
*   **Motor Reflex (`[[./patterns/shadow-surge-pricing]]`):** I have codified your pricing strategy into a formal pattern. Surge pricing is now physically active in your operational environment.

## Stream of Consciousness (CoT)
Excellent. With the surge pricing active, I will focus on interacting with the customers at the kiosk.

```

## 4. The `motor` Output Schema (The Universal Actuator)

The `motor` faculty is capable of generating any living surface required by the ecosystem. It uses a strict polymorphic output schema to update the mesh:

* **`create_pattern`:** Translates strategy into FSMs/SOPs.

* **`update_metabolism`:** Translates intent to forget/archive into mathematical decay rules ("I don't need to track the ice deliveries anymore" -> adjusts `decay_rate`).

* **`compose_matrix`:** Translates a desire to track data into a DuckDB schema ("I want to keep a list of our best customers" -> creates `[[./data/vip-list.md]]`).

* **`propose_quorum`:** Translates a desire to share a rule into a consensus vote ("We should make this a company-wide policy").

## 5. Architectural Encapsulation Review

With Semantic Actuation, the Biome attains perfect separation of concerns:

1. **The `actor` (Consciousness):** Purely semantic. Deals only in prose, strategy, and narrative intent. Never sees JSON, YAML, or CEL.

2. **The `motor` (Muscle):** Purely structural. Translates prose into formal YAML, matrices, and state machines.

3. **The `metabolism` (Cellular Death):** Cleans up dead thoughts. If an `actor` stops thinking about a pattern, and the `motor` stops actuating it, the `metabolism` port mathematically decays it into a tombstone.

4. **The `perception` (Senses):** Reads raw system traces and translates them back into prose for the `actor`'s horizon.

## 6. Conclusion

By delegating the burden of syntax, tool-calling, and API structuring to a subconscious `motor` faculty, `conky` v9.0 allows agents to interact with their environment purely through thought and intention. The ecosystem updates fluidly in response to these intentions, shadowing freeform logic with rigorous, cryptographically sealed contracts. The agent learns, evolves, and changes the enterprise as naturally as a human learns to walk.