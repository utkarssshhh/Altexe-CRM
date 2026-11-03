"""Altexe CRM - tiny SQLite data layer (+ cozy demo data)."""
from __future__ import annotations

import random
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd

try:  # Show times in your own timezone, not the server's
    from zoneinfo import ZoneInfo

    _TZ = ZoneInfo("Asia/Kolkata")  # <- change me if you like
except Exception:  # pragma: no cover
    _TZ = None

DB_PATH = Path(__file__).parent / "data" / "altexe.db"

STAGES = ["Lead", "Qualified", "Proposal", "Negotiation", "Won", "Lost"]
OPEN_STAGES = STAGES[:4]
STAGE_PROB = {"Lead": 10, "Qualified": 30, "Proposal": 55, "Negotiation": 75, "Won": 100, "Lost": 0}
CONTACT_STATUSES = ["New", "Engaged", "Customer", "Cold"]
SOURCES = ["Referral", "Website", "LinkedIn", "Cold outreach", "Event", "Partner"]
PRIORITIES = ["High", "Medium", "Low"]


def now() -> datetime:
    return datetime.now(_TZ).replace(tzinfo=None) if _TZ else datetime.now()


def today():
    return now().date()


# ----------------------------------------------------------------- plumbing
def _connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con


def run(sql: str, params: tuple = ()) -> int:
    con = _connect()
    try:
        cur = con.execute(sql, params)
        con.commit()
        return cur.lastrowid
    finally:
        con.close()


def read(sql: str, params: tuple = ()) -> pd.DataFrame:
    con = _connect()
    try:
        return pd.read_sql_query(sql, con, params=params)
    finally:
        con.close()


SCHEMA = """
CREATE TABLE IF NOT EXISTS contacts(
    id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, company TEXT, role TEXT,
    email TEXT, phone TEXT, status TEXT DEFAULT 'New', source TEXT, notes TEXT, created TEXT);
CREATE TABLE IF NOT EXISTS deals(
    id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, contact_id INTEGER, company TEXT,
    value REAL DEFAULT 0, stage TEXT DEFAULT 'Lead', close_date TEXT, created TEXT, closed_at TEXT);
CREATE TABLE IF NOT EXISTS tasks(
    id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, due TEXT,
    priority TEXT DEFAULT 'Medium', done INTEGER DEFAULT 0);
CREATE TABLE IF NOT EXISTS activities(
    id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT, icon TEXT, text TEXT);
CREATE TABLE IF NOT EXISTS meta(key TEXT PRIMARY KEY, value TEXT);
"""


def init() -> None:
    con = _connect()
    try:
        con.executescript(SCHEMA)
        con.commit()
    finally:
        con.close()
    if read("SELECT value FROM meta WHERE key='seeded'").empty:
        seed_demo()


# -------------------------------------------------------------------- reads
def get_contacts() -> pd.DataFrame:
    return read("SELECT * FROM contacts ORDER BY id DESC")


def get_deals() -> pd.DataFrame:
    return read(
        """SELECT d.*, c.name AS contact FROM deals d
           LEFT JOIN contacts c ON c.id = d.contact_id ORDER BY d.value DESC"""
    )


def get_tasks() -> pd.DataFrame:
    return read("SELECT * FROM tasks ORDER BY done ASC, due ASC, id DESC")


def get_activities(limit: int = 8) -> pd.DataFrame:
    return read("SELECT * FROM activities ORDER BY ts DESC, id DESC LIMIT ?", (limit,))


# ------------------------------------------------------------------- writes
def log(text: str, icon: str = "✨") -> None:
    run("INSERT INTO activities(ts, icon, text) VALUES (?,?,?)", (now().isoformat(timespec="seconds"), icon, text))


def add_contact(name, company="", role="", email="", phone="", status="New", source="Website", notes="") -> int:
    cid = run(
        """INSERT INTO contacts(name, company, role, email, phone, status, source, notes, created)
           VALUES (?,?,?,?,?,?,?,?,?)""",
        (name, company, role, email, phone, status, source, notes, today().isoformat()),
    )
    log(f"Added contact <b>{_e(name)}</b>" + (f" from {_e(company)}" if company else ""), "👋")
    return cid


def set_contact_status(cid: int, status: str) -> None:
    run("UPDATE contacts SET status=? WHERE id=?", (status, cid))


def delete_contact(cid: int) -> None:
    run("UPDATE deals SET contact_id=NULL WHERE contact_id=?", (cid,))
    run("DELETE FROM contacts WHERE id=?", (cid,))


