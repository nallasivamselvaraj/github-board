# utils/report_gen.py  –  Professional PDF via ReportLab + Matplotlib
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
    import matplotlib.patches as mpatches
    MPL_OK = True
except ImportError:
    MPL_OK = False

# ── Palette (light/white PDF) ─────────────────────────────
_BG     = colors.HexColor("#ffffff")   # page white
_SURF   = colors.HexColor("#f8f9fc")   # table alt row
_SURF2  = colors.HexColor("#ffffff")   # table row
_PURP   = colors.HexColor("#7c3aed")   # accent purple
_PURP_L = colors.HexColor("#5b21b6")   # darker purple for readability
_BLUE   = colors.HexColor("#2563eb")   # blue
_GREEN  = colors.HexColor("#16a34a")   # green
_RED    = colors.HexColor("#dc2626")   # red
_YELL   = colors.HexColor("#d97706")   # amber
_TEXT   = colors.HexColor("#1e1b2e")   # dark body text
_MUTED  = colors.HexColor("#6b7280")   # muted gray
_BORDER = colors.HexColor("#e5e7ef")   # light border
_WHITE  = colors.white
_HDRFG  = colors.white                 # table header text

LOGO_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "logo.png")

# ── Styles ────────────────────────────────────────────────
def _styles():
    return {
        "cover_title": ParagraphStyle("cover_title", fontSize=24,
            textColor=_TEXT, alignment=TA_CENTER, fontName="Helvetica-Bold",
            spaceAfter=6, leading=30),
        "cover_sub":   ParagraphStyle("cover_sub",   fontSize=12,
            textColor=_PURP, alignment=TA_CENTER, spaceAfter=4),
        "cover_meta":  ParagraphStyle("cover_meta",  fontSize=9,
            textColor=_MUTED, alignment=TA_CENTER, spaceAfter=2),
        "h1": ParagraphStyle("h1", fontSize=13, textColor=_PURP,
            fontName="Helvetica-Bold", spaceBefore=16, spaceAfter=8),
        "h2": ParagraphStyle("h2", fontSize=10, textColor=_TEXT,
            fontName="Helvetica-Bold", spaceBefore=10, spaceAfter=4),
        "body": ParagraphStyle("body", fontSize=8.5, textColor=_TEXT,
            leading=14, spaceAfter=4),
        "kpi_v": ParagraphStyle("kpi_v", fontSize=18, textColor=_TEXT,
            alignment=TA_CENTER, fontName="Helvetica-Bold", leading=22),
        "kpi_l": ParagraphStyle("kpi_l", fontSize=7, textColor=_MUTED,
            alignment=TA_CENTER, leading=10),
        "grade": ParagraphStyle("grade", fontSize=12, textColor=_WHITE,
            alignment=TA_CENTER, fontName="Helvetica-Bold"),
        "footer": ParagraphStyle("footer", fontSize=7, textColor=_MUTED,
            alignment=TA_CENTER),
    }

# ── Page template callbacks ────────────────────────────────
def _header_footer(canvas, doc):
    canvas.saveState()
    w, h = A4

    # ── Top bar (0.5cm tall, fully above content area) ──
    canvas.setFillColor(_PURP)
    canvas.rect(0, h - 0.5*cm, w, 0.5*cm, fill=1, stroke=0)

    # Header text — drawn INSIDE the bar (white)
    canvas.setFont("Helvetica-Bold", 6.5)
    canvas.setFillColor(colors.white)
    canvas.drawString(1.5*cm, h - 0.35*cm, "ENGINEERING INTELLIGENCE  ·  SIMTESTLAB")
    canvas.drawRightString(w - 1.5*cm, h - 0.35*cm,
        f"Generated {datetime.now().strftime('%Y-%m-%d  %H:%M')}")

    # ── Bottom footer line ──
    canvas.setStrokeColor(_BORDER)
    canvas.setLineWidth(0.5)
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

# ── Logo drawing (fallback if no PNG) ─────────────────────
def _make_logo_drawing() -> Drawing:
    d = Drawing(160, 60)
    d.add(Rect(0, 0, 160, 60, fillColor=_PURP, strokeColor=None, rx=8, ry=8))
    d.add(String(80, 22, "STL", fontSize=24, fillColor=_WHITE,
                 fontName="Helvetica-Bold", textAnchor="middle"))
    d.add(String(80, 10, "SIMTESTLAB", fontSize=7, fillColor=colors.HexColor("#c4b5fd"),
                 fontName="Helvetica", textAnchor="middle"))
    return d

