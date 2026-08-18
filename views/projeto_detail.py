from datetime import date

import streamlit as st

from services.projetos_service import (
    VALID_PROJECT_STATUS,
    delete_project,
    get_project,
    update_project,
)
from utils.ui import badge, format_date, progress_bar_html, safe_text


def _back():
    st.session_state.pop("detail_view", None)
    st.session_state.pop("detail_id", None)
    st.rerun()


def render(project_id):
    project = get_project(project_id)

    if not project:
        st.error("Projeto não encontrado.")
        if st.button("← Voltar para Projetos"):
            _back()
        return

    if st.button("← Voltar para Projetos"):
        _back()

    st.markdown(
        (
            '<div class="dh-detail-shell">'
            '<div class="dh-detail-kicker">PROJETO</div>'
            f'<div class="dh-detail-title">{safe_text(project["name"])}</div>'
            '<div class="dh-meta">'
            f'{badge(project["status"])}'
            f'{badge(project.get("technology") or "Stack não definida")}'
            f'{badge(f"{project.get("progress", 0)}% concluído")}'
            f'{badge(f"{project.get("task_count", 0)} tarefas")}'
            "</div>"
            f'{progress_bar_html(project.get("progress", 0))}'
            "</div>"
        ),
        unsafe_allow_html=True,
    )

    with st.container(border=True):
        st.subheader("Detalhes do projeto")

        with st.form(f"project_detail_{project_id}"):
            c1, c2 = st.columns(2)
            name = c1.text_input("Nome", value=project.get("name", ""))
            status = c2.selectbox(
                "Status",
                VALID_PROJECT_STATUS,
                index=VALID_PROJECT_STATUS.index(project["status"]),
            )

            description = st.text_area(
                "Descrição",
                value=project.get("description", ""),
                height=120,
            )
            objective = st.text_area(
                "Objetivo",
                value=project.get("objective", ""),
                height=120,
            )

            c1, c2 = st.columns(2)
            technology = c1.text_input(
                "Tecnologias",
                value=project.get("technology", ""),
            )
            repository_url = c2.text_input(
                "Repositório",
                value=project.get("repository_url", ""),
            )

            c1, c2 = st.columns(2)
            start_date = c1.date_input(
                "Data inicial",
                value=(
                    date.fromisoformat(project["start_date"])
                    if project.get("start_date")
                    else date.today()
                ),
            )
            has_end = c2.checkbox(
                "Definir data final",
                value=bool(project.get("end_date")),
            )
            end_date = c2.date_input(
                "Data final",
                value=(
                    date.fromisoformat(project["end_date"])
                    if project.get("end_date")
                    else date.today()
                ),
                disabled=not has_end,
            )

            result = st.text_area(
                "Resultado / impacto",
                value=project.get("result", ""),
                height=120,
            )

            if st.form_submit_button(
                "Salvar alterações",
                use_container_width=True,
            ):
                try:
                    updated = update_project(
                        project_id,
                        name,
                        description,
                        objective,
                        status,
                        technology,
                        start_date,
                        end_date if has_end else None,
                        repository_url,
                        result,
                    )
                    if updated:
                        st.success("Projeto atualizado com sucesso.")
                    else:
                        st.error("Não foi possível localizar o projeto.")
                except Exception as error:
                    st.error(str(error))

    with st.expander("Zona de exclusão", expanded=False):
        st.warning("As tarefas vinculadas ao projeto serão mantidas sem vínculo com ele.")
        confirm = st.checkbox(
            "Confirmo que desejo excluir este projeto",
            key=f"delete_project_confirm_{project_id}",
        )
        if st.button(
            "Excluir projeto",
            disabled=not confirm,
            type="secondary",
            use_container_width=True,
        ):
            try:
                if delete_project(project_id):
                    _back()
                else:
                    st.error("Não foi possível localizar o projeto.")
            except Exception as error:
                st.error(str(error))
