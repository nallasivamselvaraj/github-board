# utils/report_gen.py  –  Professional PDF Report Generator
import io, os
from datetime import date, datetime

import pandas as pd

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table,
        TableStyle, HRFlowable, PageBreak, Image, KeepTogether,
    )
    from reportlab.graphics.shapes import Drawing, Rect, String
    from reportlab.graphics import renderPDF
    REPORTLAB_OK = True
except ImportError:
    REPORTLAB_OK = False

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    MPL_OK = True
except ImportError:
    MPL_OK = False

# ── Palette ──────────────────────────────────────────────────────
C_BG     = "#ffffff"
C_SURF   = "#f7f8fa"
C_ACCENT = "#f46800"
C_BLUE   = "#1f60c4"
C_GREEN  = "#36a347"
C_RED    = "#c4162a"
C_YELLOW = "#e0b400"
C_TEXT   = "#24292e"
C_MUTED  = "#718096"
C_BORDER = "#d8dce0"
C_WHITE  = "#ffffff"

_BG     = colors.white
_SURF   = colors.HexColor(C_SURF)
_ACCENT = colors.HexColor(C_ACCENT)
_BLUE   = colors.HexColor(C_BLUE)
_GREEN  = colors.HexColor(C_GREEN)
_RED    = colors.HexColor(C_RED)
_YELLOW = colors.HexColor(C_YELLOW)
_TEXT   = colors.HexColor(C_TEXT)
_MUTED  = colors.HexColor(C_MUTED)
_BORDER = colors.HexColor(C_BORDER)
_WHITE  = colors.white

_USABLE_W = 18.0 * cm

# ── Paragraph styles ─────────────────────────────────────────────
def _styles():
    return {
        "cover_title": ParagraphStyle("cover_title", fontSize=24,
            textColor=_TEXT, alignment=TA_CENTER, fontName="Helvetica-Bold",
            spaceAfter=6, leading=30),
        "cover_sub": ParagraphStyle("cover_sub", fontSize=11,
            textColor=_ACCENT, alignment=TA_CENTER, spaceAfter=4,
            fontName="Helvetica-Bold"),
        "cover_badge": ParagraphStyle("cover_badge", fontSize=10,
            textColor=_WHITE, alignment=TA_CENTER, fontName="Helvetica-Bold",
            spaceAfter=6),
        "cover_period": ParagraphStyle("cover_period", fontSize=13,
            textColor=_TEXT, alignment=TA_CENTER, fontName="Helvetica-Bold",
            spaceAfter=2, leading=16),
        "cover_scope": ParagraphStyle("cover_scope", fontSize=9,
            textColor=_MUTED, alignment=TA_CENTER, spaceAfter=2),
        "cover_meta": ParagraphStyle("cover_meta", fontSize=8,
            textColor=_MUTED, alignment=TA_CENTER, spaceAfter=2),
        "h1": ParagraphStyle("h1", fontSize=12, textColor=_ACCENT,
            fontName="Helvetica-Bold", spaceBefore=14, spaceAfter=8),
        "h2": ParagraphStyle("h2", fontSize=9, textColor=_TEXT,
            fontName="Helvetica-Bold", spaceBefore=10, spaceAfter=5),
        "body": ParagraphStyle("body", fontSize=8, textColor=_MUTED,
            leading=12, spaceAfter=4),
        "note": ParagraphStyle("note", fontSize=7.5, textColor=_MUTED,
            leading=11, spaceAfter=3, fontName="Helvetica"),
        "kpi_v": ParagraphStyle("kpi_v", fontSize=19, textColor=_TEXT,
            alignment=TA_CENTER, fontName="Helvetica-Bold", leading=23),
        "kpi_l": ParagraphStyle("kpi_l", fontSize=6.5, textColor=_MUTED,
            alignment=TA_CENTER, leading=9, fontName="Helvetica-Bold"),
        "th": ParagraphStyle("th", fontSize=7, textColor=_WHITE,
            fontName="Helvetica-Bold", leading=9, alignment=TA_LEFT, wordWrap="CJK"),
        "td": ParagraphStyle("td", fontSize=7, textColor=_TEXT,
            fontName="Helvetica", leading=9, alignment=TA_LEFT, wordWrap="CJK"),
        "td_c": ParagraphStyle("td_c", fontSize=7, textColor=_TEXT,
            fontName="Helvetica", leading=9, alignment=TA_CENTER, wordWrap="CJK"),
        "td_green": ParagraphStyle("td_green", fontSize=7, textColor=_GREEN,
            fontName="Helvetica-Bold", leading=9, alignment=TA_CENTER, wordWrap="CJK"),
        "td_red": ParagraphStyle("td_red", fontSize=7, textColor=_RED,
            fontName="Helvetica-Bold", leading=9, alignment=TA_CENTER, wordWrap="CJK"),
        "td_muted": ParagraphStyle("td_muted", fontSize=7, textColor=_MUTED,
            fontName="Helvetica", leading=9, alignment=TA_CENTER, wordWrap="CJK"),
    }


