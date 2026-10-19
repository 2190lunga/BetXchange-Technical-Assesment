"""Create the BetXchange analytical SQL views in DuckDB.

This script loads the reusable SQL definitions that support user, betting, financial,
retention, and risk analysis. The views sit on top of the cleaned tables and provide
stakeholder-friendly analytical layers for Power BI and downstream reporting.

Business value:
    Stakeholders can review curated performance views without needing to query the raw
    data tables directly.

Technical value:
    This makes the database easier to consume, easier to validate, and easier to keep
    consistent across Power BI and analytical storytelling.
"""

from __future__ import annotations

import logging
from pathlib import Path

import duckdb

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATABASE_PATH = PROJECT_ROOT / "database" / "betxchange.duckdb"
VIEW_SQL_PATH = PROJECT_ROOT / "sql" / "views" / "analytics_views.sql"


def get_connection() -> duckdb.DuckDBPyConnection:
    """Open a connection to the DuckDB project database."""
    try:
        return duckdb.connect(str(DATABASE_PATH))
    except Exception as exc:
        logger.exception("Could not connect to DuckDB database at %s", DATABASE_PATH)
        raise RuntimeError(f"Unable to connect to database: {exc}") from exc


def create_views(connection: duckdb.DuckDBPyConnection, sql_path: Path) -> None:
    """Execute the SQL DDL file that defines the analytical views."""
    try:
        if not sql_path.exists():
            raise FileNotFoundError(f"SQL file not found: {sql_path}")

        sql = sql_path.read_text(encoding="utf-8")
        connection.execute(sql)
        connection.commit()
        logger.info("Created analytical views from %s", sql_path)
    except Exception as exc:
        logger.exception("Failed to create analytical views")
        raise RuntimeError(f"Unable to create views: {exc}") from exc


def main() -> None:
    """Create all analytical views and print a confirmation message."""
    connection = get_connection()
    try:
        create_views(connection, VIEW_SQL_PATH)
        view_names = connection.execute(
            "SELECT table_name FROM information_schema.views WHERE table_schema = 'analytics' ORDER BY table_name"
        ).fetchall()
        logger.info("Available views: %s", [name[0] for name in view_names])
        print("Analytical views created successfully.")
    finally:
        connection.close()


if __name__ == "__main__":
    main()
