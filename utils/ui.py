import html
from datetime import date, datetime

import streamlit as st


NAV_ITEMS = {
    "Dashboard": "▦",
    "Kanban": "▤",
    "Projetos": "◆",
    "PDI": "◎",
}


def apply_global_styles():
    st.markdown(
        """
        <style>
        :root {
            --bg: #f5f7fb;
            --surface: #ffffff;
            --surface-soft: #f8fafc;
            --stroke: #e2e8f0;
            --stroke-strong: #cbd5e1;
            --text: #172033;
            --muted: #64748b;
            --primary: #6557e8;
            --primary-strong: #5145cd;
            --secondary: #0e7490;
            --sidebar: #0d1424;
        }

        html, body, [data-testid="stAppViewContainer"], .stApp {
            background: var(--bg);
            color: var(--text);
        }

        [data-testid="stHeader"] {
            background: rgba(245, 247, 251, .96);
            border-bottom: 1px solid var(--stroke);
        }

        [data-testid="stSidebarNav"] {
            display: none !important;
        }

        .block-container {
            max-width: 1480px;
            padding-top: 2rem;
            padding-bottom: 3rem;
        }

        section[data-testid="stSidebar"] {
            background: var(--sidebar);
            border-right: 1px solid rgba(148, 163, 184, .12);
        }

        section[data-testid="stSidebar"] > div {
            padding-top: 1rem;
        }

        section[data-testid="stSidebar"] [data-testid="stRadio"] > label {
            display: none;
        }

        section[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] {
            gap: .45rem;
        }

        section[data-testid="stSidebar"] [data-testid="stRadio"] label {
            background: transparent;
            border: 1px solid transparent;
            border-radius: 12px;
            padding: .72rem .8rem;
            transition: background .15s ease, border-color .15s ease, transform .15s ease;
        }

        section[data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
            background: rgba(148, 163, 184, .09);
            border-color: rgba(148, 163, 184, .08);
            transform: translateX(2px);
        }

        section[data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) {
            background: linear-gradient(135deg, rgba(101, 87, 232, .98), rgba(14, 116, 144, .96));
            border-color: rgba(255, 255, 255, .08);
            box-shadow: 0 10px 26px rgba(0, 0, 0, .18);
        }

        section[data-testid="stSidebar"] [data-testid="stRadio"] label p {
            color: #dbe3f0 !important;
            font-weight: 680;
            font-size: .9rem;
        }

        section[data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) p {
            color: #ffffff !important;
        }

        section[data-testid="stSidebar"] [data-testid="stRadio"] [data-testid="stMarkdownContainer"] {
            margin: 0;
        }

        h1, h2, h3, h4, h5, h6 {
            color: var(--text);
            letter-spacing: -0.02em;
        }

        div[data-testid="stMetric"] {
            background: var(--surface);
            border: 1px solid var(--stroke);
            border-radius: 18px;
            padding: 1rem;
            box-shadow: 0 8px 24px rgba(15, 23, 42, .055);
        }

        div[data-testid="stMetric"] label {
            color: var(--muted) !important;
            font-weight: 600;
        }

        div[data-testid="stMetricValue"] {
            color: var(--text);
        }

        .stButton > button,
        .stForm button {
            border: 1px solid transparent;
            border-radius: 11px;
            background: linear-gradient(135deg, var(--primary), var(--primary-strong));
            color: #ffffff !important;
            font-weight: 700;
            min-height: 2.55rem;
            box-shadow: 0 7px 18px rgba(101, 87, 232, .17);
        }

        .stButton > button:hover,
        .stForm button:hover {
            filter: brightness(1.04);
            border-color: transparent;
        }

        .stTextInput input,
        .stTextArea textarea,
        .stDateInput input,
        .stNumberInput input {
            background: #ffffff !important;
            border: 1px solid var(--stroke-strong) !important;
            border-radius: 11px !important;
            color: var(--text) !important;
        }

        div[data-baseweb="select"] > div {
            background: #ffffff !important;
            border-color: var(--stroke-strong) !important;
            border-radius: 11px !important;
            color: var(--text) !important;
        }

        div[data-testid="stExpander"] {
            background: #ffffff;
            border: 1px solid var(--stroke);
            border-radius: 14px;
        }

        .dh-sidebar-brand {
            padding: .35rem .15rem 1.05rem;
            margin-bottom: .25rem;
            border-bottom: 1px solid rgba(148, 163, 184, .12);
        }

        .dh-sidebar-eyebrow {
            color: #67e8f9;
            font-size: .68rem;
            font-weight: 850;
            letter-spacing: .16em;
        }

        .dh-sidebar-title {
            color: #f8fafc;
            font-size: 1.22rem;
            font-weight: 820;
            margin-top: .25rem;
        }

        .dh-sidebar-subtitle {
            color: #94a3b8;
            font-size: .76rem;
            margin-top: .22rem;
        }

        .dh-sidebar-section {
            color: #64748b;
            font-size: .65rem;
            font-weight: 820;
            letter-spacing: .14em;
            margin: 1rem .15rem .45rem;
        }

        .dh-hero {
            padding: 1.35rem 1.5rem;
            border-radius: 21px;
            background: linear-gradient(135deg, #eef2ff 0%, #ecfeff 100%);
            border: 1px solid #dbe3f0;
            margin-bottom: 1.25rem;
            box-shadow: 0 9px 28px rgba(15, 23, 42, .045);
        }

        .dh-eyebrow {
            color: var(--secondary);
            font-size: .74rem;
            font-weight: 820;
            letter-spacing: .14em;
            text-transform: uppercase;
            margin-bottom: .35rem;
        }

        .dh-hero h1 {
            margin: 0;
            color: var(--text);
            font-size: clamp(2rem, 4vw, 3rem);
        }

        .dh-hero p {
            color: var(--muted);
            max-width: 900px;
            margin: .45rem 0 0;
            font-size: .98rem;
        }

        .dh-section-title {
            color: var(--text);
            font-size: 1.05rem;
            font-weight: 780;
            margin: 1.4rem 0 .78rem;
        }

        .dh-card {
            background: var(--surface);
            border: 1px solid var(--stroke);
            border-radius: 16px;
            padding: 1rem;
            margin-bottom: .7rem;
            box-shadow: 0 7px 22px rgba(15, 23, 42, .05);
        }

        .dh-card-title {
            color: var(--text);
            font-size: .98rem;
            font-weight: 760;
            margin-bottom: .35rem;
        }

        .dh-card-desc {
            color: var(--muted);
            font-size: .88rem;
            line-height: 1.5;
            margin-bottom: .65rem;
        }

        .dh-meta {
            color: var(--muted);
            font-size: .78rem;
            display: flex;
            gap: .42rem;
            flex-wrap: wrap;
        }

        .dh-badge {
            display: inline-flex;
            align-items: center;
            padding: .27rem .56rem;
            border-radius: 999px;
            border: 1px solid #dbe3f0;
            background: #f8fafc;
            color: #475569;
            font-size: .72rem;
            font-weight: 700;
        }

        .dh-empty {
            border: 1px dashed #cbd5e1;
            border-radius: 14px;
            padding: 1.2rem;
            text-align: center;
            color: var(--muted);
            background: #ffffff;
        }

        .dh-column-head {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: .2rem .15rem .65rem;
        }

        .dh-column-title {
            color: var(--text);
            font-size: .9rem;
            font-weight: 800;
        }

        .dh-count {
            min-width: 26px;
            height: 26px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            border-radius: 999px;
            background: #ede9fe;
            border: 1px solid #ddd6fe;
            color: #5b21b6;
            font-size: .72rem;
            font-weight: 800;
        }

        .dh-project {
            border-left: 3px solid var(--primary);
        }

        .dh-goal {
            border-left: 3px solid var(--secondary);
        }

        .dh-progress-track {
            width: 100%;
            height: 8px;
            background: #e2e8f0;
            border-radius: 999px;
            overflow: hidden;
            margin-top: .7rem;
        }

        .dh-progress-fill {
            height: 100%;
            background: linear-gradient(90deg, var(--primary), var(--secondary));
            border-radius: 999px;
        }

        .dh-detail-shell {
            max-width: 1050px;
            margin: 0 auto;
        }

        .dh-detail-kicker {
            color: var(--secondary);
            font-size: .72rem;
            font-weight: 820;
            letter-spacing: .13em;
            text-transform: uppercase;
            margin-bottom: .3rem;
        }

        .dh-detail-title {
            color: var(--text);
            font-size: 2rem;
            line-height: 1.15;
            font-weight: 820;
            margin-bottom: .35rem;
        }

        .dh-detail-subtitle {
            color: var(--muted);
            font-size: .92rem;
            margin-bottom: 1.15rem;
        }

        .dh-card-edit-row {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: .75rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def sidebar_navigation():
    st.sidebar.markdown(
        """
        <div class="dh-sidebar-brand">
            <div class="dh-sidebar-eyebrow">DEVELOPMENT HUB</div>
            <div class="dh-sidebar-title">Personal Growth OS</div>
            <div class="dh-sidebar-subtitle">Projetos · Tarefas · PDI</div>
        </div>
        <div class="dh-sidebar-section">NAVEGAÇÃO</div>
        """,
        unsafe_allow_html=True,
    )

    labels = list(NAV_ITEMS)
    current = st.session_state.get("active_view", "Dashboard")
    if current not in labels:
        current = "Dashboard"

    previous = st.session_state.get("_sidebar_previous", current)
    selected = st.sidebar.radio(
        "Navegação",
        labels,
        index=labels.index(current),
        format_func=lambda item: f"{NAV_ITEMS[item]}  {item}",
        label_visibility="collapsed",
        key="nav_radio",
    )

    if selected != previous:
        st.session_state.pop("detail_view", None)
        st.session_state.pop("detail_id", None)

    st.session_state["_sidebar_previous"] = selected
    st.session_state["active_view"] = selected

    st.sidebar.markdown(
        """
        <div style="margin-top:1.2rem;padding:.9rem .15rem 0;border-top:1px solid rgba(148,163,184,.12);">
            <div style="color:#64748b;font-size:.66rem;font-weight:800;letter-spacing:.12em;">WORKSPACE</div>
            <div style="color:#94a3b8;font-size:.74rem;margin-top:.35rem;line-height:1.45;">
                Organize execução, portfólio e evolução profissional em um único ambiente.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    return selected


def hero(title, subtitle, eyebrow="DEVELOPMENT HUB"):
    st.markdown(
        f"""
        <div class="dh-hero">
            <div class="dh-eyebrow">{html.escape(eyebrow)}</div>
            <h1>{html.escape(title)}</h1>
            <p>{html.escape(subtitle)}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_title(text):
    st.markdown(
        f'<div class="dh-section-title">{html.escape(text)}</div>',
        unsafe_allow_html=True,
    )


def badge(text):
    return f'<span class="dh-badge">{html.escape(str(text))}</span>'


def safe_text(value):
    return html.escape(str(value or ""))


def format_date(value):
    if not value:
        return "Sem prazo"
    try:
        parsed = datetime.fromisoformat(str(value)).date()
        return parsed.strftime("%d/%m/%Y")
    except ValueError:
        try:
            parsed = date.fromisoformat(str(value))
            return parsed.strftime("%d/%m/%Y")
        except ValueError:
            return str(value)


def progress_bar_html(progress):
    value = max(0, min(100, int(progress or 0)))
    return (
        '<div class="dh-progress-track">'
        f'<div class="dh-progress-fill" style="width:{value}%"></div>'
        "</div>"
    )