# ── KPI Table ─────────────────────────────────────────────
# A4 usable width = 21cm - 1.5cm*2 margins = 18cm
_USABLE_W = 18.0 * cm

def _kpi_table(metrics: dict, styles: dict) -> Table:
    keys   = ["total_issues","open_issues","closed_issues","closure_rate",
              "total_prs","merged_prs","contributors","stale_issues"]
    labels = ["Total Issues","Open","Closed","Closure %",
              "Total PRs","Merged PRs","Contributors","Stale >30d"]
    raw    = [metrics.get(k, "—") for k in keys]
    values = []
    for v in raw:
        try:    values.append(str(round(float(v), 1)))
        except: values.append(str(v))

    # Color-coded values (dark colors, readable on white)
    colored = []
    clr_map = {
        "open_issues":   "#dc2626",
        "stale_issues":  "#dc2626",
        "closed_issues": "#16a34a",
        "merged_prs":    "#16a34a",
        "contributors":  "#2563eb",
    }
    for i, v in enumerate(values):
        c = clr_map.get(keys[i], "#1e1b2e")
        if keys[i] == "closure_rate":
            try: c = "#16a34a" if float(v) >= 60 else ("#d97706" if float(v) >= 30 else "#dc2626")
            except: pass
        colored.append(Paragraph(f"<font color='{c}'><b>{v}</b></font>", styles["kpi_v"]))

    # 8 cols fitting exactly in usable width
    cw = [_USABLE_W / 8] * 8
    data = [colored, [Paragraph(l, styles["kpi_l"]) for l in labels]]
    t = Table(data, colWidths=cw)
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,-1), colors.HexColor("#f5f3ff")),
        ("BOX",           (0,0),(-1,-1), 0.8, _PURP),
        ("INNERGRID",     (0,0),(-1,-1), 0.4, _BORDER),
        ("ROWBACKGROUNDS",(0,0),(-1,-1), [colors.HexColor("#f5f3ff"), _WHITE]),
        ("TOPPADDING",    (0,0),(-1,-1), 10),
        ("BOTTOMPADDING", (0,0),(-1,-1), 10),
        ("LEFTPADDING",   (0,0),(-1,-1), 4),
        ("RIGHTPADDING",  (0,0),(-1,-1), 4),
    ]))
    return t

# ── DataFrame Table ───────────────────────────────────────
def _df_table(df: pd.DataFrame, max_rows=30, col_widths=None,
              grade_col: str | None = None) -> Table:
    cols = list(df.columns)
    # Truncate long cell text to prevent overflow
    display = df.head(max_rows).copy()
    for col in display.columns:
        display[col] = display[col].astype(str).str[:40]
    rows = [cols] + display.values.tolist()
    num_cols = len(cols)
    cw = col_widths or [_USABLE_W / num_cols] * num_cols

    t = Table(rows, colWidths=cw, repeatRows=1)
    style = [
        # Header row
        ("BACKGROUND",    (0,0),(-1,0),  _PURP),
        ("TEXTCOLOR",     (0,0),(-1,0),  _WHITE),
        ("FONTNAME",      (0,0),(-1,0),  "Helvetica-Bold"),
        ("FONTSIZE",      (0,0),(-1,0),  7.5),
        ("BOTTOMPADDING", (0,0),(-1,0),  7),
        ("TOPPADDING",    (0,0),(-1,0),  7),
        # Body rows
        ("FONTSIZE",      (0,1),(-1,-1), 7),
        ("TEXTCOLOR",     (0,1),(-1,-1), _TEXT),
        ("ROWBACKGROUNDS",(0,1),(-1,-1), [_WHITE, _SURF]),
        ("TOPPADDING",    (0,1),(-1,-1), 4),
        ("BOTTOMPADDING", (0,1),(-1,-1), 4),
        # Grid
        ("GRID",          (0,0),(-1,-1), 0.3, _BORDER),
        ("BOX",           (0,0),(-1,-1), 0.6, _PURP),
        ("LEFTPADDING",   (0,0),(-1,-1), 5),
        ("RIGHTPADDING",  (0,0),(-1,-1), 5),
        ("WORDWRAP",      (0,0),(-1,-1), "CJK"),
    ]
    # Grade column colors
    if grade_col and grade_col in cols:
        gi = cols.index(grade_col)
        gc_map = {"A": _GREEN, "B": _BLUE, "C": _YELL, "D": _YELL, "F": _RED}
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
    "text_color": "#1e1b2e",
    "grid_color": "#e5e7ef",
    "bar_open":   "#dc2626",
    "bar_closed": "#16a34a",
    "pie_colors": ["#7c3aed", "#dc2626", "#2563eb"],
    "line_color": "#7c3aed",
}

