use conky_airlock::enforce_parity;
use conky_airlock::types::{Fault, Line};
use rusqlite::{params, Connection};
use std::collections::HashMap;
use std::path::{Path, PathBuf};

pub struct WalEngine {
    db_path: PathBuf,
}

impl WalEngine {
    pub fn open_or_init<P: AsRef<Path>>(iceberg_dir: P) -> Result<Self, anyhow::Error> {
        let iceberg = iceberg_dir.as_ref();
        std::fs::create_dir_all(iceberg)?;
        let db_path = iceberg.join("wal.db");

        let conn = Connection::open(&db_path)?;
        conn.execute_batch(
            r#"
            CREATE TABLE IF NOT EXISTS ledger (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts DATETIME DEFAULT CURRENT_TIMESTAMP,
                vault TEXT NOT NULL,
                unit TEXT NOT NULL,
                shift REAL NOT NULL,
                purpose TEXT NOT NULL,
                pulse TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_ledger_vault_unit ON ledger(vault, unit);
            "#,
        )?;

        Ok(Self { db_path })
    }

    pub fn append_transaction(
        &self,
        lines: &[Line],
        purpose: &str,
        pulse: &str,
    ) -> Result<(), Fault> {
        // Enforce strict zero-sum parity at hypervisor boundary
        enforce_parity(&conky_airlock::types::Patch {
            target: "[[wal]]".into(),
            delta: "".into(),
            parity: lines.to_vec(),
            shadow: false,
            settle: "quiescent".into(),
            purpose: purpose.to_string(),
            base: "".into(),
        })?;

        let mut conn =
            Connection::open(&self.db_path).map_err(|e| Fault::Ward(format!("DB error: {}", e)))?;

        let tx = conn
            .transaction()
            .map_err(|e| Fault::Ward(format!("DB tx error: {}", e)))?;

        for line in lines {
            tx.execute(
                "INSERT INTO ledger (vault, unit, shift, purpose, pulse) VALUES (?1, ?2, ?3, ?4, ?5)",
                params![line.vault, line.unit, line.shift, purpose, pulse],
            ).map_err(|e| Fault::Ward(format!("Insert failed: {}", e)))?;
        }

        tx.commit()
            .map_err(|e| Fault::Ward(format!("Commit failed: {}", e)))?;
        Ok(())
    }

    pub fn get_balance(&self, vault: &str, unit: &str) -> Result<f64, anyhow::Error> {
        let conn = Connection::open(&self.db_path)?;
        let mut stmt = conn.prepare(
            "SELECT COALESCE(SUM(shift), 0.0) FROM ledger WHERE vault = ?1 AND unit = ?2",
        )?;
        let balance: f64 = stmt.query_row(params![vault, unit], |row| row.get(0))?;
        Ok(balance)
    }

    pub fn get_vault_balances(&self, vault: &str) -> Result<HashMap<String, f64>, anyhow::Error> {
        let conn = Connection::open(&self.db_path)?;
        let mut stmt =
            conn.prepare("SELECT unit, SUM(shift) FROM ledger WHERE vault = ?1 GROUP BY unit")?;
        let rows = stmt.query_map(params![vault], |row| {
            Ok((row.get::<_, String>(0)?, row.get::<_, f64>(1)?))
        })?;

        let mut map = HashMap::new();
        for r in rows {
            let (u, s) = r?;
            map.insert(u, s);
        }
        Ok(map)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_wal_sqlite_double_entry() {
        let dir = std::env::temp_dir().join(format!(
            "conky_wal_{}",
            std::time::SystemTime::now()
                .duration_since(std::time::UNIX_EPOCH)
                .unwrap()
                .as_nanos()
        ));
        let _ = std::fs::create_dir_all(&dir);
        let wal = WalEngine::open_or_init(&dir).unwrap();

        let lines = vec![
            Line {
                vault: "sol".into(),
                unit: "usd".into(),
                shift: 15.0,
            },
            Line {
                vault: "customer".into(),
                unit: "usd".into(),
                shift: -15.0,
            },
        ];

        wal.append_transaction(&lines, "[[sale]]", "flux:init")
            .unwrap();
        let sol_usd = wal.get_balance("sol", "usd").unwrap();
        let cust_usd = wal.get_balance("customer", "usd").unwrap();

        assert_eq!(sol_usd, 15.0);
        assert_eq!(cust_usd, -15.0);

        // Imbalance should fail
        let bad_lines = vec![Line {
            vault: "sol".into(),
            unit: "usd".into(),
            shift: 15.0,
        }];
        assert_eq!(
            wal.append_transaction(&bad_lines, "[[hack]]", "flux:init"),
            Err(Fault::Imbalance)
        );
    }
}
