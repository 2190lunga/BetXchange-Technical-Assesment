# BetXchange Data Analyst Assessment

## Presentation-ready executive brief

This document is designed to support a leadership presentation using the same validated analytics outputs already generated in the project:
- output/monthly_kpis.csv
- output/customer_kpis.csv
- output/product_kpis.csv
- output/retention_kpis.csv
- output/risk_kpis.csv
- output/marketing_kpis.csv

The metrics and messages below should be presented in PowerPoint using the same source-of-truth outputs used in the Power BI dashboard. This reduces risk of mismatched numbers between the dashboard and the presentation.

**Revision note:** an earlier version of this document reported `net_profit` (win minus
stake, a customer-level figure) as if it were the company's profit. Because customers
collectively lose money against a bookmaker by design, this inverted the real
conclusion: BetXchange's actual operator revenue (stake minus payout) is positive and
growing every month. This revision corrects that, fixes a join bug that inflated
product-level figures to impossible magnitudes, replaces unexplained fixed risk
thresholds with documented, data-derived ones, and adds a Marketing Analysis slide
backed by GA4 website traffic data that was previously never ingested. Full methodology
and every assumption is logged in docs/assumptions.md.

---

## Slide 1 — Title Page

Title: BetXchange Data Analyst Assessment

Subtitle:
- Candidate Name: [Insert candidate name]
- Date: 2026-10-18
- Assessment Overview: Customer behaviour, product performance, retention, risk, and growth analysis

Presentation message:
- BetXchange requires a data-driven view of customer value, loyalty, profitability, and risk exposure.
- This presentation summarises the findings from the May–July 2024 data window.

---

## Slide 2 — Executive Summary

### Main findings
- The business shows meaningful monthly activity across the three-month period, with a clear pattern of customer engagement and transaction activity.
- Product performance varies materially by category, which supports product mix and commercial focus.
- **Operator revenue (stake minus payout) is positive and growing every month**: +R7.4m (May), +R9.9m (June), +R16.6m (July), a margin of roughly 4.4%-5.7% of stake. This is the business's actual profitability signal.
- Retention remains meaningful, with cohort-based retention rates above 80% in the validated results.
- Revenue is highly concentrated: the top 1% of users by monthly stake (148 users in July) account for 77% of that month's stake volume. This is a dependency/concentration signal, not evidence of losses.

### Opportunities
- Improve the retention of high-value cohorts by focusing on engagement and repeat behaviour.
- Shift marketing and commercial effort toward the most active and profitable customer segments.
- Prioritise product categories with stronger commercial contribution and lower volatility.
- Reduce dependency on a small number of high-stake users and monitor payout exposure from large individual wins.

