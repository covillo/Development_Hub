import pandas as pd
import streamlit as st

from services.analytics_service import (
    goals_by_category,
    monthly_completions,
    tasks_by_category,
    tasks_by_column,
    tasks_by_priority,
)
from services.kanban_service import get_task_metrics, get_tasks
from services.metas_service import get_goal_metrics
from services.projetos_service import get_project_metrics, list_projects
from utils.ui import badge, format_date, hero, safe_text, section_title


def render():
    hero(
        "Dashboard",
        "Visão integrada de produtividade, projetos e desenvolvimento profissional.",
        "PERFORMANCE & GROWTH",
    )

    task_metrics = get_task_metrics()
    project_metrics = get_project_metrics()
    goal_metrics = get_goal_metrics()

    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Tarefas", task_metrics["total"])
    m2.metric("Em andamento", task_metrics["in_progress"])
    m3.metric("Projetos ativos", project_metrics["active"])
    m4.metric("Metas PDI", goal_metrics["total"])
    m5.metric("Progresso PDI", f'{goal_metrics["avg_progress"]}%')

    section_title("Performance")
    p1, p2, p3, p4 = st.columns(4)
    p1.metric("Tarefas concluídas", task_metrics["completed"])
    p2.metric("Tarefas atrasadas", task_metrics["overdue"])
    p3.metric("Projetos concluídos", project_metrics["completed"])
    p4.metric("Metas concluídas", goal_metrics["completed"])

    left, right = st.columns(2)

    with left:
        section_title("Tarefas por status")
        data = pd.DataFrame(tasks_by_column())
        if data.empty or data["total"].sum() == 0:
            st.markdown(
                '<div class="dh-empty">Ainda não há tarefas para analisar.</div>',
                unsafe_allow_html=True,
            )
        else:
            st.bar_chart(data.set_index("status")[["total"]], horizontal=True)

    with right:
        section_title("Tarefas por prioridade")
        data = pd.DataFrame(tasks_by_priority())
        if data.empty:
            st.markdown(
                '<div class="dh-empty">Ainda não há dados de prioridade.</div>',
                unsafe_allow_html=True,
            )
        else:
            st.bar_chart(data.set_index("priority")[["total"]], horizontal=True)

    left, right = st.columns(2)

    with left:
        section_title("Tarefas por categoria")
        data = pd.DataFrame(tasks_by_category())
        if data.empty:
            st.markdown(
                '<div class="dh-empty">Ainda não há dados de categoria.</div>',
                unsafe_allow_html=True,
            )
        else:
            st.bar_chart(data.set_index("category")[["total"]], horizontal=True)

    with right:
        section_title("PDI 70/20/10")
        data = pd.DataFrame(goals_by_category())
        if data.empty:
            st.markdown(
                '<div class="dh-empty">Cadastre metas para visualizar a distribuição do PDI.</div>',
                unsafe_allow_html=True,
            )
        else:
            st.bar_chart(data.set_index("category")[["avg_progress"]], horizontal=True)

    section_title("Evolução de entregas")
    data = pd.DataFrame(monthly_completions())
    if data.empty:
        st.markdown(
            '<div class="dh-empty">As entregas concluídas aparecerão aqui ao longo do tempo.</div>',
            unsafe_allow_html=True,
        )
    else:
        st.line_chart(data.set_index("month")[["total"]])

    section_title("Foco atual")
    focus_tasks = [
        task
        for task in get_tasks()
        if str(task.get("column_name", "")).lower() not in {"concluído", "concluido"}
    ][:6]

    if not focus_tasks:
        st.markdown(
            '<div class="dh-empty">Nenhuma tarefa em aberto. Use o Kanban para criar seu próximo foco.</div>',
            unsafe_allow_html=True,
        )
    else:
        cols = st.columns(3)
        for index, task in enumerate(focus_tasks):
            with cols[index % 3]:
                project = badge(task["project_name"]) if task.get("project_name") else ""
                st.markdown(
                    f"""
                    <div class="dh-card">
                        <div class="dh-card-title">{safe_text(task["title"])}</div>
                        <div class="dh-card-desc">{safe_text(task["description"]) or "Sem descrição."}</div>
                        <div class="dh-meta">
                            {badge(task.get("priority") or "Sem prioridade")}
                            {badge(task.get("category") or "Sem categoria")}
                            {project}
                            {badge(format_date(task.get("due_date")))}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    section_title("Projetos em evolução")
    projects = [
        project
        for project in list_projects()
        if str(project.get("status", "")).lower() not in {"concluído", "concluido"}
    ][:4]

    if not projects:
        st.markdown(
            '<div class="dh-empty">Nenhum projeto ativo. Registre seu primeiro projeto na área Projetos.</div>',
            unsafe_allow_html=True,
        )
    else:
        cols = st.columns(2)
        for index, project in enumerate(projects):
            with cols[index % 2]:
                st.markdown(
                    f"""
                    <div class="dh-card dh-project">
                        <div class="dh-card-title">{safe_text(project["name"])}</div>
                        <div class="dh-card-desc">
                            {safe_text(project.get("objective")) or safe_text(project.get("description")) or "Projeto sem objetivo descrito."}
                        </div>
                        <div class="dh-meta">
                            {badge(project.get("status") or "Sem status")}
                            {badge(project.get("technology") or "Stack não definida")}
                            {badge(f'{project.get("progress", 0)}% concluído')}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
