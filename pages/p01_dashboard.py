import streamlit as st

from utils.data_loader import load_issues, load_prs, load_releases
from utils.filters import apply_issue_filters, apply_pr_filters
from utils.metrics import issue_metrics, repo_summary
from utils import charts


def render():
    st.markdown("<div class='page-header'>🏠 Executive Dashboard</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='page-sub'>Organisation-wide engineering health at a glance · Simtestlab</div>",
        unsafe_allow_html=True,
    )

    f        = st.session_state.get("filters", {})
    issues   = apply_issue_filters(load_issues(), f)
    prs      = apply_pr_filters(load_prs(), f)
    releases = load_releases()

    if issues.empty:
        st.markdown(
            """<div class='sidebar-empty-msg'>
                No data found. Click <b>🔄 Refresh Data</b> in the sidebar to fetch from GitHub API.
            </div>""",
            unsafe_allow_html=True,
        )
        return

    m = issue_metrics(issues, prs, releases)

    # ── TOP ROW: Calendar ──────────────────────────────────
    st.plotly_chart(charts.activity_calendar_heatmap(issues), use_container_width=True)
    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

    # ── ROW 1: Metrics ─────────────────────────────────────
    st.markdown("<div class='kpi-group'>📋 Core Health Metrics</div>", unsafe_allow_html=True)
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("📦 Repos",         m["total_repos"])
    c2.metric("📋 Total Issues",  m["total_issues"])
    c3.metric("🟢 Open Issues",   m["open_issues"])
    c4.metric("✅ Closed",        m["closed_issues"])
    c5.metric("📉 Closure Rate",  f"{m['closure_rate']}%")
    c6.metric("🔴 Stale >30d",    m["stale_issues"])

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    # ── ROW 2: PR Metrics ──────────────────────────────────
    st.markdown("<div class='kpi-group'>🔀 Workflow Velocity</div>", unsafe_allow_html=True)
    c7, c8, c9, c10, c11, c12 = st.columns(6)
    c7.metric("🔀 Total PRs",     m["total_prs"])
    c8.metric("🟢 Open PRs",      m["open_prs"])
    c9.metric("🟣 Merged PRs",    m["merged_prs"])
    c10.metric("📈 Merge Rate",   f"{m['merge_rate']}%")
    c11.metric("🏷️ Releases",    m["total_releases"])
    c12.metric("👤 Contributors", m["contributors"])

    st.markdown("<div class='gradient-divider'></div>", unsafe_allow_html=True)

    # ── ROW 3: Pulse & Distribution ───────────────────────
    col_left, col_right = st.columns([2, 1])
    with col_left:
        st.markdown("<div class='section-header'>📡 Engineering Pulse</div>", unsafe_allow_html=True)
        st.plotly_chart(charts.engineering_activity_timeline(issues, prs), use_container_width=True)
    with col_right:
        st.markdown("<div class='section-header'>📊 Issue Balance</div>", unsafe_allow_html=True)
        st.plotly_chart(charts.issue_state_pie(issues), use_container_width=True)

    st.markdown("<div class='gradient-divider'></div>", unsafe_allow_html=True)

    # ── ROW 4: Throughput ──────────────────────────────────
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<div class='section-header'>📈 Issue Velocity</div>", unsafe_allow_html=True)
        st.plotly_chart(charts.issue_velocity(issues), use_container_width=True)
    with col2:
        st.markdown("<div class='section-header'>🔀 PR Throughput</div>", unsafe_allow_html=True)
        if not prs.empty:
            st.plotly_chart(charts.pr_trend(prs), use_container_width=True)
        else:
            st.plotly_chart(charts.release_timeline(releases), use_container_width=True)

    st.markdown("<div class='gradient-divider'></div>", unsafe_allow_html=True)

    # ── ROW 5: Repository Leaderboard ──────────────────────
    st.markdown("<div class='section-header'>📦 Repository Health Leaderboard</div>", unsafe_allow_html=True)
    rs = repo_summary(issues, prs)
    if not rs.empty:
        st.dataframe(
            rs.head(20),
            use_container_width=True,
            height=320,
            column_config={
                "Repository": st.column_config.TextColumn("Repo"),
                "Closure_Rate%": st.column_config.ProgressColumn("Closure", min_value=0, max_value=100, format="%d%%"),
            }
        )
        st.caption(f"{len(rs):,} repositories tracked across organization")
