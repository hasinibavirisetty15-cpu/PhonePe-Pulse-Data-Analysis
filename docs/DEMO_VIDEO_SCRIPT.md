# Demo video script (target length: about 13 minutes; the requirement is 7 to 20 minutes)

How to record on Windows: install OBS Studio (free) or use Xbox Game Bar (Windows key + G -> Record). Record your screen with your voice.
Have these open before you start: the Tableau Public link, the Streamlit app (run `streamlit run app\streamlit_app.py`),
your GitHub repo, and `reports\validation_report.md`. Speak slowly. Total of about 1,800 spoken words.

| Time | What to show | What to say (in your own words) |
|---|---|---|
| 0:00-0:45 | Title slide or the dashboard | Your name, the Sclaria Data Analyst Internship, the project: PhonePe Pulse Data Visualization and Exploration. The goal: turn PhonePe payment data into an interactive dashboard with insights. |
| 0:45-2:15 | The brief and the six csv files | The six tables (aggregated, map, top; transactions and users), 36 states and union territories, 2018 Q1 to 2022 Q4. They have different grains: state-quarter-type, state-quarter-brand, district-quarter, top lists. |
| 2:15-4:30 | `build_master_table.py` and `master_long.csv` | Schema validation first (expected columns and types). Cleaning: state names, the " district" suffix, Delhi's "central district" vs "central delhi" (same numbers). The single merged table has 51,442 rows with a `source_table` column. District x quarter table joins transactions and users. Users are a running total, so they are never added across quarters. |
| 4:30-6:00 | `reports\validation_report.md` | How validation is defined: 22 checks, each tests one rule on many units. 20 of 22 pass fully; overall pass rate 99.998%. The two exceptions are documented limitations (brand data ends 2022 Q1; 4 map_user rows). Be clear that this is internal consistency, not accuracy against the real world. |
| 6:00-9:00 | Tableau Public dashboard | The filled map of India, the KPI cards (12.1M crore, 71.7B payments), the trend line, top 10 states, payment types. Demo the 10 dropdowns: Year, Quarter, Half-year, Period, Phase, State, State Tier, Region, Transaction Type, Metric. Show Region = South, then Year = 2020. Mention the COVID flattening. |
| 9:00-10:30 | Growth page or `outputs\yearly_growth.csv` | YoY: +287%, +133%, +136%, +86%. CAGR 2018 to 2022: value 150.8%, transactions 145.6%, users 43.5%. Transactions per user rose from 10.6 to 90.6. |
| 10:30-12:00 | Streamlit app | 12 dropdowns, KPI cards, map, top states, top users by district, YoY and CAGR tab, data quality tab. Show one filter change and one top-users chart. |
| 12:00-13:30 | Insights and recommendation | Peer-to-peer is 41% of payments but 80% of value; merchant payments are 46% of payments but 16% of value. Telangana, Maharashtra, Karnataka lead. Recommendation: user growth slowed to +23.6% in 2022 while transactions per user keep rising, so focus on activation. Gujarat, West Bengal, Kerala and Uttar Pradesh have big user bases but below-median engagement; lifting them to the median (58 transactions per user) is worth about 525 million transactions and about Rs 89,000 crore a year (a scenario, not a forecast). |
| 13:30-14:30 | Limitations and close | Region and State Tier are my own groupings; transaction value is not PhonePe's revenue; brand data ends 2022 Q1; district-level map and a choropleth are future work. Thank the viewer. |

Tips: do one practice run first; do not read word for word; if you make a mistake, keep going and fix it in the next sentence.
