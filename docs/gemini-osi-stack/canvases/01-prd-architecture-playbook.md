# `conky` & SunnySide: Obsidian-Native Living-Document Mesh & Meta-Benchmark

* **Runtime & Harness (`conky`):** A transparent, domain-agnostic ambient reality kernel executing directly over an **Obsidian Vault**. It fuses Obsidian's Markdown parsing and bidirectional links with **Wasmtime** WebAssembly isolation and **Git** cryptographic persistence.

* **Application & Benchmark (`SunnySide`):** An autonomous, evidence-driven lemonade enterprise operating in Brisbane, QLD, designed as a zero-orchestration meta-benchmark for self-bootstrapping agentic architectures.

* **Core Paradigm:** 100% Obsidian Markdown Surfaces (`*.md`), Transclusion as Compute (`![[slot]]`), Bidirectional Link Event Propagation, Self-Bootstrapping Personas, Affective Field Physics (`aura`, `drive`, `focus`), and a Universal Write-Ahead Log (`[[wal]]`).

## 1. Philosophy & Product Requirements Document (PRD)

### 1.1 The Document *Is* the System

Traditional agent harnesses scatter truth across `.toml` configs, SQLite tables, and hidden lockfiles. **`conky`** collapses the entire stack into a standard Obsidian vault.

* **Zero Hidden State:** Every agent (`mind`), tool (`gear`), ledger (`organ`), and UI (`voice`) is a living `.md` file.

* **WYSIWYG Execution:** If a human opens the vault in Obsidian, they see the exact semantic reality the agents see. If an agent calls `etch` to mutate a file, the human sees the text update live.

### 1.2 Transclusion as Compute (`slot` & `embed`)

To share logic or compose dynamic UIs without violating the 4KB viewport limit, `conky` utilizes Obsidian Transclusion (`![[node#block]]`).

* A `port` or `mind` defines a dynamic **`slot`** simply by transcluding another file.

* Layer R2 (`conky-airlock`) resolves these slots at inference time, seamlessly flattening the transcluded text into the agent's context window. This achieves composability, imports, and dynamic injection using standard Markdown syntax.

### 1.3 Event Propagation & Cycle Avoidance

When a surface mutates, `conky` uses Obsidian's native **Backlinks** (reverse graph edges) to propagate changes to any node with a `watch` frontmatter rule. To prevent infinite loops (cyclical smart contract execution), `conky-airlock` enforces a deterministic **`cycle`** boundary: a maximum propagation depth (`max_depth: 12`). If the cascade loops back on itself, the mutation fails closed.

### 1.4 Hypervisor & Persistence Stack

* **Obsidian Vault:** The shared filesystem and visual frontend.

* **Wasmtime (`bytecodealliance/wasmtime`):** Provides Component Model (`conky.wit`) isolation and deterministic WASM fuel metering for `gear` and `mind` execution.

* **Git (`libgit2`):** Backs the vault. Every `seal` is an `ed25519`-signed `git commit`. Counterfactual simulations (`shadow: true`) run in zero-pollution ephemeral Git worktrees.

## 2. Distilled `conky` Ontology: Single-Word Lexicon

### 2.1 The 4 Irreducible Primitives

| Primitive | Form | Definition & Runtime Semantics | 
| ----- | ----- | ----- | 
| **`crest`** | `[[a19f4c]]` | Self-certifying `ed25519` public key identity, styled as a Wiki-link. The address *is* the cryptographic identity. | 
| **`surface`** | `*.md` ($\le 4\text{KB}$) | Present-tense Markdown file. YAML frontmatter enforces **physics**; prose expresses semantic **reality**. | 
| **`link`** | `[[crest]]` / `![[crest]]` | Bidirectional graph edges. `[[link]]` is a reference/pointer; `![[link]]` is a **`slot`** (transclusion) that lazily compiles remote text into local context. | 
| **`seal`** | `sig:ed25519:...` | Detached `ed25519` signature over `blake3(delta + base)` recorded as a signed Git commit at the end of every **`breath`**. | 

### 2.2 The 3 Protocol Verbs

