# ============================================================
# utils/charts.py
# Reusable Plotly chart functions used across all pages.
# Every function returns a go.Figure — call st.plotly_chart()
# at the call site.
# ============================================================

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from config import COLORS, STALENESS_BUCKETS

_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor ="rgba(0,0,0,0)",
    font_color   ="#cdd6f4",
    margin       =dict(l=0, r=0, t=36, b=0),
    legend       =dict(bgcolor="rgba(0,0,0,0)"),
)


def _apply(fig: go.Figure, title: str = "") -> go.Figure:
    fig.update_layout(title=title, **_LAYOUT)
    fig.update_xaxes(gridcolor="#313244", zerolinecolor="#313244")
    fig.update_yaxes(gridcolor="#313244", zerolinecolor="#313244")
    return fig


# ──────────────────────────────────────────────────────────
# ISSUE CHARTS
# ──────────────────────────────────────────────────────────

def issue_state_pie(df: pd.DataFrame) -> go.Figure:
    counts = df["state"].value_counts().reset_index()
    counts.columns = ["State", "Count"]
    fig = px.pie(
        counts, names="State", values="Count",
        color="State",
        color_discrete_map={"open": COLORS["open"], "closed": COLORS["closed"]},
    )
    fig.update_traces(textposition="inside", textinfo="percent+label")
    return _apply(fig, "Open vs Closed Issues")


def issue_velocity(df: pd.DataFrame) -> go.Figure:
    opened = df[df["state"] == "open"].groupby("month").size().reset_index(name="Opened")
    closed = df[df["state"] == "closed"].groupby("month").size().reset_index(name="Closed")
    vel = opened.merge(closed, on="month", how="outer").fillna(0).sort_values("month")
    fig = go.Figure()
    fig.add_trace(go.Bar(x=vel["month"], y=vel["Opened"], name="Opened", marker_color=COLORS["open"]))
    fig.add_trace(go.Bar(x=vel["month"], y=vel["Closed"], name="Closed", marker_color=COLORS["closed"]))
    fig.update_layout(barmode="group", xaxis_title="Month", yaxis_title="Count")
    return _apply(fig, "Monthly Issue Velocity")


def issue_trend_line(df: pd.DataFrame) -> go.Figure:
    trend = df.groupby("date").size().reset_index(name="Issues")
    fig = px.line(trend, x="date", y="Issues", line_shape="spline")
    fig.update_traces(line_color=COLORS["purple"])
    return _apply(fig, "Daily Issue Activity")


def top_repos_bar(df: pd.DataFrame, n: int = 10) -> go.Figure:
    counts = df["repository"].value_counts().head(n).reset_index()
    counts.columns = ["Repository", "Count"]
    fig = px.bar(
        counts, x="Count", y="Repository", orientation="h",
        color="Count", color_continuous_scale="Blues",
    )
    fig.update_layout(yaxis={"categoryorder": "total ascending"})
    return _apply(fig, "Top Active Repositories")


def aging_histogram(df: pd.DataFrame) -> go.Figure:
    open_df = df[df["state"] == "open"]
    fig = px.histogram(open_df, x="age_days", nbins=30, color_discrete_sequence=[COLORS["open"]])
    fig.update_layout(xaxis_title="Age (days)", yaxis_title="Issue Count")
    return _apply(fig, "Issue Age Distribution (Open Only)")


def staleness_pie(df: pd.DataFrame) -> go.Figure:
    order  = [b[0] for b in STALENESS_BUCKETS]
    colors = {b[0]: b[3] for b in STALENESS_BUCKETS}
    open_df = df[df["state"] == "open"].copy()
    counts  = open_df["staleness"].value_counts().reset_index()
    counts.columns = ["Bucket", "Count"]
    counts["Bucket"] = pd.Categorical(counts["Bucket"], categories=order, ordered=True)
    counts = counts.sort_values("Bucket")
    fig = px.pie(counts, names="Bucket", values="Count",
                 color="Bucket", color_discrete_map=colors)
    fig.update_traces(textposition="inside", textinfo="percent+label")
    return _apply(fig, "Staleness Distribution (Open Issues)")


def staleness_heatmap(df: pd.DataFrame) -> go.Figure:
    order  = [b[0] for b in STALENESS_BUCKETS]
    colors = {b[0]: b[3] for b in STALENESS_BUCKETS}
    open_df = df[df["state"] == "open"].copy()
    heat = open_df.groupby(["repository", "staleness"]).size().reset_index(name="count")
    fig = px.bar(
        heat, x="repository", y="count", color="staleness",
        color_discrete_map=colors,
        barmode="stack",
        category_orders={"staleness": order},
    )
    fig.update_layout(xaxis_title="Repository", yaxis_title="Open Issues")
    return _apply(fig, "Open Issue Staleness per Repository")


def label_bar(df: pd.DataFrame, n: int = 20) -> go.Figure:
    ls = df["labels"].dropna().str.split(", ").explode().str.strip()
    ls = ls[ls != ""]
    if ls.empty:
        return go.Figure()
    counts = ls.value_counts().head(n).reset_index()
    counts.columns = ["Label", "Count"]
    fig = px.bar(counts, x="Count", y="Label", orientation="h",
                 color="Count", color_continuous_scale="Purples")
    fig.update_layout(yaxis={"categoryorder": "total ascending"})
    return _apply(fig, "Label Distribution")


