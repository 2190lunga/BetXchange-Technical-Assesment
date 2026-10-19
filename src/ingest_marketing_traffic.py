"""Ingest BetXchange Google Analytics 4 website traffic exports into DuckDB.

These files (Web Traffic - <month>-24.csv) live in the same source dataset as the
users/slips/transactions workbooks, but are CSV, not .xlsx. The main ingestion script
(ingest_excel_to_duckdb.py) only scans for .xlsx files, so this marketing/traffic data
was never loaded and every marketing claim in the dashboard and reports was written
without any supporting data. This script fixes that gap.

Format notes:
    The GA4 export is a semi-structured CSV: multiple metric "blocks" are stacked in
    one file, separated by blank lines, each preceded by '# Start date:' / '# End date:'
    comment lines. Most blocks repeat twice per file: once for the target calendar
    month, and once for a trailing 31-day comparison window GA generates by default.
    Only the block matching the target calendar month is kept.

What this script deliberately does NOT attempt (see docs/assumptions.md):
    - No campaign, channel, or source/medium data exists in this export, so campaign
      effectiveness or acquisition-channel ROI cannot be computed.
    - GA sessions are anonymous and cannot be joined to the betting user_id, so traffic
      cannot be linked to specific customers, transactions, or slips.
    - Only a small, clearly useful subset of the export is ingested: daily page views,
      daily total users, daily events-per-session, country mix, gender mix, and the
      top 10 landing pages by total users. The full page-path/page-url long tail
      (tens of thousands of rows) is out of scope for this pass.
"""

from __future__ import annotations

import csv
import logging
from pathlib import Path

import duckdb

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATABASE_PATH = PROJECT_ROOT / "database" / "betxchange.duckdb"
SOURCE_DIR = Path(
    r"C:\Users\Q681996\Downloads\Data Analyst Interview - DataSet - 20261012_GT"
    r"\Data Analyst Interview - DataSet - December 2024\2 - GA"
)

MONTH_RANGES = {
    "May": ("20240501", "20240531"),
    # The GA4 export for June genuinely ends on the 29th, not the 30th (verified in the
    # raw source file; this is a property of the export, not a parsing bug). Keeping the
    # literal value instead of assuming a full month avoids silently fabricating a day
    # of data that was never exported.
    "June": ("20240601", "20240629"),
    "July": ("20240701", "20240731"),
}

FILE_NAME_TEMPLATE = "Web Traffic - {short_month}-24.csv"
SHORT_MONTH = {"May": "May", "June": "June", "July": "July"}

DAILY_BLOCKS = {
    ("Nth day", "Event count"): "page_views",
    ("Nth day", "Total users"): "total_users",
    ("Nth day", "Events per session"): "events_per_session",
}
TOP_PAGES_HEADER = ("Custom parameter", "Event count", "Total users")
TOP_PAGES_LIMIT = 10


def get_connection() -> duckdb.DuckDBPyConnection:
    """Open a connection to the DuckDB database."""
    try:
        return duckdb.connect(str(DATABASE_PATH))
    except Exception as exc:
        logger.exception("Failed to connect to DuckDB at %s", DATABASE_PATH)
        raise RuntimeError(f"Unable to connect to database: {exc}") from exc


def parse_ga_file(file_path: Path, month: str) -> dict[str, list[dict]]:
    """Parse one GA4 web traffic export and return only the target month's data."""
    target_range = MONTH_RANGES[month]
    cur_start: str | None = None
    cur_end: str | None = None
    cur_section: str | None = None  # "page_path" | "page_url" | None
    capturing: str | None = None
    rows_in_block = 0

    daily: dict[str, dict[int, float]] = {key: {} for key in DAILY_BLOCKS.values()}
    country_rows: list[dict] = []
    gender_rows: list[dict] = []
    page_rows: list[dict] = []

    with file_path.open("r", encoding="utf-8-sig", newline="") as handle:
        for raw_line in handle:
            line = raw_line.rstrip("\n").rstrip("\r")

            if line.strip() == "":
                capturing = None
                rows_in_block = 0
                continue

            if line.lstrip().startswith("#"):
                text = line.lstrip("#").strip()
                if text.startswith("Start date:"):
                    cur_start = text.split(":", 1)[1].strip()
                elif text.startswith("End date:"):
                    cur_end = text.split(":", 1)[1].strip()
                elif text == "page_path":
                    cur_section = "page_path"
                elif text == "page_url":
                    cur_section = "page_url"
                capturing = None
                continue

            parts = next(csv.reader([line]))
            header_key = tuple(part.strip() for part in parts)
            in_target_month = (cur_start, cur_end) == target_range

            if header_key in DAILY_BLOCKS:
                capturing = DAILY_BLOCKS[header_key] if in_target_month else None
                rows_in_block = 0
                continue
            if header_key == ("Country ID", "Event count"):
                capturing = "country" if in_target_month else None
                rows_in_block = 0
                continue
            if header_key == ("Gender", "Event count"):
                capturing = "gender" if in_target_month else None
                rows_in_block = 0
                continue
            if header_key == TOP_PAGES_HEADER:
                capturing = "top_pages" if (in_target_month and cur_section == "page_path") else None
                rows_in_block = 0
                continue

            if capturing in DAILY_BLOCKS.values():
                try:
                    day_index = int(parts[0].strip())
                    value = float(parts[1].strip())
                except (ValueError, IndexError):
                    continue
                daily[capturing][day_index] = value
            elif capturing == "country":
                if len(parts) >= 2:
                    country_rows.append({"country_code": parts[0].strip(), "event_count": int(float(parts[1]))})
            elif capturing == "gender":
                if len(parts) >= 2:
                    gender_rows.append({"gender": parts[0].strip(), "event_count": int(float(parts[1]))})
            elif capturing == "top_pages":
                if rows_in_block < TOP_PAGES_LIMIT and len(parts) >= 3:
                    page_rows.append({
                        "page_path": parts[0].strip(),
                        "event_count": int(float(parts[1])),
                        "total_users": int(float(parts[2])),
                    })
                rows_in_block += 1
                if rows_in_block >= TOP_PAGES_LIMIT:
                    capturing = None

    daily_rows = []
    all_days = sorted(set().union(*[set(d.keys()) for d in daily.values()])) if daily else []
    for day_index in all_days:
        daily_rows.append({
            "day_index": day_index,
            "page_views": daily["page_views"].get(day_index),
            "total_users": daily["total_users"].get(day_index),
            "events_per_session": daily["events_per_session"].get(day_index),
        })

    return {
        "daily": daily_rows,
        "country": country_rows,
        "gender": gender_rows,
        "top_pages": page_rows,
    }


