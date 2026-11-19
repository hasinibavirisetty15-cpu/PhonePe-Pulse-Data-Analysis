r"""
Compute KPIs, YoY growth, CAGR, top lists and the recommendation table from the merged tables.

Run from the project root (Windows), AFTER build_master_table.py:
    python scripts\compute_kpis.py

Reads : data\master_long.csv, data\master_district_quarter.csv
Writes: outputs\*.csv and outputs\kpi_summary.md   (every number in the report comes from these files)

Definitions
-----------
Transaction value ("revenue" in the brief)  = total rupee amount of payments made through PhonePe (NOT PhonePe's own revenue).
Registered users                            = running total at the END of a quarter (never added across quarters).
Year-end users                              = registered users in Q4.
Engagement (transactions per user)          = payments in the year / registered users at the end of that year.
YoY growth %                                = (value this year / value last year - 1) * 100
CAGR %                                      = ((last / first) ** (1 / years) - 1) * 100
"""
import argparse
from pathlib import Path

import pandas as pd

CR = 1e7  # 1 crore = 10,000,000 rupees


def cagr(first, last, years):
    return ((last / first) ** (1 / years) - 1) * 100 if first and years else float("nan")


def md_table(df, index=False):
    """Small markdown-table helper (so we do not need the optional 'tabulate' package)."""
    if index:
        df = df.reset_index()
    head = "| " + " | ".join(str(c) for c in df.columns) + " |"
    sep = "|" + "|".join("---" for _ in df.columns) + "|"
    rows = ["| " + " | ".join(f"{v:,.2f}" if isinstance(v, float) else str(v) for v in r) + " |"
            for r in df.itertuples(index=False)]
    return "\n".join([head, sep] + rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="data")
    ap.add_argument("--out", default="outputs")
    args = ap.parse_args()
    data, out = Path(args.data), Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    long = pd.read_csv(data / "master_long.csv", low_memory=False)
    dq = pd.read_csv(data / "master_district_quarter.csv", low_memory=False)
    agg = long[long["source_table"] == "aggregated_transaction"]
    users = long[long["source_table"] == "map_user"]

    years = sorted(agg["year"].unique())
    first_y, last_y = years[0], years[-1]
    n_years = last_y - first_y

    # ---------- yearly table: value, volume, ticket size, users, engagement, YoY
    y = agg.groupby("year").agg(trans_counts=("trans_counts", "sum"), amount=("amount", "sum")).reset_index()
    y["amount_cr"] = y["amount"] / CR
    y["avg_txn_value_rs"] = y["amount"] / y["trans_counts"]
    ye = users[users["quarter"] == 4].groupby("year")["registered_users"].sum().rename("registered_users_year_end")
    y = y.merge(ye, on="year")
    y["txn_per_user"] = y["trans_counts"] / y["registered_users_year_end"]
    y["amount_per_user_rs"] = y["amount"] / y["registered_users_year_end"]
    for col, name in [("amount", "yoy_amount_pct"), ("trans_counts", "yoy_transactions_pct"),
                      ("registered_users_year_end", "yoy_users_pct")]:
        y[name] = y[col].pct_change() * 100
    y.drop(columns=["amount"]).round(2).to_csv(out / "yearly_growth.csv", index=False)

    # ---------- headline KPIs
    first, last = y.iloc[0], y.iloc[-1]
    latest_users = users[(users["year"] == last_y) & (users["quarter"] == 4)]["registered_users"].sum()
    kpi = {
        "total_transaction_value_cr": agg["amount"].sum() / CR,
        "total_transactions": agg["trans_counts"].sum(),
        "average_transaction_value_rs": agg["amount"].sum() / agg["trans_counts"].sum(),
        f"registered_users_{last_y}_q4": latest_users,
        f"transactions_per_user_{last_y}": last["txn_per_user"],
        f"transaction_value_per_user_{last_y}_rs": last["amount_per_user_rs"],
        f"cagr_value_{first_y}_{last_y}_pct": cagr(first["amount"], last["amount"], n_years),
        f"cagr_transactions_{first_y}_{last_y}_pct": cagr(first["trans_counts"], last["trans_counts"], n_years),
        f"cagr_users_{first_y}_{last_y}_pct": cagr(first["registered_users_year_end"],
                                                    last["registered_users_year_end"], n_years),
        f"yoy_value_{last_y}_pct": last["yoy_amount_pct"],
        f"yoy_transactions_{last_y}_pct": last["yoy_transactions_pct"],
        f"yoy_users_{last_y}_pct": last["yoy_users_pct"],
    }
    pd.DataFrame({"kpi": list(kpi), "value": list(kpi.values())}).round(2).to_csv(out / "kpi_summary.csv", index=False)
    pd.DataFrame([kpi]).round(2).to_csv(out / "kpi_cards_wide.csv", index=False)  # one row, easy to use in Tableau

    # ---------- state level: value, share, growth, users, engagement
    s_year = agg.pivot_table(index="state", columns="year", values="amount", aggfunc="sum")
    s_cnt = agg.pivot_table(index="state", columns="year", values="trans_counts", aggfunc="sum")
    s_users = users[(users["quarter"] == 4)].pivot_table(index="state", columns="year",
                                                         values="registered_users", aggfunc="sum")
    base_y = years[1]  # 2019: 2018 bases are tiny for many small states, so state CAGR starts one year later
    st = pd.DataFrame({
        "region": agg.groupby("state")["region"].first(),
        "total_value_cr": s_year.sum(axis=1) / CR,
        f"value_{base_y}_cr": s_year[base_y] / CR,
        f"value_{last_y}_cr": s_year[last_y] / CR,
        f"cagr_value_{base_y}_{last_y}_pct": ((s_year[last_y] / s_year[base_y]) ** (1 / (last_y - base_y)) - 1) * 100,
        f"yoy_value_{last_y}_pct": (s_year[last_y] / s_year[last_y - 1] - 1) * 100,
        f"registered_users_{last_y}": s_users[last_y],
        f"transactions_{last_y}": s_cnt[last_y],
        f"txn_per_user_{last_y}": s_cnt[last_y] / s_users[last_y],
        f"avg_txn_value_{last_y}_rs": s_year[last_y] / s_cnt[last_y],
    })
    st["share_of_total_value_pct"] = 100 * st["total_value_cr"] / st["total_value_cr"].sum()
    st = st.sort_values("total_value_cr", ascending=False)
    st.round(2).to_csv(out / "state_growth_and_engagement.csv")
    st.head(10)[["region", "total_value_cr", "share_of_total_value_pct"]].round(2).to_csv(out / "top10_states_by_value.csv")
    (st.sort_values(f"registered_users_{last_y}", ascending=False).head(10)
       [["region", f"registered_users_{last_y}", f"txn_per_user_{last_y}"]].round(2)
       .to_csv(out / "top10_states_by_users.csv"))

    # ---------- districts: top transactions and top users
    d_val = dq.groupby("district_key").agg(total_value_cr=("amount_cr", "sum"), total_transactions=("trans_counts", "sum"))
    d_val.sort_values("total_value_cr", ascending=False).head(10).round(2).to_csv(out / "top10_districts_by_value.csv")
    last_period = dq[(dq["year"] == last_y) & (dq["quarter"] == 4)]
    (last_period.groupby("district_key")["registered_users"].sum().sort_values(ascending=False).head(10)
        .to_csv(out / "top10_districts_by_users.csv"))

    # ---------- payment type mix
    t = agg.groupby("trans_type").agg(trans_counts=("trans_counts", "sum"), amount=("amount", "sum"))
    t["share_of_transactions_pct"] = 100 * t["trans_counts"] / t["trans_counts"].sum()
    t["share_of_value_pct"] = 100 * t["amount"] / t["amount"].sum()
    t["avg_txn_value_rs"] = t["amount"] / t["trans_counts"]
    t.drop(columns="amount").sort_values("share_of_value_pct", ascending=False).round(2).to_csv(out / "payment_type_mix.csv")

    # ---------- seasonality
    q = agg.groupby("quarter")["trans_counts"].sum()
    pd.DataFrame({"quarter": q.index, "share_of_transactions_pct": (100 * q / q.sum()).round(2).values}).to_csv(
        out / "seasonality.csv", index=False)

    # ---------- recommendation scenario: lift engagement in big-user, low-engagement states
    col_u, col_e, col_a = f"registered_users_{last_y}", f"txn_per_user_{last_y}", f"avg_txn_value_{last_y}_rs"
    median_e = st[col_e].median()
    big = st.sort_values(col_u, ascending=False).head(15)
    target = big[big[col_e] < median_e].copy()
    target["gap_to_median_txn_per_user"] = median_e - target[col_e]
    target["extra_transactions_if_median"] = target["gap_to_median_txn_per_user"] * target[col_u]
    target["extra_value_cr_if_median"] = target["extra_transactions_if_median"] * target[col_a] / CR
    target = target.sort_values("extra_value_cr_if_median", ascending=False)
    target[["region", col_u, col_e, "gap_to_median_txn_per_user", "extra_transactions_if_median",
            "extra_value_cr_if_median"]].round(2).to_csv(out / "recommendation_engagement_gap.csv")

    # ---------- readable summary
    md = ["# KPI summary (generated by scripts/compute_kpis.py)", "", "## Headline KPIs", "",
          "| KPI | Value |", "|---|---:|"]
    md += [f"| {k} | {v:,.2f} |" for k, v in kpi.items()]
    md += ["", "## Yearly growth", "", md_table(y.drop(columns="amount").round(2))]
    md += ["", f"Median {last_y} transactions per user across states: {median_e:.1f}",
           "", "## Engagement gap (recommendation scenario)", "",
           md_table(target[["region", col_u, col_e, "extra_transactions_if_median", "extra_value_cr_if_median"]].round(1), index=True)]
    (out / "kpi_summary.md").write_text("\n".join(md), encoding="utf-8")
    print("Saved KPI files to", out)
    print(pd.DataFrame({"kpi": list(kpi), "value": [round(v, 2) for v in kpi.values()]}).to_string(index=False))


if __name__ == "__main__":
    main()
