# 🚀 Engineering Intelligence Dashboard — Run Guide

## What is this?

A **Streamlit-based GitHub Analytics Platform** for the `simtestlab` GitHub organisation.  
It fetches live data from the GitHub API and provides 9 pages of analytics:

| Page | What it shows |
|---|---|
| 🏠 Executive Dashboard | Top-level KPIs and summary charts |
| 📦 Repositories | Per-repo stats, stars, forks, contributors |
| 🐞 Issues | Issue tracker with filters and state breakdown |
| 🔀 Pull Requests | PR lifecycle, cycle times, merge rates |
| 👤 Contributors | Team activity, workload distribution |
| 📡 Activity Feed | Chronological event log |
| ⏳ Staleness | Issues/PRs that haven't been touched recently |
| 📊 Reports | PDF + Excel/CSV export with date range picker |
| 🎯 Insights | Deep analytics — velocity, health scores, burndown |

---

## Prerequisites

| Tool | Min Version | Install |
|---|---|---|
| Python | 3.10+ | https://python.org |
| pip | any | bundled with Python |
| Git | any | https://git-scm.com |

---

## 1 — Clone the repository

```bash
git clone https://github.com/simtestlab/github-board.git
cd github-board
```

---

## 2 — Create a virtual environment

```bash
# Windows (PowerShell)
python -m venv .venv
.venv\Scripts\Activate.ps1

# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
```

---

## 3 — Install dependencies

```bash
pip install -r requirements.txt
```

`requirements.txt` installs:

```
streamlit       # web framework
pandas          # data wrangling
requests        # GitHub API calls
plotly          # interactive charts
reportlab       # PDF generation
openpyxl        # Excel export (.xlsx)
xlsxwriter      # Excel formatting
matplotlib      # chart images inside PDF
Pillow          # image processing
python-dotenv   # .env file loader
```

---

## 4 — Configure GitHub credentials

Copy the example env file and fill in your values:

```bash
# Windows
copy .env.example .env

# macOS / Linux
cp .env.example .env
```

Edit `.env`:

```env
GITHUB_TOKEN=github_pat_xxxxxxxxxxxxxxxxxxxxxxxx
GITHUB_ORG=simtestlab
```

### How to create a GitHub Personal Access Token

1. Go to **GitHub → Settings → Developer Settings → Personal Access Tokens → Fine-grained tokens**
2. Click **Generate new token**
3. Set expiry (90 days recommended)
4. Under **Repository permissions**, enable:
   - `Issues` → Read
   - `Pull requests` → Read
   - `Metadata` → Read (mandatory)
   - `Contents` → Read (for releases)
5. Under **Organisation access**, select your org
6. Copy the token and paste into `.env`

> [!WARNING]  
> Never commit your `.env` file. It is already listed in `.gitignore`.

---

## 5 — Fetch GitHub data

Before launching the app, fetch data from the GitHub API:

```bash
python github_org.py
```

This writes JSON cache files to the project root:

```
github_all_repo_meta_<timestamp>.json
github_all_repo_issues_<timestamp>.json
github_all_repo_prs_<timestamp>.json
github_all_repo_contributors_<timestamp>.json
github_all_repo_releases_<timestamp>.json
```

> You can also click **🔄 Refresh Data** inside the sidebar once the app is running.

---

## 6 — Run the app

```powershell
python -m streamlit run app.py
```

> [!IMPORTANT]
> On **Windows with AppLocker / Application Control policies**, running `streamlit run app.py` directly
> will fail with _"An Application Control policy has blocked this file"_.
> Always use `python -m streamlit run app.py` — this routes through `python.exe` which is permitted.

The app opens automatically at:

```
http://localhost:8501
```

---

## 7 — Using the app

### Sidebar controls

| Control | Purpose |
|---|---|
| **Navigation** | Switch between the 9 pages |
| **🔄 Refresh Data** | Re-fetch all data from GitHub API |
| **🗑️ Clear Cache** | Clear Streamlit's in-memory cache |
| **Filters** | Filter by repository, author, label, date range |

### Generating a PDF Report

1. Navigate to **📊 Reports**
2. Select report type: `Daily / Weekly / Monthly / Custom Range`
3. Pick date range and optional repo filter
4. Check the sections you want included
5. Click **🖨️ Generate PDF Report**
6. Click **⬇️ Download PDF**

The PDF includes:
- Branded cover page with Simtestlab logo
- Executive KPI grid (8 metrics)
- Embedded charts (issues bar, PR pie, trend line, contributors)
- Repository health score table (A–F grades)
- Issues table (top 35 rows)
- PR table (top 30 rows)
- Contributor analytics
- Page headers, footers, page numbers

### Exporting to Excel / CSV

On the **Reports** page, after selecting a date range, use:
- **⬇️ CSV** — exports the daily activity table
- **⬇️ Excel** — exports Daily Activity + Issues + PRs as separate sheets

---

## 8 — Project structure

```
github-board/
├── app.py                  # Main entry point (Streamlit app)
├── config.py               # Org name, token, colors, page list
├── github_org.py           # GitHub API fetcher (writes JSON)
├── requirements.txt        # Python dependencies
├── .env                    # Your secrets (not committed)
├── .env.example            # Template for .env
├── assets/
│   └── logo.png            # Simtestlab logo (used in PDF)
├── pages/
│   ├── p01_dashboard.py    # Executive Dashboard
│   ├── p02_repositories.py # Repositories
│   ├── p03_issues.py       # Issues
│   ├── p04_pull_requests.py# Pull Requests
│   ├── p05_contributors.py # Contributors
│   ├── p06_activity.py     # Activity Feed
│   ├── p07_staleness.py    # Staleness
│   ├── p08_reports.py      # Reports & PDF Export
│   └── p09_insights.py     # Engineering Insights
└── utils/
    ├── charts.py           # All Plotly chart functions
    ├── data_loader.py      # JSON → DataFrame loaders
    ├── exports.py          # CSV / Excel download helpers
    ├── filters.py          # Sidebar filter logic
    ├── metrics.py          # KPI computation
    ├── report_gen.py       # PDF generation (ReportLab)
    └── styles.py           # Global CSS injection
```

---

## 9 — Troubleshooting

| Problem | Fix |
|---|---|
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` in the active venv |
| `GITHUB_TOKEN not set` | Check `.env` has the correct token |
| `403 Forbidden` from GitHub API | Token expired or missing permissions — regenerate |
| `reportlab not found` | Run `pip install reportlab` |
| App shows "No data" | Run `python github_org.py` first or click 🔄 Refresh |
| Port 8501 already in use | Run `streamlit run app.py --server.port 8502` |
| PDF charts missing | Run `pip install matplotlib Pillow` |

---

## 10 — Running on a server / Docker (optional)

```bash
# Keep running in background (Linux)
nohup streamlit run app.py --server.port 8501 --server.headless true &

# Or with Docker
docker build -t github-board .
docker run -p 8501:8501 --env-file .env github-board
```

---

## Quick-start cheat sheet

```bash
# 1. Clone
git clone https://github.com/simtestlab/github-board.git && cd github-board

# 2. Setup
python -m venv .venv && .venv\Scripts\Activate.ps1   # Windows
pip install -r requirements.txt

# 3. Configure
copy .env.example .env   # then edit with your token

# 4. Fetch data
python github_org.py

# 5. Launch
streamlit run app.py
```

Open → **http://localhost:8501** 🚀