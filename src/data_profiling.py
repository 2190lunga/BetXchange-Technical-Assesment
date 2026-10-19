"""Profile the ingested BetXchange tables and surface data quality issues.

This module calculates the core quality checks required for the assessment:
- row counts
- null counts
- duplicate checks
- distinct-value counts
- summary statistics

Business value:
    Business stakeholders need trustworthy data before they act on any KPI or narrative.

Technical value:
    The profiling checks make issues visible early, before analysts build dashboards or
    KPIs on unreliable data.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, Iterable, List

import duckdb

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATABASE_PATH = PROJECT_ROOT / "database" / "betxchange.duckdb"


def get_connection() -> duckdb.DuckDBPyConnection:
    """Open a connection to the project DuckDB database."""
    try:
        return duckdb.connect(str(DATABASE_PATH))
    except Exception as exc:
        logger.exception("Unable to connect to DuckDB database at %s", DATABASE_PATH)
        raise RuntimeError(f"Could not connect to database: {exc}") from exc


def fetch_single_value(connection: duckdb.DuckDBPyConnection, query: str) -> Any:
    """Execute a scalar query and return the first value."""
    return connection.execute(query).fetchone()[0]


def profile_table(connection: duckdb.DuckDBPyConnection, schema: str, table_name: str, columns: Iterable[str]) -> Dict[str, Any]:
    """Create a quality profile for a single table."""
    table_ref = f"{schema}.{table_name}"
    row_count = fetch_single_value(connection, f"SELECT COUNT(*) FROM {table_ref};")

    null_summary = {}
    distinct_summary = {}
    duplicate_summary = {}

    for column in columns:
        null_count = fetch_single_value(
            connection,
            f"SELECT COUNT(*) FROM {table_ref} WHERE {column} IS NULL OR TRIM(CAST({column} AS VARCHAR)) = '';",
        )
        distinct_count = fetch_single_value(connection, f"SELECT COUNT(DISTINCT {column}) FROM {table_ref};")
        duplicate_count = fetch_single_value(
            connection,
            f"SELECT COUNT(*) FROM (SELECT {column}, COUNT(*) AS row_count FROM {table_ref} GROUP BY {column} HAVING COUNT(*) > 1);",
        )

        null_summary[column] = int(null_count)
        distinct_summary[column] = int(distinct_count)
        duplicate_summary[column] = int(duplicate_count)

    return {
        "table": table_ref,
        "row_count": int(row_count),
        "null_counts": null_summary,
        "distinct_counts": distinct_summary,
        "duplicate_counts": duplicate_summary,
    }


def build_summary_stats(connection: duckdb.DuckDBPyConnection, schema: str, table_name: str, numeric_columns: Iterable[str]) -> Dict[str, Any]:
    """Return summary statistics for numeric columns."""
    stats: Dict[str, Any] = {}
    for column in numeric_columns:
        query = f"SELECT MIN({column}) AS min_value, MAX({column}) AS max_value, AVG({column}) AS avg_value, SUM({column}) AS total_value FROM {schema}.{table_name};"
        row = connection.execute(query).fetchone()
        stats[column] = {
            "min": row[0],
            "max": row[1],
            "avg": row[2],
            "total": row[3],
        }
    return stats


def main() -> None:
    """Run the profiling workflow and print the quality report for the curated tables."""
    connection = get_connection()
    try:
        profile_map = {
            "curated.users": ["user_id", "age", "registration_date", "country"],
            "curated.slips": ["category", "unnamed_1", "unnamed_2", "aviator", "betgames", "casino", "horse_racing", "lotto", "sport", "total"],
            "curated.transactions": ["user_id", "resolve_time_day", "price_total", "paid_out", "win_total"],
        }

        report = {}
        for table_name, columns in profile_map.items():
            schema = table_name.split(".")[0]
            name = table_name.split(".")[1]
            report[table_name] = profile_table(connection, schema, name, columns)

            if name == "transactions":
                report[table_name]["summary_statistics"] = build_summary_stats(
                    connection,
                    schema,
                    name,
                    ["price_total", "paid_out", "win_total"],
                )

        print(json.dumps(report, indent=2, default=str))

        logger.info("Profiling completed successfully.")
    finally:
        connection.close()


if __name__ == "__main__":
    main()
