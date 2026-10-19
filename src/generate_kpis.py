"""Generate the BetXchange KPI dataset tables.

These KPIs consolidate the cleaned data into summary tables that are easier to use in
Power BI and easier to explain to stakeholders. The dataset includes:
- monthly KPI summaries
- customer-level KPI scores
- product-level KPI analysis
- retention KPI tables
- risk KPI tables

Business value:
    KPI datasets are the layer that translates raw business activity into executive-ready
    metrics such as active users, net margin, churn risk, and product performance.

Technical value:
    These tables allow dashboard authors and analysts to work from consistent metrics
    instead of re-deriving the same calculations in every report.
"""

from __future__ import annotations

import logging
from pathlib import Path

import duckdb

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATABASE_PATH = PROJECT_ROOT / "database" / "betxchange.duckdb"
KPI_SQL_PATH = PROJECT_ROOT / "sql" / "kpis" / "01_create_kpi_tables.sql"


def get_connection() -> duckdb.DuckDBPyConnection:
    """Open a connection to the DuckDB analytics database."""
    try:
        return duckdb.connect(str(DATABASE_PATH))
    except Exception as exc:
        logger.exception("Failed to connect to DuckDB at %s", DATABASE_PATH)
        raise RuntimeError(f"Unable to connect to database: {exc}") from exc


def create_kpi_tables(connection: duckdb.DuckDBPyConnection, sql_path: Path) -> None:
    """Create the KPI tables in the analytics schema."""
    try:
        sql = sql_path.read_text(encoding="utf-8")
        connection.execute(sql)
        connection.commit()
        logger.info("Created KPI tables from %s", sql_path)
    except Exception as exc:
        logger.exception("Failed to create KPI table schema")
        raise RuntimeError(f"Unable to create KPI tables: {exc}") from exc


def populate_monthly_kpis(connection: duckdb.DuckDBPyConnection) -> None:
    """Populate monthly KPI summary data for executive reporting.

    operator_revenue (stake minus payout) is BetXchange's gross gaming revenue and is
    the correct figure for company profitability. customer_net_result is kept for
    reference but is the customer's perspective, not the company's. See
    docs/assumptions.md.
    """
    sql = """
    DELETE FROM analytics.monthly_kpis;
    INSERT INTO analytics.monthly_kpis
    SELECT
        source_month AS month_label,
        COUNT(DISTINCT user_id) AS active_customers,
        COUNT(*) AS transaction_count,
        SUM(price_total) AS total_stake,
        SUM(paid_out) AS total_paid_out,
        SUM(win_total) AS total_win,
        SUM(customer_net_result) AS customer_net_result,
        SUM(operator_revenue) AS operator_revenue,
        CASE
            WHEN SUM(price_total) > 0 THEN (SUM(operator_revenue) * 100.0) / SUM(price_total)
            ELSE 0
        END AS operator_margin_pct,
        AVG(customer_net_result) AS avg_customer_net_result,
        source_month
    FROM cleaned.transactions
    GROUP BY source_month
    ORDER BY source_month;
    """
    connection.execute(sql)
    connection.commit()
    logger.info("Populated analytics.monthly_kpis")


def populate_customer_kpis(connection: duckdb.DuckDBPyConnection) -> None:
    """Populate customer-level KPI metrics.

    net_margin_pct is a profitability ratio (operator revenue relative to stake), not a
    measure of usage frequency. It was previously mislabeled "engagement_score", which
    implied activity/engagement when it actually measured margin. Renamed for clarity.
    """
    sql = """
    DELETE FROM analytics.customer_kpis;
    INSERT INTO analytics.customer_kpis
    SELECT
        user_id,
        COUNT(*) AS transaction_count,
        SUM(price_total) AS total_stake,
        SUM(win_total) AS total_win,
        SUM(customer_net_result) AS customer_net_result,
        SUM(operator_revenue) AS operator_revenue_from_customer,
        MAX(source_month) AS latest_activity_month,
        CASE
            WHEN SUM(price_total) > 0 THEN (SUM(operator_revenue) / SUM(price_total)) * 100.0
            ELSE 0
        END AS net_margin_pct
    FROM cleaned.transactions
    WHERE user_id IS NOT NULL
      AND TRIM(user_id) <> ''
      AND LOWER(TRIM(user_id)) <> 'total'
    GROUP BY user_id
    ORDER BY operator_revenue_from_customer DESC;
    """
    connection.execute(sql)
    connection.commit()
    logger.info("Populated analytics.customer_kpis")


