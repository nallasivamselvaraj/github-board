# ============================================================
# utils/charts.py
# Reusable Plotly chart functions used across all pages.
# Every function returns a go.Figure — call st.plotly_chart()
# at the call site.
# ============================================================

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from config import COLORS, STALENESS_BUCKETS

_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor ="rgba(0,0,0,0)",
    font_color   ="#1e1b2e",
    font_family  ="Inter, Segoe UI, system-ui, sans-serif",
    margin       =dict(l=0, r=0, t=42, b=0),
    legend       =dict(bgcolor="rgba(255,255,255,0.8)", font_size=12,
                       bordercolor="#e5e7ef", borderwidth=1),
    title_font   =dict(size=14, color="#1e1b2e", family="Inter"),
)

_AXIS = dict(
    gridcolor="rgba(229,231,239,0.9)",
    zerolinecolor="rgba(209,213,219,0.8)",
    showgrid=True,
    linecolor="rgba(229,231,239,0.6)",
    tickfont=dict(color="#6b7280", size=11),
)


def _apply(fig: go.Figure, title: str = "") -> go.Figure:
    fig.update_layout(title=dict(text=title, font=dict(size=14, color="#1e1b2e", family="Inter")), **_LAYOUT)
    fig.update_xaxes(**_AXIS)
    fig.update_yaxes(**_AXIS)
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
        hole=0.45,
    )
    fig.update_traces(
        textposition="inside",
        textinfo="percent+label",
        marker=dict(line=dict(color="rgba(0,0,0,0.3)", width=2)),
    )
    fig.update_layout(showlegend=True)
    return _apply(fig, "Open vs Closed Issues")


def issue_velocity(df: pd.DataFrame) -> go.Figure:
    opened = df[df["state"] == "open"].groupby("month").size().reset_index(name="Opened")
    closed = df[df["state"] == "closed"].groupby("month").size().reset_index(name="Closed")
    vel = opened.merge(closed, on="month", how="outer").fillna(0).sort_values("month")
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=vel["month"], y=vel["Opened"], name="Opened",
        marker=dict(color=COLORS["open"], opacity=0.85,
                    line=dict(color="rgba(0,0,0,0.2)", width=0.5)),
    ))
    fig.add_trace(go.Bar(
        x=vel["month"], y=vel["Closed"], name="Closed",
        marker=dict(color=COLORS["closed"], opacity=0.85,
                    line=dict(color="rgba(0,0,0,0.2)", width=0.5)),
    ))
    fig.update_layout(barmode="group", xaxis_title="Month", yaxis_title="Count",
                      bargap=0.2, bargroupgap=0.05)
    return _apply(fig, "Monthly Issue Velocity")


def issue_trend_line(df: pd.DataFrame) -> go.Figure:
    trend = df.groupby("date").size().reset_index(name="Issues")
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=trend["date"], y=trend["Issues"], mode="lines",
        fill="tozeroy",
        line=dict(color=COLORS["purple"], width=2.5, shape="spline"),
        fillcolor="rgba(203,166,247,0.1)",
    ))
    fig.update_layout(xaxis_title="Date", yaxis_title="Issues")
    return _apply(fig, "Daily Issue Activity")


def top_repos_bar(df: pd.DataFrame, n: int = 10) -> go.Figure:
    counts = df["repository"].value_counts().head(n).reset_index()
    counts.columns = ["Repository", "Count"]
    fig = px.bar(
        counts, x="Count", y="Repository", orientation="h",
        color="Count",
        color_continuous_scale=["#ede9fe", "#7c3aed", "#3b82f6"],
    )
    fig.update_layout(
        yaxis={"categoryorder": "total ascending"},
        coloraxis_showscale=False,
    )
    fig.update_traces(marker_line_width=0)
    return _apply(fig, "Top Active Repositories")


