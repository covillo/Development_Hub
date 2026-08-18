from datetime import date

import streamlit as st

from services.kanban_service import (
    VALID_CATEGORIES,
    VALID_PRIORITIES,
    delete_task,
    get_columns,
    get_task,
    update_task,
)
from services.projetos_service import project_options
from utils.ui import badge, format_date, safe_text


def _back():
    st.session_state.pop("detail_view", None)
    st.session_state.pop("detail_id", None)
    st.rerun()


def render(task_id):
    task = get_task(task_id)

    if not task:
        st.error("Tarefa não encontrada.")
        if st.button("← Voltar para o Kanban"):
            _back()
        return

    top_left, top_right = st.columns([5, 1])

    with top_left:
        if st.button("← Voltar para o Kanban", use_container_width=False):
            _back()

    with top_right:
        st.markdown(
            f'<div class="dh-meta" style="justify-content:flex-end;">{badge(task["priority"])}</div>',
            unsafe_allow_html=True,
        )

    st.markdown(
        (
            '<div class="dh-detail-shell">'
            '<div class="dh-detail-kicker">TAREFA</div>'
            f'<div class="dh-detail-title">{safe_text(task["title"])}</div>'
            f'<div class="dh-detail-subtitle">Criada em {format_date(task.get("created_at"))} · Última atualização {format_date(task.get("updated_at"))}</div>'
            "</div>"
        ),
        unsafe_allow_html=True,
    )

    columns = get_columns()
    projects = project_options()
    project_map = {project["id"]: project["name"] for project in projects}

    with st.container(border=True):
        st.subheader("Detalhes da tarefa")

        with st.form(f"task_detail_{task_id}"):
            title = st.text_input("Título", value=task.get("title", ""))
            description = st.text_area(
                "Descrição",
                value=task.get("description", ""),
                height=150,
            )

            c1, c2 = st.columns(2)
            column_ids = [item["id"] for item in columns]
            column_id = c1.selectbox(
                "Status",
                column_ids,
                index=column_ids.index(task["column_id"]),
                format_func=lambda value: next(
                    item["name"] for item in columns if item["id"] == value
                ),
            )

            project_ids = [None] + [project["id"] for project in projects]
            project_index = (
                project_ids.index(task.get("project_id"))
                if task.get("project_id") in project_ids
                else 0
            )
            project_id = c2.selectbox(
                "Projeto",
                project_ids,
                index=project_index,
                format_func=lambda value: "Sem projeto" if value is None else project_map[value],
            )

            c1, c2 = st.columns(2)
            category = c1.selectbox(
                "Categoria",
                VALID_CATEGORIES,
                index=VALID_CATEGORIES.index(task["category"]),
            )
            priority = c2.selectbox(
                "Prioridade",
                VALID_PRIORITIES,
                index=VALID_PRIORITIES.index(task["priority"]),
            )

            c1, c2 = st.columns(2)
            has_due = c1.checkbox(
                "Definir prazo",
                value=bool(task.get("due_date")),
            )
            due_date = c1.date_input(
                "Prazo",
                value=(
                    date.fromisoformat(task["due_date"])
                    if task.get("due_date")
                    else date.today()
                ),
                disabled=not has_due,
            )
            tags = c2.text_input(
                "Tags",
                value=task.get("tags", ""),
                placeholder="python, automação, portfólio",
            )

            save = st.form_submit_button(
                "Salvar alterações",
                use_container_width=True,
            )

            if save:
                try:
                    updated = update_task(
                        task_id,
                        title,
                        description,
                        column_id,
                        project_id,
                        category,
                        priority,
                        due_date if has_due else None,
                        tags,
                    )
                    if updated:
                        st.success("Tarefa atualizada com sucesso.")
                    else:
                        st.error("Não foi possível localizar a tarefa.")
                except Exception as error:
                    st.error(str(error))

    with st.expander("Zona de exclusão", expanded=False):
        st.warning("A exclusão da tarefa é permanente.")
        confirm = st.checkbox(
            "Confirmo que desejo excluir esta tarefa",
            key=f"delete_task_confirm_{task_id}",
        )
        if st.button(
            "Excluir tarefa",
            disabled=not confirm,
            type="secondary",
            use_container_width=True,
        ):
            if delete_task(task_id):
                _back()
            else:
                st.error("Não foi possível localizar a tarefa.")
