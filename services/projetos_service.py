from datetime import date

from utils.database import get_connection

VALID_PROJECT_STATUS = ["Planejado", "Em andamento", "Pausado", "Concluído"]


def list_projects(status="Todos"):
    params = []
    where = ""
    if status != "Todos":
        where = "WHERE p.status = ?"
        params.append(status)
    query = f"""
        SELECT
            p.*,
            COUNT(t.id) AS task_count,
            SUM(CASE WHEN lower(c.name) IN ('concluído', 'concluido') THEN 1 ELSE 0 END) AS completed_tasks
        FROM projects p
        LEFT JOIN tasks t ON t.project_id = p.id
        LEFT JOIN kanban_columns c ON c.id = t.column_id
        {where}
        GROUP BY p.id
        ORDER BY
            CASE p.status
                WHEN 'Em andamento' THEN 1
                WHEN 'Planejado' THEN 2
                WHEN 'Pausado' THEN 3
                ELSE 4
            END,
            p.updated_at DESC
    """
    with get_connection() as connection:
        rows = connection.execute(query, params).fetchall()
    projects = []
    for row in rows:
        item = dict(row)
        total = item.get("task_count") or 0
        completed = item.get("completed_tasks") or 0
        item["progress"] = round((completed / total) * 100) if total else 0
        projects.append(item)
    return projects



def get_project(project_id):
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT
                p.*,
                COUNT(t.id) AS task_count,
                SUM(CASE WHEN lower(c.name) IN ('concluído', 'concluido') THEN 1 ELSE 0 END) AS completed_tasks
            FROM projects p
            LEFT JOIN tasks t ON t.project_id = p.id
            LEFT JOIN kanban_columns c ON c.id = t.column_id
            WHERE p.id = ?
            GROUP BY p.id
            """,
            (project_id,),
        ).fetchone()
    if not row:
        return None
    item = dict(row)
    total = item.get("task_count") or 0
    completed = item.get("completed_tasks") or 0
    item["progress"] = round((completed / total) * 100) if total else 0
    return item

def add_project(name, description, objective, status, technology, start_date, end_date, repository_url, result):
    clean_name = (name or "").strip()
    if not clean_name:
        raise ValueError("Informe o nome do projeto.")
    if status not in VALID_PROJECT_STATUS:
        raise ValueError("Status inválido.")
    start_value = start_date.isoformat() if isinstance(start_date, date) else None
    end_value = end_date.isoformat() if isinstance(end_date, date) else None
    if start_value and end_value and end_value < start_value:
        raise ValueError("A data final não pode ser anterior à data inicial.")
    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO projects (
                name, description, objective, status, technology, start_date, end_date, repository_url, result
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                clean_name,
                (description or "").strip(),
                (objective or "").strip(),
                status,
                (technology or "").strip(),
                start_value,
                end_value,
                (repository_url or "").strip(),
                (result or "").strip(),
            ),
        )
        return cursor.lastrowid


def update_project(project_id, name, description, objective, status, technology, start_date, end_date, repository_url, result):
    clean_name = (name or "").strip()
    if not clean_name:
        raise ValueError("Informe o nome do projeto.")
    if status not in VALID_PROJECT_STATUS:
        raise ValueError("Status inválido.")
    start_value = start_date.isoformat() if isinstance(start_date, date) else None
    end_value = end_date.isoformat() if isinstance(end_date, date) else None
    if start_value and end_value and end_value < start_value:
        raise ValueError("A data final não pode ser anterior à data inicial.")
    with get_connection() as connection:
        cursor = connection.execute(
            """
            UPDATE projects
            SET name = ?, description = ?, objective = ?, status = ?, technology = ?, start_date = ?,
                end_date = ?, repository_url = ?, result = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (
                clean_name,
                (description or "").strip(),
                (objective or "").strip(),
                status,
                (technology or "").strip(),
                start_value,
                end_value,
                (repository_url or "").strip(),
                (result or "").strip(),
                project_id,
            ),
        )
        return cursor.rowcount > 0


def delete_project(project_id):
    with get_connection() as connection:
        cursor = connection.execute("DELETE FROM projects WHERE id = ?", (project_id,))
        return cursor.rowcount > 0


def project_options():
    with get_connection() as connection:
        rows = connection.execute("SELECT id, name FROM projects ORDER BY name").fetchall()
    return [dict(row) for row in rows]


def get_project_metrics():
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT
                COUNT(*) AS total,
                SUM(CASE WHEN status = 'Em andamento' THEN 1 ELSE 0 END) AS active,
                SUM(CASE WHEN status = 'Concluído' THEN 1 ELSE 0 END) AS completed
            FROM projects
            """
        ).fetchone()
    return {
        "total": row["total"] or 0,
        "active": row["active"] or 0,
        "completed": row["completed"] or 0,
    }
