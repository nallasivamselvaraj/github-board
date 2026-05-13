import importlib
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

# ════════════════════════════════════════════════
# SIDEBAR
# ════════════════════════════════════════════════

# ── Brand header ──────────────────────────────
st.sidebar.markdown(
    """<div class='sidebar-brand'>
        <div class='sidebar-brand-icon'>🚀</div>
        <div class='sidebar-brand-name'>Engineering Intelligence</div>
        <div class='sidebar-brand-sub'>Simtestlab · GitHub Analytics</div>
    </div>""",
    unsafe_allow_html=True,
)

# ── Navigation ────────────────────────────────
st.sidebar.markdown(
    "<div class='nav-section'>Navigation</div>",
    unsafe_allow_html=True,
)
page = st.sidebar.radio("nav", PAGES, label_visibility="collapsed", key="nav_radio")

# ── Data controls ─────────────────────────────
st.sidebar.markdown(
    "<div class='sidebar-section-divider'></div>"
    "<div class='nav-section'>Data Controls</div>",
    unsafe_allow_html=True,
)

if st.sidebar.button("🔄 Refresh Data", use_container_width=True, key="btn_refresh"):
    with st.sidebar.status("Fetching from GitHub API…", expanded=True):
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
                st.sidebar.error(f"❌ {result.stderr[:200]}")
        except Exception as e:
            st.sidebar.error(f"❌ {e}")

if st.sidebar.button("🗑️ Clear Cache", use_container_width=True, key="btn_cache"):
    st.cache_data.clear()
    st.rerun()

# ── Filters ───────────────────────────────────
st.sidebar.markdown(
    "<div class='sidebar-section-divider'></div>"
    "<div class='nav-section'>Filters</div>",
    unsafe_allow_html=True,
)
if not issues.empty:
    filters = build_sidebar_filters(issues, prs)
    st.session_state["filters"] = filters
else:
    st.session_state["filters"] = {}
    st.sidebar.markdown(
        "<div class='sidebar-empty-msg'>No data yet.<br>Click 🔄 Refresh Data above.</div>",
        unsafe_allow_html=True,
    )

# ── Footer ────────────────────────────────────
lbl = latest_file_label()
st.sidebar.markdown(
    f"""<div class='sidebar-footer'>
        <span class='data-pill'>🕐 {lbl}</span>
        <div class='sidebar-footer-ver'>v2.0 · Simtestlab Analytics</div>
    </div>""",
    unsafe_allow_html=True,
)

# ════════════════════════════════════════════════
# PAGE ROUTING
# ════════════════════════════════════════════════
_page_map = {
    "🏠 Executive Dashboard":  "pages.p01_dashboard",
    "📦 Repositories":         "pages.p02_repositories",
    "🐞 Issues":               "pages.p03_issues",
    "🔀 Pull Requests":        "pages.p04_pull_requests",
    "👤 Contributors":         "pages.p05_contributors",
    "📡 Activity Feed":        "pages.p06_activity",
    "⏳ Staleness":            "pages.p07_staleness",
    "📊 Reports":              "pages.p08_reports",
    "🎯 Insights":             "pages.p09_insights",
}
mod_name = _page_map.get(page, "pages.p01_dashboard")
pg = importlib.import_module(mod_name)
pg.render()
