"""
Prepare the PhonePe Pulse aggregated-transaction data for Tableau.

Input : aggregated_transaction.csv  (from the provided PhonePe dataset)
Output: data/pp_dashboard.csv       (the file loaded into Tableau Public)

Usage : python scripts/prepare_data.py path/to/aggregated_transaction.csv data/pp_dashboard.csv
"""
import sys
import pandas as pd

SRC = sys.argv[1] if len(sys.argv) > 1 else "aggregated_transaction.csv"
OUT = sys.argv[2] if len(sys.argv) > 2 else "data/pp_dashboard.csv"

# My own grouping of states into regions (not part of the PhonePe data)
REGIONS = {
    "North": ["Delhi", "Haryana", "Himachal Pradesh", "Jammu and Kashmir", "Ladakh",
              "Punjab", "Chandigarh", "Rajasthan", "Uttarakhand"],
    "Central": ["Uttar Pradesh", "Madhya Pradesh", "Chhattisgarh"],
    "West": ["Gujarat", "Maharashtra", "Goa", "Dadra and Nagar Haveli and Daman and Diu"],
    "South": ["Andhra Pradesh", "Telangana", "Karnataka", "Kerala", "Tamil Nadu",
              "Puducherry", "Lakshadweep"],
    "East": ["Bihar", "Jharkhand", "Odisha", "West Bengal", "Andaman and Nicobar Islands"],
    "North East": ["Assam", "Arunachal Pradesh", "Manipur", "Meghalaya", "Mizoram",
                   "Nagaland", "Sikkim", "Tripura"],
}
STATE_TO_REGION = {s: r for r, states in REGIONS.items() for s in states}


def clean_state(s: pd.Series) -> pd.Series:
    # 'andaman-&-nicobar-islands' -> 'Andaman and Nicobar Islands'
    s = s.str.replace("-&-", "-and-", regex=False).str.replace("-", " ", regex=False).str.title()
    return s.str.replace(r"\bAnd\b", "and", regex=True)


df = pd.read_csv(SRC).drop(columns=["Unnamed: 0"], errors="ignore")
df = df.rename(columns={"states": "state"})
df["state"] = clean_state(df["state"])

df["region"] = df["state"].map(STATE_TO_REGION)
df["country"] = "India"                                   # helps Tableau place the map
df["period"] = df["year"].astype(str) + " Q" + df["quarter"].astype(str)
df["quarter_start"] = pd.to_datetime(dict(year=df["year"], month=(df["quarter"] - 1) * 3 + 1, day=1))
df["amount_cr"] = df["amount"] / 1e7                      # rupees -> crore

# State tier: top 12 / middle 12 / bottom 12 states by total amount
totals = df.groupby("state")["amount"].sum().sort_values(ascending=False)
tier = {s: ("High" if i < 12 else "Medium" if i < 24 else "Low") for i, s in enumerate(totals.index)}
df["state_tier"] = df["state"].map(tier)

df["half"] = df["quarter"].map(lambda q: "H1 (Q1-Q2)" if q <= 2 else "H2 (Q3-Q4)")
df["phase"] = df["year"].map(lambda y: "Pre-COVID (2018-19)" if y <= 2019
                             else "COVID period (2020-21)" if y <= 2021 else "Post-COVID (2022)")

cols = ["state", "region", "country", "state_tier", "year", "quarter", "half", "period", "phase",
        "quarter_start", "trans_type", "trans_counts", "amount", "amount_cr"]
df[cols].to_csv(OUT, index=False)
print(f"Saved {len(df)} rows to {OUT}")
