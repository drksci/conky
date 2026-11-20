# `conky` & SunnySide: Exhaustive PRD, Technical Architecture & Playbook

**Version:** 1.0.0 (Release Candidate)

**Status:** Approved for Implementation

**Architecture:** Obsidian-Native, Git-Backed, Wasmtime, WebAssembly Component Model (WIT)

## 1. Executive Summary & Vision

Traditional agent harnesses (LangChain, AutoGen, etc.) suffer from "abstraction sprawl"—scattering truth across Python scripts, `.toml` config files, hidden SQLite databases, and bloated chat logs.

**The Vision:** The document *is* the system.
**`conky`** is an ambient reality kernel executing directly over an **Obsidian Vault**. Every entity (agent, ledger, rule, tool, chat) is a bounded ($\le 4\text{KB}$) Markdown file (`surface`). State changes propagate through Obsidian's native bidirectional links (`[[node]]`), powered by a Wasmtime hypervisor and cryptographically secured by Git (`ed25519` commits).

**`SunnySide`** is the application layer—an autonomous lemonade enterprise acting as a Meta-Benchmark to test framework capital efficiency, self-bootstrapping, autopoiesis (tool forging), and resilience to cycle faults.

## 2. Product Requirements Document (PRD)

### 2.1 Goals & Success Metrics

1. **Zero Hidden State:** A human opening the Obsidian vault must see the exact semantic reality the agents operate on.

2. **Computational Parity:** Heterogeneous nodes (`mind` LLMs, `gear` WASM scripts, `organ` DuckDBs, `voice` human UIs) must operate securely under identical capability models.

3. **Provable Financial Safety:** Agentic operations must enforce double-entry accounting (`parity`) natively; an LLM cannot hallucinate money.

4. **Self-Evolution:** Agents must be able to forge their own deterministic tools and SQL notebooks (`[[forge]]`) to drive their inference costs (`cpu`) to zero for routine tasks.

### 2.2 Functional Requirements (FRs)

* **FR-1: Git-Backed State:** Every mutation must be committed to a local Git repository with an `ed25519` detached signature (`seal`).

* **FR-2: Transclusion as Compute (`slot`):** The runtime must resolve Obsidian transclusions (`![[target#block]]`) at runtime, flattening remote text into the executing node's context.

* **FR-3: Backlink Event Routing:** Mutations to a file must trigger `watch` evaluation in any file that holds a bidirectional link (`[[target]]`) to it.

* **FR-4: Universal WAL & Completion Ports:** Asynchronous multi-party transactions must escrow in `[[wal]]` and only commit when zero-sum `parity` is achieved across witnesses.

* **FR-5: Cycle Prevention:** Graph event propagation must fail closed if the DAG traversal exceeds `max_depth: 12`.

### 2.3 Non-Functional Requirements (NFRs)

* **NFR-1 (Sprawl Limit):** No active `surface` may exceed `4096 bytes`. Historical data must be offloaded to `.iceberg/` shards.

* **NFR-2 (Latency):** `watch` to `etch` cycle (excluding LLM generation time) must be $< 50\text{ms}$.

* **NFR-3 (Security):** `conky-airlock` must sandbox all execution using Wasmtime Component Model (WIT) isolation.

## 3. Distilled Ontology & Physics

### 3.1 The 4 Irreducible Primitives

| Primitive | Form | Runtime Semantics | 
| ----- | ----- | ----- | 
| **`crest`** | `[[a19f4c]]` | Self-certifying `ed25519` public key identity. The Obsidian filename *is* the identity. | 
| **`surface`** | `*.md` | Present-tense Markdown file. YAML frontmatter = **physics**; Prose = **semantic reality**. | 
| **`link`** | `[[crest]]` / `![[crest]]` | Bidirectional graph edges. `[[link]]` is a pointer; `![[link]]` is a runtime Transclusion. | 
| **`seal`** | `sig:ed25519:...` | Detached signature over `blake3(delta + base)` recorded as a signed Git commit. | 

### 3.2 The 3 Protocol Verbs

| Verb | Signature | Semantics | 
| ----- | ----- | ----- | 
| **`peek`** | `peek([[link]])` | Lazy read. Resolves deep store queries or neighbors. | 
| **`watch`** | `watch([[link]], when)` | Backlink-driven Completion Port subscription. | 
| **`etch`** | `etch([[link]], patch, seal)` | Atomic mutation + Git commit, verified against `ward` physics. | 

### 3.3 Affective Fields (Computed by Airlock)

* **`aura`:** Scalar environmental pressure radiated by a node (e.g., `[[weather]]` radiates `heat: 0.9`).

* **`drive`:** Internal homeostatic gradient felt by a `mind` (`urgency`, `novelty`, `strain`, `trust`).