# ── Header / footer on every page ────────────────────────────────
def _header_footer(canvas, doc):
    canvas.saveState()
    w, h = A4
    canvas.setFillColor(_ACCENT)
    canvas.rect(0, h - 0.5*cm, w, 0.5*cm, fill=1, stroke=0)
    canvas.setFont("Helvetica-Bold", 7)
    canvas.setFillColor(_WHITE)
    canvas.drawString(1.5*cm, h - 0.35*cm, "SIMTESTLAB  ·  ENGINEERING INTELLIGENCE")
    canvas.drawRightString(w - 1.5*cm, h - 0.35*cm,
                           f"Generated {datetime.now().strftime('%Y-%m-%d  %H:%M')}")
    canvas.setStrokeColor(_BORDER)
    canvas.setLineWidth(0.5)
    canvas.line(1.5*cm, 1.0*cm, w - 1.5*cm, 1.0*cm)
    canvas.setFont("Helvetica", 7)
    canvas.setFillColor(_MUTED)
    canvas.drawCentredString(w / 2, 0.55*cm, f"Page {doc.page}")
    canvas.restoreState()


_first_page  = _header_footer
_later_pages = _header_footer


# ── Logo drawing ─────────────────────────────────────────────────
def _make_logo_drawing() -> Drawing:
    d = Drawing(170, 65)
    d.add(Rect(0, 0, 170, 65, fillColor=_ACCENT, strokeColor=None, rx=5, ry=5))
    d.add(String(85, 26, "SIMTESTLAB", fontSize=22, fillColor=_WHITE,
                 fontName="Helvetica-Bold", textAnchor="middle"))
    d.add(String(85, 12, "ENGINEERING INTELLIGENCE", fontSize=7, fillColor=_WHITE,
                 fontName="Helvetica", textAnchor="middle"))
    return d


def _report_type_badge(report_type: str) -> Drawing:
    label = f"{report_type.upper()}  REPORT"
    d = Drawing(120, 22)
    d.add(Rect(0, 0, 120, 22, fillColor=_ACCENT, strokeColor=None, rx=4, ry=4))
    d.add(String(60, 7, label, fontSize=8, fillColor=_WHITE,
                 fontName="Helvetica-Bold", textAnchor="middle"))
    return d


# ── Section heading ───────────────────────────────────────────────
def _section(title: str, styles: dict, count: int | None = None) -> list:
    label = f"{title.upper()}  ({count})" if count is not None else title.upper()
    return [
        Spacer(1, 0.3*cm),
        Paragraph(label, styles["h1"]),
        HRFlowable(width="100%", thickness=0.7, color=_ACCENT, spaceAfter=6),
    ]


