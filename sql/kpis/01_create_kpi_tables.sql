CREATE SCHEMA IF NOT EXISTS analytics;

-- NOTE ON SIGN CONVENTION (see docs/assumptions.md):
-- customer_net_result = what customers won minus what they staked (negative = customers
--   lost money on balance). operator_revenue = the mirror image (what customers staked
--   minus what they were paid out), i.e. BetXchange's gross gaming revenue. A positive
--   operator_revenue is GOOD for the company. Earlier versions of this project reported
--   customer_net_result as if it were "company net profit", which inverted the real
--   financial conclusion. operator_revenue is the figure to use for company profitability.
CREATE OR REPLACE TABLE analytics.monthly_kpis (
    month_label VARCHAR,
    active_customers BIGINT,
    transaction_count BIGINT,
    total_stake DOUBLE,
    total_paid_out DOUBLE,
    total_win DOUBLE,
    customer_net_result DOUBLE,
    operator_revenue DOUBLE,
    operator_margin_pct DOUBLE,
    avg_customer_net_result DOUBLE,
    source_month VARCHAR
);

CREATE OR REPLACE TABLE analytics.customer_kpis (
    user_id VARCHAR,
    transaction_count BIGINT,
    total_stake DOUBLE,
    total_win DOUBLE,
    customer_net_result DOUBLE,
    operator_revenue_from_customer DOUBLE,
    latest_activity_month VARCHAR,
    net_margin_pct DOUBLE
);

-- product_kpis financial columns are MODELED, not directly measured: the source
-- transactions table has no product dimension, so stake/win/revenue are allocated to
-- each user's products in proportion to that user's share of slip volume that month.
-- Columns are prefixed est_ to make this explicit. total_slip_count and active_users
-- are directly measured (not estimated).
CREATE OR REPLACE TABLE analytics.product_kpis (
    product_category VARCHAR,
    source_month VARCHAR,
    total_slip_count BIGINT,
    active_users BIGINT,
    avg_slips_per_user DOUBLE,
    est_total_stake DOUBLE,
    est_total_win DOUBLE,
    est_operator_revenue DOUBLE
);

CREATE OR REPLACE TABLE analytics.retention_kpis (
    cohort_month VARCHAR,
    activity_month VARCHAR,
    unique_customers BIGINT,
    customers_with_slips BIGINT,
    customers_with_transactions BIGINT,
    retention_rate DOUBLE
);

-- risk_kpis: documented, auditable, data-grounded exposure indicators. Thresholds are
-- computed per month (95th percentile of that month's transaction stake), not fixed
-- dollar amounts, because monthly volume changes materially across the period. This
-- table cannot and does not claim to detect fraud, collusion, or multi-accounting:
-- the source data has no device, IP, payment method, or account-linkage fields. See
-- docs/assumptions.md for the full methodology and its limits.
CREATE OR REPLACE TABLE analytics.risk_kpis (
    source_month VARCHAR,
    total_transactions BIGINT,
    large_stake_threshold DOUBLE,
    large_stake_transaction_count BIGINT,
    large_stake_share_pct DOUBLE,
    customer_win_event_count BIGINT,
    customer_win_event_share_pct DOUBLE,
    top10_user_stake_share_pct DOUBLE,
    operator_margin_pct DOUBLE
);

-- marketing_kpis: summarises the GA4 website traffic export (Web Traffic - <month>-24.csv).
-- This export has NO campaign, channel, source/medium, or user_id field, so it cannot
-- support "campaign effectiveness" or "acquisition channel" claims. It can only describe
-- aggregate, anonymous website engagement. See docs/assumptions.md.
CREATE OR REPLACE TABLE analytics.marketing_kpis (
    source_month VARCHAR,
    total_page_views BIGINT,
    avg_daily_total_users DOUBLE,
    avg_events_per_session DOUBLE,
    top_country VARCHAR,
    top_country_share_pct DOUBLE,
    za_traffic_share_pct DOUBLE
);

-- demographic_kpis: stake/revenue contribution by age band and by country.
-- IMPORTANT COVERAGE LIMIT: only 7,918 of 24,142 transacting customers (33%) have a
-- matching row in cleaned.users -- the raw Users exports do not cover every customer
-- who placed a bet. These figures describe the MATCHED SUBSET ONLY and must not be
-- presented as covering the full customer base. See docs/assumptions.md.
CREATE OR REPLACE TABLE analytics.demographic_kpis (
    dimension_type VARCHAR,
    dimension_value VARCHAR,
    customers BIGINT,
    total_stake DOUBLE,
    operator_revenue DOUBLE,
    stake_share_pct DOUBLE,
    revenue_share_pct DOUBLE
);

