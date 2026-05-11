import streamlit as st

CSS = """
<style>
/* ── Hide Streamlit auto-generated MPA nav ───────────────── */
[data-testid="stSidebarNav"] { display: none !important; }

/* ── Base & typography ───────────────────────────────────── */
html, body, [data-testid="stAppViewContainer"] {
    background: #11111b !important;
}
[data-testid="stMain"] {
    background: #11111b;
}
body, .stMarkdown, .stText {
    font-family: 'Inter', 'Segoe UI', system-ui, sans-serif;
    color: #cdd6f4;
}

/* ── Main content padding ────────────────────────────────── */
.block-container {
    padding: 1.75rem 2rem 3rem !important;
    max-width: 1400px;
}

/* ── Metric cards ────────────────────────────────────────── */
[data-testid="metric-container"] {
    background: linear-gradient(135deg, #1e1e2e 0%, #181825 100%);
    border: 1px solid #313244;
    border-radius: 14px;
    padding: 18px 22px 16px;
    position: relative;
    overflow: hidden;
    transition: border-color 0.2s, transform 0.15s;
}
[data-testid="metric-container"]:hover {
    border-color: #585b70;
    transform: translateY(-1px);
}
[data-testid="metric-container"]::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, #cba6f7, #89b4fa, #a6e3a1);
    opacity: 0.7;
}
[data-testid="metric-container"] label {
    color: #a6adc8 !important;
    font-size: 0.72rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.07em;
    text-transform: uppercase;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    font-size: 1.9rem !important;
    font-weight: 700 !important;
    color: #cdd6f4 !important;
    line-height: 1.1;
}
[data-testid="metric-container"] [data-testid="stMetricDelta"] {
    font-size: 0.78rem !important;
}

/* ── Sidebar ─────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: #181825 !important;
    border-right: 1px solid #313244;
}
[data-testid="stSidebar"] > div:first-child {
    padding-top: 0;
}
[data-testid="stSidebar"] .stMarkdown h2 {
    color: #cba6f7;
    font-size: 0.82rem;
    font-weight: 700;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    margin: 0;
}
[data-testid="stSidebar"] [data-testid="stRadio"] label {
    font-size: 0.87rem;
    color: #a6adc8;
    padding: 2px 0;
}
[data-testid="stSidebar"] [data-testid="stRadio"] [aria-checked="true"] ~ div {
    color: #cba6f7;
}

/* Sidebar nav radio — highlight selected */
[data-testid="stSidebar"] .stRadio > div {
    gap: 4px;
}

/* ── Horizontal rule ─────────────────────────────────────── */
hr {
    border-color: #313244 !important;
    margin: 12px 0 !important;
}

/* ── Tabs ────────────────────────────────────────────────── */
[data-testid="stTabs"] [data-baseweb="tab-list"] {
    background: transparent;
    gap: 4px;
    border-bottom: 1px solid #313244;
    padding-bottom: 0;
}
[data-testid="stTabs"] button[data-baseweb="tab"] {
    font-size: 0.83rem;
    font-weight: 500;
    color: #a6adc8;
    background: transparent;
    border-radius: 8px 8px 0 0;
    padding: 8px 16px;
    border: 1px solid transparent;
    border-bottom: none;
    transition: color 0.15s, background 0.15s;
}
[data-testid="stTabs"] button[data-baseweb="tab"]:hover {
    color: #cdd6f4;
    background: #1e1e2e;
}
[data-testid="stTabs"] button[data-baseweb="tab"][aria-selected="true"] {
    color: #cba6f7 !important;
    background: #1e1e2e !important;
    border-color: #313244 !important;
    border-bottom-color: #1e1e2e !important;
}
[data-testid="stTabs"] [data-baseweb="tab-highlight"] {
    display: none;
}

/* ── Dataframe / table ───────────────────────────────────── */
[data-testid="stDataFrame"] {
    border: 1px solid #313244;
    border-radius: 10px;
    overflow: hidden;
}
[data-testid="stDataFrame"] thead th {
    background: #181825 !important;
    color: #a6adc8 !important;
    font-size: 0.78rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    border-bottom: 1px solid #313244 !important;
}
[data-testid="stDataFrame"] tbody tr:hover td {
    background: #1e1e2e !important;
}

/* ── Buttons ─────────────────────────────────────────────── */
.stButton > button {
    border-radius: 9px;
    font-size: 0.85rem;
    font-weight: 600;
    padding: 8px 18px;
    transition: all 0.15s;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #cba6f7, #89b4fa);
    border: none;
    color: #11111b;
}
.stButton > button[kind="primary"]:hover {
    opacity: 0.88;
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(203,166,247,0.3);
}
.stButton > button[kind="secondary"] {
    background: transparent;
    border: 1px solid #45475a;
    color: #cdd6f4;
}
.stButton > button[kind="secondary"]:hover {
    border-color: #cba6f7;
    color: #cba6f7;
}
.stDownloadButton > button {
    border-radius: 9px;
    font-size: 0.82rem;
    font-weight: 600;
    background: #1e1e2e;
    border: 1px solid #45475a;
    color: #cdd6f4;
    transition: all 0.15s;
}
.stDownloadButton > button:hover {
    border-color: #89b4fa;
    color: #89b4fa;
    box-shadow: 0 2px 8px rgba(137,180,250,0.15);
}

/* ── Form inputs ─────────────────────────────────────────── */
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input,
[data-testid="stDateInput"] input {
    background: #1e1e2e !important;
    border: 1px solid #313244 !important;
    border-radius: 8px !important;
    color: #cdd6f4 !important;
    font-size: 0.85rem;
}
[data-testid="stTextInput"] input:focus,
[data-testid="stNumberInput"] input:focus {
    border-color: #cba6f7 !important;
    box-shadow: 0 0 0 2px rgba(203,166,247,0.15) !important;
}
[data-testid="stSelectbox"] > div,
[data-testid="stMultiSelect"] > div {
    background: #1e1e2e !important;
    border-color: #313244 !important;
    border-radius: 8px !important;
}

/* ── Page header ─────────────────────────────────────────── */
.page-header {
    font-size: 1.65rem;
    font-weight: 800;
    color: #cdd6f4;
    letter-spacing: -0.01em;
    margin-bottom: 2px;
    line-height: 1.2;
}
.page-sub {
    font-size: 0.875rem;
    color: #6c7086;
    margin-bottom: 20px;
}

/* ── Section headers ─────────────────────────────────────── */
.section-header {
    font-size: 1rem;
    font-weight: 700;
    color: #cdd6f4;
    padding: 4px 0 8px;
    border-bottom: 2px solid #313244;
    margin-bottom: 14px;
    letter-spacing: -0.005em;
}

/* ── KPI group labels ────────────────────────────────────── */
.kpi-group {
    font-size: 0.68rem;
    color: #585b70;
    text-transform: uppercase;
    letter-spacing: 0.09em;
    font-weight: 700;
    margin-bottom: 6px;
    margin-top: 4px;
}

/* ── Status badges ───────────────────────────────────────── */
.badge-open   { display:inline-block; background:rgba(243,139,168,.15); color:#f38ba8; padding:2px 9px; border-radius:20px; font-size:.72rem; font-weight:700; border:1px solid rgba(243,139,168,.3); }
.badge-closed { display:inline-block; background:rgba(166,227,161,.15); color:#a6e3a1; padding:2px 9px; border-radius:20px; font-size:.72rem; font-weight:700; border:1px solid rgba(166,227,161,.3); }
.badge-merged { display:inline-block; background:rgba(203,166,247,.15); color:#cba6f7; padding:2px 9px; border-radius:20px; font-size:.72rem; font-weight:700; border:1px solid rgba(203,166,247,.3); }
.badge-draft  { display:inline-block; background:rgba(137,180,250,.15); color:#89b4fa; padding:2px 9px; border-radius:20px; font-size:.72rem; font-weight:700; border:1px solid rgba(137,180,250,.3); }

/* ── Info / warning / error boxes ───────────────────────── */
[data-testid="stAlert"] {
    border-radius: 10px !important;
    border-left-width: 3px !important;
    font-size: 0.875rem;
}

/* ── Scrollable feed ─────────────────────────────────────── */
.feed-container {
    max-height: 640px;
    overflow-y: auto;
    padding-right: 6px;
    scrollbar-width: thin;
    scrollbar-color: #313244 transparent;
}
.feed-container::-webkit-scrollbar { width: 5px; }
.feed-container::-webkit-scrollbar-track { background: transparent; }
.feed-container::-webkit-scrollbar-thumb { background: #313244; border-radius: 3px; }
.feed-item {
    display: flex;
    gap: 14px;
    padding: 12px 0;
    border-bottom: 1px solid #1e1e2e;
    align-items: flex-start;
    transition: background 0.1s;
}
.feed-item:hover { background: #1e1e2e; border-radius: 6px; padding-left: 6px; }
.feed-icon {
    font-size: 1.1rem;
    width: 26px;
    flex-shrink: 0;
    text-align: center;
    margin-top: 1px;
}
.feed-body { flex: 1; min-width: 0; }
.feed-title { font-size: 0.86rem; color: #cdd6f4; font-weight: 500; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.feed-meta  { font-size: 0.76rem; color: #585b70; margin-top: 3px; }

/* ── Caption / helper text ───────────────────────────────── */
.stCaption, [data-testid="stCaptionContainer"] {
    font-size: 0.76rem !important;
    color: #585b70 !important;
}

/* ── Progress column ─────────────────────────────────────── */
[data-testid="stProgressBar"] > div {
    background: linear-gradient(90deg, #cba6f7, #f38ba8) !important;
    border-radius: 3px;
}

/* ── Spinner ─────────────────────────────────────────────── */
[data-testid="stSpinner"] svg { stroke: #cba6f7 !important; }

/* ── Sidebar brand block ─────────────────────────────────── */
.sidebar-brand {
    background: linear-gradient(160deg, #1e1e2e 0%, #181825 100%);
    border-bottom: 1px solid #313244;
    padding: 20px 16px 16px;
    margin-bottom: 0;
    text-align: center;
}
.sidebar-brand-icon { font-size: 2rem; line-height: 1; }
.sidebar-brand-name {
    font-size: 0.9rem;
    font-weight: 800;
    color: #cdd6f4;
    letter-spacing: -0.01em;
    margin-top: 6px;
}
.sidebar-brand-sub {
    font-size: 0.7rem;
    color: #585b70;
    margin-top: 2px;
}
</style>
"""


def inject_css():
    st.markdown(CSS, unsafe_allow_html=True)
