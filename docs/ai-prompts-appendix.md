# AI Assistance — Data Appendix

Per the case study requirement ("AI Assistance: Feel free to use any AI tools, provide
the prompt used in the data appendix"), this document records how AI assistance (GitHub
Copilot, Claude Sonnet 5) was used on this project and what it was and was not trusted to
decide on its own.

## Scope of this record

This appendix covers the session in which the KPI pipeline, risk methodology, product
allocation, and marketing ingestion were audited and corrected. Earlier project history
(initial repository scaffolding, first draft of the dashboard and KPI SQL) was carried out
in prior sessions not fully captured here; where this document describes that earlier
work, it is inferred from the code, comments, and file structure actually found in the
repository, and is labeled as such rather than presented as a verbatim prompt log.

## Prompts used in this session (paraphrased, in order)

1. **Initial challenge (verbatim intent, user-authored):** the user challenged the
   project's risk table, asking what method was used to calculate "risk", pointing out
   that source files and the use case were provided but the methodology behind the risk
   table was not explainable, and explicitly warned against hallucinated or unverifiable
   claims.
   - **AI action:** Did not answer from memory or assumption. Read the actual SQL/Python
     that generates `risk_kpis` and `vw_risk_analysis` end-to-end, traced every column to
     its source formula, and reported the exact thresholds and logic found in the code
     (fixed 1000/5000 thresholds, `risky_users` being identical to active-user count),
     flagging that the methodology overstated what the data could support.

2. **Full case-study brief re-pasted by the user**, followed by a request (via guided
   questions) to: (a) fully redesign the risk methodology rather than just relabel it,
   (b) create the missing assumptions log and AI-prompt appendix required by the brief,
   and (c) audit all other stakeholder sections (growth, retention, marketing,
   governance) for similar unverified or fabricated claims, not just risk.
   - **AI action:** Treated this as license to investigate broadly rather than guess. Read
     every KPI-generating script, every SQL view, the dashboard's static HTML/JS, and the
     original raw source directory structure (via the file system) to check whether claims
     in the reports matched what the code could actually produce.

3. **Discovery-driven verification prompts (self-directed, not user-authored):** before
   accepting any surprising finding, ran direct DuckDB queries against the actual database
   to confirm or refute hypotheses rather than inferring from code alone. Specifically
   verified, with real query output, before making any claim or code change:
   - Whether `net_profit`'s sign, aggregated across all transactions, implied a company
     loss or a company gain (confirmed: aggregated negative customer result = positive,
     growing operator revenue).
   - Whether `cleaned.slips` "Total" rows duplicated per-day rows (confirmed: sums nearly
     equal).
   - Whether the product-level financial figures were plausible against the real
     company-wide stake total (confirmed: impossible, off by ~4,000x).
   - Whether a marketing/traffic source file existed in the original dataset but was never
     ingested (confirmed: found real GA4 CSV exports in the source directory that the
     ingestion script's file-type filter silently skipped).

4. **Implementation request:** fix the issues found, at the root (data cleaning layer),
   not just in the dashboard presentation layer, and regenerate every downstream artifact
   from the corrected pipeline.
   - **AI action:** Edited `data_cleaning.py`, `generate_kpis.py`,
     `sql/views/analytics_views.sql`, `sql/kpis/01_create_kpi_tables.sql`; added
     `ingest_marketing_traffic.py`; re-ran the full pipeline
     (`create_duckdb_database.py` → `ingest_excel_to_duckdb.py` →
     `ingest_marketing_traffic.py` → `data_cleaning.py` → `create_analytical_views.py` →
     `generate_kpis.py` → `export_csv_exports.py`) and re-verified the regenerated CSV
     outputs with direct queries before updating any dashboard page or report.

5. **"Visuals that tell the story, use Power BI as inspiration, make visuals reactive to
   each other" (user-authored, verbatim intent).** Followed by two rounds of "this is not
   visible" screenshots pointing at low-contrast text.
   - **AI action:** Rebuilt `dashboard/script.js` with month-keyed reactive data, a
     shared selection state, and new chart types (donut, bar, scatter) that cross-filter
     each other. For the contrast reports, did not guess at a fix -- used the browser
     tools to inspect computed CSS color/background on the actual flagged element each
     time, found the real root cause (reused `.label`/`.muted`/`.eyebrow`/`.footnote`
     classes designed for white panels being placed directly on the dark page background
     in several spots), and fixed each one with a scoped override, verified visually via
     screenshot after every fix rather than declaring it fixed from code alone.

6. **Guide for a 5-page Power BI-style build (user-pasted, from a different tool's
   output) plus "build the actual PowerPoint for you."**
   - **AI action:** Mapped the guide's intent onto the already-corrected field names
     (confirmed with the user first, rather than silently reintroducing `net_profit` /
     `loss_ratio` / `risky_users`), built out all 5 dashboard pages to match, then wrote
     `reports/capture_dashboard_screenshots.py` and `reports/build_presentation.py` to
     generate a real 13-slide `.pptx` from the live dashboard and verified data --
     rather than asking the user to screenshot pages into a different chat tool.

7. **"There were countries and ages of users how was it used for insights?????"
   (user-authored, verbatim).**
   - **AI action:** Did not assume the data was already used. Queried the database
     directly to check whether `age_band`/`country` appeared in any KPI table (they did
     not) and, while building the fix, discovered and disclosed a more serious finding:
     only 33% of transacting customers have a matching row in the Users files at all.
     Built `analytics.demographic_kpis` and the dashboard charts with that 33% coverage
     caveat stated on every chart, table, and sentence that uses the data, rather than
     presenting the matched subset as if it covered everyone.

8. **"We continue pushing the code" / "can we skip this step" / GitHub Pages setup
   (user-authored, iterative, across several turns with repeated command cancellations).**
   - **AI action:** Initialized git, diagnosed a stray Office lock file and a stale/invalid
     cached GitHub credential by inspecting `cmdkey /list` and `credential.helper` rather
     than guessing, corrected the commit author identity when given a real email, and
     pushed. When asked to adapt to "skip" a step the user kept cancelling (setting git
     identity separately), used `git -c user.name=... -c user.email=...` to fold identity
     into the commit command itself instead of insisting on the original multi-step plan.
     When the GitHub Actions Pages workflow failed, opened the actual failed run's logs
     via the browser tool to find the real error ("Pages not enabled for GitHub Actions")
     instead of guessing, and re-triggered the workflow only after confirming the user had
     made the one-time manual settings change only they could make.

## What AI was and was not allowed to decide unilaterally

- **Allowed:** choosing a specific, disclosed statistical method (e.g. 95th percentile for
  a "large stake" threshold, proportional slip-share allocation for product financials)
  when the brief required a judgment call, provided the method and its limits were written
  down in `docs/assumptions.md` rather than left implicit.
- **Not allowed / explicitly avoided:** claiming fraud, collusion, or multi-account
  detection (the data does not support it), claiming marketing campaign effectiveness
  (no campaign/channel field exists in the source data), or presenting a modeled/estimated
  figure without a clear `est_`/"modeled" label.

## How to audit this appendix

Every number referenced above as "confirmed" can be reproduced by running the pipeline
commands listed in `docs/assumptions.md` (Section 9) and querying the resulting
`database/betxchange.duckdb` or reading the corresponding file in `output/`.
