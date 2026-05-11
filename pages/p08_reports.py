import calendar
from datetime import date, timedelta

import pandas as pd
import streamlit as st

from utils.data_loader import load_issues, load_prs, load_releases
from utils.filters import apply_issue_filters, apply_pr_filters
from utils.metrics import contributor_summary, issue_metrics, repo_summary
from utils.exports import download_csv_button, download_excel_button


def _date_filter(df: pd.DataFrame, start: date, end: date, col: str = "created_date") -> pd.DataFrame:
    if df.empty or col not in df.columns:
        return df
    return df[(df[col] >= start) & (df[col] <= end)]


def render():
    st.markdown("<div class='page-header'>📊 Reports</div>", unsafe_allow_html=True)
    st.markdown("<div class='page-sub'>Generate PDF reports and export data for any date range</div>", unsafe_allow_html=True)

    f        = st.session_state.get("filters", {})
    issues   = apply_issue_filters(load_issues(), f)
    prs      = apply_pr_filters(load_prs(), f)
    releases = load_releases()

    st.markdown("<div class='section-header'>📅 Report Configuration</div>", unsafe_allow_html=True)

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
            sel_date = st.date_input("Select Day", value=today, key="rpt_day")
            start, end = sel_date, sel_date
        elif report_type == "Weekly":
            week_start = today - timedelta(days=today.weekday())
            start      = st.date_input("Week start", value=week_start, key="rpt_wk")
            end        = start + timedelta(days=6)
            st.caption(f"Week: {start} → {end}")
        elif report_type == "Monthly":
            month_start = today.replace(day=1)
            sel_month   = st.date_input("Month start", value=month_start, key="rpt_mo")
            start       = sel_month.replace(day=1)
            last_day    = calendar.monthrange(start.year, start.month)[1]
            end         = start.replace(day=last_day)
            st.caption(f"Month: {start} → {end}")
        else:
            dr    = st.date_input("Date Range", value=[today - timedelta(days=30), today], key="rpt_dr")
            start, end = (dr[0], dr[1]) if len(dr) == 2 else (today - timedelta(days=30), today)
    with col3:
        repo_opts = (
            ["All repositories"] + sorted(issues["repository"].unique().tolist())
            if not issues.empty else ["All repositories"]
        )
        by_repo = st.selectbox("Filter by Repo", repo_opts, key="rpt_repo")

    ri = _date_filter(issues, start, end)
    rp = _date_filter(prs, start, end)
    if by_repo != "All repositories":
        ri = ri[ri["repository"] == by_repo]
        rp = rp[rp["repository"] == by_repo]

    st.markdown("---")
    st.markdown(f"<div class='section-header'>Summary: {start} → {end}</div>", unsafe_allow_html=True)
    m = issue_metrics(ri, rp, releases)

    k1, k2, k3, k4, k5, k6 = st.columns(6)
    k1.metric("Issues Opened",  len(ri[ri["state"] != "closed"]) if not ri.empty else 0)
    k2.metric("Issues Closed",  len(ri[ri["state"] == "closed"]) if not ri.empty else 0)
    k3.metric("PRs Opened",     len(rp))
    k4.metric("PRs Merged",     int(rp["merged"].sum()) if not rp.empty and "merged" in rp.columns else 0)
    k5.metric("Contributors",   m["contributors"])
    k6.metric("Closure Rate",   f"{m['closure_rate']}%")

    st.markdown("---")
    st.markdown("<div class='section-header'>Day-by-Day Activity</div>", unsafe_allow_html=True)

    daily_i = (
        ri.groupby("created_date").agg(
            Issues_Opened  = ("issue_number", "count"),
            Issues_Closed  = ("state",        lambda x: (x == "closed").sum()),
            Comments       = ("comments",     "sum"),
            Contributors   = ("author",       "nunique"),
        ).reset_index().rename(columns={"created_date": "Date"})
        if not ri.empty else pd.DataFrame()
    )
    daily_p = (
        rp.groupby("created_date").agg(PRs_Opened=("pr_number", "count"))
        .reset_index().rename(columns={"created_date": "Date"})
        if not rp.empty else pd.DataFrame()
    )

    if not daily_i.empty and not daily_p.empty:
        daily = daily_i.merge(daily_p, on="Date", how="outer").fillna(0).sort_values("Date", ascending=False)
    elif not daily_i.empty:
        daily = daily_i.sort_values("Date", ascending=False)
    else:
        daily = pd.DataFrame()

    if not daily.empty:
        st.dataframe(daily, width="stretch", height=300)
        exp1, exp2, _ = st.columns([1, 1, 5])
        download_csv_button(exp1, daily, f"daily_{start}_{end}.csv")
        download_excel_button(
            exp2,
            {"Daily Activity": daily, "Issues": ri, "PRs": rp},
            f"report_{start}_{end}.xlsx",
        )
    else:
        st.info("No activity in this date range.")

    st.markdown("---")

    tab1, tab2, tab3 = st.tabs(["🐞 Issues", "🔀 Pull Requests", "👤 Contributors"])

    with tab1:
        if ri.empty:
            st.info("No issues in this period.")
        else:
            icols = [c for c in ["repository", "issue_number", "title", "state", "author",
                                  "labels", "comments", "age_days", "issue_url"] if c in ri.columns]
            st.dataframe(ri[icols], width="stretch", height=380,
                         column_config={"issue_url": st.column_config.LinkColumn("Link")})

    with tab2:
        if rp.empty:
            st.info("No PRs in this period.")
        else:
            pcols = [c for c in ["repository", "pr_number", "title", "state", "author",
                                  "merged", "cycle_time_days", "pr_url"] if c in rp.columns]
            st.dataframe(rp[pcols], width="stretch", height=380,
                         column_config={"pr_url": st.column_config.LinkColumn("Link")})

    with tab3:
        cs = contributor_summary(ri, rp)
        if cs.empty:
            st.info("No contributor activity in this period.")
        else:
            st.dataframe(cs, width="stretch", height=380)

    st.markdown("---")
    st.markdown("<div class='section-header'>📄 Generate PDF Report</div>", unsafe_allow_html=True)

    pdf_col1, pdf_col2 = st.columns([2, 4])
    with pdf_col1:
        include_repos   = st.checkbox("Include repository summary",   value=True)
        include_contrib = st.checkbox("Include contributor analytics", value=True)
    with pdf_col2:
        st.info(
            "The PDF includes: KPI summary, repository metrics, issues table, "
            "PR summary, and contributor analytics for the selected period."
        )

    if st.button("🖨️ Generate PDF Report", type="primary"):
        try:
            from utils.report_gen import REPORTLAB_OK, generate_pdf
            if not REPORTLAB_OK:
                st.error("❌ `reportlab` is not installed. Run: `pip install reportlab`")
            else:
                with st.spinner("Generating PDF…"):
                    rs  = repo_summary(ri, rp)     if include_repos   else pd.DataFrame()
                    cs2 = contributor_summary(ri, rp) if include_contrib else pd.DataFrame()
                    pdf_bytes = generate_pdf(
                        metrics       = m,
                        issues        = ri,
                        prs           = rp,
                        contributors  = cs2,
                        repo_summary  = rs,
                        report_type   = report_type,
                        selected_date = start if report_type == "Daily" else None,
                        date_range    = (start, end),
                    )
                fname = f"report_{report_type.lower()}_{start}_{end}.pdf"
                st.download_button(
                    label="⬇️ Download PDF",
                    data=pdf_bytes,
                    file_name=fname,
                    mime="application/pdf",
                )
                st.success(f"✅ PDF ready: {fname}")
        except Exception as e:
            st.error(f"❌ PDF generation failed: {e}")
