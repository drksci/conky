pub mod cel_eval;
pub mod forge;
pub mod sql_projector;
pub mod wal;

pub use cel_eval::CelEvaluator;
pub use forge::{ForgeEngine, ForgedTriad};
pub use sql_projector::SqlProjector;
pub use wal::WalEngine;

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum EngineType {
    Mind,
    Gear,
    Organ,
    Realm,
    Guard,
    View,
}

impl std::str::FromStr for EngineType {
    type Err = anyhow::Error;

    fn from_str(s: &str) -> Result<Self, Self::Err> {
        match s {
            "mind" => Ok(EngineType::Mind),
            "gear" => Ok(EngineType::Gear),
            "organ" | "organ/wal" | "organ/duckdb" => Ok(EngineType::Organ),
            "realm" => Ok(EngineType::Realm),
            "guard" => Ok(EngineType::Guard),
            "view" => Ok(EngineType::View),
            other => anyhow::bail!("Unknown engine type: {}", other),
        }
    }
}
