"""Altexe CRM — a cozy, premium little CRM built with Streamlit.

Run locally:   streamlit run app.py
"""
import streamlit as st

import db
import theme
import screens

st.set_page_config(page_title="Altexe CRM", page_icon="🪴", layout="wide", initial_sidebar_state="expanded")

db.init()

# Settings that must survive page changes (Streamlit forgets widget values of widgets that aren't on screen)
for key, default in {"palette": theme.DEFAULT, "user_name": "Utkarsh", "currency": "₹"}.items():
    st.session_state.setdefault(key, default)
    st.session_state[key] = st.session_state[key]

theme.inject(st.session_state["palette"])

PAGES = {
    "🏡  Home": screens.home,
    "🧭  Pipeline": screens.pipeline,
    "👥  Contacts": screens.contacts,
    "💼  Deals": screens.deals,
    "✅  Tasks": screens.tasks,
    "⚙️  Settings": screens.settings,
}

with st.sidebar:
    st.markdown(
        '<div class="brand"><div class="brand-mark">a</div>'
        '<div><div class="brand-name">Altexe</div><div class="brand-sub">crm · studio</div></div></div>',
        unsafe_allow_html=True,
    )
    page = st.radio("Navigate", list(PAGES), label_visibility="collapsed", key="nav")

    st.markdown('<div class="side-label">Mood</div>', unsafe_allow_html=True)
    st.selectbox("Mood", list(theme.PALETTES), key="palette", label_visibility="collapsed")

    tasks_df = db.get_tasks()
    due_today = int(((tasks_df.done == 0) & (tasks_df.due <= db.today().isoformat())).sum()) if not tasks_df.empty else 0
    note = (f"You have <b>{due_today}</b> task{'s' if due_today != 1 else ''} needing love today."
            if due_today else "Nothing urgent today. <b>Breathe easy</b> ☕")
    st.markdown(f'<div class="side-note">{note}</div>', unsafe_allow_html=True)

PAGES[page]()

if st.session_state.pop("celebrate", False):
    st.balloons()
