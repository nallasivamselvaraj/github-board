# ============================================================
# utils/charts.py
# Reusable Plotly chart functions used across all pages.
# ============================================================

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from config import COLORS, STALENESS_BUCKETS

# ── Professional Light Layout Constants ───────────────────
_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor ="rgba(0,0,0,0)",
    font_color   ="#24292e",
    font_family  ="'Inter', 'Segoe UI', sans-serif",
    margin       =dict(l=10, r=10, t=50, b=10),
    legend       =dict(
        bgcolor="rgba(255,255,255,0.8)",
        font=dict(size=11, color="#4a5568"),
        bordercolor="#d8dce0",
        borderwidth=1,
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    ),
    title_font   =dict(size=13, color="#4a5568", family="'Inter', sans-serif"),
    hoverlabel   =dict(bgcolor="#ffffff", font_size=12, font_family="'Inter'"),
)

_AXIS = dict(
    gridcolor="#e2e8f0",
    zerolinecolor="#cbd5e0",
    showgrid=True,
    linecolor="#cbd5e0",
    tickfont=dict(color="#718096", size=10, family="'JetBrains Mono', monospace"),
    title_font=dict(size=11, color="#4a5568"),
)


def _apply(fig: go.Figure, title: str = "") -> go.Figure:
    fig.update_layout(
        title=dict(
            text=title.upper(),
            x=0,
            xanchor="left",
            font=dict(size=12, color="#4a5568", family="'Inter', sans-serif")
        ),
        **_LAYOUT
    )
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
        hole=0.6,
    )
    fig.update_traces(
        textposition="outside",
        textinfo="label+percent",
        marker=dict(line=dict(color="#ffffff", width=2)),
        rotation=90,
    )
    fig.update_layout(showlegend=False)
    return _apply(fig, "Issue Status Distribution")


def issue_velocity(df: pd.DataFrame) -> go.Figure:
    if df.empty: return go.Figure()
    opened = df[df["state"] == "open"].groupby("month").size().reset_index(name="Opened")
    closed = df[df["state"] == "closed"].groupby("month").size().reset_index(name="Closed")
    vel = opened.merge(closed, on="month", how="outer").fillna(0).sort_values("month")
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=vel["month"], y=vel["Opened"], name="Opened",
        marker=dict(color=COLORS["open"], line=dict(width=0)),
    ))
    fig.add_trace(go.Bar(
        x=vel["month"], y=vel["Closed"], name="Closed",
        marker=dict(color=COLORS["closed"], line=dict(width=0)),
    ))
    fig.update_layout(barmode="group", bargap=0.15, bargroupgap=0.05)
    return _apply(fig, "Monthly Issue Velocity")


def issue_close_rate_trend(df: pd.DataFrame) -> go.Figure:
    if df.empty: return go.Figure()
    opened = df.groupby("month").size().reset_index(name="Opened")
    closed = df[df["state"] == "closed"].groupby("month").size().reset_index(name="Closed")
    merged = opened.merge(closed, on="month", how="outer").fillna(0).sort_values("month")
    merged["Rate"] = (merged["Closed"] / merged["Opened"].replace(0, 1) * 100).round(1)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=merged["month"], y=merged["Rate"], mode="lines+markers",
        line=dict(color=COLORS["green"], width=3),
        marker=dict(size=8, symbol="diamond"),
        fill="tozeroy", fillcolor="rgba(54,163,71,0.05)"
    ))
    fig.update_yaxes(range=[0, 110])
    return _apply(fig, "Closure Rate Trend (%)")


def issue_cumulative(df: pd.DataFrame) -> go.Figure:
    if df.empty: return go.Figure()
    df = df.sort_values("date")
    opened = df.groupby("date").size().cumsum().reset_index(name="Total")
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=opened["date"], y=opened["Total"], mode="lines",
        line=dict(color=COLORS["orange"], width=2),
        fill="tozeroy", fillcolor="rgba(244,104,0,0.05)"
    ))
    return _apply(fig, "Cumulative Issues")