def add_deal(title, contact_id, company, value, stage="Lead", close_date=None) -> int:
    closed = today().isoformat() if stage in ("Won", "Lost") else None
    did = run(
        """INSERT INTO deals(title, contact_id, company, value, stage, close_date, created, closed_at)
           VALUES (?,?,?,?,?,?,?,?)""",
        (title, contact_id, company, float(value), stage, str(close_date) if close_date else None,
         today().isoformat(), closed),
    )
    log(f"New deal <b>{_e(title)}</b> created", "💼")
    return did


def set_deal_stage(did: int, stage: str) -> None:
    closed = today().isoformat() if stage in ("Won", "Lost") else None
    run("UPDATE deals SET stage=?, closed_at=? WHERE id=?", (stage, closed, did))
    row = read("SELECT title FROM deals WHERE id=?", (did,))
    if not row.empty:
        icon = "🎉" if stage == "Won" else "📦" if stage == "Lost" else "➡️"
        log(f"<b>{_e(row.title.iloc[0])}</b> moved to {stage}", icon)


def update_deal(did: int, stage: str, value: float, close_date) -> None:
    run("UPDATE deals SET value=?, close_date=? WHERE id=?", (float(value), str(close_date), did))
    set_deal_stage(did, stage)


def delete_deal(did: int) -> None:
    run("DELETE FROM deals WHERE id=?", (did,))


def add_task(title, due, priority="Medium") -> int:
    return run("INSERT INTO tasks(title, due, priority) VALUES (?,?,?)", (title, str(due), priority))


def set_task_done(tid: int, done: bool) -> None:
    run("UPDATE tasks SET done=? WHERE id=?", (1 if done else 0, tid))
    if done:
        row = read("SELECT title FROM tasks WHERE id=?", (tid,))
        if not row.empty:
            log(f"Completed <b>{_e(row.title.iloc[0])}</b>", "✅")


def delete_task(tid: int) -> None:
    run("DELETE FROM tasks WHERE id=?", (tid,))


def clear_all() -> None:
    for t in ("contacts", "deals", "tasks", "activities"):
        run(f"DELETE FROM {t}")
    run("INSERT OR REPLACE INTO meta(key, value) VALUES ('seeded','1')")


def _e(s) -> str:
    import html

    return html.escape(str(s or ""))


