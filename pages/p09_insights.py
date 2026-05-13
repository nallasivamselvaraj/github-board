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
    score = 100
    cr, age, op = row.get("Closure_Rate%", 0), row.get("Avg_Age_Days", 0), row.get("Open_Issues", 0)
    if cr < 30: score -= 30
    elif cr < 60: score -= 15
    if age > 90: score -= 30
    elif age > 45: score -= 15
    if op > 50: score -= 10
    score = max(0, min(100, score))
    # Using light-mode compatible status colors
    if score >= 85: return score, "A", "#36a347"  # Green
    if score >= 70: return score, "B", "#1f60c4"  # Blue
    if score >= 55: return score, "C", "#e0b400"  # Yellow
    if score >= 40: return score, "D", "#f46800"  # Orange
    return score, "F", "#c4162a"                  # Red

def _health_card(repo, score, grade, color, cr, age, opens):
    return f"""
    <div class='health-card'>
      <div style='position:absolute;bottom:0;left:0;height:4px;width:{score}%;background:{color};'></div>
      <div class='health-name'>{repo}</div>
      <div style='display:flex;align-items:baseline;gap:8px;margin:8px 0'>
        <span class='health-score' style='color:{color}'>{score}</span>
        <span style='font-size:1.4rem;font-weight:800;color:{color}'>{grade}</span>
      </div>
      <div class='health-label'>Overall Health Index</div>
      <div style='margin-top:12px;font-size:0.75rem;color:#718096;line-height:1.6'>
        Velocity: <b style='color:#24292e'>{cr}%</b><br>
        Age: <b style='color:#24292e'>{int(age)}d</b> · Open: <b style='color:#24292e'>{int(opens)}</b>
      </div>
    </div>"""

