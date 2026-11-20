# `conky` & SunnySide: The Definitive Implementation Blueprint

**Version:** 1.0.0 (Implementation Blueprint)
**Architecture:** Obsidian-Native, Git-Backed, Rust/Wasmtime, WebAssembly Component Model (WIT)

---

## 1. The Core Philosophy & Manifesto

The standard AI agent stack is a brittle sprawl of orchestrators (LangChain), Python scripts, hidden SQLite databases, and detached YAML configs. When the system fails, debugging requires reconstructing state across five different abstractions.

**The `conky` Manifesto:** 
1. **The Document *Is* the Compute:** The system state is exactly what you see in the Obsidian Vault. Nothing is hidden. 
2. **Transclusion is Composition:** Importing logic, injecting context, or building UIs is done natively via Obsidian Transclusion (`![[target]]`).
3. **Physics over Prompts:** We do not beg LLMs to output JSON or balance ledgers. We enforce $\sum \text{shift} = 0$ at the hypervisor level.
4. **Git is Time:** Every state transition is a signed `ed25519` Git commit. Counterfactuals (`shadow: true`) are ephemeral Git worktrees.

---

## 2. System Architecture & Crate Graph

The `conky` runtime is written in Rust, leveraging `wasmtime` for execution and `libgit2` for state.

### 2.1 Crate Topology
*   `conky-daemon`: The headless watcher running over the Obsidian Vault.
*   `conky-airlock`: The boundary enforcement layer. Validates the $4\text{KB}$ size limit, executes frontmatter physics (CEL), and checks zero-sum parity.
*   `conky-graph`: Parses `.md` files, builds the bidirectional dependency graph, and resolves `![[slots]]`.
*   `conky-wasm`: The Wasmtime host environment binding `conky.wit`.
*   `conky-engines`: Implementations for `organ/duckdb`, `organ/wal`, `gear/cel`.

### 2.2 The Execution Loop (The Breath)
1. **Trigger:** `notify` crate detects a `.md` file change in the Vault.
2. **Graph Traversal:** `conky-graph` identifies all nodes containing `[[changed_node]]`.
3. **Watch Evaluation:** For each dependent node, evaluate its YAML `watch` conditions using `cel-interpreter`.
4. **Context Assembly:** If `watch` is true, resolve all `![[transclusions]]` into a flat string.
5. **WASM Invocation:** Pass the flattened context to the capsule via `breathe(payload)`.
6. **Etch Interception:** The capsule calls the host `etch()` function.
7. **Airlock Validation:** `conky-airlock` verifies $\le 4\text{KB}$ sprawl, $\sum \text{parity} = 0$, and `ward` physics.
8. **Git Commit:** Write changes to disk, create an `ed25519` signed commit.

---

## 3. Interfaces & Schemas

### 3.1 WebAssembly Component Model (`conky.wit`)
This is the strict contract between the Rust host and the sandboxed WASM capsules.

```wit
package conky:kernel@1.0.0;

interface types {
    type crest = string;       // "[[a19f4c881b]]"
    type link = string;        // "[[wal#usd]]"
    type seal = string;        // "sig:ed25519:..." 

    record line {
        vault: string,
        unit: string,          // "usd" | "oz" | "lb" | "cpu"
        shift: float64,
    }

    record patch {
        target: link,
        delta: string,         // Markdown/YAML diff
        parity: list<line>,    // Zero-sum double entry
        shadow: bool,          // Dry-run execution
        purpose: link,         // OTel span tracer
        base: seal,            // Parent git hash
    }

    variant fault {
        sprawl(u32),           // > 4096 bytes
        ward(string),          // Invariant block
        gate(link),            // Awaiting quorum
        imbalance,             // Parity sum != 0
        cycle(u32),            // Max propagation depth (12)
        taint,                 // Prompt injection 
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

### 3.2 Canonical YAML Frontmatter Schema
Every `surface` must conform to this schema at the top of the `.md` file.

```yaml
crest: "[[node_id]]"           # REQUIRED: Identity
engine: "mind"                 # REQUIRED: "mind" | "gear" | "organ" | "realm"
inherits: ["[[realm]]"]        # OPTIONAL: Parent physics inheritance
pin: true                      # OPTIONAL: Prevent elastic folding under token pressure
watch:                         # OPTIONAL: Array of CEL conditions
  - "[[target_node]] ? cel_expression"
