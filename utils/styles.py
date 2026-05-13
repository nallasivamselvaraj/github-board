import streamlit as st

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

/* ── Hide Streamlit chrome ───────────────────────── */
[data-testid="stSidebarNav"],#MainMenu,footer { display:none !important; }
header[data-testid="stHeader"] { background:transparent !important; height:0 !important; }

/* ── Global base ─────────────────────────────────── */
html,body,[data-testid="stAppViewContainer"] {
    background:#f4f6fb !important;
}
[data-testid="stMain"] { background:#f4f6fb; }
body,.stMarkdown,.stText {
    font-family:'Inter','Segoe UI',system-ui,sans-serif;
    color:#1e1b2e;
}

/* ── Subtle pattern ──────────────────────────────── */
[data-testid="stMain"]::before {
    content:'';
    position:fixed;
    inset:0;
    background-image:radial-gradient(rgba(124,58,237,0.04) 1px,transparent 1px);
    background-size:30px 30px;
    pointer-events:none;
    z-index:0;
}

/* ── Content container ───────────────────────────── */
.block-container {
    padding:1.5rem 2.5rem 3rem !important;
    max-width:1540px;
    position:relative;
    z-index:1;
}

/* ══════════════════════════════════════════════════
   METRIC CARDS
══════════════════════════════════════════════════ */
[data-testid="metric-container"] {
    background:#ffffff;
    border:1px solid #e5e7ef;
    border-radius:18px;
    padding:22px 24px 18px;
    position:relative;
    overflow:hidden;
    transition:border-color .3s,transform .25s,box-shadow .3s;
    box-shadow:0 2px 8px rgba(0,0,0,0.05);
}
[data-testid="metric-container"]:hover {
    border-color:rgba(124,58,237,0.4);
    transform:translateY(-4px);
    box-shadow:0 12px 32px rgba(124,58,237,0.1),0 2px 8px rgba(0,0,0,0.06);
}
/* Top accent bar */
[data-testid="metric-container"]::before {
    content:'';
    position:absolute;
    top:0;left:0;right:0;
    height:3px;
    background:linear-gradient(90deg,#7c3aed,#3b82f6,#10b981,#f59e0b);
    opacity:.85;
}
/* Corner glow */
[data-testid="metric-container"]::after {
    content:'';
    position:absolute;
    top:-40px;right:-40px;
    width:120px;height:120px;
    background:radial-gradient(circle,rgba(124,58,237,0.05) 0%,transparent 70%);
    border-radius:50%;
}
[data-testid="metric-container"] label {
    color:#6b7280 !important;
    font-size:0.68rem !important;
    font-weight:800 !important;
    letter-spacing:.1em;
    text-transform:uppercase;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    font-size:2.1rem !important;
    font-weight:900 !important;
    color:#1e1b2e !important;
    line-height:1.1;
    letter-spacing:-0.03em;
}

/* ══════════════════════════════════════════════════
   SIDEBAR
══════════════════════════════════════════════════ */
[data-testid="stSidebar"] {
    background:#ffffff !important;
    border-right:1px solid #e5e7ef !important;
    box-shadow:2px 0 12px rgba(0,0,0,0.04);
}
[data-testid="stSidebar"] > div:first-child { padding-top:0; }

/* Sidebar inner padding */
[data-testid="stSidebar"] .stMarkdown,
[data-testid="stSidebar"] .stRadio,
[data-testid="stSidebar"] .stButton,
[data-testid="stSidebar"] .stExpander,
[data-testid="stSidebar"] .stTextInput {
    padding-left:4px;
    padding-right:4px;
}

/* Nav radio — clean pill style */
[data-testid="stSidebar"] [data-testid="stRadio"] > div {
    gap:1px !important;
    padding:0 6px;
}
[data-testid="stSidebar"] [data-testid="stRadio"] label {
    font-size:0.855rem;
    color:#6b7280;
    padding:8px 14px;
    border-radius:10px;
    transition:background .15s, color .15s;
    font-weight:500;
    cursor:pointer;
    display:flex;
    align-items:center;
    gap:8px;
    line-height:1.3;
    margin:1px 0;
}
[data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
    background:#f5f3ff;
    color:#7c3aed;
}
[data-testid="stSidebar"] [data-testid="stRadio"] [aria-checked="true"] + div label,
[data-testid="stSidebar"] [data-testid="stRadio"] [aria-checked="true"] ~ div label {
    color:#7c3aed;
    background:#f5f3ff;
    font-weight:700;
}
/* Hide the default radio circle */
[data-testid="stSidebar"] [data-testid="stRadio"] [data-testid="stWidgetLabel"] { display:none; }
[data-testid="stSidebar"] [data-testid="stRadio"] input[type=radio] { display:none !important; }

/* Sidebar buttons — full width, stacked */
[data-testid="stSidebar"] .stButton > button {
    width:100%;
    border-radius:10px;
    font-size:0.82rem;
    font-weight:600;
    padding:9px 16px;
    margin-bottom:6px;
    text-align:left;
}
[data-testid="stSidebar"] .stButton > button[kind="secondary"] {
    background:#f9fafb;
    border:1px solid #e5e7ef;
    color:#374151;
}
[data-testid="stSidebar"] .stButton > button[kind="secondary"]:hover {
    background:#f5f3ff;
    border-color:#7c3aed;
    color:#7c3aed;
}

/* Sidebar expander (filter groups) */
[data-testid="stSidebar"] [data-testid="stExpander"] {
    border:1px solid #f3f4f6 !important;
    border-radius:10px !important;
    background:#fafafa !important;
    margin:0 6px 6px !important;
    box-shadow:none !important;
}
[data-testid="stSidebar"] [data-testid="stExpander"] summary {
    font-size:0.75rem !important;
    font-weight:700 !important;
    color:#374151 !important;
    letter-spacing:.02em;
    padding:10px 14px !important;
}
[data-testid="stSidebar"] [data-testid="stExpander"] summary:hover {
    color:#7c3aed !important;
}

/* ══════════════════════════════════════════════════
   TABS
══════════════════════════════════════════════════ */
[data-testid="stTabs"] [data-baseweb="tab-list"] {
    background:#ffffff;
    gap:2px;
    border-bottom:2px solid #e5e7ef;
    border-radius:12px 12px 0 0;
    padding:6px 8px 0;
    box-shadow:0 2px 8px rgba(0,0,0,0.04);
}
[data-testid="stTabs"] button[data-baseweb="tab"] {
    font-size:0.82rem;
    font-weight:600;
    color:#9ca3af;
    background:transparent;
    border-radius:8px 8px 0 0;
    padding:9px 18px;
    border:1px solid transparent;
    border-bottom:none;
    transition:all .2s;
    letter-spacing:.01em;
}
[data-testid="stTabs"] button[data-baseweb="tab"]:hover {
    color:#7c3aed;
    background:rgba(124,58,237,0.05);
}
[data-testid="stTabs"] button[data-baseweb="tab"][aria-selected="true"] {
    color:#7c3aed !important;
    background:#fff !important;
    border-color:#e5e7ef !important;
    border-bottom-color:#fff !important;
    font-weight:700 !important;
}
[data-testid="stTabs"] [data-baseweb="tab-highlight"] { display:none; }
[data-testid="stTabs"] [data-baseweb="tab-panel"] {
    background:#ffffff;
    border:1px solid #e5e7ef;
    border-top:none;
    border-radius:0 0 14px 14px;
    padding:18px 10px;
    box-shadow:0 4px 12px rgba(0,0,0,0.04);
}

/* ══════════════════════════════════════════════════
   DATAFRAME / TABLE
══════════════════════════════════════════════════ */
[data-testid="stDataFrame"] {
    border:1px solid #e5e7ef !important;
    border-radius:14px !important;
    overflow:hidden !important;
    box-shadow:0 4px 16px rgba(0,0,0,0.06);
}
[data-testid="stDataFrame"] thead th {
    background:#f8f9fc !important;
    color:#7c3aed !important;
    font-size:0.72rem !important;
    font-weight:800 !important;
    letter-spacing:.07em;
    text-transform:uppercase;
    border-bottom:2px solid #e5e7ef !important;
    padding:10px 12px !important;
}
[data-testid="stDataFrame"] tbody tr:hover td {
    background:rgba(124,58,237,0.04) !important;
}

/* ══════════════════════════════════════════════════
   BUTTONS
══════════════════════════════════════════════════ */
.stButton > button {
    border-radius:12px;
    font-size:0.84rem;
    font-weight:700;
    padding:10px 22px;
    transition:all .25s;
    font-family:'Inter',sans-serif;
    letter-spacing:.01em;
}
.stButton > button[kind="primary"] {
    background:linear-gradient(135deg,#7c3aed 0%,#3b82f6 100%);
    border:none;
    color:#fff;
    box-shadow:0 4px 18px rgba(124,58,237,0.3);
}
.stButton > button[kind="primary"]:hover {
    opacity:.9;
    transform:translateY(-2px);
    box-shadow:0 10px 28px rgba(124,58,237,0.4);
}
.stButton > button[kind="secondary"] {
    background:#ffffff;
    border:1px solid #d1d5db;
    color:#374151;
}
.stButton > button[kind="secondary"]:hover {
    border-color:#7c3aed;
    color:#7c3aed;
    background:rgba(124,58,237,0.04);
}
.stDownloadButton > button {
    border-radius:12px;
    font-size:0.82rem;
    font-weight:700;
    background:#ffffff;
    border:1px solid #3b82f6;
    color:#3b82f6;
    transition:all .2s;
}
.stDownloadButton > button:hover {
    background:rgba(59,130,246,0.07);
    box-shadow:0 4px 14px rgba(59,130,246,0.15);
}

/* ══════════════════════════════════════════════════
   FORM INPUTS
══════════════════════════════════════════════════ */
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input,
[data-testid="stDateInput"] input {
    background:#ffffff !important;
    border:1px solid #d1d5db !important;
    border-radius:12px !important;
    color:#1e1b2e !important;
    font-size:0.85rem;
    font-family:'Inter',sans-serif !important;
    transition:border-color .2s,box-shadow .2s;
    box-shadow:0 1px 3px rgba(0,0,0,0.05);
}
[data-testid="stTextInput"] input:focus,
[data-testid="stNumberInput"] input:focus {
    border-color:#7c3aed !important;
    box-shadow:0 0 0 3px rgba(124,58,237,0.12) !important;
}
[data-testid="stSelectbox"] > div,
[data-testid="stMultiSelect"] > div {
    background:#ffffff !important;
    border-color:#d1d5db !important;
    border-radius:12px !important;
    box-shadow:0 1px 3px rgba(0,0,0,0.05);
}
/* Input labels */
[data-testid="stTextInput"] label,
[data-testid="stSelectbox"] label,
[data-testid="stMultiSelect"] label,
[data-testid="stDateInput"] label,
[data-testid="stNumberInput"] label {
    font-size:0.72rem !important;
    font-weight:800 !important;
    color:#6b7280 !important;
    text-transform:uppercase;
    letter-spacing:.07em;
}

/* ══════════════════════════════════════════════════
   ALERTS
══════════════════════════════════════════════════ */
[data-testid="stAlert"] {
    border-radius:14px !important;
    border-left-width:4px !important;
    font-size:0.85rem;
    background:#ffffff !important;
    box-shadow:0 2px 8px rgba(0,0,0,0.06);
}

/* ── HR ───────────────────────────────────────── */
hr { border-color:#e5e7ef !important; margin:12px 0 !important; }

/* ══════════════════════════════════════════════════
   CUSTOM COMPONENTS — LIGHT
══════════════════════════════════════════════════ */

/* Page header */
.page-header {
    font-size:1.85rem;
    font-weight:900;
    letter-spacing:-0.04em;
    line-height:1.15;
    margin-bottom:4px;
    background:linear-gradient(135deg,#1e1b2e 0%,#7c3aed 55%,#3b82f6 100%);
    -webkit-background-clip:text;
    -webkit-text-fill-color:transparent;
    background-clip:text;
}
.page-sub {
    font-size:0.875rem;
    color:#9ca3af;
    margin-bottom:26px;
    font-weight:400;
}

/* Section header with left purple accent */
.section-header {
    font-size:0.92rem;
    font-weight:800;
    color:#1e1b2e;
    padding:0 0 10px 14px;
    border-left:3px solid #7c3aed;
    border-bottom:1px solid #e5e7ef;
    margin-bottom:16px;
    letter-spacing:-0.01em;
    display:flex;
    align-items:center;
    gap:8px;
}

/* KPI group label */
.kpi-group {
    font-size:0.62rem;
    color:#9ca3af;
    text-transform:uppercase;
    letter-spacing:.14em;
    font-weight:800;
    margin:8px 0 6px;
    padding-left:2px;
}

/* Status badges */
.badge-open    { display:inline-flex;align-items:center;gap:4px;background:#fee2e2;color:#dc2626;padding:2px 10px;border-radius:20px;font-size:.7rem;font-weight:700;border:1px solid #fecaca; }
.badge-closed  { display:inline-flex;align-items:center;gap:4px;background:#dcfce7;color:#16a34a;padding:2px 10px;border-radius:20px;font-size:.7rem;font-weight:700;border:1px solid #bbf7d0; }
.badge-merged  { display:inline-flex;align-items:center;gap:4px;background:#ede9fe;color:#7c3aed;padding:2px 10px;border-radius:20px;font-size:.7rem;font-weight:700;border:1px solid #ddd6fe; }
.badge-draft   { display:inline-flex;align-items:center;gap:4px;background:#dbeafe;color:#2563eb;padding:2px 10px;border-radius:20px;font-size:.7rem;font-weight:700;border:1px solid #bfdbfe; }
.badge-warning { display:inline-flex;align-items:center;gap:4px;background:#fef3c7;color:#d97706;padding:2px 10px;border-radius:20px;font-size:.7rem;font-weight:700;border:1px solid #fde68a; }

/* Health scorecard */
.health-card {
    background:#ffffff;
    border:1px solid #e5e7ef;
    border-radius:16px;
    padding:18px 20px;
    position:relative;
    overflow:hidden;
    transition:border-color .25s,transform .2s,box-shadow .25s;
    margin-bottom:8px;
    box-shadow:0 2px 8px rgba(0,0,0,0.05);
}
.health-card:hover {
    border-color:rgba(124,58,237,0.35);
    transform:translateY(-3px);
    box-shadow:0 12px 28px rgba(124,58,237,0.1);
}
.health-score { font-size:2.5rem;font-weight:900;line-height:1;letter-spacing:-0.05em; }
.health-label { font-size:0.68rem;font-weight:800;text-transform:uppercase;letter-spacing:.1em;color:#9ca3af;margin-top:4px; }
.health-name  { font-size:0.83rem;font-weight:700;color:#1e1b2e;margin-bottom:8px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis; }

/* Gradient divider */
.gradient-divider {
    height:1px;
    background:linear-gradient(90deg,transparent,rgba(124,58,237,0.25),rgba(59,130,246,0.2),transparent);
    margin:22px 0;
    border:none;
}

/* Sidebar brand */
.sidebar-brand {
    background:linear-gradient(160deg,#ffffff 0%,#f8f9fc 100%);
    border-bottom:2px solid #f0eeff;
    padding:24px 16px 20px;
    text-align:center;
    position:relative;
    overflow:hidden;
}
.sidebar-brand::before {
    content:'';
    position:absolute;
    bottom:-40px;left:50%;transform:translateX(-50%);
    width:160px;height:80px;
    background:radial-gradient(ellipse,rgba(124,58,237,0.1) 0%,transparent 70%);
}
.sidebar-brand-icon {
    font-size:2.4rem;line-height:1;
    filter:drop-shadow(0 0 10px rgba(124,58,237,0.4));
}
.sidebar-brand-name {
    font-size:0.9rem;font-weight:900;color:#1e1b2e;
    letter-spacing:-0.02em;margin-top:10px;
}
.sidebar-brand-sub {
    font-size:0.68rem;color:#9ca3af;margin-top:3px;font-weight:500;letter-spacing:.03em;
}

/* Nav section label */
.nav-section {
    font-size:0.62rem;
    font-weight:800;
    color:#9ca3af;
    text-transform:uppercase;
    letter-spacing:.12em;
    padding:12px 16px 4px;
}

/* Sidebar section divider */
.sidebar-section-divider {
    height:1px;
    background:#f3f4f6;
    margin:8px 12px;
}

/* Sidebar footer */
.sidebar-footer {
    padding:12px 14px 8px;
    text-align:center;
    border-top:1px solid #f3f4f6;
    margin-top:8px;
}
.sidebar-footer-ver {
    font-size:0.63rem;
    color:#d1d5db;
    margin-top:6px;
    font-weight:500;
    letter-spacing:.03em;
}

/* Sidebar empty state */
.sidebar-empty-msg {
    font-size:0.8rem;
    color:#9ca3af;
    text-align:center;
    padding:12px 16px;
    line-height:1.6;
    background:#fafafa;
    border-radius:10px;
    margin:0 6px;
    border:1px dashed #e5e7ef;
}

/* Data timestamp pill */
.data-pill {
    display:inline-flex;align-items:center;gap:5px;
    background:#f4f6fb;
    border:1px solid #e5e7ef;
    border-radius:20px;padding:4px 12px;
    font-size:0.7rem;color:#9ca3af;font-weight:500;
}

/* Feed */
.feed-container {
    max-height:680px;overflow-y:auto;padding-right:4px;
    scrollbar-width:thin;scrollbar-color:#e5e7ef transparent;
}
.feed-container::-webkit-scrollbar { width:4px; }
.feed-container::-webkit-scrollbar-track { background:transparent; }
.feed-container::-webkit-scrollbar-thumb { background:#e5e7ef;border-radius:4px; }
.feed-item {
    display:flex;gap:14px;padding:12px 10px;
    border-bottom:1px solid #f3f4f6;
    align-items:flex-start;transition:background .15s;
    border-radius:10px;
}
.feed-item:hover { background:#f9fafb; }
.feed-icon { font-size:1rem;width:28px;flex-shrink:0;text-align:center;margin-top:2px; }
.feed-body { flex:1;min-width:0; }
.feed-title { font-size:0.855rem;color:#1e1b2e;font-weight:500;white-space:nowrap;overflow:hidden;text-overflow:ellipsis; }
.feed-meta  { font-size:0.74rem;color:#9ca3af;margin-top:3px; }
.feed-type-badge {
    display:inline-block;background:#f3f4f6;color:#6b7280;
    padding:1px 8px;border-radius:10px;font-size:0.67rem;font-weight:700;
}

/* Stat row */
.stat-row {
    display:flex;align-items:center;justify-content:space-between;
    padding:9px 0;border-bottom:1px solid #f3f4f6;font-size:0.85rem;
}
.stat-row:last-child { border-bottom:none; }
.stat-label { color:#6b7280;font-weight:500; }
.stat-value { color:#1e1b2e;font-weight:800; }

/* Info card */
.info-card {
    background:#ffffff;
    border:1px solid #e5e7ef;
    border-radius:16px;padding:20px 24px;margin-bottom:16px;
    position:relative;overflow:hidden;
    box-shadow:0 2px 10px rgba(0,0,0,0.05);
}
.info-card::before {
    content:'';position:absolute;top:0;left:0;right:0;height:3px;
    background:linear-gradient(90deg,#7c3aed,#3b82f6);
}

/* Accent card */
.accent-card {
    background:#ffffff;
    border:1px solid rgba(124,58,237,0.25);
    border-radius:16px;padding:20px 24px;margin-bottom:16px;
    box-shadow:0 4px 16px rgba(124,58,237,0.07);
}

/* Caption */
.stCaption,[data-testid="stCaptionContainer"] {
    font-size:0.74rem !important;color:#9ca3af !important;
}

/* Checkbox */
[data-testid="stCheckbox"] label {
    font-size:0.85rem;color:#374151;font-weight:500;
}

/* Multiselect tags */
[data-baseweb="tag"] {
    background:rgba(124,58,237,0.1) !important;
    border:1px solid rgba(124,58,237,0.2) !important;
    border-radius:8px !important;
}
[data-baseweb="tag"] span { color:#7c3aed !important;font-size:0.78rem !important;font-weight:700 !important; }

/* Progress bar */
[data-testid="stProgressBar"] > div {
    background:linear-gradient(90deg,#7c3aed,#3b82f6) !important;
    border-radius:4px;
}

/* Spinner */
[data-testid="stSpinner"] svg { stroke:#7c3aed !important; }

/* Chart card */
.chart-card {
    background:#ffffff;
    border:1px solid #e5e7ef;
    border-radius:18px;padding:6px;margin-bottom:10px;
    box-shadow:0 2px 10px rgba(0,0,0,0.05);
}

/* Column gap */
[data-testid="stHorizontalBlock"] { gap:16px !important; }

/* Slider */
[data-testid="stSlider"] [data-baseweb="slider"] div[role="slider"] {
    background:#7c3aed !important;border-color:#7c3aed !important;
}

/* Scrollbar */
::-webkit-scrollbar { width:6px;height:6px; }
::-webkit-scrollbar-track { background:#f4f6fb; }
::-webkit-scrollbar-thumb { background:#d1d5db;border-radius:6px; }
::-webkit-scrollbar-thumb:hover { background:#7c3aed; }
</style>
"""


def inject_css():
    st.markdown(CSS, unsafe_allow_html=True)