def aging_histogram(df: pd.DataFrame) -> go.Figure:
    open_df = df[df["state"] == "open"]
    fig = px.histogram(
        open_df, x="age_days", nbins=30,
        color_discrete_sequence=[COLORS["open"]],
    )
    fig.update_traces(opacity=0.85, marker_line_width=0)
    fig.update_layout(xaxis_title="Age (days)", yaxis_title="Issue Count",
                      bargap=0.05)
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
                 color="Bucket", color_discrete_map=colors, hole=0.45)
    fig.update_traces(
        textposition="inside", textinfo="percent+label",
        marker=dict(line=dict(color="rgba(0,0,0,0.3)", width=2)),
    )
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
    fig.update_traces(marker_line_width=0)
    fig.update_layout(
        xaxis_title="Repository", yaxis_title="Open Issues",
        xaxis_tickangle=-35,
    )
    return _apply(fig, "Open Issue Staleness per Repository")


def label_bar(df: pd.DataFrame, n: int = 20) -> go.Figure:
    ls = df["labels"].dropna().str.split(", ").explode().str.strip()
    ls = ls[ls != ""]
    if ls.empty:
        return go.Figure()
    counts = ls.value_counts().head(n).reset_index()
    counts.columns = ["Label", "Count"]
    fig = px.bar(
        counts, x="Count", y="Label", orientation="h",
        color="Count",
        color_continuous_scale=["#ede9fe", "#7c3aed", "#dc2626"],
    )
    fig.update_layout(
        yaxis={"categoryorder": "total ascending"},
        coloraxis_showscale=False,
    )
    fig.update_traces(marker_line_width=0)
    return _apply(fig, "Label Distribution")


def issue_cumulative(df: pd.DataFrame) -> go.Figure:
    """Cumulative open vs closed issues over time."""
    if df.empty or "date" not in df.columns:
        return go.Figure()
    opened = df.groupby("date").size().cumsum().reset_index(name="Cumulative_Opened")
    closed = df[df["state"] == "closed"].groupby("date").size().cumsum().reset_index(name="Cumulative_Closed")
    merged = opened.merge(closed, on="date", how="outer").fillna(method="ffill").fillna(0)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=merged["date"], y=merged["Cumulative_Opened"], name="Opened",
        mode="lines", fill="tozeroy",
        line=dict(color=COLORS["open"], width=2),
        fillcolor="rgba(243,139,168,0.08)",
    ))
    fig.add_trace(go.Scatter(
        x=merged["date"], y=merged["Cumulative_Closed"], name="Closed",
        mode="lines", fill="tozeroy",
        line=dict(color=COLORS["closed"], width=2),
        fillcolor="rgba(166,227,161,0.08)",
    ))
    fig.update_layout(xaxis_title="Date", yaxis_title="Cumulative Issues")
    return _apply(fig, "Cumulative Issues Over Time")


# ──────────────────────────────────────────────────────────
# PR CHARTS
# ──────────────────────────────────────────────────────────

def pr_state_pie(df: pd.DataFrame) -> go.Figure:
    counts = df["state"].value_counts().reset_index()
    counts.columns = ["State", "Count"]
    cmap = {"open": COLORS["open"], "closed": COLORS["closed"]}
    fig = px.pie(counts, names="State", values="Count",
                 color="State", color_discrete_map=cmap, hole=0.45)
    fig.update_traces(
        textposition="inside", textinfo="percent+label",
        marker=dict(line=dict(color="rgba(0,0,0,0.3)", width=2)),
    )
    return _apply(fig, "PR State Distribution")


