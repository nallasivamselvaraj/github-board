# pages/p08_reports.py  –  Professional Reports page
import calendar
from datetime import date, timedelta

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils.data_loader import load_issues, load_prs, load_releases
from utils.filters import apply_issue_filters, apply_pr_filters
from utils.metrics import contributor_summary, issue_metrics, repo_summary
from utils.exports import download_csv_button, download_excel_button


def _date_filter(df: pd.DataFrame, start: date, end: date, col="created_date") -> pd.DataFrame:
    if df.empty or col not in df.columns:
        return df
    return df[(df[col] >= start) & (df[col] <= end)]


def _kpi_delta(val, ref=None, fmt=None):
    """Return formatted value; optionally compute delta."""
    if fmt:
        return fmt(val), None
    return val, None


def render():
    st.markdown("<div class='page-header'>📊 Reports & Exports</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='page-sub'>Generate professional PDF reports · Export data to CSV / Excel</div>",
        unsafe_allow_html=True,
    )

    f       = st.session_state.get("filters", {})
    issues  = apply_issue_filters(load_issues(), f)
    prs     = apply_pr_filters(load_prs(), f)
    releases = load_releases()

    # ── Report configuration card ─────────────────────────
    st.markdown(
        """<div style='background:#1e1e2e;border:1px solid #313244;border-radius:12px;
                      padding:20px 24px 16px;margin-bottom:18px'>
            <div style='font-size:1.05rem;font-weight:700;color:#cba6f7;margin-bottom:14px'>
                📅 Report Configuration
            </div>""",
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns([2, 3, 2])
    with col1:
        report_type = st.selectbox(
            "Report Type",
            ["Daily", "Weekly", "Monthly", "Custom Range"],
            key="rpt_type",
        )
    with col2:
        today = date.today()
        if report_type == "Daily":
            sel_date    = st.date_input("Select Day", value=today, key="rpt_day")
            start, end  = sel_date, sel_date
        elif report_type == "Weekly":
            week_start  = today - timedelta(days=today.weekday())
            start       = st.date_input("Week start", value=week_start, key="rpt_wk")
            end         = start + timedelta(days=6)
            st.caption(f"📅 Week: {start} → {end}")
        elif report_type == "Monthly":
            month_start = today.replace(day=1)
            sel_month   = st.date_input("Month start", value=month_start, key="rpt_mo")
            start       = sel_month.replace(day=1)
            last_day    = calendar.monthrange(start.year, start.month)[1]
            end         = start.replace(day=last_day)
            st.caption(f"📅 Month: {start} → {end}")
        else:
            dr          = st.date_input("Date Range", value=[today - timedelta(days=30), today], key="rpt_dr")
            start, end  = (dr[0], dr[1]) if len(dr) == 2 else (today - timedelta(days=30), today)
    with col3:
        repo_opts = (
            ["All repositories"] + sorted(issues["repository"].unique().tolist())
            if not issues.empty else ["All repositories"]
        )
        by_repo = st.selectbox("Filter by Repo", repo_opts, key="rpt_repo")

    st.markdown("</div>", unsafe_allow_html=True)

    # Filter
    ri = _date_filter(issues, start, end)
    rp = _date_filter(prs,    start, end)
    if by_repo != "All repositories":
        ri = ri[ri["repository"] == by_repo]
        rp = rp[rp["repository"] == by_repo]

    # ── Period KPIs ───────────────────────────────────────
    m = issue_metrics(ri, rp, releases)
    st.markdown(f"<div class='section-header'>📈 Period Summary: {start} → {end}</div>", unsafe_allow_html=True)

    k1,k2,k3,k4,k5,k6 = st.columns(6)
    open_cnt   = int((ri["state"] != "closed").sum()) if not ri.empty else 0
    closed_cnt = int((ri["state"] == "closed").sum()) if not ri.empty else 0
    merged_cnt = int(rp["merged"].sum()) if not rp.empty and "merged" in rp.columns else 0
    k1.metric("Issues Opened",  open_cnt)
    k2.metric("Issues Closed",  closed_cnt)
    k3.metric("PRs Opened",     len(rp))
    k4.metric("PRs Merged",     merged_cnt)
    k5.metric("Contributors",   m["contributors"])
    k6.metric("Closure Rate",   f"{m['closure_rate']}%")

    # ── Activity trend chart ───────────────────────────────
    st.markdown("<div class='section-header'>📉 Day-by-Day Activity</div>", unsafe_allow_html=True)

    daily_i = (
        ri.groupby("created_date").agg(
            Issues_Opened=("issue_number", "count"),
            Issues_Closed=("state", lambda x: (x == "closed").sum()),
            Comments=("comments", "sum"),
            Contributors=("author", "nunique"),
        ).reset_index().rename(columns={"created_date": "Date"})
        if not ri.empty else pd.DataFrame()
    )
    daily_p = (
        rp.groupby("created_date").agg(PRs_Opened=("pr_number", "count"))
        .reset_index().rename(columns={"created_date": "Date"})
        if not rp.empty else pd.DataFrame()
    )

    if not daily_i.empty and not daily_p.empty:
        daily = daily_i.merge(daily_p, on="Date", how="outer").fillna(0).sort_values("Date")
    elif not daily_i.empty:
        daily = daily_i.sort_values("Date")
    else:
        daily = pd.DataFrame()

    if not daily.empty:
        fig = go.Figure()
        if "Issues_Opened" in daily.columns:
            fig.add_trace(go.Scatter(x=daily["Date"], y=daily["Issues_Opened"],
                name="Issues Opened", mode="lines+markers",
                line=dict(color="#f38ba8", width=2),
                marker=dict(size=5)))
        if "Issues_Closed" in daily.columns:
            fig.add_trace(go.Scatter(x=daily["Date"], y=daily["Issues_Closed"],
                name="Issues Closed", mode="lines+markers",
                line=dict(color="#a6e3a1", width=2),
                marker=dict(size=5)))
        if "PRs_Opened" in daily.columns:
            fig.add_trace(go.Bar(x=daily["Date"], y=daily["PRs_Opened"],
                name="PRs Opened", marker_color="#cba6f7", opacity=0.5))
        fig.update_layout(
            plot_bgcolor="#1e1e2e", paper_bgcolor="#181825",
            font=dict(color="#cdd6f4", size=11),
            legend=dict(bgcolor="#1e1e2e", bordercolor="#313244", borderwidth=1),
            margin=dict(l=10,r=10,t=30,b=10), height=280,
            xaxis=dict(gridcolor="#313244", showgrid=True),
            yaxis=dict(gridcolor="#313244", showgrid=True),
            hovermode="x unified",
        )
        st.plotly_chart(fig, use_container_width=True)

        # Export row
        exp1, exp2, _ = st.columns([1,1,6])
        download_csv_button(exp1, daily, f"daily_{start}_{end}.csv")
        download_excel_button(
            exp2,
            {"Daily Activity": daily, "Issues": ri, "PRs": rp},
            f"report_{start}_{end}.xlsx",
        )
    else:
        st.info("No activity in this date range.")

    st.markdown("<div class='gradient-divider'></div>", unsafe_allow_html=True)

    # ── Tabs ──────────────────────────────────────────────
    tab1, tab2, tab3, tab4 = st.tabs(["🐞 Issues", "🔀 Pull Requests", "👤 Contributors", "📦 Repository Breakdown"])

    with tab1:
        if ri.empty:
            st.info("No issues in this period.")
        else:
            icols = [c for c in ["repository","issue_number","title","state","author",
                                  "labels","comments","age_days","issue_url"] if c in ri.columns]
            st.dataframe(ri[icols], use_container_width=True, height=380,
                         column_config={"issue_url": st.column_config.LinkColumn("Link")})
            st.caption(f"{len(ri):,} issues in selected period")

    with tab2:
        if rp.empty:
            st.info("No PRs in this period.")
        else:
            pcols = [c for c in ["repository","pr_number","title","state","author",
                                  "merged","cycle_time_days","pr_url"] if c in rp.columns]
            st.dataframe(rp[pcols], use_container_width=True, height=380,
                         column_config={"pr_url": st.column_config.LinkColumn("Link")})
            st.caption(f"{len(rp):,} PRs in selected period")

    with tab3:
        cs = contributor_summary(ri, rp)
        if cs.empty:
            st.info("No contributor activity in this period.")
        else:
            st.dataframe(cs, use_container_width=True, height=380)

    with tab4:
        rs = repo_summary(ri, rp)
        if rs.empty:
            st.info("No repository data.")
        else:
            st.dataframe(rs, use_container_width=True, height=380)
            # mini bar chart of open issues per repo
            if "Open_Issues" in rs.columns and "Repository" in rs.columns:
                top_rs = rs.sort_values("Open_Issues", ascending=False).head(15)
                fig2 = go.Figure(go.Bar(
                    x=top_rs["Repository"], y=top_rs["Open_Issues"],
                    marker_color="#f38ba8",
                    text=top_rs["Open_Issues"], textposition="outside",
                ))
                fig2.update_layout(
                    title="Open Issues per Repository",
                    plot_bgcolor="#1e1e2e", paper_bgcolor="#181825",
                    font=dict(color="#cdd6f4", size=10),
                    margin=dict(l=10,r=10,t=40,b=100), height=320,
                    xaxis=dict(tickangle=-40, gridcolor="#313244"),
                    yaxis=dict(gridcolor="#313244"),
                )
                st.plotly_chart(fig2, use_container_width=True)

    st.markdown("<div class='gradient-divider'></div>", unsafe_allow_html=True)

    # ── PDF generation card ───────────────────────────────
    st.markdown(
        """<div style='background:#1e1e2e;border:1px solid #7c3aed;border-radius:12px;
                      padding:20px 24px;margin-bottom:18px'>
            <div style='font-size:1.05rem;font-weight:700;color:#cba6f7;margin-bottom:12px'>
                📄 Generate Professional PDF Report
            </div>""",
        unsafe_allow_html=True,
    )

    col_opt, col_info = st.columns([2, 4])
    with col_opt:
        include_repos   = st.checkbox("📦 Include repository summary",   value=True, key="pdf_repos")
        include_contrib = st.checkbox("👤 Include contributor analytics", value=True, key="pdf_contrib")
        include_charts  = st.checkbox("📊 Include embedded charts",       value=True, key="pdf_charts")
    with col_info:
        st.markdown(
            """<div style='background:#181825;border-radius:8px;padding:14px;font-size:0.83rem;
                          color:#6c7086;line-height:2'>
                ✅ &nbsp;Branded cover page with logo &amp; period details<br>
                ✅ &nbsp;Executive KPI summary grid (8 key metrics)<br>
                ✅ &nbsp;Embedded matplotlib charts (bar, pie, trend line)<br>
                ✅ &nbsp;Repository health score table (A–F grades)<br>
                ✅ &nbsp;Issues &amp; PR detail tables (top 35 rows each)<br>
                ✅ &nbsp;Page headers &amp; footers with page numbers<br>
                ✅ &nbsp;Confidentiality footer
            </div>""",
            unsafe_allow_html=True,
        )

    st.markdown("</div>", unsafe_allow_html=True)

    if st.button("🖨️ Generate PDF Report", type="primary", use_container_width=False):
        try:
            from utils.report_gen import REPORTLAB_OK, generate_pdf
            if not REPORTLAB_OK:
                st.error("❌ `reportlab` is not installed. Run: `pip install reportlab`")
            else:
                with st.spinner("Generating professional PDF…"):
                    rs2  = repo_summary(ri, rp)     if include_repos   else pd.DataFrame()
                    cs2  = contributor_summary(ri, rp) if include_contrib else pd.DataFrame()
                    pdf_bytes = generate_pdf(
                        metrics      = m,
                        issues       = ri,
                        prs          = rp,
                        contributors = cs2,
                        repo_summary = rs2,
                        report_type  = report_type,
                        selected_date= start if report_type == "Daily" else None,
                        date_range   = (start, end),
                    )
                fname = f"report_{report_type.lower()}_{start}_{end}.pdf"
                st.download_button(
                    label    = "⬇️ Download PDF",
                    data     = pdf_bytes,
                    file_name= fname,
                    mime     = "application/pdf",
                    use_container_width=False,
                )
                st.success(f"✅ PDF ready — {fname}")
        except Exception as e:
            st.error(f"❌ PDF generation failed: {e}")
            import traceback
            st.code(traceback.format_exc(), language="python")