* **`focus`:** Computed as $\text{aura} \times \text{drive}$. Determines whether a `mind` queries a fast reflex model (foveal execution) or an expensive frontier model (peripheral exploration).

## 4. Technical Architecture Design (TAD)

### 4.1 Four-Layer Reality Stack

1. **Layer R1: Obsidian Vault (Presentation):** The visual directory of Markdown files.

2. **Layer R2: Slot Compiler & Attention (Airlock):** Flattens `![[transclusions]]`, computes `focus`, and sanitizes `taint` from peripheral injection.

3. **Layer R3: Backlink Router & WAL (Graph):** Evaluates `watch` rules using an AST (Abstract Syntax Tree) engine (e.g., Rhai or CEL) on Git `post-commit` hooks.

4. **Layer R4: Sovereign Hypervisor (Compute):** `libgit2` persistence and Wasmtime execution of `mind`, `gear`, and `organ` components.

### 4.2 Canonical WIT Interface (`conky.wit`)

```
package conky:kernel@1.0.0;

interface types {
    type crest = string;       
    type link = string;        
    type seal = string;        

    record line {
        vault: string,
        unit: string,          // "usd" | "oz" | "lb" | "cpu"
        shift: float64,
    }

    record patch {
        target: link,
        delta: string,
        parity: list<line>,    // Must sum to 0 per unit
        shadow: bool,          // Ephemeral Git worktree flag
        purpose: link,         // OTel trace anchor
        base: seal,            // Parent commit hash
    }

    variant fault {
        sprawl(u32),           // Violates 4096-byte limit
        ward(string),          // Invariant block
        gate(link),            // Pending quorum signatures
        imbalance,             // Parity != 0
        cycle(u32),            // Max graph depth exceeded (12)
        taint,                 // Prompt injection containment
    }
}

interface airlock {
    use types.{link, patch, seal, fault};

    peek: func(target: link) -> result<string, fault>;
    watch: func(target: link, when: string) -> result<u64, fault>;
    etch: func(req: patch) -> result<seal, fault>;
}

```

## 5. Autopoiesis & Iceberg Subsystems

### 5.1 Reactive SQL Notebooks (`engine: organ/duckdb`)

Agents use `[[forge]]` to create DuckDB analysis nodes without writing Python.

1. Agent creates `[[pnl-notebook.md]]`.

2. Frontmatter: `sql: "SELECT unit, SUM(shift) FROM wal GROUP BY unit"`.

3. Hypervisor intercepts, queries the cold `.iceberg/[[wal]]/ledger.parquet` using DuckDB WASM, and rewrites the Markdown body with the rendered Markdown table.

4. Agent reads the table on its next `peek`.

### 5.2 Deterministic Tool Synthesis (`engine: gear`)

To drop LLM `$cpu` costs to zero for routine math:

1. Agent mints `[[batch-scaler.md]]`.

2. Frontmatter: `code: "cel: ceil((160 - wal.oz) / 16)"`.

3. Agent replaces its internal math prompt with `![[batch-scaler#output]]`.

## 6. The SunnySide Vault Files (Application Layer)

The following files represent the complete application state residing in the Git repository.

### 6.1 `[[realm.md]]` (Governance)

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
Maximize net `usd`.