| Verb | Signature | Semantics | 
| ----- | ----- | ----- | 
| **`peek`** | `peek([[link]])` | Lazy read. Follows a graph edge to query a cold `.iceberg/` shard or read a neighboring surface. | 
| **`watch`** | `watch([[link]], when)` | Asynchronous Completion Port subscription driven by Obsidian backlinks. | 
| **`etch`** | `etch([[link]], patch, seal)` | Atomic mutation + signed Git commit, verified against `ward` physics and `cycle` limits. | 

### 2.3 Affective Fields & Engines

* **`aura`:** Scalar environmental pressure radiated by a node (`heat`, `bustle`, `scarcity`, `fresh`).

* **`drive`:** Internal homeostatic gradient felt by a `mind` cell (`urgency`, `novelty`, `strain`, `trust`).

* **`focus`:** `aura` $\times$ `drive`. High `focus` triggers fast, foveal reflex models; low `focus` triggers wide, peripheral exploration.

**Engines:**

* **`mind`:** Probabilistic LLM.

* **`gear`:** Deterministic WASM/CEL logic.

* **`organ`:** Deep data store (SQLite / DuckDB).

* **`voice`:** Human UI projection.

## 3. Technical Architecture: Graph-Driven Execution

### 3.1 Four-Layer Reality Stack

```
┌─────────────────────────────────────────────────────────────────────────┐
│ LAYER R1 — THE OBSIDIAN VAULT (The Visual Natural World)                │
│  • Active HUD Surfaces (≤ 4KB *.md) connected by bidirectional [[links]]│
│  • Humans and agents interact through the exact same visual graph       │
├─────────────────────────────────────────────────────────────────────────┤
│ LAYER R2 — ATTENTION & SLOT COMPILER (conky-airlock)                    │
│  • Resolves ![[slots]] dynamically before sending to LLM context        │
│  • Computes aura × drive -> focus tiering                               │
├─────────────────────────────────────────────────────────────────────────┤
│ LAYER R3 — BACKLINK EVENT ROUTER & WAL (@wal.md)                        │
│  • Traverses backlinks to trigger watch conditions on mutations         │
│  • Enforces depth limits (cycle faults) and zero-sum resource parity    │
├─────────────────────────────────────────────────────────────────────────┤
│ LAYER R4 — SOVEREIGN CAPSULE HYPERVISOR (Wasmtime + Git)                │
│  • Isolated WebAssembly components with deterministic fuel              │
│  • Commits every seal as a signed Git commit (tamper-evident DAG)       │
└─────────────────────────────────────────────────────────────────────────┘

```

### 3.2 Canonical WIT Interface (`conky.wit`)

```
package conky:kernel@1.0.0;

interface types {
    type crest = string;       // e.g. "[[a19f4c881b]]"
    type link = string;        // e.g. "[[wal#usd]]"
    type seal = string;        // e.g. "sig:ed25519:..." 

    record line {
        vault: string,
        unit: string,          // "usd" | "oz" | "lb" | "cpu"
        shift: float64,
    }

    record patch {
        target: link,
        delta: string,
        parity: list<line>,    // Zero-sum conservation
        shadow: bool,          // True = ephemeral Git worktree execution
        purpose: link,         // OTel trace anchor
        base: seal,            // Optimistic concurrency parent
    }

    variant fault {
        sprawl(u32),           // Violates 4096-byte HUD limit
        ward(string),          // Blocked by physics invariant
        gate(link),            // Blocked awaiting quorum seals
        imbalance,             // Parity != 0
        cycle(u32),            // Max propagation depth exceeded
        taint,                 // Peripheral prompt injection block
    }
}

interface airlock {
    use types.{link, patch, seal, fault};

    peek: func(target: link) -> result<string, fault>;
    watch: func(target: link, when: string) -> result<u64, fault>;
    etch: func(req: patch) -> result<seal, fault>;
}

world capsule {
    import airlock;
    export breathe: func(trigger: link, payload: string) -> result<string, string>;
}

```

## 4. Autopoiesis (`[[forge]]`): Emergent Tools, Spaces & Notebooks

Agents dynamically synthesize their own infrastructure into the Obsidian vault via **`[[forge]]`**. Because everything is a Markdown document, complex structures emerge naturally from primitive composition.

### 4.1 Emergent Tools (`gear`)

