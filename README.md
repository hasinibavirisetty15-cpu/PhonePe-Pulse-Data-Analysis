# PhonePe Pulse Data Visualization and Exploration

An interactive geo-visualization dashboard built in **Tableau Public** on PhonePe Pulse digital-payments data (2018 Q1 – 2022 Q4).
Project for the **Sclaria Data Analyst Internship**.

## Live dashboard

**[Open the dashboard on Tableau Public](https://public.tableau.com/app/profile/hasini.bavirisetty/viz/PhonePePulseDashboard_17947499605220/PhonePePulseDataDashboard)**

![Dashboard overview](screenshots/dashboard.png)

## What the dashboard shows

| Visual | What it answers |
|---|---|
| Filled map of India | Which states move the most money? (colour = selected metric) |
| KPI cards | Total transaction value (12.1M Cr) and total payments (71.7B) |
| Trend line | How transaction value grew quarter by quarter, 2018–2022 |
| Top States bar chart | Top 10 states by transaction value |
| Types bar chart | Payment categories (merchant, peer-to-peer, recharge & bills, ...) |

### 10 dropdown filters

Year, Quarter, Half-year, Period, Phase (Pre-COVID / COVID period / Post-COVID), State, State Tier (High / Medium / Low), Region, Transaction Type, and a **Metric** switch (Amount in crore vs. Transactions).

## Dataset

- Source: the pre-processed PhonePe Pulse files provided with the project brief (aggregated transactions, aggregated users, map and top tables).
- Coverage: 36 states and union territories, 20 quarters (2018 Q1 to 2022 Q4).
- `data/pp_dashboard.csv` is the file loaded into Tableau (3,594 rows, built from the aggregated transaction table).
- Amounts in the raw data are in rupees; the dashboard uses crore (1 crore = 10,000,000).

## How it was built

1. **Cleaned the data with Python (pandas)** – `scripts/prepare_data.py`:
   - fixed state names (`andaman-&-nicobar-islands` -> `Andaman and Nicobar Islands`) so the map recognises every state;
   - added `period`, `quarter_start` (a real date), `amount_cr`, and a `country` column for the map;
   - added grouping columns used as filters: `region`, `state_tier`, `half`, `phase`.
2. **Loaded the CSV into Tableau Public** and set geographic roles (country, state/province).
3. **Built five sheets** (Map, Trend, Top States, Types, two KPI cards) and combined them in one dashboard with 10 dropdowns.
4. **Published** to Tableau Public for a live, shareable link.

## Key insights

- **Strong growth:** yearly transaction value grew from about ₹1.6 lakh crore (2018) to about ₹64 lakh crore (2022), a CAGR of about **151%**. Year-on-year growth was +287% in 2019, +133% in 2020, +136% in 2021 and +86% in 2022: still strong, but slowing as the base gets larger.
- **COVID effect:** the trend line flattens in early 2020 (lockdown period) and then rises steeply.
- **Peer-to-peer carries the money, merchants carry the volume:** peer-to-peer is about 41% of payments but about 80% of the value; merchant payments are about 46% of payments but only about 16% of the value.
- **Average payment size** rose from about ₹1,503 (2018) to about ₹1,836 (2020), then fell to about ₹1,635 (2022), consistent with small merchant payments growing fastest.
- **Concentration:** Telangana (13.6%), Maharashtra (12.2%), Karnataka (11.4%), Andhra Pradesh (9.5%) and Rajasthan (7.5%) together account for about 54% of all value in this dataset.
- **Fast-growing smaller states:** Andaman and Nicobar Islands, Manipur and Assam show the highest growth from 2019 to 2022 (from small starting bases).
- **Users:** registered users in the dataset grew from about 47 million (2018 Q1) to about 434 million (2022 Q4).
- **Seasonality:** Q4 is the busiest quarter overall and Q1 the quietest.

## Notes and limitations

- Region and State Tier are my own groupings for filtering; they are not part of the PhonePe data.
- Telangana ranks above Maharashtra by value in this dataset; the dashboard reports what the data shows.
- Registered users are a running total per quarter, so they should never be summed across quarters.
- Brand (device) data in the aggregated user table ends at 2022 Q1.
- Possible next steps: a users and engagement page, a district-level view, and growth-rate KPI cards.

## Repository structure

```
data/pp_dashboard.csv        data loaded into Tableau
scripts/prepare_data.py      cleaning and feature script (Python, pandas)
screenshots/                 dashboard screenshots
README.md
```

## Author

Bavirisetty Hasini