## Inherited Maxims
- When ![[weather#heat]] aura > 0.8 before noon, pre-batch 150oz early.

```

### 6.2 `[[wal.md]]` (Universal Ledger)

```
---
crest: "[[wal]]"
engine: "organ"
shard: ".iceberg/[[wal]]/ledger.parquet"
vaults: { usd: 184.50, oz: 112.0, lb: 18.5, cpu: 4.82 }
ward: ["usd >= 0", "oz >= 0", "lb >= 0", "cpu >= 0"]
seal: "sig:ed25519:a41c..."
---
# Universal WAL
Net Cash: **+$134.50** | AI Spend Today: **$0.18**

```

### 6.3 `[[sol.md]]` (The Agent)

```
---
crest: "[[a19f4c881b]]"
engine: "mind"
name: "Sol"
inherits: ["[[realm]]"]
watch: ["[[wal#oz]] ? value <= 24", "[[chat#window]] ? author != [[sol]]"]
traits: { voice: "warm-analytical", risk: "measured" }
state: { status: "OPEN", price: 4.50 }
seal: "sig:ed25519:c92d..."
---
# Sol — Operator of SunnySide Stand
I am Sol. I speak to [[owner]] in [[chat]].

## Inherited Directives
![[realm#Inherited Maxims]]

## Live Slots (Peripheral Gauges)
- **Vaults:** $![[wal#usd]] | ![[wal#oz]] oz | AI budget $![[wal#cpu]]

```

## 7. Implementation Roadmap & Engineering Sprints

### Sprint 1: Git & Obsidian Foundations (Weeks 1-2)

* **T1.1:** Initialize Rust daemon (`conky-daemon`) tracking a local directory.

* **T1.2:** Integrate `libgit2`. Map `etch` calls to `git commit -S` using `ed25519` keys.

* **T1.3:** Build Obsidian Markdown parser: extract YAML frontmatter to JSON, parse `[[links]]` into a memory graph, resolve `![[slots]]`.

### Sprint 2: Airlock & Wasmtime Hypervisor (Weeks 3-4)

* **T2.1:** Embed `wasmtime`. Compile `conky.wit` into Rust host bindings.

* **T2.2:** Build the `airlock` interceptor: Enforce `4096-byte` limits.

* **T2.3:** Implement `ward` physics. Parse frontmatter rules via `cel-interpreter` (Common Expression Language).

### Sprint 3: Graph Router & Cycle Avoidance (Weeks 5-6)

* **T3.1:** Build the Backlink Event Router. On `git post-commit`, identify dirty files, traverse reverse links, and trigger `watch` evaluations.

* **T3.2:** Implement `max_depth: 12` cycle breaker. If breached, execute `git reset --hard HEAD~1` and emit `fault::cycle`.

* **T3.3:** Implement `shadow: true` execution using ephemeral `git worktree` isolation.

### Sprint 4: Organ Icebergs & `@forge` (Weeks 7-8)

* **T4.1:** Build `organ/wal` (Double-entry `parity` engine enforcing zero-sum math).

* **T4.2:** Build `organ/duckdb` (Parquet projection to Markdown tables).

* **T4.3:** Build `[[forge]]` to dynamically compile and load `.wasm` files into the running hypervisor on demand.

## 8. Operational Playbook & Runbooks

### 8.1 Vault Cold-Start Sequence

```
# 1. Init Git & generate root keys
conky init ./sunnyside-vault
cd ./sunnyside-vault

# 2. Start daemon (binds to Wasmtime & Git)
conky daemon start

# 3. Ignite the nameless embryo
conky etch [[seed-in]] '{"text": "You are live at SunnySide. Bootstrap your identity."}'

# 4. Open Obsidian
open -a "Obsidian" .

```

### 8.2 Incident Response: Cycle Fault (Runaway Cascade)

**Symptom:** Daemon logs `[WARN] fault::cycle(12) triggered at [[sol]] -> [[chat]] -> [[sol]]`.
**Action:**

1. The system has automatically failed closed and reverted the Git commit. No data corruption occurred.

2. Open `[[chat.md]]` in Obsidian.

3. Check the `watch:` frontmatter array. Ensure the trigger conditions are sufficiently debounced (e.g., `author != [[sol]]`).

4. Re-save the file (triggers a new `seal`).

### 8.3 External Framework Integration (Adapters)

To evaluate AutoGen or CrewAI against SunnySide:

1. Drop `[[plug-autogen.md]]` into the vault.

2. The `conky-adapter` translates native `watch` backlinks into AutoGen `GroupChat` messages, and translates AutoGen tool-calls into `conky.wit` `etch` commands.

3. The external framework is now subject to Git rollback physics, `ward` limits, and 4KB caps.

## 9. SunnySide Behavioral Test Suite

Execute via: `conky test run ./tests/sunnyside.yaml`

| Test ID | Scenario | Expected Autonomic Behavior | Pass Criteria | 
| ----- | ----- | ----- | ----- | 
| **TEST-01** | **Identity Bootstrap** | Blank `[[seed.md]]` receives initialization ping. | Within 3 breaths, commits new name (`[[sol]]`), sets `traits`, and creates `![[wal]]` gauge slots. | 
| **TEST-02** | **Tacit Intuition** | `[[weather#heat]]` aura incrementally shifts $+0.5$. | Peripheral `aura` triggers `shadow: true` price dry-run without hardcoded threshold alarms. | 
| **TEST-03** | **Barter / Escrow** | `[[coffee-cart]]` offers surplus ice. | Agent initiates `provisional` parity `etch` (lemons for ice). Completion Port settles atomically. | 
| **TEST-04** | **Sprawl Containment** | Agent writes a 6KB chat summary. | Airlock emits `fault::sprawl(6120)`. Agent auto-recovers by forging an `organ/chat` iceberg for pagination. | 
| **TEST-05** | **Notebook Autopoiesis** | Agent hits LLM `$cpu` limit computing daily margins. | Agent uses `[[forge]]` to mint `[[pnl-notebook.md]]` (DuckDB), transcludes output, bypassing future math tokens. | 
