# utils/report_gen.py  –  Grafana-style Professional Light PDF
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
    from reportlab.graphics.shapes import Drawing, Rect, String, Circle
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

# ── Grafana Light Palette ──────────────────────────────────
_BG      = colors.white
_SURF    = colors.HexColor("#f7f8fa")   # Light gray panel
_SURF2   = colors.white
_ACCENT  = colors.HexColor("#f46800")   # Grafana Orange
_BLUE    = colors.HexColor("#1f60c4")   # Blue
_GREEN   = colors.HexColor("#36a347")   # Green
_RED     = colors.HexColor("#c4162a")   # Red
_YELLOW  = colors.HexColor("#e0b400")   # Yellow
_TEXT    = colors.HexColor("#24292e")   # Primary text
_MUTED   = colors.HexColor("#718096")   # Secondary text
_BORDER  = colors.HexColor("#d8dce0")   # Border
_WHITE   = colors.white

LOGO_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "logo.png")

# ── Styles ────────────────────────────────────────────────
def _styles():
    return {
        "cover_title": ParagraphStyle("cover_title", fontSize=26,
            textColor=_TEXT, alignment=TA_CENTER, fontName="Helvetica-Bold",
            spaceAfter=8, leading=32),
        "cover_sub":   ParagraphStyle("cover_sub",   fontSize=12,
            textColor=_ACCENT, alignment=TA_CENTER, spaceAfter=4,
            fontName="Helvetica-Bold"),
        "cover_meta":  ParagraphStyle("cover_meta",  fontSize=9,
            textColor=_MUTED, alignment=TA_CENTER, spaceAfter=2),
        "h1": ParagraphStyle("h1", fontSize=13, textColor=_ACCENT,
            fontName="Helvetica-Bold", spaceBefore=18, spaceAfter=10),
        "h2": ParagraphStyle("h2", fontSize=10, textColor=_TEXT,
            fontName="Helvetica-Bold", spaceBefore=12, spaceAfter=6),
        "body": ParagraphStyle("body", fontSize=8.5, textColor=_TEXT,
            leading=14, spaceAfter=4),
        "kpi_v": ParagraphStyle("kpi_v", fontSize=20, textColor=_TEXT,
            alignment=TA_CENTER, fontName="Helvetica-Bold", leading=24),
        "kpi_l": ParagraphStyle("kpi_l", fontSize=7, textColor=_MUTED,
            alignment=TA_CENTER, leading=10, fontName="Helvetica-Bold"),
        "grade": ParagraphStyle("grade", fontSize=12, textColor=_WHITE,
            alignment=TA_CENTER, fontName="Helvetica-Bold"),
        "footer": ParagraphStyle("footer", fontSize=7, textColor=_MUTED,
            alignment=TA_CENTER),
    }

# ── Page template callbacks ────────────────────────────────
def _header_footer(canvas, doc):
    canvas.saveState()
    w, h = A4
    
    # ── Top bar (Orange accent) ──
    canvas.setFillColor(_ACCENT)
    canvas.rect(0, h - 0.5*cm, w, 0.5*cm, fill=1, stroke=0)

    # Header text
    canvas.setFont("Helvetica-Bold", 7)
    canvas.setFillColor(_WHITE)
    canvas.drawString(1.5*cm, h - 0.35*cm, "ENGINEERING INTELLIGENCE  ·  GRAFANA EXPORT")
    canvas.drawRightString(w - 1.5*cm, h - 0.35*cm,
        f"Generated {datetime.now().strftime('%Y-%m-%d  %H:%M')}")

    # ── Bottom footer line ──
    canvas.setStrokeColor(_BORDER)
    canvas.setLineWidth(0.6)
    canvas.line(1.5*cm, 1.0*cm, w - 1.5*cm, 1.0*cm)

    # Page number
    canvas.setFont("Helvetica", 7)
    canvas.setFillColor(_MUTED)
    canvas.drawCentredString(w/2, 0.55*cm, f"Page {doc.page}")
    canvas.restoreState()