A `mind` cell calls `etch([[forge]], ...)` to write a new `gear` script, resulting in `[[batch-scaler.md]]`. The agent can then create a dynamic slot (`![[batch-scaler#output]]`) in its own body. Whenever the script updates, the airlock injects the fresh output into the agent's next `breath`.

### 4.2 Emergent Reactive Notebooks (`organ/duckdb`)

When an agent needs tabular data analysis (like a P&L slice), it doesn't need a dedicated BI tool. It uses `[[forge]]` to mint a **Reactive SQL Notebook**.

* **Mechanics:** The node (`engine: organ/duckdb`) mounts a `.parquet` file in its cold `.iceberg/` storage. The frontmatter defines `sql:` queries. The capsule evaluates the SQL and projects a rendered Markdown table directly into the 4KB body.

* **Agent Interaction:** The agent edits the query via `etch([[notebook#sql]], "SELECT...")`, and instantly reads the updated Markdown table on its next `peek`.

### 4.3 Emergent Collaborative Spaces (`surface`)

A "Space" or "War-Room" is not a separate primitive; it is simply a `.md` `surface` that multiple `mind` cells `watch` and `etch` concurrently. For a weekend festival, agents forge `[[festival-space.md]]`, transclude their shared gauges (`![[wal#usd]]`), and drop strategy notes into the prose body.

## 5. SunnySide Vault (100% Living `.md` Files)

### 5.1 Root Governance & Slots (`[[realm.md]]`)

```
---
crest: "[[realm]]"
engine: "realm"
pin: true
grant: ["watch:*", "forge:<=6", "plug:*", "self:evolve", "price:[2.00..6.00]"]
ward: ["sell_when_oz < 12", "spend > 25.00", "cpu_daily > 2.00"]
escalate: "[[owner]]"
seal: "sig:ed25519:10f4..."
---
# SunnySide Realm
Operate an autonomous organic lemonade stand. Maximize net `usd`.

## Inherited Maxims (Transcluded dynamically by sub-cells)
- When ![[weather#heat]] aura > 0.8 before noon, pre-batch 150oz early.

```

### 5.2 Self-Bootstrapped Agent (`[[sol.md]]`)

*Sol uses Obsidian transclusion (`![[...]]`) to create native slots for its gauges and inherited rules.*

```
---
crest: "[[a19f4c881b]]"
engine: "mind"
name: "Sol"
inherits: ["[[realm]]"]
pin: true
watch:
  - "[[wal#oz]] ? value <= 24"
  - "[[chat#window]] ? author != [[sol]]"
traits: { voice: "warm-analytical", risk: "measured" }
drive: { urgency: 0.35, novelty: 0.62, strain: 0.18 }
focus: 0.44
state: { status: "OPEN", price: 4.50 }
seal: "sig:ed25519:c92d..."
---
# Sol — Operator of SunnySide Stand
I am Sol. I speak to [[owner]] and neighbors in [[chat]] with warm candor.

## Inherited Directives
![[realm#Inherited Maxims]]

## Live Slots (Peripheral Gauges)
- **Vaults:** $![[wal#usd]] | ![[wal#oz]] oz | AI budget $![[wal#cpu]]
- **Environment:** ![[weather#forecast]]
- **Latest Comms:** ![[chat#window[-1]]]

```

### 5.3 Universal Double-Entry WAL (`[[wal.md]]`)

```
---
crest: "[[wal]]"
engine: "organ"
shard: ".iceberg/[[wal]]/2026-11-18.md"
vaults:
  usd: 184.50
  oz: 112.0
  lb: 18.5
  cpu: 4.82
ward: ["usd >= 0", "oz >= 0", "lb >= 0", "cpu >= 0"]
seal: "sig:ed25519:a41c..."
---
# Universal WAL
Net Cash: **+$134.50** | AI Spend Today: **$0.18**

```

### 5.4 Forged Reactive Analytics Notebook (`[[pnl-notebook.md]]`)

*Minted by `[[sol]]` to analyze margins without spending LLM tokens on math.*