def issue_trend_line(df: pd.DataFrame) -> go.Figure:
    if df.empty: return go.Figure()
    trend = df.groupby("date").size().reset_index(name="Issues")
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=trend["date"], y=trend["Issues"], mode="lines",
        fill="tozeroy",
        line=dict(color=COLORS["orange"], width=2, shape="linear"),
        fillcolor="rgba(244,104,0,0.1)",
    ))
    return _apply(fig, "Daily Activity Trend")


def top_repos_bar(df: pd.DataFrame, n: int = 10) -> go.Figure:
    if df.empty: return go.Figure()
    counts = df["repository"].value_counts().head(n).reset_index()
    counts.columns = ["Repository", "Count"]
    fig = px.bar(
        counts, x="Count", y="Repository", orientation="h",
        color="Count",
        color_continuous_scale=[[0, "#f7f8fa"], [1, COLORS["orange"]]],
    )
    fig.update_layout(
        yaxis={"categoryorder": "total ascending"},
        coloraxis_showscale=False,
    )
    fig.update_traces(marker_line_width=0)
    return _apply(fig, "Most Active Repositories")


def aging_histogram(df: pd.DataFrame) -> go.Figure:
    if df.empty: return go.Figure()
    open_df = df[df["state"] == "open"]
    fig = px.histogram(
        open_df, x="age_days", nbins=25,
        color_discrete_sequence=[COLORS["orange"]],
    )
    fig.update_traces(marker_line_width=1, marker_line_color="#ffffff")
    fig.update_layout(bargap=0.1)
    return _apply(fig, "Issue Age Distribution (Days)")


def staleness_heatmap(df: pd.DataFrame) -> go.Figure:
    if df.empty: return go.Figure()
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
    fig.update_layout(xaxis_tickangle=-45)
    return _apply(fig, "Staleness per Repository")


def staleness_pie(df: pd.DataFrame) -> go.Figure:
    if df.empty: return go.Figure()
    order  = [b[0] for b in STALENESS_BUCKETS]
    colors = {b[0]: b[3] for b in STALENESS_BUCKETS}
    open_df = df[df["state"] == "open"].copy()
    counts  = open_df["staleness"].value_counts().reset_index()
    counts.columns = ["Bucket", "Count"]
    counts["Bucket"] = pd.Categorical(counts["Bucket"], categories=order, ordered=True)
    counts = counts.sort_values("Bucket")
    fig = px.pie(counts, names="Bucket", values="Count",
                 color="Bucket", color_discrete_map=colors, hole=0.6)
    fig.update_traces(
        textposition="outside", textinfo="percent",
        marker=dict(line=dict(color="#ffffff", width=2)),
    )
    fig.update_layout(showlegend=True)
    return _apply(fig, "Open Issue Staleness")


def label_bar(df: pd.DataFrame, n: int = 15) -> go.Figure:
    ls = df["labels"].dropna().str.split(", ").explode().str.strip()
    ls = ls[ls != ""]
    if ls.empty: return go.Figure()
    counts = ls.value_counts().head(n).reset_index()
    counts.columns = ["Label", "Count"]
    fig = px.bar(
        counts, x="Count", y="Label", orientation="h",
        color="Count",
        color_continuous_scale=[[0, "#f7f8fa"], [1, COLORS["blue"]]],
    )
    fig.update_layout(
        yaxis={"categoryorder": "total ascending"},
        coloraxis_showscale=False,
    )
    return _apply(fig, "Top Labels Used")


# ──────────────────────────────────────────────────────────
# PR CHARTS
# ──────────────────────────────────────────────────────────

def pr_state_pie(df: pd.DataFrame) -> go.Figure:
    if df.empty: return go.Figure()
    counts = df["state"].value_counts().reset_index()
    counts.columns = ["State", "Count"]
    cmap = {"open": COLORS["open"], "closed": COLORS["closed"]}
    fig = px.pie(counts, names="State", values="Count",
                 color="State", color_discrete_map=cmap, hole=0.6)
    fig.update_traces(
        textposition="outside", textinfo="label+percent",
        marker=dict(line=dict(color="#ffffff", width=2)),
    )
    fig.update_layout(showlegend=False)
    return _apply(fig, "Pull Request Status")


