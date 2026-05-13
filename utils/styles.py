import streamlit as st

# ── Grafana-inspired Light Design System ──────────────────
# Colors: #ffffff bg · #f7f8fa panel · #d8dce0 border
# Accent: #f46800 orange · #1f60c4 blue
# Status: #36a347 green · #c4162a red · #e0b400 yellow

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

/* ── Kill Streamlit chrome ───────────────────────────── */
[data-testid="stSidebarNav"],#MainMenu,footer { display:none !important; }
header[data-testid="stHeader"] { background:transparent !important; height:0 !important; }

/* ── Global background ───────────────────────────────── */
html,body,[data-testid="stAppViewContainer"] {
    background:#ffffff !important;
}
[data-testid="stMain"] { background:#ffffff; }
body,.stMarkdown,.stText {
    font-family:'Inter','Segoe UI',system-ui,sans-serif;
    color:#24292e;
}

/* ── Content container ───────────────────────────────── */
.block-container {
    padding:1.5rem 2.5rem 3rem !important;
    max-width:1600px;
    position:relative;
    z-index:1;
}

/* ══════════════════════════════════════════════════════
   METRIC CARDS — Grafana panel style (Light)
   Fixed "Overlays": increased padding and removed absolute overlap
══════════════════════════════════════════════════════ */
[data-testid="metric-container"] {
    background:#f7f8fa;
    border:1px solid #d8dce0;
    border-radius:2px;
    padding:20px 22px 18px !important;
    position:relative;
    overflow:hidden;
    transition:border-color .2s,box-shadow .2s;
    display: flex;
    flex-direction: column;
}
[data-testid="metric-container"]:hover {
    border-color:#f46800;
    box-shadow:0 2px 12px rgba(0,0,0,0.06);
}
/* Orange left bar - using a safer position to avoid text overlay */
[data-testid="metric-container"]::before {
    content:'';
    position:absolute;
    left:0;top:0;bottom:0;
    width:4px;
    background:#f46800;
    z-index: 2;
}
[data-testid="metric-container"] label {
    color:#1f60c4 !important;
    font-size:0.72rem !important;
    font-weight:700 !important;
    letter-spacing:.08em;
    text-transform:uppercase;
    font-family:'JetBrains Mono',monospace !important;
    margin-bottom: 8px !important;
    z-index: 3;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    font-size:2.2rem !important;
    font-weight:700 !important;
    color:#24292e !important;
    line-height:1;
    font-family:'JetBrains Mono',monospace !important;
    letter-spacing:-0.02em;
    z-index: 3;
}
[data-testid="metric-container"] [data-testid="stMetricDelta"] {
    font-size:0.8rem !important;
    font-family:'JetBrains Mono',monospace !important;
    margin-top: 4px !important;
}

/* ══════════════════════════════════════════════════════
   SIDEBAR — Grafana Light Nav
   Fixed "Overlays": fixed label interaction and spacing
══════════════════════════════════════════════════════ */
[data-testid="stSidebar"] {
    background:#f7f8fa !important;
    border-right:1px solid #d8dce0 !important;
    box-shadow:none;
}
[data-testid="stSidebar"] > div:first-child { padding-top:0; }

/* Nav pills - Radio button replacement */
[data-testid="stSidebar"] [data-testid="stRadio"] > div {
    gap:2px !important;
    padding:0 8px;
}
[data-testid="stSidebar"] [data-testid="stRadio"] label {
    font-size:0.88rem;
    color:#4a5568;
    padding:10px 16px !important;
    border-radius:3px;
    transition:background .15s,color .15s;
    font-weight:500;
    cursor:pointer;
    display:flex;
    align-items:center;
    gap:10px;
    line-height:1.4;
    margin:2px 0 !important;
    letter-spacing:.01em;
    border: 1px solid transparent;
}
[data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
    background:rgba(244,104,0,0.06);
    color:#f46800;
}
/* Selected state for radio labels */
[data-testid="stSidebar"] [data-testid="stRadio"] [aria-checked="true"] + div label,
[data-testid="stSidebar"] [data-testid="stRadio"] [aria-checked="true"] ~ div label {
    color:#f46800 !important;
    background:#ffffff !important;
    border-color: #d8dce0 !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    font-weight:600;
}

/* Hide the actual radio circle and its default label */
[data-testid="stSidebar"] [data-testid="stRadio"] [data-testid="stWidgetLabel"] { display:none; }
[data-testid="stSidebar"] [data-testid="stRadio"] input[type=radio] { display:none !important; }

/* Sidebar buttons */
[data-testid="stSidebar"] .stButton > button {
    width:100%;
    border-radius:3px;
    font-size:0.85rem;
    font-weight:600;
    padding:10px 16px;
    margin-bottom:6px;
    text-align:left;
    font-family:'Inter',sans-serif;
    border: 1px solid #d8dce0;
    background: #ffffff;
    color: #4a5568;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background:rgba(244,104,0,0.06);
    border-color:#f46800;
    color:#f46800;
}

/* ══════════════════════════════════════════════════════
   TABS — Grafana light tab bar
══════════════════════════════════════════════════════ */
[data-testid="stTabs"] [data-baseweb="tab-list"] {
    background:#f7f8fa;
    gap:0;
    border-bottom:1px solid #d8dce0;
    padding:0 12px;
    border-radius:4px 4px 0 0;
}
[data-testid="stTabs"] button[data-baseweb="tab"] {
    font-size:0.85rem;
    font-weight:500;
    color:#4a5568;
    background:transparent;
    border-radius:0;
    padding:12px 20px;
    border:none;
    border-bottom:2px solid transparent;
    transition:all .15s;
    letter-spacing:.01em;
}
[data-testid="stTabs"] button[data-baseweb="tab"]:hover {
    color:#24292e;
    background:rgba(0,0,0,0.03);
}
[data-testid="stTabs"] button[data-baseweb="tab"][aria-selected="true"] {
    color:#f46800 !important;
    background:transparent !important;
    border-bottom-color:#f46800 !important;
    font-weight:600 !important;
}
[data-testid="stTabs"] [data-baseweb="tab-panel"] {
    background:#ffffff;
    border:1px solid #d8dce0;
    border-top:none;
    border-radius:0 0 4px 4px;
    padding:20px 15px;
}

/* ══════════════════════════════════════════════════════
   DATAFRAME — Professional table style
══════════════════════════════════════════════════════ */
[data-testid="stDataFrame"] {
    border:1px solid #d8dce0 !important;
    border-radius:3px !important;
}
[data-testid="stDataFrame"] thead th {
    background:#f7f8fa !important;
    color:#4a5568 !important;
    font-size:0.75rem !important;
    font-weight:700 !important;
    letter-spacing:.06em;
    text-transform:uppercase;
    border-bottom:1px solid #d8dce0 !important;
}

/* ══════════════════════════════════════════════════════
   CUSTOM COMPONENTS
══════════════════════════════════════════════════════ */
.page-header {
    font-size:1.8rem;
    font-weight:800;
    color:#24292e;
    letter-spacing:-0.02em;
    margin-bottom:4px;
}
.page-sub {
    font-size:0.88rem;
    color:#718096;
    margin-bottom:24px;
}
.section-header {
    font-size:0.82rem;
    font-weight:700;
    color:#4a5568;
    padding:0 0 8px 12px;
    border-left:3px solid #f46800;
    border-bottom:1px solid #e2e8f0;
    margin-bottom:16px;
    letter-spacing:.04em;
    text-transform:uppercase;
}
.kpi-group {
    font-size:0.65rem;
    color:#718096;
    text-transform:uppercase;
    letter-spacing:.12em;
    font-weight:700;
    margin-bottom:8px;
    font-family:'JetBrains Mono',monospace;
}

/* Grafana panel card */
.info-card {
    background:#ffffff;
    border:1px solid #d8dce0;
    border-radius:4px;
    padding:20px 24px;
    margin-bottom:15px;
    position:relative;
    box-shadow: 0 1px 3px rgba(0,0,0,0.02);
}
.info-card::before {
    content:'';position:absolute;top:0;left:0;right:0;height:3px;
    background:linear-gradient(90deg,#f46800,#1f60c4);
}

.gradient-divider {
    height:1px;
    background:linear-gradient(90deg,#e2e8f0,#cbd5e0,transparent);
    margin:20px 0;
    border:none;
}

/* Sidebar brand */
.sidebar-brand {
    background:#ffffff;
    border-bottom:1px solid #d8dce0;
    padding:24px 20px 20px;
    margin-bottom:10px;
}
.sidebar-brand-name {
    font-size:1rem;font-weight:800;color:#24292e;
    letter-spacing:-0.01em;margin-top:10px;
}
.sidebar-brand-sub {
    font-size:0.68rem;color:#718096;margin-top:3px;text-transform:uppercase;letter-spacing:.05em;
}

.nav-section {
    font-size:0.6rem;
    font-weight:800;
    color:#a0aec0;
    text-transform:uppercase;
    letter-spacing:.15em;
    padding:16px 20px 6px;
}

.sidebar-footer {
    padding:15px 20px;
    border-top:1px solid #d8dce0;
    margin-top:10px;
}
.sidebar-footer-ver {
    font-size:0.65rem;
    color:#718096;
    margin-top:8px;
}

/* Feed */
.feed-item {
    display:flex;gap:14px;padding:12px 14px;
    border-bottom:1px solid #f7f8fa;
    align-items:flex-start;
}
.feed-item:hover { background:#f9fafb; }
.feed-title { font-size:0.85rem;color:#2d3748;font-weight:600; }
.feed-meta  { font-size:0.75rem;color:#718096;margin-top:3px;font-family:'JetBrains Mono',monospace; }

/* Status badges */
.badge-open    { background:rgba(196,22,42,0.1);color:#c4162a;padding:2px 8px;border-radius:2px;font-size:.7rem;font-weight:700;border:1px solid rgba(196,22,42,0.2); }
.badge-closed  { background:rgba(54,163,71,0.1);color:#36a347;padding:2px 8px;border-radius:2px;font-size:.7rem;font-weight:700;border:1px solid rgba(54,163,71,0.2); }

/* Fix generic Streamlit gaps */
[data-testid="stHorizontalBlock"] { gap:16px !important; }

/* Kill focus rings on generic elements to look cleaner */
*:focus { outline:none !important; }

</style>
"""

def inject_css():
    st.markdown(CSS, unsafe_allow_html=True)
