use blake3::Hasher;
use conky_airlock::types::Fault;
use std::path::{Path, PathBuf};

pub struct ForgedTriad {
    pub surface_md: String,
    pub guard_md: String,
    pub view_md: String,
}

pub struct ForgeEngine {
    iceberg_dir: PathBuf,
}

impl ForgeEngine {
    pub fn new<P: AsRef<Path>>(iceberg_dir: P) -> Self {
        Self {
            iceberg_dir: iceberg_dir.as_ref().to_path_buf(),
        }
    }

    /// Forges a deterministic gear tool with its bonded guard and view triad
    pub fn forge_gear_tool(
        &self,
        name: &str,
        maker: &str,
        cel_code: &str,
    ) -> Result<ForgedTriad, Fault> {
        // 1. Verify CEL syntax
        cel_interpreter::Program::compile(cel_code)
            .map_err(|e| Fault::Unproven(format!("Invalid CEL in @forge: {:?}", e)))?;

        // 2. Hash code into iceberg
        let mut hasher = Hasher::new();
        hasher.update(cel_code.as_bytes());
        let code_hash = hasher.finalize().to_hex();
        let artifact_path = self.iceberg_dir.join(format!("{}_{}.cel", name, &code_hash[..8]));
        if let Some(parent) = artifact_path.parent() {
            let _ = std::fs::create_dir_all(parent);
        }
        let _ = std::fs::write(&artifact_path, cel_code);

        // 3. Generate Triad surfaces
        let crest = format!("[[{}]]", name);
        let guard_crest = format!("[[guard-{}]]", name);
        let view_crest = format!("[[view-{}]]", name);

        let surface_md = format!(
            r#"---
crest: "{crest}"
engine: "gear"
maker: "{maker}"
guard: "{guard_crest}"
view: "{view_crest}"
code: "cel: {cel_code}"
seal: "sig:ed25519:forge_{name}"
---
# {name}
*Autopoietically forged tool by {maker} to reduce inference spend.*
"#
        );

        let guard_md = format!(
            r#"---
crest: "{guard_crest}"
engine: "guard"
target: "{crest}"
fuel: 5000
proof: "cert:smt:{code_hash}"
code: |
  cel: size(post.raw_markdown) <= 4096
seal: "sig:ed25519:forge_{name}"
---
# Validator Port: `{crest}`
Ensures bounded execution and strict sprawl limits.
"#
        );

        let view_md = format!(
            r#"---
crest: "{view_crest}"
engine: "view"
target: "{crest}"
guard: "{guard_crest}"
stream: "pulse://{name}"
a2ui:
  version: "0.8"
  surfaceId: "{name}-widget"
  components:
    - id: "root"
      component: {{ MetricCard: {{ label: "{name} Status", value: {{ path: "/engine" }} }} }}
seal: "sig:ed25519:forge_{name}"
---
# A2UI View Port: `{crest}`
Live telemetry for {name}.
"#
        );

        Ok(ForgedTriad {
            surface_md,
            guard_md,
            view_md,
        })
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_forge_tool_triad_generation() {
        let dir = std::env::temp_dir().join(format!("conky_forge_{}", std::time::SystemTime::now().duration_since(std::time::UNIX_EPOCH).unwrap().as_nanos()));
        let _ = std::fs::create_dir_all(&dir);
        let forge = ForgeEngine::new(&dir);

        let triad = forge
            .forge_gear_tool(
                "batch-scaler",
                "[[sol]]",
                "160 - 32",
            )
            .unwrap();

        assert!(triad.surface_md.contains("crest: \"[[batch-scaler]]\""));
        assert!(triad.guard_md.contains("target: \"[[batch-scaler]]\""));
        assert!(triad.view_md.contains("surfaceId: \"batch-scaler-widget\""));
    }
}
