# PhonePe Pulse Data Visualization and Exploration

**Data Analyst Internship Project | Sclaria | November 2026**

**Author:** Bavirisetty Hasini

An end-to-end data analytics project exploring PhonePe Pulse digital payment trends across India from 2018 Q1 to 2022 Q4. The project combines Python-based data processing, KPI analysis, data validation, an interactive Streamlit dashboard, and a Tableau Public visualization.

## Project links
- **Demo Video:** https://drive.google.com/file/d/10p_5JchI3xb719wCk5q_Z9W-8mvPFh86/view?usp=drive_link
- **Tableau Public Dashboard:** https://public.tableau.com/app/profile/hasini.bavirisetty/viz/PhonePePulseDashboard_17947499605220/PhonePePulseDataDashboard
- **GitHub Repository:** https://github.com/hasinibavirisetty15-cpu/PhonePe-Pulse-Data-Analysis
- **Streamlit:** https://phonepe-pulse-data-analysis-vd4ner9je9wjqrrqronhbe.streamlit.app/?
## Project objectives

- Analyze digital transaction trends across Indian states and districts.
- Measure transaction value, transaction volume, and user growth.
- Identify leading states, districts, and payment categories.
- Calculate year-on-year growth and compound annual growth rates (CAGR).
- Explore user engagement and regional differences.
- Build interactive dashboards for data exploration.
- Validate data consistency and document limitations.

## Technology stack

- Python
- Pandas
- Streamlit
- Plotly
- Tableau Public
- CSV datasets
- Git and GitHub

## Dataset overview

The analysis covers:

- 36 Indian states and union territories.
- 20 quarters from 2018 Q1 to 2022 Q4.
- Aggregated transactions and users.
- State-level and district-level transaction and user information.
- Top transaction and user statistics.

The project uses six PhonePe Pulse source datasets.

## Project structure

```text
PhonePe-Pulse-Data-Analysis/
│
├── app/
│   ├── streamlit_app.py
│   └── data_access.py
│
├── data/
│   ├── master_long.csv
│   ├── master_district_quarter.csv
│   └── pp_dashboard.csv
│
├── docs/
│   ├── DEMO_VIDEO_SCRIPT.md
│   ├── HOW_TO_RUN.md
│   └── README_additions.md
│
├── outputs/
│   ├── KPI and growth summaries
│   ├── payment type analysis
│   ├── district and state rankings
│   └── recommendation and seasonality outputs
│
├── reports/
│   ├── PhonePe_Pulse_Project_Report.pdf
│   ├── validation_report.md
│   ├── validation_results.csv
│   └── figures/
│       └── dashboard screenshots
│
├── scripts/
│   ├── build_master_table.py
│   ├── compute_kpis.py
│   ├── validate_data.py
│   ├── prepare_data.py
│   └── form_pay_common.py
│
├── README.md
└── requirements.txt
```

## Interactive Streamlit dashboard

The Streamlit application provides five main sections:

1. **Overview:** Overall KPIs, transaction distribution, state rankings, and quarterly trends.
2. **Growth:** Year-on-year growth and CAGR analysis.
3. **Users and Engagement:** Registered users and transaction engagement patterns.
4. **Top Districts:** District-level transaction and user rankings.
5. **Data Quality:** Validation results and data-quality observations.

The dashboard includes interactive filters for exploring the dataset.

## Key findings

- Total transaction value in the analyzed dataset: approximately ₹12,140,593 crore.
- Total transaction volume: approximately 71.7 billion transactions.
- Transaction value increased from approximately ₹162,305 crore in 2018 to ₹6,426,633 crore in 2022.
- Transaction value CAGR: approximately 150.8%.
- Registered users increased from approximately 102.3 million at the end of 2018 to 433.9 million at the end of 2022.
- Registered-user CAGR: approximately 43.5%.
- Telangana, Maharashtra, Karnataka, Andhra Pradesh, and Rajasthan were among the leading states by transaction value.
- Peer-to-peer payments accounted for approximately 80.1% of transaction value, while merchant payments represented approximately 46.2% of transaction volume.

*Transaction value represents the value of payments processed in the dataset, not PhonePe's revenue.*

## Data validation

The validation process performed 22 checks.

- Fully passed checks: 19 out of 22.
- Overall unit pass rate: 99.972% (250,204 out of 250,273 units).
- Target validation threshold: 80% — met.

### Data-quality observations

- Aggregated transaction reconciliation against map transaction data passed for 656 of 720 state-quarter comparisons (91.11%).
- Aggregated user data covers 17 of the 20 quarters.
- Four map-user rows did not have matching map-transaction rows.

These differences are documented rather than silently excluded. Refer to the validation report in `reports/` for details.

## Installation and execution

### 1. Clone the repository

```bash
git clone https://github.com/hasinibavirisetty15-cpu/PhonePe-Pulse-Data-Analysis.git
cd PhonePe-Pulse-Data-Analysis
```

### 2. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 3. Run the Streamlit dashboard

```bash
python -m streamlit run app/streamlit_app.py
```

The dashboard will open in your browser.

### 4. Rebuild analysis outputs

The processing scripts require the original six source CSV datasets in the expected `data/raw/` location.

After placing those source files there, run the scripts from the project root in the documented order:

```bash
python scripts/prepare_data.py
python scripts/build_master_table.py
python scripts/compute_kpis.py
python scripts/validate_data.py
```

Refer to `docs/HOW_TO_RUN.md` for the detailed execution instructions.

## Business recommendation

The analysis identifies opportunities to improve transaction engagement in states with relatively low transactions per registered user.

The project includes an engagement-gap scenario in `outputs/recommendation_engagement_gap.csv`. This is an illustrative analytical scenario, not a guaranteed forecast.

## Project deliverables

- Python data processing and analysis scripts.
- Interactive Streamlit dashboard.
- Tableau Public dashboard.
- KPI summaries and analytical CSV outputs.
- Data validation report and results.
- Project report PDF.
- Dashboard screenshots.

## Limitations

- The dataset covers 2018 Q1 to 2022 Q4 and does not represent current PhonePe activity.
- Aggregated user data has incomplete quarter coverage.
- Some state-quarter transaction reconciliation differences remain.
- The recommendation scenario is illustrative and depends on the assumptions documented in the analysis.

## Author

**Bavirisetty Hasini**  
B.Sc. Computer Science Student  
Data Analyst Internship Project — Sclaria  
November 2026