def pr_trend(df: pd.DataFrame) -> go.Figure:
    if df.empty: return go.Figure()
    opened = df.groupby("month").size().reset_index(name="Opened")
    merged_df = df[df["merged"] == True].groupby("month").size().reset_index(name="Merged") if "merged" in df.columns else pd.DataFrame()
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=opened["month"], y=opened["Opened"], name="Opened",
        marker=dict(color=COLORS["open"], line=dict(width=0)),
    ))
    if not merged_df.empty:
        fig.add_trace(go.Bar(
            x=merged_df["month"], y=merged_df["Merged"], name="Merged",
            marker=dict(color=COLORS["merged"], line=dict(width=0)),
        ))
    fig.update_layout(barmode="group", bargap=0.15)
    return _apply(fig, "PR Throughput")


def pr_cycle_hist(df: pd.DataFrame) -> go.Figure:
    closed = df[df["cycle_time_days"].notna() & (df["cycle_time_days"] >= 0)]
    if closed.empty: return go.Figure()
    fig = px.histogram(
        closed, x="cycle_time_days", nbins=25,
        color_discrete_sequence=[COLORS["merged"]],
    )
    fig.update_traces(marker_line_width=1, marker_line_color="#ffffff")
    fig.update_layout(bargap=0.1)
    return _apply(fig, "Cycle Time Distribution (Days)")


def pr_repo_bar(df: pd.DataFrame, n: int = 10) -> go.Figure:
    if df.empty: return go.Figure()
    counts = df["repository"].value_counts().head(n).reset_index()
    counts.columns = ["Repository", "Count"]
    fig = px.bar(
        counts, x="Count", y="Repository", orientation="h",
        color="Count",
        color_continuous_scale=[[0, "#f7f8fa"], [1, COLORS["purple"]]],
    )
    fig.update_layout(
        yaxis={"categoryorder": "total ascending"},
        coloraxis_showscale=False,
    )
    fig.update_traces(marker_line_width=0)
    return _apply(fig, "PRs by Repository")


def pr_author_bar(df: pd.DataFrame, n: int = 10) -> go.Figure:
    if df.empty or "author" not in df.columns: return go.Figure()
    counts = df["author"].value_counts().head(n).reset_index()
    counts.columns = ["Author", "PRs"]
    fig = px.bar(
        counts, x="PRs", y="Author", orientation="h",
        color="PRs",
        color_continuous_scale=[[0, "#f7f8fa"], [1, COLORS["blue"]]],
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
    if summary.empty: return go.Figure()
    top = summary.head(12)
    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Open",
        x=top["Repository"], y=top["Open_Issues"],
        marker=dict(color=COLORS["open"], line=dict(width=0)),
    ))
    fig.add_trace(go.Bar(
        name="Closed",
        x=top["Repository"], y=top["Closed_Issues"],
        marker=dict(color=COLORS["closed"], line=dict(width=0)),
    ))
    fig.update_layout(barmode="stack", xaxis_tickangle=-45)
    return _apply(fig, "Health per Repository")


def repo_health_radar(rs: pd.DataFrame) -> go.Figure:
    if rs.empty: return go.Figure()
    top = rs.head(5).copy()
    fig = go.Figure()
    for _, r in top.iterrows():
        fig.add_trace(go.Scatterpolar(
            r=[r["Closure_Rate%"], min(100, r["Open_Issues"]*2), min(100, r["Avg_Age_Days"])],
            theta=["Closure %", "Open Vol", "Avg Age"],
            fill="toself",
            name=r["Repository"]
        ))
    fig.update_layout(
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(visible=True, range=[0, 100], gridcolor="#e2e8f0"),
            angularaxis=dict(gridcolor="#e2e8f0")
        ),
        showlegend=True
    )
    return _apply(fig, "Repo Health Comparison")


# ──────────────────────────────────────────────────────────
# CONTRIBUTOR CHARTS
# ──────────────────────────────────────────────────────────

def contributor_bar(df: pd.DataFrame, n: int = 15) -> go.Figure:
    if df.empty: return go.Figure()
    top = df.head(n).copy()
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=top["Closed_Issues"], y=top["Author"],
        name="Closed", orientation="h",
        marker=dict(color=COLORS["closed"], line=dict(width=0)),
    ))
    fig.add_trace(go.Bar(
        x=top["Open_Issues"], y=top["Author"],
        name="Open", orientation="h",
        marker=dict(color=COLORS["open"], line=dict(width=0)),
    ))
    fig.update_layout(barmode="stack", yaxis={"categoryorder": "total ascending"})
    return _apply(fig, "Contributor Output")