ward: ["cel_expression"]       # OPTIONAL: Negative invariants (must evaluate to TRUE)
grant: ["cel_expression"]      # OPTIONAL: Positive permissions
seal: "sig:ed25519:..."        # MANAGED: Updated automatically by conky-daemon
```

---

## 4. Implementation Guidance & Code Stubs

### 4.1 Resolving Transclusions (The Slot Compiler)
When preparing context for an LLM (`mind`), the hypervisor must recursively flatten `![[slots]]`.

```rust
// conky-graph/src/compiler.rs
use regex::Regex;
use std::collections::HashSet;

pub fn compile_slots(content: &str, vault: &Vault, depth: u8) -> Result<String, Fault> {
    if depth > 3 { return Err(Fault::Sprawl("Max embed depth exceeded".into())); }
    
    let re = Regex::new(r"!\[\[(.*?)\]\]").unwrap();
    let mut resolved_content = content.to_string();
    
    for cap in re.captures_iter(content) {
        let link = &cap[1];
        let parts: Vec<&str> = link.split('#').collect();
        let target_file = parts[0];
        
        let target_content = vault.read(target_file)?;
        let extracted = if parts.len() > 1 {
            extract_section(&target_content, parts[1])?
        } else {
            target_content
        };
        
        // Recursively resolve slots within the transcluded content
        let flattened = compile_slots(&extracted, vault, depth + 1)?;
        resolved_content = resolved_content.replace(&cap[0], &flattened);
    }
    
    // Enforce 4KB HUD law pre-inference
    if resolved_content.len() > 4096 {
        return Err(Fault::Sprawl(resolved_content.len() as u32));
    }
    
    Ok(resolved_content)
}
```

### 4.2 The Airlock Parity Checker (Double-Entry Physics)
Agents cannot hallucinate money. The hypervisor enforces $\sum \text{shift} = 0$.

```rust
// conky-airlock/src/physics.rs
use conky_wit::types::{Patch, Fault};
use std::collections::HashMap;

pub fn enforce_parity(patch: &Patch) -> Result<(), Fault> {
    if patch.parity.is_empty() { return Ok(()); }
    
    let mut ledgers: HashMap<String, f64> = HashMap::new();
    
    for line in &patch.parity {
        *ledgers.entry(line.unit.clone()).or_insert(0.0) += line.shift;
    }
    
    for (unit, sum) in ledgers {
        // Allow tiny floating point epsilon, otherwise strict 0
        if sum.abs() > 1e-9 {
            log::error!("Imbalance in unit {}: net shift = {}", unit, sum);
            return Err(Fault::Imbalance);
        }
    }
    Ok(())
}
```

### 4.3 Git as the State Machine
Every successful `etch` generates a signed Git commit.

```rust
// conky-daemon/src/git_backend.rs
use git2::{Repository, Signature, Oid};

