from datetime import date

import streamlit as st

from services.metas_service import (
    VALID_CATEGORIES,
    VALID_STATUS,
    delete_goal,
    get_goal,
    update_goal,
)
from utils.ui import badge, progress_bar_html, safe_text


CATEGORY_LABELS = {
    "70": "70% · Experiência",
    "20": "20% · Exposição",
    "10": "10% · Educação",
}


def _back():
    st.session_state.pop("detail_view", None)
    st.session_state.pop("detail_id", None)
    st.rerun()


def render(goal_id):
    goal = get_goal(goal_id)

    if not goal:
        st.error("Meta não encontrada.")
        if st.button("← Voltar para o PDI"):
            _back()
        return

    if st.button("← Voltar para o PDI"):
        _back()

    st.markdown(
        (
            '<div class="dh-detail-shell">'
            '<div class="dh-detail-kicker">META DE DESENVOLVIMENTO</div>'
            f'<div class="dh-detail-title">{safe_text(goal["title"])}</div>'
            '<div class="dh-meta">'
            f'{badge(CATEGORY_LABELS[goal["category"]])}'
            f'{badge(goal["status"])}'
            f'{badge(f"{goal["progress"]}%")}'
            f'{badge(goal["competency"]) if goal.get("competency") else ""}'
            "</div>"
            f'{progress_bar_html(goal["progress"])}'
            "</div>"
        ),
        unsafe_allow_html=True,
    )

    with st.container(border=True):
        st.subheader("Detalhes da meta")

        with st.form(f"pdi_detail_{goal_id}"):
            c1, c2 = st.columns(2)
            title = c1.text_input("Título", value=goal.get("title", ""))
            category = c2.selectbox(
                "Categoria",
                VALID_CATEGORIES,
                index=VALID_CATEGORIES.index(goal["category"]),
                format_func=lambda value: CATEGORY_LABELS[value],
            )

            strategic_objective = st.text_area(
                "Objetivo estratégico",
                value=goal.get("strategic_objective", ""),
                height=110,
            )
            description = st.text_area(
                "Descrição",
                value=goal.get("description", ""),
                height=110,
            )

            c1, c2, c3 = st.columns(3)
            start_date = c1.date_input(
                "Data inicial",
                value=date.fromisoformat(goal["start_date"]),
            )
            end_date = c2.date_input(
                "Data final",
                value=date.fromisoformat(goal["end_date"]),
            )
            status = c3.selectbox(
                "Status",
                VALID_STATUS,
                index=VALID_STATUS.index(goal["status"]),
            )

            progress = st.slider(
                "Progresso (%)",
                0,
                100,
                int(goal["progress"]),
                5,
            )

            c1, c2 = st.columns(2)
            competency = c1.text_input(
                "Competência desenvolvida",
                value=goal.get("competency", ""),
            )
            evidence = c2.text_area(
                "Evidência",
                value=goal.get("evidence", ""),
                height=100,
            )

            result = st.text_area(
                "Resultado obtido",
                value=goal.get("result", ""),
                height=110,
            )

            if st.form_submit_button(
                "Salvar alterações",
                use_container_width=True,
            ):
                try:
                    updated = update_goal(
                        goal_id,
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
                    if updated:
                        st.success("Meta atualizada com sucesso.")
                    else:
                        st.error("Não foi possível localizar a meta.")
                except Exception as error:
                    st.error(str(error))

    with st.expander("Zona de exclusão", expanded=False):
        st.warning("A exclusão da meta é permanente.")
        confirm = st.checkbox(
            "Confirmo que desejo excluir esta meta",
            key=f"delete_goal_confirm_{goal_id}",
        )
        if st.button(
            "Excluir meta",
            disabled=not confirm,
            type="secondary",
            use_container_width=True,
        ):
            if delete_goal(goal_id):
                _back()
            else:
                st.error("Não foi possível localizar a meta.")
