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
    "open":   "#f38ba8",
    "closed": "#a6e3a1",
    "merged": "#cba6f7",
    "draft":  "#89b4fa",
    "green":  "#a6e3a1",
    "yellow": "#f9e2af",
    "orange": "#fab387",
    "red":    "#f38ba8",
    "blue":   "#89b4fa",
    "purple": "#cba6f7",
}

STALENESS_BUCKETS = [
    ("🟢 < 1 week",   0,  7,      "#a6e3a1"),
    ("🟡 1–4 weeks",  7,  30,     "#f9e2af"),
    ("🟠 1–3 months", 30, 90,     "#fab387"),
    ("🔴 > 3 months", 90, 999999, "#f38ba8"),
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
]
