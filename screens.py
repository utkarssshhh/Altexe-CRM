"""Altexe CRM - every screen lives here."""
from __future__ import annotations

import html as _html
import re
from datetime import timedelta

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import db
import theme


# ------------------------------------------------------------------ helpers
def esc(s) -> str:
    return _html.escape("" if s is None or (isinstance(s, float) and pd.isna(s)) else str(s))


def h(markup: str) -> None:
    """Render HTML. Newlines are stripped so Markdown never mistakes indented tags for code blocks."""
    st.markdown(re.sub(r"\s*\n\s*", "", markup.strip()), unsafe_allow_html=True)


def sym() -> str:
    return st.session_state.get("currency", "₹")


def money(v, s: str | None = None) -> str:
    s = s or sym()
    v = float(v or 0)
    if s == "₹":
        if v >= 1e7:
            return f"{s}{v / 1e7:.2f} Cr"
        if v >= 1e5:
            return f"{s}{v / 1e5:.1f} L"
        if v >= 1e3:
            return f"{s}{v / 1e3:.0f}K"
        return f"{s}{v:,.0f}"
    if v >= 1e6:
        return f"{s}{v / 1e6:.2f}M"
    if v >= 1e3:
        return f"{s}{v / 1e3:.0f}K"
    return f"{s}{v:,.0f}"


def chip(label: str, color: str) -> str:
    return f'<span class="chip" style="--c:{color}">{esc(label)}</span>'


def initials(name: str) -> str:
    parts = [p for p in str(name).split() if p]
    return ("".join(p[0] for p in parts[:2]) or "?").upper()


def avatar(name: str) -> str:
    series = theme.palette()["series"]
    color = series[sum(map(ord, str(name))) % len(series)]
    return f'<div class="avatar" style="--c:{color}">{esc(initials(name))}</div>'


