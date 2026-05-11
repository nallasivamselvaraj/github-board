# ============================================================
# utils/filters.py
# Global filter engine — builds sidebar widgets once,
# applies them to every DataFrame consistently.
# ============================================================

from datetime import date

import pandas as pd
import streamlit as st


# ─────────────────────────────────────────────
# SIDEBAR FILTER BUILDER
# Renders all sidebar widgets and stores choices
# in st.session_state["filters"]
# ─────────────────────────────────────────────

def build_sidebar_filters(issues: pd.DataFrame, prs: pd.DataFrame) -> dict:
    """
    Renders the global filter sidebar.
    Returns a dict of selected filter values.
    """
    st.sidebar.markdown("## 📌 Global Filters")
    st.sidebar.markdown("---")

    f = {}

    # ── Repositories ──────────────────────────
    all_repos = sorted(
        set(issues["repository"].dropna().unique())
        | set(prs["repository"].dropna().unique() if not prs.empty else [])
    )
    f["repositories"] = st.sidebar.multiselect(
        "📦 Repositories", all_repos, default=all_repos, key="f_repos"
    )

    st.sidebar.markdown("---")

    # ── Issue state ───────────────────────────
    issue_states = sorted(issues["state"].dropna().unique()) if not issues.empty else []
    f["issue_states"] = st.sidebar.multiselect(
        "🐞 Issue State", issue_states, default=issue_states, key="f_istates"
    )

    # ── PR state ──────────────────────────────
    if not prs.empty:
        pr_states = sorted(prs["state"].dropna().unique())
        f["pr_states"] = st.sidebar.multiselect(
            "🔀 PR State", pr_states, default=pr_states, key="f_prstates"
        )
    else:
        f["pr_states"] = []

    st.sidebar.markdown("---")

    # ── Authors ───────────────────────────────
    all_authors = sorted(
        set(issues["author"].dropna().unique())
        | set(prs["author"].dropna().unique() if not prs.empty else [])
    )
    f["authors"] = st.sidebar.multiselect(
        "👤 Authors / Contributors", all_authors, default=all_authors, key="f_authors"
    )

    # ── Labels ────────────────────────────────
    label_series = (
        issues["labels"].dropna()
        .str.split(", ").explode().str.strip()
    )
    label_series = label_series[label_series != ""]
    all_labels = sorted(label_series.unique()) if not label_series.empty else []
    f["labels"] = st.sidebar.multiselect(
        "🏷️ Labels", all_labels, default=all_labels, key="f_labels"
    )

    st.sidebar.markdown("---")

    # ── Date range ────────────────────────────
    min_d = issues["created_date"].min() if not issues.empty else date.today()
    max_d = issues["created_date"].max() if not issues.empty else date.today()
    dr = st.sidebar.date_input(
        "📅 Created Date Range", [min_d, max_d], key="f_daterange"
    )
    f["date_range"] = dr if len(dr) == 2 else [min_d, max_d]

    st.sidebar.markdown("---")

    # ── Search ────────────────────────────────
    f["search"] = st.sidebar.text_input("🔍 Search (title / author / label)", key="f_search")

    # ── Staleness ─────────────────────────────
    f["min_age"] = st.sidebar.slider("⏳ Min age (days)", 0, 365, 0, key="f_age")

    st.sidebar.markdown("---")

    return f


# ─────────────────────────────────────────────
# APPLY FILTERS TO DATAFRAMES
# ─────────────────────────────────────────────

def apply_issue_filters(df: pd.DataFrame, f: dict) -> pd.DataFrame:
    if df.empty:
        return df
    out = df.copy()

    if f.get("repositories"):
        out = out[out["repository"].isin(f["repositories"])]
    if f.get("issue_states"):
        out = out[out["state"].isin(f["issue_states"])]
    if f.get("authors"):
        out = out[out["author"].isin(f["authors"])]

    dr = f.get("date_range", [])
    if len(dr) == 2 and "created_date" in out.columns:
        out = out[(out["created_date"] >= dr[0]) & (out["created_date"] <= dr[1])]

    labels = f.get("labels", [])
    if labels and len(labels) < len(_all_labels_from(df)):
        mask = out["labels"].apply(
            lambda x: any(lb in x for lb in labels) if x else False
        )
        out = out[mask]

    search = f.get("search", "").strip()
    if search:
        mask = (
            out["title"].str.contains(search, case=False, na=False)
            | out["author"].str.contains(search, case=False, na=False)
            | out["labels"].str.contains(search, case=False, na=False)
        )
        out = out[mask]

    min_age = f.get("min_age", 0)
    if min_age > 0 and "age_days" in out.columns:
        out = out[out["age_days"] >= min_age]

    return out.reset_index(drop=True)


def apply_pr_filters(df: pd.DataFrame, f: dict) -> pd.DataFrame:
    if df.empty:
        return df
    out = df.copy()

    if f.get("repositories"):
        out = out[out["repository"].isin(f["repositories"])]
    if f.get("pr_states"):
        out = out[out["state"].isin(f["pr_states"])]
    if f.get("authors"):
        out = out[out["author"].isin(f["authors"])]

    dr = f.get("date_range", [])
    if len(dr) == 2 and "created_date" in out.columns:
        out = out[(out["created_date"] >= dr[0]) & (out["created_date"] <= dr[1])]

    search = f.get("search", "").strip()
    if search:
        mask = (
            out["title"].str.contains(search, case=False, na=False)
            | out["author"].str.contains(search, case=False, na=False)
        )
        out = out[mask]

    return out.reset_index(drop=True)


def apply_repo_filters(df: pd.DataFrame, f: dict) -> pd.DataFrame:
    if df.empty:
        return df
    out = df.copy()
    if f.get("repositories"):
        out = out[out["name"].isin(f["repositories"])]
    return out.reset_index(drop=True)


def _all_labels_from(df: pd.DataFrame) -> list:
    s = df["labels"].dropna().str.split(", ").explode().str.strip()
    return sorted(s[s != ""].unique())
