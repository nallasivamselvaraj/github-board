# ============================================================
# config.py — Central Configuration
# ============================================================

import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

def _secret(key: str, default: str = "") -> str:
    """Read from env first, then Streamlit secrets (cloud deployment)."""
    val = os.getenv(key, "")
    if val:
        return val
    try:
        import streamlit as st
        return st.secrets.get(key, default)
    except Exception:
        return default

ORG_NAME     = _secret("GITHUB_ORG") or "simtestlab"
GITHUB_TOKEN = _secret("GITHUB_TOKEN")
BASE_URL     = "https://api.github.com"
ISSUE_STATE = "all"
CACHE_TTL = 300  # seconds

STALE_WARNING  = 30   # days
STALE_CRITICAL = 90   # days

COLORS = {
    "open":   "#f2495c",  # Vibrant Red
    "closed": "#73bf69",  # Vibrant Green
    "merged": "#5794f2",  # Vibrant Blue
    "draft":  "#fade2a",  # Yellow
    "green":  "#73bf69",
    "yellow": "#fade2a",
    "orange": "#f46800",  # Simtestlab Orange
    "red":    "#f2495c",
    "blue":   "#5794f2",
    "purple": "#b877d9",
}

STALENESS_BUCKETS = [
    ("🟢 < 1 week",   0,  7,      "#73bf69"),
    ("🟡 1–4 weeks",  7,  30,     "#fade2a"),
    ("🟠 1–3 months", 30, 90,     "#f46800"),
    ("🔴 > 3 months", 90, 999999, "#f2495c"),
]

PAGES = [
    "🏠 Executive Dashboard",
    "📦 Repositories",
    "🐞 Issues",
    "🔀 Pull Requests",
    "👤 Contributors",
    "📡 Activity Feed",
    "⏳ Staleness",
    "📊 Reports",
    "🎯 Insights",
]
