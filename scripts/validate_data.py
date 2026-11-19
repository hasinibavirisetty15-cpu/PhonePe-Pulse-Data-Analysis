r"""
Data validation for the PhonePe Pulse project.

Run from the project root (Windows):
    python scripts\validate_data.py

Reads : data\raw\*.csv                 (six original files)
        data\master_long.csv           (optional - checked if it exists)
        data\master_district_quarter.csv (optional - checked if it exists)
Writes: reports\validation_report.md
        reports\validation_results.csv

HOW "VALIDATION PASS RATE" IS DEFINED (read this before quoting a number)
-------------------------------------------------------------------------
There is no outside ground truth for this dataset, so we cannot measure "accuracy" against reality.
Instead every check tests ONE rule on a number of "units" (rows, state-quarters or tables).
  pass rate of a check      = units that pass / units tested
  overall pass rate         = all passing units / all tested units   (weighted by units)
  checks fully passed       = number of checks with a 100% pass rate / number of checks
A check that is not 100% is marked FAIL (critical rule) or WARN (known data limitation, explained in the note).
The project target of 80% is compared with the overall pass rate AND the share of fully passed checks.
"""
import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
import phonepe_common as pc  # noqa: E402

YEARS = range(2018, 2023)
RESULTS = []


def add(group, name, passed, total, severity="critical", note=""):
    passed, total = int(passed), int(total)
    status = "PASS" if passed == total else ("WARN" if severity == "info" else "FAIL")
    RESULTS.append(dict(group=group, check=name, units_tested=total, units_passed=passed,
                        pass_rate=round(100 * passed / total, 2) if total else 100.0,
                        status=status, note=note))


def raw_checks(raw, std):
    # --- structure
    ok = sum(1 for n, d in raw.items() if not [p for p in pc.schema_problems(n, d) if "dtype" not in p
                                               and "should be" not in p])
    add("Schema", "Expected columns present in every table", ok, len(raw))
    ok = sum(1 for n, d in raw.items() if not pc.schema_problems(n, d))
    add("Schema", "Expected data types in every table", ok, len(raw))

    # --- row-level quality
    tested = passed = 0
    for n, d in raw.items():
        tested += len(d)
        passed += int((~d.isna().any(axis=1)).sum())
    add("Row quality", "No missing values", passed, tested)

    tested = passed = 0
    for n, d in raw.items():
        tested += len(d)
        passed += int((~d.duplicated(pc.NATURAL_KEYS[n])).sum())
    add("Row quality", "No duplicate rows on the natural key", passed, tested)

    tested = passed = 0
    for n, d in raw.items():
        valid = d["year"].isin(list(YEARS)) & d["quarter"].between(1, 4)
        for col in ["trans_counts", "amount", "registered_user_counts", "user_counts"]:
            if col in d.columns:
                valid &= d[col] > 0
        tested += len(d)
        passed += int(valid.sum())
    add("Row quality", "Valid ranges (year 2018-2022, quarter 1-4, counts and amounts > 0)", passed, tested)

    # --- consistency across tables
    base = set(std["aggregated_transaction"]["state"])
    add("Coverage", "Same 36 states in every table", sum(set(d["state"]) == base for d in std.values()), len(std))
    full = sum(d.groupby(["year", "quarter"]).ngroups == 20 for d in raw.values())
    cov = raw["aggregated_user"].groupby(["year", "quarter"]).ngroups
    add("Coverage", "All 20 quarters (2018 Q1 - 2022 Q4) present", full, len(raw), "info",
        f"aggregated_user covers only {cov} of 20 quarters (ends 2022 Q1) - brand charts stop there")

    # --- reconciliation between tables
    a = std["aggregated_transaction"].groupby(["state", "year", "quarter"])[["trans_counts", "amount"]].sum()
    m = std["map_transaction"].groupby(["state", "year", "quarter"])[["trans_counts", "amount"]].sum()
    j = a.join(m, rsuffix="_map", how="outer")
    good = (j["trans_counts"] == j["trans_counts_map"]) & np.isclose(j["amount"], j["amount_map"], rtol=1e-6)
    add("Reconciliation", "aggregated_transaction = sum of map_transaction (counts and amount, per state-quarter)",
        good.sum(), len(j))

    ua = std["aggregated_user"].groupby(["state", "year", "quarter"])["user_counts"].sum()
    um = std["map_user"].groupby(["state", "year", "quarter"])["registered_user_counts"].sum()
    k = pd.concat([ua, um], axis=1, keys=["agg", "map"]).dropna()
    add("Reconciliation", "aggregated_user total = sum of map_user (per state-quarter, overlapping quarters)",
        (k["agg"] == k["map"]).sum(), len(k))

    ps = std["aggregated_user"].groupby(["state", "year", "quarter"])["percentage"].sum()
    add("Reconciliation", "Brand shares add up to 100% (per state-quarter)", np.isclose(ps, 1.0, atol=1e-6).sum(), len(ps))

    keys = ["state", "year", "quarter", "district"]
    t = std["top_transaction"].merge(std["map_transaction"][keys + ["trans_counts", "amount"]], on=keys,
                                     how="left", suffixes=("", "_map"))
    good = (t["trans_counts"] == t["trans_counts_map"]) & np.isclose(t["amount"], t["amount_map"], rtol=1e-6)
    add("Reconciliation", "top_transaction rows match map_transaction (same counts and amount)", good.sum(), len(t),
        note="Delhi's 'central delhi' (top tables) and 'central district' (map tables) are unified by an alias")
    t = std["top_user"].merge(std["map_user"][keys + ["registered_user_counts"]], on=keys, how="left",
                              suffixes=("", "_map"))
    add("Reconciliation", "top_user rows match map_user (same registered users)",
        (t["registered_user_counts"] == t["registered_user_counts_map"]).sum(), len(t))

    mm = std["map_user"].merge(std["map_transaction"][keys], on=keys, how="left", indicator=True)
    add("Reconciliation", "Every map_user row also exists in map_transaction", (mm["_merge"] == "both").sum(), len(mm),
        "info", "4 Arunachal Pradesh rows (Anjaw 2018 Q1; Shi Yomi 2018 Q1-Q3) have users but no transactions")

    # --- logic
    s = std["map_user"].groupby(["state", "year", "quarter"])["registered_user_counts"].sum().unstack(0).sort_index()
    d = s.diff().dropna()
    add("Logic", "Registered users never fall from one quarter to the next (running total)", (d >= 0).sum().sum(), d.size)

    sizes = std["top_transaction"].groupby(["state", "year", "quarter"]).size()
    add("Logic", "Top lists hold at most 10 rows per state-quarter", (sizes <= 10).sum(), len(sizes))