# ── KPI activity grid (7 cells) ──────────────────────────────────
def _kpi_table(metrics: dict, styles: dict) -> Table:
    keys   = ["opened_issues", "closed_issues", "updated_issues",
              "total_prs",    "merged_prs",    "contributors"]
    labels = ["ISSUES OPENED", "ISSUES CLOSED", "ISSUES UPDATED",
              "PRS OPENED",    "PRS MERGED",    "CONTRIBUTORS"]
    clr_map = {
        "opened_issues":  C_TEXT,
        "closed_issues":  C_GREEN,
        "updated_issues": C_BLUE,
        "merged_prs":     C_GREEN,
        "contributors":   C_BLUE,
    }

    colored = []
    for k, lbl in zip(keys, labels):
        v = metrics.get(k, 0)
        try:
            fv = float(v)
            v  = str(int(fv)) if fv == int(fv) else str(round(fv, 1))
        except Exception:
            v = str(v)

        c = clr_map.get(k, C_TEXT)
        if k == "closure_rate":
            try:
                c = C_GREEN if float(v) >= 60 else (C_ACCENT if float(v) >= 30 else C_RED)
            except Exception:
                pass
        colored.append(Paragraph(f"<font color='{c}'><b>{v}</b></font>", styles["kpi_v"]))

    cw = [_USABLE_W / 6] * 6
    t  = Table(
        [colored, [Paragraph(l, styles["kpi_l"]) for l in labels]],
        colWidths=cw,
    )
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), _SURF),
        ("BOX",           (0, 0), (-1, -1), 0.8, _ACCENT),
        ("INNERGRID",     (0, 0), (-1, -1), 0.4, _BORDER),
        ("TOPPADDING",    (0, 0), (-1, -1), 14),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 14),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
    ]))
    return t


# ── Shared table renderer ─────────────────────────────────────────
_TABLE_STYLE = [
    ("BACKGROUND",    (0, 0), (-1, 0),  _ACCENT),
    ("ROWBACKGROUNDS",(0, 1), (-1, -1), [_WHITE, _SURF]),
    ("GRID",          (0, 0), (-1, -1), 0.3, _BORDER),
    ("BOX",           (0, 0), (-1, -1), 0.6, _ACCENT),
    ("TOPPADDING",    (0, 0), (-1, -1), 5),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ("LEFTPADDING",   (0, 0), (-1, -1), 5),
    ("RIGHTPADDING",  (0, 0), (-1, -1), 5),
    ("VALIGN",        (0, 0), (-1, -1), "TOP"),
]


def _safe(val) -> str:
    try:
        return "" if pd.isna(val) else str(val)
    except Exception:
        return str(val)


# Short display names for column headers — prevents multi-line wrapping in narrow cells
_HDR = {
    "issue_number": "#",
    "created_date": "Created",
    "updated_date": "Updated",
    "closed_date":  "Closed",
    "age_days":     "Age",
    "commented":    "Comm.",
    "days_since_update": "Stale",
}


def _th(col: str, styles: dict) -> Paragraph:
    label = _HDR.get(col, col.replace("_", " ").title())
    return Paragraph(label.upper(), styles["th"])


def _state_cell(val, st_dict: dict) -> Paragraph:
    s = _safe(val).lower()
    if s == "open":
        return Paragraph(f"<font color='{C_RED}'><b>OPEN</b></font>", st_dict["td_c"])
    if s == "closed":
        return Paragraph(f"<font color='{C_GREEN}'><b>CLOSED</b></font>", st_dict["td_c"])
    return Paragraph(s.upper(), st_dict["td_c"])


