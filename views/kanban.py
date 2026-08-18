from datetime import date

import streamlit as st

from services.kanban_service import (
    VALID_CATEGORIES,
    VALID_PRIORITIES,
    add_column,
    add_task,
    delete_column,
    get_columns,
    get_tasks,
    move_task,
    rename_column,
)
from services.projetos_service import project_options
from utils.ui import badge, format_date, hero, safe_text, section_title


def _open_task(task_id):
    st.session_state["detail_view"] = "tarefa"
    st.session_state["detail_id"] = task_id
    st.rerun()


def render():
    hero(
        "Kanban",
        "Organize prioridades, projetos e entregas em um fluxo visual de execução.",
        "EXECUTION BOARD",
    )

    columns = get_columns()
    projects = project_options()
    project_map = {project["id"]: project["name"] for project in projects}

    action_left, action_right = st.columns([2, 1])

    with action_left:
        with st.expander("＋ Nova tarefa", expanded=False):
            if not columns:
                st.info("Crie pelo menos uma coluna antes de adicionar tarefas.")
            else:
                with st.form("new_task", clear_on_submit=True):
                    c1, c2 = st.columns(2)
                    title = c1.text_input("Título")
                    column_id = c2.selectbox(
                        "Status",
                        [column["id"] for column in columns],
                        format_func=lambda value: next(
                            column["name"] for column in columns if column["id"] == value
                        ),
                    )
                    description = st.text_area("Descrição", height=90)
                    c1, c2, c3 = st.columns(3)
                    project_ids = [None] + [project["id"] for project in projects]
                    project_id = c1.selectbox(
                        "Projeto",
                        project_ids,
                        format_func=lambda value: "Sem projeto" if value is None else project_map[value],
                    )
                    category = c2.selectbox("Categoria", VALID_CATEGORIES)
                    priority = c3.selectbox("Prioridade", VALID_PRIORITIES, index=2)
                    c1, c2 = st.columns(2)
                    has_due_date = c1.checkbox("Definir prazo")
                    due_date = c1.date_input(
                        "Prazo",
                        value=date.today(),
                        disabled=not has_due_date,
                    )
                    tags = c2.text_input(
                        "Tags",
                        placeholder="python, automação, portfólio",
                    )

                    if st.form_submit_button("Criar tarefa", use_container_width=True):
                        try:
                            add_task(
                                title,
                                description,
                                column_id,
                                project_id,
                                category,
                                priority,
                                due_date if has_due_date else None,
                                tags,
                            )
                            st.success("Tarefa criada.")
                            st.rerun()
                        except Exception as error:
                            st.error(str(error))

    with action_right:
        with st.expander("⚙ Configurar colunas", expanded=False):
            with st.form("add_column", clear_on_submit=True):
                new_column_name = st.text_input("Nova coluna")
                if st.form_submit_button("Adicionar", use_container_width=True):
                    try:
                        add_column(new_column_name)
                        st.rerun()
                    except Exception as error:
                        st.error(str(error))

            if columns:
                selected_column = st.selectbox(
                    "Coluna existente",
                    [column["id"] for column in columns],
                    format_func=lambda value: next(
                        column["name"] for column in columns if column["id"] == value
                    ),
                    key="selected_column",
                )
                rename_value = st.text_input("Novo nome", key="rename_column")
                c1, c2 = st.columns(2)

                if c1.button("Renomear", use_container_width=True):
                    try:
                        rename_column(selected_column, rename_value)
                        st.rerun()
                    except Exception as error:
                        st.error(str(error))

                confirm_delete_column = st.checkbox(
                    "Confirmar exclusão",
                    key="confirm_column",
                )

                if c2.button(
                    "Excluir",
                    use_container_width=True,
                    disabled=not confirm_delete_column,
                ):
                    try:
                        delete_column(selected_column)
                        st.rerun()
                    except Exception as error:
                        st.error(str(error))

    section_title("Quadro de execução")

    f1, f2, f3, f4 = st.columns([2.2, 1, 1, 1.3])
    search = f1.text_input(
        "Buscar",
        placeholder="Título, descrição ou tag",
        label_visibility="collapsed",
    )
    filter_category = f2.selectbox(
        "Categoria",
        ["Todas"] + VALID_CATEGORIES,
        label_visibility="collapsed",
    )
    filter_priority = f3.selectbox(
        "Prioridade",
        ["Todas"] + VALID_PRIORITIES,
        label_visibility="collapsed",
    )
    project_filter_options = [None] + [project["id"] for project in projects]
    filter_project = f4.selectbox(
        "Projeto",
        project_filter_options,
        format_func=lambda value: "Todos os projetos" if value is None else project_map[value],
        label_visibility="collapsed",
    )

    tasks = get_tasks(search, filter_category, filter_priority, filter_project)
    tasks_by_column = {column["id"]: [] for column in columns}

    for task in tasks:
        if task["column_id"] in tasks_by_column:
            tasks_by_column[task["column_id"]].append(task)

    if not columns:
        st.markdown(
            '<div class="dh-empty">Nenhuma coluna configurada.</div>',
            unsafe_allow_html=True,
        )
        return

    board_columns = st.columns(len(columns))

    for column_index, column in enumerate(columns):
        items = tasks_by_column[column["id"]]

        with board_columns[column_index]:
            st.markdown(
                (
                    '<div class="dh-column-head">'
                    f'<div class="dh-column-title">{safe_text(column["name"])}</div>'
                    f'<div class="dh-count">{len(items)}</div>'
                    "</div>"
                ),
                unsafe_allow_html=True,
            )

            if not items:
                st.markdown(
                    '<div class="dh-empty">Sem tarefas</div>',
                    unsafe_allow_html=True,
                )

            for task in items:
                with st.container(border=True):
                    title_col, edit_col = st.columns([8, 1])

                    with title_col:
                        st.markdown(
                            f'<div class="dh-card-title">{safe_text(task["title"])}</div>',
                            unsafe_allow_html=True,
                        )

                    with edit_col:
                        if st.button(
                            "✎",
                            key=f"edit_task_{task['id']}",
                            help="Abrir tarefa",
                            use_container_width=True,
                        ):
                            _open_task(task["id"])

                    if task.get("description"):
                        st.markdown(
                            f'<div class="dh-card-desc">{safe_text(task["description"])}</div>',
                            unsafe_allow_html=True,
                        )

                    badges = [
                        badge(task["priority"]),
                        badge(task["category"]),
                    ]

                    if task.get("project_name"):
                        badges.append(badge(task["project_name"]))

                    badges.append(badge(format_date(task.get("due_date"))))

                    for tag in (task.get("tags") or "").split(","):
                        clean_tag = tag.strip()
                        if clean_tag:
                            badges.append(badge(clean_tag))

                    st.markdown(
                        f'<div class="dh-meta">{"".join(badges)}</div>',
                        unsafe_allow_html=True,
                    )

                    destination_ids = [item["id"] for item in columns]
                    destination = st.selectbox(
                        "Mover",
                        destination_ids,
                        index=destination_ids.index(task["column_id"]),
                        key=f"move_dest_{task['id']}",
                        format_func=lambda value: next(
                            item["name"] for item in columns if item["id"] == value
                        ),
                        label_visibility="collapsed",
                    )

                    if st.button(
                        "Mover",
                        key=f"move_{task['id']}",
                        use_container_width=True,
                    ):
                        try:
                            move_task(task["id"], destination)
                            st.rerun()
                        except Exception as error:
                            st.error(str(error))
