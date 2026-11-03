"""Altexe CRM - the cozy look: palettes + CSS."""
from __future__ import annotations

import streamlit as st

PALETTES = {
    "Oat Latte": dict(
        bg="#FBF5EC", surface="#FFFDF9", sidebar="#F3E9DA", lane="#F6EDE0", ink="#3A2E28", muted="#8A7B70",
        line="#EADFCF", accent="#C4623A", accent2="#E0A96D", glow="#F6DDC4",
        series=["#C4623A", "#E0A96D", "#7C9A7E", "#7A9CB0", "#9C6B8E", "#B98B73"],
    ),
    "Sage Garden": dict(
        bg="#F3F6EE", surface="#FCFDF9", sidebar="#E4EBDA", lane="#EBF0E2", ink="#26332B", muted="#6F8076",
        line="#DAE3CF", accent="#4F7A5C", accent2="#C9A45C", glow="#D5E4C6",
        series=["#4F7A5C", "#C9A45C", "#C2714F", "#6F94A6", "#9C6B8E", "#8FA37A"],
    ),
    "Blush Hour": dict(
        bg="#FCF3F1", surface="#FFFBFA", sidebar="#F6E3DF", lane="#F9E9E5", ink="#3D2A2E", muted="#8F7479",
        line="#F0D9D4", accent="#B5546B", accent2="#E3A27A", glow="#F6D0CC",
        series=["#B5546B", "#E3A27A", "#7C9A7E", "#7A9CB0", "#8C6BA0", "#C48B7A"],
    ),
}
DEFAULT = "Oat Latte"


def palette() -> dict:
    return PALETTES.get(st.session_state.get("palette", DEFAULT), PALETTES[DEFAULT])


def rgba(hex_color: str, alpha: float) -> str:
    h = hex_color.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return f"rgba({r},{g},{b},{alpha})"


def stage_colors(p: dict | None = None) -> dict:
    s = (p or palette())["series"]
    return {"Lead": s[5], "Qualified": s[3], "Proposal": s[1], "Negotiation": s[4], "Won": s[2], "Lost": "#A39A92"}


STATIC_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600;9..144,700&family=DM+Sans:wght@400;500;600;700&display=swap');

