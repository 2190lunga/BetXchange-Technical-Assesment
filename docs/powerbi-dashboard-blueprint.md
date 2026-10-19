# Power BI Dashboard Blueprint

## Purpose
This document turns the validated KPI layer into a stakeholder-ready dashboard specification for BetXchange. The dashboard will be designed to answer the core business questions across growth, customer retention, financial performance, risk, and product opportunities.

## Executive Summary of the KPI evidence
The KPI tables show a clear pattern across the three months in scope:

- May active customers: 11,797
- June active customers: 13,372
- July active customers: 14,887
- Total stakes are material and increasing month-on-month
- **Operator revenue (stake minus payout) is positive and growing every month**: +R7.4m (May), +R9.9m (June), +R16.6m (July)
- Operator margin is consistently 4.4%-5.7%, a typical bookmaker house edge
- Revenue is concentrated: the top 1% of users (148 in July) account for 77% of that month's stake

This means the business is growing in both activity volume and revenue. The real strategic
tension is not growth-vs-profitability, it is **growth-vs-concentration**: a small group of
high-stake users drives most of the volume, which the dashboard should make obvious.

## Dashboard objective
The dashboard should support five stakeholder groups with a single evidence-based narrative:

- Ryan: growth opportunities and expansion viability
- Warren: customer retention and engagement quality
- Craig: stake concentration, payout exposure, and operational concerns
- Holly: website traffic and engagement (campaign-level data does not exist in this dataset, see below)
- Gracia: governance, quality, and traceability

## Proposed dashboard pages

### 1. Executive Overview
Purpose:
- give leadership a 30-second readout of business health

Key visuals:
- KPI cards: active customers, total stake, operator revenue, operator margin, product count
- month-over-month trend line: operator revenue vs total stake
- bar chart: active customers by month
- waterfall or column chart: operator revenue contribution by month
- donut chart: customer activity share by product category

Primary questions answered:
- Are we growing or shrinking?
- Are customer volumes and financial outcomes aligned?
- Where is performance weakening?

### 2. Customer Behaviour and Retention
Purpose:
- understand engagement quality and repeat usage

Key visuals:
- cohort retention matrix by month and retention period
- active user trend by customer segment
- customer lifecycle chart: new vs returning users
- scatter plot: operator revenue from customer vs customer activity
- age band and country segmentation visuals

Primary questions answered:
- Which customer groups stay engaged?
- Where are churn and inactivity risks emerging?
- Are the right users returning over time?

### 3. Product and Betting Activity
Purpose:
- identify which products are driving customer activity and value

Key visuals:
- product category performance matrix
- stacked bar: stake by product category across months
- scatter plot: product category profit vs volume
- heatmap: product by month by active users
- average slips per user by category

Primary questions answered:
- Which products generate the most activity?
- Which categories are profitable or unprofitable?
- Which products are best for growth investment?

### 4. Financial Performance and Risk
Purpose:
- translate customer activity into financial performance and concentration-risk narratives

Key visuals:
- trend chart: total stake, paid out, win, and operator revenue
- KPI panel: operator margin, large-stake transaction share, customer-win transaction share
- bar chart: large-stake transaction count by month
- concentration gauge: top 10 / top 1% user stake share vs prior months
- table: stake-percentile segments (Normal/Elevated/High/Very high) by month

Primary questions answered:
- How much operator revenue is BetXchange generating, and is it growing?
- Which months or user segments drive the most stake and payout volatility?
- How dependent is revenue on a small number of high-stake users?

### 5. Marketing and Website Traffic
Purpose:
- summarise verified GA4 website engagement; explicitly scope out what cannot be measured

Key visuals:
- trend chart: daily page views and daily users by month
- country mix (ZA vs rest of world)
- table: top landing pages by users

Primary questions answered:
- Is website traffic growing in line with transaction volume?
- Where does traffic come from geographically?
- (Explicitly out of scope: which campaign or channel drives conversion -- no campaign/channel field exists in this export, and GA sessions cannot be linked to betting user_id.)

### 6. Campaign and Growth Opportunities
Purpose:
- align customer behaviour with strategic expansion opportunities

Key visuals:
- cohort retention trend
- matrix: customer segment (stake percentile) by margin and stake share
- heatmap: product interest by demographic segment
- map or regional split by country (from user registration data)
- opportunity table: highest-value segments to target

Primary questions answered:
- Which user groups should be prioritized for retention investment?
- Which countries or segments have the strongest commercialisation potential?
- Where should the next growth investment be focused?

## Recommended measures
The base KPI set should be standardised in Power BI and reused across all pages:

- Active customers
- Total stake
- Operator revenue (stake minus payout)
- Operator margin %
- Retention rate
- Product category stake share (modeled allocation, disclosed as such)
- Large-stake transaction count and share
- Top 10 / top 1% user stake share
- Average slips per user
- Customer net margin %
- Website page views and users (marketing, GA4)

## Suggested filters
Include user-controlled slicers for:

- month
- country
- age band
- product category
- customer segment
- user status: new, active, returning, churned

## Design principles
- keep the executive page uncluttered
- use consistent color coding for profit, loss, and risk
- highlight trends and threshold breaches clearly
- ensure metrics are grounded in the upstream SQL KPI tables
- use tooltips to explain assumptions and calculations

## Stakeholder-specific interpretation

### Ryan — Strategy and Growth
Focus on:
- growth trend in users and transaction volume
- product categories generating the most volume
- segments with strongest expansion potential

Key conclusion to test:
The business is growing in user activity and operator revenue; the strategic question is how to reduce dependency on a small group of high-stake users while sustaining growth.

### Warren — Operations and Retention
Focus on:
- repeat customer patterns
- customer engagement by segment
- retention rates by cohort

Key conclusion to test:
Customer acquisition appears healthy, but retention and engagement quality need stronger operational attention.

### Craig — Risk Management
Focus on:
- stake concentration by month (top 10 / top 1% share)
- large-stake transactions (month-specific 95th percentile threshold)
- customer-win transactions (payout exposure for the operator)

Key conclusion to test:
Revenue is healthy, but highly concentrated; a small number of users and large payouts drive most of the volatility. This is a dependency risk, not a loss-making business, and the methodology cannot detect fraud/collusion given the fields available.

### Holly — Marketing and Website Traffic
Focus on:
- website traffic trend (daily page views, daily users)
- geographic mix of traffic
- top landing pages

Key conclusion to test:
Website traffic is growing in line with transactions and is concentrated in South Africa. Campaign-level effectiveness (which channel or campaign drives conversion) **cannot be tested with the current GA4 export**, which has no campaign/channel dimension and cannot be linked to betting user_id.

### Gracia — Governance and Quality
Focus on:
- auditability
- clearly defined KPI logic
- data quality and traceability
- governance notes for assumptions and exclusions

Key conclusion to test:
All KPI definitions must be documented and auditable to support internal governance and stakeholder trust.

## Recommended final dashboard narrative
The story to tell with the dashboard should be:

> BetXchange is seeing strong customer and transaction growth across the period, and operator revenue is positive and increasing every month (a healthy, growing house edge of roughly 4-6% of stake). The real strategic focus is not profitability but **concentration**: a very small number of high-stake users account for the large majority of stake volume and payout volatility. The dashboard should therefore focus on how customer engagement, revenue concentration, and product mix can be reshaped to sustain growth while reducing dependency on a small user base.

## Deliverable output
This blueprint should be used to guide:

1. the Power BI data model
2. page-by-page report layout
3. visual selection and KPI definitions
4. stakeholder narrative in the final presentation

This is the bridge between the validated analytics layer and the final management-ready reporting experience.