def _mpl_buf(fig) -> io.BytesIO:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=130, bbox_inches="tight",
                facecolor="#ffffff", edgecolor="none")
    plt.close(fig)
    buf.seek(0)
    return buf

def _chart_issues_bar(issues: pd.DataFrame) -> io.BytesIO | None:
    if not MPL_OK or issues.empty or "state" not in issues.columns:
        return None
    grp = issues.groupby("state").size()
    fig, ax = plt.subplots(figsize=(5, 2.5), facecolor="#ffffff")
    clrs = [_MPL_STYLE["bar_open"] if s=="open" else _MPL_STYLE["bar_closed"] for s in grp.index]
    bars = ax.bar(grp.index, grp.values, color=clrs, width=0.5, zorder=3)
    ax.bar_label(bars, fmt="%d", color=_MPL_STYLE["text_color"], fontsize=9, padding=3)
    ax.set_facecolor("#ffffff")
    ax.set_title("Issues by State", color=_MPL_STYLE["text_color"], fontsize=10, pad=8)
    ax.tick_params(colors=_MPL_STYLE["text_color"], labelsize=8)
    ax.spines[:].set_visible(False)
    ax.yaxis.grid(True, color=_MPL_STYLE["grid_color"], linewidth=0.6)
    ax.set_axisbelow(True)
    return _mpl_buf(fig)

def _chart_pr_pie(prs: pd.DataFrame) -> io.BytesIO | None:
    if not MPL_OK or prs.empty:
        return None
    merged = int(prs.get("merged", pd.Series(dtype=bool)).sum()) if "merged" in prs.columns else 0
    open_  = int((prs["state"] == "open").sum()) if "state" in prs.columns else 0
    closed_unmerged = max(0, len(prs) - merged - open_)
    vals   = [merged, open_, closed_unmerged]
    labels = ["Merged","Open","Closed"]
    clrs   = ["#7c3aed","#dc2626","#2563eb"]
    filtered = [(v,l,c) for v,l,c in zip(vals,labels,clrs) if v>0]
    if not filtered: return None
    vals, labels, clrs = zip(*filtered)
    fig, ax = plt.subplots(figsize=(4, 2.5), facecolor="#ffffff")
    ax.pie(vals, labels=labels, colors=clrs,
           autopct="%1.0f%%", startangle=140, pctdistance=0.75,
           textprops={"color":"#1e1b2e", "fontsize":8})
    ax.set_facecolor("#ffffff")
    ax.set_title("Pull Request Status", color="#1e1b2e", fontsize=10)
    fig.patch.set_facecolor("#ffffff")
    return _mpl_buf(fig)

def _chart_top_contributors(contributors: pd.DataFrame) -> io.BytesIO | None:
    if not MPL_OK or contributors.empty:
        return None
    col = "Issues_Opened" if "Issues_Opened" in contributors.columns else contributors.columns[1]
    top = contributors.head(10)
    fig, ax = plt.subplots(figsize=(5.5, 2.8), facecolor="#ffffff")
    bars = ax.barh(top["Author"] if "Author" in top.columns else top.iloc[:,0],
                   top[col], color="#7c3aed", zorder=3)
    ax.bar_label(bars, fmt="%d", color="#1e1b2e", fontsize=8, padding=3)
    ax.set_facecolor("#ffffff")
    ax.invert_yaxis()
    ax.set_title("Top Contributors", color="#1e1b2e", fontsize=10, pad=8)
    ax.tick_params(colors="#6b7280", labelsize=7)
    ax.spines[:].set_visible(False)
    ax.xaxis.grid(True, color="#e5e7ef", linewidth=0.6)
    ax.set_axisbelow(True)
    return _mpl_buf(fig)