def render():
    st.markdown("<div class='page-header'>🎯 Engineering Insights</div>", unsafe_allow_html=True)
    st.markdown("<div class='page-sub'>Advanced analytics · velocity trends · health scores · team efficiency</div>", unsafe_allow_html=True)

    f = st.session_state.get("filters", {})
    issues, prs = apply_issue_filters(load_issues(), f), apply_pr_filters(load_prs(), f)
    if issues.empty:
        st.markdown("<div class='sidebar-empty-msg'>No data available for analysis.</div>", unsafe_allow_html=True)
        return

    m, rs, cs = issue_metrics(issues, prs, pd.DataFrame()), repo_summary(issues, prs), contributor_summary(issues, prs)

    # ── KPI Row ───────────────────────────────────────────
    st.markdown("<div class='kpi-group'>🎯 Executive Indicators</div>", unsafe_allow_html=True)
    k1, k2, k3, k4, k5, k6 = st.columns(6)
    k1.metric("📦 Repositories", m["total_repos"])
    k2.metric("👤 Contributors", m["contributors"])
    k3.metric("📈 Closure Rate", f"{m['closure_rate']}%")
    k4.metric("⏱️ Avg PR Cycle", f"{m['avg_cycle']}d")
    k5.metric("🟣 Merge Rate",   f"{m['merge_rate']}%")
    stale_pct = round(m.get("stale_issues",0) / max(m.get("total_issues",1),1) * 100, 1)
    k6.metric("🔴 Stale Rate",   f"{stale_pct}%")

    st.markdown("<div class='gradient-divider'></div>", unsafe_allow_html=True)

    # ── Time Filter ───────────────────────────────────────
    period = st.selectbox("📅 Analysis Window", ["Last 30 days","Last 90 days","Last 6 months","All time"], index=1)
    days = {"Last 30 days":30,"Last 90 days":90,"Last 6 months":180,"All time":9999}[period]
    cutoff = date.today() - timedelta(days=days) if days < 9999 else date(2000,1,1)
    wi = issues[issues["created_date"] >= cutoff] if "created_date" in issues.columns else issues
    wp = prs[prs["created_date"] >= cutoff] if not prs.empty and "created_date" in prs.columns else prs

    t_vel, t_health, t_team, t_pr = st.tabs(["📈 Velocity", "🏥 Health Scorecard", "👥 Team Efficiency", "⚡ PR Flow"])

    with t_vel:
        st.markdown("<div class='section-header'>🗓️ Contribution Pulse</div>", unsafe_allow_html=True)
        st.plotly_chart(charts.activity_calendar_heatmap(issues), use_container_width=True)
        
        c1, c2 = st.columns(2)
        with c1: st.plotly_chart(charts.issue_velocity(wi), use_container_width=True)
        with c2: st.plotly_chart(charts.issue_close_rate_trend(wi), use_container_width=True)
        
        c3, c4 = st.columns(2)
        with c3: st.plotly_chart(charts.engineering_activity_timeline(wi, wp), use_container_width=True)
        with c4: st.plotly_chart(charts.issue_cumulative(wi), use_container_width=True)

    with t_health:
        st.markdown("<div class='section-header'>🏥 Organization Health Scoring</div>", unsafe_allow_html=True)
        if not rs.empty:
            scored = rs.copy()
            scored["Score"], scored["Grade"], scored["Color"] = zip(*scored.apply(_health_score, axis=1))
            scored = scored.sort_values("Score", ascending=False)
            
            top12 = scored.head(12)
            for i in range(0, len(top12), 4):
                cols = st.columns(4)
                for j, (_, r) in enumerate(top12.iloc[i:i+4].iterrows()):
                    with cols[j]:
                        st.markdown(_health_card(r["Repository"], r["Score"], r["Grade"], r["Color"], 
                                                r.get("Closure_Rate%",0), r.get("Avg_Age_Days",0), r.get("Open_Issues",0)), 
                                    unsafe_allow_html=True)
            
            st.markdown("<div class='section-header'>📊 Health Comparison</div>", unsafe_allow_html=True)
            st.plotly_chart(charts.repo_health_radar(rs), use_container_width=True)
            st.dataframe(scored[["Repository","Score","Grade","Closure_Rate%","Avg_Age_Days","Open_Issues"]], use_container_width=True)

    with t_team:
        st.markdown("<div class='section-header'>👥 Team Efficiency Heatmap</div>", unsafe_allow_html=True)
        st.plotly_chart(charts.contributor_heatmap(cs, issues), use_container_width=True)
        
        c1, c2 = st.columns(2)
        with c1: st.plotly_chart(charts.contributor_bar(cs), use_container_width=True)
        with c2: st.plotly_chart(charts.contributor_repos_scatter(cs), use_container_width=True)

    with t_pr:
        st.markdown("<div class='section-header'>⚡ Pull Request Cycle Time</div>", unsafe_allow_html=True)
        if not prs.empty and "cycle_time_days" in prs.columns:
            c1, c2 = st.columns(2)
            with c1: st.plotly_chart(charts.pr_cycle_hist(prs), use_container_width=True)
            with c2: st.plotly_chart(charts.pr_author_bar(prs), use_container_width=True)
            
            st.markdown("<div class='section-header'>🏢 Cycle Time by Repository</div>", unsafe_allow_html=True)
            repo_c = prs.dropna(subset=["cycle_time_days"]).groupby("repository")["cycle_time_days"].agg(["mean","median"]).reset_index()
            st.dataframe(repo_c.sort_values("mean", ascending=False), use_container_width=True)
        else:
            st.info("No cycle time data found.")
            
    st.markdown("<div class='gradient-divider'></div>", unsafe_allow_html=True)
    if st.button("🖨️ Generate Insights PDF", type="primary"):
        from utils.report_gen import generate_pdf
        pdf = generate_pdf(m, issues, prs, cs, rs, "Insights")
        st.download_button("⬇️ Download PDF", pdf, f"insights_{date.today()}.pdf", "application/pdf")