html, body, .stApp, button, input, textarea, select { font-family: 'DM Sans', system-ui, sans-serif; }
.stApp {
  color: var(--ink);
  background:
    radial-gradient(900px 480px at 92% -8%, var(--glow) 0%, transparent 65%),
    radial-gradient(700px 420px at -5% 105%, var(--glow) 0%, transparent 60%),
    var(--bg);
}
.stApp p, .stApp label, .stApp li, .stMarkdown, [data-testid="stWidgetLabel"] p, [data-testid="stCaptionContainer"] { color: var(--ink); }
h1, h2, h3, h4 { font-family: 'Fraunces', Georgia, serif !important; color: var(--ink) !important; letter-spacing: -0.01em; }
header[data-testid="stHeader"] { background: transparent; }
#MainMenu, footer, [data-testid="stToolbar"] { visibility: hidden; }
.block-container { padding-top: 2.4rem; padding-bottom: 4rem; max-width: 1320px; }
::selection { background: var(--accent); color: #fff; }

/* ---------- sidebar ---------- */
section[data-testid="stSidebar"] { background: var(--sidebar); border-right: 1px solid var(--line); }
section[data-testid="stSidebar"] .block-container { padding-top: 1.6rem; }
.brand { display:flex; align-items:center; gap:12px; margin: 4px 4px 22px; }
.brand-mark { width:42px; height:42px; border-radius:14px; display:grid; place-items:center; color:#fff;
  font-family:'Fraunces',serif; font-weight:700; font-size:24px; background: linear-gradient(135deg, var(--accent), var(--accent2));
  box-shadow: 0 8px 18px -6px var(--accent); transform: rotate(-6deg); }
.brand-name { font-family:'Fraunces',serif; font-size:24px; font-weight:700; line-height:1; color:var(--ink); }
.brand-sub { font-size:11px; letter-spacing:.18em; text-transform:uppercase; color:var(--muted); margin-top:4px; }
.side-label { font-size:11px; letter-spacing:.16em; text-transform:uppercase; color:var(--muted); margin: 22px 6px 6px; font-weight:600; }
section[data-testid="stSidebar"] div[role="radiogroup"] { gap: 4px; }
section[data-testid="stSidebar"] div[role="radiogroup"] label { width:100%; padding: 10px 14px; border-radius: 14px; cursor:pointer; transition: all .18s ease; }
section[data-testid="stSidebar"] div[role="radiogroup"] label > div:first-child { display:none; }
section[data-testid="stSidebar"] div[role="radiogroup"] label:hover { background: rgba(0,0,0,.045); transform: translateX(3px); }
section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) { background: var(--accent); box-shadow: 0 10px 20px -10px var(--accent); }
section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) p { color:#fff !important; font-weight:600; }
section[data-testid="stSidebar"] div[role="radiogroup"] label p { font-size: 15px; }
.side-note { margin-top: 26px; padding: 14px 16px; border-radius: 16px; background: var(--surface); border: 1px solid var(--line);
  font-size: 13px; color: var(--muted); line-height: 1.5; }
.side-note b { color: var(--ink); }

/* ---------- hero ---------- */
.hero { margin: 0 0 26px; }
.eyebrow { font-size: 12px; letter-spacing:.18em; text-transform: uppercase; color: var(--accent); font-weight:700; margin-bottom: 8px; }
.hero-title { font-family:'Fraunces',serif; font-size: 40px; font-weight:600; letter-spacing:-.02em; line-height:1.1; color: var(--ink); }
.hero-sub { color: var(--muted); font-size: 16px; margin-top: 8px; }
.wave { display:inline-block; animation: wave 2.4s ease-in-out infinite; transform-origin: 70% 70%; }
@keyframes wave { 0%,60%,100%{transform:rotate(0)} 10%,30%{transform:rotate(14deg)} 20%,40%{transform:rotate(-8deg)} 50%{transform:rotate(10deg)} }
@keyframes rise { from { opacity:0; transform: translateY(10px);} to { opacity:1; transform:none; } }

/* ---------- cards & panels ---------- */
[class*="st-key-panel"] { background: var(--surface); border: 1px solid var(--line); border-radius: 22px; padding: 20px 22px;
  box-shadow: 0 1px 0 rgba(255,255,255,.8) inset, 0 14px 30px -22px rgba(60,40,20,.35); animation: rise .45s ease both; }
[class*="st-key-lane"] { background: var(--lane); border: 1px dashed var(--line); border-radius: 22px; padding: 14px 12px; min-height: 120px; }
.panel-title { font-family:'Fraunces',serif; font-size: 20px; font-weight:600; color: var(--ink); margin-bottom: 2px; }
.panel-title span { font-family:'DM Sans',sans-serif; font-size: 12px; font-weight:500; color: var(--muted); margin-left: 8px; }
.kpis { display:grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 18px; }
@media (max-width: 900px) { .kpis { grid-template-columns: repeat(2, 1fr); } .hero-title { font-size: 30px; } }
.kpi { background: var(--surface); border:1px solid var(--line); border-radius: 22px; padding: 20px 22px; position:relative; overflow:hidden;
  box-shadow: 0 14px 30px -22px rgba(60,40,20,.4); transition: transform .2s ease, box-shadow .2s ease; animation: rise .5s ease both; }
.kpi:nth-child(2){animation-delay:.06s} .kpi:nth-child(3){animation-delay:.12s} .kpi:nth-child(4){animation-delay:.18s}
.kpi:hover { transform: translateY(-3px); box-shadow: 0 22px 36px -22px rgba(60,40,20,.5); }
.kpi-icon { width:38px; height:38px; border-radius: 12px; display:grid; place-items:center; font-size:18px; background: var(--lane); margin-bottom: 14px; }
.kpi-label { font-size: 13px; color: var(--muted); font-weight:500; }
.kpi-value { font-family:'Fraunces',serif; font-size: 32px; font-weight:600; letter-spacing:-.02em; margin-top: 2px; color: var(--ink); }
.kpi-sub { font-size: 12.5px; color: var(--muted); margin-top: 6px; }
.kpi-sub.up { color: #4C8A5B; font-weight:600; } .kpi-sub.down { color: #C0483C; font-weight:600; }
.kpi.feature { background: linear-gradient(140deg, var(--accent), var(--accent2)); border: none; }
.kpi.feature .kpi-label, .kpi.feature .kpi-value, .kpi.feature .kpi-sub { color:#fff; }
.kpi.feature .kpi-icon { background: rgba(255,255,255,.25); }
.kpi.feature::after { content:""; position:absolute; right:-30px; top:-30px; width:120px; height:120px; border-radius:50%; background: rgba(255,255,255,.15); }

/* ---------- chips, avatars, lists ---------- */
.chip { display:inline-block; padding: 3px 10px; border-radius: 999px; font-size: 11.5px; font-weight:600; white-space:nowrap;
  background: color-mix(in srgb, var(--c) 17%, transparent); color: color-mix(in srgb, var(--c) 72%, #000); }
.avatar { width:44px; height:44px; border-radius: 15px; display:grid; place-items:center; color:#fff; font-weight:700; font-size:15px;
  font-family:'Fraunces',serif; background: var(--c); flex: none; }
.person { display:flex; gap:14px; align-items:center; }
.person-name { font-weight:700; color: var(--ink); font-size: 16px; line-height:1.2; }
.person-sub { color: var(--muted); font-size: 13px; }
.meta-row { display:flex; justify-content:space-between; align-items:center; margin-top: 14px; font-size: 13px; color: var(--muted); }
.meta-line { font-size: 13px; color: var(--muted); margin-top: 10px; line-height: 1.7; word-break: break-all; }
.task-row { display:flex; align-items:center; justify-content:space-between; gap:10px; padding: 11px 0; border-bottom: 1px dashed var(--line); font-size: 14px; }
.task-row:last-child { border-bottom: none; }
.task-title { color: var(--ink); font-weight: 500; }
.due { font-size: 12px; color: var(--muted); font-weight:600; } .due.over { color:#C0483C; } .due.today { color: var(--accent); }
.tl-item { display:flex; gap: 12px; padding: 9px 0; align-items:flex-start; }
.tl-dot { width: 30px; height: 30px; border-radius: 10px; background: var(--lane); display:grid; place-items:center; font-size: 14px; flex:none; }
.tl-text { font-size: 13.5px; color: var(--ink); line-height: 1.35; } .tl-time { font-size: 11.5px; color: var(--muted); margin-top: 2px; }
.empty { text-align:center; color: var(--muted); padding: 26px 8px; font-size: 14px; }

/* ---------- kanban cards ---------- */
.lane-head { display:flex; justify-content:space-between; align-items:center; margin: 2px 4px 12px; }
.lane-name { font-family:'Fraunces',serif; font-weight:600; font-size: 17px; color: var(--ink); display:flex; align-items:center; gap:8px; }
.lane-dot { width:10px; height:10px; border-radius:50%; background: var(--c); }
.lane-sum { font-size: 12px; color: var(--muted); font-weight:600; }
.deal { background: var(--surface); border:1px solid var(--line); border-radius: 16px; padding: 14px 14px 12px; margin-bottom: 6px;
  box-shadow: 0 8px 18px -14px rgba(60,40,20,.5); border-left: 4px solid var(--c); }
.deal-title { font-weight:700; font-size: 14.5px; color: var(--ink); line-height:1.25; }
.deal-co { color: var(--muted); font-size: 12.5px; margin-top: 2px; }
.deal-foot { display:flex; justify-content:space-between; align-items:center; margin-top: 10px; }
.deal-val { font-family:'Fraunces',serif; font-weight:600; font-size: 17px; color: var(--ink); }

/* ---------- table ---------- */
.tbl { width:100%; border-collapse: separate; border-spacing: 0 8px; }
.tbl th { text-align:left; font-size: 11px; letter-spacing:.14em; text-transform:uppercase; color: var(--muted); font-weight:600; padding: 0 14px 4px; }
.tbl td { background: var(--surface); padding: 14px; font-size: 14px; color: var(--ink); border-top:1px solid var(--line); border-bottom:1px solid var(--line); }
.tbl td:first-child { border-left:1px solid var(--line); border-radius: 16px 0 0 16px; }
.tbl td:last-child { border-right:1px solid var(--line); border-radius: 0 16px 16px 0; }
.tbl tr:hover td { background: var(--lane); }
.tbl .num { font-family:'Fraunces',serif; font-weight:600; font-size: 16px; }
.t-main { font-weight:700; } .t-sub { color: var(--muted); font-size: 12.5px; }
.bar { width: 90px; height: 7px; background: var(--line); border-radius: 99px; overflow:hidden; }
.bar i { display:block; height:100%; background: linear-gradient(90deg, var(--accent), var(--accent2)); border-radius:99px; }

/* ---------- native widgets, softened ---------- */
.stButton > button, .stDownloadButton > button, .stFormSubmitButton > button {
  border-radius: 12px; border: 1px solid var(--line); background: var(--surface); color: var(--ink); font-weight: 600;
  transition: all .18s ease; width: 100%; }
.stButton > button:hover, .stDownloadButton > button:hover { border-color: var(--accent); color: var(--accent); transform: translateY(-1px);
  box-shadow: 0 10px 18px -12px var(--accent); }
.stButton > button p, .stFormSubmitButton > button p { color: inherit !important; }
button[kind="primary"], button[kind="primaryFormSubmit"], [data-testid="stBaseButton-primary"], [data-testid="stBaseButton-primaryFormSubmit"] {
  background: var(--accent) !important; color:#fff !important; border: none !important; }
button[kind="primary"]:hover, [data-testid="stBaseButton-primary"]:hover { filter: brightness(1.07); color:#fff !important; }
[data-testid="stBaseButton-primary"] p, [data-testid="stBaseButton-primaryFormSubmit"] p { color:#fff !important; }
div[data-baseweb="input"], div[data-baseweb="textarea"], div[data-baseweb="select"] > div {
  background: var(--surface) !important; border-radius: 12px !important; border: 1px solid var(--line) !important; }
div[data-baseweb="input"]:focus-within, div[data-baseweb="select"] > div:focus-within { border-color: var(--accent) !important; box-shadow: 0 0 0 3px color-mix(in srgb, var(--accent) 18%, transparent); }
div[data-baseweb="input"] input, div[data-baseweb="textarea"] textarea { background: transparent !important; color: var(--ink) !important; }
div[role="dialog"] { background: var(--bg) !important; border-radius: 24px !important; }
[data-testid="stExpander"] { border: 1px solid var(--line) !important; border-radius: 18px !important; background: var(--surface); }
[data-testid="stCheckbox"] label p { font-weight: 500; }
div[data-baseweb="popover"] > div { border-radius: 16px; }
[data-testid="stPlotlyChart"] { margin-top: -6px; }

/* ---------- force the cozy light look even if Streamlit / the browser is in dark mode ---------- */
:root, .stApp, section[data-testid="stSidebar"] { color-scheme: light; }
/* text inputs: one soft shell, transparent inner layers */
div[data-baseweb="input"], div[data-baseweb="base-input"], div[data-baseweb="textarea"] { background: var(--surface) !important; }
div[data-baseweb="base-input"] { border: none !important; }
input, textarea { color: var(--ink) !important; -webkit-text-fill-color: var(--ink) !important; background: transparent !important; }
input::placeholder, textarea::placeholder { color: var(--muted) !important; -webkit-text-fill-color: var(--muted) !important; opacity: 1; }
/* selects + multiselects */
div[data-baseweb="select"] > div, div[data-baseweb="select"] > div > div { background: var(--surface) !important; color: var(--ink) !important; }
div[data-baseweb="select"] * { color: var(--ink); }
div[data-baseweb="select"] svg { fill: var(--muted) !important; }
div[data-baseweb="select"] input { color: var(--ink) !important; }
/* dropdown / popover menus */
div[data-baseweb="popover"], div[data-baseweb="popover"] > div, [data-baseweb="menu"], div[data-baseweb="popover"] ul,
[data-testid="stPopoverBody"] { background: var(--surface) !important; color: var(--ink) !important; }
div[data-baseweb="popover"] li, [data-baseweb="menu"] li { background: transparent !important; color: var(--ink) !important; }
div[data-baseweb="popover"] li:hover, [data-baseweb="menu"] li:hover { background: var(--lane) !important; }
/* the "Manage" popover button and any other secondary buttons */
[data-testid="stPopover"] button, [data-testid="stPopoverButton"], button[kind="secondary"], [data-testid="stBaseButton-secondary"],
[data-testid="stBaseButton-secondaryFormSubmit"] { background: var(--surface) !important; color: var(--ink) !important; border: 1px solid var(--line) !important; border-radius: 12px !important; }
[data-testid="stPopover"] button *, [data-testid="stPopoverButton"] *, [data-testid="stBaseButton-secondary"] * { color: var(--ink) !important; }
[data-testid="stPopover"] button svg { fill: var(--muted) !important; }
[data-testid="stPopover"] button:hover, [data-testid="stPopoverButton"]:hover, [data-testid="stBaseButton-secondary"]:hover { border-color: var(--accent) !important; }
[data-testid="stPopover"] button:hover *, [data-testid="stBaseButton-secondary"]:hover * { color: var(--accent) !important; }
[data-testid="stBaseButton-primary"], [data-testid="stBaseButton-primaryFormSubmit"] { background: var(--accent) !important; color: #fff !important; border: none !important; }
[data-testid="stBaseButton-primary"] * { color: #fff !important; }
/* sidebar nav: hide the round radio indicator whatever the markup, keep only the label text */
section[data-testid="stSidebar"] div[role="radiogroup"] label > div:not(:has([data-testid="stMarkdownContainer"])) { display: none !important; }
section[data-testid="stSidebar"] div[role="radiogroup"] label { background: transparent; }
/* checkboxes + expanders + dialogs */
[data-testid="stExpander"] summary, [data-testid="stExpander"] summary * { color: var(--ink) !important; }
[data-testid="stExpander"] details { background: var(--surface); }
[data-testid="stDialog"] > div, div[role="dialog"], div[role="dialog"] > div { background: var(--bg) !important; color: var(--ink); }
[data-testid="stTooltipContent"] { background: var(--ink) !important; }
"""


def inject(name: str) -> None:
    p = PALETTES.get(name, PALETTES[DEFAULT])
    root = ":root{" + "".join(f"--{k}:{v};" for k, v in p.items() if k != "series") + "}"
    st.markdown(f"<style>{root}{STATIC_CSS}</style>", unsafe_allow_html=True)
