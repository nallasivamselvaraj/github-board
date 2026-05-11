# ============================================================
# utils/metrics.py
# All KPI computations in one place.
# ============================================================

import pandas as pd


def issue_metrics(issues: pd.DataFrame, prs: pd.DataFrame, releases: pd.DataFrame) -> dict:
    total_repos      = issues["repository"].nunique() if not issues.empty else 0
    total_issues     = len(issues)
    open_issues      = int((issues["state"] == "open").sum()) if not issues.empty else 0
    closed_issues    = int((issues["state"] == "closed").sum()) if not issues.empty else 0
    closure_rate     = round(closed_issues / total_issues * 100, 1) if total_issues else 0

    total_prs        = len(prs)
    open_prs         = int((prs["state"] == "open").sum()) if not prs.empty else 0
    merged_prs       = int(prs["merged"].sum()) if not prs.empty and "merged" in prs.columns else 0
    merge_rate       = round(merged_prs / total_prs * 100, 1) if total_prs else 0

    contributors     = issues["author"].nunique() if not issues.empty else 0
    total_releases   = len(releases)

    stale_issues     = int(
        ((issues["state"] == "open") & (issues["days_since_update"] > 30)).sum()
    ) if not issues.empty else 0

    avg_cycle        = round(prs["cycle_time_days"].dropna().mean(), 1) if not prs.empty and "cycle_time_days" in prs.columns else 0

    return dict(
        total_repos    = total_repos,
        total_issues   = total_issues,
        open_issues    = open_issues,
        closed_issues  = closed_issues,
        closure_rate   = closure_rate,
        total_prs      = total_prs,
        open_prs       = open_prs,
        merged_prs     = merged_prs,
        merge_rate     = merge_rate,
        contributors   = contributors,
        total_releases = total_releases,
        stale_issues   = stale_issues,
        avg_cycle      = avg_cycle,
    )


def repo_summary(issues: pd.DataFrame, prs: pd.DataFrame) -> pd.DataFrame:
    """Per-repo aggregated table joining issue + PR counts."""
    if issues.empty:
        return pd.DataFrame()

    i_agg = (
        issues.groupby("repository")
        .agg(
            Total_Issues  = ("issue_number", "count"),
            Open_Issues   = ("state", lambda x: (x == "open").sum()),
            Closed_Issues = ("state", lambda x: (x == "closed").sum()),
            Contributors  = ("author",       "nunique"),
            Total_Comments= ("comments",     "sum"),
            Avg_Age_Days  = ("age_days",     "mean"),
        )
        .reset_index()
        .rename(columns={"repository": "Repository"})
    )
    i_agg["Closure_Rate%"] = (
        i_agg["Closed_Issues"] / i_agg["Total_Issues"] * 100
    ).round(1)
    i_agg["Avg_Age_Days"] = i_agg["Avg_Age_Days"].round(0).astype(int)

    if not prs.empty:
        p_agg = (
            prs.groupby("repository")
            .agg(Total_PRs=("pr_number", "count"))
            .reset_index()
            .rename(columns={"repository": "Repository"})
        )
        i_agg = i_agg.merge(p_agg, on="Repository", how="left")
        i_agg["Total_PRs"] = i_agg["Total_PRs"].fillna(0).astype(int)

    return i_agg.sort_values("Total_Issues", ascending=False)


def contributor_summary(issues: pd.DataFrame, prs: pd.DataFrame) -> pd.DataFrame:
    """Per-author aggregated stats."""
    if issues.empty:
        return pd.DataFrame()

    c = (
        issues.groupby("author")
        .agg(
            Issues_Opened = ("issue_number", "count"),
            Open_Issues   = ("state", lambda x: (x == "open").sum()),
            Closed_Issues = ("state", lambda x: (x == "closed").sum()),
            Repos_Active  = ("repository",   "nunique"),
            Comments      = ("comments",     "sum"),
            Avg_Age       = ("age_days",     "mean"),
        )
        .reset_index()
        .rename(columns={"author": "Author"})
    )
    c["Avg_Age"] = c["Avg_Age"].round(0).astype(int)

    if not prs.empty:
        p = (
            prs.groupby("author")
            .agg(PRs_Opened=("pr_number", "count"))
            .reset_index()
            .rename(columns={"author": "Author"})
        )
        c = c.merge(p, on="Author", how="left")
        c["PRs_Opened"] = c["PRs_Opened"].fillna(0).astype(int)

    return c.sort_values("Issues_Opened", ascending=False)
