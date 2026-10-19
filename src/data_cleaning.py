"""Clean and standardise the BetXchange raw analytical tables.

The project loads raw Excel export files into DuckDB and then uses this script to
transform them into clean, analysis-ready data. This is the point where we fix:
- inconsistent country names
- missing or invalid dates
- duplicated user identifiers
- low-quality aggregated slips structure
- transaction financial values

Business value:
    Stakeholders need the numbers to be accurate before they are used for KPIs,
    dashboards, and recommendations.

Technical value:
    This creates the clean analytical layer used for retention, financial, and risk
    analysis in DuckDB and Power BI.
"""

from __future__ import annotations

import logging
import unicodedata
from pathlib import Path
from typing import Any, Dict

import duckdb
import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATABASE_PATH = PROJECT_ROOT / "database" / "betxchange.duckdb"


def get_connection() -> duckdb.DuckDBPyConnection:
    """Open a connection to the DuckDB database."""
    try:
        return duckdb.connect(str(DATABASE_PATH))
    except Exception as exc:
        logger.exception("Failed to connect to DuckDB at %s", DATABASE_PATH)
        raise RuntimeError(f"Unable to connect to database: {exc}") from exc


def normalize_country(value: Any) -> str | None:
    """Standardise inconsistent country strings to a single value."""
    if pd.isna(value):
        return "Unknown"

    text = str(value).strip()
    if not text or text.lower() in {"none", "nan", "null", "n/a", "na"}:
        return "Unknown"

    normalized = unicodedata.normalize("NFD", text)
    normalized = "".join(ch for ch in normalized if unicodedata.category(ch) != "Mn")
    cleaned = " ".join(normalized.lower().replace("-", " ").replace("_", " ").split())
    cleaned = cleaned.replace("{", " ").replace("}", " ")
    cleaned = cleaned.replace("(democratic rep)", "democratic republic")
    cleaned = " ".join(cleaned.split())

    mapping = {
        "sa": "South Africa",
        "za": "South Africa",
        "s a": "South Africa",
        "s/a": "South Africa",
        "z": "South Africa",
        "south africa": "South Africa",
        "southafrica": "South Africa",
        "africa do sul": "South Africa",
        "africa do sul ": "South Africa",
        "uk": "United Kingdom",
        "united kingdom": "United Kingdom",
        "england": "United Kingdom",
        "great britain": "United Kingdom",
        "usa": "United States",
        "us": "United States",
        "united states": "United States",
        "p": "Pakistan",
        "pk": "Pakistan",
        "pakistan": "Pakistan",
        "nigeria": "Nigeria",
        "kenya": "Kenya",
        "mozambique": "Mozambique",
        "mocambique": "Mozambique",
        "malawi": "Malawi",
        "lesotho": "Lesotho",
        "ghana": "Ghana",
        "india": "India",
        "bangladesh": "Bangladesh",
        "angola": "Angola",
        "swaziland": "Eswatini",
        "eswatini": "Eswatini",
        "cameroon": "Cameroon",
        "congo": "Congo",
        "democratic republic of the congo": "Democratic Republic of the Congo",
        "democratic republic congo": "Democratic Republic of the Congo",
        "democratic republic of congo": "Democratic Republic of the Congo",
        "congo democratic republic": "Democratic Republic of the Congo",
        "congo democratic rep": "Democratic Republic of the Congo",
        "congo democratic republic of": "Democratic Republic of the Congo",
        "lithuania": "Lithuania",
    }

    if cleaned in mapping:
        return mapping[cleaned]

    return " ".join(part.capitalize() for part in cleaned.split())


def derive_age_band(age_value: Any) -> str:
    """Create a coarse age band for customer segmentation."""
    if pd.isna(age_value):
        return "Unknown"

    try:
        age = int(float(age_value))
    except (TypeError, ValueError):
        return "Unknown"

    if age < 18:
        return "Under 18"
    if age < 25:
        return "18-24"
    if age < 35:
        return "25-34"
    if age < 45:
        return "35-44"
    if age < 55:
        return "45-54"
    if age < 65:
        return "55-64"
    return "65+"