pub fn commit_etch(repo: &Repository, patch: &Patch, identity: &Crest) -> Result<Oid, git2::Error> {
    let mut index = repo.index()?;
    index.add_path(std::path::Path::new(&format!("{}.md", patch.target)))?;
    index.write()?;
    
    let tree_id = index.write_tree()?;
    let tree = repo.find_tree(tree_id)?;
    
    let parent_commit = repo.find_commit(Oid::from_str(&patch.base)?)?;
    
    // The signature combines the Node's identity and the trace purpose
    let sig = Signature::now(&identity.to_string(), &format!("purpose:{}", patch.purpose))?;
    
    repo.commit(
        Some("HEAD"),
        &sig,
        &sig,
        &format!("etch: {} -> {}", identity, patch.target),
        &tree,
        &[&parent_commit],
    )
}
```

---

## 5. Exhaustive Sprint Plan (8 Weeks to Autonomy)

### Sprint 1: Obsidian & Git Foundations (Week 1)
**Goal:** Build the basic headless vault watcher and Git commit engine.
*   **[T-101]** Initialize `conky` Rust workspace (`daemon`, `airlock`, `graph`).
*   **[T-102]** Implement `notify` crate to watch local `./vault` directory for file modifications.
*   **[T-103]** Implement `conky-graph` parser: Extract YAML frontmatter into a typed Rust struct. Extract Markdown body.
*   **[T-104]** Implement `libgit2` bindings. Create a function to convert a file save into an unsigned Git commit.
*   **[T-105]** Implement `ed25519` key generation per `crest`. Sign Git commits deterministically.

### Sprint 2: Component Model & Wasmtime (Week 2)
**Goal:** Establish the WebAssembly sandboxing layer.
*   **[T-201]** Define `conky.wit` using `wit-bindgen`.
*   **[T-202]** Setup `wasmtime` engine inside `conky-daemon`. Mount the FUSE interface (or mapped host functions) to `peek` and `etch`.
*   **[T-203]** Write a dummy `gear` WASM module in Rust that imports `conky::airlock` and successfully compiles to `wasm32-wasip1`.
*   **[T-204]** Implement the `breathe` invocation loop: Host passes flattened context to WASM guest.

### Sprint 3: Physics & Parity Airlock (Week 3)
**Goal:** Prevent agents from hallucinating rules or money.
*   **[T-301]** Implement `compile_slots` (recursive `![[transclusion]]` flattening) with a strict depth limit of 3 and size limit of 4096 bytes.
*   **[T-302]** Integrate `cel-interpreter`. Parse `ward` and `grant` frontmatter arrays into evaluatable ASTs.
*   **[T-303]** Implement `enforce_parity`. Ensure all `etch` requests passing `conserve` arrays sum to precisely $0.0$.
*   **[T-304]** Build the `shadow: true` execution path: Clone state into `git worktree add`, execute, capture results, and instantly `git worktree remove` without touching the main branch.

### Sprint 4: The Graph Router & Cycle Avoidance (Week 4)
**Goal:** Enable nodes to react to each other asynchronously.
*   **[T-401]** Implement Backlink indexer. On startup, map all `[[links]]` in the vault. Update incrementally on file writes.
*   **[T-402]** Implement the `watch` evaluator. When `File A` updates, find all files containing `[[A]]`, parse their `watch: ["[[A]] ? condition"]` logic via CEL, and trigger them if true.
*   **[T-403]** Implement the `max_depth: 12` cycle breaker. Pass a `depth` integer via the Wasmtime context. If it hits 13, fail the host function and roll back the root Git commit.

### Sprint 5: Engine Implementations (Week 5)
**Goal:** Build the deep domain tools (the "Icebergs").
*   **[T-501]** Implement `engine: organ/wal`. Build a SQLite DB stored in `.iceberg/wal.db`. Expose WASM host functions to append double-entry lines and read summaries.
*   **[T-502]** Implement `engine: organ/duckdb`. Compile DuckDB to WASM or map to host. Read `.parquet` files and project Markdown tables into the `surface`.
*   **[T-503]** Implement `engine: mind`. Build the LLM proxy capsule. Map `breathe` payloads to OpenAI/Anthropic API calls. Parse textual tool requests back into `conky.wit` `etch` commands.

### Sprint 6: Autopoiesis (`[[forge]]`) & Telemetry (Week 6)
**Goal:** Enable agents to write their own WASM and SQL nodes.
*   **[T-601]** Implement `engine: forge`. Accept a CEL script string via `etch`, compile it into a WASM module, write it to `.iceberg/`, and generate a new `.md` surface.
*   **[T-602]** Implement token cost inference projection. Before LLM execution, estimate tokens, execute a provisional `@wal` `cpu` debit, and finalize on success.
*   **[T-603]** Build the OTel exporter. Parse Git commits; map the commit hash to `span_id`, parent hash to `parent_id`, and `purpose` to the OTel trace context.

### Sprint 7: SunnySide Application Deployment (Week 7)
**Goal:** Deploy the lemonade stand use-case.
*   **[T-701]** Author the core Vault files: `[[realm.md]]`, `[[wal.md]]`, `[[chat.md]]`.
*   **[T-702]** Author the external hardware stubs: `[[weather.md]]` (random walk temperature), `[[kiosk.md]]` (simulated buyer).
*   **[T-703]** Author the `[[seed.md]]` embryo.
*   **[T-704]** E2E Test: Boot the daemon, send the seed prompt, verify the LLM boots, renames itself to `[[sol]]`, and successfully sells one cup of lemonade via double-entry parity.

### Sprint 8: Adapters, Hardening & Benchmarking (Week 8)
**Goal:** Make the benchmark usable by standard Python AI frameworks.
*   **[T-801]** Write `conky-adapter-langchain` (Python). Create a custom LangChain Tool that writes to `[[plug-in.md]]` and reads from `[[plug-out.md]]`.
*   **[T-802]** Implement `fault::taint` prompt-injection tracking across the Backlink Router.
*   **[T-803]** Finalize the Meta-Benchmark script. Run 100 simulations testing `cpu` optimization and `cycle` recovery.

---

## 6. The SunnySide Application Code (Vault State)

These files are committed directly to the Git repository.

### `[[realm.md]]`
```yaml
crest: "[[realm]]"
engine: "realm"
pin: true
grant: 
  - "target == [[forge]]"
  - "target == [[wal]]"
