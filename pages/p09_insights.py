# ============================================================
# pages/p09_insights.py
# Advanced Team Velocity & Engineering Insights dashboard
# ============================================================

from datetime import date, timedelta

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from config import COLORS
from utils.data_loader import load_contributors, load_issues, load_prs, load_repo_meta
from utils.filters import apply_issue_filters, apply_pr_filters
from utils.metrics import contributor_summary, issue_metrics, repo_summary
from utils import charts


def _health_score(row: pd.Series) -> tuple[int, str, str]:
    """Compute a 0-100 health score for a repository row."""
    score = 100
    color = "#a6e3a1"
    grade = "A"

    closure_rate = row.get("Closure_Rate%", 0)
    avg_age      = row.get("Avg_Age_Days", 0)
    open_issues  = row.get("Open_Issues", 0)

    # Closure rate penalty (lower = worse)
    if closure_rate < 30:
        score -= 30
    elif closure_rate < 60:
        score -= 15
    elif closure_rate < 80:
        score -= 5

    # Avg age penalty
    if avg_age > 90:
        score -= 30
    elif avg_age > 60:
        score -= 20
    elif avg_age > 30:
        score -= 10

    # Open issues count penalty (relative)
    if open_issues > 100:
        score -= 15
    elif open_issues > 50:
        score -= 8
    elif open_issues > 20:
        score -= 3

    score = max(0, min(100, score))

    if score >= 80:
        grade, color = "A", "#a6e3a1"
    elif score >= 65:
        grade, color = "B", "#89b4fa"
    elif score >= 50:
        grade, color = "C", "#f9e2af"
    elif score >= 35:
        grade, color = "D", "#fab387"
    else:
        grade, color = "F", "#f38ba8"

    return score, grade, color