# ──────────────────────────────────────────────────────────
# PR CHARTS
# ──────────────────────────────────────────────────────────

def pr_state_pie(df: pd.DataFrame) -> go.Figure:
    counts = df["state"].value_counts().reset_index()
    counts.columns = ["State", "Count"]
    cmap = {"open": COLORS["open"], "closed": COLORS["closed"]}
    fig = px.pie(counts, names="State", values="Count",
                 color="State", color_discrete_map=cmap)
    fig.update_traces(textposition="inside", textinfo="percent+label")
    return _apply(fig, "PR State Distribution")


def pr_trend(df: pd.DataFrame) -> go.Figure:
    opened = df.groupby("month").size().reset_index(name="Opened")
    merged = df[df["merged"] == True].groupby("month").size().reset_index(name="Merged") if "merged" in df.columns else pd.DataFrame()
    fig = go.Figure()
    fig.add_trace(go.Bar(x=opened["month"], y=opened["Opened"], name="Opened", marker_color=COLORS["open"]))
    if not merged.empty:
        fig.add_trace(go.Bar(x=merged["month"], y=merged["Merged"], name="Merged", marker_color=COLORS["merged"]))
    fig.update_layout(barmode="group", xaxis_title="Month", yaxis_title="PRs")
    return _apply(fig, "PR Trend (Opened vs Merged)")


def pr_cycle_hist(df: pd.DataFrame) -> go.Figure:
    closed = df[df["cycle_time_days"].notna() & (df["cycle_time_days"] >= 0)]
    if closed.empty:
        return go.Figure()
    fig = px.histogram(closed, x="cycle_time_days", nbins=30,
                       color_discrete_sequence=[COLORS["merged"]])
    fig.update_layout(xaxis_title="Cycle Time (days)", yaxis_title="PRs")
    return _apply(fig, "PR Cycle Time Distribution")


def pr_repo_bar(df: pd.DataFrame, n: int = 10) -> go.Figure:
    counts = df["repository"].value_counts().head(n).reset_index()
    counts.columns = ["Repository", "Count"]
    fig = px.bar(counts, x="Count", y="Repository", orientation="h",
                 color="Count", color_continuous_scale="Purples")
    fig.update_layout(yaxis={"categoryorder": "total ascending"})
    return _apply(fig, "PRs by Repository")


# ──────────────────────────────────────────────────────────
# REPO CHARTS
# ──────────────────────────────────────────────────────────

def repo_stacked_bar(summary: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Bar(name="Open",   x=summary["Repository"], y=summary["Open_Issues"],   marker_color=COLORS["open"]))
    fig.add_trace(go.Bar(name="Closed", x=summary["Repository"], y=summary["Closed_Issues"], marker_color=COLORS["closed"]))
    fig.update_layout(barmode="stack", xaxis_title="", yaxis_title="Issues")
    return _apply(fig, "Open vs Closed Issues per Repository")


# ──────────────────────────────────────────────────────────
# CONTRIBUTOR CHARTS
# ──────────────────────────────────────────────────────────

def contributor_bar(df: pd.DataFrame, n: int = 15) -> go.Figure:
    top = df.head(n).copy()
    fig = go.Figure()
    fig.add_trace(go.Bar(x=top["Closed_Issues"], y=top["Author"],
                         name="Closed", orientation="h", marker_color=COLORS["closed"]))
    fig.add_trace(go.Bar(x=top["Open_Issues"],   y=top["Author"],
                         name="Open",   orientation="h", marker_color=COLORS["open"]))
    fig.update_layout(barmode="stack", yaxis={"categoryorder": "total ascending"})
    return _apply(fig, "Top Contributors by Issues")


def contributor_repos_scatter(df: pd.DataFrame) -> go.Figure:
    fig = px.scatter(
        df.head(30), x="Repos_Active", y="Issues_Opened",
        size="Comments", color="Closed_Issues",
        hover_name="Author",
        color_continuous_scale="Greens",
        size_max=30,
    )
    fig.update_layout(xaxis_title="Repos Active", yaxis_title="Issues Opened")
    return _apply(fig, "Contributor Activity Spread")


# ──────────────────────────────────────────────────────────
# RELEASE / ACTIVITY CHARTS
# ──────────────────────────────────────────────────────────

def release_timeline(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return go.Figure()
    counts = df.groupby("month").size().reset_index(name="Releases")
    fig = px.bar(counts, x="month", y="Releases", color_discrete_sequence=[COLORS["purple"]])
    return _apply(fig, "Releases per Month")


def engineering_activity_timeline(issues: pd.DataFrame, prs: pd.DataFrame) -> go.Figure:
    """Combined daily activity: issues + PRs."""
    fig = go.Figure()
    if not issues.empty:
        i = issues.groupby("date").size().reset_index(name="Issues")
        fig.add_trace(go.Scatter(x=i["date"], y=i["Issues"],
                                 mode="lines", name="Issues",
                                 line=dict(color=COLORS["open"], width=2)))
    if not prs.empty and "date" in prs.columns:
        p = prs.groupby("date").size().reset_index(name="PRs")
        fig.add_trace(go.Scatter(x=p["date"], y=p["PRs"],
                                 mode="lines", name="PRs",
                                 line=dict(color=COLORS["merged"], width=2)))
    fig.update_layout(xaxis_title="Date", yaxis_title="Activity")
    return _apply(fig, "Engineering Activity Timeline")