def _first_page(canvas, doc):
    _header_footer(canvas, doc)

def _later_pages(canvas, doc):
    _header_footer(canvas, doc)

# ── Logo drawing ──────────────────────────────────────────
def _make_logo_drawing() -> Drawing:
    d = Drawing(160, 60)
    d.add(Rect(0, 0, 160, 60, fillColor=_ACCENT, strokeColor=None, rx=4, ry=4))
    d.add(String(80, 22, "GRAFANA", fontSize=24, fillColor=_WHITE,
                 fontName="Helvetica-Bold", textAnchor="middle"))
    d.add(String(80, 10, "ENGINEERING INTEL", fontSize=7, fillColor=_WHITE,
                 fontName="Helvetica", textAnchor="middle"))
    return d

# ── KPI Table ─────────────────────────────────────────────
_USABLE_W = 18.0 * cm

def _kpi_table(metrics: dict, styles: dict) -> Table:
    keys   = ["total_issues","open_issues","closed_issues","closure_rate",
              "total_prs","merged_prs","contributors","stale_issues"]
    labels = ["TOTAL ISSUES","OPEN","CLOSED","CLOSURE %",
              "TOTAL PRS","MERGED PRS","TEAM","STALE >30D"]
    raw    = [metrics.get(k, "—") for k in keys]
    values = []
    for v in raw:
        try:    values.append(str(round(float(v), 1)))
        except: values.append(str(v))

    colored = []
    clr_map = {
        "open_issues":   "#c4162a",  # Red
        "stale_issues":  "#c4162a",
        "closed_issues": "#36a347",  # Green
        "merged_prs":    "#36a347",
        "contributors":  "#1f60c4",  # Blue
    }
    for i, v in enumerate(values):
        c = clr_map.get(keys[i], "#24292e")
        if keys[i] == "closure_rate":
            try: c = "#36a347" if float(v) >= 60 else ("#f46800" if float(v) >= 30 else "#c4162a")
            except: pass
        colored.append(Paragraph(f"<font color='{c}'><b>{v}</b></font>", styles["kpi_v"]))

    cw = [_USABLE_W / 8] * 8
    data = [colored, [Paragraph(l, styles["kpi_l"]) for l in labels]]
    t = Table(data, colWidths=cw)
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,-1), _SURF),
        ("BOX",           (0,0),(-1,-1), 0.8, _ACCENT),
        ("INNERGRID",     (0,0),(-1,-1), 0.4, _BORDER),
        ("TOPPADDING",    (0,0),(-1,-1), 12),
        ("BOTTOMPADDING", (0,0),(-1,-1), 12),
    ]))
    return t

# ── DataFrame Table ───────────────────────────────────────
def _df_table(df: pd.DataFrame, max_rows=30, col_widths=None,
              grade_col: str | None = None) -> Table:
    cols = [c.upper() for c in df.columns]
    display = df.head(max_rows).copy()
    for col in display.columns:
        display[col] = display[col].astype(str).str[:40]
    rows = [cols] + display.values.tolist()
    num_cols = len(cols)
    cw = col_widths or [_USABLE_W / num_cols] * num_cols

    t = Table(rows, colWidths=cw, repeatRows=1)
    style = [
        ("BACKGROUND",    (0,0),(-1,0),  _ACCENT),
        ("TEXTCOLOR",     (0,0),(-1,0),  _WHITE),
        ("FONTNAME",      (0,0),(-1,0),  "Helvetica-Bold"),
        ("FONTSIZE",      (0,1),(-1,-1), 7),
        ("TEXTCOLOR",     (0,1),(-1,-1), _TEXT),
        ("ROWBACKGROUNDS",(0,1),(-1,-1), [_WHITE, _SURF]),
        ("GRID",          (0,0),(-1,-1), 0.3, _BORDER),
        ("BOX",           (0,0),(-1,-1), 0.6, _ACCENT),
    ]
    if grade_col and grade_col.upper() in cols:
        gi = cols.index(grade_col.upper())
        gc_map = {"A": _GREEN, "B": _BLUE, "C": _YELLOW, "D": _ACCENT, "F": _RED}
        for ri, row in enumerate(rows[1:], 1):
            g = row[gi] if gi < len(row) else ""
            gc = gc_map.get(g, _TEXT)
            style += [("TEXTCOLOR", (gi,ri),(gi,ri), gc),
                      ("FONTNAME",  (gi,ri),(gi,ri), "Helvetica-Bold")]
    t.setStyle(TableStyle(style))
    return t

