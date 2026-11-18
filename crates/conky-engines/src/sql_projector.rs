use rusqlite::Connection;
use std::path::Path;

pub struct SqlProjector {}

impl SqlProjector {
    pub fn new() -> Self {
        Self {}
    }

    /// Validates query purity: must be SELECT only
    pub fn validate_query(sql: &str) -> Result<(), anyhow::Error> {
        let trimmed = sql.trim().to_uppercase();
        if !trimmed.starts_with("SELECT") {
            anyhow::bail!("Only SELECT queries are permitted in surface projectors");
        }
        for forbidden in &["DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "ATTACH", "DETACH"] {
            if trimmed.contains(forbidden) {
                anyhow::bail!("Forbidden mutating keyword '{}' in projector SQL", forbidden);
            }
        }
        Ok(())
    }

    /// Executes query against SQLite ledger and formats result into a Markdown table
    pub fn project_markdown_table<P: AsRef<Path>>(
        db_path: P,
        sql: &str,
    ) -> Result<String, anyhow::Error> {
        Self::validate_query(sql)?;

        let conn = Connection::open_with_flags(
            db_path,
            rusqlite::OpenFlags::SQLITE_OPEN_READ_ONLY,
        )?;

        let mut stmt = conn.prepare(sql)?;
        let column_count = stmt.column_count();
        let column_names: Vec<String> = stmt
            .column_names()
            .into_iter()
            .map(|s| s.to_string())
            .collect();

        let mut rows_out = Vec::new();
        let mut rows = stmt.query([])?;

        while let Some(row) = rows.next()? {
            let mut row_vals = Vec::new();
            for i in 0..column_count {
                let val_str = match row.get_ref(i)? {
                    rusqlite::types::ValueRef::Null => "null".to_string(),
                    rusqlite::types::ValueRef::Integer(n) => n.to_string(),
                    rusqlite::types::ValueRef::Real(r) => format!("{:.2}", r),
                    rusqlite::types::ValueRef::Text(t) => String::from_utf8_lossy(t).to_string(),
                    rusqlite::types::ValueRef::Blob(_) => "<blob>".to_string(),
                };
                row_vals.push(val_str);
            }
            rows_out.push(row_vals);
        }

        // Format Markdown table
        let mut md = String::new();
        md.push_str(&format!("| {} |\n", column_names.join(" | ")));
        let sep: Vec<&str> = column_names.iter().map(|_| ":---").collect();
        md.push_str(&format!("| {} |\n", sep.join(" | ")));

        for row in rows_out {
            md.push_str(&format!("| {} |\n", row.join(" | ")));
        }

        Ok(md.trim_end().to_string())
    }
}

impl Default for SqlProjector {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_sql_projection_to_markdown() {
        let dir = std::env::temp_dir().join(format!("conky_sql_{}", std::time::SystemTime::now().duration_since(std::time::UNIX_EPOCH).unwrap().as_nanos()));
        let _ = std::fs::create_dir_all(&dir);
        let db_path = dir.join("test.db");
        let conn = Connection::open(&db_path).unwrap();
        conn.execute_batch(
            "CREATE TABLE sales (unit TEXT, net REAL);
             INSERT INTO sales VALUES ('lemonade_sales', 168.0), ('lemon_cogs', -33.5);",
        ).unwrap();

        let md = SqlProjector::project_markdown_table(
            &db_path,
            "SELECT unit, net FROM sales ORDER BY net DESC",
        ).unwrap();

        assert!(md.contains("| unit | net |"));
        assert!(md.contains("| lemonade_sales | 168.00 |"));
        assert!(md.contains("| lemon_cogs | -33.50 |"));
    }

    #[test]
    fn test_mutation_rejected() {
        assert!(SqlProjector::validate_query("DROP TABLE ledger").is_err());
        assert!(SqlProjector::validate_query("DELETE FROM ledger").is_err());
        assert!(SqlProjector::validate_query("SELECT * FROM ledger; DELETE FROM ledger;").is_err());
    }
}
