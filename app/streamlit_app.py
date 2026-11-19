r"""
PhonePe Pulse - Streamlit dashboard (minimal, 12 dropdown filters).

Run from the project root (Windows):
    pip install -r requirements.txt
    streamlit run app\streamlit_app.py

Needs data\master_long.csv and data\master_district_quarter.csv (create them with scripts\build_master_table.py).
"""
import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

sys.path.insert(0, str(Path(__file__).parent))
import data_access as da  # noqa: E402
from geo import STATE_COORDS  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
BLUE = "#1f4e8c"

st.set_page_config(page_title="PhonePe Pulse Dashboard", layout="wide")


@st.cache_data
def get_data():
    return da.load_data(ROOT / "data")


if not (ROOT / "data" / "master_long.csv").exists():
    st.error("data/master_long.csv not found. Run:  python scripts\\build_master_table.py")
    st.stop()

long, dq = get_data()
agg = da.source(long, "aggregated_transaction")
users = da.source(long, "map_user")
brands = da.source(long, "aggregated_user")

# ------------------------------------------------------------------ sidebar: 12 dropdown filters
st.sidebar.header("Filters")
sel = {
    "year": st.sidebar.selectbox("1. Year", da.options(agg, "year")),
    "quarter": st.sidebar.selectbox("2. Quarter", da.options(agg, "quarter")),
    "half": st.sidebar.selectbox("3. Half-year", da.options(agg, "half")),
    "phase": st.sidebar.selectbox("4. Phase", da.options(agg, "phase")),
    "region": st.sidebar.selectbox("5. Region", da.options(agg, "region")),
    "state_tier": st.sidebar.selectbox("6. State tier", da.options(agg, "state_tier")),
    "state": st.sidebar.selectbox("7. State", da.options(agg, "state")),
}
trans_type = st.sidebar.selectbox("8. Transaction type", da.options(agg, "trans_type"))
brand_sel = st.sidebar.selectbox("9. Device brand", da.options(brands, "brand"))
metric_label = st.sidebar.selectbox("10. Metric", list(da.METRICS))
top_n = st.sidebar.selectbox("11. Top N", [5, 10, 15, 20], index=1)
district_options = da.options(da.apply_filters(dq, {k: v for k, v in sel.items()}), "district_key")
district_sel = st.sidebar.selectbox("12. District", district_options)
metric_col = da.METRICS[metric_label]

# ------------------------------------------------------------------ filtered frames
agg_f = da.apply_filters(agg, {**sel, "trans_type": trans_type})
users_f = da.apply_filters(users, sel)
dq_f = da.apply_filters(dq, sel)
if district_sel != da.ALL:
    dq_f = dq_f[dq_f["district_key"] == district_sel]

# growth views ignore the time filters (they need several years) but respect the other filters
non_time = {k: v for k, v in sel.items() if k in ("region", "state_tier", "state")}
agg_g = da.apply_filters(agg, {**non_time, "trans_type": trans_type})
users_g = da.apply_filters(users, non_time)

st.title("PhonePe Pulse Data Dashboard")
st.caption("Digital payments in India, 2018 Q1 - 2022 Q4. Source: PhonePe Pulse data provided with the project brief.")

if agg_f.empty:
    st.warning("No data for this combination of filters. Change a filter.")
    st.stop()

tab_overview, tab_growth, tab_users, tab_districts, tab_quality = st.tabs(
    ["Overview", "Growth (YoY and CAGR)", "Users and engagement", "Top districts", "Data quality"])