# ── Issues Opened in Period ───────────────────────────────────────
def _opened_issues_section(issues: pd.DataFrame, styles: dict) -> list:
    if issues is None or issues.empty:
        return [Paragraph("No issues were opened in this period.", styles["body"])]

    wanted = ["repository", "issue_number", "title", "state", "author", "labels", "created_date"]
    cols   = [c for c in wanted if c in issues.columns]
    df     = issues[cols].head(50).copy()
    if "created_date" in df.columns:
        df["created_date"] = df["created_date"].astype(str)

    # Widths sum to exactly 18 cm
    w_map = {
        "repository":   3.5*cm, "issue_number": 0.8*cm, "title":        6.2*cm,
        "state":        1.6*cm, "author":       2.4*cm, "labels":       2.2*cm,
        "created_date": 1.3*cm,
    }
    cw = [w_map.get(c, 2.0*cm) for c in cols]

    def _td(v):  return Paragraph(_safe(v), styles["td"])
    def _tdc(v): return Paragraph(_safe(v), styles["td_c"])

    rows = [[_th(c, styles) for c in cols]]
    for _, row in df.iterrows():
        cells = []
        for c in cols:
            if c == "state":
                cells.append(_state_cell(row[c], styles))
            elif c in ("issue_number", "created_date"):
                cells.append(_tdc(row[c]))
            else:
                cells.append(_td(row[c]))
        rows.append(cells)

    t = Table(rows, colWidths=cw, repeatRows=1)
    t.setStyle(TableStyle(_TABLE_STYLE))
    note = Paragraph(
        f"Showing {min(50, len(issues))} of {len(issues)} issues opened in this period.",
        styles["note"],
    )
    return [t, Spacer(1, 0.25*cm), note]


# ── Issues Closed in Period ───────────────────────────────────────
def _closed_issues_section(issues_closed: pd.DataFrame, styles: dict) -> list:
    if issues_closed is None or issues_closed.empty:
        return [Paragraph("No issues were closed in this period.", styles["body"])]

    wanted = ["repository", "issue_number", "title", "author", "labels", "closed_date", "age_days"]
    cols   = [c for c in wanted if c in issues_closed.columns]
    df     = issues_closed[cols].head(50).copy()
    if "closed_date" in df.columns:
        df["closed_date"] = df["closed_date"].astype(str)
    if "age_days" in df.columns:
        df["age_days"] = df["age_days"].astype(str) + " d"

    # Widths sum to exactly 18 cm
    w_map = {
        "repository":   3.5*cm, "issue_number": 0.8*cm, "title":       6.5*cm,
        "author":       2.5*cm, "labels":       2.2*cm, "closed_date": 1.7*cm,
        "age_days":     0.8*cm,
    }
    cw = [w_map.get(c, 2.0*cm) for c in cols]

    def _td(v):  return Paragraph(_safe(v), styles["td"])
    def _tdc(v): return Paragraph(_safe(v), styles["td_c"])

    rows = [[_th(c, styles) for c in cols]]
    for _, row in df.iterrows():
        cells = [
            _tdc(row[c]) if c in ("issue_number", "closed_date", "age_days") else _td(row[c])
            for c in cols
        ]
        rows.append(cells)

    t = Table(rows, colWidths=cw, repeatRows=1)
    t.setStyle(TableStyle(_TABLE_STYLE))
    note = Paragraph(
        f"Showing {min(50, len(issues_closed))} of {len(issues_closed)} issues closed in this period.",
        styles["note"],
    )
    return [t, Spacer(1, 0.25*cm), note]


# ── Issues Updated in Period ──────────────────────────────────────
def _updated_issues_section(issues_updated: pd.DataFrame, styles: dict) -> list:
    if issues_updated is None or issues_updated.empty:
        return [Paragraph("No issues were updated in this period.", styles["body"])]

    wanted = ["repository", "issue_number", "title", "state", "author", "commented", "updated_date"]
    cols   = [c for c in wanted if c in issues_updated.columns]
    df     = issues_updated[cols].head(50).copy()
    if "commented" in df.columns:
        df["commented"] = df["commented"].map({True: "Yes", False: "No"}).fillna("No")
    if "updated_date" in df.columns:
        df["updated_date"] = df["updated_date"].astype(str)

    # Widths sum to exactly 18 cm
    w_map = {
        "repository":   3.5*cm, "issue_number": 0.8*cm, "title":       5.8*cm,
        "state":        1.6*cm, "author":       2.5*cm, "commented":   1.5*cm,
        "updated_date": 2.3*cm,
    }
    cw = [w_map.get(c, 2.0*cm) for c in cols]

    def _td(v):  return Paragraph(_safe(v), styles["td"])
    def _tdc(v): return Paragraph(_safe(v), styles["td_c"])

    rows = [[_th(c, styles) for c in cols]]
    for _, row in df.iterrows():
        cells = []
        for c in cols:
            if c == "state":
                cells.append(_state_cell(row[c], styles))
            elif c == "commented":
                v = _safe(row[c])
                cells.append(
                    Paragraph(f"<font color='{C_GREEN}'><b>{v}</b></font>", styles["td_c"])
                    if v == "Yes"
                    else Paragraph(v, styles["td_muted"])
                )
            elif c in ("issue_number", "updated_date"):
                cells.append(_tdc(row[c]))
            else:
                cells.append(_td(row[c]))
        rows.append(cells)

    t = Table(rows, colWidths=cw, repeatRows=1)
    t.setStyle(TableStyle(_TABLE_STYLE))
    note = Paragraph(
        f"Showing {min(50, len(issues_updated))} of {len(issues_updated)} issues "
        "updated in this period (includes opened and closed issues).",
        styles["note"],
    )
    return [t, Spacer(1, 0.25*cm), note]


