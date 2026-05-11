# ============================================================
# utils/report_gen.py
# PDF report generation via ReportLab.
# ============================================================

import io
from datetime import date, datetime

import pandas as pd

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table,
        TableStyle, HRFlowable, PageBreak,
    )
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    REPORTLAB_OK = True
except ImportError:
    REPORTLAB_OK = False


# ── Color palette ─────────────────────────────────────────
_BG    = colors.HexColor("#1e1e2e")
_SURF  = colors.HexColor("#181825")
_PURP  = colors.HexColor("#cba6f7")
_GREEN = colors.HexColor("#a6e3a1")
_RED   = colors.HexColor("#f38ba8")
_BLUE  = colors.HexColor("#89b4fa")
_TEXT  = colors.HexColor("#cdd6f4")
_MUTED = colors.HexColor("#7f849c")
_WHITE = colors.white
_BLACK = colors.black


def _styles():
    base = getSampleStyleSheet()
    return {
        "title":  ParagraphStyle("title",  fontSize=22, textColor=_WHITE,
                                 spaceAfter=6, alignment=TA_CENTER, fontName="Helvetica-Bold"),
        "sub":    ParagraphStyle("sub",    fontSize=11, textColor=_MUTED,
                                 spaceAfter=12, alignment=TA_CENTER),
        "h1":     ParagraphStyle("h1",     fontSize=14, textColor=_PURP,
                                 spaceBefore=14, spaceAfter=4, fontName="Helvetica-Bold"),
        "h2":     ParagraphStyle("h2",     fontSize=11, textColor=_TEXT,
                                 spaceBefore=8,  spaceAfter=4, fontName="Helvetica-Bold"),
        "body":   ParagraphStyle("body",   fontSize=9,  textColor=_TEXT,
                                 leading=14, spaceAfter=4),
        "kpi_v":  ParagraphStyle("kpi_v",  fontSize=20, textColor=_WHITE,
                                 alignment=TA_CENTER, fontName="Helvetica-Bold"),
        "kpi_l":  ParagraphStyle("kpi_l",  fontSize=8,  textColor=_MUTED,
                                 alignment=TA_CENTER),
    }


def _kpi_table(metrics: dict, styles: dict) -> Table:
    """Build a horizontal KPI summary table."""
    keys   = ["total_issues", "open_issues", "closed_issues", "total_prs",
              "merged_prs", "contributors", "total_releases", "stale_issues"]
    labels = ["Total Issues", "Open", "Closed", "Total PRs",
              "Merged PRs", "Contributors", "Releases", "Stale (>30d)"]
    values = [str(metrics.get(k, "—")) for k in keys]

    data = [
        [Paragraph(v, styles["kpi_v"]) for v in values],
        [Paragraph(l, styles["kpi_l"]) for l in labels],
    ]
    t = Table(data, colWidths=[2.1 * cm] * len(keys))
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), _SURF),
        ("BOX",        (0, 0), (-1, -1), 0.5, _MUTED),
        ("INNERGRID",  (0, 0), (-1, -1), 0.3, colors.HexColor("#313244")),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [_SURF, _BG]),
        ("TOPPADDING",  (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 8),
    ]))
    return t


def _df_table(df: pd.DataFrame, max_rows: int = 30, col_widths=None) -> Table:
    """Convert a DataFrame to a ReportLab Table."""
    cols = list(df.columns)
    rows = [cols] + df.head(max_rows).astype(str).values.tolist()

    num_cols = len(cols)
    page_width = A4[0] - 3 * cm
    cw = col_widths or [page_width / num_cols] * num_cols

    t = Table(rows, colWidths=cw, repeatRows=1)
    style = [
        # Header
        ("BACKGROUND",   (0, 0), (-1, 0), _BG),
        ("TEXTCOLOR",    (0, 0), (-1, 0), _PURP),
        ("FONTNAME",     (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",     (0, 0), (-1, 0), 8),
        ("BOTTOMPADDING",(0, 0), (-1, 0), 6),
        ("TOPPADDING",   (0, 0), (-1, 0), 6),
        # Body
        ("FONTSIZE",  (0, 1), (-1, -1), 7),
        ("TEXTCOLOR", (0, 1), (-1, -1), _TEXT),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [_SURF, _BG]),
        ("TOPPADDING",    (0, 1), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 1), (-1, -1), 4),
        # Grid
        ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#313244")),
        ("BOX",  (0, 0), (-1, -1), 0.5, _MUTED),
    ]
    t.setStyle(TableStyle(style))
    return t


