import glob
import json
import os
import re
from datetime import datetime, timezone

import pandas as pd
import streamlit as st

from config import CACHE_TTL


def _latest(pattern: str) -> str | None:
    files = glob.glob(pattern)
    return max(files) if files else None


def _read(pattern: str) -> list:
    path = _latest(pattern)
    if not path:
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _to_dt(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    for c in cols:
        if c in df.columns:
            df[c] = pd.to_datetime(df[c], utc=True, errors="coerce")
    return df


def _age(df: pd.DataFrame, col: str, suffix: str) -> pd.DataFrame:
    now = datetime.now(timezone.utc)
    if col in df.columns:
        df[suffix] = (now - df[col]).dt.days.fillna(0).astype(int)
    return df


def _period(df: pd.DataFrame, col: str) -> pd.DataFrame:
    if col not in df.columns:
        return df
    # Strip timezone before to_period() to avoid the UserWarning about dropped tz info
    naive = df[col].dt.tz_convert(None)
    df["week"]  = naive.dt.to_period("W").astype(str)
    df["month"] = naive.dt.to_period("M").astype(str)
    df["year"]  = naive.dt.year
    df["date"]  = naive.dt.date
    return df


def _staleness(days: int) -> str:
    if days <= 7:   return "🟢 < 1 week"
    if days <= 30:  return "🟡 1–4 weeks"
    if days <= 90:  return "🟠 1–3 months"
    return "🔴 > 3 months"


@st.cache_data(ttl=CACHE_TTL, show_spinner=False)
def load_issues() -> pd.DataFrame:
    data = _read("github_all_repo_issues_*.json")
    if not data:
        return pd.DataFrame()
    df = pd.DataFrame(data)
    df = _to_dt(df, ["created_at", "updated_at", "closed_at"])
    df = _age(df, "created_at", "age_days")
    df = _age(df, "updated_at", "days_since_update")
    df = _period(df, "created_at")
    df["labels"]       = df.get("labels", pd.Series(dtype=str)).fillna("")
    df["comments"]     = pd.to_numeric(df.get("comments", 0), errors="coerce").fillna(0).astype(int)
    df["staleness"]    = df["days_since_update"].apply(_staleness)
    df["created_date"] = df["created_at"].dt.date
    df["updated_date"] = df["updated_at"].dt.date
    return df


@st.cache_data(ttl=CACHE_TTL, show_spinner=False)
def load_prs() -> pd.DataFrame:
    data = _read("github_all_repo_prs_*.json")
    if not data:
        return pd.DataFrame()
    df = pd.DataFrame(data)
    df = _to_dt(df, ["created_at", "updated_at", "closed_at", "merged_at"])
    df = _age(df, "created_at", "age_days")
    df = _age(df, "updated_at", "days_since_update")
    df = _period(df, "created_at")
    df["draft"]        = df.get("draft",  pd.Series(dtype=bool)).fillna(False).astype(bool)
    df["merged"]       = df.get("merged", pd.Series(dtype=bool)).fillna(False).astype(bool)
    df["labels"]       = df.get("labels", pd.Series(dtype=str)).fillna("")
    df["created_date"] = df["created_at"].dt.date
    end_col = df["merged_at"].where(df["merged_at"].notna(), df["closed_at"])
    df["cycle_time_days"] = (end_col - df["created_at"]).dt.days
    return df


@st.cache_data(ttl=CACHE_TTL, show_spinner=False)
def load_releases() -> pd.DataFrame:
    data = _read("github_all_repo_releases_*.json")
    if not data:
        return pd.DataFrame()
    df = pd.DataFrame(data)
    df = _to_dt(df, ["created_at", "published_at"])
    naive = df["published_at"].dt.tz_convert(None)
    df["date"]  = naive.dt.date
    df["month"] = naive.dt.to_period("M").astype(str)
    return df


@st.cache_data(ttl=CACHE_TTL, show_spinner=False)
def load_contributors() -> pd.DataFrame:
    data = _read("github_all_repo_contributors_*.json")
    if not data:
        return pd.DataFrame()
    return pd.DataFrame(data)


@st.cache_data(ttl=CACHE_TTL, show_spinner=False)
def load_repo_meta() -> pd.DataFrame:
    data = _read("github_all_repo_meta_*.json")
    if not data:
        return pd.DataFrame()
    df = pd.DataFrame(data)
    df = _to_dt(df, ["created_at", "updated_at"])
    df["updated_date"] = df["updated_at"].dt.date
    return df


def load_all() -> dict[str, pd.DataFrame]:
    return {
        "issues":       load_issues(),
        "prs":          load_prs(),
        "releases":     load_releases(),
        "contributors": load_contributors(),
        "repos":        load_repo_meta(),
    }


def latest_file_label() -> str:
    path = _latest("github_all_repo_issues_*.json")
    if not path:
        return "No data — click Refresh"
    m = re.search(r"(\d{8}_\d{6})", os.path.basename(path))
    if m:
        ts = datetime.strptime(m.group(1), "%Y%m%d_%H%M%S")
        return f"Last fetched {ts.strftime('%b %d, %Y  %H:%M')}"
    return os.path.basename(path)