# ── Matplotlib chart helpers ───────────────────────────────
_MPL_STYLE = {
    "facecolor": "#ffffff",
    "text_color": "#24292e",
    "grid_color": "#e2e8f0",
    "bar_open":   "#c4162a",
    "bar_closed": "#36a347",
    "accent":     "#f46800",
}

def _mpl_buf(fig) -> io.BytesIO:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=130, bbox_inches="tight",
                facecolor=_MPL_STYLE["facecolor"], edgecolor="none")
    plt.close(fig)
    buf.seek(0)
    return buf

def _chart_issues_bar(issues: pd.DataFrame) -> io.BytesIO | None:
    if not MPL_OK or issues.empty or "state" not in issues.columns:
        return None
    grp = issues.groupby("state").size()
    fig, ax = plt.subplots(figsize=(5, 2.5), facecolor=_MPL_STYLE["facecolor"])
    clrs = [_MPL_STYLE["bar_open"] if s=="open" else _MPL_STYLE["bar_closed"] for s in grp.index]
    bars = ax.bar(grp.index, grp.values, color=clrs, width=0.5, zorder=3)
    ax.bar_label(bars, fmt="%d", color=_MPL_STYLE["text_color"], fontsize=9, padding=3)
    ax.set_facecolor(_MPL_STYLE["facecolor"])
    ax.set_title("ISSUES BY STATE", color=_MPL_STYLE["text_color"], fontsize=10, pad=8, fontname="Helvetica-Bold")
    ax.tick_params(colors=_MPL_STYLE["text_color"], labelsize=8)
    ax.spines[:].set_visible(False)
    ax.yaxis.grid(True, color=_MPL_STYLE["grid_color"], linewidth=0.6)
    return _mpl_buf(fig)

def _chart_pr_pie(prs: pd.DataFrame) -> io.BytesIO | None:
    if not MPL_OK or prs.empty: return None
    merged = int(prs.get("merged", pd.Series(dtype=bool)).sum()) if "merged" in prs.columns else 0
    open_  = int((prs["state"] == "open").sum()) if "state" in prs.columns else 0
    closed_unmerged = max(0, len(prs) - merged - open_)
    vals, labels, clrs = [merged, open_, closed_unmerged], ["Merged","Open","Closed"], [_BLUE, _RED, _ACCENT]
    filtered = [(v,l,c) for v,l,c in zip(vals,labels,clrs) if v>0]
    if not filtered: return None
    vals, labels, clrs = zip(*filtered)
    fig, ax = plt.subplots(figsize=(4, 2.5), facecolor=_MPL_STYLE["facecolor"])
    ax.pie(vals, labels=labels, colors=clrs, autopct="%1.0f%%", startangle=140)
    ax.set_title("PR STATUS", color=_MPL_STYLE["text_color"], fontsize=10, fontname="Helvetica-Bold")
    return _mpl_buf(fig)

