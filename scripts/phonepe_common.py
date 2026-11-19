
"""
Shared helpers for the PhonePe Pulse project.
Supports Claude-cleaned CSVs that use 'state' instead of 'states'.
"""
from pathlib import Path

import pandas as pd
from pandas.api import types as pdt

RAW_TABLES = [
    "aggregated_transaction",
    "aggregated_user",
    "map_transaction",
    "map_user",
    "top_transaction",
    "top_user",
]

EXPECTED_SCHEMA = {
    "aggregated_transaction": {
        "states": "str", "year": "int", "quarter": "int",
        "trans_type": "str", "trans_counts": "int", "amount": "float"
    },
    "aggregated_user": {
        "states": "str", "year": "int", "quarter": "int",
        "brand": "str", "user_counts": "int", "percentage": "float"
    },
    "map_transaction": {
        "states": "str", "year": "int", "quarter": "int",
        "district": "str", "trans_counts": "int", "amount": "float"
    },
    "map_user": {
        "states": "str", "year": "int", "quarter": "int",
        "district": "str", "registered_user_counts": "int"
    },
    "top_transaction": {
        "states": "str", "year": "int", "quarter": "int",
        "district": "str", "trans_counts": "int", "amount": "float"
    },
    "top_user": {
        "states": "str", "year": "int", "quarter": "int",
        "district": "str", "registered_user_counts": "int"
    },
}

NATURAL_KEYS = {
    "aggregated_transaction": ["states", "year", "quarter", "trans_type"],
    "aggregated_user": ["states", "year", "quarter", "brand"],
    "map_transaction": ["states", "year", "quarter", "district"],
    "map_user": ["states", "year", "quarter", "district"],
    "top_transaction": ["states", "year", "quarter", "district"],
    "top_user": ["states", "year", "quarter", "district"],
}

DISTRICT_ALIASES = {("delhi", "central delhi"): "central"}

REGIONS = {
    "North": ["Delhi", "Haryana", "Himachal Pradesh", "Jammu and Kashmir",
              "Ladakh", "Punjab", "Chandigarh", "Rajasthan", "Uttarakhand"],
    "Central": ["Uttar Pradesh", "Madhya Pradesh", "Chhattisgarh"],
    "West": ["Gujarat", "Maharashtra", "Goa",
             "Dadra and Nagar Haveli and Daman and Diu"],
    "South": ["Andhra Pradesh", "Telangana", "Karnataka", "Kerala",
              "Tamil Nadu", "Puducherry", "Lakshadweep"],
    "East": ["Bihar", "Jharkhand", "Odisha", "West Bengal",
             "Andaman and Nicobar Islands"],
    "North East": ["Assam", "Arunachal Pradesh", "Manipur", "Meghalaya",
                   "Mizoram", "Nagaland", "Sikkim", "Tripura"],
}
STATE_TO_REGION = {s: r for r, states in REGIONS.items() for s in states}


def clean_state(s: pd.Series) -> pd.Series:
    s = (s.astype(str)
         .str.replace("-&-", "-and-", regex=False)
         .str.replace("-", " ", regex=False)
         .str.title())
    return s.str.replace(r"\bAnd\b", "and", regex=True)


def clean_district(districts: pd.Series, raw_states: pd.Series) -> pd.Series:
    d = districts.astype(str).str.replace(
        r"\s+district$", "", regex=True
    ).str.strip()

    for (state, name), new_name in DISTRICT_ALIASES.items():
        d = d.where(
            ~((raw_states.astype(str).str.lower() == state) &
              (d.str.lower() == name)),
            new_name
        )

    d = d.str.title()
    return d.str.replace(r"\bAnd\b", "and", regex=True)


def dtype_ok(series: pd.Series, kind: str) -> bool:
    if kind == "str":
        return pdt.is_string_dtype(series) or pdt.is_object_dtype(series)
    if kind == "int":
        return pdt.is_integer_dtype(series)
    if kind == "float":
        return pdt.is_float_dtype(series)
    return False


def schema_problems(name: str, df: pd.DataFrame) -> list:
    problems = []
    expected = EXPECTED_SCHEMA[name]

    for col, kind in expected.items():
        if col not in df.columns:
            problems.append(f"{name}: missing column '{col}'")
        elif not dtype_ok(df[col], kind):
            problems.append(
                f"{name}: column '{col}' should be {kind} "
                f"but is {df[col].dtype}"
            )

    extra = [
        c for c in df.columns
        if c not in expected and c != "Unnamed: 0"
    ]
    if extra:
        problems.append(f"{name}: unexpected extra columns {extra}")

    return problems


def load_raw(raw_dir) -> dict:
    """Load Claude-cleaned CSVs and convert their headers to the expected schema."""
    raw_dir = Path(raw_dir)

    missing = [
        t for t in RAW_TABLES
        if not (raw_dir / f"{t}.csv").exists()
    ]

    if missing:
        raise FileNotFoundError(
            f"Missing CSV files in '{raw_dir}': "
            f"{', '.join(m + '.csv' for m in missing)}"
        )

    tables = {}

    for table_name in RAW_TABLES:
        df = pd.read_csv(raw_dir / f"{table_name}.csv")

        # Claude's cleaned files use 'state'; scripts expect 'states'.
        if "states" not in df.columns and "state" in df.columns:
            df = df.rename(columns={"state": "states"})

        # These columns are generated again by standardise().
        df = df.drop(
            columns=["period", "quarter_start", "region", "district_key"],
            errors="ignore"
        )

        tables[table_name] = df

    return tables


def standardise(df: pd.DataFrame) -> pd.DataFrame:
    out = df.drop(columns=["Unnamed: 0"], errors="ignore").copy()
    raw_states = out["states"].astype(str)

    out["state"] = clean_state(out["states"])

    if "district" in out.columns:
        out["district"] = clean_district(out["district"], raw_states)
        out["district_key"] = out["district"] + ", " + out["state"]

    out["region"] = out["state"].map(STATE_TO_REGION)
    out["period"] = (
        out["year"].astype(str) + " Q" + out["quarter"].astype(str)
    )
    out["quarter_start"] = pd.to_datetime(
        dict(
            year=out["year"],
            month=(out["quarter"] - 1) * 3 + 1,
            day=1
        )
    )

    return out.drop(columns=["states"])


def state_tier_map(agg_transaction_std: pd.DataFrame) -> dict:
    totals = (
        agg_transaction_std.groupby("state")["amount"]
        .sum()
        .sort_values(ascending=False)
    )

    return {
        state: (
            "High" if i < 12 else
            "Medium" if i < 24 else
            "Low"
        )
        for i, state in enumerate(totals.index)
    }


def add_calendar_labels(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df["half"] = df["quarter"].map(
        lambda q: "H1 (Q1-Q2)" if q <= 2 else "H2 (Q3-Q4)"
    )

    df["phase"] = df["year"].map(
        lambda y: "Pre-COVID (2018-19)" if y <= 2019
        else "COVID period (2020-21)" if y <= 2021
        else "Post-COVID (2022)"
    )

    return df