def contributor_repos_scatter(df: pd.DataFrame) -> go.Figure:
    if df.empty: return go.Figure()
    fig = px.scatter(
        df.head(40), x="Repos_Active", y="Issues_Opened",
        size="Comments", color="Closed_Issues",
        hover_name="Author",
        color_continuous_scale=[[0, "#f7f8fa"], [0.5, COLORS["blue"]], [1, COLORS["orange"]]],
        size_max=30,
    )
    fig.update_traces(marker_line_width=1, marker_line_color="#ffffff")
    fig.update_layout(coloraxis_showscale=False)
    return _apply(fig, "Activity Heat Spread")


def contributor_heatmap(cs: pd.DataFrame, issues: pd.DataFrame) -> go.Figure:
    if cs.empty or issues.empty: return go.Figure()
    top = cs.head(20)["Author"].tolist()
    filtered = issues[issues["author"].isin(top)].copy()
    matrix = filtered.groupby(["author", "repository"]).size().reset_index(name="count")
    
    fig = go.Figure(data=go.Heatmap(
        x=matrix["repository"],
        y=matrix["author"],
        z=matrix["count"],
        colorscale=[[0, "#f7f8fa"], [1, COLORS["orange"]]],
        showscale=False
    ))
    fig.update_layout(xaxis_tickangle=-45)
    return _apply(fig, "Author x Repo Activity")


# ──────────────────────────────────────────────────────────
# TIMELINE / CALENDAR
# ──────────────────────────────────────────────────────────

def engineering_activity_timeline(issues: pd.DataFrame, prs: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    if not issues.empty:
        i = issues.groupby("date").size().reset_index(name="Issues")
        fig.add_trace(go.Scatter(
            x=i["date"], y=i["Issues"], mode="lines",
            name="Issues", fill="tozeroy",
            line=dict(color=COLORS["open"], width=2),
            fillcolor="rgba(196,22,42,0.05)",
        ))
    if not prs.empty and "date" in prs.columns:
        p = prs.groupby("date").size().reset_index(name="PRs")
        fig.add_trace(go.Scatter(
            x=p["date"], y=p["PRs"], mode="lines",
            name="PRs", fill="tozeroy",
            line=dict(color=COLORS["merged"], width=2),
            fillcolor="rgba(31,96,196,0.05)",
        ))
    return _apply(fig, "Engineering Pulse")


def activity_calendar_heatmap(df: pd.DataFrame, col: str = "date") -> go.Figure:
    if df.empty or col not in df.columns: return go.Figure()
    daily = df.groupby(col).size().reset_index(name="count")
    daily[col] = pd.to_datetime(daily[col])
    daily["dow"] = daily[col].dt.dayofweek
    daily["week"] = daily[col].dt.strftime("%Y-W%U")

    pivot = daily.pivot_table(index="dow", columns="week", values="count", fill_value=0)
    fig = go.Figure(data=go.Heatmap(
        z=pivot.values,
        x=pivot.columns.tolist(),
        y=["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
        colorscale=[[0, "#f7f8fa"], [0.2, "#e2e8f0"], [0.6, COLORS["orange"]], [1, "#d85a00"]],
        showscale=False,
        xgap=2, ygap=2,
    ))
    fig.update_layout(
        height=180,
        xaxis=dict(showticklabels=False, showgrid=False),
        yaxis=dict(showgrid=False, tickfont=dict(size=10)),
    )
    return _apply(fig, "Contribution Calendar")


def release_timeline(releases: pd.DataFrame) -> go.Figure:
    if releases.empty: return go.Figure()
    rel = releases.copy()
    rel["published_at"] = pd.to_datetime(rel["published_at"])
    fig = px.scatter(rel, x="published_at", y="repository", color="repository",
                     hover_name="tag", title="Release History")
    fig.update_traces(marker=dict(size=12, symbol="diamond"))
    return _apply(fig, "Release Timeline")
