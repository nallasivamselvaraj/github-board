import streamlit as st

from utils.data_loader import load_issues, load_prs, load_releases
from utils.filters import apply_issue_filters, apply_pr_filters
from utils.metrics import issue_metrics, repo_summary
from utils import charts


def render():
    st.markdown("<div class='page-header'>🏠 Executive Dashboard</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='page-sub'>Organisation-wide engineering health at a glance</div>",
        unsafe_allow_html=True,
    )

    f        = st.session_state.get("filters", {})
    issues   = apply_issue_filters(load_issues(), f)
    prs      = apply_pr_filters(load_prs(), f)
    releases = load_releases()

    if issues.empty:
        st.warning("No issue data found. Click **🔄 Refresh Data** in the sidebar.")
        return

    m = issue_metrics(issues, prs, releases)

    # ── Issue KPIs ─────────────────────────────────────────
    st.markdown("<div class='kpi-group'>Issues</div>", unsafe_allow_html=True)
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("📦 Repositories",  m["total_repos"])
    c2.metric("📋 Total Issues",  m["total_issues"])
    c3.metric("🟢 Open",          m["open_issues"])
    c4.metric("✅ Closed",        m["closed_issues"])
    c5.metric("📉 Closure Rate",  f"{m['closure_rate']}%")
    c6.metric("🔴 Stale >30d",    m["stale_issues"])

    st.markdown("<br>", unsafe_allow_html=True)

    # ── PR & Release KPIs ──────────────────────────────────
    st.markdown("<div class='kpi-group'>Pull Requests & Releases</div>", unsafe_allow_html=True)
    c7, c8, c9, c10, c11, c12 = st.columns(6)
    c7.metric("🔀 Total PRs",     m["total_prs"])
    c8.metric("🟡 Open PRs",      m["open_prs"])
    c9.metric("🟣 Merged PRs",    m["merged_prs"])
    c10.metric("📈 Merge Rate",   f"{m['merge_rate']}%")
    c11.metric("🏷️ Releases",    m["total_releases"])
    c12.metric("👤 Contributors", m["contributors"])

    st.markdown("<div class='gradient-divider'></div>", unsafe_allow_html=True)

    # ── Activity Timeline (full width) ─────────────────────
    st.plotly_chart(charts.engineering_activity_timeline(issues, prs), use_container_width=True)

    # ── Core charts ────────────────────────────────────────
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(charts.issue_state_pie(issues), use_container_width=True)
    with col2:
        st.plotly_chart(charts.top_repos_bar(issues), use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        st.plotly_chart(charts.issue_velocity(issues), use_container_width=True)
    with col4:
        if not prs.empty:
            st.plotly_chart(charts.pr_trend(prs), use_container_width=True)
        else:
            st.plotly_chart(charts.release_timeline(releases), use_container_width=True)

    col5, col6 = st.columns(2)
    with col5:
        fig_lbl = charts.label_bar(issues)
        if fig_lbl.data:
            st.plotly_chart(fig_lbl, use_container_width=True)
    with col6:
        st.plotly_chart(charts.staleness_pie(issues), use_container_width=True)

    st.markdown("<div class='gradient-divider'></div>", unsafe_allow_html=True)

    # ── Repository Overview table ──────────────────────────
    st.markdown("<div class='section-header'>Repository Overview</div>", unsafe_allow_html=True)
    rs = repo_summary(issues, prs)
    if not rs.empty:
        st.dataframe(rs.head(15), use_container_width=True, height=380)