### Risks identified
- Revenue is concentrated: 148 users (top 1% of July's active base) generated 77% of July's stake.
- Large-stake transactions (above that month's own 95th percentile) account for ~91% of stake volume, confirming volume is driven by a small set of large bets.
- 11.6% of July transactions resulted in the customer coming out ahead -- this is the operator's payout exposure and should be monitored for concentration in large individual payouts.

### Executive-level summary statement
BetXchange has strong customer activity, a viable product base, and positive, growing operator revenue. The key management focus is not "losses" but **concentration risk**: a small group of high-stake users drives most of the volume and payout volatility, and retention quality in newer cohorts should be protected.

---

## Slide 3 — Data Overview

### Source files analysed
- Users: 3 monthly source files
- Slips: 3 monthly source files
- Transactions: 3 monthly source files
- Marketing: 3 monthly GA4 website traffic exports (previously never ingested; see below)

### Verified project outputs
- Customer KPI table: output/customer_kpis.csv
- Monthly KPI table: output/monthly_kpis.csv
- Product KPI table: output/product_kpis.csv
- Retention KPI table: output/retention_kpis.csv
- Risk KPI table: output/risk_kpis.csv
- Marketing KPI table: output/marketing_kpis.csv

### Observed data quality findings
- The raw Excel exports were not in a clean analytical format; they contained exported pivot-style layouts and subtotal rows.
- The slip export included both a per-user "Total" row and per-day rows for the same user/product/month; the Total rows were duplicates and are now excluded to avoid double-counting activity.
- The marketing dataset (GA4 website traffic CSVs) was never ingested in the original pipeline because the ingestion script only scanned for `.xlsx` files; it is now ingested directly.
- An earlier product-level KPI query joined slips to transactions without a day-level key, causing a fan-out that inflated product stake figures by several orders of magnitude (e.g. an apparent R1.1 trillion Casino stake in a month where total company stake was R293 million). This is fixed; product financials are now a documented, proportional allocation (see docs/assumptions.md).
- **The raw Users files do not cover every customer who transacted.** Joining `customer_kpis` (24,142 distinct transacting customers) to `cleaned.users` on `user_id` matches only 7,918 customers (33%) -- the remaining 16,224 (67%) placed bets but have no age or country on record. This is a genuine data-governance gap, not a bug in this project's pipeline, and it is disclosed wherever age/country figures are shown (see Slide 4 and docs/assumptions.md).
- The project applied cleaning and standardisation before KPIs were generated.
- The KPI layer was designed to provide a single reporting source for Power BI and presentation use.

### Data quality notes
- The raw source files reflect a 3-month period: May, June, and July 2024.
- The raw exports required transformation before they could support reliable business reporting.
- The cleaned KPI outputs form the single source of truth for the presentation.

---

## Slide 4 — Customer Analysis

### Business question
Who are the customers, how old are they, where do they come from, and how does stake/revenue concentrate by segment?

### Data source
- output/customer_kpis.csv
- output/demographic_kpis.csv (age_band and country, joined to customer_kpis)

### Critical coverage limitation (read before presenting this slide)
Only **7,918 of 24,142 transacting customers (33%)** have a matching row in the raw
Users files. The remaining 16,224 customers (67%) placed bets but have no age or
country on record at all. **Every figure below describes only the matched 33% and must
not be presented as covering the full customer base.** This coverage gap is itself a
finding for Gracia (data governance) -- see docs/assumptions.md.

### Verified values from the project (matched subset, n=7,918)
- Age is heavily concentrated: the 35-44 age band is 38.8% of matched customers but
  49.3% of their stake and 57.5% of their operator revenue.
- The 18-24 age band is under 1% of both stake and revenue in the matched subset.
- Country is extremely concentrated: South Africa is 97.8% of matched customers'
  stake; the "Unknown" country bucket is 1.0%; everywhere else combined (35+
  countries) is only 1.3%. This matches the GA4 marketing finding of ~96% South
  African website traffic.
- `engagement_status` in `vw_user_analysis` is "Active" for 100% of matched users (zero
  variation) -- it is not currently a useful differentiator and should not be
  presented as one.

### Recommended visuals
- Stake/revenue share by age band (bar chart, matched subset only)
- Stake share by country: South Africa vs Unknown vs Rest of world (matched subset only)
- Always display the 33% coverage caveat alongside these visuals

### Suggested message
- Among the customers we can identify by age/country, value is concentrated in the
  35-44 age band and overwhelmingly in South Africa.
- The bigger finding is the data gap itself: two-thirds of transacting customers have
  no demographic record, which limits how far this kind of segmentation can go until
  the Users data collection is fixed.

### Key business interpretation
Demographic concentration (age, country) is a real but partial signal -- it is only as
reliable as its 33% coverage. Closing the Users-to-Transactions data gap should be a
near-term governance priority before demographic segmentation is used to drive major
commercial decisions.

---

## Slide 5 — Betting Activity Analysis

### Business question
Which products perform best, which categories are most popular, and how activity changes over time?

### Data source
- output/product_kpis.csv
- output/monthly_kpis.csv

### Recommended visuals
- Monthly transaction trend by month
- Product category contribution chart
- Product level total stake and total win comparison
- Active customer monthly trend

### Verified KPI examples
- Monthly KPI table shows an increasing monthly active customer count from May to July.
- Transaction and stake activity rise materially across the three-month period.
- Product KPI outputs indicate a large product mix spread across categories and should be used for category-level commercial decisions.

### Business takeaway
The business is not only growing in activity, but also showing product-level concentration. That supports both marketing investment and product strategy decisions.

---

## Slide 6 — Financial Analysis

### Business question
What is the size of betting activity, what are the payout trends, and how are the core financial metrics behaving?

### Data source
- output/monthly_kpis.csv
- output/product_kpis.csv

### Recommended KPI cards
- Total Stake
- Total Win
- Operator Revenue (stake minus payout)
- Active Customers
- Transaction Count

### Verified observations
The validated monthly KPI exports show that:
- Total stake and total win are material at monthly level, and both are rising.
- Operator revenue (BetXchange's gross gaming revenue) is **positive and growing**: +R7.4m (May) -> +R9.9m (June) -> +R16.6m (July).
- Operator margin (revenue as a % of stake) is 4.4% (May), 4.4% (June), 5.7% (July) -- within a typical bookmaker range.
- Transaction volume rises month on month.

### Recommended slide wording
- Betting activity remains substantial across the period and is accelerating.
- The business is generating increasing operator revenue; this is healthy, expected bookmaker economics (customers losing money on balance is how a sportsbook/casino earns revenue), not a sign of distress.
- The commercial question is not "why is profit negative" but **how dependent is this revenue on a small number of high-stake users** (see Risk Analysis).

### Why it matters
This metric set helps the business confirm that growth is translating into real revenue, and separates genuine financial performance from customer-level win/loss framing that does not represent the company's position.

---

## Slide 7 — Retention Analysis

### Business question
How many users return, and which segments remain engaged over time?

### Data source
- output/retention_kpis.csv
- output/customer_kpis.csv

### Verified values from the project
The validated retention KPI file shows a realistic cohort retention profile:
- March cohort → July retention: 87.55%
- March cohort → June retention: 82.23%
- March cohort → May retention: 80.10%

### Recommended visuals
- Retention matrix by cohort month and activity month
- Bar chart of retention rate by activity month
- Cohort comparison chart

### Key interpretation
Retention is strongest in the most recent activity window, suggesting the business is retaining a meaningful share of active users over time. This is a strategically important area for Warren and Ryan.

### Recommendation
Focus on improving repeat engagement among lower-retention cohorts and protect the higher-retention groups with better offer design and customer experience.

---

## Slide 8 — Risk Analysis

### Business question
Where is BetXchange's revenue and stake volume concentrated, and what exposure does that create for the operator?

### Data source
- output/risk_kpis.csv
- output/vw_risk_analysis.csv

### Methodology (fully reproducible, see docs/assumptions.md)
- **large_stake_threshold** is that month's own 95th percentile of transaction stake (not a fixed dollar amount), so it adapts as volume grows.
- **customer_win_event_share_pct** is the share of transactions where the customer came out ahead -- this is payout exposure for the operator, not a company "loss".
- **top10_user_stake_share_pct** and the stake-percentile segmentation measure revenue concentration/dependency.
- This methodology **cannot detect fraud, collusion, bonus abuse, or multi-accounting**: the source data has no device, IP, payment method, or account-linkage fields. It only measures stake concentration and payout exposure.

### Verified values from the project (July)
- Operator margin: 5.7%
- Large-stake transactions (>R3,929, the month's 95th percentile): 5,656 transactions, 90.9% of stake volume
- Top 10 users' share of July stake: 36.3%
- Top 1% of users (148 people): 77.3% of July stake
- Transactions where the customer won (payout exposure): 11.6%

### Recommended visuals
- Stake concentration by percentile segment (bar chart)
- Top 10 / top 1% stake share trend by month
- Operator margin trend
- Large-stake transaction share trend

### Interpretation
Revenue is not at risk of loss -- it is positive and growing. The real exposure is **concentration**: a very small number of users drive the large majority of stake and payout volatility. If a handful of top users change behaviour or experience a large win, monthly results could swing significantly. This is a dependency/liquidity risk, not a profitability crisis.

### Important governance note
This table and view are fully reproducible from `cleaned.transactions` with documented, percentile-based thresholds (see docs/assumptions.md). They measure stake concentration and payout exposure only. They must not be described as fraud detection, and any claim beyond what is listed above would not be verifiable from this dataset.

### Business impact
- dependency on a small number of high-stake users
- payout volatility risk if top users have an unusually good month
- need for concentration monitoring and payout-size review, not generic "loss" control

---

## Slide 9 — Marketing Analysis (new)

### Business question
How much website traffic does BetXchange generate, and what does it reveal about audience reach and engagement?

### Data source
- output/marketing_kpis.csv
- output/marketing_daily_traffic.csv, output/marketing_country.csv

### What this data is (and is not)
The marketing dataset is a GA4 website traffic export (daily page views, daily users,
country mix, gender mix, top landing pages). **It has no campaign, channel, or
source/medium field, and GA sessions cannot be linked to the betting `user_id`.** This
means it can describe aggregate, anonymous website engagement, but it **cannot support
claims about campaign effectiveness, acquisition-channel ROI, or conversion quality** --
those claims appeared in earlier drafts of this project without any supporting data and
have been removed.

### Verified values from the project
- Total monthly page views: ~7.1m (May), ~7.0m (June), ~8.7m (July) -- traffic is growing broadly in line with transaction volume.
- Average daily website users: ~11,600 (May) -> ~13,700 (July).
- South Africa accounts for ~96% of website traffic every month, consistent with BetXchange's primary market.

### Recommended visuals
- Daily page views trend by month
- Country mix (ZA vs rest of world)
- Top landing pages by users

### Interpretation
Website traffic is growing in step with transaction activity, and the audience is
overwhelmingly South African, which supports the company's current market focus. Any
further marketing conclusion (which channels or campaigns are working) would require
campaign-tagged analytics data that does not currently exist in this dataset.

### Recommendation for Gracia / data governance
If campaign-level marketing evaluation is required going forward, GA4 needs to be
configured (or tagged) to capture UTM source/medium/campaign, and ideally a login-linked
user identifier, so traffic can be joined to the betting `user_id`.

---

## Slide 10 — Stakeholder Recommendations

### Ryan — Growth & Strategy
- Prioritise the strongest-performing product categories.
- Invest in retention programmes for high-value cohorts.
- Capture growth from customers with strong repeat activity and engagement.

### Warren — Customer Retention
- Focus retention actions on lower-performing cohorts.
- Improve repeat engagement for customers with weaker activity cycles.
- Use cohort and engagement metrics to personalise communication.

### Craig — Risk Management
- Revenue is positive and growing; the priority is managing **concentration risk**, not "losses".
- Monitor the top 1%/top 10 users' share of monthly stake and the large-stake transaction threshold (recomputed each month from the data, not a fixed number).
- Set a review process for large individual payouts (customer-win transactions), since that is the operator's real payout exposure.

### Holly — Marketing
- Website traffic (GA4) is growing in line with transaction volume and is ~96% South African, consistent with the core market.
- Campaign-level effectiveness cannot currently be measured -- the GA4 export has no channel/campaign dimension and cannot be linked to betting user_id. Recommend adding UTM tagging and a login-linked identifier before claiming channel ROI.
- Use the verified top-landing-page data to review funnel entry points, not to infer acquisition-channel performance.

### Gracia — Data Quality & Governance
- Maintain the raw-to-cleaned-to-KPI audit trail.
- Document metrics and assumptions clearly.
- Use the validated KPI tables as the reporting source-of-truth.

---

## Slide 11 — Business Action Plan

### 30 Day Actions
- Finalise dashboard and KPI review with stakeholders.
- Validate retention and concentration-risk metrics with business owners.
- Review product contribution and stake-concentration trends.
- Agree on the priority customer and product segments.

### 60 Day Actions
- Launch targeted retention campaign to improve repeat activity.
- Introduce a monitoring process for large individual payouts and top-user stake concentration.
- Reassess product mix; scope GA4 campaign tagging if channel-level marketing evaluation is required.

### 90 Day Actions
- Create a formal performance review cycle with stakeholder scorecards.
- Quantify retention uplift, product growth, and concentration-risk reduction.
- Develop an operational action plan tied to ROI and governance requirements.

---

## Slide 12 — Expected Impact

### Revenue opportunities
- Growth in product contribution and stronger activity concentration can improve monetisation.
- Reducing dependency on the top 1% of users reduces revenue volatility, which supports more predictable growth.

### Retention opportunities
- Cohort-based retention is a strong lever for sustainable revenue growth.
- Higher repeat engagement can improve customer lifetime value.

### Operational improvements
- Cleaner and more standardised KPI reporting improves stakeholder decision quality.
- Monthly monitoring of stake concentration and payout exposure can improve business responsiveness.

### Risk reduction opportunities
- Stake-concentration monitoring (top 10 / top 1% share) allows earlier intervention on dependency risk.
- Large-payout review can reduce volatility from a small number of high-stake outcomes.

---

## Slide 13 — Closing Summary

### Key findings
- BetXchange has measurable customer activity and growing engagement signals across the period.
- Operator revenue is positive and growing (+R7.4m to +R16.6m, May to July); the earlier "weak profitability" conclusion was based on an inverted metric and has been corrected.
- Retention remains an important commercial lever.
- Revenue and stake volume are highly concentrated in a small number of users -- this is the real exposure to manage.

### Key recommendations
- Focus on retention and engagement quality.
- Review product contribution and category mix.
- Strengthen concentration-risk monitoring (top-user stake share, large-payout review).
- Use validated KPI outputs as the single reporting source of truth.

### Next steps
- Finalise stakeholder review of dashboard outputs.
- Confirm concentration-risk thresholds and retention definitions with business owners.
- Prepare the final presentation and appendix with supporting analysis.

---

## PowerPoint design guidance

### Branding
- Primary colour: Blue
- Accent: Yellow / Gold
- Secondary: White
- Use a clean, modern executive style with minimal clutter

### Slide styling recommendations
- Use clean KPI cards with strong contrast and concise values
- Use one core message per slide
- Keep titles business-focused and short
- Use charts and visuals to support the story, not overload the audience

### Recommended visual style
- KPI cards for summary metrics
- line charts for time trends
- bar charts for category comparison
- retention matrix for cohort analysis
- risk summary table for operational detail

### Executive presentation guidance
- Keep technical detail out of the main narrative
- Focus on business impact, decisions, and action
- Use the validated KPI tables as the single source of truth
- Ensure all screenshots in the deck align with the Power BI dashboard outputs

---

## Final note
This presentation should be positioned as a business-facing summary of the BetXchange case study, not a technical deep dive. The value of the deck is in translating data into clear decisions, actions, and stakeholder recommendations.