def _chart_closure_trend(issues: pd.DataFrame) -> io.BytesIO | None:
    if not MPL_OK or issues.empty or "created_date" not in issues.columns:
        return None
    try:
        issues = issues.copy()
        issues["created_date"] = pd.to_datetime(issues["created_date"])
        monthly = issues.groupby([issues["created_date"].dt.to_period("M"), "state"]).size().unstack(fill_value=0)
        if monthly.empty: return None
        monthly.index = [str(p) for p in monthly.index]
        fig, ax = plt.subplots(figsize=(6, 2.5), facecolor="#ffffff")
        if "open"   in monthly.columns:
            ax.plot(monthly.index, monthly["open"],   color="#dc2626", marker="o", markersize=4, linewidth=1.8, label="Open")
        if "closed" in monthly.columns:
            ax.plot(monthly.index, monthly["closed"], color="#16a34a", marker="s", markersize=4, linewidth=1.8, label="Closed")
        ax.set_facecolor("#ffffff")
        ax.set_title("Monthly Issue Trend", color="#1e1b2e", fontsize=10, pad=8)
        ax.tick_params(colors="#6b7280", labelsize=7)
        plt.xticks(rotation=45, ha="right")
        ax.spines[:].set_visible(False)
        ax.yaxis.grid(True, color="#e5e7ef", linewidth=0.6)
        ax.legend(fontsize=7, labelcolor="#1e1b2e", facecolor="#ffffff", edgecolor="#e5e7ef")
        return _mpl_buf(fig)
    except Exception:
        return None

def _buf_to_image(buf, width_cm=8) -> Image | None:
    if buf is None: return None
    try:
        img = Image(buf)
        img.drawWidth  = width_cm * cm
        img.drawHeight = width_cm * cm * (img.imageHeight / img.imageWidth)
        return img
    except Exception:
        return None

# ── Section header helper ─────────────────────────────────
def _section(title: str, styles: dict) -> list:
    return [
        Spacer(1, 0.2*cm),
        Paragraph(title, styles["h1"]),
        HRFlowable(width="100%", thickness=0.5, color=_PURP, spaceAfter=6),
    ]

