"""Create the BetXchange DuckDB database and bootstrap analytical tables.

This script exists to establish the reporting foundation for the technical assessment.
It creates a DuckDB database in the project repository and initializes the schema that
will later hold the cleaned users, slips, and transactions data.

Business value:
    Stakeholders need a trusted analytics layer that is consistent, reusable, and easy
    to connect to Power BI dashboards.

Technical value:
    DuckDB provides a fast analytical engine designed for SQL-based reporting workloads,
    making it well suited to tabular analytics and dashboard consumption.
"""

from __future__ import annotations

import logging
from pathlib import Path

import duckdb

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATABASE_DIR = PROJECT_ROOT / "database"
DATABASE_PATH = DATABASE_DIR / "betxchange.duckdb"
DDL_PATH = PROJECT_ROOT / "sql" / "ddl" / "01_create_database_objects.sql"


def ensure_database() -> duckdb.DuckDBPyConnection:
    """Create the database directory and open a connection to the DuckDB file."""
    try:
        DATABASE_DIR.mkdir(parents=True, exist_ok=True)
        connection = duckdb.connect(str(DATABASE_PATH))
        logger.info("Connected to database: %s", DATABASE_PATH)
        return connection
    except Exception as exc:
        logger.exception("Failed to create DuckDB database at %s", DATABASE_PATH)
        raise RuntimeError(f"Unable to create database: {exc}") from exc


def apply_schema(connection: duckdb.DuckDBPyConnection, ddl_path: Path) -> None:
    """Execute the SQL DDL file to create the base analytical schema."""
    try:
        if not ddl_path.exists():
            raise FileNotFoundError(f"DDL file not found: {ddl_path}")

        connection.execute("DROP VIEW IF EXISTS analytics.vw_user_analysis")
        connection.execute("DROP VIEW IF EXISTS analytics.vw_betting_analysis")
        connection.execute("DROP VIEW IF EXISTS analytics.vw_financial_analysis")
        connection.execute("DROP TABLE IF EXISTS curated.users")
        connection.execute("DROP TABLE IF EXISTS curated.slips")
        connection.execute("DROP TABLE IF EXISTS curated.transactions")
        connection.execute("DROP TABLE IF EXISTS raw.source_file_log")

        sql = ddl_path.read_text(encoding="utf-8")
        connection.execute(sql)
        connection.commit()
        logger.info("Applied schema from %s", ddl_path)
    except Exception as exc:
        logger.exception("Schema creation failed for %s", ddl_path)
        raise RuntimeError(f"Unable to apply SQL schema: {exc}") from exc


def main() -> None:
    """Create the database and validate that foundation tables exist."""
    connection = ensure_database()
    try:
        apply_schema(connection, DDL_PATH)

        table_names = connection.execute(
            "SELECT table_name FROM information_schema.tables WHERE table_schema IN ('raw', 'curated', 'analytics') ORDER BY table_name"
        ).fetchall()

        logger.info("Database tables created: %s", [name[0] for name in table_names])
        print(f"DuckDB database created successfully at: {DATABASE_PATH}")
    finally:
        connection.close()


if __name__ == "__main__":
    main()
