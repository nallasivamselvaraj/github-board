import os
import subprocess
import sys

import streamlit as st

ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from config import PAGES
from utils.data_loader import load_issues, load_prs, latest_file_label
from utils.filters import build_sidebar_filters
from utils.styles import inject_css

st.set_page_config(
    page_title="Engineering Intelligence · Simtestlab",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)
inject_css()

issues = load_issues()
prs    = load_prs()

# ── Sidebar brand ─────────────────────────────────────────
st.sidebar.markdown(
    "<div class='sidebar-brand'>"
    "<div class='sidebar-brand-icon'>🚀</div>"
    "<div class='sidebar-brand-name'>Engineering Intelligence</div>"
    "<div class='sidebar-brand-sub'>Simtestlab · GitHub Analytics</div>"
    "</div>",
    unsafe_allow_html=True,
)

st.sidebar.markdown("<div class='nav-section'>Navigation</div>", unsafe_allow_html=True)
page = st.sidebar.radio("Navigation", PAGES, label_visibility="collapsed")

st.sidebar.markdown("---")

# ── Data refresh ──────────────────────────────────────────
col_a, col_b = st.sidebar.columns(2)
with col_a:
    if st.button("🔄 Refresh Data", use_container_width=True):
        with st.spinner("Fetching data from GitHub API…"):
            try:
                result = subprocess.run(
                    [sys.executable, os.path.join(ROOT, "github_org.py")],
                    capture_output=True, text=True, cwd=ROOT,
                )
                if result.returncode == 0:
                    st.cache_data.clear()
                    st.sidebar.success("✅ Data refreshed!")
                    st.rerun()
                else:
                    st.sidebar.error(f"❌ Failed:\n{result.stderr[:300]}")
            except Exception as e:
                st.sidebar.error(f"❌ Error: {e}")
with col_b:
    if st.button("🗑️ Clear Cache", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# ── Global filters ────────────────────────────────────────
st.sidebar.markdown("<div class='nav-section'>Filters</div>", unsafe_allow_html=True)
if not issues.empty:
    filters = build_sidebar_filters(issues, prs)
    st.session_state["filters"] = filters
else:
    st.session_state["filters"] = {}

st.sidebar.markdown("---")
# Last fetched timestamp pill
lbl = latest_file_label()
st.sidebar.markdown(
    f"<div style='text-align:center;padding:4px 0'>"
    f"<span class='data-pill'>🕐 {lbl}</span>"
    f"</div>",
    unsafe_allow_html=True,
)

# ── Page routing ──────────────────────────────────────────
if page == "🏠 Executive Dashboard":
    from pages import p01_dashboard as pg
elif page == "📦 Repositories":
    from pages import p02_repositories as pg
elif page == "🐞 Issues":
    from pages import p03_issues as pg
elif page == "🔀 Pull Requests":
    from pages import p04_pull_requests as pg
elif page == "👤 Contributors":
    from pages import p05_contributors as pg
elif page == "📡 Activity Feed":
    from pages import p06_activity as pg
elif page == "⏳ Staleness":
    from pages import p07_staleness as pg
elif page == "📊 Reports":
    from pages import p08_reports as pg
elif page == "🎯 Insights":
    from pages import p09_insights as pg
else:
    from pages import p01_dashboard as pg

pg.render()