# --------------------------------------------------------------- demo data
def seed_demo() -> None:
    """Fill the CRM with friendly sample data so it never looks empty on day one."""
    for t in ("contacts", "deals", "tasks", "activities"):
        run(f"DELETE FROM {t}")
    rng = random.Random(42)
    td = today()

    people = [
        ("Aarav Mehta", "Northwind Studio", "Founder"), ("Isha Kapoor", "Bloom & Co.", "Head of Marketing"),
        ("Daniel Reyes", "Lumen Labs", "CTO"), ("Priya Nair", "Juniper Foods", "Operations Lead"),
        ("Rohan Verma", "Pixelhaus", "Creative Director"), ("Sofia Laurent", "Maison Verte", "Owner"),
        ("Kabir Singh", "Orbit Logistics", "VP Growth"), ("Meera Iyer", "Saffron Digital", "CEO"),
        ("Liam O'Connor", "Harbor & Pine", "Partnerships"), ("Ananya Das", "Tidewater Health", "COO"),
        ("Vikram Rao", "Copperleaf", "Procurement"), ("Zara Khan", "Moonrise Media", "Producer"),
        ("Noah Fischer", "Alder Systems", "Engineering Mgr"), ("Tara Menon", "Kiln & Clay", "Founder"),
        ("Arjun Malhotra", "BrightPath Edu", "Director"), ("Chloe Martin", "Fernwood Travel", "Brand Lead"),
        ("Devansh Joshi", "Quill Publishing", "Editor-in-Chief"), ("Nisha Patel", "Sunbeam Retail", "Buyer"),
        ("Ethan Brooks", "Redwood Capital", "Associate"), ("Kavya Reddy", "Mosaic Interiors", "Principal"),
        ("Yash Agarwal", "Nimbus Cloud", "Product Manager"), ("Hana Sato", "Origami Games", "Studio Head"),
        ("Rahul Bansal", "Terrace Hospitality", "GM"), ("Olivia Grant", "Willow & Wren", "Founder"),
    ]
    status_pool = ["New"] * 4 + ["Engaged"] * 9 + ["Customer"] * 8 + ["Cold"] * 3
    for i, (name, company, role) in enumerate(people):
        first = name.split()[0].lower().replace("'", "")
        slug = "".join(ch for ch in company.lower() if ch.isalnum())
        con = _connect()
        try:
            con.execute(
                """INSERT INTO contacts(name, company, role, email, phone, status, source, notes, created)
                   VALUES (?,?,?,?,?,?,?,?,?)""",
                (name, company, role, f"{first}@{slug}.com", f"+91 9{rng.randint(10000, 99999)} {rng.randint(10000, 99999)}",
                 status_pool[i % len(status_pool)], rng.choice(SOURCES), "",
                 (td - timedelta(days=rng.randint(3, 200))).isoformat()),
            )
            con.commit()
        finally:
            con.close()

    titles = [
        "Brand refresh retainer", "Website rebuild", "Annual support plan", "Onboarding workshop", "Analytics setup",
        "Content engine (6 mo)", "Mobile app MVP", "Growth audit", "Sales playbook", "Automation sprint",
        "Design system", "Partner portal", "Email nurture flows", "Data migration", "Customer research",
        "Pricing strategy", "Launch campaign", "Integration build", "Training programme", "Pilot project",
        "Q4 expansion", "Platform licence",
    ]
    plan = ["Lead"] * 4 + ["Qualified"] * 4 + ["Proposal"] * 4 + ["Negotiation"] * 3 + ["Won"] * 5 + ["Lost"] * 2
    won_offsets = [0, 1, 25, 40, 58, 75, 95, 118, 140, 160]  # days ago -> spreads revenue over 6 months
    won_i = 0
    for i, stage in enumerate(plan):
        title = titles[i]
        cid = (i * 3) % len(people) + 1
        company = people[cid - 1][1]
        value = rng.randrange(60000, 950000, 25000)
        closed = None
        close_date = (td + timedelta(days=rng.randint(7, 70))).isoformat()
        if stage in ("Won", "Lost"):
            off = won_offsets[won_i % len(won_offsets)] if stage == "Won" else rng.randint(10, 120)
            won_i += stage == "Won"
            closed = (td - timedelta(days=min(off, 170))).isoformat()
            close_date = closed
        run(
            """INSERT INTO deals(title, contact_id, company, value, stage, close_date, created, closed_at)
               VALUES (?,?,?,?,?,?,?,?)""",
            (title, cid, company, value, stage, close_date, (td - timedelta(days=rng.randint(15, 180))).isoformat(), closed),
        )
    # a few extra wins so the revenue chart is lively
    for off, v, t in [(18, 420000, "Retainer renewal"), (48, 310000, "Landing pages"), (85, 560000, "Platform setup"),
                      (110, 275000, "Strategy sprint"), (150, 640000, "Annual contract")]:
        cid = rng.randint(1, len(people))
        d = (td - timedelta(days=off)).isoformat()
        run(
            """INSERT INTO deals(title, contact_id, company, value, stage, close_date, created, closed_at)
               VALUES (?,?,?,?,?,?,?,?)""",
            (t, cid, people[cid - 1][1], v, "Won", d, d, d),
        )

    tasks = [
        ("Send proposal to Lumen Labs", -1, "High"), ("Follow up with Bloom & Co.", 0, "High"),
        ("Prepare demo for Pixelhaus", 0, "Medium"), ("Review Q4 pricing sheet", 1, "Medium"),
        ("Call Kabir about contract terms", 2, "High"), ("Update CRM notes after events", 3, "Low"),
        ("Draft case study: Maison Verte", 5, "Low"), ("Book quarterly check-ins", 7, "Medium"),
    ]
    for t, off, pr in tasks:
        run("INSERT INTO tasks(title, due, priority) VALUES (?,?,?)", (t, (td + timedelta(days=off)).isoformat(), pr))

    acts = [
        (35, "🎉", "<b>Annual support plan</b> moved to Won"), (130, "📞", "Call with <b>Priya Nair</b> from Juniper Foods"),
        (260, "✉️", "Proposal sent to <b>Lumen Labs</b>"), (600, "👋", "Added contact <b>Hana Sato</b> from Origami Games"),
        (1300, "➡️", "<b>Website rebuild</b> moved to Proposal"), (1700, "✅", "Completed <b>Update pricing deck</b>"),
        (2900, "💼", "New deal <b>Pilot project</b> created"),
    ]
    for mins, icon, text in acts:
        run("INSERT INTO activities(ts, icon, text) VALUES (?,?,?)",
            ((now() - timedelta(minutes=mins)).isoformat(timespec="seconds"), icon, text))
    run("INSERT OR REPLACE INTO meta(key, value) VALUES ('seeded','1')")
