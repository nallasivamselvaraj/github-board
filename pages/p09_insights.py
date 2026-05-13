# pages/p09_insights.py  –  Advanced Engineering Insights
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


# ── Health scoring ─────────────────────────────────────────
def _health_score(row: pd.Series) -> tuple[int, str, str]:
    score = 100
    cr  = row.get("Closure_Rate%", 0)
    age = row.get("Avg_Age_Days", 0)
    op  = row.get("Open_Issues", 0)
    if cr  < 30: score -= 30
    elif cr  < 60: score -= 15
    elif cr  < 80: score -= 5
    if age > 90: score -= 30
    elif age > 60: score -= 20
    elif age > 30: score -= 10
    if op > 100: score -= 15
    elif op > 50: score -= 8
    elif op > 20: score -= 3
    score = max(0, min(100, score))
    if score >= 80: return score, "A", "#a6e3a1"
    if score >= 65: return score, "B", "#89b4fa"
    if score >= 50: return score, "C", "#f9e2af"
    if score >= 35: return score, "D", "#fab387"
    return score, "F", "#f38ba8"


def _health_card(repo, score, grade, color, cr, age, opens):
    bar_pct = score
    return f"""
    <div class='health-card' style='position:relative;overflow:hidden'>
      <div style='position:absolute;bottom:0;left:0;height:3px;width:{bar_pct}%;
                  background:linear-gradient(90deg,{color}88,{color});
                  border-radius:0 0 12px 12px'></div>
      <div class='health-name' title='{repo}'>{repo}</div>
      <div style='display:flex;align-items:baseline;gap:8px;margin:6px 0 2px'>
        <span class='health-score' style='color:{color}'>{score}</span>
        <span style='font-size:1.3rem;font-weight:800;color:{color}'>{grade}</span>
      </div>
      <div class='health-label'>Health Score</div>
      <div style='margin-top:8px;font-size:0.75rem;color:#6c7086;line-height:1.9'>
        📉 Closure: <b style='color:#cdd6f4'>{cr}%</b><br>
        ⏳ Avg Age: <b style='color:#cdd6f4'>{int(age)}d</b><br>
        🟢 Open: <b style='color:#cdd6f4'>{int(opens)}</b>
      </div>
    </div>"""


