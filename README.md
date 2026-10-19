# BetXchange Technical Assessment

This repository contains a portfolio-ready analytics project for BetXchange, designed to support the assessment requirements around customer behaviour, betting activity, financial performance, retention, risk, and growth opportunities.

## Project Goal

The objective is to build a clean, professional analytics workflow using Python, DuckDB, and Power BI to:

- ingest raw Excel source files,
- transform and validate the data,
- model key business tables,
- create reusable analytical SQL views,
- generate KPI datasets,
- and prepare Power BI reporting assets for stakeholder review.

## Project Structure

```text
BetXchange-Technical-Assessment/
├── data/
│   ├── raw/
│   └── processed/
├── database/
│   └── betxchange.duckdb
├── docs/
├── notebooks/
├── sql/
├── src/
├── reports/
├── dashboard/
├── output/
├── tests/
├── .gitignore
├── README.md
├── requirements.txt
└── .env.example
```

## Folder Purpose

- `data/raw/` stores the original Excel source files as received from the business.
- `data/processed/` stores cleaned, validated, and transformed files ready for analytics.
- `database/` contains the DuckDB analytical database and exported data assets.
- `docs/` holds project documentation, methodology notes, and business context.
- `notebooks/` stores exploratory analysis and rapid validation notebooks.
- `sql/` contains SQL scripts and analytical views for business analysis.
- `src/` houses Python scripts for ingestion, profiling, cleaning, validation, and KPI generation.
- `reports/` stores markdown, output summaries, and generated reports.
- `dashboard/` keeps Power BI assets and theme specification files.
- `output/` stores generated datasets, quality checks, and export files.
- `tests/` contains unit tests and validation checks for the project workflow.

## Business Context

BetXchange needs a reliable analytics solution to understand:

- who its customers are,
- how they behave,
- which betting products are driving value,
- which financial trends matter most,
- how retention and engagement evolve over time,
- and where risk signals or anomalies require attention.

This project is intentionally designed to support those business questions using a repeatable and auditable data pipeline.

## Case Study Context

This project reflects the BetXchange case study based on a three-month dataset covering May, June, and July 2024. The analysis is designed to answer stakeholder questions across strategy, engagement, retention, risk, and marketing.

### Stakeholder lens

- Ryan: growth strategy and business expansion
- Warren: customer retention and operations
- Craig: risk, anomalies, and financial exposure
- Holly: campaigns and marketing effectiveness
- Gracia: governance, quality, and responsible data practice

### Core focus areas

- user behaviour analysis
- betting patterns and product preferences
- financial transactions and risk assessment
- marketing performance
- operational efficiency
- strategic recommendations

### Deliverables expected

- comprehensive analysis report
- stakeholder specific recommendations
- presentation deck
- data appendix and supporting calculations
- documented assumptions and data governance notes -- see [docs/assumptions.md](docs/assumptions.md)
- AI assistance record -- see [docs/ai-prompts-appendix.md](docs/ai-prompts-appendix.md)

This project is therefore framed not only as a technical exercise, but as a business-facing analytics case that must support executive and operational decision-making.

## Recommended Workflow

1. Place the source Excel files into `data/raw/`.
2. Run the ingestion scripts in `src/` to load them into DuckDB.
3. Profile and validate the raw dataset.
4. Clean and transform the data into canonical tables: `users`, `slips`, and `transactions`.
5. Create analytical SQL views.
6. Generate KPI tables.
7. Build Power BI data models and dashboards.

## Getting Started

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## GitHub Notes

This repository is structured to be easy to review, explain, and present during an interview or stakeholder conversation. The project emphasises maintainability, modularity, and business-focused analytics rather than ad hoc analysis.

## Next Steps

This scaffold is the starting point for the assessment. The next step is to define the project architecture and build the database foundation using DuckDB.
