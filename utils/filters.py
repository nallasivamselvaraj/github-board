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
    Renders the global filter sidebar with collapsible sections.
    Returns a dict of selected filter values.
    """
    f = {}

    # ── Repositories ──────────────────────────
    all_repos = sorted(
        set(issues["repository"].dropna().unique())
        | set(prs["repository"].dropna().unique() if not prs.empty else [])
    )
    with st.sidebar.expander("📦 Repositories", expanded=True):
        f["repositories"] = st.multiselect(
            "Select repositories", all_repos, default=all_repos, key="f_repos",
            label_visibility="collapsed",
        )

    # ── Status filters ─────────────────────────
    with st.sidebar.expander("🔖 Status Filters", expanded=False):
        issue_states = sorted(issues["state"].dropna().unique()) if not issues.empty else []
        f["issue_states"] = st.multiselect(
            "🐞 Issue State", issue_states, default=issue_states, key="f_istates"
        )
        if not prs.empty:
            pr_states = sorted(prs["state"].dropna().unique())
            f["pr_states"] = st.multiselect(
                "🔀 PR State", pr_states, default=pr_states, key="f_prstates"
            )
        else:
            f["pr_states"] = []

    # ── People & Labels ───────────────────────
    with st.sidebar.expander("👤 People & Labels", expanded=False):
        all_authors = sorted(
            set(issues["author"].dropna().unique())
            | set(prs["author"].dropna().unique() if not prs.empty else [])
        )
        f["authors"] = st.multiselect(
            "Authors / Contributors", all_authors, default=all_authors, key="f_authors"
        )

        label_series = (
            issues["labels"].dropna()
            .str.split(", ").explode().str.strip()
        )
        label_series = label_series[label_series != ""]
        all_labels = sorted(label_series.unique()) if not label_series.empty else []
        f["labels"] = st.multiselect(
            "🏷️ Labels", all_labels, default=all_labels, key="f_labels"
        )

    # ── Date range ────────────────────────────
    with st.sidebar.expander("📅 Date Range", expanded=False):
        min_d = issues["created_date"].min() if not issues.empty else date.today()
        max_d = issues["created_date"].max() if not issues.empty else date.today()
        dr = st.date_input(
            "Created between", [min_d, max_d], key="f_daterange",
            label_visibility="collapsed",
        )
        f["date_range"] = dr if len(dr) == 2 else [min_d, max_d]

    # ── Search ────────────────────────────────
    st.sidebar.markdown("")
    f["search"] = st.sidebar.text_input(
        "🔍 Search",
        key="f_search",
        placeholder="Title · author · label…",
    )

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