def clean_users(connection: duckdb.DuckDBPyConnection) -> pd.DataFrame:
    """Clean the users table before analysis."""
    logger.info("Cleaning users table...")
    users_df = connection.execute("SELECT * FROM curated.users").fetchdf()

    if users_df.empty:
        logger.warning("No user data available for cleaning.")
        return users_df

    users_df = users_df.rename(columns={
        "user_id": "user_id",
        "age": "age",
        "registration_date": "registration_date",
        "country": "country",
        "source_file": "source_file",
        "source_month": "source_month",
    })

    users_df["user_id"] = users_df["user_id"].map(lambda value: None if pd.isna(value) else str(value))
    users_df["age"] = pd.to_numeric(users_df["age"], errors="coerce").astype("Int64")
    users_df["registration_date"] = pd.to_datetime(users_df["registration_date"], errors="coerce")
    users_df["country"] = users_df["country"].apply(normalize_country)
    users_df["age_band"] = users_df["age"].apply(derive_age_band)
    users_df = users_df.drop_duplicates(subset=["user_id"]).reset_index(drop=True)

    cleaned_users = users_df[[
        "user_id",
        "age",
        "registration_date",
        "country",
        "age_band",
        "source_file",
        "source_month",
    ]].copy()

    connection.execute("CREATE SCHEMA IF NOT EXISTS cleaned")
    connection.execute("DROP TABLE IF EXISTS cleaned.users")
    connection.register("users_clean_stage", cleaned_users)
    connection.execute("CREATE TABLE cleaned.users AS SELECT * FROM users_clean_stage")
    logger.info("Created cleaned.users with %s rows.", len(cleaned_users))
    return cleaned_users


def clean_slips(connection: duckdb.DuckDBPyConnection) -> pd.DataFrame:
    """Reshape the aggregated slips export into a long-form, analysis-ready structure."""
    logger.info("Cleaning slips table...")
    slips_df = connection.execute("SELECT * FROM curated.slips").fetchdf()

    if slips_df.empty:
        logger.warning("No slip data available for cleaning.")
        return slips_df

    product_columns = ["aviator", "betgames", "casino", "horse_racing", "lotto", "sport"]
    rows: list[dict[str, Any]] = []

    for _, row in slips_df.iterrows():
        category_value = row.get("category")
        if pd.isna(category_value):
            continue

        category_text = str(category_value).strip()
        if category_text in {"", "Category", "user_id"}:
            continue

        if category_text.lower() == "total":
            continue

        try:
            user_id = str(int(float(category_value)))
        except (TypeError, ValueError):
            user_id = category_text

        source_file = row.get("source_file")
        source_month = row.get("source_month")

        activity_day_value = row.get("unnamed_1")
        activity_day_text = "" if pd.isna(activity_day_value) else str(activity_day_value).strip()
        if activity_day_text.lower() == "total":
            # The raw export repeats a per-user monthly "Total" row alongside the
            # per-day rows for the same user/product/month. Keeping both would
            # double-count slip volume (verified: the sum of "Total" rows is
            # roughly equal to the sum of all daily rows). Only the daily rows
            # are kept so each unit of activity is counted exactly once.
            continue

        for product in product_columns:
            value = row.get(product)
            if pd.isna(value):
                continue
            try:
                slip_count = int(float(value))
            except (TypeError, ValueError):
                continue

            if slip_count <= 0:
                continue

            activity_day = row.get("unnamed_1")
            rows.append({
                "user_id": user_id,
                "activity_day": activity_day,
                "product_category": product.title(),
                "slip_count": slip_count,
                "source_file": source_file,
                "source_month": source_month,
            })

    cleaned_slips = pd.DataFrame(rows)
    if not cleaned_slips.empty:
        cleaned_slips["user_id"] = cleaned_slips["user_id"].astype(str)
        cleaned_slips["activity_day"] = cleaned_slips["activity_day"].map(
            lambda value: None if pd.isna(value) else str(value)
        )
        cleaned_slips["product_category"] = cleaned_slips["product_category"].map(
            lambda value: str(value).replace("_", " ").title()
        )
        cleaned_slips = cleaned_slips.drop_duplicates().reset_index(drop=True)

    connection.execute("CREATE SCHEMA IF NOT EXISTS cleaned")
    connection.execute("DROP TABLE IF EXISTS cleaned.slips")
    connection.register("slips_clean_stage", cleaned_slips)
    connection.execute("CREATE TABLE cleaned.slips AS SELECT * FROM slips_clean_stage")
    logger.info("Created cleaned.slips with %s rows.", len(cleaned_slips))
    return cleaned_slips


