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
    if df.empty or col not in df.columns: return df
    return df[(df[col] >= start) & (df[col] <= end)]


def render():
    st.markdown("<div class='page-header'>📊 Reports & Exports</div>", unsafe_allow_html=True)
    st.markdown("<div class='page-sub'>Generate professional PDF reports · Export data to CSV / Excel</div>", unsafe_allow_html=True)

    f        = st.session_state.get("filters", {})
    issues   = apply_issue_filters(load_issues(), f)
    prs      = apply_pr_filters(load_prs(), f)
    releases = load_releases()

    # ── Configuration Card ────────────────────────────────
    st.markdown("<div class='section-header'>📅 Report Configuration</div>", unsafe_allow_html=True)
    with st.container():
        c1, c2, c3 = st.columns([2, 3, 2])
        with c1:
            report_type = st.selectbox("Report Type", ["Daily", "Weekly", "Monthly", "Custom Range"], key="rpt_type")
        with c2:
            today = date.today()
            if report_type == "Daily":
                sel_date = st.date_input("Select Day", value=today, key="rpt_day")
                start, end = sel_date, sel_date
            elif report_type == "Weekly":
                week_start = today - timedelta(days=today.weekday())
                start = st.date_input("Week start", value=week_start, key="rpt_wk")
                end = start + timedelta(days=6)
                st.caption(f"Selected: {start} to {end}")
            elif report_type == "Monthly":
                month_start = today.replace(day=1)
                sel_month = st.date_input("Month start", value=month_start, key="rpt_mo")
                start = sel_month.replace(day=1)
                last_day = calendar.monthrange(start.year, start.month)[1]
                end = start.replace(day=last_day)
                st.caption(f"Selected: {calendar.month_name[start.month]} {start.year}")
            else:
                dr = st.date_input("Date Range", value=[today - timedelta(days=30), today], key="rpt_dr")
                start, end = (dr[0], dr[1]) if len(dr) == 2 else (today - timedelta(days=30), today)
        with c3:
            repo_opts = ["All repositories"] + sorted(issues["repository"].unique().tolist()) if not issues.empty else ["All repositories"]
            by_repo = st.selectbox("Scope", repo_opts, key="rpt_repo")

    # Filter data for the report
    ri = _date_filter(issues, start, end)
    rp = _date_filter(prs,    start, end)
    if by_repo != "All repositories":
        ri = ri[ri["repository"] == by_repo]
        rp = rp[rp["repository"] == by_repo]

    st.markdown("<div class='gradient-divider'></div>", unsafe_allow_html=True)

    # ── Period Summary ─────────────────────────────────────
    m = issue_metrics(ri, rp, releases)
    st.markdown(f"<div class='section-header'>📊 Period Summary: {start} to {end}</div>", unsafe_allow_html=True)

    k1, k2, k3, k4, k5, k6 = st.columns(6)
    open_cnt   = int((ri["state"] != "closed").sum()) if not ri.empty else 0
    closed_cnt = int((ri["state"] == "closed").sum()) if not ri.empty else 0
    merged_cnt = int(rp["merged"].sum()) if not rp.empty and "merged" in rp.columns else 0
    k1.metric("Issues Opened", open_cnt)
    k2.metric("Issues Closed", closed_cnt)
    k3.metric("PRs Opened",    len(rp))
    k4.metric("PRs Merged",    merged_cnt)
    k5.metric("Contributors",  m["contributors"])
    k6.metric("Closure Rate",  f"{m['closure_rate']}%")

    st.markdown("<div class='gradient-divider'></div>", unsafe_allow_html=True)

    # ── Exports ───────────────────────────────────────────
    tab1, tab2, tab3 = st.tabs(["📄 PDF Generator", "📂 Raw Data Explorer", "📊 Period Trends"])

    with tab1:
        st.markdown("<div class='accent-card'>"
                    "<div style='font-size:1.1rem;font-weight:700;color:#f46800;margin-bottom:8px'>Professional PDF Generation</div>"
                    "<div style='font-size:0.85rem;color:#9fa7b3;margin-bottom:15px'>Create a branded, data-rich report for the selected period.</div>", unsafe_allow_html=True)
        
        c_opt, c_info = st.columns([2, 4])
        with c_opt:
            include_repos   = st.checkbox("📦 Repository summary", value=True)
            include_contrib = st.checkbox("👤 Team analytics", value=True)
            include_charts  = st.checkbox("📊 Embedded charts", value=True)
            
            if st.button("🖨️ Generate PDF Report", type="primary", use_container_width=True):
                try:
                    from utils.report_gen import REPORTLAB_OK, generate_pdf
                    if not REPORTLAB_OK: st.error("❌ reportlab missing.")
                    else:
                        with st.spinner("Compiling Grafana-style PDF…"):
                            rs2 = repo_summary(ri, rp) if include_repos else pd.DataFrame()
                            cs2 = contributor_summary(ri, rp) if include_contrib else pd.DataFrame()
                            pdf_bytes = generate_pdf(m, ri, rp, cs2, rs2, report_type, 
                                                     start if report_type == "Daily" else None, (start, end))
                            st.download_button("⬇️ Download PDF", pdf_bytes, 
                                               f"report_{start}_{end}.pdf", "application/pdf")
                except Exception as e: st.error(f"Failed: {e}")
        
        with c_info:
            st.markdown("""<div style='background:#111217;border-radius:4px;padding:15px;font-size:0.8rem;color:#6e7077;line-height:1.8;border:1px solid #2c3235'>
                ✅ Grafana-inspired dark theme<br>
                ✅ Executive KPI grid & Branded cover<br>
                ✅ Health scores (A-F grading)<br>
                ✅ Embedded Matplotlib high-contrast charts
            </div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with tab2:
        st.markdown("<div class='section-header'>📋 Issue & PR Tables</div>", unsafe_allow_html=True)
        c1, c2, _ = st.columns([1,1,4])
        download_csv_button(c1, ri, f"issues_{start}_{end}.csv")
        download_excel_button(c2, {"Issues": ri, "PRs": rp}, f"data_{start}_{end}.xlsx")
        
        t1, t2 = st.tabs(["Issues", "PRs"])
        with t1: st.dataframe(ri, use_container_width=True, height=350)
        with t2: st.dataframe(rp, use_container_width=True, height=350)

    with tab3:
        st.markdown("<div class='section-header'>📈 Activity Pulse</div>", unsafe_allow_html=True)
        st.plotly_chart(charts.engineering_activity_timeline(ri, rp), use_container_width=True)
