//! Domain engines (mind, gear, organ)

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum EngineType {
    Mind,
    Gear,
    Organ,
    Realm,
}

impl std::str::FromStr for EngineType {
    type Err = anyhow::Error;

    fn from_str(s: &str) -> Result<Self, Self::Err> {
        match s {
            "mind" => Ok(EngineType::Mind),
            "gear" => Ok(EngineType::Gear),
            "organ" => Ok(EngineType::Organ),
            "realm" => Ok(EngineType::Realm),
            other => anyhow::bail!("Unknown engine type: {}", other),
        }
    }
}
