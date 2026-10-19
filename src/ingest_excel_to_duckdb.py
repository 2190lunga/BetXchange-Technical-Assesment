"""Ingest the BetXchange raw Excel files into DuckDB.

This script loads each source workbook into the DuckDB analytical database while
preserving source metadata such as the source file name and month. The purpose is
to maintain an auditable data lineage from the original raw files through the
curated analytical tables used for reporting.

Business value:
    Stakeholders need a trusted data pipeline that can explain where each record came
    from and how it passed into the business reporting layer.

Technical value:
    This provides the raw-to-curated ingestion layer needed for analytics, KPI
    reporting, and Power BI modelling.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Iterable

import pandas as pd
import duckdb

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = Path(r"C:\Users\Q681996\Downloads\Data Analyst Interview - DataSet - 20261012_GT\Data Analyst Interview - DataSet - December 2024")
DATABASE_PATH = PROJECT_ROOT / "database" / "betxchange.duckdb"


def normalize_column_name(column_name: object) -> str:
    """Convert a raw Excel column name into a consistent snake_case field name."""
    text = str(column_name).strip().lower()
    cleaned = "".join(ch if ch.isalnum() else "_" for ch in text)
    cleaned = "_".join(part for part in cleaned.split("_") if part)
    return cleaned or "column"


def infer_source_type(file_name: str) -> str:
    """Map a file name to the BetXchange analytical domain."""
    lower_name = file_name.lower()
    if "user" in lower_name:
        return "users"
    if lower_name.endswith(".xlsx") and "- 2024" in lower_name:
        return "transactions"
    if lower_name.endswith(".xlsx") and lower_name in {"may.xlsx", "june.xlsx", "july.xlsx"}:
        return "slips"
    if "slip" in lower_name:
        return "slips"
    return "unknown"


def infer_source_month(file_name: str) -> str:
    """Extract month information from the source file name."""
    lower_name = file_name.lower()
    for month in ["may", "june", "july"]:
        if month in lower_name:
            return month.title()
    return "unknown"


def ensure_database() -> duckdb.DuckDBPyConnection:
    """Open a connection to the project DuckDB database."""
    try:
        connection = duckdb.connect(str(DATABASE_PATH))
        logger.info("Connected to database: %s", DATABASE_PATH)
        return connection
    except Exception as exc:
        logger.exception("Could not connect to DuckDB database at %s", DATABASE_PATH)
        raise RuntimeError(f"Unable to connect to database: {exc}") from exc


def load_excel_file(file_path: Path, connection: duckdb.DuckDBPyConnection) -> dict:
    """Load one Excel file into the corresponding curated table and return row counts."""
    file_name = file_path.name
    source_type = infer_source_type(file_name)
    source_month = infer_source_month(file_name)

    if source_type == "unknown":
        logger.warning("Skipping unsupported file: %s", file_name)
        return {"source_file": file_name, "rows": 0, "status": "skipped"}

    logger.info("Reading file: %s (%s)", file_name, source_type)

    try:
        sheet_name = pd.ExcelFile(file_path).sheet_names[0]
        df = pd.read_excel(file_path, sheet_name=sheet_name)
    except Exception as exc:
        logger.exception("Failed to read Excel file: %s", file_name)
        raise RuntimeError(f"Unable to read file {file_name}: {exc}") from exc

    if df.empty:
        logger.warning("File has no rows: %s", file_name)
        return {"source_file": file_name, "rows": 0, "status": "empty"}

    # Standardise the field names to a consistent structure.
    df = df.rename(columns=lambda column: normalize_column_name(column))

    # Convert mixed identifier fields to strings before loading into DuckDB. This is
    # important because some raw export columns contain both numeric values and labels
    # such as 'Total', which would otherwise trigger a type conversion error.
    if source_type == "users":
        if "user_id" in df.columns:
            df["user_id"] = df["user_id"].map(lambda value: None if pd.isna(value) else str(value))
        if "country" in df.columns:
            df["country"] = df["country"].map(lambda value: None if pd.isna(value) else str(value))
    elif source_type == "slips":
        for col in df.columns:
            if col not in {"source_file", "source_month", "loaded_at"}:
                df[col] = df[col].map(lambda value: None if pd.isna(value) else str(value))
    elif source_type == "transactions":
        if "user_id" in df.columns:
            df["user_id"] = df["user_id"].map(lambda value: None if pd.isna(value) else str(value))
        if "resolve_time_day" in df.columns:
            df["resolve_time_day"] = df["resolve_time_day"].map(lambda value: None if pd.isna(value) else str(value))

    # Add source metadata so every row can be traced back to the original file.
    df["source_file"] = file_name
    df["source_month"] = source_month
    df["loaded_at"] = pd.Timestamp.utcnow()

    table_name = f"curated.{source_type}"
    delete_sql = f"DELETE FROM {table_name} WHERE source_file = ?"
    connection.execute(delete_sql, [file_name])

    connection.register("staging_table", df)
    connection.execute(f"INSERT INTO {table_name} SELECT * FROM staging_table")

    row_count = len(df)
    connection.execute(
        "INSERT INTO raw.source_file_log (id, source_name, source_month, source_type, file_path, imported_at, row_count, status) VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP, ?, 'loaded')",
        [None, file_name, source_month, source_type, str(file_path), row_count],
    )

    logger.info("Loaded %s rows from %s into %s", row_count, file_name, table_name)
    return {"source_file": file_name, "rows": row_count, "status": "loaded"}


def discover_excel_files(source_dir: Path) -> Iterable[Path]:
    """Return all Excel files in the source directory, sorted by name."""
    if not source_dir.exists():
        raise FileNotFoundError(f"Source directory not found: {source_dir}")
    return sorted(source_dir.rglob("*.xlsx"))


def main() -> None:
    """Run the raw data ingestion process for all BetXchange Excel files."""
    connection = ensure_database()
    try:
        files = discover_excel_files(SOURCE_DIR)
        logger.info("Found %s Excel files to ingest.", len(files))

        for file_path in files:
            load_excel_file(file_path, connection)

        connection.commit()
        logger.info("All files processed successfully.")
        print(f"Ingestion complete. Files processed: {len(files)}")
    except Exception as exc:
        logger.exception("Ingestion process failed")
        raise RuntimeError(f"Ingestion failed: {exc}") from exc
    finally:
        connection.close()


if __name__ == "__main__":
    main()
