import streamlit as st

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

/* ── Hide Streamlit auto-generated MPA nav ───────────────── */
[data-testid="stSidebarNav"] { display: none !important; }
#MainMenu { display: none !important; }
footer { display: none !important; }
header[data-testid="stHeader"] { background: transparent !important; }

/* ── Base & typography ───────────────────────────────────── */
html, body, [data-testid="stAppViewContainer"] {
    background: #0d0d14 !important;
}
[data-testid="stMain"] {
    background: #0d0d14;
}
body, .stMarkdown, .stText {
    font-family: 'Inter', 'Segoe UI', system-ui, sans-serif;
    color: #cdd6f4;
}

/* ── Subtle background grid pattern ─────────────────────── */
[data-testid="stMain"]::before {
    content: '';
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background-image:
        linear-gradient(rgba(203,166,247,0.025) 1px, transparent 1px),
        linear-gradient(90deg, rgba(203,166,247,0.025) 1px, transparent 1px);
    background-size: 40px 40px;
    pointer-events: none;
    z-index: 0;
}

/* ── Main content padding ────────────────────────────────── */
.block-container {
    padding: 1.75rem 2.5rem 3rem !important;
    max-width: 1500px;
    position: relative;
    z-index: 1;
}

/* ── Metric cards — glassmorphism ────────────────────────── */
[data-testid="metric-container"] {
    background: linear-gradient(135deg, rgba(30,30,46,0.9) 0%, rgba(24,24,37,0.95) 100%);
    border: 1px solid rgba(49,50,68,0.8);
    border-radius: 16px;
    padding: 20px 24px 18px;
    position: relative;
    overflow: hidden;
    transition: border-color 0.3s, transform 0.2s, box-shadow 0.3s;
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
}
[data-testid="metric-container"]:hover {
    border-color: rgba(203,166,247,0.4);
    transform: translateY(-3px);
    box-shadow: 0 12px 32px rgba(0,0,0,0.4), 0 0 0 1px rgba(203,166,247,0.1);
}
[data-testid="metric-container"]::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, #cba6f7, #89b4fa, #a6e3a1, #f38ba8);
    opacity: 0.8;
}
[data-testid="metric-container"]::after {
    content: '';
    position: absolute;
    top: -40px; right: -40px;
    width: 120px; height: 120px;
    background: radial-gradient(circle, rgba(203,166,247,0.06) 0%, transparent 70%);
    border-radius: 50%;
}
[data-testid="metric-container"] label {
    color: #a6adc8 !important;
    font-size: 0.7rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.09em;
    text-transform: uppercase;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    font-size: 2rem !important;
    font-weight: 800 !important;
    color: #cdd6f4 !important;
    line-height: 1.1;
    letter-spacing: -0.02em;
}
[data-testid="metric-container"] [data-testid="stMetricDelta"] {
    font-size: 0.77rem !important;
}

/* ── Sidebar ─────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #12121e 0%, #0f0f1a 100%) !important;
    border-right: 1px solid rgba(49,50,68,0.6);
}
[data-testid="stSidebar"] > div:first-child {
    padding-top: 0;
}

/* ── Sidebar nav radio — highlight selected */
[data-testid="stSidebar"] [data-testid="stRadio"] label {
    font-size: 0.865rem;
    color: #6c7086;
    padding: 6px 0;
    transition: color 0.2s;
    font-weight: 500;
}
[data-testid="stSidebar"] [data-testid="stRadio"] [aria-checked="true"] ~ div {
    color: #cba6f7 !important;
}
[data-testid="stSidebar"] .stRadio > div {
    gap: 2px;
}

/* ── Expander in sidebar ─────────────────────────────────── */
[data-testid="stSidebar"] [data-testid="stExpander"] {
    border: 1px solid rgba(49,50,68,0.5) !important;
    border-radius: 10px !important;
    background: rgba(30,30,46,0.4) !important;
}
[data-testid="stSidebar"] [data-testid="stExpander"] summary {
    font-size: 0.78rem !important;
    font-weight: 700 !important;
    color: #a6adc8 !important;
    text-transform: uppercase;
    letter-spacing: 0.07em;
}

/* ── Horizontal rule ─────────────────────────────────────── */
hr {
    border-color: rgba(49,50,68,0.6) !important;
    margin: 14px 0 !important;
}

