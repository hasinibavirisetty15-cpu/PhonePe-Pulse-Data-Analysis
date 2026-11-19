"""
Data layer for the Streamlit dashboard. Pure pandas (no Streamlit / Plotly) so it can be tested on its own.
Reads the tables created by scripts/build_master_table.py.
"""
from pathlib import Path

import pandas as pd

CR = 1e7
ALL = "All"

METRICS = {
    "Transaction value (Cr)": "amount_cr",
    "Transactions": "trans_counts",
    "Average transaction value (Rs)": "avg_value",
}


def load_data(data_dir="data"):
    data_dir = Path(data_dir)
    long = pd.read_csv(data_dir / "master_long.csv", low_memory=False)
    dq = pd.read_csv(data_dir / "master_district_quarter.csv", low_memory=False)
    return long, dq


def options(df, col):
    """Sorted unique values of a column, with 'All' first."""
    vals = sorted(df[col].dropna().unique().tolist())
    return [ALL] + vals


def apply_filters(df, selections):
    """selections = {column: value}; 'All' / None means no filter. Columns missing from df are ignored."""
    out = df
    for col, val in selections.items():
        if col in out.columns and val not in (ALL, None):
            out = out[out[col] == val]
    return out


def source(long, name):
    return long[long["source_table"] == name]


def user_snapshot(users_df):
    """Registered users are a RUNNING TOTAL: take the latest quarter inside the selection, never add quarters."""
    if users_df.empty:
        return 0
    last = users_df.sort_values(["year", "quarter"]).iloc[-1][["year", "quarter"]]
    snap = users_df[(users_df["year"] == last["year"]) & (users_df["quarter"] == last["quarter"])]
    return int(snap["registered_users"].sum())


def headline_kpis(agg_f, users_f):
    value_cr = agg_f["amount_cr"].sum()
    txns = agg_f["trans_counts"].sum()
    users = user_snapshot(users_f)
    return {
        "value_cr": value_cr,
        "transactions": txns,
        "avg_value": (value_cr * CR / txns) if txns else 0,
        "users": users,
        "txn_per_user": (txns / users) if users else 0,
    }


def state_metric_table(agg_f, metric_col):
    g = agg_f.groupby("state").agg(amount_cr=("amount_cr", "sum"), trans_counts=("trans_counts", "sum")).reset_index()
    g["avg_value"] = g["amount_cr"] * CR / g["trans_counts"]
    g["metric"] = g[metric_col]
    return g


def yearly_growth(agg_f, users_f):
    """Yearly value, transactions, year-end users, engagement and YoY %. Needs several years in the data."""
    y = agg_f.groupby("year").agg(amount_cr=("amount_cr", "sum"), trans_counts=("trans_counts", "sum")).reset_index()
    ye = (users_f[users_f["quarter"] == 4].groupby("year")["registered_users"].sum()
          .rename("users_year_end").reset_index())
    y = y.merge(ye, on="year", how="left")
    y["txn_per_user"] = y["trans_counts"] / y["users_year_end"]
    y["yoy_value_pct"] = y["amount_cr"].pct_change() * 100
    y["yoy_transactions_pct"] = y["trans_counts"].pct_change() * 100
    y["yoy_users_pct"] = y["users_year_end"].pct_change() * 100
    return y


def cagr_pct(first, last, years):
    if not first or years <= 0 or pd.isna(first) or pd.isna(last):
        return float("nan")
    return ((last / first) ** (1 / years) - 1) * 100


def growth_summary(yearly):
    if len(yearly) < 2:
        return {}
    a, b = yearly.iloc[0], yearly.iloc[-1]
    n = int(b["year"] - a["year"])
    return {
        "from_year": int(a["year"]), "to_year": int(b["year"]),
        "cagr_value": cagr_pct(a["amount_cr"], b["amount_cr"], n),
        "cagr_transactions": cagr_pct(a["trans_counts"], b["trans_counts"], n),
        "cagr_users": cagr_pct(a["users_year_end"], b["users_year_end"], n),
    }


def top_n(df, label_col, value_col, n):
    return df.groupby(label_col)[value_col].sum().sort_values(ascending=False).head(n).reset_index()


def top_districts_by_users(dq_f, n):
    """Latest quarter inside the selection only (running total)."""
    if dq_f.empty:
        return pd.DataFrame(columns=["district_key", "registered_users"])
    last = dq_f.sort_values(["year", "quarter"]).iloc[-1][["year", "quarter"]]
    snap = dq_f[(dq_f["year"] == last["year"]) & (dq_f["quarter"] == last["quarter"])]
    return snap.groupby("district_key")["registered_users"].sum().sort_values(ascending=False).head(n).reset_index()