def populate_product_kpis(connection: duckdb.DuckDBPyConnection) -> None:
    """Populate product-level KPI metrics from the cleaned slips table.

    IMPORTANT: the source transactions table has no product dimension, so a user's
    stake/win cannot be directly attributed to a product. The previous implementation
    joined slips to transactions on user_id + source_month only (no day key), which
    created a fan-out (cross join) within each user-month group and inflated financial
    totals by orders of magnitude (verified: reported Casino stake exceeded total
    company-wide stake for the same month by roughly 4000x).

    This version allocates each user's monthly stake/win/operator revenue across
    products in proportion to that user's share of slip volume for each product that
    month. This is a modeled estimate, not a direct measurement, and est_ columns are
    named accordingly. total_slip_count and active_users remain directly measured.
    See docs/assumptions.md.
    """
    sql = """
    DELETE FROM analytics.product_kpis;
    INSERT INTO analytics.product_kpis
    WITH user_month_txn AS (
        SELECT
            user_id,
            source_month,
            SUM(price_total) AS total_stake,
            SUM(win_total) AS total_win,
            SUM(operator_revenue) AS operator_revenue
        FROM cleaned.transactions
        GROUP BY user_id, source_month
    ),
    user_month_slip_total AS (
        SELECT
            user_id,
            source_month,
            SUM(slip_count) AS total_slips_all_products
        FROM cleaned.slips
        GROUP BY user_id, source_month
    ),
    product_user_month AS (
        SELECT
            user_id,
            source_month,
            product_category,
            SUM(slip_count) AS product_slip_count
        FROM cleaned.slips
        GROUP BY user_id, source_month, product_category
    )
    SELECT
        p.product_category,
        p.source_month,
        SUM(p.product_slip_count) AS total_slip_count,
        COUNT(DISTINCT p.user_id) AS active_users,
        AVG(p.product_slip_count) AS avg_slips_per_user,
        SUM(
            CASE WHEN m.total_slips_all_products > 0
                 THEN COALESCE(t.total_stake, 0) * (p.product_slip_count / m.total_slips_all_products)
                 ELSE 0 END
        ) AS est_total_stake,
        SUM(
            CASE WHEN m.total_slips_all_products > 0
                 THEN COALESCE(t.total_win, 0) * (p.product_slip_count / m.total_slips_all_products)
                 ELSE 0 END
        ) AS est_total_win,
        SUM(
            CASE WHEN m.total_slips_all_products > 0
                 THEN COALESCE(t.operator_revenue, 0) * (p.product_slip_count / m.total_slips_all_products)
                 ELSE 0 END
        ) AS est_operator_revenue
    FROM product_user_month p
    JOIN user_month_slip_total m
        ON m.user_id = p.user_id AND m.source_month = p.source_month
    LEFT JOIN user_month_txn t
        ON t.user_id = p.user_id AND t.source_month = p.source_month
    GROUP BY p.product_category, p.source_month
    ORDER BY p.source_month, p.product_category;
    """
    connection.execute(sql)
    connection.commit()
    logger.info("Populated analytics.product_kpis")


def populate_retention_kpis(connection: duckdb.DuckDBPyConnection) -> None:
    """Populate retention KPI metrics using cohort-month logic."""
    sql = """
    DELETE FROM analytics.retention_kpis;
    INSERT INTO analytics.retention_kpis
    WITH cohort_sizes AS (
        SELECT
            DATE_TRUNC('month', registration_date)::DATE AS cohort_month,
            COUNT(DISTINCT user_id) AS unique_customers
        FROM cleaned.users
        GROUP BY 1
    ),
    transaction_activity AS (
        SELECT
            u.user_id,
            DATE_TRUNC('month', u.registration_date)::DATE AS cohort_month,
            t.source_month AS activity_month
        FROM cleaned.users u
        JOIN cleaned.transactions t
          ON t.user_id = u.user_id
        GROUP BY 1, 2, 3
    ),
    slip_activity AS (
        SELECT
            u.user_id,
            DATE_TRUNC('month', u.registration_date)::DATE AS cohort_month,
            s.source_month AS activity_month
        FROM cleaned.users u
        JOIN cleaned.slips s
          ON s.user_id = u.user_id
        GROUP BY 1, 2, 3
    ),
    activity_summary AS (
        SELECT
            ta.cohort_month,
            ta.activity_month,
            COUNT(DISTINCT ta.user_id) AS customers_with_transactions,
            COUNT(DISTINCT sa.user_id) AS customers_with_slips
        FROM transaction_activity ta
        LEFT JOIN slip_activity sa
          ON sa.user_id = ta.user_id
         AND sa.cohort_month = ta.cohort_month
         AND sa.activity_month = ta.activity_month
        GROUP BY ta.cohort_month, ta.activity_month
    )
    SELECT
        cs.cohort_month,
        a.activity_month,
        cs.unique_customers,
        COALESCE(a.customers_with_slips, 0) AS customers_with_slips,
        COALESCE(a.customers_with_transactions, 0) AS customers_with_transactions,
        CASE
            WHEN cs.unique_customers > 0 THEN (COALESCE(a.customers_with_transactions, 0) * 100.0) / cs.unique_customers
            ELSE 0
        END AS retention_rate
    FROM cohort_sizes cs
    LEFT JOIN activity_summary a
      ON a.cohort_month = cs.cohort_month
    ORDER BY cs.cohort_month, a.activity_month;
    """
    connection.execute(sql)
    connection.commit()
    logger.info("Populated analytics.retention_kpis")