def clean_transactions(connection: duckdb.DuckDBPyConnection) -> pd.DataFrame:
    """Normalise numeric transaction fields and prepare a financial metric layer."""
    logger.info("Cleaning transactions table...")
    transactions_df = connection.execute("SELECT * FROM curated.transactions").fetchdf()

    if transactions_df.empty:
        logger.warning("No transaction data available for cleaning.")
        return transactions_df

    transactions_df["user_id"] = transactions_df["user_id"].map(
        lambda value: None if pd.isna(value) else str(value).strip()
    )
    transactions_df["resolve_time_day"] = transactions_df["resolve_time_day"].map(
        lambda value: None if pd.isna(value) else str(value).strip()
    )
    transactions_df["price_total"] = pd.to_numeric(transactions_df["price_total"], errors="coerce")
    transactions_df["paid_out"] = pd.to_numeric(transactions_df["paid_out"], errors="coerce")
    transactions_df["win_total"] = pd.to_numeric(transactions_df["win_total"], errors="coerce")
    # customer_net_result is the result FROM THE CUSTOMER'S perspective (what the
    # customer won minus what the customer staked). It is negative when the
    # customer lost money on balance.
    #
    # operator_revenue is the result FROM THE OPERATOR'S perspective (BetXchange's
    # gross gaming revenue): what customers staked minus what they were paid out.
    # This is the mirror image of customer_net_result and is the figure that
    # should be used whenever a stakeholder asks about company profit, margin, or
    # financial health. See docs/assumptions.md for why both fields exist and why
    # the project previously reported customer_net_result as if it were company
    # profit (an inverted/incorrect conclusion).
    transactions_df["customer_net_result"] = transactions_df["win_total"] - transactions_df["price_total"]
    transactions_df["operator_revenue"] = transactions_df["price_total"] - transactions_df["win_total"]
    transactions_df["is_total_row"] = (
        transactions_df["user_id"].fillna("").str.lower().str.contains("total")
        | transactions_df["resolve_time_day"].fillna("").str.lower().str.contains("total")
        | transactions_df["source_month"].fillna("").str.lower().str.contains("total")
    )
    transactions_df = transactions_df[
        ~transactions_df["is_total_row"]
        & transactions_df["user_id"].notna()
        & transactions_df["user_id"].str.strip().ne("")
    ].copy()
    transactions_df = transactions_df.drop_duplicates().reset_index(drop=True)

    cleaned_transactions = transactions_df[[
        "user_id",
        "resolve_time_day",
        "price_total",
        "paid_out",
        "win_total",
        "customer_net_result",
        "operator_revenue",
        "source_file",
        "source_month",
    ]].copy()

    connection.execute("CREATE SCHEMA IF NOT EXISTS cleaned")
    connection.execute("DROP TABLE IF EXISTS cleaned.transactions")
    connection.register("transactions_clean_stage", cleaned_transactions)
    connection.execute("CREATE TABLE cleaned.transactions AS SELECT * FROM transactions_clean_stage")
    logger.info("Created cleaned.transactions with %s rows.", len(cleaned_transactions))
    return cleaned_transactions


def main() -> None:
    """Run the end-to-end cleaning workflow for all BetXchange tables."""
    connection = get_connection()
    try:
        clean_users(connection)
        clean_slips(connection)
        clean_transactions(connection)

        connection.commit()
        logger.info("Cleaning completed successfully.")
        print("Data cleaning completed successfully.")
    finally:
        connection.close()


if __name__ == "__main__":
    main()
