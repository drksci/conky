use serde::{Deserialize, Serialize};
use thiserror::Error;

pub type Crest = String;
pub type Link = String;
pub type Seal = String;

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
    pub purpose: Link,
    pub base: Seal,
}

#[derive(Debug, Clone, PartialEq, Eq, Error, Serialize, Deserialize)]
pub enum Fault {
    #[error("Sprawl error: {0} bytes exceeds 4096 limit")]
    Sprawl(u32),

    #[error("Ward invariant broken: {0}")]
    Ward(String),

    #[error("Gate awaiting quorum: {0}")]
    Gate(Link),

    #[error("Imbalance: net zero-sum parity != 0")]
    Imbalance,

    #[error("Cycle detected: depth {0} exceeded maximum")]
    Cycle(u32),

    #[error("Taint detected: prompt injection")]
    Taint,
}