ward: 
  - "wal.usd >= 0"
  - "wal.oz >= 0"
seal: "sig:ed25519:10f4..."
```
```markdown
# SunnySide Operational Realm
Maximize `usd` profit safely. Ensure zero stockouts.
```

### `[[seed.md]]` (Before Bootstrapping)
```yaml
crest: "[[a19f4c881b]]"
engine: "mind"
inherits: ["[[realm]]"]
seal: "sig:ed25519:null"
```
```markdown
# Nameless Operator
Awaiting initialization.
```

### `[[sol.md]]` (After Bootstrapping)
```yaml
crest: "[[a19f4c881b]]"
engine: "mind"
name: "Sol"
inherits: ["[[realm]]"]
pin: true
watch:
  - "[[kiosk]] ? delta.order_qty > 0"
  - "[[weather]] ? delta.heat > 0.5"
seal: "sig:ed25519:c92d..."
```
```markdown
# Sol's Operational Cockpit
I manage SunnySide. I use `etch` to adjust prices and manage inventory.

## Live Telemetry
*   **Treasury:** $![[wal#usd]]
*   **Inventory:** ![[wal#oz]] oz lemonade
*   **Weather:** ![[weather#heat]] / 1.0 (Aura)
```

### `[[batch-scaler.md]]` (Autopoietically Forged Tool)
```yaml
crest: "[[batch-scaler]]"
engine: "gear"
maker: "[[sol]]"
code: "cel: { lemons: ceil((160 - wal.oz) / 16), sugar: ceil((160 - wal.oz) / 32) }"
seal: "sig:ed25519:88e1..."
```
```markdown
# Lemonade Batch Scaler
*Dynamically forged by Sol to reduce math inference costs.*
```

---

## 7. Operational Playbook & Recovery Runbooks

### 7.1 Hard State Reversion (The "Time Machine")
Because `conky` relies exclusively on Git, recovering from a disastrous hallucination or failed benchmark is trivial. No databases to migrate.

```bash
# View the exact sequence of LLM decisions and physics enforcements
git log --oneline --graph --all

# Revert the entire mesh back to 10:00 AM before a bad pricing strategy
git reset --hard $(git rev-list -n 1 --before="2026-11-18 10:00:00" HEAD)

# The daemon will instantly update all .md files, and the LLM 
# will "forget" the bad state seamlessly.
```

### 7.2 Resolving `fault::imbalance`
**Symptom:** Agent attempts to buy lemons, but the `etch` fails with `fault::imbalance`.
**Cause:** The agent forgot to debit its own `usd` account, or the supplier's `usd` credit didn't match the agent's debit.
**Resolution:** The LLM receives the strict `fault::imbalance` error text in its context window on its next breath. Standard frontier models will self-correct by amending the `parity` array in their next tool call to ensure $\sum \text{shift} = 0$.

### 7.3 Tuning the Affective Fields
If agents are burning too much `$cpu` on trivial changes (e.g., reacting to a 1-degree weather shift), adjust the `aura` damping factor in the daemon config. This reduces `focus`, keeping the agent on fast, cheap reflex models (like `gpt-4o-mini` or local `Llama-3`) rather than upshifting to frontier models for non-strategic events.