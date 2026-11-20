use conky_airlock::types::{Fault, Patch};
use conky_airlock::Airlock;

pub struct ExternalHarnessAdapter {
    airlock: Airlock,
}

impl ExternalHarnessAdapter {
    pub fn new() -> Self {
        Self {
            airlock: Airlock::new(),
        }
    }

    /// Translates an external tool call into a conky etch patch
    pub fn execute_tool_call(
        &self,
        framework: &str,
        tool_name: &str,
        target_link: &str,
        arguments_json: &str,
    ) -> Result<String, Fault> {
        tracing::info!(
            "Harness bridge [{}]: tool '{}' mutating '{}'",
            framework,
            tool_name,
            target_link
        );

        let patch = Patch {
            target: target_link.to_string(),
            delta: arguments_json.to_string(),
            parity: vec![],
            shadow: false,
            settle: "eager".to_string(),
            purpose: format!("[[plug-{}#{tool_name}]]", framework.to_lowercase()),
            base: "".to_string(),
        };

        self.airlock
            .validate_patch(&patch, "", arguments_json, &[], None)?;
        Ok(format!("sig:ed25519:bridge_{framework}_{tool_name}"))
    }
}

impl Default for ExternalHarnessAdapter {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_langgraph_adapter() {
        let adapter = ExternalHarnessAdapter::new();
        let seal = adapter
            .execute_tool_call("langgraph", "update_price", "[[sol]]", r#"{"price": 4.75}"#)
            .unwrap();
        assert!(seal.starts_with("sig:ed25519:bridge_langgraph_update_price"));
    }
}
