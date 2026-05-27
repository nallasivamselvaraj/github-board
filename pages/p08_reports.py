import calendar
from datetime import date, timedelta
import pandas as pd
import streamlit as st

from utils.data_loader import load_issues, load_prs, load_releases
from utils.filters import apply_issue_filters, apply_pr_filters
from utils.metrics import contributor_summary, issue_metrics, repo_summary
from utils.exports import download_csv_button, download_excel_button
from utils import charts


def _date_filter(df: pd.DataFrame, start: date, end: date, col="created_date") -> pd.DataFrame:
    if df.empty or col not in df.columns:
        return df
    mask = (df[col] >= start) & (df[col] <= end)
    return df[mask]


def render():
    st.markdown("<div class='page-header'>📊 Reports & Exports</div>", unsafe_allow_html=True)
    st.markdown("<div class='page-sub'>Generate professional PDF reports · Export data to CSV / Excel</div>", unsafe_allow_html=True)

    f   = st.session_state.get("filters", {})
    raw = load_issues()
    if not raw.empty:
        raw["commented"] = raw["comments"] > 0
        # Derive closed_date from closed_at for period-based closed filtering
        if "closed_at" in raw.columns:
            raw = raw.copy()
            raw["closed_date"] = raw["closed_at"].dt.date

    # Strip sidebar date_range — report period supersedes it so ri_updated
    # correctly captures issues created before the sidebar range but updated today.
    f_no_date = {k: v for k, v in f.items() if k != "date_range"}
    issues   = apply_issue_filters(raw, f_no_date)
    prs      = apply_pr_filters(load_prs(), f_no_date)
    releases = load_releases()

    # ── Configuration Card ────────────────────────────────────
    st.markdown("<div class='section-header'>📅 Report Configuration</div>", unsafe_allow_html=True)
    with st.container():
        c1, c2, c3 = st.columns([2, 3, 2])
        with c1:
            report_type = st.selectbox(
                "Report Type", ["Daily", "Weekly", "Monthly", "Custom Range"], key="rpt_type"
            )
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
            repo_opts = (
                ["All repositories"] + sorted(issues["repository"].unique().tolist())
                if not issues.empty else ["All repositories"]
            )
            by_repo = st.selectbox("Scope", repo_opts, key="rpt_repo")

    # ── Period-filtered datasets ──────────────────────────────
    ri        = _date_filter(issues, start, end, col="created_date")   # opened in period
    ri_closed = _date_filter(issues, start, end, col="closed_date")    # closed in period
    ri_updated = _date_filter(issues, start, end, col="updated_date")  # any activity in period
    rp        = _date_filter(prs, start, end)

    if by_repo != "All repositories":
        ri         = ri[ri["repository"] == by_repo]         if not ri.empty         else ri
        ri_closed  = ri_closed[ri_closed["repository"] == by_repo]  if not ri_closed.empty  else ri_closed
        ri_updated = ri_updated[ri_updated["repository"] == by_repo] if not ri_updated.empty else ri_updated
        rp         = rp[rp["repository"] == by_repo]         if not rp.empty         else rp

    st.markdown("<div class='gradient-divider'></div>", unsafe_allow_html=True)

    # ── Period Summary ────────────────────────────────────────
    st.markdown(
        f"<div class='section-header'>📊 Period Summary: {start} to {end}</div>",
        unsafe_allow_html=True,
    )

    opened_cnt  = len(ri)
    closed_cnt  = len(ri_closed)
    updated_cnt = len(ri_updated)
    merged_cnt  = int(rp["merged"].sum()) if not rp.empty and "merged" in rp.columns else 0

    # Unique authors across all period activity
    _period_authors: set = set()
    for _df in [ri, ri_closed, ri_updated, rp]:
        if not _df.empty and "author" in _df.columns:
            _period_authors |= set(_df["author"].dropna())
    period_contrib = len(_period_authors)

    total_activity = opened_cnt + closed_cnt
    closure_rate = round(closed_cnt / total_activity * 100, 1) if total_activity else 0

    # Stale = open issues in the scoped dataset not updated in 30+ days
    _scope_issues = issues[issues["repository"] == by_repo] if by_repo != "All repositories" else issues
    _scope_stale  = int(
        ((_scope_issues["state"] == "open") & (_scope_issues["days_since_update"] > 30)).sum()
    ) if not _scope_issues.empty else 0

    k1, k2, k3, k4, k5, k6, k7 = st.columns(7)
    k1.metric("Issues Opened",    opened_cnt)
    k2.metric("Issues Closed",    closed_cnt)
    k3.metric("Issues Updated",   updated_cnt)
    k4.metric("PRs Opened",       len(rp))
    k5.metric("PRs Merged",       merged_cnt)
    k6.metric("Contributors",     period_contrib)
    k7.metric("Closure Rate",     f"{closure_rate}%")

    # Metrics dict for PDF KPI grid
    period_metrics = {
        "opened_issues":  opened_cnt,
        "closed_issues":  closed_cnt,
        "updated_issues": updated_cnt,
        "total_prs":      len(rp),
        "merged_prs":     merged_cnt,
        "contributors":   period_contrib,
    }

    m = issue_metrics(ri, rp, releases)  # kept for repo_summary / contributor_summary callers

    st.markdown("<div class='gradient-divider'></div>", unsafe_allow_html=True)

    # ── Exports ──────────────────────────────────────────────
    tab1, tab2, tab3 = st.tabs(["📄 PDF Generator", "📂 Raw Data Explorer", "📊 Period Trends"])

    with tab1:
        st.markdown(
            "<div class='accent-card'>"
            "<div style='font-size:1.1rem;font-weight:700;color:#f46800;margin-bottom:8px'>Professional PDF Generation</div>"
            "<div style='font-size:0.85rem;color:#9fa7b3;margin-bottom:15px'>Create a branded, data-rich report for the selected period.</div>",
            unsafe_allow_html=True,
        )

        c_opt, c_info = st.columns([2, 4])
        with c_opt:
            include_repos   = st.checkbox("📦 Repository summary", value=True)
            include_contrib = st.checkbox("👤 Team analytics",      value=True)
            include_charts  = st.checkbox("📊 Embedded charts",     value=True)

            if st.button("🖨️ Generate PDF Report", type="primary", use_container_width=True):
                try:
                    from utils.report_gen import REPORTLAB_OK, generate_pdf
                    if not REPORTLAB_OK:
                        st.error("❌ reportlab missing — install with: pip install reportlab")
                    else:
                        with st.spinner("Compiling professional PDF…"):
                            # Use ri_updated as fallback so repo/contrib tables populate
                            # even when no issues were created in the period
                            _base = ri if not ri.empty else ri_updated
                            rs2 = repo_summary(_base, rp)     if include_repos   else pd.DataFrame()
                            cs2 = contributor_summary(_base, rp) if include_contrib else pd.DataFrame()

                            if report_type == "Daily":
                                period_label = start.strftime("%B %d, %Y")
                            else:
                                period_label = f"{start.strftime('%b %d, %Y')}  –  {end.strftime('%b %d, %Y')}"
                            scope_label = by_repo if by_repo != "All repositories" else "All Repositories"

                            pdf_bytes = generate_pdf(
                                period_metrics, ri, rp, cs2, rs2, report_type,
                                start if report_type == "Daily" else None,
                                (start, end),
                                issues_updated=ri_updated,
                                issues_closed=ri_closed,
                                period_label=period_label,
                                scope_label=scope_label,
                            )
                            st.download_button(
                                "⬇️ Download PDF", pdf_bytes,
                                f"report_{start}_{end}.pdf", "application/pdf",
                            )
                except Exception as e:
                    st.error(f"Failed: {e}")

        with c_info:
            st.markdown(
                """<div style='background:#f7f8fa;border-radius:4px;padding:15px;font-size:0.8rem;color:#718096;line-height:1.8;border:1px solid #d8dce0'>
                ✅ Issues Opened · Closed · Updated sections<br>
                ✅ Accurate period-based metrics (not state snapshots)<br>
                ✅ State-colored tables with contributor analytics<br>
                ✅ Embedded Matplotlib charts · Repository health
            </div>""",
                unsafe_allow_html=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)

    with tab2:
        st.markdown("<div class='section-header'>📋 Issue & PR Tables</div>", unsafe_allow_html=True)
        c1, c2, _ = st.columns([1, 1, 4])
        download_csv_button(c1, ri, f"issues_opened_{start}_{end}.csv")
        download_excel_button(
            c2,
            {"Opened": ri, "Closed": ri_closed, "Updated": ri_updated, "PRs": rp},
            f"data_{start}_{end}.xlsx",
        )

        _upd_cols = [c for c in [
            "repository", "issue_number", "title", "state", "author",
            "labels", "commented", "updated_date", "age_days", "issue_url",
        ] if c in ri_updated.columns]

        t1, t2, t3, t4 = st.tabs([
            f"Opened ({len(ri):,})",
            f"Closed ({len(ri_closed):,})",
            f"Updated ({len(ri_updated):,})",
            "PRs",
        ])
        with t1:
            st.caption("Issues created during this period.")
            st.dataframe(ri, use_container_width=True, height=350)
        with t2:
            st.caption("Issues whose closed_at date falls within this period.")
            st.dataframe(ri_closed, use_container_width=True, height=350)
        with t3:
            st.caption("Issues with any activity (comment, label, status change) during this period.")
            if not ri_updated.empty and "commented" not in ri_updated.columns:
                ri_updated["commented"] = ri_updated["comments"] > 0
            st.dataframe(
                ri_updated[_upd_cols] if _upd_cols else ri_updated,
                column_config={
                    "issue_url":    st.column_config.LinkColumn("Link", display_text="Open ↗"),
                    "issue_number": st.column_config.NumberColumn("#"),
                    "updated_date": st.column_config.DateColumn("Updated On"),
                    "age_days":     st.column_config.NumberColumn("Age (days)", format="%d d"),
                    "commented":    st.column_config.CheckboxColumn("💬 Commented"),
                },
                use_container_width=True,
                height=350,
            )
        with t4:
            st.dataframe(rp, use_container_width=True, height=350)

    with tab3:
        st.markdown("<div class='section-header'>📈 Activity Pulse</div>", unsafe_allow_html=True)
        st.plotly_chart(charts.engineering_activity_timeline(ri, rp), use_container_width=True)
