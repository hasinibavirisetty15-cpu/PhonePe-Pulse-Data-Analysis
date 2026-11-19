r"""
Merge the six original PhonePe csv files into ONE analysis table, with schema validation.

Run from the project root (Windows):
    python scripts\build_master_table.py

Reads : data\raw\*.csv                      (the six original files)
Writes: data\master_long.csv                (single merged table: all six sources stacked, with a source_table column)
        data\master_district_quarter.csv    (district x quarter table: transactions + users + top-list flags)

Nothing is overwritten except these two output files.
"""
import argparse
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
import phonepe_common as pc  # noqa: E402

LONG_COLUMNS = [
    "source_table", "state", "region", "state_tier", "year", "quarter", "half", "period", "phase",
    "quarter_start", "district", "district_key", "trans_type", "brand",
    "trans_counts", "amount", "amount_cr", "registered_users", "user_counts", "brand_share", "top_rank",
]
INT_COLUMNS = ["year", "quarter", "trans_counts", "registered_users", "user_counts", "top_rank"]


def add_rank(df, value_col):
    """Rank inside each state-quarter (1 = biggest). The top_* tables hold the top 10 per state-quarter."""
    return (df.groupby(["state", "year", "quarter"])[value_col]
              .rank(method="first", ascending=False).astype(int))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", default="data/raw", help="folder with the six original csv files")
    ap.add_argument("--out", default="data", help="folder for the merged tables")
    args = ap.parse_args()

    raw = pc.load_raw(args.raw)

    # ---- 1. schema validation (stop with a clear message if a file is not what we expect)
    problems = [p for name, df in raw.items() for p in pc.schema_problems(name, df)]
    if problems:
        print("SCHEMA VALIDATION FAILED:")
        for p in problems:
            print("  -", p)
        sys.exit(1)
    print("Schema validation passed for all 6 tables.")

    std = {name: pc.standardise(df) for name, df in raw.items()}
    tiers = pc.state_tier_map(std["aggregated_transaction"])

    # ---- 2. single long table: all six sources stacked (columns that don't apply stay empty)
    parts = []
    for name, df in std.items():
        d = df.copy()
        d["source_table"] = name
        if "amount" in d.columns:
            d["amount_cr"] = d["amount"] / 1e7
        if "registered_user_counts" in d.columns:
            d = d.rename(columns={"registered_user_counts": "registered_users"})
        if name == "aggregated_user":
            d = d.rename(columns={"percentage": "brand_share"})
        if name == "top_transaction":
            d["top_rank"] = add_rank(d, "amount")
        if name == "top_user":
            d["top_rank"] = add_rank(d, "registered_users")
        d["state_tier"] = d["state"].map(tiers)
        parts.append(d)
    long = pd.concat(parts, ignore_index=True)
    long = pc.add_calendar_labels(long)
    for col in LONG_COLUMNS:
        if col not in long.columns:
            long[col] = pd.NA
    long = long[LONG_COLUMNS]
    for col in INT_COLUMNS:
        long[col] = long[col].astype("Int64")

    # ---- 3. district x quarter table (the most detailed grain that has both transactions and users)
    keys = ["state", "district", "year", "quarter"]
    mt = std["map_transaction"][keys + ["trans_counts", "amount"]]
    mu = std["map_user"][keys + ["registered_user_counts"]].rename(
        columns={"registered_user_counts": "registered_users"})
    dq = mt.merge(mu, on=keys, how="outer", indicator=True)
    dq["only_in_map_user"] = dq["_merge"] == "right_only"
    dq = dq.drop(columns="_merge")
    dq[["trans_counts", "amount"]] = dq[["trans_counts", "amount"]].fillna(0)

    for src, flag, rank_col in [("top_transaction", "in_top_transaction", "top_transaction_rank"),
                                ("top_user", "in_top_user", "top_user_rank")]:
        t = std[src].copy()
        value = "amount" if src == "top_transaction" else "registered_user_counts"
        t[rank_col] = add_rank(t, value)
        dq = dq.merge(t[keys + [rank_col]], on=keys, how="left")
        dq[flag] = dq[rank_col].notna()
        dq[rank_col] = dq[rank_col].astype("Int64")
        n_top = int(dq[flag].sum())
        print(f"{src}: {len(t)} rows, {n_top} matched to the district table"
              + ("  <-- MISMATCH" if n_top != len(t) else ""))

    dq["state_tier"] = dq["state"].map(tiers)
    dq["region"] = dq["state"].map(pc.STATE_TO_REGION)
    dq["district_key"] = dq["district"] + ", " + dq["state"]
    dq["period"] = dq["year"].astype(str) + " Q" + dq["quarter"].astype(str)
    dq["quarter_start"] = pd.to_datetime(dict(year=dq["year"], month=(dq["quarter"] - 1) * 3 + 1, day=1))
    dq["amount_cr"] = dq["amount"] / 1e7
    dq = pc.add_calendar_labels(dq)

    # helper columns so Tableau/Streamlit never add up a running total of users across quarters
    last_year, last_quarter = dq.sort_values(["year", "quarter"]).iloc[-1][["year", "quarter"]]
    dq["users_year_end"] = dq["registered_users"].where(dq["quarter"] == 4, 0)
    dq["users_latest"] = dq["registered_users"].where(
        (dq["year"] == last_year) & (dq["quarter"] == last_quarter), 0)

    dq_cols = ["state", "region", "state_tier", "district", "district_key", "year", "quarter", "half",
               "period", "phase", "quarter_start", "trans_counts", "amount", "amount_cr",
               "registered_users", "users_year_end", "users_latest", "in_top_transaction",
               "top_transaction_rank", "in_top_user", "top_user_rank", "only_in_map_user"]
    dq = dq[dq_cols].sort_values(["state", "district", "year", "quarter"]).reset_index(drop=True)

    # ---- 4. save
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    long.to_csv(out / "master_long.csv", index=False)
    dq.to_csv(out / "master_district_quarter.csv", index=False)

    expected_rows = sum(len(df) for df in raw.values())
    print(f"master_long.csv: {len(long):,} rows (sum of the six source tables = {expected_rows:,})")
    print(f"master_district_quarter.csv: {len(dq):,} rows")
    print("Done. Next: python scripts\\validate_data.py")


if __name__ == "__main__":
    main()
