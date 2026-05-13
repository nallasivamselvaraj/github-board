import pandas as pd
import streamlit as st

from utils.data_loader import load_issues
from utils.filters import apply_issue_filters
from utils import charts
from utils.exports import download_csv_button, download_excel_button
from config import STALENESS_BUCKETS

_COLS = ["repository", "issue_number", "title", "author", "labels",
         "days_since_update", "age_days", "comments", "issue_url"]

_CFG  = {
    "issue_url":         st.column_config.LinkColumn("Link", display_text="Open ↗"),
    "days_since_update": st.column_config.NumberColumn("Stale (days)", format="%d d"),
    "age_days":          st.column_config.NumberColumn("Age (days)", format="%d d"),
    "issue_number":      st.column_config.NumberColumn("#"),
}


def render():
    st.markdown("<div class='page-header'>⏳ Staleness & Health</div>", unsafe_allow_html=True)
    st.markdown("<div class='page-sub'>Identify neglected open issues before they become blockers</div>", unsafe_allow_html=True)

    f      = st.session_state.get("filters", {})
    issues = apply_issue_filters(load_issues(), f)

    if issues.empty:
        st.markdown(
            """<div class='info-card' style='border-color:rgba(220,38,38,0.3)'>
                <div style='font-size:1rem;font-weight:700;color:#dc2626;margin-bottom:6px'>⚠️ No Data</div>
                <div style='font-size:0.85rem;color:#6b7280'>No data found — click <b>🔄 Refresh Data</b> in the sidebar.</div>
            </div>""",
            unsafe_allow_html=True,
        )
        return

    open_df = issues[issues["state"] == "open"].copy()

    if open_df.empty:
        st.markdown(
            """<div class='accent-card' style='border-color:rgba(54,163,71,0.4);text-align:center;padding:40px;'>
                <div style='font-size:2rem;margin-bottom:10px;'>🎉</div>
                <div style='color:#36a347;font-weight:700;font-size:1.1rem;'>Zero Open Issues</div>
                <div style='color:#718096;font-size:0.85rem;'>Everything is resolved in current selection!</div>
            </div>""",
            unsafe_allow_html=True,
        )
        return

    buckets = {b[0]: int((open_df["staleness"] == b[0]).sum()) for b in STALENESS_BUCKETS}

    # ── KPI row ────────────────────────────────────────────
    st.markdown("<div class='kpi-group'>⏳ Staleness Breakdown</div>", unsafe_allow_html=True)
    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("📦 Open Issues",       len(open_df))
    k2.metric("🟢 Fresh (<1w)",       buckets.get("🟢 < 1 week", 0))
    k3.metric("🟡 1–4 weeks",         buckets.get("🟡 1–4 weeks", 0))
    k4.metric("🟠 1–3 months",        buckets.get("🟠 1–3 months", 0))
    k5.metric("🔴 Critical (>3mo)",   buckets.get("🔴 > 3 months", 0))

    st.markdown("<div class='gradient-divider'></div>", unsafe_allow_html=True)

    # ── Charts ─────────────────────────────────────────────
    st.markdown("<div class='section-header'>📊 Staleness Distribution</div>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(charts.staleness_pie(issues), use_container_width=True)
    with col2:
        st.plotly_chart(charts.aging_histogram(issues), use_container_width=True)

    st.markdown("<div class='section-header'>📡 Repository Staleness Heatmap</div>", unsafe_allow_html=True)
    st.plotly_chart(charts.staleness_heatmap(issues), use_container_width=True)

    st.markdown("<div class='gradient-divider'></div>", unsafe_allow_html=True)

    # ── Tabs ──────────────────────────────────────────────
    st.markdown("<div class='section-header'>📋 Stale Issue Explorer</div>", unsafe_allow_html=True)
    tab_labels = [f"{b[0].split(' ')[0]} {b[0].split(' ')[1]} ({buckets.get(b[0], 0)})" for b in STALENESS_BUCKETS]
    tabs = st.tabs(tab_labels + [f"📋 All Open ({len(open_df)})"])

    for i, bucket in enumerate(STALENESS_BUCKETS):
        bname = bucket[0]
        with tabs[i]:
            sub  = open_df[open_df["staleness"] == bname].sort_values("days_since_update", ascending=False)
            if sub.empty:
                st.markdown("<div style='padding:20px;color:#6e7077;text-align:center;'>No issues in this bucket.</div>", unsafe_allow_html=True)
                continue
            
            cols = [c for c in _COLS if c in sub.columns]
            c1, c2, _ = st.columns([1, 1, 5])
            download_csv_button(c1, sub[cols], f"stale_{i}.csv")
            download_excel_button(c2, {bname: sub[cols]}, f"stale_{i}.xlsx")
            st.dataframe(sub[cols], column_config=_CFG, use_container_width=True, height=400)

    with tabs[len(STALENESS_BUCKETS)]:
        all_cols   = [c for c in _COLS if c in open_df.columns]
        all_sorted = open_df.sort_values("days_since_update", ascending=False)
        c1, c2, _ = st.columns([1, 1, 5])
        download_csv_button(c1, all_sorted[all_cols], "all_open_issues.csv")
        download_excel_button(c2, {"All Open": all_sorted[all_cols]}, "all_open_issues.xlsx")
        st.dataframe(all_sorted[all_cols], column_config=_CFG, use_container_width=True, height=400)

    st.markdown("<div class='gradient-divider'></div>", unsafe_allow_html=True)

    # ── Scorecard ──────────────────────────────────────────
    st.markdown("<div class='section-header'>🏥 Repository Health Scorecard</div>", unsafe_allow_html=True)
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
        use_container_width=True,
        column_config={
            "Critical_%": st.column_config.ProgressColumn(
                "Critical %", min_value=0, max_value=100, format="%.1f%%"
            ),
            "Repository": st.column_config.TextColumn("Repo"),
        },
        height=400,
    )
