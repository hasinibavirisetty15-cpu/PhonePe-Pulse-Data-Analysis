<!-- Paste these sections into your existing README.md (do not replace the whole file). -->

## Data validation

`scripts/validate_data.py` runs 22 automated checks on the six original files and the merged tables and writes
`reports/validation_report.md`.

- **Checks fully passed: 20 of 22 (90.9%)**
- **Overall unit pass rate: 99.998%** (250,268 of 250,273 units tested)
- The two remaining checks are documented data limitations, not errors:
  1. `aggregated_user` covers 17 of 20 quarters (it ends at 2022 Q1), so brand charts stop there.
  2. 4 of 14,640 `map_user` rows (Arunachal Pradesh districts Anjaw and Shi Yomi, 2018) have users but no transactions.
- Method: each check tests one rule on many units (rows, state-quarters or tables). There is no external ground truth,
  so this measures internal consistency (for example: aggregated totals equal the sum of the district tables; top lists equal
  the district tables; registered users never fall), not accuracy against the real world.

## Merged analysis table

`scripts/build_master_table.py` validates the schema of all six files and merges them:

- `data/master_long.csv` - one table with all six sources stacked (51,442 rows, a `source_table` column, a shared set of key columns).
- `data/master_district_quarter.csv` - district x quarter table with transactions, registered users and top-list flags.

Findings that shaped the merge: the tables have different grains; district names carry a " district" suffix in the map tables only;
9 district names repeat across states (so a `district_key` of district + state is used); Delhi's "central district" (map tables) and
"central delhi" (top tables) are the same district (identical numbers) and are unified.

## KPIs, YoY growth and CAGR

`scripts/compute_kpis.py` writes every KPI used in the report to `outputs/`.

| KPI (2018-2022) | Value |
|---|---:|
| Total transaction value | 12,140,593 Cr |
| Total transactions | 71.7 billion |
| Average transaction value | Rs 1,693 |
| Registered users (2022 Q4) | 433.9 million |
| Transactions per registered user (2022) | 90.6 (10.6 in 2018) |
| CAGR transaction value 2018-2022 | 150.8% |
| CAGR transactions | 145.6% |
| CAGR registered users (year-end) | 43.5% |

YoY transaction value: +286.7% (2019), +133.3% (2020), +136.3% (2021), +85.7% (2022).
"Revenue" in the project brief is interpreted as **transaction value** (money moved through PhonePe), not PhonePe's own revenue.

## Streamlit app

`app/streamlit_app.py` is a minimal Streamlit dashboard with 12 dropdown filters, KPI cards, a map, top states, top districts,
top users, YoY / CAGR and the validation report.

```
pip install -r requirements.txt
streamlit run app/streamlit_app.py
```

## Business recommendation

See `outputs/recommendation_engagement_gap.csv` and the project report. In short: user growth is slowing (+23.6% in 2022) while
transactions per user keep rising, so growth now depends on activation, not sign-ups. Gujarat, West Bengal, Kerala and Uttar Pradesh
have large user bases but below-median transactions per user; lifting them to the median (58 transactions per user) would add about
525 million transactions and about Rs 89,000 crore of annual value (a scenario, not a forecast).

## Updated repository structure

```
PhonePe-Pulse-Dashboard/
├── README.md, dashboard.png, pp_dashboard.csv, prepare_data.py     (existing)
├── requirements.txt
├── app/            streamlit_app.py, data_access.py, geo.py
├── scripts/        phonepe_common.py, build_master_table.py, validate_data.py, compute_kpis.py
├── data/           master_long.csv, master_district_quarter.csv   (raw/ holds the six original csv files)
├── outputs/        KPI, growth, top-list and recommendation csv files
├── reports/        validation_report.md, validation_results.csv
└── docs/           HOW_TO_RUN.md, DEMO_VIDEO_SCRIPT.md
```