# ------------------------------------------------------------------ Overview
with tab_overview:
    k = da.headline_kpis(agg_f, users_f)
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Transaction value", f"{k['value_cr']:,.0f} Cr")
    c2.metric("Transactions", f"{k['transactions'] / 1e9:,.2f} B")
    c3.metric("Avg transaction value", f"Rs {k['avg_value']:,.0f}")
    c4.metric("Registered users", f"{k['users'] / 1e6:,.1f} M")
    c5.metric("Transactions per user", f"{k['txn_per_user']:,.1f}")
    st.caption("Registered users = latest quarter in the selection (a running total, never added across quarters).")

    tbl = da.state_metric_table(agg_f, metric_col)
    tbl["lat"] = tbl["state"].map(lambda s: STATE_COORDS[s][0])
    tbl["lon"] = tbl["state"].map(lambda s: STATE_COORDS[s][1])
    left, right = st.columns([3, 2])
    with left:
        fig = px.scatter_geo(tbl, lat="lat", lon="lon", size="metric", color="metric", hover_name="state",
                             size_max=40, color_continuous_scale="Blues", title=f"{metric_label} by state")
        fig.update_geos(scope="asia", lataxis_range=[5, 38], lonaxis_range=[66, 99], showcountries=True,
                        countrycolor="#999999", showland=True, landcolor="#f3f4f6")
        fig.update_layout(margin=dict(l=0, r=0, t=40, b=0), coloraxis_colorbar_title="")
        st.plotly_chart(fig)
        st.caption("Bubbles are placed at approximate state centre points.")
    with right:
        top = tbl.sort_values("metric", ascending=False).head(top_n)
        fig = px.bar(top.sort_values("metric"), x="metric", y="state", orientation="h",
                     title=f"Top {top_n} states", color_discrete_sequence=[BLUE])
        fig.update_layout(margin=dict(l=0, r=0, t=40, b=0), xaxis_title=metric_label, yaxis_title="")
        st.plotly_chart(fig)

    l2, r2 = st.columns(2)
    trend = (agg_f.groupby(["period", "quarter_start"]).agg(amount_cr=("amount_cr", "sum"),
             trans_counts=("trans_counts", "sum")).reset_index().sort_values("quarter_start"))
    trend["avg_value"] = trend["amount_cr"] * da.CR / trend["trans_counts"]
    with l2:
        fig = px.line(trend, x="quarter_start", y=metric_col, title=f"Quarterly trend: {metric_label}",
                      color_discrete_sequence=[BLUE])
        fig.update_layout(margin=dict(l=0, r=0, t=40, b=0), xaxis_title="", yaxis_title="")
        st.plotly_chart(fig)
    with r2:
        mix = agg_f.groupby("trans_type").agg(amount_cr=("amount_cr", "sum"), trans_counts=("trans_counts", "sum")).reset_index()
        mix["avg_value"] = mix["amount_cr"] * da.CR / mix["trans_counts"]
        fig = px.bar(mix.sort_values(metric_col), x=metric_col, y="trans_type", orientation="h",
                     title=f"Payment types: {metric_label}", color_discrete_sequence=[BLUE])
        fig.update_layout(margin=dict(l=0, r=0, t=40, b=0), xaxis_title="", yaxis_title="")
        st.plotly_chart(fig)

# ------------------------------------------------------------------ Growth
with tab_growth:
    yearly = da.yearly_growth(agg_g, users_g)
    summ = da.growth_summary(yearly)
    st.subheader("Year-on-year growth and CAGR")
    st.caption("Uses all years; respects the Region, State tier, State and Transaction type filters.")
    if summ:
        g1, g2, g3 = st.columns(3)
        g1.metric(f"CAGR transaction value {summ['from_year']}-{summ['to_year']}", f"{summ['cagr_value']:.1f}%")
        g2.metric("CAGR transactions", f"{summ['cagr_transactions']:.1f}%")
        g3.metric("CAGR registered users", f"{summ['cagr_users']:.1f}%")
    show = yearly.rename(columns={
        "amount_cr": "Value (Cr)", "trans_counts": "Transactions", "users_year_end": "Users (year end)",
        "txn_per_user": "Txns per user", "yoy_value_pct": "YoY value %",
        "yoy_transactions_pct": "YoY transactions %", "yoy_users_pct": "YoY users %"}).round(1)
    st.dataframe(show)
    fig = px.bar(yearly.dropna(subset=["yoy_value_pct"]), x="year", y="yoy_value_pct",
                 title="YoY growth in transaction value (%)", color_discrete_sequence=[BLUE])
    fig.update_layout(margin=dict(l=0, r=0, t=40, b=0), xaxis_title="", yaxis_title="%")
    fig.update_xaxes(type="category")
    st.plotly_chart(fig)

