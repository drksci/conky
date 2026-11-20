use serde::{Deserialize, Serialize};
use thiserror::Error;

pub type Crest = String; // "[[a19f4c881b]]"
pub type Link = String; // "[[wal#usd]]"
pub type Seal = String; // "sig:ed25519:..."

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct Line {
    pub vault: String,
    pub unit: String, // "usd" | "oz" | "lb" | "cpu"
    pub shift: f64,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct Patch {
    pub target: Link,
    pub delta: String,
    pub parity: Vec<Line>,
    pub shadow: bool,
    #[serde(default = "default_settle")]
    pub settle: String, // "eager" | "quiescent"
    pub purpose: Link,
    pub base: Seal,
}

fn default_settle() -> String {
    "quiescent".to_string()
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct PulseFrame {
    pub source: Link,
    pub seq: u64,
    pub rolling_hash: String, // blake3 chain digest
    pub patch_json: String,   // Incremental JSONL / A2UI delta
    pub depth: u8,
}

#[derive(Debug, Clone, PartialEq, Eq, Error, Serialize, Deserialize)]
pub enum Fault {
    #[error("Sprawl error: {0} bytes exceeds 4096 limit")]
    Sprawl(u32),

    #[error("Ward invariant broken: {0}")]
    Ward(String),

    #[error("Guard rejected mutation: {0}")]
    GuardRejected(String),

    #[error("Unproven validator: {0}")]
    Unproven(String),

    #[error("Weakened invariant: SMT counterexample {0}")]
    Weakened(String),

    #[error("Gate awaiting quorum: {0}")]
    Gate(Link),

    #[error("Imbalance: net zero-sum parity != 0")]
    Imbalance,

    #[error("Cycle detected: depth {0} exceeded maximum (12)")]
    Cycle(u8),

    #[error("Taint detected: prompt injection")]
    Taint,
}