def populate_risk_kpis(connection: duckdb.DuckDBPyConnection) -> None:
    """Populate risk-based KPI metrics.

    Methodology (fully documented in docs/assumptions.md):
    - large_stake_threshold is the 95th percentile of that month's per-transaction
      stake, computed from the data itself. This replaces an unexplained fixed
      threshold (previously hardcoded at 5000) that did not scale with monthly volume.
    - customer_win_event_count counts transactions where the CUSTOMER came out ahead
      (customer_net_result > 0). This is payout exposure for the operator, not a
      company "loss" -- the previous version labeled this "loss_events" and
      "risky_users", which inverted the business meaning and also mislabeled a plain
      active-user count as a risk flag.
    - top10_user_stake_share_pct measures revenue concentration: how dependent that
      month's volume is on its ten highest-staking users.
    - operator_margin_pct is the house edge/hold for the month.
    This table cannot detect fraud, collusion, bonus abuse, or multi-accounting: the
    source data has no device, IP, payment method, or account-linkage fields.
    """
    sql = """
    DELETE FROM analytics.risk_kpis;
    INSERT INTO analytics.risk_kpis
    WITH monthly_threshold AS (
        SELECT
            source_month,
            QUANTILE_CONT(price_total, 0.95) AS large_stake_threshold
        FROM cleaned.transactions
        GROUP BY source_month
    ),
    monthly_base AS (
        SELECT
            t.source_month,
            COUNT(*) AS total_transactions,
            SUM(t.price_total) AS total_stake,
            SUM(t.operator_revenue) AS operator_revenue,
            SUM(CASE WHEN t.customer_net_result > 0 THEN 1 ELSE 0 END) AS customer_win_event_count,
            SUM(CASE WHEN t.price_total > th.large_stake_threshold THEN 1 ELSE 0 END) AS large_stake_transaction_count,
            SUM(CASE WHEN t.price_total > th.large_stake_threshold THEN t.price_total ELSE 0 END) AS large_stake_total,
            MAX(th.large_stake_threshold) AS large_stake_threshold
        FROM cleaned.transactions t
        JOIN monthly_threshold th ON th.source_month = t.source_month
        GROUP BY t.source_month
    ),
    user_month_stake AS (
        SELECT user_id, source_month, SUM(price_total) AS user_stake
        FROM cleaned.transactions
        GROUP BY user_id, source_month
    ),
    top10 AS (
        SELECT
            source_month,
            SUM(user_stake) AS top10_stake
        FROM (
            SELECT
                source_month,
                user_stake,
                ROW_NUMBER() OVER (PARTITION BY source_month ORDER BY user_stake DESC) AS rn
            FROM user_month_stake
        )
        WHERE rn <= 10
        GROUP BY source_month
    )
    SELECT
        b.source_month,
        b.total_transactions,
        b.large_stake_threshold,
        b.large_stake_transaction_count,
        CASE WHEN b.total_stake > 0 THEN (b.large_stake_total * 100.0) / b.total_stake ELSE 0 END AS large_stake_share_pct,
        b.customer_win_event_count,
        CASE WHEN b.total_transactions > 0 THEN (b.customer_win_event_count * 100.0) / b.total_transactions ELSE 0 END AS customer_win_event_share_pct,
        CASE WHEN b.total_stake > 0 THEN (t10.top10_stake * 100.0) / b.total_stake ELSE 0 END AS top10_user_stake_share_pct,
        CASE WHEN b.total_stake > 0 THEN (b.operator_revenue * 100.0) / b.total_stake ELSE 0 END AS operator_margin_pct
    FROM monthly_base b
    JOIN top10 t10 ON t10.source_month = b.source_month
    ORDER BY b.source_month;
    """
    connection.execute(sql)
    connection.commit()
    logger.info("Populated analytics.risk_kpis")