def pr_trend(df: pd.DataFrame) -> go.Figure:
    opened = df.groupby("month").size().reset_index(name="Opened")
    merged_df = df[df["merged"] == True].groupby("month").size().reset_index(name="Merged") if "merged" in df.columns else pd.DataFrame()
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=opened["month"], y=opened["Opened"], name="Opened",
        marker=dict(color=COLORS["open"], opacity=0.85, line=dict(width=0)),
    ))
    if not merged_df.empty:
        fig.add_trace(go.Bar(
            x=merged_df["month"], y=merged_df["Merged"], name="Merged",
            marker=dict(color=COLORS["merged"], opacity=0.85, line=dict(width=0)),
        ))
    fig.update_layout(barmode="group", xaxis_title="Month", yaxis_title="PRs",
                      bargap=0.2, bargroupgap=0.05)
    return _apply(fig, "PR Trend (Opened vs Merged)")


def pr_cycle_hist(df: pd.DataFrame) -> go.Figure:
    closed = df[df["cycle_time_days"].notna() & (df["cycle_time_days"] >= 0)]
    if closed.empty:
        return go.Figure()
    fig = px.histogram(
        closed, x="cycle_time_days", nbins=30,
        color_discrete_sequence=[COLORS["merged"]],
    )
    fig.update_traces(opacity=0.85, marker_line_width=0)
    fig.update_layout(xaxis_title="Cycle Time (days)", yaxis_title="PRs", bargap=0.05)
    return _apply(fig, "PR Cycle Time Distribution")


def pr_repo_bar(df: pd.DataFrame, n: int = 10) -> go.Figure:
    counts = df["repository"].value_counts().head(n).reset_index()
    counts.columns = ["Repository", "Count"]
    fig = px.bar(
        counts, x="Count", y="Repository", orientation="h",
        color="Count",
        color_continuous_scale=["#ede9fe", "#7c3aed", "#3b82f6"],
    )
    fig.update_layout(
        yaxis={"categoryorder": "total ascending"},
        coloraxis_showscale=False,
    )
    fig.update_traces(marker_line_width=0)
    return _apply(fig, "PRs by Repository")


def pr_author_bar(df: pd.DataFrame, n: int = 10) -> go.Figure:
    """Top PR authors."""
    if df.empty or "author" not in df.columns:
        return go.Figure()
    counts = df["author"].value_counts().head(n).reset_index()
    counts.columns = ["Author", "PRs"]
    fig = px.bar(
        counts, x="PRs", y="Author", orientation="h",
        color="PRs",
        color_continuous_scale=["#fce7f3", "#ec4899", "#7c3aed"],
    )
    fig.update_layout(
        yaxis={"categoryorder": "total ascending"},
        coloraxis_showscale=False,
    )
    fig.update_traces(marker_line_width=0)
    return _apply(fig, "Top PR Authors")


# ──────────────────────────────────────────────────────────
# REPO CHARTS
# ──────────────────────────────────────────────────────────

def repo_stacked_bar(summary: pd.DataFrame) -> go.Figure:
    top = summary.head(15)
    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Open",
        x=top["Repository"], y=top["Open_Issues"],
        marker=dict(color=COLORS["open"], opacity=0.85, line=dict(width=0)),
    ))
    fig.add_trace(go.Bar(
        name="Closed",
        x=top["Repository"], y=top["Closed_Issues"],
        marker=dict(color=COLORS["closed"], opacity=0.85, line=dict(width=0)),
    ))
    fig.update_layout(
        barmode="stack", xaxis_title="", yaxis_title="Issues",
        xaxis_tickangle=-30,
    )
    return _apply(fig, "Open vs Closed Issues per Repository")


