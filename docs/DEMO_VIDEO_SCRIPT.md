
# PhonePe Pulse Data Visualization and Exploration
## Demo Video Script
**Target duration:** 13–14 minutes

### Before Recording

Open the following:
- GitHub project repository
- Tableau Public dashboard
- Streamlit application
- reports/validation_report.md

Record your screen with OBS Studio or Windows Xbox Game Bar (Windows + G).

Speak clearly and demonstrate the actual project.

---

### 1. Introduction (0:00–0:45)

Hello everyone. My name is Hasini Bavirisetty.

I am presenting my PhonePe Pulse Data Visualization and Exploration project, completed as part of my Sclaria Data Analyst Internship.

The objective of this project is to analyze digital payment trends across India using PhonePe Pulse data and develop interactive dashboards that communicate meaningful insights.

### 2. Dataset Overview (0:45–2:15)

The project uses PhonePe Pulse datasets covering 2018 Q1 to 2022 Q4 across 36 states and union territories.

The datasets include:
- Aggregated transactions
- Aggregated users
- Map transactions
- Map users
- Top transactions
- Top users

These datasets contain information at different levels, including state, district, quarter, payment category and brand.

### 3. Data Processing and Integration (2:15–4:30)

I used Python and Pandas for data cleaning, processing and integration.

The build_master_table.py script validates the expected schemas, standardizes state and district names, and combines the source datasets.

Special attention was given to district-name inconsistencies, including Delhi district aliases.

The merged master_long table contains 51,442 rows and includes a source_table column to identify the original dataset.

A separate district-quarter table combines transaction and user information.

Registered users represent cumulative totals, so they are not added across quarters.

### 4. Data Validation (4:30–6:00)

I performed 22 validation checks to assess data quality and consistency.

According to the validation report:
- 19 out of 22 checks passed completely.
- The overall unit pass rate was 99.972%.
- 250,204 out of 250,273 tested units passed.

The validation target of 80% was achieved.

There are three non-passing checks that need to be understood:

1. Aggregated transaction reconciliation has a 91.11% pass rate.
2. Aggregated user data covers only 17 of the 20 quarters.
3. Four Arunachal Pradesh map-user records have no corresponding map-transaction records.

These limitations are documented in the validation report.

The validation measures internal consistency and does not establish accuracy against external ground truth.

### 5. Tableau Dashboard Demonstration (6:00–9:00)

Now I will demonstrate the interactive Tableau Public dashboard.

The dashboard provides an overview of digital payment activity across India.

It includes:
- KPI cards
- Geographic visualization
- Transaction trends
- Top-performing states
- Payment category analysis

The dashboard provides filters for year, quarter, half-year, period, phase, state, state tier, region, transaction type and metric.

I will demonstrate how selecting a region and year changes the visualizations.

The dashboard helps users compare payment activity across states and time periods.

[Tableau Public Dashboard](https://public.tableau.com/app/profile/hasini.bavirisetty/viz/PhonePePulseDashboard_)

### 6. Growth Analysis (9:00–10:30)

The project also examines year-over-year growth and compound annual growth rates.

The analysis shows strong growth in digital payment activity during the study period.

The calculated CAGR values are:
- Transaction value: 150.8%
- Transaction count: 145.6%
- Registered users: 43.5%

Transactions per user increased from approximately 10.6 to 90.6.

These findings demonstrate the expansion of digital payments and increasing engagement.

### 7. Streamlit Application (10:30–12:00)

In addition to Tableau, I developed a Streamlit application using Python.

The application provides interactive filters, KPI cards, geographic analysis, top-state comparisons, district-level user analysis, growth metrics and data-quality information.

I will demonstrate a filter selection and show how the visualizations respond.

### 8. Key Insights and Recommendations (12:00–13:30)

The analysis highlights differences between payment categories.

Peer-to-peer payments account for approximately 41% of transactions and 80% of transaction value.

Merchant payments account for approximately 46% of transactions and 16% of transaction value.

Telangana, Maharashtra and Karnataka are among the leading states.

One important observation is that user growth slowed while transactions per user continued to increase.

Therefore, a useful business recommendation is to focus on improving user activation and engagement.

The analysis also identifies opportunities to improve engagement in Gujarat, West Bengal, Kerala and Uttar Pradesh.

The estimated opportunity of approximately 525 million additional transactions and Rs 89,000 crore in transaction value is a scenario based on reaching median engagement, not a forecast.

### 9. Limitations and Conclusion (13:30–14:30)

This project has certain limitations.

- The available brand dataset ends in 2022 Q1.
- Some district-level records have reconciliation differences.
- Region and state-tier classifications are analytical groupings.
- Transaction value should not be interpreted as PhonePe revenue.
- Additional district-level visualizations can be developed in the future.

To conclude, this project helped me apply Python, Pandas, SQL concepts, data analysis and visualization techniques to a real-world digital payments dataset.

Thank you for watching my project demonstration.
