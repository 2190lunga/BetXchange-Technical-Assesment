"""Refresh the project CSV exports from the main DuckDB database.

This script ensures the files in the output/ folder are generated from the current
validated data instead of stale copies produced earlier in the project.
"""

from __future__ import annotations

from pathlib import Path

import duckdb

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATABASE_PATH = PROJECT_ROOT / "database" / "betxchange.duckdb"
OUTPUT_DIR = PROJECT_ROOT / "output"

TABLE_EXPORTS = [
    ("analytics.monthly_kpis", "monthly_kpis.csv"),
    ("analytics.customer_kpis", "customer_kpis.csv"),
    ("analytics.product_kpis", "product_kpis.csv"),
    ("analytics.retention_kpis", "retention_kpis.csv"),
    ("analytics.risk_kpis", "risk_kpis.csv"),
    ("analytics.marketing_kpis", "marketing_kpis.csv"),
    ("analytics.demographic_kpis", "demographic_kpis.csv"),
    ("analytics.vw_user_analysis", "vw_user_analysis.csv"),
    ("analytics.vw_betting_analysis", "vw_betting_analysis.csv"),
    ("analytics.vw_financial_analysis", "vw_financial_analysis.csv"),
    ("analytics.vw_retention_analysis", "vw_retention_analysis.csv"),
    ("analytics.vw_risk_analysis", "vw_risk_analysis.csv"),
    ("analytics.vw_marketing_analysis", "vw_marketing_analysis.csv"),
    ("cleaned.users", "users.csv"),
    ("cleaned.slips", "slips.csv"),
    ("cleaned.transactions", "transactions.csv"),
    ("cleaned.marketing_daily_traffic", "marketing_daily_traffic.csv"),
    ("cleaned.marketing_country", "marketing_country.csv"),
    ("cleaned.marketing_gender", "marketing_gender.csv"),
    ("cleaned.marketing_top_pages", "marketing_top_pages.csv"),
    ("raw.source_file_log", "source_file_log.csv"),
]


def export_table(connection: duckdb.DuckDBPyConnection, table_name: str, file_name: str) -> None:
    """Export a single table to a CSV file in the project output directory."""
    if table_name.startswith("analytics."):
        query = f"SELECT * FROM {table_name} ORDER BY 1"
    elif table_name.startswith("cleaned."):
        query = f"SELECT * FROM {table_name} ORDER BY 1"
    else:
        query = f"SELECT * FROM {table_name}"

    df = connection.execute(query).fetchdf()
    target = OUTPUT_DIR / file_name
    if target.exists():
        target.unlink()
    df.to_csv(target, index=False)
    print(f"Exported {table_name} -> {target}")


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    connection = duckdb.connect(str(DATABASE_PATH))
    try:
        for table_name, file_name in TABLE_EXPORTS:
            export_table(connection, table_name, file_name)
        print("CSV exports refreshed successfully.")
    finally:
        connection.close()


if __name__ == "__main__":
    main()