def repo_health_radar(summary: pd.DataFrame) -> go.Figure:
    """Radar chart of top repos' health dimensions."""
    if summary.empty:
        return go.Figure()
    top = summary.head(8).copy()
    # Normalise columns for radar
    cols = ["Closure_Rate%", "Total_Issues", "Total_PRs", "Contributors", "Avg_Age_Days"]
    cols = [c for c in cols if c in top.columns]
    if len(cols) < 3:
        return go.Figure()

    fig = go.Figure()
    palette = ["#cba6f7", "#89b4fa", "#a6e3a1", "#f38ba8", "#fab387", "#f9e2af", "#94e2d5", "#b4befe"]
    for i, (_, row) in enumerate(top.iterrows()):
        vals = []
        for c in cols:
            col_max = top[c].max()
            norm = (row[c] / col_max * 100) if col_max > 0 else 0
            if c == "Avg_Age_Days":   # lower is better
                norm = 100 - norm
            vals.append(round(norm, 1))
        vals.append(vals[0])  # close the shape
        labels = [c.replace("_", " ").replace("%", "") for c in cols]
        labels.append(labels[0])
        fig.add_trace(go.Scatterpolar(
            r=vals, theta=labels, fill="toself",
            name=row["Repository"][:18],
            line=dict(color=palette[i % len(palette)], width=2),
            fillcolor=palette[i % len(palette)].replace(")", ",0.07)").replace("rgb(", "rgba("),
            opacity=0.8,
        ))
    fig.update_layout(
        polar=dict(
            bgcolor="rgba(248,249,252,0.8)",
            radialaxis=dict(visible=True, range=[0, 100], gridcolor="rgba(209,213,219,0.8)",
                            tickfont=dict(size=9, color="#6b7280")),
            angularaxis=dict(gridcolor="rgba(209,213,219,0.8)"),
        ),
    )
    return _apply(fig, "Repository Health Radar (Top 8)")


# ──────────────────────────────────────────────────────────
# CONTRIBUTOR CHARTS
# ──────────────────────────────────────────────────────────

def contributor_bar(df: pd.DataFrame, n: int = 15) -> go.Figure:
    top = df.head(n).copy()
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=top["Closed_Issues"], y=top["Author"],
        name="Closed", orientation="h",
        marker=dict(color=COLORS["closed"], opacity=0.85, line=dict(width=0)),
    ))
    fig.add_trace(go.Bar(
        x=top["Open_Issues"], y=top["Author"],
        name="Open", orientation="h",
        marker=dict(color=COLORS["open"], opacity=0.85, line=dict(width=0)),
    ))
    fig.update_layout(barmode="stack", yaxis={"categoryorder": "total ascending"})
    return _apply(fig, "Top Contributors by Issues")


def contributor_repos_scatter(df: pd.DataFrame) -> go.Figure:
    fig = px.scatter(
        df.head(30), x="Repos_Active", y="Issues_Opened",
        size="Comments", color="Closed_Issues",
        hover_name="Author",
        color_continuous_scale=["#dbeafe", "#10b981", "#7c3aed"],
        size_max=35,
    )
    fig.update_layout(xaxis_title="Repos Active", yaxis_title="Issues Opened")
    fig.update_traces(marker_line_width=0)
    return _apply(fig, "Contributor Activity Spread")


def contributor_heatmap(df: pd.DataFrame, issues: pd.DataFrame) -> go.Figure:
    """Issues per contributor per repository heatmap."""
    if issues.empty or "author" not in issues.columns or "repository" not in issues.columns:
        return go.Figure()
    top_authors = df.head(12)["Author"].tolist() if not df.empty else []
    if not top_authors:
        return go.Figure()
    sub = issues[issues["author"].isin(top_authors)]
    heat = sub.groupby(["author", "repository"]).size().reset_index(name="count")
    pivot = heat.pivot(index="author", columns="repository", values="count").fillna(0)
    fig = go.Figure(data=go.Heatmap(
        z=pivot.values,
        x=[c[:20] for c in pivot.columns],
        y=pivot.index.tolist(),
        colorscale=[[0, "#f5f3ff"], [0.5, "#7c3aed"], [1, "#dc2626"]],
        hoverongaps=False,
        xgap=2, ygap=2,
    ))
    fig.update_layout(
        xaxis_tickangle=-35,
        coloraxis_showscale=True,
    )
    return _apply(fig, "Contributor × Repository Activity Heatmap")