def populate_marketing_kpis(connection: duckdb.DuckDBPyConnection) -> None:
    """Populate marketing/website-traffic KPI metrics from the GA4 export.

    The GA4 export has no campaign, channel, source/medium, or user_id dimension, so
    it cannot support "campaign effectiveness" or "acquisition channel" claims. It can
    only describe aggregate, anonymous website engagement. See docs/assumptions.md.
    Skips silently if the marketing tables have not been ingested yet.
    """
    tables = connection.execute(
        "SELECT table_name FROM information_schema.tables WHERE table_schema = 'cleaned'"
    ).fetchall()
    table_names = {row[0] for row in tables}
    if "marketing_daily_traffic" not in table_names or "marketing_country" not in table_names:
        logger.warning("Marketing tables not found; skipping analytics.marketing_kpis")
        return

    sql = """
    DELETE FROM analytics.marketing_kpis;
    INSERT INTO analytics.marketing_kpis
    WITH daily AS (
        SELECT
            source_month,
            SUM(page_views) AS total_page_views,
            AVG(total_users) AS avg_daily_total_users,
            AVG(events_per_session) AS avg_events_per_session
        FROM cleaned.marketing_daily_traffic
        GROUP BY source_month
    ),
    country_totals AS (
        SELECT source_month, SUM(event_count) AS total_country_events
        FROM cleaned.marketing_country
        GROUP BY source_month
    ),
    ranked_country AS (
        SELECT
            source_month,
            country_code,
            event_count,
            ROW_NUMBER() OVER (PARTITION BY source_month ORDER BY event_count DESC) AS rn
        FROM cleaned.marketing_country
    ),
    za AS (
        SELECT source_month, event_count AS za_event_count
        FROM cleaned.marketing_country
        WHERE country_code = 'ZA'
    )
    SELECT
        d.source_month,
        d.total_page_views,
        d.avg_daily_total_users,
        d.avg_events_per_session,
        rc.country_code AS top_country,
        (rc.event_count * 100.0) / ct.total_country_events AS top_country_share_pct,
        (COALESCE(za.za_event_count, 0) * 100.0) / ct.total_country_events AS za_traffic_share_pct
    FROM daily d
    JOIN country_totals ct ON ct.source_month = d.source_month
    JOIN ranked_country rc ON rc.source_month = d.source_month AND rc.rn = 1
    LEFT JOIN za ON za.source_month = d.source_month
    ORDER BY d.source_month;
    """
    connection.execute(sql)
    connection.commit()
    logger.info("Populated analytics.marketing_kpis")


def populate_demographic_kpis(connection: duckdb.DuckDBPyConnection) -> None:
    """Populate stake/revenue contribution by age band and by country.

    COVERAGE LIMIT (see docs/assumptions.md): only customers present in cleaned.users
    are included here. Verified: only 7,918 of 24,142 transacting customers (33%) have
    a matching row in cleaned.users -- the raw Users exports do not cover every
    customer who placed a bet. These figures describe the matched subset only and must
    not be presented as covering the full customer base.
    """
    sql = """
    DELETE FROM analytics.demographic_kpis;
    INSERT INTO analytics.demographic_kpis
    WITH matched AS (
        SELECT
            u.age_band,
            u.country,
            c.total_stake,
            c.operator_revenue_from_customer
        FROM analytics.customer_kpis c
        JOIN cleaned.users u ON u.user_id = c.user_id
    ),
    totals AS (
        SELECT SUM(total_stake) AS total_stake_all, SUM(operator_revenue_from_customer) AS total_revenue_all
        FROM matched
    ),
    by_age AS (
        SELECT
            'age_band' AS dimension_type,
            age_band AS dimension_value,
            COUNT(*) AS customers,
            SUM(total_stake) AS total_stake,
            SUM(operator_revenue_from_customer) AS operator_revenue
        FROM matched
        GROUP BY age_band
    ),
    by_country AS (
        SELECT
            'country' AS dimension_type,
            country AS dimension_value,
            COUNT(*) AS customers,
            SUM(total_stake) AS total_stake,
            SUM(operator_revenue_from_customer) AS operator_revenue
        FROM matched
        GROUP BY country
    )
    SELECT
        d.dimension_type,
        d.dimension_value,
        d.customers,
        d.total_stake,
        d.operator_revenue,
        (d.total_stake * 100.0) / t.total_stake_all AS stake_share_pct,
        (d.operator_revenue * 100.0) / t.total_revenue_all AS revenue_share_pct
    FROM (SELECT * FROM by_age UNION ALL SELECT * FROM by_country) d
    CROSS JOIN totals t
    ORDER BY d.dimension_type, d.total_stake DESC;
    """
    connection.execute(sql)
    connection.commit()
    logger.info("Populated analytics.demographic_kpis")


def main() -> None:
    """Generate all KPI datasets inside the analytics schema."""
    connection = get_connection()
    try:
        create_kpi_tables(connection, KPI_SQL_PATH)
        populate_monthly_kpis(connection)
        populate_customer_kpis(connection)
        populate_product_kpis(connection)
        populate_retention_kpis(connection)
        populate_risk_kpis(connection)
        populate_marketing_kpis(connection)
        populate_demographic_kpis(connection)

        print("KPI datasets generated successfully.")
        logger.info("KPI generation completed successfully.")
    finally:
        connection.close()


if __name__ == "__main__":
    main()
