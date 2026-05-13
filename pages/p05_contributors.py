import plotly.express as px
import streamlit as st

from utils.data_loader import load_contributors, load_issues, load_prs
from utils.filters import apply_issue_filters, apply_pr_filters
from utils.metrics import contributor_summary
from utils import charts
from utils.exports import download_csv_button, download_excel_button


def render():
    st.markdown("<div class='page-header'>👤 Contributors</div>", unsafe_allow_html=True)
    st.markdown("<div class='page-sub'>Who's driving engineering activity across the organisation</div>",
                unsafe_allow_html=True)

    f      = st.session_state.get("filters", {})
    issues = apply_issue_filters(load_issues(), f)
    prs    = apply_pr_filters(load_prs(), f)
    raw_c  = load_contributors()

    if issues.empty:
        st.markdown(
            """<div class='info-card' style='border-color:rgba(220,38,38,0.3)'>
                <div style='font-size:1rem;font-weight:700;color:#dc2626;margin-bottom:6px'>⚠️ No Data</div>
                <div style='font-size:0.85rem;color:#6b7280'>No data available — click <b>🔄 Refresh Data</b> in the sidebar.</div>
            </div>""",
            unsafe_allow_html=True,
        )
        return

    cs = contributor_summary(issues, prs)

    # ── KPI row ────────────────────────────────────────────
    st.markdown("<div class='kpi-group'>👤 Team Summary</div>", unsafe_allow_html=True)
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("👤 Contributors",     len(cs))
    k2.metric("🏆 Top Contributor",  cs.iloc[0]["Author"] if not cs.empty else "—")
    k3.metric("📋 Avg Issues/Author", round(cs["Issues_Opened"].mean(), 1) if not cs.empty else 0)
    k4.metric("📦 Avg Repos/Author",  round(cs["Repos_Active"].mean(), 1) if not cs.empty else 0)

    st.markdown("<div class='gradient-divider'></div>", unsafe_allow_html=True)

    # ── Charts ─────────────────────────────────────────────
    st.markdown("<div class='section-header'>📊 Contributor Activity</div>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(charts.contributor_bar(cs), use_container_width=True)
    with col2:
        st.plotly_chart(charts.contributor_repos_scatter(cs), use_container_width=True)

    st.markdown("<div class='gradient-divider'></div>", unsafe_allow_html=True)

    # ── Leaderboard table ──────────────────────────────────
    st.markdown("<div class='section-header'>🏆 Contributor Leaderboard</div>", unsafe_allow_html=True)

    c1, c2, _, c3 = st.columns([1, 1, 2, 3])
    download_csv_button(c1, cs, "contributors.csv")
    download_excel_button(c2, {"Contributors": cs}, "contributors.xlsx")
    with c3:
        q = st.text_input("🔍 Search contributor", key="contrib_search", placeholder="GitHub username…")
    if q:
        cs = cs[cs["Author"].str.contains(q, case=False, na=False)]

    st.caption(f"**{len(cs):,}** contributors found")
    st.dataframe(cs, use_container_width=True, height=460)

    # ── Drill-down by contributor ──────────────────────────
    if not raw_c.empty and "author" in raw_c.columns:
        st.markdown("<div class='gradient-divider'></div>", unsafe_allow_html=True)
        st.markdown("<div class='section-header'>🔍 Contributor Drill-Down</div>", unsafe_allow_html=True)

        all_cs = contributor_summary(load_issues(), load_prs())
        selected = st.selectbox(
            "Select contributor",
            options=all_cs["Author"].tolist()[:40],
            key="contrib_drill",
        )
        if selected:
            cr = raw_c[raw_c["author"] == selected][["repository", "contributions"]]
            cr = cr.sort_values("contributions", ascending=False)

            total_contrib = int(cr["contributions"].sum())
            st.markdown(
                f"<div class='info-card'>"
                f"<span style='font-weight:700;color:#7c3aed'>{selected}</span> "
                f"— <b>{total_contrib:,}</b> total contributions across "
                f"<b>{len(cr)}</b> repositories"
                f"</div>",
                unsafe_allow_html=True,
            )

            c1, c2 = st.columns([2, 3])
            with c1:
                st.dataframe(cr, use_container_width=True, height=320)
            with c2:
                fig = px.bar(
                    cr.head(20), x="contributions", y="repository",
                    orientation="h", color="contributions",
                    color_continuous_scale=["#ede9fe", "#7c3aed", "#4f46e5"],
                    title=f"{selected} — contributions by repository",
                )
                fig.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font_color="#1e1b2e",
                    font_family="Inter, Segoe UI, sans-serif",
                    margin=dict(l=0, r=0, t=36, b=0),
                    yaxis={"categoryorder": "total ascending"},
                    coloraxis_showscale=False,
                )
                fig.update_xaxes(gridcolor="rgba(229,231,239,0.9)", tickfont=dict(color="#6b7280"))
                fig.update_yaxes(gridcolor="rgba(229,231,239,0.9)", tickfont=dict(color="#6b7280"))
                st.plotly_chart(fig, use_container_width=True)
