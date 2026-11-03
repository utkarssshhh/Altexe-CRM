# 🪴 Altexe CRM

A cozy, premium CRM dashboard built with Streamlit.

## Run it
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Put it online (Streamlit Community Cloud)
1. Upload these files to a GitHub repo (keep `.streamlit/config.toml`).
2. Go to share.streamlit.io -> New app -> pick the repo -> main file `app.py`.

> **Heads-up:** the database is a local SQLite file (`data/altexe.db`). On Streamlit Community Cloud the disk is
> temporary, so data can reset when the app restarts. Use Settings -> Export CSV as a backup, or swap `db.py`
> for a hosted database (Supabase / Neon / Google Sheets) when you go live with real customers.

## What's inside
| Page | What it does |
|---|---|
| Home | KPI cards, revenue trend, pipeline by stage, lead sources, today's focus, activity feed |
| Pipeline | Kanban board - move deals with arrows (balloons when you win!) |
| Contacts | Searchable contact cards, add / change status / delete |
| Deals | Clean deal table, edit value / stage / close date |
| Tasks | Overdue / today / upcoming, tick to complete |
| Settings | Your name, currency, CSV export, load demo data or start fresh |

Switch the **Mood** in the sidebar: Oat Latte, Sage Garden or Blush Hour.
Colours live in `theme.py` (`PALETTES`) and `.streamlit/config.toml`; timezone is at the top of `db.py`.

Files: `app.py` (entry) - `screens.py` (pages) - `db.py` (data) - `theme.py` (look).