def load_marketing_traffic(connection: duckdb.DuckDBPyConnection) -> None:
    """Parse each month's GA4 export and load it into the cleaned marketing tables."""
    connection.execute("CREATE SCHEMA IF NOT EXISTS cleaned")

    connection.execute("DROP TABLE IF EXISTS cleaned.marketing_daily_traffic")
    connection.execute("""
        CREATE TABLE cleaned.marketing_daily_traffic (
            source_month VARCHAR,
            day_index INTEGER,
            page_views DOUBLE,
            total_users DOUBLE,
            events_per_session DOUBLE
        )
    """)
    connection.execute("DROP TABLE IF EXISTS cleaned.marketing_country")
    connection.execute("""
        CREATE TABLE cleaned.marketing_country (
            source_month VARCHAR,
            country_code VARCHAR,
            event_count BIGINT
        )
    """)
    connection.execute("DROP TABLE IF EXISTS cleaned.marketing_gender")
    connection.execute("""
        CREATE TABLE cleaned.marketing_gender (
            source_month VARCHAR,
            gender VARCHAR,
            event_count BIGINT
        )
    """)
    connection.execute("DROP TABLE IF EXISTS cleaned.marketing_top_pages")
    connection.execute("""
        CREATE TABLE cleaned.marketing_top_pages (
            source_month VARCHAR,
            page_path VARCHAR,
            event_count BIGINT,
            total_users BIGINT
        )
    """)

    for month, short_month in SHORT_MONTH.items():
        file_name = FILE_NAME_TEMPLATE.format(short_month=short_month)
        file_path = SOURCE_DIR / file_name
        if not file_path.exists():
            logger.warning("Marketing source file not found, skipping: %s", file_path)
            continue

        logger.info("Parsing marketing traffic file: %s", file_name)
        parsed = parse_ga_file(file_path, month)

        for row in parsed["daily"]:
            connection.execute(
                "INSERT INTO cleaned.marketing_daily_traffic VALUES (?, ?, ?, ?, ?)",
                [month, row["day_index"], row["page_views"], row["total_users"], row["events_per_session"]],
            )
        for row in parsed["country"]:
            connection.execute(
                "INSERT INTO cleaned.marketing_country VALUES (?, ?, ?)",
                [month, row["country_code"], row["event_count"]],
            )
        for row in parsed["gender"]:
            connection.execute(
                "INSERT INTO cleaned.marketing_gender VALUES (?, ?, ?)",
                [month, row["gender"], row["event_count"]],
            )
        for row in parsed["top_pages"]:
            connection.execute(
                "INSERT INTO cleaned.marketing_top_pages VALUES (?, ?, ?, ?)",
                [month, row["page_path"], row["event_count"], row["total_users"]],
            )

        connection.execute(
            """
            INSERT INTO raw.source_file_log
                (id, source_name, source_month, source_type, file_path, imported_at, row_count, status)
            VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP, ?, 'loaded')
            """,
            [None, file_name, month, "marketing_web_traffic", str(file_path), len(parsed["daily"])],
        )
        logger.info(
            "Loaded marketing traffic for %s: %s daily rows, %s countries, %s genders, %s top pages",
            month, len(parsed["daily"]), len(parsed["country"]), len(parsed["gender"]), len(parsed["top_pages"]),
        )

    connection.commit()


def main() -> None:
    """Ingest GA4 marketing traffic data into the cleaned schema."""
    connection = get_connection()
    try:
        load_marketing_traffic(connection)
        print("Marketing traffic ingestion completed successfully.")
    finally:
        connection.close()


if __name__ == "__main__":
    main()