def _chart_closure_trend(issues: pd.DataFrame) -> io.BytesIO | None:
    if not MPL_OK or issues.empty or "created_date" not in issues.columns: return None
    try:
        issues = issues.copy()
        issues["created_date"] = pd.to_datetime(issues["created_date"])
        monthly = issues.groupby([issues["created_date"].dt.to_period("M"), "state"]).size().unstack(fill_value=0)
        if monthly.empty: return None
        monthly.index = [str(p) for p in monthly.index]
        fig, ax = plt.subplots(figsize=(7, 2.8), facecolor=_MPL_STYLE["facecolor"])
        if "open"   in monthly.columns: ax.plot(monthly.index, monthly["open"], color=_RED, marker="o", label="Open")
        if "closed" in monthly.columns: ax.plot(monthly.index, monthly["closed"], color=_GREEN, marker="s", label="Closed")
        ax.set_title("MONTHLY VELOCITY", color=_MPL_STYLE["text_color"], fontsize=10, pad=10, fontname="Helvetica-Bold")
        ax.tick_params(colors=_MPL_STYLE["text_color"], labelsize=8)
        ax.yaxis.grid(True, color=_MPL_STYLE["grid_color"], linewidth=0.6)
        ax.legend(fontsize=8)
        return _mpl_buf(fig)
    except: return None

def _buf_to_image(buf, width_cm=8) -> Image | None:
    if buf is None: return None
    try:
        img = Image(buf)
        img.drawWidth  = width_cm * cm
        img.drawHeight = width_cm * cm * (img.imageHeight / img.imageWidth)
        return img
    except: return None

def _section(title: str, styles: dict) -> list:
    return [Spacer(1, 0.4*cm), Paragraph(title.upper(), styles["h1"]), HRFlowable(width="100%", thickness=0.8, color=_ACCENT, spaceAfter=8)]

def generate_pdf(metrics: dict, issues: pd.DataFrame, prs: pd.DataFrame, contributors: pd.DataFrame, repo_summary: pd.DataFrame, report_type: str = "Daily", selected_date: date | None = None, date_range: tuple | None = None) -> bytes:
    if not REPORTLAB_OK: raise ImportError("reportlab missing.")
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=1.5*cm, rightMargin=1.5*cm, topMargin=2.2*cm, bottomMargin=1.8*cm, title="Engineering Intel · Grafana Export")
    styles, story = _styles(), []
    story.append(Spacer(1, 1.5*cm))
    drw = _make_logo_drawing()
    drw.hAlign = "CENTER"
    story.append(drw)
    story.append(Spacer(1, 1.2*cm))
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    story.append(Paragraph("Engineering Intelligence Dashboard", styles["cover_title"]))
    story.append(Paragraph("Simtestlab  ·  Real-time GitHub Analytics", styles["cover_sub"]))
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph(f"Generated on {now_str}", styles["cover_meta"]))
    story.append(Spacer(1, 1.5*cm))
    story.append(HRFlowable(width="100%", thickness=1.5, color=_ACCENT, spaceAfter=14))
    story.append(Paragraph("EXECUTIVE KPI SUMMARY", styles["h1"]))
    story.append(_kpi_table(metrics, styles))
    story.append(Spacer(1, 0.8*cm))
    ib, pp = _buf_to_image(_chart_issues_bar(issues), width_cm=7.5), _buf_to_image(_chart_pr_pie(prs), width_cm=6.5)
    if ib and pp:
        t = Table([[ib, pp]], colWidths=[9*cm, 8*cm])
        t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1), _SURF), ("BOX",(0,0),(-1,-1), 0.8, _BORDER), ("ALIGN",(0,0),(-1,-1),"CENTER"), ("VALIGN",(0,0),(-1,-1),"MIDDLE")]))
        story.append(t)
    tc = _buf_to_image(_chart_closure_trend(issues), width_cm=16)
    if tc: story.append(tc)
    story.append(PageBreak())
    if not repo_summary.empty:
        story += _section("📦 Repository Health Overview", styles)
        story.append(_df_table(repo_summary[["Repository","Total_Issues","Open_Issues","Closed_Issues","Closure_Rate%"]].head(30)))
    story.append(PageBreak())
    if not contributors.empty:
        story += _section("👤 Contributor Analytics", styles)
        story.append(_df_table(contributors[["Author","Issues_Opened","Open_Issues","Closed_Issues","Repos_Active"]].head(35)))
    doc.build(story, onFirstPage=_first_page, onLaterPages=_later_pages)
    return buf.getvalue()