# ------------------------------------------------------------------ Users and engagement
with tab_users:
    st.subheader("Top users and engagement")
    left, right = st.columns(2)
    with left:
        tu = da.top_districts_by_users(dq_f, top_n)
        fig = px.bar(tu.sort_values("registered_users"), x="registered_users", y="district_key", orientation="h",
                     title=f"Top {top_n} districts by registered users", color_discrete_sequence=[BLUE])
        fig.update_layout(margin=dict(l=0, r=0, t=40, b=0), xaxis_title="", yaxis_title="")
        st.plotly_chart(fig)
    with right:
        last = users_f.sort_values(["year", "quarter"]).iloc[-1][["year", "quarter"]] if not users_f.empty else None
        if last is not None:
            snap = users_f[(users_f["year"] == last["year"]) & (users_f["quarter"] == last["quarter"])]
            u_state = snap.groupby("state")["registered_users"].sum()
            t_state = agg_f.groupby("state")["trans_counts"].sum()
            eng = (t_state / u_state).dropna().rename("txn_per_user").reset_index()
            eng = eng.sort_values("txn_per_user", ascending=False).head(top_n)
            fig = px.bar(eng.sort_values("txn_per_user"), x="txn_per_user", y="state", orientation="h",
                         title=f"Top {top_n} states by transactions per registered user",
                         color_discrete_sequence=[BLUE])
            fig.update_layout(margin=dict(l=0, r=0, t=40, b=0), xaxis_title="", yaxis_title="")
            st.plotly_chart(fig)
    st.markdown("**Device brands** (brand data ends at 2022 Q1)")
    b = da.apply_filters(brands, {**sel, "brand": brand_sel})
    if b.empty:
        st.info("No brand data for this selection (brand data covers 2018 Q1 - 2022 Q1 only).")
    else:
        last = b.sort_values(["year", "quarter"]).iloc[-1][["year", "quarter"]]
        bs = b[(b["year"] == last["year"]) & (b["quarter"] == last["quarter"])]
        bt = bs.groupby("brand")["user_counts"].sum().sort_values(ascending=False).head(top_n).reset_index()
        fig = px.bar(bt.sort_values("user_counts"), x="user_counts", y="brand", orientation="h",
                     title=f"Users by device brand ({int(last['year'])} Q{int(last['quarter'])})",
                     color_discrete_sequence=[BLUE])
        fig.update_layout(margin=dict(l=0, r=0, t=40, b=0), xaxis_title="", yaxis_title="")
        st.plotly_chart(fig)

# ------------------------------------------------------------------ Districts
with tab_districts:
    st.subheader("Top transactions by district")
    dist = da.top_n(dq_f, "district_key", "amount_cr", top_n)
    fig = px.bar(dist.sort_values("amount_cr"), x="amount_cr", y="district_key", orientation="h",
                 title=f"Top {top_n} districts by transaction value (Cr)", color_discrete_sequence=[BLUE])
    fig.update_layout(margin=dict(l=0, r=0, t=40, b=0), xaxis_title="", yaxis_title="")
    st.plotly_chart(fig)
    st.dataframe(dist.round(1))

# ------------------------------------------------------------------ Data quality
with tab_quality:
    st.subheader("Data validation")
    report = ROOT / "reports" / "validation_report.md"
    if report.exists():
        st.markdown(report.read_text(encoding="utf-8"))
    else:
        st.info("Run  python scripts\\validate_data.py  to create reports/validation_report.md")
