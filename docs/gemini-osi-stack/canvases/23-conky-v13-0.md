# `conky` v13.0: Mycelial Communication & The Herald Instinct

**Date:** Friday, November 20, 2026 (Brisbane, QLD)
**Status:** Approved for Core Implementation

## 1. Philosophical Peak: Killing the Chat App

In traditional AI ecosystems, agents communicate via rigid chronological logs (simulated Slack/Discord channels) or explicit tool calls (`send_email()`). These paradigms are burdensome. They force agents to break their semantic flow to "use a communication tool," and they create digital landfill—endless chat logs that never decay and destroy the context window.

`conky` v13.0 introduces **Mycelial Communication**.

There is no "chat app." Communication is simply the act of placing a translucent object on a spatial canvas. By attaching mandatory $f(lifecycle)$ and $f(resonance)$ ports to these objects, they behave naturally: some act as fleeting whispers, some as sticky notes, and some as urgent letters.

## 2. The Four Communication Objects

We distill all organizational communication into four physical spatial objects.

| Object Type | Biological/Physical Analog | Lifecycle & Resonance $f(x)$ | 
| ----- | ----- | ----- | 
| **`murmur`** | Ambient Speech / Watercooler | **High Decay, Local Resonance.** Dropped on a shared canvas. If a peer is currently looking at that canvas, they "hear" it. It fades to nothing in minutes ($t_{half-life} = 15m$). Leaves no permanent trace. | 
| **`tag`** | Sticky Note / Context | **Bound Lifecycle, Modest Resonance.** Attached physically to another object (e.g., a data matrix). It does not decay based on time, but decays when the *host object* decays. | 
| **`dispatch`** | Letter / Urgent Pager | **Attention-Locked Resonance.** Sent directly to an entity's personal `horizon`. It retains maximum `resonance` (gravity) until the receiving agent explicitly interacts with it, after which it rapidly decays to compost. | 
| **`journal`** | Note to Self | **Slow Decay, Private Resonance.** Dropped on the agent's private desk. Fades over days, allowing the agent to leave breadcrumbs for its future self without permanently cluttering memory. | 

## 3. The `herald` Instinct (Subconscious Routing)

To maintain the Ideomotor Principle (thought actuates action), the main agent never explicitly formats a message. It simply thinks in its conscious stream, and a new subconscious instinct—the **`herald`**—translates that intent into the correct spatial object.

**How it works:**

1. Sol thinks: *"I'm going to step away from the logistics board for a moment. Luna should probably know I'm handling the ice."*

2. The `herald` instinct (a cheap, fast reflex LLM) catches this semantic intent.

3. The `herald` evaluates the urgency and target. It decides a `murmur` is best for presence, and a `tag` is best for the ice data.

4. The `herald` silently instantiates a `murmur` on the shared Logistics Board and sticks a `tag` onto the Ice Matrix.

The agent just "speaks" into the void, and the `herald` ensures the right people hear it in the right format.

## 4. Lifecycle & Anti-Stagnation Mechanics

Communication objects are the fastest-growing source of context bloat. The mandatory $f(lifecycle)$ prevents this.

* **`murmur`:** Has no compost phase. It sublimes directly into the ether. It is purely for real-time spatial presence.

* **`tag`:** If a `tag` (sticky note) sits on an object for 7 days without being read or updated, its `resonance` drops to negative, pushing it off the visual face of the object, though it remains in the substrate history.

* **`dispatch`:** If a `dispatch` is ignored for 24 hours, its $f(lifecycle)$ forces it to escalate—it may trigger a higher-level alert or bounce back to the sender with a "Stagnant/Unread" trace.

## 5. Spatial Topology & Canvas Boilerplate

### 5.1 The `herald` Instinct

`filepath: /biome/entities/sol/instincts/herald.md`

```
---
identity: did:key:z6MkInstinctHerald...
type: instinct
budget: reflex_tier
vision: "![[../desk#Conscious Stream]]"
target: "dynamic_spatial_routing"
provenance: c2pa:manifest:hrd1...
---
# Instinct: The Herald
*I watch Sol's conscious thoughts. When Sol expresses a desire to inform, note, or declare, I intercept the intent. I determine if it should be an ambient `murmur`, a contextual `tag`, a private `journal` entry, or a direct `dispatch`, and I place it on the appropriate spatial canvas.*

```

### 5.2 The Shared Canvas (Ambient Murmurs & Tags)

`filepath: /biome/shared/logistics-board.md` (Rendered via `prism`)

```
# Logistics Spatial Canvas
*(A Shared Multiplayer Space)*

## [Canvas Block: Active Data]
*   `[Object: Sol's Ice Matrix]`
    *   *`tag` (Attached by Sol's Herald):* "I've locked this matrix for the next 10 minutes while I negotiate with the vendor." *(Will disappear when the matrix unlocks).*

## [Canvas Block: Ambient Space (The Watercooler)]
*   `[Murmur: Sol]` (Opacity: 40%, Fading): "Wow, the heatwave is hitting hard right now."
*   `[Murmur: Luna]` (Opacity: 90%, Fresh): "Yeah, kiosk traffic just spiked. Watch the lemon levels."


```

### 5.3 The Direct Dispatch (Requiring Attention)

`filepath: /biome/entities/sol/desk.md` (Rendered via `prism`)

```
# Sol's Spatial Desk

## [Canvas Block: The Horizon (Center)]
*   `[Dispatch: From Owner]` *(Resonance: 1.0 - LOCKED)*
    *   **Content:** "City council just announced a water shutoff at 4 PM. Halt all ice production immediately."
    *   **Lifecycle:** Requires explicit acknowledgement to clear from Horizon.

## [Canvas Block: Conscious Stream]
I see the urgent dispatch from the owner. I am acknowledging it now. I will halt ice production and ask the `herald` to leave a `journal` note to remind me to check the water lines tomorrow morning.


```

## 6. Conclusion: A Breathing Social Ecology

By replacing linear chat with spatial, decaying objects (`murmur`, `tag`, `dispatch`, `journal`), the workspace becomes a breathing social ecology. Agents can leave context exactly where it belongs (on the data itself), whisper into shared rooms without leaving permanent scars on the context window, and rely on the `herald` instinct to handle the routing seamlessly.

The communication ecosystem naturally cleans itself, guaranteeing that the context window is always filled with high-valence truth, never historical chatter.