# ── Generic DataFrame → PDF table ────────────────────────────────
def _df_table(df: pd.DataFrame, max_rows: int = 30,
              col_widths=None, grade_col: str | None = None) -> Table:
    if df.empty:
        return Table([["No data"]], colWidths=[_USABLE_W])
    display   = df.head(max_rows).copy()
    col_names = list(display.columns)
    cw = col_widths or [_USABLE_W / len(col_names)] * len(col_names)
    st = _styles()

    def _th(t):  return Paragraph(str(t).upper().replace("_", " "), st["th"])
    def _td(v):  return Paragraph(_safe(v), st["td"])

    header_row = [_th(c) for c in col_names]
    data_rows  = [[_td(v) for v in row] for row in display.itertuples(index=False)]
    t = Table([header_row] + data_rows, colWidths=cw, repeatRows=1)

    style = list(_TABLE_STYLE)
    if grade_col:
        gc_map = {"A": _GREEN, "B": _BLUE, "C": _YELLOW, "D": _ACCENT, "F": _RED}
        upper_cols = [c.upper() for c in col_names]
        if grade_col.upper() in upper_cols:
            gi = upper_cols.index(grade_col.upper())
            for ri_idx, _ in enumerate(data_rows, 1):
                raw = display.iloc[ri_idx - 1][col_names[gi]]
                gc  = gc_map.get(str(raw), _TEXT)
                style += [("TEXTCOLOR", (gi, ri_idx), (gi, ri_idx), gc),
                          ("FONTNAME",  (gi, ri_idx), (gi, ri_idx), "Helvetica-Bold")]
    t.setStyle(TableStyle(style))
    return t


# ── Matplotlib chart helpers ──────────────────────────────────────
_MPL = {"facecolor": C_BG, "text": C_TEXT, "grid": "#e2e8f0",
        "open": C_RED, "closed": C_GREEN, "accent": C_ACCENT}


def _mpl_buf(fig) -> io.BytesIO:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=130, bbox_inches="tight",
                facecolor=_MPL["facecolor"], edgecolor="none")
    plt.close(fig)
    buf.seek(0)
    return buf


def _chart_issues_bar(issues: pd.DataFrame) -> io.BytesIO | None:
    if not MPL_OK or issues.empty or "state" not in issues.columns:
        return None
    grp  = issues.groupby("state").size()
    fig, ax = plt.subplots(figsize=(5, 2.8), facecolor=_MPL["facecolor"])
    clrs = [_MPL["open"] if s == "open" else _MPL["closed"] for s in grp.index]
    bars = ax.bar(grp.index, grp.values, color=clrs, width=0.5, zorder=3)
    ax.bar_label(bars, fmt="%d", color=_MPL["text"], fontsize=9, padding=3)
    ax.set_facecolor(_MPL["facecolor"])
    ax.set_title("ISSUES BY STATE", color=_MPL["text"], fontsize=9, pad=8,
                 fontfamily="sans-serif", fontweight="bold")
    ax.tick_params(colors=_MPL["text"], labelsize=8)
    ax.spines[:].set_visible(False)
    ax.yaxis.grid(True, color=_MPL["grid"], linewidth=0.6)
    return _mpl_buf(fig)


