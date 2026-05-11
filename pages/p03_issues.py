import pandas as pd
import streamlit as st

from utils.data_loader import load_issues
from utils.filters import apply_issue_filters
from utils import charts
from utils.exports import download_csv_button, download_excel_button

_DISPLAY = [
    "repository", "issue_number", "title", "state", "author",
    "labels", "comments", "age_days", "days_since_update",
    "created_at", "issue_url",
]

_COL_CFG = {
    "issue_url":          st.column_config.LinkColumn("Link"),
    "age_days":           st.column_config.NumberColumn("Age (days)"),
    "days_since_update":  st.column_config.NumberColumn("Stale (days)"),
    "comments":           st.column_config.NumberColumn("💬"),
}


def _table(df: pd.DataFrame, key_prefix: str, filename: str):
    cols = [c for c in _DISPLAY if c in df.columns]

    exp1, exp2, _, search_col = st.columns([1, 1, 2, 3])
    download_csv_button(exp1, df[cols], f"{filename}.csv")
    download_excel_button(exp2, {filename: df[cols]}, f"{filename}.xlsx")
    with search_col:
        q = st.text_input("🔍 Filter", key=f"srch_{key_prefix}")
    if q:
        mask = (
            df["title"].str.contains(q, case=False, na=False)
            | df["author"].str.contains(q, case=False, na=False)
            | df["labels"].str.contains(q, case=False, na=False)
        )
        df = df[mask]

    PAGE  = 25
    total = max(1, (len(df) - 1) // PAGE + 1)
    pg    = st.number_input("Page", 1, total, 1, key=f"pg_{key_prefix}")
    st.dataframe(
        df.iloc[(pg - 1) * PAGE : pg * PAGE][cols],
        column_config=_COL_CFG,
        width="stretch",
        height=480,
    )
    st.caption(f"{len(df):,} issues · page {pg}/{total}")


def render():
    st.markdown("<div class='page-header'>🐞 Issues Dashboard</div>", unsafe_allow_html=True)
    st.markdown("<div class='page-sub'>Open, closed, critical, aging, and recent issues</div>", unsafe_allow_html=True)

    f      = st.session_state.get("filters", {})
    issues = apply_issue_filters(load_issues(), f)

    if issues.empty:
        st.warning("No issue data found. Click **🔄 Refresh GitHub Data** in the sidebar.")
        return

    open_df   = issues[issues["state"] == "open"].copy()
    closed_df = issues[issues["state"] == "closed"].copy()
    crit_df   = issues[
        (issues["state"] == "open") & (issues["days_since_update"] > 60)
    ].sort_values("days_since_update", ascending=False)
    aging_df  = open_df.sort_values("age_days", ascending=False)
    recent_df = issues.sort_values("created_at", ascending=False).head(200)

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Total",                   len(issues))
    k2.metric("🟢 Open",                 len(open_df))
    k3.metric("✅ Closed",               len(closed_df))
    k4.metric("🔴 Critical (>60d stale)", len(crit_df))
    k5.metric("Closure %", f"{round(len(closed_df) / len(issues) * 100, 1) if len(issues) else 0}%")

    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(charts.issue_velocity(issues), width="stretch")
    with col2:
        st.plotly_chart(charts.aging_histogram(issues), width="stretch")

    col3, col4 = st.columns(2)
    with col3:
        st.plotly_chart(charts.issue_state_pie(issues), width="stretch")
    with col4:
        fig_lbl = charts.label_bar(issues)
        if fig_lbl.data:
            st.plotly_chart(fig_lbl, width="stretch")

    st.markdown("---")

    tabs = st.tabs([
        f"🟢 Open ({len(open_df)})",
        f"✅ Closed ({len(closed_df)})",
        f"🚨 Critical ({len(crit_df)})",
        f"⏳ Aging ({len(aging_df)})",
        f"🆕 Recent ({min(200, len(recent_df))})",
    ])

    with tabs[0]:
        _table(open_df,   "open",   "open_issues")
    with tabs[1]:
        _table(closed_df, "closed", "closed_issues")
    with tabs[2]:
        st.info("Issues open for >60 days with no update — these need attention.")
        _table(crit_df,   "crit",   "critical_issues")
    with tabs[3]:
        _table(aging_df,  "aging",  "aging_issues")
    with tabs[4]:
        _table(recent_df, "recent", "recent_issues")