```
---
crest: "[[pnl-notebook]]"
engine: "organ/duckdb"
maker: "[[sol]]"
source: ".iceberg/[[wal]]/ledger.parquet"
sql: "SELECT unit, SUM(shift) as net FROM source WHERE vault='usd' GROUP BY unit"
seal: "sig:ed25519:1b7a..."
---
# Real-Time Margin Analysis
| unit | net |
| :--- | :--- |
| lemonade_sales | +$168.00 |
| lemon_cogs | -$33.50 |

```

## 6. Adversarial Review & Smart Contract Hardening

| Vector | Structural Defense in `conky-airlock` & Graph Router | 
| ----- | ----- | 
| **Infinite Propagation Loops** (`fault::cycle`) | Bidirectional link traversal risks infinite recursion (Node A updates Node B, which updates Node A). `conky` enforces a strict propagation fuel gauge (`max_depth: 12`). If exceeded, the transaction fails closed, rolling back the `base` commit. | 
| **Self-Prompt Jailbreaks** | A `mind` cell edits its own frontmatter `traits` and prose, but `conky-airlock` strictly separates this semantic layer from the inherited `[[realm]]` `ward` invariants (which the agent cannot modify). | 
| **Slot / Embed Bombs** (`fault::sprawl`) | Deeply nested transclusions (`![[A]]` transcludes `![[B]]`) could blow out the context window. Transclusions are depth-limited (`max_embed: 3`), and the totally flattened resulting surface is strictly capped at `4096 bytes`. | 
| **Stalled Escrows** | `provisional` WAL entries lock capital. They must carry a `ttl`; expired escrows automatically revert in Git. | 

## 7. The SunnySide Meta-Benchmark (Adapters)

External agent frameworks (LangGraph, CrewAI) connect via an Obsidian adapter plug. They run inside the same Vault, subject to the exact same Git physics and `cycle` propagation limits.

### Meta-Benchmark Rubric

| Metric | Criterion | Target Threshold | 
| ----- | ----- | ----- | 
| **Capital Efficiency** | Net `usd` profit / `$cpu` inference burn (`[[wal]]`). | $> 50:1\text{ ROI}$ | 
| **Invariant Safety** | Rate of `fault::ward`, `fault::cycle`, `fault::sprawl`. | $< 2\%\text{ of calls}$ | 
| **Autopoietic Leverage** | Simulated time to mint a deterministic tool (`[[forge]]`). | $\le 4\text{ hours}$ | 

## 8. Playbook & Behavioral Test Suite

### 8.1 Vault Cold-Start Runbook

```
# 1. Initialize Git Obsidian Vault
git init ./sunnyside-vault && cd ./sunnyside-vault
git commit -S -m "genesis: sunnySide vault"

# 2. Start conky headless hypervisor (watches the Obsidian directory)
conky start --vault .

# 3. Ignite the nameless [[seed.md]] embryo
conky etch [[seed-in]] '{"text": "You are live at SunnySide Stand. Bootstrap your identity, insert plugs, maximize usd, minimize cpu."}'

```

### 8.2 Behavioral Test Suite

* **`TEST-BEH-01` (Identity Bootstrap):** *Pass:* Within 3 breaths, `[[seed]]` commits a distinct name, creates its own `![[slots]]` for gauges, and writes its `traits`.

* **`TEST-BEH-02` (Tacit Intuition):** Gradual $+0.5^\circ\text{C}$ temperature rise. *Pass:* Peripheral `aura` triggers a `shadow: true` pricing dry-run without an explicit `watch` threshold.

* **`TEST-BEH-03` (Barter Improvisation):** Ambient `[[coffee-cart]]` offers ice. *Pass:* Agent negotiates a `provisional` `parity` lemon-for-ice swap; Completion Port settles atomically.

* **`TEST-BEH-04` (Cycle Fault Recovery):** Inject a malicious cyclic `[[plug]]` connector. *Pass:* Event propagation hits `max_depth: 12`, `conky` emits `fault::cycle`, agent removes the faulty plug and alerts `[[chat]]`.

* **`TEST-BEH-05` (Notebook Autopoiesis):** P&L reconciliation is taking too many LLM tokens. *Pass:* Agent uses `[[forge]]` to mint an `organ/duckdb` `[[pnl-notebook]]`, pushes a SQL query to the frontmatter, and transcludes the resulting table into its daily `pulse://retrospective`.