def _chart_pr_pie(prs: pd.DataFrame) -> io.BytesIO | None:
    if not MPL_OK or prs.empty:
        return None
    merged = int(prs.get("merged", pd.Series(dtype=bool)).sum()) if "merged" in prs.columns else 0
    open_  = int((prs["state"] == "open").sum()) if "state" in prs.columns else 0
    closed = max(0, len(prs) - merged - open_)
    pairs  = [(v, l, c) for v, l, c in
              zip([merged, open_, closed], ["Merged", "Open", "Closed"],
                  [C_BLUE, C_RED, C_ACCENT]) if v > 0]
    if not pairs:
        return None
    vals, labels, clrs = zip(*pairs)
    fig, ax = plt.subplots(figsize=(4, 2.8), facecolor=_MPL["facecolor"])
    ax.pie(vals, labels=labels, colors=clrs, autopct="%1.0f%%", startangle=140,
           textprops={"fontsize": 8})
    ax.set_title("PR STATUS", color=_MPL["text"], fontsize=9,
                 fontfamily="sans-serif", fontweight="bold")
    return _mpl_buf(fig)


def _chart_activity_trend(issues_updated: pd.DataFrame) -> io.BytesIO | None:
    """Daily activity bars for the period (uses updated issues for richer signal)."""
    if not MPL_OK or issues_updated.empty or "updated_date" not in issues_updated.columns:
        return None
    try:
        df = issues_updated.copy()
        df["updated_date"] = pd.to_datetime(df["updated_date"])
        daily = df.groupby([df["updated_date"].dt.date, "state"]).size().unstack(fill_value=0)
        if daily.empty:
            return None
        daily.index = [str(d) for d in daily.index]
        fig, ax = plt.subplots(figsize=(8, 2.8), facecolor=_MPL["facecolor"])
        if "open" in daily.columns:
            ax.bar(daily.index, daily["open"],   color=C_RED,   label="Open",   alpha=0.85)
        if "closed" in daily.columns:
            ax.bar(daily.index, daily["closed"], color=C_GREEN, label="Closed", alpha=0.85,
                   bottom=daily.get("open", 0))
        ax.set_title("DAILY ACTIVITY (UPDATED ISSUES)", color=_MPL["text"], fontsize=9,
                     pad=8, fontfamily="sans-serif", fontweight="bold")
        ax.tick_params(colors=_MPL["text"], labelsize=7, axis="x", rotation=30)
        ax.tick_params(colors=_MPL["text"], labelsize=7, axis="y")
        ax.yaxis.grid(True, color=_MPL["grid"], linewidth=0.6)
        ax.spines[:].set_visible(False)
        ax.legend(fontsize=7)
        return _mpl_buf(fig)
    except Exception:
        return None


def _buf_to_image(buf, width_cm: float = 8) -> Image | None:
    if buf is None:
        return None
    try:
        img = Image(buf)
        img.drawWidth  = width_cm * cm
        img.drawHeight = width_cm * cm * (img.imageHeight / img.imageWidth)
        return img
    except Exception:
        return None