def generate_pdf(
    metrics: dict,
    issues: pd.DataFrame,
    prs: pd.DataFrame,
    contributors: pd.DataFrame,
    repo_summary: pd.DataFrame,
    report_type: str = "Daily",
    selected_date: date | None = None,
    date_range: tuple | None = None,
) -> bytes:
    """
    Generate a PDF report and return raw bytes.
    report_type: "Daily" | "Weekly" | "Monthly" | "Custom"
    """
    if not REPORTLAB_OK:
        raise ImportError("reportlab is not installed. Run: pip install reportlab")

    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=1.5 * cm, rightMargin=1.5 * cm,
        topMargin=1.5 * cm, bottomMargin=1.5 * cm,
    )
    styles = _styles()
    story  = []

    # ── Cover ─────────────────────────────────────────────
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    if report_type == "Daily" and selected_date:
        period_str = f"Daily Report — {selected_date}"
    elif report_type == "Custom" and date_range:
        period_str = f"Custom Report — {date_range[0]} to {date_range[1]}"
    else:
        period_str = f"{report_type} Report — generated {now_str}"

    story.append(Spacer(1, 1 * cm))
    story.append(Paragraph("🚀 Engineering Intelligence Dashboard", styles["title"]))
    story.append(Paragraph("Simtestlab · GitHub Analytics Platform", styles["sub"]))
    story.append(Paragraph(period_str, styles["sub"]))
    story.append(HRFlowable(width="100%", thickness=0.5, color=_MUTED, spaceAfter=16))

    # ── KPI Summary ───────────────────────────────────────
    story.append(Paragraph("Executive KPI Summary", styles["h1"]))
    story.append(_kpi_table(metrics, styles))
    story.append(Spacer(1, 0.4 * cm))

    # ── Repository Summary ────────────────────────────────
    if not repo_summary.empty:
        story.append(Paragraph("Repository Metrics", styles["h1"]))
        cols_to_show = ["Repository", "Total_Issues", "Open_Issues",
                        "Closed_Issues", "Contributors", "Closure_Rate%"]
        cols_to_show = [c for c in cols_to_show if c in repo_summary.columns]
        cws = [3.5*cm] + [1.8*cm] * (len(cols_to_show) - 1)
        story.append(_df_table(repo_summary[cols_to_show].head(20), col_widths=cws))
        story.append(Spacer(1, 0.3 * cm))

    story.append(PageBreak())

    # ── Issues Summary ────────────────────────────────────
    if not issues.empty:
        story.append(Paragraph("Issues Summary", styles["h1"]))
        i_cols = ["repository", "issue_number", "title", "state",
                  "author", "age_days", "comments"]
        i_cols = [c for c in i_cols if c in issues.columns]
        cws = [2.5*cm, 1.2*cm, 5.5*cm, 1.2*cm, 2*cm, 1.2*cm, 1.2*cm][:len(i_cols)]
        story.append(_df_table(issues[i_cols].head(40), col_widths=cws))
        story.append(Spacer(1, 0.3 * cm))

    story.append(PageBreak())

    # ── Pull Request Summary ──────────────────────────────
    if not prs.empty:
        story.append(Paragraph("Pull Request Summary", styles["h1"]))
        p_cols = ["repository", "pr_number", "title", "state",
                  "author", "merged", "cycle_time_days"]
        p_cols = [c for c in p_cols if c in prs.columns]
        cws = [2.5*cm, 1.2*cm, 5*cm, 1.2*cm, 2*cm, 1.2*cm, 1.6*cm][:len(p_cols)]
        story.append(_df_table(prs[p_cols].head(30), col_widths=cws))
        story.append(Spacer(1, 0.3 * cm))

    story.append(PageBreak())

    # ── Contributor Analytics ─────────────────────────────
    if not contributors.empty:
        story.append(Paragraph("Contributor Analytics", styles["h1"]))
        c_cols = ["Author", "Issues_Opened", "Open_Issues",
                  "Closed_Issues", "Repos_Active", "Comments"]
        c_cols = [c for c in c_cols if c in contributors.columns]
        story.append(_df_table(contributors[c_cols].head(25)))
        story.append(Spacer(1, 0.3 * cm))

    # ── Footer ────────────────────────────────────────────
    story.append(HRFlowable(width="100%", thickness=0.5, color=_MUTED))
    story.append(Spacer(1, 0.2 * cm))
    story.append(Paragraph(
        f"Generated by Engineering Intelligence Dashboard · {now_str}",
        styles["body"]
    ))

    doc.build(story)
    return buf.getvalue()