# ──────────────────────────────────────────────────────────
# RELEASE / ACTIVITY CHARTS
# ──────────────────────────────────────────────────────────

def release_timeline(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return go.Figure()
    counts = df.groupby("month").size().reset_index(name="Releases")
    fig = px.bar(
        counts, x="month", y="Releases",
        color_discrete_sequence=[COLORS["purple"]],
    )
    fig.update_traces(opacity=0.85, marker_line_width=0)
    return _apply(fig, "Releases per Month")


def engineering_activity_timeline(issues: pd.DataFrame, prs: pd.DataFrame) -> go.Figure:
    """Combined daily activity: issues + PRs with area fill."""
    fig = go.Figure()
    if not issues.empty:
        i = issues.groupby("date").size().reset_index(name="Issues")
        fig.add_trace(go.Scatter(
            x=i["date"], y=i["Issues"], mode="lines",
            name="Issues", fill="tozeroy",
            line=dict(color=COLORS["open"], width=2.5, shape="spline"),
            fillcolor="rgba(243,139,168,0.08)",
        ))
    if not prs.empty and "date" in prs.columns:
        p = prs.groupby("date").size().reset_index(name="PRs")
        fig.add_trace(go.Scatter(
            x=p["date"], y=p["PRs"], mode="lines",
            name="PRs", fill="tozeroy",
            line=dict(color=COLORS["merged"], width=2.5, shape="spline"),
            fillcolor="rgba(203,166,247,0.08)",
        ))
    fig.update_layout(xaxis_title="Date", yaxis_title="Activity")
    return _apply(fig, "Engineering Activity Timeline")


def activity_calendar_heatmap(df: pd.DataFrame, col: str = "date") -> go.Figure:
    """GitHub-style contribution calendar (weekly heatmap)."""
    if df.empty or col not in df.columns:
        return go.Figure()
    daily = df.groupby(col).size().reset_index(name="count")
    daily[col] = pd.to_datetime(daily[col])
    daily["dow"] = daily[col].dt.dayofweek        # 0=Mon
    daily["week"] = daily[col].dt.strftime("%Y-W%U")

    pivot = daily.pivot_table(index="dow", columns="week", values="count", fill_value=0)
    fig = go.Figure(data=go.Heatmap(
        z=pivot.values,
        x=pivot.columns.tolist(),
        y=["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
        colorscale=[[0, "#f5f3ff"], [0.4, "#c4b5fd"], [0.75, "#7c3aed"], [1, "#4f46e5"]],
        hoverongaps=False,
        xgap=3, ygap=3,
        showscale=False,
    ))
    fig.update_layout(
        height=200,
        xaxis=dict(showticklabels=False, showgrid=False),
        yaxis=dict(showgrid=False, tickfont=dict(size=10)),
        margin=dict(l=0, r=0, t=42, b=0),
    )
    return _apply(fig, "Activity Calendar (All Time)")


def issue_close_rate_trend(df: pd.DataFrame) -> go.Figure:
    """Monthly closure rate % trend line."""
    if df.empty or "month" not in df.columns:
        return go.Figure()
    monthly = df.groupby("month").agg(
        total=("issue_number", "count"),
        closed=("state", lambda x: (x == "closed").sum()),
    ).reset_index()
    monthly["rate"] = (monthly["closed"] / monthly["total"] * 100).round(1)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=monthly["month"], y=monthly["rate"],
        mode="lines+markers",
        name="Closure Rate %",
        line=dict(color="#10b981", width=2.5, shape="spline"),
        marker=dict(size=7, color="#10b981",
                    line=dict(color="#ffffff", width=2)),
        fill="tozeroy",
        fillcolor="rgba(16,185,129,0.08)",
    ))
    fig.update_layout(
        xaxis_title="Month", yaxis_title="Closure Rate (%)",
        yaxis=dict(range=[0, 105]),
    )
    return _apply(fig, "Monthly Issue Closure Rate (%)")