def render():
    st.markdown("<div class='page-header'>🎯 Engineering Insights</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='page-sub'>Deep-dive analytics · velocity trends · health scores · team efficiency</div>",
        unsafe_allow_html=True,
    )

    f      = st.session_state.get("filters", {})
    issues = apply_issue_filters(load_issues(), f)
    prs    = apply_pr_filters(load_prs(), f)
    raw_c  = load_contributors()
    meta   = load_repo_meta()

    if issues.empty:
        st.warning("No data available. Click **🔄 Refresh Data** in the sidebar.")
        return

    m  = issue_metrics(issues, prs, pd.DataFrame())
    rs = repo_summary(issues, prs)
    cs = contributor_summary(issues, prs)

    # ── Top KPIs ──────────────────────────────────────────
    k1, k2, k3, k4, k5, k6 = st.columns(6)
    k1.metric("📦 Repositories",  m["total_repos"])
    k2.metric("👤 Contributors",  m["contributors"])
    k3.metric("📈 Closure Rate",  f"{m['closure_rate']}%")
    k4.metric("⏱️ Avg PR Cycle",  f"{m['avg_cycle']}d")
    k5.metric("🟣 PR Merge Rate", f"{m['merge_rate']}%" if m["total_prs"] else "—")
    stale_pct = round(m.get("stale_issues",0) / max(m.get("total_issues",1),1) * 100, 1)
    k6.metric("🔴 Stale Rate",    f"{stale_pct}%")

    st.markdown("<div class='gradient-divider'></div>", unsafe_allow_html=True)

    # ── Analysis window ───────────────────────────────────
    period_col, _, _ = st.columns([2,3,3])
    with period_col:
        period = st.selectbox("📅 Analysis Window",
            ["Last 30 days","Last 60 days","Last 90 days","Last 6 months","All time"],
            index=2, key="insights_period")
    days_map = {"Last 30 days":30,"Last 60 days":60,"Last 90 days":90,
                "Last 6 months":180,"All time":9999}
    days   = days_map[period]
    cutoff = date.today() - timedelta(days=days) if days < 9999 else date(2000,1,1)
    wi     = issues[issues["created_date"] >= cutoff] if "created_date" in issues.columns else issues
    wp     = prs[prs["created_date"] >= cutoff] if not prs.empty and "created_date" in prs.columns else prs

    # ════════════════════════════════════════════════════════
    # TAB LAYOUT for feature grouping
    # ════════════════════════════════════════════════════════
    tab_vel, tab_health, tab_team, tab_pr, tab_alert, tab_burn = st.tabs([
        "📈 Velocity", "🏥 Health Scores", "👥 Team Efficiency",
        "⚡ PR Analytics", "🚨 Attention Required", "🔥 Burndown",
    ])

    # ── TAB 1: Velocity ───────────────────────────────────
    with tab_vel:
        st.markdown("<div class='section-header'>🗓️ Activity Calendar</div>", unsafe_allow_html=True)
        st.plotly_chart(charts.activity_calendar_heatmap(issues, "date"), use_container_width=True)

        st.markdown("<div class='section-header'>📈 Velocity Trends</div>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1: st.plotly_chart(charts.issue_velocity(wi), use_container_width=True)
        with c2: st.plotly_chart(charts.issue_close_rate_trend(wi), use_container_width=True)

        c3, c4 = st.columns(2)
        with c3: st.plotly_chart(charts.pr_trend(wp), use_container_width=True)
        with c4: st.plotly_chart(charts.issue_cumulative(wi), use_container_width=True)

        # Weekly velocity table
        if not wi.empty and "created_date" in wi.columns:
            st.markdown("<div class='section-header'>📅 Weekly Velocity Breakdown</div>", unsafe_allow_html=True)
            wi2 = wi.copy()
            wi2["week"] = pd.to_datetime(wi2["created_date"]).dt.to_period("W").astype(str)
            weekly = wi2.groupby("week").agg(
                Opened=("issue_number","count"),
                Closed=("state", lambda x: (x=="closed").sum()),
                Authors=("author","nunique"),
            ).reset_index().sort_values("week", ascending=False).head(12)
            weekly["Closure%"] = (weekly["Closed"] / weekly["Opened"].replace(0,1) * 100).round(1)
            st.dataframe(weekly, use_container_width=True, height=300)

    # ── TAB 2: Health Scores ──────────────────────────────
    with tab_health:
        st.markdown("<div class='section-header'>🏥 Repository Health Scores</div>", unsafe_allow_html=True)
        st.caption("Score = composite of closure rate, average issue age, and open issue volume")

        if not rs.empty:
            scored = rs.copy()
            scored["Score"], scored["Grade"], scored["ScoreColor"] = zip(*scored.apply(_health_score, axis=1))
            scored = scored.sort_values("Score", ascending=False)

            # Score distribution donut
            grade_counts = scored["Grade"].value_counts()
            fig_donut = go.Figure(go.Pie(
                labels=grade_counts.index, values=grade_counts.values,
                hole=0.55,
                marker_colors=["#a6e3a1","#89b4fa","#f9e2af","#fab387","#f38ba8"],
                textinfo="label+percent",
                textfont_size=11,
            ))
            fig_donut.update_layout(
                title="Grade Distribution", plot_bgcolor="#1e1e2e", paper_bgcolor="#181825",
                font=dict(color="#cdd6f4", size=11), height=250,
                margin=dict(l=10,r=10,t=40,b=10),
                showlegend=False,
            )
            dc, sc = st.columns([1,2])
            with dc:
                st.plotly_chart(fig_donut, use_container_width=True)
            with sc:
                # Score gauge bar
                avg_score = int(scored["Score"].mean())
                fig_gauge = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=avg_score,
                    title={"text":"Avg Health Score","font":{"color":"#cdd6f4","size":13}},
                    gauge={
                        "axis":{"range":[0,100],"tickcolor":"#6c7086"},
                        "bar":{"color":"#7c3aed"},
                        "bgcolor":"#1e1e2e",
                        "steps":[
                            {"range":[0,35],"color":"#f38ba822"},
                            {"range":[35,65],"color":"#f9e2af22"},
                            {"range":[65,100],"color":"#a6e3a122"},
                        ],
                        "threshold":{"line":{"color":"#cba6f7","width":3},"value":avg_score},
                    },
                    number={"font":{"color":"#cdd6f4","size":36}},
                ))
                fig_gauge.update_layout(
                    plot_bgcolor="#1e1e2e", paper_bgcolor="#181825",
                    font=dict(color="#cdd6f4"), height=250,
                    margin=dict(l=20,r=20,t=30,b=10),
                )
                st.plotly_chart(fig_gauge, use_container_width=True)

            # Health cards grid
            top_12 = scored.head(12)
            cols_per_row = 4
            rows_df = [top_12.iloc[i:i+cols_per_row] for i in range(0, len(top_12), cols_per_row)]
            for row_df in rows_df:
                row_cols = st.columns(cols_per_row)
                for j, (_, r) in enumerate(row_df.iterrows()):
                    with row_cols[j]:
                        st.markdown(
                            _health_card(r["Repository"], r["Score"], r["Grade"], r["ScoreColor"],
                                         r.get("Closure_Rate%",0), r.get("Avg_Age_Days",0),
                                         r.get("Open_Issues",0)),
                            unsafe_allow_html=True,
                        )

            # Health table
            st.markdown("<div class='section-header'>📋 Full Health Table</div>", unsafe_allow_html=True)
            display_cols = ["Repository","Score","Grade","Closure_Rate%","Avg_Age_Days","Open_Issues","Total_Issues"]
            display_cols = [c for c in display_cols if c in scored.columns]
            st.dataframe(scored[display_cols], use_container_width=True, height=360)

            # Radar chart
            st.plotly_chart(charts.repo_health_radar(rs), use_container_width=True)

    # ── TAB 3: Team Efficiency ────────────────────────────
    with tab_team:
        st.markdown("<div class='section-header'>👥 Contributor Overview</div>", unsafe_allow_html=True)
        c5, c6 = st.columns(2)
        with c5: st.plotly_chart(charts.contributor_bar(cs), use_container_width=True)
        with c6: st.plotly_chart(charts.contributor_repos_scatter(cs), use_container_width=True)

        st.plotly_chart(charts.contributor_heatmap(cs, issues), use_container_width=True)

        # Workload distribution
        if not cs.empty and "Issues_Opened" in cs.columns:
            st.markdown("<div class='section-header'>⚖️ Workload Distribution</div>", unsafe_allow_html=True)
            total = cs["Issues_Opened"].sum()
            if total > 0:
                cs2 = cs.copy()
                cs2["Workload%"] = (cs2["Issues_Opened"] / total * 100).round(1)
                top10 = cs2.sort_values("Issues_Opened", ascending=False).head(10)
                fig_wl = go.Figure(go.Bar(
                    x=top10["Author"] if "Author" in top10.columns else top10.iloc[:,0],
                    y=top10["Workload%"],
                    marker=dict(
                        color=top10["Workload%"],
                        colorscale=[[0,"#313244"],[0.5,"#7c3aed"],[1,"#cba6f7"]],
                        showscale=True,
                        colorbar=dict(title="Workload%", tickfont=dict(color="#6c7086")),
                    ),
                    text=[f"{v}%" for v in top10["Workload%"]],
                    textposition="outside",
                ))
                fig_wl.update_layout(
                    title="Workload Share (% of total issues opened)",
                    plot_bgcolor="#1e1e2e", paper_bgcolor="#181825",
                    font=dict(color="#cdd6f4", size=11),
                    xaxis=dict(tickangle=-30, gridcolor="#313244"),
                    yaxis=dict(gridcolor="#313244", title="Workload %"),
                    margin=dict(l=10,r=10,t=50,b=80), height=340,
                )
                st.plotly_chart(fig_wl, use_container_width=True)

        # Contributor data table
        st.markdown("<div class='section-header'>📋 Contributor Detail</div>", unsafe_allow_html=True)
        st.dataframe(cs, use_container_width=True, height=320)

    # ── TAB 4: PR Analytics ───────────────────────────────
    with tab_pr:
        if not prs.empty and "cycle_time_days" in prs.columns:
            merged_prs = prs[prs.get("merged", False) == True] if "merged" in prs.columns else pd.DataFrame()
            avg_cyc = round(prs["cycle_time_days"].dropna().mean(), 1)
            med_cyc = round(prs["cycle_time_days"].dropna().median(), 1)
            p90_cyc = round(prs["cycle_time_days"].dropna().quantile(0.9), 1)

            a, b, c_, d = st.columns(4)
            a.metric("Avg Cycle Time",    f"{avg_cyc}d")
            b.metric("Median Cycle Time", f"{med_cyc}d")
            c_.metric("P90 Cycle Time",   f"{p90_cyc}d")
            d.metric("Merged PRs",        len(merged_prs))

            c7, c8 = st.columns(2)
            with c7: st.plotly_chart(charts.pr_cycle_hist(prs), use_container_width=True)
            with c8: st.plotly_chart(charts.pr_author_bar(prs), use_container_width=True)

            # PR cycle time by repo
            if "repository" in prs.columns:
                st.markdown("<div class='section-header'>🏢 Cycle Time by Repository</div>", unsafe_allow_html=True)
                repo_cycle = (
                    prs.dropna(subset=["cycle_time_days"])
                    .groupby("repository")["cycle_time_days"]
                    .agg(["mean","median","count"])
                    .reset_index()
                    .rename(columns={"mean":"Avg Days","median":"Median Days","count":"PR Count"})
                    .sort_values("Avg Days", ascending=False)
                )
                repo_cycle["Avg Days"]    = repo_cycle["Avg Days"].round(1)
                repo_cycle["Median Days"] = repo_cycle["Median Days"].round(1)

                fig_rc = go.Figure()
                fig_rc.add_trace(go.Bar(
                    x=repo_cycle["repository"], y=repo_cycle["Avg Days"],
                    name="Avg Cycle (days)", marker_color="#cba6f7",
                ))
                fig_rc.add_trace(go.Scatter(
                    x=repo_cycle["repository"], y=repo_cycle["Median Days"],
                    name="Median", mode="markers",
                    marker=dict(color="#f9e2af", size=9, symbol="diamond"),
                ))
                fig_rc.update_layout(
                    plot_bgcolor="#1e1e2e", paper_bgcolor="#181825",
                    font=dict(color="#cdd6f4", size=10),
                    xaxis=dict(tickangle=-35, gridcolor="#313244"),
                    yaxis=dict(gridcolor="#313244", title="Days"),
                    legend=dict(bgcolor="#1e1e2e", bordercolor="#313244"),
                    margin=dict(l=10,r=10,t=30,b=100), height=320,
                    barmode="group",
                )
                st.plotly_chart(fig_rc, use_container_width=True)
                st.dataframe(repo_cycle, use_container_width=True, height=280)
        else:
            st.info("No PR cycle time data available.")

    # ── TAB 5: Attention Required ─────────────────────────
    with tab_alert:
        if not issues.empty:
            atabs = st.tabs(["🔴 Stale >90d","⚡ High Comments","🏷️ No Labels","🆕 Today","🔁 Reopened"])

            with atabs[0]:
                df = issues[(issues["state"]=="open") & (issues["days_since_update"]>90)].sort_values("days_since_update", ascending=False)
                if df.empty: st.success("✅ No issues stale >90 days!")
                else:
                    cols = [c for c in ["repository","issue_number","title","author","days_since_update","age_days","issue_url"] if c in df.columns]
                    st.dataframe(df[cols].head(50), use_container_width=True, height=360,
                                 column_config={"issue_url": st.column_config.LinkColumn("Link")})
                    st.caption(f"{len(df):,} issues stale 90+ days")

            with atabs[1]:
                if "comments" in issues.columns:
                    df2 = issues[issues["state"]=="open"].sort_values("comments", ascending=False).head(50)
                    cols2 = [c for c in ["repository","issue_number","title","author","comments","age_days","issue_url"] if c in df2.columns]
                    st.dataframe(df2[cols2], use_container_width=True, height=360,
                                 column_config={"issue_url": st.column_config.LinkColumn("Link")})

            with atabs[2]:
                df3 = issues[(issues["state"]=="open") & (issues["labels"].fillna("")=="")].sort_values("age_days", ascending=False)
                if df3.empty: st.success("✅ All open issues have labels!")
                else:
                    cols3 = [c for c in ["repository","issue_number","title","author","age_days","issue_url"] if c in df3.columns]
                    st.dataframe(df3[cols3].head(50), use_container_width=True, height=360,
                                 column_config={"issue_url": st.column_config.LinkColumn("Link")})
                    st.caption(f"{len(df3):,} open issues have no labels")

            with atabs[3]:
                today = date.today()
                df4 = issues[issues["created_date"]==today] if "created_date" in issues.columns else pd.DataFrame()
                if df4.empty: st.info("No new issues opened today.")
                else:
                    cols4 = [c for c in ["repository","issue_number","title","state","author","labels","issue_url"] if c in df4.columns]
                    st.dataframe(df4[cols4], use_container_width=True, height=360,
                                 column_config={"issue_url": st.column_config.LinkColumn("Link")})
                    st.caption(f"{len(df4):,} issues opened today")

            with atabs[4]:
                # Reopened issues heuristic: closed but updated recently
                if "days_since_update" in issues.columns and "age_days" in issues.columns:
                    df5 = issues[
                        (issues["state"]=="open") &
                        (issues["age_days"] > 7) &
                        (issues["days_since_update"] < 3)
                    ].sort_values("days_since_update")
                    if df5.empty: st.success("✅ No recently re-activated issues found.")
                    else:
                        cols5 = [c for c in ["repository","issue_number","title","author","age_days","days_since_update","issue_url"] if c in df5.columns]
                        st.dataframe(df5[cols5].head(50), use_container_width=True, height=360,
                                     column_config={"issue_url": st.column_config.LinkColumn("Link")})
                        st.caption(f"{len(df5):,} issues re-activated in last 3 days")
                else:
                    st.info("Insufficient data for reopened issue detection.")

    # ── TAB 6: Burndown ───────────────────────────────────
    with tab_burn:
        st.markdown("<div class='section-header'>🔥 Cumulative Burndown View</div>", unsafe_allow_html=True)
        st.caption("Cumulative issues opened vs closed over time — gap = current open backlog")

        if not issues.empty and "created_date" in issues.columns:
            issues_sorted = issues.sort_values("created_date").copy()
            issues_sorted["created_date"] = pd.to_datetime(issues_sorted["created_date"])
            daily_open   = issues_sorted.groupby("created_date").size().cumsum()

            closed_df = issues_sorted[issues_sorted["state"]=="closed"]
            if not closed_df.empty:
                daily_closed = closed_df.groupby("created_date").size().cumsum()
            else:
                daily_closed = pd.Series(dtype=int)

            fig_burn = go.Figure()
            fig_burn.add_trace(go.Scatter(
                x=daily_open.index, y=daily_open.values,
                name="Cumulative Opened", fill="tozeroy",
                line=dict(color="#f38ba8", width=2),
                fillcolor="#f38ba820",
            ))
            if not daily_closed.empty:
                fig_burn.add_trace(go.Scatter(
                    x=daily_closed.index, y=daily_closed.values,
                    name="Cumulative Closed", fill="tozeroy",
                    line=dict(color="#a6e3a1", width=2),
                    fillcolor="#a6e3a130",
                ))

            fig_burn.update_layout(
                title="Cumulative Issues: Opened vs Closed",
                plot_bgcolor="#1e1e2e", paper_bgcolor="#181825",
                font=dict(color="#cdd6f4", size=11),
                xaxis=dict(gridcolor="#313244", title="Date"),
                yaxis=dict(gridcolor="#313244", title="Cumulative Count"),
                legend=dict(bgcolor="#1e1e2e", bordercolor="#313244"),
                margin=dict(l=10,r=10,t=50,b=30), height=380,
                hovermode="x unified",
            )
            st.plotly_chart(fig_burn, use_container_width=True)

            # Backlog by repo
            if "repository" in issues.columns:
                st.markdown("<div class='section-header'>📦 Open Backlog by Repository</div>", unsafe_allow_html=True)
                backlog = (
                    issues[issues["state"]=="open"]
                    .groupby("repository").size()
                    .reset_index(name="Open_Backlog")
                    .sort_values("Open_Backlog", ascending=True)
                    .tail(15)
                )
                fig_bl = go.Figure(go.Bar(
                    x=backlog["Open_Backlog"], y=backlog["repository"],
                    orientation="h",
                    marker=dict(
                        color=backlog["Open_Backlog"],
                        colorscale=[[0,"#a6e3a1"],[0.5,"#f9e2af"],[1,"#f38ba8"]],
                        showscale=True,
                        colorbar=dict(title="Issues", tickfont=dict(color="#6c7086")),
                    ),
                    text=backlog["Open_Backlog"], textposition="outside",
                ))
                fig_bl.update_layout(
                    plot_bgcolor="#1e1e2e", paper_bgcolor="#181825",
                    font=dict(color="#cdd6f4", size=10),
                    xaxis=dict(gridcolor="#313244", title="Open Issues"),
                    yaxis=dict(gridcolor="#313244"),
                    margin=dict(l=10,r=80,t=20,b=20), height=380,
                )
                st.plotly_chart(fig_bl, use_container_width=True)
        else:
            st.info("No issue data available for burndown chart.")

    # ── Export Insights PDF ───────────────────────────────
    st.markdown("<div class='gradient-divider'></div>", unsafe_allow_html=True)
    st.markdown(
        "<div style='background:#1e1e2e;border:1px solid #7c3aed;border-radius:12px;"
        "padding:16px 20px;margin-top:8px'>"
        "<div style='font-size:1rem;font-weight:700;color:#cba6f7;margin-bottom:10px'>"
        "📄 Export Full Insights PDF</div>",
        unsafe_allow_html=True,
    )
    if st.button("🖨️ Generate Insights PDF", key="insights_pdf_btn"):
        try:
            from utils.report_gen import REPORTLAB_OK, generate_pdf
            from utils.metrics import issue_metrics
            if not REPORTLAB_OK:
                st.error("❌ reportlab not installed.")
            else:
                with st.spinner("Generating PDF…"):
                    pdf_bytes = generate_pdf(
                        metrics=m, issues=issues, prs=prs,
                        contributors=cs, repo_summary=rs,
                        report_type="Insights",
                    )
                st.download_button("⬇️ Download Insights PDF", data=pdf_bytes,
                    file_name=f"insights_{date.today()}.pdf", mime="application/pdf")
                st.success("✅ PDF ready!")
        except Exception as e:
            st.error(f"❌ Error: {e}")
    st.markdown("</div>", unsafe_allow_html=True)
