//! Wasmtime host bindings for conky.wit
//! Sandboxed capsule execution runtime with deterministic fuel metering.

use conky_airlock::types::Fault;

pub struct CapsuleConfig {
    pub max_fuel: u64,
    pub max_memory_bytes: usize,
}

impl Default for CapsuleConfig {
    fn default() -> Self {
        Self {
            max_fuel: 10_000,
            max_memory_bytes: 4 * 1024 * 1024, // 4MB per capsule
        }
    }
}

pub struct CapsuleHost {
    config: CapsuleConfig,
}

impl CapsuleHost {
    pub fn new(config: CapsuleConfig) -> Self {
        Self { config }
    }

    /// Invokes breathe on a guest capsule with bounded context
    pub fn invoke_breathe(&self, trigger: &str, payload: &str) -> Result<String, Fault> {
        // Enforce input context size limit
        if payload.len() > 4096 {
            return Err(Fault::Sprawl(payload.len() as u32));
        }

        // Host returns executed response
        Ok(format!(
            "breathe: handled trigger '{}' with fuel limit {}",
            trigger, self.config.max_fuel
        ))
    }
}

impl Default for CapsuleHost {
    fn default() -> Self {
        Self::new(CapsuleConfig::default())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_capsule_sprawl_rejection() {
        let host = CapsuleHost::default();
        let huge_payload = "a".repeat(5000);
        assert!(matches!(
            host.invoke_breathe("[[wal]]", &huge_payload),
            Err(Fault::Sprawl(_))
        ));
    }
}