def render():
    st.markdown("<div class='page-header'>🎯 Engineering Insights</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='page-sub'>Deep-dive analytics — velocity trends, health scores, team efficiency</div>",
        unsafe_allow_html=True,
    )

    f        = st.session_state.get("filters", {})
    issues   = apply_issue_filters(load_issues(), f)
    prs      = apply_pr_filters(load_prs(), f)
    raw_c    = load_contributors()
    meta     = load_repo_meta()

    if issues.empty:
        st.warning("No data available. Click **🔄 Refresh Data** in the sidebar.")
        return

    m  = issue_metrics(issues, prs, pd.DataFrame())
    rs = repo_summary(issues, prs)
    cs = contributor_summary(issues, prs)

    # ── Summary KPIs ──────────────────────────────────────
    st.markdown("<div class='kpi-group'>Team Overview</div>", unsafe_allow_html=True)
    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("📦 Repositories",   m["total_repos"])
    k2.metric("👤 Contributors",   m["contributors"])
    k3.metric("📈 Closure Rate",   f"{m['closure_rate']}%")
    k4.metric("⏱️ Avg PR Cycle",   f"{m['avg_cycle']}d")

    merged_rate_str = f"{m['merge_rate']}%" if m["total_prs"] else "—"
    k5.metric("🟣 PR Merge Rate",  merged_rate_str)

    st.markdown("<div class='gradient-divider'></div>", unsafe_allow_html=True)

    # ── Time period selector ──────────────────────────────
    period_col, _, _ = st.columns([2, 3, 3])
    with period_col:
        period = st.selectbox(
            "📅 Analysis Window",
            ["Last 30 days", "Last 60 days", "Last 90 days", "Last 6 months", "All time"],
            index=2,
            key="insights_period",
        )
    days_map = {"Last 30 days": 30, "Last 60 days": 60, "Last 90 days": 90,
                "Last 6 months": 180, "All time": 9999}
    days = days_map[period]
    cutoff = date.today() - timedelta(days=days) if days < 9999 else date(2000, 1, 1)

    windowed_issues = issues[issues["created_date"] >= cutoff] if "created_date" in issues.columns else issues
    windowed_prs    = prs[prs["created_date"] >= cutoff] if not prs.empty and "created_date" in prs.columns else prs

    # ── Activity Calendar ─────────────────────────────────
    st.markdown("<div class='section-header'>🗓️ Activity Calendar</div>", unsafe_allow_html=True)
    st.plotly_chart(charts.activity_calendar_heatmap(issues, "date"), use_container_width=True)

    st.markdown("<div class='gradient-divider'></div>", unsafe_allow_html=True)

    # ── Velocity & Closure Rate ───────────────────────────
    st.markdown("<div class='section-header'>📈 Velocity Trends</div>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(charts.issue_velocity(windowed_issues), use_container_width=True)
    with col2:
        st.plotly_chart(charts.issue_close_rate_trend(windowed_issues), use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        st.plotly_chart(charts.pr_trend(windowed_prs), use_container_width=True)
    with col4:
        st.plotly_chart(charts.issue_cumulative(windowed_issues), use_container_width=True)

    st.markdown("<div class='gradient-divider'></div>", unsafe_allow_html=True)

    # ── Repository Health Scorecards ──────────────────────
    st.markdown("<div class='section-header'>🏥 Repository Health Scores</div>", unsafe_allow_html=True)
    st.caption("Score = composite of closure rate, average issue age, and open issue volume")

    if not rs.empty:
        # Compute health scores
        scored = rs.copy()
        scored["Score"], scored["Grade"], scored["ScoreColor"] = zip(*scored.apply(_health_score, axis=1))
        scored = scored.sort_values("Score", ascending=False)

        # Show top repos as health cards
        top_12 = scored.head(12)
        cols_per_row = 4
        rows = [top_12.iloc[i:i+cols_per_row] for i in range(0, len(top_12), cols_per_row)]
        for row_df in rows:
            row_cols = st.columns(cols_per_row)
            for j, (_, repo_row) in enumerate(row_df.iterrows()):
                with row_cols[j]:
                    score  = repo_row["Score"]
                    grade  = repo_row["Grade"]
                    color  = repo_row["ScoreColor"]
                    repo   = repo_row["Repository"]
                    cr     = repo_row.get("Closure_Rate%", 0)
                    age    = repo_row.get("Avg_Age_Days", 0)
                    opens  = repo_row.get("Open_Issues", 0)
                    st.markdown(
                        f"""<div class='health-card'>
                          <div class='health-name' title='{repo}'>{repo}</div>
                          <div style='display:flex;align-items:baseline;gap:10px'>
                            <span class='health-score' style='color:{color}'>{score}</span>
                            <span style='font-size:1.4rem;font-weight:800;color:{color}'>{grade}</span>
                          </div>
                          <div class='health-label'>Health Score</div>
                          <div style='margin-top:10px;font-size:0.76rem;color:#6c7086;line-height:1.8'>
                            📉 Closure: <b style='color:#cdd6f4'>{cr}%</b><br>
                            ⏳ Avg Age: <b style='color:#cdd6f4'>{int(age)}d</b><br>
                            🟢 Open: <b style='color:#cdd6f4'>{int(opens)}</b>
                          </div>
                        </div>""",
                        unsafe_allow_html=True,
                    )
        st.markdown("")

        # Radar chart
        st.plotly_chart(charts.repo_health_radar(rs), use_container_width=True)

    st.markdown("<div class='gradient-divider'></div>", unsafe_allow_html=True)

    # ── Team Efficiency ───────────────────────────────────
    st.markdown("<div class='section-header'>👥 Team Efficiency</div>", unsafe_allow_html=True)

    col5, col6 = st.columns(2)
    with col5:
        st.plotly_chart(charts.contributor_bar(cs), use_container_width=True)
    with col6:
        st.plotly_chart(charts.contributor_repos_scatter(cs), use_container_width=True)

    # Contributor × Repo heatmap
    st.plotly_chart(charts.contributor_heatmap(cs, issues), use_container_width=True)

    st.markdown("<div class='gradient-divider'></div>", unsafe_allow_html=True)

    # ── PR Efficiency Table ───────────────────────────────
    if not prs.empty and "cycle_time_days" in prs.columns:
        st.markdown("<div class='section-header'>⚡ PR Performance Analysis</div>", unsafe_allow_html=True)

        pr_stats_col1, pr_stats_col2, pr_stats_col3, pr_stats_col4 = st.columns(4)
        merged_prs = prs[prs.get("merged", False) == True] if "merged" in prs.columns else pd.DataFrame()
        avg_cyc    = round(prs["cycle_time_days"].dropna().mean(), 1)
        med_cyc    = round(prs["cycle_time_days"].dropna().median(), 1)
        p90_cyc    = round(prs["cycle_time_days"].dropna().quantile(0.9), 1)

        pr_stats_col1.metric("Avg Cycle Time",    f"{avg_cyc}d")
        pr_stats_col2.metric("Median Cycle Time", f"{med_cyc}d")
        pr_stats_col3.metric("P90 Cycle Time",    f"{p90_cyc}d")
        pr_stats_col4.metric("Merged PRs",        len(merged_prs))

        col7, col8 = st.columns(2)
        with col7:
            st.plotly_chart(charts.pr_cycle_hist(prs), use_container_width=True)
        with col8:
            st.plotly_chart(charts.pr_author_bar(prs), use_container_width=True)

    st.markdown("<div class='gradient-divider'></div>", unsafe_allow_html=True)

    # ── Issues Needing Attention ──────────────────────────
    st.markdown("<div class='section-header'>🚨 Issues Needing Attention</div>", unsafe_allow_html=True)

    if not issues.empty:
        attention_tabs = st.tabs([
            "🔴 Long-Stale (>90d)", "⚡ High Comment Count", "🏷️ No Labels", "🆕 Opened Today"
        ])

        with attention_tabs[0]:
            stale_df = issues[
                (issues["state"] == "open") & (issues["days_since_update"] > 90)
            ].sort_values("days_since_update", ascending=False)
            if stale_df.empty:
                st.success("✅ No issues stale for more than 90 days!")
            else:
                cols = [c for c in ["repository", "issue_number", "title", "author", "days_since_update", "age_days", "issue_url"] if c in stale_df.columns]
                st.dataframe(
                    stale_df[cols].head(50),
                    column_config={"issue_url": st.column_config.LinkColumn("Link")},
                    use_container_width=True, height=360,
                )
                st.caption(f"{len(stale_df):,} issues stale for 90+ days")

        with attention_tabs[1]:
            if "comments" in issues.columns:
                hot_df = issues[issues["state"] == "open"].sort_values("comments", ascending=False).head(50)
                cols = [c for c in ["repository", "issue_number", "title", "author", "comments", "age_days", "issue_url"] if c in hot_df.columns]
                st.dataframe(
                    hot_df[cols],
                    column_config={"issue_url": st.column_config.LinkColumn("Link")},
                    use_container_width=True, height=360,
                )

        with attention_tabs[2]:
            no_label_df = issues[
                (issues["state"] == "open") & (issues["labels"].fillna("") == "")
            ].sort_values("age_days", ascending=False)
            if no_label_df.empty:
                st.success("✅ All open issues have labels!")
            else:
                cols = [c for c in ["repository", "issue_number", "title", "author", "age_days", "issue_url"] if c in no_label_df.columns]
                st.dataframe(
                    no_label_df[cols].head(50),
                    column_config={"issue_url": st.column_config.LinkColumn("Link")},
                    use_container_width=True, height=360,
                )
                st.caption(f"{len(no_label_df):,} open issues have no labels")

        with attention_tabs[3]:
            today = date.today()
            today_df = issues[issues["created_date"] == today] if "created_date" in issues.columns else pd.DataFrame()
            if today_df.empty:
                st.info("No new issues opened today.")
            else:
                cols = [c for c in ["repository", "issue_number", "title", "state", "author", "labels", "issue_url"] if c in today_df.columns]
                st.dataframe(
                    today_df[cols],
                    column_config={"issue_url": st.column_config.LinkColumn("Link")},
                    use_container_width=True, height=360,
                )
                st.caption(f"{len(today_df):,} issues opened today")
