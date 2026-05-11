import plotly.express as px
import streamlit as st

from utils.data_loader import load_contributors, load_issues, load_prs
from utils.filters import apply_issue_filters, apply_pr_filters
from utils.metrics import contributor_summary
from utils import charts
from utils.exports import download_csv_button, download_excel_button


def render():
    st.markdown("<div class='page-header'>👤 Contributors</div>", unsafe_allow_html=True)
    st.markdown("<div class='page-sub'>Who's driving engineering activity across the organisation</div>", unsafe_allow_html=True)

    f      = st.session_state.get("filters", {})
    issues = apply_issue_filters(load_issues(), f)
    prs    = apply_pr_filters(load_prs(), f)
    raw_c  = load_contributors()

    if issues.empty:
        st.warning("No data available. Click **🔄 Refresh GitHub Data** in the sidebar.")
        return

    cs = contributor_summary(issues, prs)

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("👤 Total Contributors", len(cs))
    k2.metric("🏆 Top Contributor",    cs.iloc[0]["Author"] if not cs.empty else "—")
    k3.metric("📋 Avg Issues/Author",  round(cs["Issues_Opened"].mean(), 1) if not cs.empty else 0)
    k4.metric("📦 Avg Repos/Author",   round(cs["Repos_Active"].mean(), 1) if not cs.empty else 0)

    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(charts.contributor_bar(cs), width="stretch")
    with col2:
        st.plotly_chart(charts.contributor_repos_scatter(cs), width="stretch")

    st.markdown("---")
    st.markdown("<div class='section-header'>Contributor Leaderboard</div>", unsafe_allow_html=True)

    exp1, exp2, _, sq = st.columns([1, 1, 2, 3])
    download_csv_button(exp1, cs, "contributors.csv")
    download_excel_button(exp2, {"Contributors": cs}, "contributors.xlsx")
    with sq:
        q = st.text_input("🔍 Search contributor", key="contrib_search")
    if q:
        cs = cs[cs["Author"].str.contains(q, case=False, na=False)]

    st.dataframe(cs, width="stretch", height=480)

    if not raw_c.empty and "author" in raw_c.columns:
        st.markdown("---")
        st.markdown("<div class='section-header'>Contribution Counts by Repository</div>", unsafe_allow_html=True)
        selected = st.selectbox(
            "Drill down by contributor",
            options=cs["Author"].tolist()[:40],
            key="contrib_drill",
        )
        if selected:
            cr = raw_c[raw_c["author"] == selected][["repository", "contributions"]]
            cr = cr.sort_values("contributions", ascending=False)
            c1, c2 = st.columns([2, 3])
            with c1:
                st.dataframe(cr, width="stretch", height=320)
            with c2:
                fig = px.bar(
                    cr.head(20), x="contributions", y="repository",
                    orientation="h", color="contributions",
                    color_continuous_scale="Teal",
                    title=f"{selected} — commits by repo",
                )
                fig.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font_color="#cdd6f4",
                    margin=dict(l=0, r=0, t=36, b=0),
                    yaxis={"categoryorder": "total ascending"},
                )
                st.plotly_chart(fig, width="stretch")
