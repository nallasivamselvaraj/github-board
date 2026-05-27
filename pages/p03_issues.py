import pandas as pd
import streamlit as st

from utils.data_loader import load_issues
from utils.filters import apply_issue_filters
from utils import charts
from utils.exports import download_csv_button, download_excel_button

_DISPLAY = [
    "repository", "issue_number", "title", "state", "author",
    "labels", "commented", "age_days", "days_since_update",
    "created_at", "issue_url",
]
_COL_CFG = {
    "issue_url":         st.column_config.LinkColumn("Link", display_text="Open ↗"),
    "age_days":          st.column_config.NumberColumn("Age (days)", format="%d d"),
    "days_since_update": st.column_config.NumberColumn("Stale (days)", format="%d d"),
    "commented":         st.column_config.CheckboxColumn("💬 Commented"),
    "issue_number":      st.column_config.NumberColumn("#"),
}


def _table(df: pd.DataFrame, key_prefix: str, filename: str):
    cols = [c for c in _DISPLAY if c in df.columns]

    c1, c2, _, c3 = st.columns([1, 1, 2, 3])
    download_csv_button(c1, df[cols], f"{filename}.csv")
    download_excel_button(c2, {filename: df[cols]}, f"{filename}.xlsx")
    with c3:
        q = st.text_input("🔍 Quick filter", key=f"srch_{key_prefix}",
                          placeholder="Search title, author, label…")
    if q:
        mask = (
            df["title"].str.contains(q, case=False, na=False)
            | df["author"].str.contains(q, case=False, na=False)
            | df["labels"].str.contains(q, case=False, na=False)
        )
        df = df[mask]

    PAGE  = 25
    total = max(1, (len(df) - 1) // PAGE + 1)

    left, right = st.columns([6, 1])
    with right:
        pg = st.number_input("Page", 1, total, 1, key=f"pg_{key_prefix}", label_visibility="collapsed")
    with left:
        st.caption(f"Showing **{len(df):,}** issues · page {pg}/{total}")

    st.dataframe(
        df.iloc[(pg - 1) * PAGE: pg * PAGE][cols],
        column_config=_COL_CFG,
        use_container_width=True,
        height=460,
    )


def render():
    st.markdown("<div class='page-header'>🐞 Issues Dashboard</div>", unsafe_allow_html=True)
    st.markdown("<div class='page-sub'>Track open, closed, critical, and aging issues across all repositories</div>",
                unsafe_allow_html=True)

    f      = st.session_state.get("filters", {})
    raw    = load_issues()
    if not raw.empty:
        raw["commented"] = raw["comments"] > 0
    issues = apply_issue_filters(raw, f)

    if issues.empty:
        st.markdown(
            """<div class='info-card' style='border-color:rgba(196,22,42,0.3)'>
                <div style='font-size:1rem;font-weight:700;color:#c4162a;margin-bottom:6px'>⚠️ No Data</div>
                <div style='font-size:0.85rem;color:#718096'>No issue data found — click <b>🔄 Refresh Data</b> in the sidebar.</div>
            </div>""",
            unsafe_allow_html=True,
        )
        return

    open_df   = issues[issues["state"] == "open"].copy()
    closed_df = issues[issues["state"] == "closed"].copy()
    crit_df   = issues[(issues["state"] == "open") & (issues["days_since_update"] > 60)]\
                    .sort_values("days_since_update", ascending=False)
    aging_df  = open_df.sort_values("age_days", ascending=False)
    recent_df = issues.sort_values("created_at", ascending=False).head(200)
    closure   = round(len(closed_df) / len(issues) * 100, 1) if len(issues) else 0

    # ── KPI row ────────────────────────────────────────────
    st.markdown("<div class='kpi-group'>📋 Issue Summary</div>", unsafe_allow_html=True)
    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("📦 Total Issues",        len(issues))
    k2.metric("🟢 Open",                len(open_df))
    k3.metric("✅ Closed",              len(closed_df))
    k4.metric("🚨 Critical (>60d)",     len(crit_df))
    k5.metric("📉 Closure Rate",        f"{closure}%")

    st.markdown("<div class='gradient-divider'></div>", unsafe_allow_html=True)

    # ── Charts ─────────────────────────────────────────────
    st.markdown("<div class='section-header'>📊 Issue Analytics</div>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(charts.issue_velocity(issues), use_container_width=True)
    with col2:
        st.plotly_chart(charts.aging_histogram(issues), use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        st.plotly_chart(charts.issue_state_pie(issues), use_container_width=True)
    with col4:
        fig_lbl = charts.label_bar(issues)
        if fig_lbl.data:
            st.plotly_chart(fig_lbl, use_container_width=True)

    st.markdown("<div class='gradient-divider'></div>", unsafe_allow_html=True)

    # ── Tabbed data tables ─────────────────────────────────
    st.markdown("<div class='section-header'>📋 Issue Details</div>", unsafe_allow_html=True)
    tabs = st.tabs([
        f"🟢 Open ({len(open_df):,})",
        f"✅ Closed ({len(closed_df):,})",
        f"🚨 Critical ({len(crit_df):,})",
        f"⏳ Aging ({len(aging_df):,})",
        f"🆕 Recent ({min(200, len(recent_df)):,})",
    ])
    with tabs[0]: _table(open_df,   "open",   "open_issues")
    with tabs[1]: _table(closed_df, "closed", "closed_issues")
    with tabs[2]:
        if len(crit_df):
            st.markdown(
                "<div class='accent-card' style='border-color:rgba(196,22,42,0.3);margin-bottom:12px'>"
                "<span style='color:#c4162a;font-weight:700'>🚨 Critical Issues</span>"
                " — open &gt;60 days with no recent activity. These need immediate attention.</div>",
                unsafe_allow_html=True,
            )
        _table(crit_df, "crit", "critical_issues")
    with tabs[3]: _table(aging_df,  "aging",  "aging_issues")
    with tabs[4]: _table(recent_df, "recent", "recent_issues")
