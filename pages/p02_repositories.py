import plotly.express as px
import streamlit as st

from utils.data_loader import load_issues, load_prs, load_releases, load_repo_meta
from utils.filters import apply_issue_filters, apply_pr_filters, apply_repo_filters
from utils.metrics import repo_summary
from utils import charts
from utils.exports import download_csv_button, download_excel_button


def render():
    st.markdown("<div class='page-header'>📦 Repository Analytics</div>", unsafe_allow_html=True)
    st.markdown("<div class='page-sub'>Health, activity, and metrics for every repository</div>",
                unsafe_allow_html=True)

    f        = st.session_state.get("filters", {})
    issues   = apply_issue_filters(load_issues(), f)
    prs      = apply_pr_filters(load_prs(), f)
    releases = load_releases()
    meta     = apply_repo_filters(load_repo_meta(), f)

    if issues.empty:
        st.markdown(
            """<div class='info-card' style='border-color:rgba(220,38,38,0.3)'>
                <div style='font-size:1rem;font-weight:700;color:#dc2626;margin-bottom:6px'>⚠️ No Data</div>
                <div style='font-size:0.85rem;color:#6b7280'>No data available — click <b>🔄 Refresh Data</b> in the sidebar.</div>
            </div>""",
            unsafe_allow_html=True,
        )
        return

    rs = repo_summary(issues, prs)

    if not meta.empty:
        meta_slim = meta[["name", "language", "stars", "forks",
                           "updated_date", "repo_url", "description"]].rename(
            columns={"name": "Repository"}
        )
        rs = rs.merge(meta_slim, on="Repository", how="left")

    if not releases.empty:
        rel_counts = releases.groupby("repository").size().reset_index(name="Releases")
        rel_counts.rename(columns={"repository": "Repository"}, inplace=True)
        rs = rs.merge(rel_counts, on="Repository", how="left")
        rs["Releases"] = rs["Releases"].fillna(0).astype(int)

    # ── KPI row ────────────────────────────────────────────
    st.markdown("<div class='kpi-group'>📦 Repository Overview</div>", unsafe_allow_html=True)
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("📦 Repositories",   len(rs))
    k2.metric("⭐ Total Stars",    int(rs["stars"].sum()) if "stars" in rs.columns else "—")
    k3.metric("🔀 Total Forks",    int(rs["forks"].sum()) if "forks" in rs.columns else "—")
    k4.metric("🏷️ Total Releases", int(rs["Releases"].sum()) if "Releases" in rs.columns else "—")

    st.markdown("<div class='gradient-divider'></div>", unsafe_allow_html=True)

    # ── Search + Sort controls ─────────────────────────────
    st.markdown("<div class='section-header'>📋 Repository Table</div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([3, 2, 1])
    with c1:
        search = st.text_input("🔍 Search repository", key="repo_search", placeholder="Name or description…")
    with c2:
        sort_by = st.selectbox(
            "Sort by",
            [c for c in ["Total_Issues", "Open_Issues", "Closure_Rate%", "stars", "forks", "Releases", "Repository"]
             if c in rs.columns],
            key="repo_sort",
        )
    with c3:
        asc = st.checkbox("Ascending", value=False, key="repo_asc")

    if search:
        mask = rs["Repository"].str.contains(search, case=False, na=False)
        if "description" in rs.columns:
            mask |= rs["description"].fillna("").str.contains(search, case=False, na=False)
        rs = rs[mask]

    if sort_by in rs.columns:
        rs = rs.sort_values(sort_by, ascending=asc)

    PAGE_SIZE   = 20
    total_pages = max(1, (len(rs) - 1) // PAGE_SIZE + 1)
    left, right = st.columns([6, 1])
    with right:
        page_num = st.number_input("Page", 1, total_pages, 1, key="repo_page", label_visibility="collapsed")
    with left:
        st.caption(f"Showing **{len(rs):,}** repositories · page {page_num}/{total_pages}")

    page_df   = rs.iloc[(page_num - 1) * PAGE_SIZE: page_num * PAGE_SIZE]
    show_cols = [c for c in [
        "Repository", "language", "stars", "forks",
        "Total_Issues", "Open_Issues", "Closed_Issues", "Closure_Rate%",
        "Total_PRs", "Releases", "Contributors", "Avg_Age_Days",
        "updated_date", "repo_url",
    ] if c in rs.columns]

    col_config = {}
    if "repo_url" in rs.columns:
        col_config["repo_url"] = st.column_config.LinkColumn("GitHub ↗", display_text="Open ↗")
    if "stars" in rs.columns:
        col_config["stars"] = st.column_config.NumberColumn("⭐ Stars")
    if "forks" in rs.columns:
        col_config["forks"] = st.column_config.NumberColumn("🔀 Forks")

    st.dataframe(page_df[show_cols], column_config=col_config, use_container_width=True, height=460)

    exp1, exp2, _ = st.columns([1, 1, 4])
    download_csv_button(exp1, rs[show_cols], "repositories.csv")
    download_excel_button(exp2, {"Repositories": rs[show_cols]}, "repositories.xlsx")

    st.markdown("<div class='gradient-divider'></div>", unsafe_allow_html=True)

    # ── Charts ─────────────────────────────────────────────
    st.markdown("<div class='section-header'>📊 Repository Charts</div>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(charts.repo_stacked_bar(rs), use_container_width=True)
    with col2:
        st.plotly_chart(charts.top_repos_bar(issues), use_container_width=True)

    st.plotly_chart(charts.issue_velocity(issues), use_container_width=True)

    if "language" in rs.columns:
        st.markdown("<div class='gradient-divider'></div>", unsafe_allow_html=True)
        st.markdown("<div class='section-header'>🌐 Language Breakdown</div>", unsafe_allow_html=True)
        lang = rs["language"].fillna("Unknown").value_counts().reset_index()
        lang.columns = ["Language", "Repos"]
        fig_lang = px.pie(
            lang.head(12), names="Language", values="Repos",
            title="Repositories by Language",
            color_discrete_sequence=["#7c3aed","#3b82f6","#10b981","#f59e0b",
                                     "#ec4899","#06b6d4","#84cc16","#f97316",
                                     "#8b5cf6","#14b8a6","#ef4444","#a3e635"],
        )
        fig_lang.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#1e1b2e",
            font_family="Inter, Segoe UI, sans-serif",
            margin=dict(l=0, r=0, t=36, b=0),
            legend=dict(bgcolor="rgba(255,255,255,0.8)", bordercolor="#e5e7ef", borderwidth=1),
        )
        st.plotly_chart(fig_lang, use_container_width=True)