/* ── Tabs ────────────────────────────────────────────────── */
[data-testid="stTabs"] [data-baseweb="tab-list"] {
    background: transparent;
    gap: 4px;
    border-bottom: 1px solid rgba(49,50,68,0.6);
    padding-bottom: 0;
}
[data-testid="stTabs"] button[data-baseweb="tab"] {
    font-size: 0.83rem;
    font-weight: 600;
    color: #6c7086;
    background: transparent;
    border-radius: 10px 10px 0 0;
    padding: 9px 18px;
    border: 1px solid transparent;
    border-bottom: none;
    transition: color 0.2s, background 0.2s;
}
[data-testid="stTabs"] button[data-baseweb="tab"]:hover {
    color: #cdd6f4;
    background: rgba(30,30,46,0.6);
}
[data-testid="stTabs"] button[data-baseweb="tab"][aria-selected="true"] {
    color: #cba6f7 !important;
    background: rgba(30,30,46,0.9) !important;
    border-color: rgba(49,50,68,0.6) !important;
    border-bottom-color: #0d0d14 !important;
}
[data-testid="stTabs"] [data-baseweb="tab-highlight"] {
    display: none;
}

/* ── Dataframe / table ───────────────────────────────────── */
[data-testid="stDataFrame"] {
    border: 1px solid rgba(49,50,68,0.7) !important;
    border-radius: 12px !important;
    overflow: hidden !important;
}
[data-testid="stDataFrame"] thead th {
    background: rgba(18,18,30,0.95) !important;
    color: #a6adc8 !important;
    font-size: 0.76rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    border-bottom: 1px solid rgba(49,50,68,0.6) !important;
}
[data-testid="stDataFrame"] tbody tr:hover td {
    background: rgba(30,30,46,0.7) !important;
}

/* ── Buttons ─────────────────────────────────────────────── */
.stButton > button {
    border-radius: 10px;
    font-size: 0.85rem;
    font-weight: 600;
    padding: 9px 20px;
    transition: all 0.2s;
    font-family: 'Inter', sans-serif;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #cba6f7 0%, #89b4fa 100%);
    border: none;
    color: #11111b;
    box-shadow: 0 4px 15px rgba(203,166,247,0.25);
}
.stButton > button[kind="primary"]:hover {
    opacity: 0.9;
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(203,166,247,0.35);
}
.stButton > button[kind="secondary"] {
    background: rgba(30,30,46,0.8);
    border: 1px solid rgba(69,71,90,0.8);
    color: #cdd6f4;
}
.stButton > button[kind="secondary"]:hover {
    border-color: #cba6f7;
    color: #cba6f7;
    background: rgba(203,166,247,0.08);
}
.stDownloadButton > button {
    border-radius: 10px;
    font-size: 0.82rem;
    font-weight: 600;
    background: rgba(30,30,46,0.8);
    border: 1px solid rgba(69,71,90,0.7);
    color: #cdd6f4;
    transition: all 0.2s;
}
.stDownloadButton > button:hover {
    border-color: #89b4fa;
    color: #89b4fa;
    box-shadow: 0 4px 12px rgba(137,180,250,0.2);
}

/* ── Form inputs ─────────────────────────────────────────── */
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input,
[data-testid="stDateInput"] input {
    background: rgba(30,30,46,0.8) !important;
    border: 1px solid rgba(49,50,68,0.8) !important;
    border-radius: 10px !important;
    color: #cdd6f4 !important;
    font-size: 0.85rem;
    font-family: 'Inter', sans-serif !important;
}
[data-testid="stTextInput"] input:focus,
[data-testid="stNumberInput"] input:focus {
    border-color: #cba6f7 !important;
    box-shadow: 0 0 0 3px rgba(203,166,247,0.12) !important;
}
[data-testid="stSelectbox"] > div,
[data-testid="stMultiSelect"] > div {
    background: rgba(30,30,46,0.8) !important;
    border-color: rgba(49,50,68,0.8) !important;
    border-radius: 10px !important;
}

/* ── Slider ──────────────────────────────────────────────── */
[data-testid="stSlider"] [data-baseweb="slider"] div[role="slider"] {
    background: #cba6f7 !important;
    border-color: #cba6f7 !important;
}

