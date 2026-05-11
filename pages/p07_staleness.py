import streamlit as st

from utils.data_loader import load_issues
from utils.filters import apply_issue_filters
from utils import charts
from utils.exports import download_csv_button, download_excel_button
from config import STALENESS_BUCKETS

_COLS = ["repository", "issue_number", "title", "author", "labels",
         "days_since_update", "age_days", "comments", "issue_url"]

_CFG  = {
    "issue_url":         st.column_config.LinkColumn("Link"),
    "days_since_update": st.column_config.NumberColumn("Stale (days)"),
    "age_days":          st.column_config.NumberColumn("Age (days)"),
}


def render():
    st.markdown("<div class='page-header'>⏳ Staleness & Health</div>", unsafe_allow_html=True)
    st.markdown("<div class='page-sub'>Identify neglected open issues before they become blockers</div>", unsafe_allow_html=True)

    f      = st.session_state.get("filters", {})
    issues = apply_issue_filters(load_issues(), f)

    if issues.empty:
        st.warning("No data available. Click **🔄 Refresh GitHub Data** in the sidebar.")
        return

    open_df = issues[issues["state"] == "open"].copy()

    if open_df.empty:
        st.success("🎉 No open issues in current filter — everything is resolved!")
        return

    buckets = {b[0]: int((open_df["staleness"] == b[0]).sum()) for b in STALENESS_BUCKETS}

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Open Issues",          len(open_df))
    k2.metric("🟢 Fresh (<1 week)",   buckets.get("🟢 < 1 week", 0))
    k3.metric("🟡 1–4 weeks",         buckets.get("🟡 1–4 weeks", 0))
    k4.metric("🟠 1–3 months",        buckets.get("🟠 1–3 months", 0))
    k5.metric("🔴 Critical (>3 mo)",  buckets.get("🔴 > 3 months", 0))

    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(charts.staleness_pie(issues), width="stretch")
    with col2:
        st.plotly_chart(charts.aging_histogram(issues), width="stretch")

    st.plotly_chart(charts.staleness_heatmap(issues), width="stretch")

    st.markdown("---")

    tab_labels = [f"{b[0]}  ({buckets.get(b[0], 0)})" for b in STALENESS_BUCKETS]
    tabs = st.tabs(tab_labels + ["📋 All Open"])

    for i, bucket in enumerate(STALENESS_BUCKETS):
        bname = bucket[0]
        with tabs[i]:
            sub  = open_df[open_df["staleness"] == bname].sort_values("days_since_update", ascending=False)
            cols = [c for c in _COLS if c in sub.columns]
            exp1, exp2, _ = st.columns([1, 1, 5])
            download_csv_button(exp1, sub[cols], f"stale_{i}.csv")
            download_excel_button(exp2, {bname: sub[cols]}, f"stale_{i}.xlsx")
            st.dataframe(sub[cols], column_config=_CFG, width="stretch", height=460)
            st.caption(f"{len(sub):,} issues in this bucket")

    with tabs[len(STALENESS_BUCKETS)]:
        all_cols   = [c for c in _COLS if c in open_df.columns]
        all_sorted = open_df.sort_values("days_since_update", ascending=False)
        exp1, exp2, _ = st.columns([1, 1, 5])
        download_csv_button(exp1, all_sorted[all_cols], "all_open_issues.csv")
        download_excel_button(exp2, {"All Open": all_sorted[all_cols]}, "all_open_issues.xlsx")
        st.dataframe(all_sorted[all_cols], column_config=_CFG, width="stretch", height=480)
        st.caption(f"{len(all_sorted):,} open issues total")

    st.markdown("---")
    st.markdown("<div class='section-header'>Repository Health Scorecard</div>", unsafe_allow_html=True)

    scorecard = (
        open_df.groupby("repository")
        .agg(
            Open_Issues    = ("issue_number",       "count"),
            Critical       = ("staleness",          lambda x: (x == "🔴 > 3 months").sum()),
            Avg_Stale_Days = ("days_since_update",  "mean"),
            Max_Stale_Days = ("days_since_update",  "max"),
        )
        .reset_index()
        .rename(columns={"repository": "Repository"})
    )
    scorecard["Avg_Stale_Days"] = scorecard["Avg_Stale_Days"].round(0).astype(int)
    scorecard["Max_Stale_Days"] = scorecard["Max_Stale_Days"].astype(int)
    scorecard["Critical_%"]     = (scorecard["Critical"] / scorecard["Open_Issues"] * 100).round(1)
    scorecard = scorecard.sort_values("Critical_%", ascending=False)

    st.dataframe(
        scorecard,
        width="stretch",
        column_config={
            "Critical_%": st.column_config.ProgressColumn(
                "Critical %", min_value=0, max_value=100, format="%.1f%%"
            )
        },
        height=400,
    )
