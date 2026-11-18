---
crest: "[[pnl-notebook]]"
engine: "organ/duckdb"
maker: "[[sol]]"
guard: "[[guard-pnl-notebook]]"
view: "[[view-pnl-notebook]]"
source: ".iceberg/[[wal]]/ledger.parquet"
sql: "SELECT unit, SUM(shift) AS net FROM source WHERE vault='usd' GROUP BY unit"
seal: "sig:ed25519:1b7a998124b"
---
# Real-Time Margin Analysis
| unit | net |
| :--- | :--- |
| lemonade_sales | +$168.00 |
| lemon_cogs | -$33.50 |
