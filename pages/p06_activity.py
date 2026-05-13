from datetime import datetime, timedelta, timezone

import pandas as pd
import streamlit as st

from utils.data_loader import load_issues, load_prs, load_releases
from utils.filters import apply_issue_filters, apply_pr_filters

_ICONS = {
    "issue_opened": "🟢",
    "issue_closed": "✅",
    "pr_opened":    "🔀",
    "pr_merged":    "🟣",
    "pr_closed":    "🔴",
    "release":      "🏷️",
}


def _build_feed(issues: pd.DataFrame, prs: pd.DataFrame, releases: pd.DataFrame) -> pd.DataFrame:
    rows = []
    if not issues.empty:
        for _, r in issues.iterrows():
            rows.append({
                "ts": r["created_at"], "type": "issue_opened",
                "repo": r["repository"], "title": r["title"],
                "actor": r["author"], "url": r.get("issue_url", ""),
                "meta": f"#{r['issue_number']}",
            })
            if r["state"] == "closed" and pd.notna(r.get("closed_at")):
                rows.append({
                    "ts": r["closed_at"], "type": "issue_closed",
                    "repo": r["repository"], "title": r["title"],
                    "actor": r["author"], "url": r.get("issue_url", ""),
                    "meta": f"#{r['issue_number']}",
                })
    if not prs.empty:
        for _, r in prs.iterrows():
            rows.append({
                "ts": r["created_at"], "type": "pr_opened",
                "repo": r["repository"], "title": r["title"],
                "actor": r["author"], "url": r.get("pr_url", ""),
                "meta": f"#{r['pr_number']}",
            })
            if r.get("merged") and pd.notna(r.get("merged_at")):
                rows.append({
                    "ts": r["merged_at"], "type": "pr_merged",
                    "repo": r["repository"], "title": r["title"],
                    "actor": r["author"], "url": r.get("pr_url", ""),
                    "meta": f"#{r['pr_number']}",
                })
    if not releases.empty:
        for _, r in releases.iterrows():
            rows.append({
                "ts": r.get("published_at", r.get("created_at")),
                "type": "release", "repo": r["repository"],
                "title": r.get("name") or r.get("tag", ""),
                "actor": r.get("author", ""), "url": r.get("release_url", ""),
                "meta": r.get("tag", ""),
            })
    if not rows: return pd.DataFrame()
    df = pd.DataFrame(rows)
    df["ts"] = pd.to_datetime(df["ts"], utc=True, errors="coerce")
    return df.dropna(subset=["ts"]).sort_values("ts", ascending=False).reset_index(drop=True)


def render():
    st.markdown("<div class='page-header'>📡 Activity Feed</div>", unsafe_allow_html=True)
    st.markdown("<div class='page-sub'>Chronological stream of engineering events across the organisation</div>",
                unsafe_allow_html=True)

    f        = st.session_state.get("filters", {})
    issues   = apply_issue_filters(load_issues(), f)
    prs      = apply_pr_filters(load_prs(), f)
    releases = load_releases()

    feed = _build_feed(issues, prs, releases)

    if feed.empty:
        st.markdown("<div class='sidebar-empty-msg'>No activity found for current filters.</div>", unsafe_allow_html=True)
        return

    # ── Controls ──────────────────────────────────────────
    st.markdown("<div class='section-header'>🔍 Feed Controls</div>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        event_types = st.multiselect(
            "Event Types",
            options=list(_ICONS.keys()),
            default=list(_ICONS.keys()),
            key="feed_types",
            format_func=lambda x: f"{_ICONS[x]} {x.replace('_', ' ').title()}",
        )
    with c2:
        days_back = st.selectbox(
            "Time window",
            [7, 14, 30, 60, 90, 180, 365, 9999],
            index=3,
            format_func=lambda x: "All time" if x == 9999 else f"Last {x} days",
            key="feed_window",
        )
    with c3:
        repo_filter = st.text_input("Repo search", key="feed_repo", placeholder="Filter repos…")
    with c4:
        actor_filter = st.text_input("Author search", key="feed_actor", placeholder="Filter people…")

    df = feed.copy()
    if event_types: df = df[df["type"].isin(event_types)]
    if days_back < 9999:
        cutoff = datetime.now(timezone.utc) - timedelta(days=days_back)
        df = df[df["ts"] >= cutoff]
    if repo_filter: df = df[df["repo"].str.contains(repo_filter, case=False, na=False)]
    if actor_filter: df = df[df["actor"].str.contains(actor_filter, case=False, na=False)]

    st.markdown("<div class='gradient-divider'></div>", unsafe_allow_html=True)

    # ── Feed ──────────────────────────────────────────────
    st.markdown(f"<div class='section-header'>📡 Live Activity · {len(df):,} events</div>", unsafe_allow_html=True)

    PAGE = 50
    total_pages = max(1, (len(df) - 1) // PAGE + 1)
    left, right = st.columns([6, 1])
    with right:
        pg = st.number_input("Page", 1, total_pages, 1, key="feed_page", label_visibility="collapsed")
    with left:
        st.caption(f"Showing page {pg} of {total_pages}")

    page_df = df.iloc[(pg - 1) * PAGE: pg * PAGE]
    items_html = ""
    for _, row in page_df.iterrows():
        icon  = _ICONS.get(row["type"], "•")
        ts    = row["ts"].strftime("%b %d, %H:%M") if pd.notna(row["ts"]) else ""
        url   = row.get("url", "")
        title = row.get("title", "")
        # Link styling
        link  = f'<a href="{url}" target="_blank" style="color:#24292e;text-decoration:none;font-weight:600;">{title}</a>' if url else f'<b>{title}</b>'
        
        type_badge = f'<span class="feed-type-badge">{row["type"].replace("_"," ").upper()}</span>'
        
        items_html += f"""
        <div class="feed-item">
          <div class="feed-icon">{icon}</div>
          <div class="feed-body">
            <div class="feed-title">{link}&nbsp;<span style="color:#718096;font-size:.7rem">{row.get('meta','')}</span></div>
            <div class="feed-meta">
              <span style="color:#1f60c4;font-weight:600">{row.get('repo','')}</span>
              &nbsp;·&nbsp;<span style="color:#4a5568">{row.get('actor','')}</span>
              &nbsp;·&nbsp;<span style="color:#a0aec0">{ts}</span>
              &nbsp;·&nbsp;{type_badge}
            </div>
          </div>
        </div>"""

    st.markdown(f'<div class="feed-container">{items_html}</div>', unsafe_allow_html=True)
