from datetime import date

import streamlit as st

from services.metas_service import (
    VALID_CATEGORIES,
    VALID_STATUS,
    add_goal,
    list_goals,
    summarize_by_category,
)
from utils.ui import badge, hero, progress_bar_html, safe_text, section_title


CATEGORY_LABELS = {
    "70": "70% · Experiência",
    "20": "20% · Exposição",
    "10": "10% · Educação",
}


def _open_goal(goal_id):
    st.session_state["detail_view"] = "pdi"
    st.session_state["detail_id"] = goal_id
    st.rerun()


def render():
    hero(
        "PDI 70/20/10",
        "Transforme aprendizado em aplicação prática, evidências e resultados profissionais.",
        "PROFESSIONAL GROWTH",
    )

    with st.expander("＋ Nova meta", expanded=False):
        with st.form("new_goal", clear_on_submit=True):
            c1, c2 = st.columns(2)
            title = c1.text_input("Título")
            category = c2.selectbox(
                "Categoria",
                VALID_CATEGORIES,
                format_func=lambda value: CATEGORY_LABELS[value],
            )
            strategic_objective = st.text_area("Objetivo estratégico", height=70)
            description = st.text_area("Descrição", height=80)
            c1, c2, c3 = st.columns(3)
            start_date = c1.date_input("Data inicial", value=date.today())
            end_date = c2.date_input("Data final", value=date.today())
            status = c3.selectbox("Status", VALID_STATUS, index=0)
            progress = st.slider("Progresso (%)", 0, 100, 0, 5)
            c1, c2 = st.columns(2)
            competency = c1.text_input("Competência desenvolvida")
            evidence = c2.text_area("Evidência", height=70)
            result = st.text_area("Resultado obtido", height=70)

            if st.form_submit_button("Criar meta", use_container_width=True):
                try:
                    add_goal(
                        title,
                        description,
                        category,
                        start_date,
                        end_date,
                        status,
                        progress,
                        strategic_objective,
                        evidence,
                        competency,
                        result,
                    )
                    st.success("Meta criada.")
                    st.rerun()
                except Exception as error:
                    st.error(str(error))

    summary = summarize_by_category()
    m1, m2, m3 = st.columns(3)
    m1.metric(
        "70% · Experiência",
        f'{summary["70"]["count"]} metas',
        f'{summary["70"]["avg_progress"]}% médio',
    )
    m2.metric(
        "20% · Exposição",
        f'{summary["20"]["count"]} metas',
        f'{summary["20"]["avg_progress"]}% médio',
    )
    m3.metric(
        "10% · Educação",
        f'{summary["10"]["count"]} metas',
        f'{summary["10"]["avg_progress"]}% médio',
    )

    section_title("Metas de desenvolvimento")

    f1, f2 = st.columns(2)
    filter_category = f1.selectbox(
        "Categoria",
        ["Todas"] + VALID_CATEGORIES,
        format_func=lambda value: value if value == "Todas" else CATEGORY_LABELS[value],
    )
    filter_status = f2.selectbox("Status", ["Todos"] + VALID_STATUS)

    goals = list_goals(filter_category, filter_status)

    if not goals:
        st.markdown(
            '<div class="dh-empty">Nenhuma meta encontrada para os filtros atuais.</div>',
            unsafe_allow_html=True,
        )
        return

    for goal in goals:
        with st.container(border=True):
            title_col, edit_col = st.columns([12, 1])

            with title_col:
                st.markdown(
                    f'<div class="dh-card-title">{safe_text(goal["title"])}</div>',
                    unsafe_allow_html=True,
                )

            with edit_col:
                if st.button(
                    "✎",
                    key=f"edit_goal_{goal['id']}",
                    help="Abrir meta",
                    use_container_width=True,
                ):
                    _open_goal(goal["id"])

            objective = (
                safe_text(goal.get("strategic_objective"))
                or safe_text(goal.get("description"))
                or "Sem objetivo estratégico descrito."
            )

            st.markdown(
                f'<div class="dh-card-desc">{objective}</div>',
                unsafe_allow_html=True,
            )

            competency = badge(goal["competency"]) if goal.get("competency") else ""

            st.markdown(
                (
                    '<div class="dh-meta">'
                    f'{badge(f"{goal["category"]}%")}'
                    f'{badge(goal["status"])}'
                    f'{badge(f"{goal["progress"]}%")}'
                    f'{competency}'
                    "</div>"
                ),
                unsafe_allow_html=True,
            )

            st.markdown(
                progress_bar_html(goal["progress"]),
                unsafe_allow_html=True,
            )
