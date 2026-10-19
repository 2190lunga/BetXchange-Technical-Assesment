-- BetXchange DuckDB schema bootstrap
-- Purpose: establish a clean analytical foundation for raw ingestion and reporting.

CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS curated;
CREATE SCHEMA IF NOT EXISTS analytics;

CREATE TABLE IF NOT EXISTS raw.source_file_log (
    id INTEGER,
    source_name VARCHAR,
    source_month VARCHAR,
    source_type VARCHAR,
    file_path VARCHAR,
    imported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    row_count BIGINT,
    status VARCHAR DEFAULT 'loaded'
);

CREATE TABLE IF NOT EXISTS curated.users (
    user_id VARCHAR,
    age INTEGER,
    registration_date TIMESTAMP,
    country VARCHAR,
    source_file VARCHAR,
    source_month VARCHAR,
    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS curated.slips (
    category VARCHAR,
    unnamed_1 VARCHAR,
    unnamed_2 VARCHAR,
    aviator VARCHAR,
    betgames VARCHAR,
    casino VARCHAR,
    horse_racing VARCHAR,
    lotto VARCHAR,
    sport VARCHAR,
    total VARCHAR,
    source_file VARCHAR,
    source_month VARCHAR,
    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS curated.transactions (
    user_id VARCHAR,
    resolve_time_day VARCHAR,
    price_total DOUBLE,
    paid_out DOUBLE,
    win_total DOUBLE,
    source_file VARCHAR,
    source_month VARCHAR,
    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE VIEW IF NOT EXISTS analytics.vw_user_analysis AS
SELECT
    user_id,
    age,
    registration_date,
    country,
    source_month
FROM curated.users;

CREATE VIEW IF NOT EXISTS analytics.vw_betting_analysis AS
SELECT
    category,
    unnamed_1,
    unnamed_2,
    aviator,
    betgames,
    casino,
    horse_racing,
    lotto,
    sport,
    total,
    source_month
FROM curated.slips;

CREATE VIEW IF NOT EXISTS analytics.vw_financial_analysis AS
SELECT
    user_id,
    resolve_time_day,
    price_total,
    paid_out,
    win_total,
    source_month
FROM curated.transactions;