def ago(ts: str) -> str:
    try:
        delta = db.now() - pd.to_datetime(ts).to_pydatetime()
    except Exception:
        return ""
    mins = int(delta.total_seconds() // 60)
    if mins < 1:
        return "just now"
    if mins < 60:
        return f"{mins}m ago"
    if mins < 60 * 24:
        return f"{mins // 60}h ago"
    return f"{mins // (60 * 24)}d ago"


def due_label(due) -> str:
    try:
        d = pd.to_datetime(due).date()
    except Exception:
        return ""
    diff = (d - db.today()).days
    if diff < 0:
        return f'<span class="due over">{-diff}d overdue</span>'
    if diff == 0:
        return '<span class="due today">Today</span>'
    if diff == 1:
        return '<span class="due">Tomorrow</span>'
    return f'<span class="due">{d:%d %b}</span>'


def priority_chip(p: str) -> str:
    pal = theme.palette()["series"]
    return chip(p, {"High": pal[0], "Medium": pal[1], "Low": pal[2]}.get(p, pal[5]))


def panel(name: str):
    return st.container(key=f"panel_{name}")


def panel_title(title: str, sub: str = "") -> None:
    h(f'<div class="panel-title">{esc(title)}<span>{esc(sub)}</span></div>')


def style_fig(fig: go.Figure, height: int = 300) -> go.Figure:
    p = theme.palette()
    fig.update_layout(
        height=height, margin=dict(l=4, r=4, t=14, b=4), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Sans, sans-serif", color=p["muted"], size=12), showlegend=False,
        hoverlabel=dict(bgcolor=p["ink"], font=dict(color="#fff", family="DM Sans")),
    )
    return fig


def show(fig: go.Figure) -> None:
    st.plotly_chart(fig, config={"displayModeBar": False})


# ------------------------------------------------------------------- dialogs
@st.dialog("New contact")
def contact_dialog() -> None:
    with st.form("new_contact", border=False):
        name = st.text_input("Full name *")
        c1, c2 = st.columns(2)
        company = c1.text_input("Company")
        role = c2.text_input("Role")
        email = c1.text_input("Email")
        phone = c2.text_input("Phone")
        status = c1.selectbox("Status", db.CONTACT_STATUSES)
        source = c2.selectbox("Where did they find you?", db.SOURCES)
        notes = st.text_area("Notes", height=80)
        ok = st.form_submit_button("Save contact", type="primary")
    if ok:
        if not name.strip():
            st.error("A name is needed to save a contact.")
            return
        db.add_contact(name.strip(), company.strip(), role.strip(), email.strip(), phone.strip(), status, source, notes.strip())
        st.rerun()


@st.dialog("New deal")
def deal_dialog() -> None:
    contacts = db.get_contacts()
    options = [None] + contacts.id.tolist()
    labels = {None: "— no contact —"}
    labels.update({int(r.id): f"{r.name} · {r.company}" for r in contacts.itertuples()})
    with st.form("new_deal", border=False):
        title = st.text_input("Deal name *")
        contact_id = st.selectbox("Contact", options, format_func=lambda x: labels.get(x, str(x)))
        c1, c2 = st.columns(2)
        value = c1.number_input(f"Value ({sym()})", min_value=0.0, step=5000.0, value=100000.0)
        stage = c2.selectbox("Stage", db.OPEN_STAGES)
        close = st.date_input("Expected close", value=db.today() + timedelta(days=30))
        ok = st.form_submit_button("Create deal", type="primary")
    if ok:
        if not title.strip():
            st.error("Give the deal a name first.")
            return
        company = ""
        if contact_id is not None:
            company = contacts.loc[contacts.id == contact_id, "company"].iloc[0] or ""
            contact_id = int(contact_id)
        db.add_deal(title.strip(), contact_id, company, value, stage, close)
        st.rerun()


@st.dialog("New task")
def task_dialog() -> None:
    with st.form("new_task", border=False):
        title = st.text_input("What needs doing? *")
        c1, c2 = st.columns(2)
        due = c1.date_input("Due", value=db.today())
        priority = c2.selectbox("Priority", db.PRIORITIES, index=1)
        ok = st.form_submit_button("Add task", type="primary")
    if ok:
        if not title.strip():
            st.error("Please describe the task.")
            return
        db.add_task(title.strip(), due, priority)
        st.rerun()


# --------------------------------------------------------------------- HOME
def home() -> None:
    deals, contacts, tasks, acts = db.get_deals(), db.get_contacts(), db.get_tasks(), db.get_activities(7)
    p, s, stc = theme.palette(), sym(), theme.stage_colors()
    now, today = db.now(), db.today()
    greet = "Good morning" if now.hour < 12 else "Good afternoon" if now.hour < 17 else "Good evening"
    name = st.session_state.get("user_name", "there")
    h(f"""<div class="hero"><div class="eyebrow">{now:%A, %d %B %Y}</div>
        <div class="hero-title">{greet}, {esc(name)} <span class="wave">👋</span></div>
        <div class="hero-sub">Here's what's brewing at <b>Altexe</b> today.</div></div>""")

    open_d = deals[deals.stage.isin(db.OPEN_STAGES)]
    pipeline_val = float(open_d.value.sum())
    weighted = float((open_d.value * open_d.stage.map(db.STAGE_PROB) / 100).sum())
    won = deals[deals.stage == "Won"].copy()
    won["dt"] = pd.to_datetime(won.closed_at)
    lost_n = int((deals.stage == "Lost").sum())
    win_rate = (len(won) / (len(won) + lost_n) * 100) if (len(won) + lost_n) else 0
    cur_p = pd.Period(today, "M")
    won["period"] = won.dt.dt.to_period("M")
    this_m = float(won.loc[won.period == cur_p, "value"].sum())
    last_m = float(won.loc[won.period == cur_p - 1, "value"].sum())
    if last_m > 0:
        pct = (this_m - last_m) / last_m * 100
        delta = f'<div class="kpi-sub {"up" if pct >= 0 else "down"}">{"▲" if pct >= 0 else "▼"} {abs(pct):.0f}% vs last month</div>'
    else:
        delta = '<div class="kpi-sub">Fresh month, fresh wins</div>'
    customers = int((contacts.status == "Customer").sum())

    h(f"""<div class="kpis">
      <div class="kpi feature"><div class="kpi-icon">💰</div><div class="kpi-label">Won this month</div>
        <div class="kpi-value">{money(this_m)}</div>{delta.replace('class="kpi-sub up"', 'class="kpi-sub"').replace('class="kpi-sub down"', 'class="kpi-sub"')}</div>
      <div class="kpi"><div class="kpi-icon">🌱</div><div class="kpi-label">Open pipeline</div>
        <div class="kpi-value">{money(pipeline_val)}</div><div class="kpi-sub">{len(open_d)} deals · {money(weighted)} forecast</div></div>
      <div class="kpi"><div class="kpi-icon">🎯</div><div class="kpi-label">Win rate</div>
        <div class="kpi-value">{win_rate:.0f}%</div><div class="kpi-sub">{len(won)} won · {lost_n} lost</div></div>
      <div class="kpi"><div class="kpi-icon">🤝</div><div class="kpi-label">Contacts</div>
        <div class="kpi-value">{len(contacts)}</div><div class="kpi-sub">{customers} are customers</div></div>
    </div>""")

    left, right = st.columns([1.55, 1])
    with left:
        with panel("revenue"):
            panel_title("Revenue", "won deals · last 6 months")
            periods = pd.period_range(end=cur_p, periods=6, freq="M")
            vals = [float(won.loc[won.period == pm, "value"].sum()) for pm in periods]
            labels = [pm.strftime("%b") for pm in periods]
            fig = go.Figure(go.Scatter(
                x=labels, y=vals, mode="lines+markers+text", text=[money(v) for v in vals], textposition="top center",
                line=dict(color=p["accent"], width=3.5, shape="spline", smoothing=0.9),
                marker=dict(size=10, color=p["surface"], line=dict(color=p["accent"], width=3)),
                fill="tozeroy", fillcolor=theme.rgba(p["accent"], 0.13), textfont=dict(color=p["ink"], size=12),
                hovertemplate="%{x}<br><b>%{text}</b><extra></extra>", cliponaxis=False,
            ))
            style_fig(fig, 300)
            top = max(vals) if vals and max(vals) > 0 else 1
            fig.update_yaxes(showgrid=True, gridcolor=p["line"], showticklabels=False, zeroline=False, range=[0, top * 1.28])
            fig.update_xaxes(showgrid=False, zeroline=False)
            show(fig)
    with right:
        with panel("stages"):
            panel_title("Pipeline by stage", "open deals")
            sums = [float(open_d.loc[open_d.stage == st_, "value"].sum()) for st_ in db.OPEN_STAGES]
            fig = go.Figure(go.Bar(
                y=db.OPEN_STAGES, x=sums, orientation="h", text=[money(v) for v in sums], textposition="outside",
                marker=dict(color=[stc[x] for x in db.OPEN_STAGES], cornerradius=10), cliponaxis=False,
                hovertemplate="%{y}<br><b>%{text}</b><extra></extra>", textfont=dict(color=p["ink"]),
            ))
            style_fig(fig, 300)
            fig.update_xaxes(visible=False, range=[0, (max(sums) if sums and max(sums) > 0 else 1) * 1.35])
            fig.update_yaxes(autorange="reversed", showgrid=False, tickfont=dict(color=p["ink"], size=13))
            show(fig)

    st.write("")
    c1, c2, c3 = st.columns([1, 1.1, 1.1])
    with c1:
        with panel("sources"):
            panel_title("Where leads come from")
            counts = contacts.source.value_counts() if not contacts.empty else pd.Series(dtype=int)
            if counts.empty:
                h('<div class="empty">Add contacts to see your sources 🌿</div>')
            else:
                fig = go.Figure(go.Pie(
                    labels=counts.index.tolist(), values=counts.values.tolist(), hole=0.68, sort=False,
                    marker=dict(colors=p["series"], line=dict(color=p["surface"], width=3)),
                    textinfo="none", hovertemplate="%{label}<br><b>%{value}</b> contacts<extra></extra>",
                ))
                style_fig(fig, 250)
                fig.update_layout(showlegend=True, legend=dict(font=dict(color=p["ink"], size=12), orientation="h", y=-0.05))
                fig.add_annotation(text=f"<b>{int(counts.sum())}</b><br>contacts", showarrow=False,
                                   font=dict(family="Fraunces, serif", size=18, color=p["ink"]))
                show(fig)
    with c2:
        with panel("focus"):
            panel_title("Today's focus", "what needs you next")
            todo = tasks[tasks.done == 0].sort_values("due").head(5)
            if todo.empty:
                h('<div class="empty">All clear — enjoy your chai ☕</div>')
            for t in todo.itertuples():
                h(f'<div class="task-row"><div><div class="task-title">{esc(t.title)}</div>{due_label(t.due)}</div>{priority_chip(t.priority)}</div>')
    with c3:
        with panel("activity"):
            panel_title("Recent activity")
            if acts.empty:
                h('<div class="empty">Nothing yet — go make some magic ✨</div>')
            for a in acts.itertuples():
                h(f'<div class="tl-item"><div class="tl-dot">{a.icon}</div><div><div class="tl-text">{a.text}</div><div class="tl-time">{ago(a.ts)}</div></div></div>')


# ----------------------------------------------------------------- PIPELINE
def _move(did: int, stage: str) -> None:
    db.set_deal_stage(did, stage)
    if stage == "Won":
        st.session_state["celebrate"] = True
        st.toast("Deal won! 🎉 Nicely done.")


def pipeline() -> None:
    h('<div class="hero"><div class="eyebrow">Pipeline</div><div class="hero-title">Move deals forward</div>'
      '<div class="hero-sub">Nudge a deal along with the arrows — land it in Won to celebrate.</div></div>')
    if st.button("＋ New deal", type="primary", key="pl_new"):
        deal_dialog()
    st.write("")
    deals, stc = db.get_deals(), theme.stage_colors()
    lanes = ["Lead", "Qualified", "Proposal", "Negotiation", "Won"]
    cols = st.columns(len(lanes))
    for col, stage in zip(cols, lanes):
        with col, st.container(key=f"lane_{stage}"):
            sub = deals[deals.stage == stage]
            h(f'<div class="lane-head"><div class="lane-name"><span class="lane-dot" style="--c:{stc[stage]}"></span>{stage} '
              f'<span class="lane-sum">{len(sub)}</span></div><div class="lane-sum">{money(sub.value.sum())}</div></div>')
            if sub.empty:
                h('<div class="empty">Nothing here yet</div>')
            idx = lanes.index(stage)
            for d in sub.itertuples():
                close = ""
                if stage != "Won" and isinstance(d.close_date, str):
                    close = f'<span class="due">closes {pd.to_datetime(d.close_date):%d %b}</span>'
                h(f'<div class="deal" style="--c:{stc[stage]}"><div class="deal-title">{esc(d.title)}</div>'
                  f'<div class="deal-co">{esc(d.company)}</div><div class="deal-foot"><div class="deal-val">{money(d.value)}</div>{close}</div></div>')
                b1, b2 = st.columns(2)
                if idx > 0:
                    b1.button("←", key=f"l{d.id}", on_click=_move, args=(int(d.id), lanes[idx - 1]), help=f"Move to {lanes[idx - 1]}")
                if idx < len(lanes) - 1:
                    b2.button("→", key=f"r{d.id}", on_click=_move, args=(int(d.id), lanes[idx + 1]), help=f"Move to {lanes[idx + 1]}")


# ----------------------------------------------------------------- CONTACTS
def _set_status(cid: int) -> None:
    db.set_contact_status(cid, st.session_state[f"cs_{cid}"])


def contacts() -> None:
    h('<div class="hero"><div class="eyebrow">People</div><div class="hero-title">Your contacts</div>'
      '<div class="hero-sub">Everyone you\'re building a relationship with.</div></div>')
    df = db.get_contacts()
    f1, f2, f3 = st.columns([2.2, 2, 1])
    q = f1.text_input("Search", placeholder="Search name, company, email…", label_visibility="collapsed")
    status = f2.multiselect("Status", db.CONTACT_STATUSES, placeholder="All statuses", label_visibility="collapsed")
    with f3:
        if st.button("＋ Add contact", type="primary", key="ct_new"):
            contact_dialog()
    if q:
        mask = df[["name", "company", "email"]].fillna("").apply(lambda c: c.str.contains(q, case=False, regex=False)).any(axis=1)
        df = df[mask]
    if status:
        df = df[df.status.isin(status)]
    st.write("")
    if df.empty:
        h('<div class="empty">No contacts match — try a different search 🔍</div>')
        return
    pal = theme.palette()["series"]
    sc = {"New": pal[3], "Engaged": pal[1], "Customer": pal[2], "Cold": "#A39A92"}
    rows = list(df.itertuples())
    for i in range(0, len(rows), 3):
        cols = st.columns(3)
        for col, c in zip(cols, rows[i:i + 3]):
            with col, panel(f"c{c.id}"):
                h(f'<div class="person">{avatar(c.name)}<div><div class="person-name">{esc(c.name)}</div>'
                  f'<div class="person-sub">{esc(c.role)}{" · " if c.role and c.company else ""}{esc(c.company)}</div></div></div>'
                  f'<div class="meta-line">✉️ {esc(c.email) or "—"}<br>📞 {esc(c.phone) or "—"}</div>'
                  f'<div class="meta-row">{chip(c.status, sc.get(c.status, pal[5]))}<span>via {esc(c.source)}</span></div>')
                with st.popover("Manage"):
                    st.selectbox("Status", db.CONTACT_STATUSES, index=db.CONTACT_STATUSES.index(c.status) if c.status in db.CONTACT_STATUSES else 0,
                                 key=f"cs_{c.id}", on_change=_set_status, args=(int(c.id),))
                    if st.button("Delete contact", key=f"cd_{c.id}"):
                        db.delete_contact(int(c.id))
                        st.rerun()


# -------------------------------------------------------------------- DEALS
def deals() -> None:
    h('<div class="hero"><div class="eyebrow">Revenue</div><div class="hero-title">All deals</div>'
      '<div class="hero-sub">Every opportunity in one calm list.</div></div>')
    df = db.get_deals()
    f1, f2 = st.columns([3, 1])
    stages = f1.multiselect("Stage", db.STAGES, placeholder="All stages", label_visibility="collapsed")
    with f2:
        if st.button("＋ New deal", type="primary", key="dl_new"):
            deal_dialog()
    if stages:
        df = df[df.stage.isin(stages)]
    st.write("")
    if df.empty:
        h('<div class="empty">No deals here yet 🌤️</div>')
        return
    stc = theme.stage_colors()
    body = ""
    for d in df.itertuples():
        close = pd.to_datetime(d.close_date).strftime("%d %b %Y") if isinstance(d.close_date, str) else "—"
        body += (f'<tr><td><div class="t-main">{esc(d.title)}</div><div class="t-sub">{esc(d.contact) if isinstance(d.contact, str) else ""}</div></td>'
                 f'<td>{esc(d.company)}</td><td>{chip(d.stage, stc.get(d.stage, "#999"))}</td><td class="num">{money(d.value)}</td>'
                 f'<td>{close}</td><td><div class="bar"><i style="width:{db.STAGE_PROB.get(d.stage, 0)}%"></i></div></td></tr>')
    h(f'<table class="tbl"><thead><tr><th>Deal</th><th>Company</th><th>Stage</th><th>Value</th><th>Close</th><th>Chance</th></tr></thead><tbody>{body}</tbody></table>')

    with st.expander("✏️ Edit a deal"):
        labels = {int(r.id): f"{r.title} · {r.company}" for r in df.itertuples()}
        sel = st.selectbox("Choose a deal", list(labels), format_func=labels.get)
        row = df[df.id == sel].iloc[0]
        c1, c2, c3 = st.columns(3)
        stage = c1.selectbox("Stage", db.STAGES, index=db.STAGES.index(row.stage), key=f"es_{sel}")
        value = c2.number_input(f"Value ({sym()})", min_value=0.0, value=float(row.value), step=5000.0, key=f"ev_{sel}")
        cur = pd.to_datetime(row.close_date).date() if isinstance(row.close_date, str) else db.today()
        close = c3.date_input("Expected close", value=cur, key=f"ed_{sel}")
        b1, b2 = st.columns(2)
        if b1.button("Save changes", type="primary", key=f"sv_{sel}"):
            db.update_deal(int(sel), stage, value, close)
            if stage == "Won" and row.stage != "Won":
                st.session_state["celebrate"] = True
            st.rerun()
        if b2.button("Delete deal", key=f"dd_{sel}"):
            db.delete_deal(int(sel))
            st.rerun()


# -------------------------------------------------------------------- TASKS
def _toggle_task(tid: int) -> None:
    db.set_task_done(tid, st.session_state[f"task_{tid}"])


def tasks() -> None:
    h('<div class="hero"><div class="eyebrow">Focus</div><div class="hero-title">Tasks</div>'
      '<div class="hero-sub">Small steps, warm relationships.</div></div>')
    if st.button("＋ New task", type="primary", key="tk_new"):
        task_dialog()
    st.write("")
    df, today = db.get_tasks(), db.today()
    if df.empty:
        h('<div class="empty">No tasks yet. A clear desk is a clear mind 🌿</div>')
        return
    df["due_d"] = pd.to_datetime(df.due).dt.date
    open_t, done_t = df[df.done == 0], df[df.done == 1]
    groups = [
        ("Overdue", open_t[open_t.due_d < today]),
        ("Today", open_t[open_t.due_d == today]),
        ("Upcoming", open_t[open_t.due_d > today]),
    ]
    for title, sub in groups:
        if sub.empty:
            continue
        with panel(f"tasks_{title}"):
            panel_title(title, f"{len(sub)} task{'s' if len(sub) != 1 else ''}")
            for t in sub.itertuples():
                a, b = st.columns([3, 1.3])
                a.checkbox(t.title, value=False, key=f"task_{t.id}", on_change=_toggle_task, args=(int(t.id),))
                with b:
                    h(f'<div style="text-align:right;padding-top:6px">{due_label(t.due)} &nbsp; {priority_chip(t.priority)}</div>')
        st.write("")
    if open_t.empty:
        h('<div class="empty">Everything is done. Go celebrate 🎉</div>')
    if not done_t.empty:
        with st.expander(f"Completed ({len(done_t)})"):
            for t in done_t.itertuples():
                a, b = st.columns([4, 1])
                a.checkbox(t.title, value=True, key=f"task_{t.id}", on_change=_toggle_task, args=(int(t.id),))
                if b.button("Delete", key=f"td_{t.id}"):
                    db.delete_task(int(t.id))
                    st.rerun()


# ----------------------------------------------------------------- SETTINGS
def settings() -> None:
    h('<div class="hero"><div class="eyebrow">Settings</div><div class="hero-title">Make it yours</div>'
      '<div class="hero-sub">Tweak the details, back up your data, start fresh.</div></div>')
    c1, c2 = st.columns(2)
    with c1, panel("set_you"):
        panel_title("About you")
        st.text_input("Your first name", key="user_name")
        syms = ["₹", "$", "€", "£", "AED "]
        st.selectbox("Currency", syms, key="currency")
    with c2, panel("set_data"):
        panel_title("Your data", "stored in data/altexe.db")
        st.download_button("⬇ Export contacts (CSV)", db.get_contacts().to_csv(index=False).encode(), "altexe_contacts.csv", "text/csv")
        st.download_button("⬇ Export deals (CSV)", db.get_deals().to_csv(index=False).encode(), "altexe_deals.csv", "text/csv")
    st.write("")
    with panel("set_danger"):
        panel_title("Reset", "careful, these can't be undone")
        sure = st.checkbox("I understand this replaces what's in my CRM", key="sure")
        d1, d2 = st.columns(2)
        if d1.button("Load demo data", disabled=not sure):
            db.seed_demo()
            st.toast("Demo data loaded 🌿")
            st.rerun()
        if d2.button("Start fresh (empty CRM)", disabled=not sure):
            db.clear_all()
            st.toast("All clear. A blank page, ready for Altexe ✨")
            st.rerun()
