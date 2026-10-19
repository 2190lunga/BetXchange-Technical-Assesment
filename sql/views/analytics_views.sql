CREATE SCHEMA IF NOT EXISTS analytics;

CREATE OR REPLACE VIEW analytics.vw_user_analysis AS
SELECT
    u.user_id,
    u.age,
    u.age_band,
    u.country,
    u.registration_date,
    DATE_TRUNC('month', u.registration_date)::DATE AS registration_month,
    COUNT(DISTINCT s.user_id) AS slip_activity_count,
    COUNT(DISTINCT t.user_id) AS transaction_activity_count,
    CASE
        WHEN COUNT(DISTINCT s.user_id) > 0 OR COUNT(DISTINCT t.user_id) > 0 THEN 'Active'
        ELSE 'Inactive'
    END AS engagement_status
FROM cleaned.users u
LEFT JOIN cleaned.slips s ON s.user_id = u.user_id
LEFT JOIN cleaned.transactions t ON t.user_id = u.user_id
GROUP BY
    u.user_id,
    u.age,
    u.age_band,
    u.country,
    u.registration_date;

CREATE OR REPLACE VIEW analytics.vw_betting_analysis AS
SELECT
    s.product_category AS betting_product,
    s.source_month AS analysis_month,
    COUNT(*) AS activity_records,
    SUM(s.slip_count) AS total_slips,
    AVG(s.slip_count) AS avg_slips_per_activity,
    COUNT(DISTINCT s.user_id) AS active_users
FROM cleaned.slips s
GROUP BY
    s.product_category,
    s.source_month;

CREATE OR REPLACE VIEW analytics.vw_financial_analysis AS
SELECT
    t.source_month,
    SUM(t.price_total) AS total_stake,
    SUM(t.paid_out) AS total_paid_out,
    SUM(t.win_total) AS total_win,
    SUM(t.customer_net_result) AS customer_net_result,
    SUM(t.operator_revenue) AS operator_revenue,
    CASE
        WHEN SUM(t.price_total) > 0 THEN (SUM(t.operator_revenue) * 100.0) / SUM(t.price_total)
        ELSE 0
    END AS operator_margin_pct,
    AVG(t.customer_net_result) AS avg_customer_net_result,
    COUNT(DISTINCT t.user_id) AS active_users
FROM cleaned.transactions t
GROUP BY t.source_month;

CREATE OR REPLACE VIEW analytics.vw_retention_analysis AS
SELECT
    DATE_TRUNC('month', u.registration_date)::DATE AS cohort_month,
    u.source_month AS activity_month,
    COUNT(DISTINCT u.user_id) AS unique_customers,
    COUNT(DISTINCT CASE WHEN s.user_id IS NOT NULL THEN u.user_id END) AS customers_with_slips,
    COUNT(DISTINCT CASE WHEN t.user_id IS NOT NULL THEN u.user_id END) AS customers_with_transactions
FROM cleaned.users u
LEFT JOIN cleaned.slips s
    ON s.user_id = u.user_id
   AND s.source_month = u.source_month
LEFT JOIN cleaned.transactions t
    ON t.user_id = u.user_id
   AND t.source_month = u.source_month
GROUP BY
    DATE_TRUNC('month', u.registration_date)::DATE,
    u.source_month
ORDER BY cohort_month, activity_month;

-- vw_risk_analysis: user-month exposure summary.
--
-- Methodology (see docs/assumptions.md for full detail):
-- - stake_percentile_band classifies each user-month by where its total stake falls in
--   that MONTH's own stake distribution (percentile, computed via NTILE over all
--   user-months in the same source_month). This replaces fixed dollar thresholds
--   (previously 1000/5000) that had no stated justification and did not adjust as
--   monthly volume grew ~75% across the period.
-- - customer_result_flag reports the correct, non-inverted direction: a user-month
--   where the CUSTOMER came out ahead (customer_net_result > 0) is a payout-risk /
--   exposure event FOR THE OPERATOR, not a "loss" for the business. A user-month where
--   the customer lost money is revenue for the operator and is labeled accordingly.
-- - This view cannot detect fraud, collusion, bonus abuse, or multi-accounting: the
--   source data has no device, IP, payment method, or account-linkage fields.
CREATE OR REPLACE VIEW analytics.vw_risk_analysis AS
WITH user_month AS (
    SELECT
        t.user_id,
        t.source_month,
        COUNT(*) AS transaction_events,
        SUM(t.price_total) AS total_stake,
        SUM(t.win_total) AS total_win,
        SUM(t.customer_net_result) AS customer_net_result,
        SUM(t.operator_revenue) AS operator_revenue
    FROM cleaned.transactions t
    GROUP BY t.user_id, t.source_month
),
ranked AS (
    SELECT
        *,
        NTILE(100) OVER (PARTITION BY source_month ORDER BY total_stake) AS stake_percentile
    FROM user_month
)
SELECT
    user_id,
    source_month,
    transaction_events,
    total_stake,
    total_win,
    customer_net_result,
    operator_revenue,
    CASE
        WHEN total_stake > 0 THEN (operator_revenue * 100.0) / total_stake
        ELSE 0
    END AS operator_margin_pct,
    CASE
        WHEN stake_percentile > 99 THEN 'Very high (top 1% of stake this month)'
        WHEN stake_percentile > 95 THEN 'High (top 5% of stake this month)'
        WHEN stake_percentile > 80 THEN 'Elevated (top 20% of stake this month)'
        ELSE 'Normal'
    END AS stake_percentile_band,
    CASE
        WHEN customer_net_result > 0 THEN 'Customer net win (payout exposure for operator)'
        ELSE 'Customer net loss (revenue for operator)'
    END AS customer_result_flag
FROM ranked;

-- vw_marketing_analysis: GA4 website traffic summary (daily + country mix).
-- See docs/assumptions.md: this source has no campaign/channel/user_id dimension and
-- cannot be linked to the betting users/transactions/slips tables.
CREATE OR REPLACE VIEW analytics.vw_marketing_analysis AS
SELECT
    source_month,
    day_index,
    page_views,
    total_users,
    events_per_session
FROM cleaned.marketing_daily_traffic
ORDER BY source_month, day_index;

