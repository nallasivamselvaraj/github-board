import plotly.express as px
import streamlit as st

from utils.data_loader import load_issues, load_prs, load_releases, load_repo_meta
from utils.filters import apply_issue_filters, apply_pr_filters, apply_repo_filters
from utils.metrics import repo_summary
from utils import charts
from utils.exports import download_csv_button, download_excel_button


def render():
    st.markdown("<div class='page-header'>📦 Repository Analytics</div>", unsafe_allow_html=True)
    st.markdown("<div class='page-sub'>Health, activity, and metrics for every repository</div>", unsafe_allow_html=True)

    f        = st.session_state.get("filters", {})
    issues   = apply_issue_filters(load_issues(), f)
    prs      = apply_pr_filters(load_prs(), f)
    releases = load_releases()
    meta     = apply_repo_filters(load_repo_meta(), f)

    if issues.empty:
        st.warning("No data available. Click **🔄 Refresh GitHub Data** in the sidebar.")
        return

    st.markdown("<div class='section-header'>Repository Summary</div>", unsafe_allow_html=True)

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

    search_col, sort_col, order_col = st.columns([3, 2, 1])
    with search_col:
        search = st.text_input("🔍 Search repository", key="repo_search")
    with sort_col:
        sort_by = st.selectbox(
            "Sort by",
            ["Total_Issues", "Open_Issues", "Closure_Rate%", "stars", "forks", "Releases", "Repository"],
            key="repo_sort",
        )
    with order_col:
        asc = st.checkbox("Asc", value=False, key="repo_asc")

    if search:
        mask = rs["Repository"].str.contains(search, case=False, na=False)
        if "description" in rs.columns:
            mask |= rs["description"].str.contains(search, case=False, na=False)
        rs = rs[mask]

    if sort_by in rs.columns:
        rs = rs.sort_values(sort_by, ascending=asc)

    PAGE_SIZE   = 20
    total_pages = max(1, (len(rs) - 1) // PAGE_SIZE + 1)
    page_num    = st.number_input("Page", min_value=1, max_value=total_pages, value=1, step=1, key="repo_page")
    page_df     = rs.iloc[(page_num - 1) * PAGE_SIZE : page_num * PAGE_SIZE]

    show_cols = [c for c in [
        "Repository", "language", "stars", "forks",
        "Total_Issues", "Open_Issues", "Closed_Issues", "Closure_Rate%",
        "Total_PRs", "Releases", "Contributors", "Avg_Age_Days",
        "updated_date", "repo_url",
    ] if c in rs.columns]

    col_config = {}
    if "repo_url" in rs.columns:
        col_config["repo_url"] = st.column_config.LinkColumn("GitHub Link")

    st.dataframe(page_df[show_cols], column_config=col_config, width="stretch", height=460)
    st.caption(f"Page {page_num} of {total_pages} · {len(rs)} repositories")

    exp1, exp2, _ = st.columns([1, 1, 4])
    download_csv_button(exp1, rs[show_cols], "repositories.csv")
    download_excel_button(exp2, {"Repositories": rs[show_cols]}, "repositories.xlsx")

    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(charts.repo_stacked_bar(rs), width="stretch")
    with col2:
        st.plotly_chart(charts.top_repos_bar(issues), width="stretch")

    st.plotly_chart(charts.issue_velocity(issues), width="stretch")

    if "language" in rs.columns:
        st.markdown("<div class='section-header'>Language Breakdown</div>", unsafe_allow_html=True)
        lang = rs["language"].fillna("Unknown").value_counts().reset_index()
        lang.columns = ["Language", "Repos"]
        fig_lang = px.pie(
            lang.head(12), names="Language", values="Repos",
            title="Repositories by Language",
            color_discrete_sequence=px.colors.qualitative.Pastel,
        )
        fig_lang.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#cdd6f4",
            margin=dict(l=0, r=0, t=36, b=0),
        )
        st.plotly_chart(fig_lang, width="stretch")
