import pandas as pd
import streamlit as st

from utils.data_loader import load_prs
from utils.filters import apply_pr_filters
from utils import charts
from utils.exports import download_csv_button, download_excel_button

_DISPLAY = [
    "repository", "pr_number", "title", "state", "author",
    "draft", "merged", "labels", "comments", "commits",
    "additions", "deletions", "changed_files",
    "cycle_time_days", "age_days", "created_at", "pr_url",
]

_COL_CFG = {
    "pr_url":          st.column_config.LinkColumn("Link"),
    "age_days":        st.column_config.NumberColumn("Age (days)"),
    "cycle_time_days": st.column_config.NumberColumn("Cycle (days)"),
    "additions":       st.column_config.NumberColumn("➕"),
    "deletions":       st.column_config.NumberColumn("➖"),
    "comments":        st.column_config.NumberColumn("💬"),
}


def _table(df: pd.DataFrame, key_prefix: str, filename: str):
    if df.empty:
        st.info(f"No {filename.replace('_', ' ')} in current filter.")
        return
    cols = [c for c in _DISPLAY if c in df.columns]
    exp1, exp2, _, sq = st.columns([1, 1, 2, 3])
    download_csv_button(exp1, df[cols], f"{filename}.csv")
    download_excel_button(exp2, {filename: df[cols]}, f"{filename}.xlsx")
    with sq:
        q = st.text_input("🔍 Filter", key=f"prq_{key_prefix}")
    if q:
        mask = (
            df["title"].str.contains(q, case=False, na=False)
            | df["author"].str.contains(q, case=False, na=False)
        )
        df = df[mask]

    PAGE  = 25
    total = max(1, (len(df) - 1) // PAGE + 1)
    pg    = st.number_input("Page", 1, total, 1, key=f"prp_{key_prefix}")
    st.dataframe(
        df.iloc[(pg - 1) * PAGE : pg * PAGE][cols],
        column_config=_COL_CFG,
        width="stretch",
        height=480,
    )
    st.caption(f"{len(df):,} pull requests · page {pg}/{total}")


def render():
    st.markdown("<div class='page-header'>🔀 Pull Request Dashboard</div>", unsafe_allow_html=True)
    st.markdown("<div class='page-sub'>Open, closed, draft, merged, and review-pending PRs</div>", unsafe_allow_html=True)

    f   = st.session_state.get("filters", {})
    prs = apply_pr_filters(load_prs(), f)

    if prs.empty:
        st.info("No PR data found. Click **🔄 Refresh GitHub Data** in the sidebar.")
        return

    has_draft  = "draft"  in prs.columns
    has_merged = "merged" in prs.columns

    open_prs   = prs[prs["state"] == "open"]
    closed_prs = prs[prs["state"] == "closed"]
    draft_prs  = prs[prs["draft"]  == True]  if has_draft  else pd.DataFrame(columns=prs.columns)
    merged_prs = prs[prs["merged"] == True]  if has_merged else pd.DataFrame(columns=prs.columns)
    review_prs = prs[(prs["state"] == "open") & (~prs["draft"])] if has_draft else open_prs

    avg_cyc = round(prs["cycle_time_days"].dropna().mean(), 1) if "cycle_time_days" in prs.columns else "—"

    k1, k2, k3, k4, k5, k6 = st.columns(6)
    k1.metric("Total PRs",   len(prs))
    k2.metric("🟢 Open",     len(open_prs))
    k3.metric("✅ Closed",   len(closed_prs))
    k4.metric("🟣 Merged",   len(merged_prs))
    k5.metric("📝 Draft",    len(draft_prs))
    k6.metric("⏱ Avg Cycle", f"{avg_cyc}d")

    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(charts.pr_state_pie(prs), width="stretch")
    with col2:
        st.plotly_chart(charts.pr_repo_bar(prs), width="stretch")

    col3, col4 = st.columns(2)
    with col3:
        st.plotly_chart(charts.pr_trend(prs), width="stretch")
    with col4:
        st.plotly_chart(charts.pr_cycle_hist(prs), width="stretch")

    st.markdown("---")

    tabs = st.tabs([
        f"🟢 Open ({len(open_prs)})",
        f"✅ Closed ({len(closed_prs)})",
        f"📝 Draft ({len(draft_prs)})",
        f"🟣 Merged ({len(merged_prs)})",
        f"👁 Review Pending ({len(review_prs)})",
    ])

    with tabs[0]: _table(open_prs,   "open",   "open_prs")
    with tabs[1]: _table(closed_prs, "closed", "closed_prs")
    with tabs[2]: _table(draft_prs,  "draft",  "draft_prs")
    with tabs[3]: _table(merged_prs, "merged", "merged_prs")
    with tabs[4]:
        st.info("Open PRs not in draft — awaiting review.")
        _table(review_prs, "review", "review_prs")