# ── Main entry point ──────────────────────────────────────────────
def generate_pdf(
    metrics: dict,
    issues: pd.DataFrame,
    prs: pd.DataFrame,
    contributors: pd.DataFrame,
    repo_summary: pd.DataFrame,
    report_type: str = "Daily",
    selected_date: date | None = None,
    date_range: tuple | None = None,
    issues_updated: pd.DataFrame | None = None,
    issues_closed: pd.DataFrame | None = None,
    period_label: str | None = None,
    scope_label: str | None = None,
) -> bytes:
    if not REPORTLAB_OK:
        raise ImportError("reportlab missing.")

    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=1.5*cm, rightMargin=1.5*cm,
        topMargin=2.0*cm,  bottomMargin=1.8*cm,
        title="Engineering Intelligence Report",
    )
    styles = _styles()
    story  = []

    # ── Cover ────────────────────────────────────────────────
    story.append(Spacer(1, 1.2*cm))

    drw = _make_logo_drawing()
    drw.hAlign = "CENTER"
    story.append(drw)
    story.append(Spacer(1, 0.6*cm))

    bdg = _report_type_badge(report_type)
    bdg.hAlign = "CENTER"
    story.append(bdg)
    story.append(Spacer(1, 0.5*cm))

    story.append(Paragraph("Engineering Intelligence Dashboard", styles["cover_title"]))
    story.append(Paragraph("Simtestlab  ·  Real-time GitHub Analytics", styles["cover_sub"]))
    story.append(Spacer(1, 0.5*cm))

    if period_label:
        story.append(Paragraph(period_label, styles["cover_period"]))
    if scope_label:
        story.append(Paragraph(f"Scope: {scope_label}", styles["cover_scope"]))

    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph(
        f"Generated  {datetime.now().strftime('%Y-%m-%d  %H:%M')}",
        styles["cover_meta"],
    ))
    story.append(Spacer(1, 0.8*cm))
    story.append(HRFlowable(width="100%", thickness=1.5, color=_ACCENT, spaceAfter=12))

    # ── KPI activity grid ─────────────────────────────────────
    story.append(Paragraph("PERIOD ACTIVITY SUMMARY", styles["h1"]))
    story.append(_kpi_table(metrics, styles))
    story.append(Spacer(1, 0.6*cm))

    # ── Issue Detail Pages (flow naturally after KPI — no forced break) ──
    story.append(PageBreak())

    story += _section("Issues Opened in Period", styles, count=len(issues))
    story += _opened_issues_section(issues, styles)

    story += _section(
        "Issues Closed in Period", styles,
        count=len(issues_closed) if issues_closed is not None else 0,
    )
    story += _closed_issues_section(issues_closed, styles)

    if issues_updated is not None:
        story += _section("Issues Updated in Period", styles, count=len(issues_updated))
        story += _updated_issues_section(issues_updated, styles)

    # ── Repository Health + Contributors on same page ─────────
    has_repo   = not repo_summary.empty
    has_contrib = not contributors.empty
    if has_repo or has_contrib:
        story.append(PageBreak())

    if has_repo:
        story += _section("Repository Health Overview", styles)
        rs_wanted = ["Repository", "Total_Issues", "Open_Issues", "Closed_Issues", "Closure_Rate%"]
        rs_cols   = [c for c in rs_wanted if c in repo_summary.columns]
        rs_rename = {
            "Total_Issues": "Total", "Open_Issues": "Open",
            "Closed_Issues": "Closed", "Closure_Rate%": "Closure %",
        }
        rs_display = repo_summary[rs_cols].head(30).rename(columns=rs_rename)
        rs_cw_map  = {
            "Repository": 6.0*cm, "Total": 2.5*cm,
            "Open":       2.5*cm, "Closed": 2.5*cm, "Closure %": 4.5*cm,
        }
        story.append(_df_table(
            rs_display,
            col_widths=[rs_cw_map.get(rs_rename.get(c, c), 3.0*cm) for c in rs_cols],
        ))

    if has_contrib:
        story += _section("Contributor Analytics", styles)
        ct_wanted = ["Author", "Issues_Opened", "Open_Issues", "Closed_Issues", "Repos_Active"]
        ct_cols   = [c for c in ct_wanted if c in contributors.columns]
        ct_rename = {
            "Issues_Opened": "Opened", "Open_Issues": "Open",
            "Closed_Issues": "Closed", "Repos_Active": "Repos Active",
        }
        ct_display = contributors[ct_cols].head(35).rename(columns=ct_rename)
        ct_cw_map  = {
            "Author": 6.0*cm, "Opened": 2.5*cm,
            "Open":   2.5*cm, "Closed": 2.5*cm, "Repos Active": 4.5*cm,
        }
        story.append(_df_table(
            ct_display,
            col_widths=[ct_cw_map.get(ct_rename.get(c, c), 3.0*cm) for c in ct_cols],
        ))

    doc.build(story, onFirstPage=_first_page, onLaterPages=_later_pages)
    return buf.getvalue()
