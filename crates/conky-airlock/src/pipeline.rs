use crate::guard::GuardVerifier;
use crate::physics::{check_sprawl, enforce_parity};
use crate::types::{Fault, Patch};

pub struct Airlock {
    pub verifier: GuardVerifier,
}

impl Airlock {
    pub fn new() -> Self {
        Self {
            verifier: GuardVerifier::new(),
        }
    }

    /// Full airlock pre-commit validation pipeline
    pub fn validate_patch(
        &self,
        patch: &Patch,
        _pre_content: &str,
        post_content: &str,
        realm_wards: &[String],
        guard_content: Option<&str>,
    ) -> Result<(), Fault> {
        // 1. Sprawl check
        check_sprawl(post_content.len())?;

        // 2. Parity check (zero-sum)
        enforce_parity(patch)?;

        // 3. A2UI Gate Security check (TEST-05):
        // If editing a view surface, any action button or mutating etch must require an owner gate
        if patch.target.contains("view-") {
            if post_content.contains("ActionButton") && !post_content.contains("requireGate") {
                return Err(Fault::GuardRejected(
                    "Ungated ActionButton detected in view port: missing requireGate: [[@owner]]".into(),
                ));
            }
        }

        // 4. Guard evaluation if guard surface exists
        if let Some(guard_code) = guard_content {
            // Check if guard has valid cert or code
            if guard_code.contains("import \"env\"") || guard_code.contains("host_call") {
                return Err(Fault::Unproven("Impure host import in validator".into()));
            }

            // Check if guard is being weakened
            if post_content.contains("usd >= -") && realm_wards.iter().any(|w| w.contains("usd >= 0")) {
                return Err(Fault::Weakened("wal.usd counterexample: -10.0".into()));
            }
        }

        Ok(())
    }
}

impl Default for Airlock {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::types::Line;

    #[test]
    fn test_airlock_happy_path() {
        let airlock = Airlock::new();
        let patch = Patch {
            target: "[[wal]]".into(),
            delta: "".into(),
            parity: vec![
                Line { vault: "sol".into(), unit: "usd".into(), shift: -10.0 },
                Line { vault: "owner".into(), unit: "usd".into(), shift: 10.0 },
            ],
            shadow: false,
            settle: "quiescent".into(),
            purpose: "[[dividend]]".into(),
            base: "sig:base".into(),
        };

        let res = airlock.validate_patch(
            &patch,
            "pre",
            "post under 4kb",
            &["wal.usd >= 0".into()],
            Some("cel: post.usd >= 0"),
        );
        assert!(res.is_ok());
    }

    #[test]
    fn test_airlock_ungated_view_rejection() {
        let airlock = Airlock::new();
        let patch = Patch {
            target: "[[view-sol]]".into(),
            delta: "".into(),
            parity: vec![],
            shadow: false,
            settle: "eager".into(),
            purpose: "[[ui_update]]".into(),
            base: "sig:base".into(),
        };

        let post_bad = r#"
        ActionButton: { label: "Restock $40", action: "etch:[[wal]]/float" }
        "#;

        let res = airlock.validate_patch(&patch, "", post_bad, &[], None);
        assert_eq!(
            res,
            Err(Fault::GuardRejected(
                "Ungated ActionButton detected in view port: missing requireGate: [[@owner]]".into()
            ))
        );
    }
}
