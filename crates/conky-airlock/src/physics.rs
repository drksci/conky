use crate::types::{Fault, Patch};
use std::collections::HashMap;

pub const MAX_SURFACE_BYTES: usize = 4096;

pub fn enforce_parity(patch: &Patch) -> Result<(), Fault> {
    if patch.parity.is_empty() {
        return Ok(());
    }

    let mut ledgers: HashMap<String, f64> = HashMap::new();

    for line in &patch.parity {
        *ledgers.entry(line.unit.clone()).or_insert(0.0) += line.shift;
    }

    for (unit, sum) in ledgers {
        // Allow tiny floating point epsilon, otherwise strict 0
        if sum.abs() > 1e-9 {
            tracing::error!("Imbalance in unit {}: net shift = {}", unit, sum);
            return Err(Fault::Imbalance);
        }
    }
    Ok(())
}

pub fn check_sprawl(content_len: usize) -> Result<(), Fault> {
    if content_len > MAX_SURFACE_BYTES {
        Err(Fault::Sprawl(content_len as u32))
    } else {
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::types::Line;

    #[test]
    fn test_zero_sum_parity() {
        let patch = Patch {
            target: "[[wal]]".into(),
            delta: "".into(),
            parity: vec![
                Line {
                    vault: "sol".into(),
                    unit: "usd".into(),
                    shift: -5.0,
                },
                Line {
                    vault: "supplier".into(),
                    unit: "usd".into(),
                    shift: 5.0,
                },
            ],
            shadow: false,
            settle: "quiescent".into(),
            purpose: "[[buy]]".into(),
            base: "sig:dummy".into(),
        };
        assert!(enforce_parity(&patch).is_ok());
    }

    #[test]
    fn test_imbalance_detected() {
        let patch = Patch {
            target: "[[wal]]".into(),
            delta: "".into(),
            parity: vec![
                Line {
                    vault: "sol".into(),
                    unit: "usd".into(),
                    shift: -5.0,
                },
                Line {
                    vault: "supplier".into(),
                    unit: "usd".into(),
                    shift: 4.5,
                },
            ],
            shadow: false,
            settle: "quiescent".into(),
            purpose: "[[buy]]".into(),
            base: "sig:dummy".into(),
        };
        assert_eq!(enforce_parity(&patch), Err(Fault::Imbalance));
    }
}