# ── Main generate function ─────────────────────────────────
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
    if not REPORTLAB_OK:
        raise ImportError("reportlab is not installed. Run: pip install reportlab")

    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=1.5*cm, rightMargin=1.5*cm,
        topMargin=2.2*cm, bottomMargin=1.8*cm,
        title="Engineering Intelligence Report",
        author="Simtestlab",
    )
    styles = _styles()
    story  = []

    # ══ COVER PAGE ══════════════════════════════════════
    story.append(Spacer(1, 1.5*cm))

    # Logo
    if os.path.exists(LOGO_PATH):
        logo = Image(LOGO_PATH, width=8*cm, height=3.2*cm)
        logo.hAlign = "CENTER"
        story.append(logo)
    else:
        drw = _make_logo_drawing()
        drw.hAlign = "CENTER"
        story.append(drw)

    story.append(Spacer(1, 0.8*cm))

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    if report_type == "Daily" and selected_date:
        period_str = f"Daily Report  ·  {selected_date}"
    elif report_type == "Custom Range" and date_range:
        period_str = f"Custom Report  ·  {date_range[0]}  →  {date_range[1]}"
    else:
        period_str = f"{report_type} Report  ·  {now_str}"

    story.append(Paragraph("Engineering Intelligence Dashboard", styles["cover_title"]))
    story.append(Paragraph("Simtestlab  ·  GitHub Analytics Platform", styles["cover_sub"]))
    story.append(Spacer(1, 0.4*cm))
    story.append(Paragraph(period_str, styles["cover_meta"]))
    story.append(Paragraph(f"Generated  {now_str}", styles["cover_meta"]))

    story.append(Spacer(1, 1.2*cm))
    story.append(HRFlowable(width="100%", thickness=1.5, color=_PURP, spaceAfter=12))

    # ── KPI Summary on cover ───────────────────────────────
    story.append(Paragraph("Executive KPI Summary", styles["h1"]))
    story.append(_kpi_table(metrics, styles))
    story.append(Spacer(1, 0.6*cm))

    # ── Charts row ────────────────────────────────────────
    chart_row_data = []

    ib = _buf_to_image(_chart_issues_bar(issues), width_cm=7)
    pp = _buf_to_image(_chart_pr_pie(prs), width_cm=6)
    if ib and pp:
        t = Table([[ib, pp]], colWidths=[9*cm, 8*cm])
        t.setStyle(TableStyle([
            ("BACKGROUND",(0,0),(-1,-1), _SURF),
            ("BOX",(0,0),(-1,-1), 0.5, _BORDER),
            ("ALIGN",(0,0),(-1,-1),"CENTER"),
            ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
            ("TOPPADDING",(0,0),(-1,-1),8),
            ("BOTTOMPADDING",(0,0),(-1,-1),8),
        ]))
        story.append(t)
        story.append(Spacer(1, 0.3*cm))

    # trend chart
    tc = _buf_to_image(_chart_closure_trend(issues), width_cm=15)
    if tc:
        tc.hAlign = "CENTER"
        story.append(tc)
        story.append(Spacer(1, 0.3*cm))

    story.append(PageBreak())

    # ══ REPOSITORY METRICS ══════════════════════════════
    if not repo_summary.empty:
        story += _section("📦  Repository Metrics", styles)
        cols_to_show = ["Repository","Total_Issues","Open_Issues","Closed_Issues",
                        "Contributors","Closure_Rate%"]
        cols_to_show = [c for c in cols_to_show if c in repo_summary.columns]
        cws = [4*cm] + [2*cm] * (len(cols_to_show)-1)
        story.append(_df_table(repo_summary[cols_to_show].head(20), col_widths=cws))
        story.append(Spacer(1, 0.4*cm))

    # ══ REPOSITORY HEALTH SCORES ═════════════════════════
    if not repo_summary.empty and "Closure_Rate%" in repo_summary.columns:
        story += _section("🏥  Repository Health Scores", styles)

        def _grade(row):
            s = 100
            cr  = row.get("Closure_Rate%", 0)
            age = row.get("Avg_Age_Days", 0)
            op  = row.get("Open_Issues", 0)
            if cr  < 30: s -= 30
            elif cr  < 60: s -= 15
            elif cr  < 80: s -= 5
            if age > 90: s -= 30
            elif age > 60: s -= 20
            elif age > 30: s -= 10
            if op > 100: s -= 15
            elif op > 50: s -= 8
            elif op > 20: s -= 3
            s = max(0, min(100, s))
            g = "A" if s>=80 else ("B" if s>=65 else ("C" if s>=50 else ("D" if s>=35 else "F")))
            return s, g

        scored = repo_summary.copy()
        scored["Score"], scored["Grade"] = zip(*scored.apply(_grade, axis=1))
        scored = scored.sort_values("Score", ascending=False)
        h_cols = ["Repository","Score","Grade","Closure_Rate%","Avg_Age_Days","Open_Issues"]
        h_cols = [c for c in h_cols if c in scored.columns]
        cws2 = [4*cm, 1.5*cm, 1.5*cm] + [2*cm] * (len(h_cols)-3)
        story.append(_df_table(scored[h_cols].head(20), col_widths=cws2, grade_col="Grade"))
        story.append(Spacer(1, 0.4*cm))

    story.append(PageBreak())

    # ══ ISSUES ════════════════════════════════════════════
    if not issues.empty:
        story += _section("🐞  Issues Summary", styles)
        i_cols = ["repository","issue_number","title","state","author","age_days","comments"]
        i_cols = [c for c in i_cols if c in issues.columns]
        cws3 = [2.8*cm,1.2*cm,5*cm,1.2*cm,2.2*cm,1.3*cm,1.3*cm][:len(i_cols)]
        story.append(_df_table(issues[i_cols].head(35), col_widths=cws3))
        story.append(Spacer(1, 0.3*cm))

    story.append(PageBreak())

    # ══ PULL REQUESTS ═════════════════════════════════════
    if not prs.empty:
        story += _section("🔀  Pull Request Summary", styles)
        p_cols = ["repository","pr_number","title","state","author","merged","cycle_time_days"]
        p_cols = [c for c in p_cols if c in prs.columns]
        cws4 = [2.8*cm,1.2*cm,4.8*cm,1.2*cm,2.2*cm,1.3*cm,1.6*cm][:len(p_cols)]
        story.append(_df_table(prs[p_cols].head(30), col_widths=cws4))
        story.append(Spacer(1, 0.3*cm))

    story.append(PageBreak())

    # ══ CONTRIBUTORS ══════════════════════════════════════
    if not contributors.empty:
        story += _section("👤  Contributor Analytics", styles)
        c_cols = ["Author","Issues_Opened","Open_Issues","Closed_Issues",
                  "Repos_Active","Comments"]
        c_cols = [c for c in c_cols if c in contributors.columns]
        story.append(_df_table(contributors[c_cols].head(25)))
        story.append(Spacer(1, 0.3*cm))

        # contributor chart
        cc = _buf_to_image(_chart_top_contributors(contributors), width_cm=14)
        if cc:
            cc.hAlign = "CENTER"
            story.append(cc)

    # ══ FOOTER ════════════════════════════════════════════
    story.append(Spacer(1, 0.5*cm))
    story.append(HRFlowable(width="100%", thickness=0.5, color=_MUTED))
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph(
        f"Confidential · Engineering Intelligence Dashboard · Simtestlab · {now_str}",
        styles["footer"],
    ))

    doc.build(story, onFirstPage=_first_page, onLaterPages=_later_pages)
    return buf.getvalue()
