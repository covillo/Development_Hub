from datetime import date

import streamlit as st

from services.projetos_service import (
    VALID_PROJECT_STATUS,
    add_project,
    list_projects,
)
from utils.ui import badge, hero, progress_bar_html, safe_text, section_title


def _open_project(project_id):
    st.session_state["detail_view"] = "projeto"
    st.session_state["detail_id"] = project_id
    st.rerun()


def render():
    hero(
        "Projetos",
        "Registre iniciativas, tecnologias, evolução e resultados que fortalecem seu portfólio.",
        "PORTFOLIO MANAGEMENT",
    )

    with st.expander("＋ Novo projeto", expanded=False):
        with st.form("new_project", clear_on_submit=True):
            c1, c2 = st.columns(2)
            name = c1.text_input("Nome")
            status = c2.selectbox("Status", VALID_PROJECT_STATUS, index=0)
            description = st.text_area("Descrição", height=80)
            objective = st.text_area("Objetivo", height=80)
            c1, c2 = st.columns(2)
            technology = c1.text_input(
                "Tecnologias",
                placeholder="Python · Streamlit · SQLite",
            )
            repository_url = c2.text_input("Repositório")
            c1, c2 = st.columns(2)
            start_date = c1.date_input("Data inicial", value=date.today())
            has_end_date = c2.checkbox("Definir data final")
            end_date = c2.date_input(
                "Data final",
                value=date.today(),
                disabled=not has_end_date,
            )
            result = st.text_area("Resultado / impacto", height=80)

            if st.form_submit_button("Criar projeto", use_container_width=True):
                try:
                    add_project(
                        name,
                        description,
                        objective,
                        status,
                        technology,
                        start_date,
                        end_date if has_end_date else None,
                        repository_url,
                        result,
                    )
                    st.success("Projeto criado.")
                    st.rerun()
                except Exception as error:
                    st.error(str(error))

    section_title("Portfólio")

    filter_status = st.selectbox(
        "Filtrar status",
        ["Todos"] + VALID_PROJECT_STATUS,
    )
    projects = list_projects(filter_status)

    if not projects:
        st.markdown(
            '<div class="dh-empty">Nenhum projeto encontrado para o filtro atual.</div>',
            unsafe_allow_html=True,
        )
        return

    cards = st.columns(2)

    for index, project in enumerate(projects):
        with cards[index % 2]:
            with st.container(border=True):
                title_col, edit_col = st.columns([9, 1])

                with title_col:
                    st.markdown(
                        f'<div class="dh-card-title">{safe_text(project["name"])}</div>',
                        unsafe_allow_html=True,
                    )

                with edit_col:
                    if st.button(
                        "✎",
                        key=f"edit_project_{project['id']}",
                        help="Abrir projeto",
                        use_container_width=True,
                    ):
                        _open_project(project["id"])

                objective = (
                    safe_text(project.get("objective"))
                    or safe_text(project.get("description"))
                    or "Sem objetivo descrito."
                )

                st.markdown(
                    f'<div class="dh-card-desc">{objective}</div>',
                    unsafe_allow_html=True,
                )

                st.markdown(
                    (
                        '<div class="dh-meta">'
                        f'{badge(project["status"])}'
                        f'{badge(project.get("technology") or "Stack não definida")}'
                        f'{badge(f"{project.get("task_count", 0)} tarefas")}'
                        f'{badge(f"{project.get("progress", 0)}% concluído")}'
                        "</div>"
                    ),
                    unsafe_allow_html=True,
                )

                st.markdown(
                    progress_bar_html(project.get("progress", 0)),
                    unsafe_allow_html=True,
                )