def merged_checks(raw, std, master_dir):
    long_path, dq_path = master_dir / "master_long.csv", master_dir / "master_district_quarter.csv"
    if not (long_path.exists() and dq_path.exists()):
        print("Merged tables not found - skipping merged-table checks (run build_master_table.py first).")
        return False
    long = pd.read_csv(long_path, low_memory=False)
    dq = pd.read_csv(dq_path, low_memory=False)

    add("Merged table", "master_long has one row for every source row", int(len(long) == sum(len(d) for d in raw.values())), 1)
    needed = ["source_table", "state", "region", "year", "quarter", "period", "amount", "trans_counts"]
    add("Merged table", "master_long has the required columns", int(all(c in long.columns for c in needed)), 1)
    add("Merged table", "No missing key fields in master_long (source_table, state, region, year, quarter)",
        int((~long[["source_table", "state", "region", "year", "quarter"]].isna().any(axis=1)).sum()), len(long))
    ok = 0
    for src in ["aggregated_transaction", "map_transaction", "top_transaction"]:
        part = long[long["source_table"] == src]
        ok += int(part["trans_counts"].sum() == raw[src]["trans_counts"].sum())
        ok += int(np.isclose(part["amount"].sum(), raw[src]["amount"].sum(), rtol=1e-9))
    add("Merged table", "Counts and amounts in master_long equal the original files (3 tables x 2 measures)", ok, 6)
    add("Merged table", "master_district_quarter has no duplicate district-quarter rows",
        int((~dq.duplicated(["state", "district", "year", "quarter"])).sum()), len(dq))
    ok = int(dq["trans_counts"].sum() == raw["map_transaction"]["trans_counts"].sum())
    ok += int(np.isclose(dq["amount"].sum(), raw["map_transaction"]["amount"].sum(), rtol=1e-9))
    ok += int(dq["registered_users"].sum() == raw["map_user"]["registered_user_counts"].sum())
    add("Merged table", "master_district_quarter totals equal the original files (counts, amount, users)", ok, 3)
    add("Merged table", "All top_transaction and top_user rows were matched into master_district_quarter",
        int(dq["in_top_transaction"].sum() == len(raw["top_transaction"])) + int(dq["in_top_user"].sum() == len(raw["top_user"])), 2)
    return True


def write_reports(out_dir, merged_checked):
    out_dir.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(RESULTS)
    df.to_csv(out_dir / "validation_results.csv", index=False)
    tested, passed = df["units_tested"].sum(), df["units_passed"].sum()
    overall = 100 * passed / tested
    full = int((df["status"] == "PASS").sum())
    share_checks = 100 * full / len(df)
    lines = [
        "# Data validation report", "",
        "Method: each check tests one rule on a number of units (rows, state-quarters or tables). "
        "There is no external ground truth, so this measures internal consistency, not accuracy against the real world.", "",
        f"- Checks run: **{len(df)}** (merged-table checks included: {'yes' if merged_checked else 'no'})",
        f"- Checks fully passed: **{full} of {len(df)} ({share_checks:.1f}%)**",
        f"- Overall unit pass rate: **{overall:.3f}%** ({passed:,} of {tested:,} units)",
        f"- Target of 80%: **{'MET' if overall >= 80 and share_checks >= 80 else 'NOT MET'}** "
        "(both measures must be at least 80%)", "",
        "| Group | Check | Tested | Passed | Pass rate | Status | Note |", "|---|---|---:|---:|---:|---|---|",
    ]
    for r in RESULTS:
        lines.append(f"| {r['group']} | {r['check']} | {r['units_tested']:,} | {r['units_passed']:,} | "
                     f"{r['pass_rate']:.2f}% | {r['status']} | {r['note']} |")
    lines += ["", "WARN = known data limitation, explained in the note. FAIL = a rule that must hold but does not."]
    (out_dir / "validation_report.md").write_text("\n".join(lines), encoding="utf-8")
    return df, overall, share_checks


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", default="data/raw")
    ap.add_argument("--master", default="data")
    ap.add_argument("--out", default="reports")
    args = ap.parse_args()

    raw = pc.load_raw(args.raw)
    std = {n: pc.standardise(d) for n, d in raw.items()}
    raw_checks(raw, std)
    merged_checked = merged_checks(raw, std, Path(args.master))
    df, overall, share_checks = write_reports(Path(args.out), merged_checked)

    print(df[["check", "units_tested", "units_passed", "pass_rate", "status"]].to_string(index=False))
    print(f"\nChecks fully passed: {int((df['status'] == 'PASS').sum())} of {len(df)}")
    print(f"Overall unit pass rate: {overall:.3f}%")
    print("Report saved to reports\\validation_report.md")
    if (df["status"] == "FAIL").any():
        sys.exit(2)


if __name__ == "__main__":
    main()