/* ── Page header ─────────────────────────────────────────── */
.page-header {
    font-size: 1.8rem;
    font-weight: 900;
    color: #cdd6f4;
    letter-spacing: -0.03em;
    margin-bottom: 2px;
    line-height: 1.15;
    background: linear-gradient(135deg, #cdd6f4 0%, #cba6f7 60%, #89b4fa 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.page-sub {
    font-size: 0.88rem;
    color: #585b70;
    margin-bottom: 24px;
    font-weight: 400;
}

/* ── Section headers ─────────────────────────────────────── */
.section-header {
    font-size: 0.95rem;
    font-weight: 800;
    color: #cdd6f4;
    padding: 4px 0 10px;
    border-bottom: 2px solid rgba(49,50,68,0.6);
    margin-bottom: 16px;
    letter-spacing: -0.01em;
    display: flex;
    align-items: center;
    gap: 8px;
}

/* ── KPI group labels ────────────────────────────────────── */
.kpi-group {
    font-size: 0.65rem;
    color: #45475a;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    font-weight: 800;
    margin-bottom: 8px;
    margin-top: 6px;
}

/* ── Status badges ───────────────────────────────────────── */
.badge-open   { display:inline-block; background:rgba(243,139,168,.12); color:#f38ba8; padding:3px 10px; border-radius:20px; font-size:.7rem; font-weight:700; border:1px solid rgba(243,139,168,.25); letter-spacing:.03em; }
.badge-closed { display:inline-block; background:rgba(166,227,161,.12); color:#a6e3a1; padding:3px 10px; border-radius:20px; font-size:.7rem; font-weight:700; border:1px solid rgba(166,227,161,.25); letter-spacing:.03em; }
.badge-merged { display:inline-block; background:rgba(203,166,247,.12); color:#cba6f7; padding:3px 10px; border-radius:20px; font-size:.7rem; font-weight:700; border:1px solid rgba(203,166,247,.25); letter-spacing:.03em; }
.badge-draft  { display:inline-block; background:rgba(137,180,250,.12); color:#89b4fa; padding:3px 10px; border-radius:20px; font-size:.7rem; font-weight:700; border:1px solid rgba(137,180,250,.25); letter-spacing:.03em; }
.badge-warning{ display:inline-block; background:rgba(249,226,175,.12); color:#f9e2af; padding:3px 10px; border-radius:20px; font-size:.7rem; font-weight:700; border:1px solid rgba(249,226,175,.25); letter-spacing:.03em; }

/* ── Score / health bar cards ────────────────────────────── */
.health-card {
    background: linear-gradient(135deg, rgba(30,30,46,0.85) 0%, rgba(24,24,37,0.9) 100%);
    border: 1px solid rgba(49,50,68,0.7);
    border-radius: 14px;
    padding: 16px 20px;
    position: relative;
    overflow: hidden;
    transition: border-color 0.25s, transform 0.2s;
}
.health-card:hover {
    border-color: rgba(203,166,247,0.35);
    transform: translateY(-2px);
}
.health-score {
    font-size: 2.4rem;
    font-weight: 900;
    line-height: 1;
    letter-spacing: -0.04em;
}
.health-label {
    font-size: 0.7rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: #6c7086;
    margin-top: 4px;
}
.health-name {
    font-size: 0.85rem;
    font-weight: 600;
    color: #cdd6f4;
    margin-bottom: 6px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

/* ── Info / warning / error boxes ───────────────────────── */
[data-testid="stAlert"] {
    border-radius: 12px !important;
    border-left-width: 3px !important;
    font-size: 0.875rem;
    background: rgba(30,30,46,0.6) !important;
}

/* ── Scrollable feed ─────────────────────────────────────── */
.feed-container {
    max-height: 680px;
    overflow-y: auto;
    padding-right: 4px;
    scrollbar-width: thin;
    scrollbar-color: rgba(49,50,68,0.8) transparent;
}
.feed-container::-webkit-scrollbar { width: 4px; }
.feed-container::-webkit-scrollbar-track { background: transparent; }
.feed-container::-webkit-scrollbar-thumb { background: rgba(49,50,68,0.8); border-radius: 4px; }
.feed-item {
    display: flex;
    gap: 14px;
    padding: 11px 10px;
    border-bottom: 1px solid rgba(30,30,46,0.8);
    align-items: flex-start;
    transition: background 0.15s, border-radius 0.15s;
    border-radius: 8px;
}
.feed-item:hover { background: rgba(30,30,46,0.7); }
.feed-icon {
    font-size: 1rem;
    width: 26px;
    flex-shrink: 0;
    text-align: center;
    margin-top: 2px;
}
.feed-body { flex: 1; min-width: 0; }
.feed-title { font-size: 0.855rem; color: #cdd6f4; font-weight: 500; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.feed-meta  { font-size: 0.75rem; color: #45475a; margin-top: 3px; }
.feed-type-badge {
    display: inline-block;
    background: rgba(49,50,68,0.5);
    color: #6c7086;
    padding: 1px 7px;
    border-radius: 10px;
    font-size: 0.68rem;
    font-weight: 600;
}

/* ── Caption / helper text ───────────────────────────────── */
.stCaption, [data-testid="stCaptionContainer"] {
    font-size: 0.75rem !important;
    color: #45475a !important;
}

/* ── Progress bar ────────────────────────────────────────── */
[data-testid="stProgressBar"] > div {
    background: linear-gradient(90deg, #cba6f7, #89b4fa) !important;
    border-radius: 4px;
}

/* ── Spinner ─────────────────────────────────────────────── */
[data-testid="stSpinner"] svg { stroke: #cba6f7 !important; }

/* ── Sidebar brand block ─────────────────────────────────── */
.sidebar-brand {
    background: linear-gradient(160deg, rgba(30,30,46,0.9) 0%, rgba(18,18,30,0.95) 100%);
    border-bottom: 1px solid rgba(49,50,68,0.5);
    padding: 22px 18px 18px;
    margin-bottom: 0;
    text-align: center;
    position: relative;
    overflow: hidden;
}
.sidebar-brand::after {
    content: '';
    position: absolute;
    bottom: -30px; left: 50%; transform: translateX(-50%);
    width: 120px; height: 60px;
    background: radial-gradient(ellipse, rgba(203,166,247,0.15) 0%, transparent 70%);
}
.sidebar-brand-icon {
    font-size: 2.2rem;
    line-height: 1;
    filter: drop-shadow(0 0 12px rgba(203,166,247,0.5));
}
.sidebar-brand-name {
    font-size: 0.88rem;
    font-weight: 800;
    color: #cdd6f4;
    letter-spacing: -0.01em;
    margin-top: 8px;
}
.sidebar-brand-sub {
    font-size: 0.68rem;
    color: #45475a;
    margin-top: 3px;
    font-weight: 500;
}

/* ── Sidebar nav section label ───────────────────────────── */
.nav-section {
    font-size: 0.62rem;
    font-weight: 800;
    color: #45475a;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    padding: 12px 12px 4px;
}

/* ── Data timestamp pill ─────────────────────────────────── */
.data-pill {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    background: rgba(30,30,46,0.7);
    border: 1px solid rgba(49,50,68,0.6);
    border-radius: 20px;
    padding: 3px 10px;
    font-size: 0.7rem;
    color: #585b70;
    font-weight: 500;
}

/* ── Insight stat row ────────────────────────────────────── */
.stat-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 8px 0;
    border-bottom: 1px solid rgba(49,50,68,0.4);
    font-size: 0.85rem;
}
.stat-row:last-child { border-bottom: none; }
.stat-label { color: #a6adc8; font-weight: 500; }
.stat-value { color: #cdd6f4; font-weight: 700; }

/* ── Gradient divider ────────────────────────────────────── */
.gradient-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(203,166,247,0.3), transparent);
    margin: 20px 0;
    border: none;
}

/* ── Chart container card ────────────────────────────────── */
.chart-card {
    background: linear-gradient(135deg, rgba(30,30,46,0.5) 0%, rgba(24,24,37,0.6) 100%);
    border: 1px solid rgba(49,50,68,0.5);
    border-radius: 16px;
    padding: 4px;
    margin-bottom: 8px;
}

/* ── Checkbox ────────────────────────────────────────────── */
[data-testid="stCheckbox"] label {
    font-size: 0.85rem;
    color: #a6adc8;
    font-weight: 500;
}

/* ── Multiselect tags ────────────────────────────────────── */
[data-baseweb="tag"] {
    background: rgba(203,166,247,0.15) !important;
    border: 1px solid rgba(203,166,247,0.25) !important;
    border-radius: 6px !important;
}
[data-baseweb="tag"] span {
    color: #cba6f7 !important;
    font-size: 0.78rem !important;
    font-weight: 600 !important;
}
</style>
"""


def inject_css():
    st.markdown(CSS, unsafe_allow_html=True)
