from datetime import date

from utils.database import get_connection

VALID_PRIORITIES = ["Crítica", "Alta", "Média", "Baixa"]
VALID_CATEGORIES = ["Projeto", "Processo", "Python", "Automação", "Estudo", "PDI", "Pessoal"]


def _row_to_dict(row):
    return dict(row) if row else None


def get_columns():
    with get_connection() as connection:
        rows = connection.execute(
            "SELECT id, name, position FROM kanban_columns ORDER BY position, name"
        ).fetchall()
    return [dict(row) for row in rows]


def add_column(name):
    clean_name = (name or "").strip()
    if not clean_name:
        raise ValueError("Informe o nome da coluna.")
    with get_connection() as connection:
        exists = connection.execute(
            "SELECT 1 FROM kanban_columns WHERE lower(name) = lower(?)",
            (clean_name,),
        ).fetchone()
        if exists:
            raise ValueError("Já existe uma coluna com esse nome.")
        next_position = connection.execute(
            "SELECT COALESCE(MAX(position), 0) + 1 AS value FROM kanban_columns"
        ).fetchone()["value"]
        cursor = connection.execute(
            "INSERT INTO kanban_columns (name, position) VALUES (?, ?)",
            (clean_name, next_position),
        )
        return cursor.lastrowid


def rename_column(column_id, new_name):
    clean_name = (new_name or "").strip()
    if not clean_name:
        raise ValueError("Informe o novo nome da coluna.")
    with get_connection() as connection:
        duplicate = connection.execute(
            "SELECT 1 FROM kanban_columns WHERE lower(name) = lower(?) AND id <> ?",
            (clean_name, column_id),
        ).fetchone()
        if duplicate:
            raise ValueError("Já existe outra coluna com esse nome.")
        cursor = connection.execute(
            "UPDATE kanban_columns SET name = ? WHERE id = ?",
            (clean_name, column_id),
        )
        return cursor.rowcount > 0


def delete_column(column_id):
    with get_connection() as connection:
        total_columns = connection.execute("SELECT COUNT(*) AS total FROM kanban_columns").fetchone()["total"]
        if total_columns <= 1:
            raise ValueError("O Kanban precisa manter pelo menos uma coluna.")
        task_count = connection.execute(
            "SELECT COUNT(*) AS total FROM tasks WHERE column_id = ?",
            (column_id,),
        ).fetchone()["total"]
        if task_count:
            raise ValueError("Mova as tarefas desta coluna antes de excluí-la.")
        cursor = connection.execute("DELETE FROM kanban_columns WHERE id = ?", (column_id,))
        return cursor.rowcount > 0


def get_tasks(search="", category="Todas", priority="Todas", project_id=None):
    clauses = []
    params = []
    if search.strip():
        clauses.append("(lower(t.title) LIKE lower(?) OR lower(t.description) LIKE lower(?) OR lower(t.tags) LIKE lower(?))")
        term = f"%{search.strip()}%"
        params.extend([term, term, term])
    if category != "Todas":
        clauses.append("t.category = ?")
        params.append(category)
    if priority != "Todas":
        clauses.append("t.priority = ?")
        params.append(priority)
    if project_id:
        clauses.append("t.project_id = ?")
        params.append(project_id)
    where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
    query = f"""
        SELECT
            t.id,
            t.title,
            t.description,
            t.column_id,
            t.project_id,
            t.category,
            t.priority,
            t.due_date,
            t.tags,
            t.created_at,
            t.updated_at,
            p.name AS project_name,
            c.name AS column_name
        FROM tasks t
        JOIN kanban_columns c ON c.id = t.column_id
        LEFT JOIN projects p ON p.id = t.project_id
        {where}
        ORDER BY
            CASE t.priority
                WHEN 'Crítica' THEN 1
                WHEN 'Alta' THEN 2
                WHEN 'Média' THEN 3
                ELSE 4
            END,
            CASE WHEN t.due_date IS NULL OR t.due_date = '' THEN 1 ELSE 0 END,
            t.due_date,
            t.created_at DESC
    """
    with get_connection() as connection:
        rows = connection.execute(query, params).fetchall()
    return [dict(row) for row in rows]


def get_task(task_id):
    with get_connection() as connection:
        row = connection.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    return _row_to_dict(row)


def add_task(title, description, column_id, project_id, category, priority, due_date, tags):
    clean_title = (title or "").strip()
    if not clean_title:
        raise ValueError("Informe o título da tarefa.")
    if category not in VALID_CATEGORIES:
        raise ValueError("Categoria inválida.")
    if priority not in VALID_PRIORITIES:
        raise ValueError("Prioridade inválida.")
    due_value = due_date.isoformat() if isinstance(due_date, date) else None
    with get_connection() as connection:
        valid_column = connection.execute("SELECT 1 FROM kanban_columns WHERE id = ?", (column_id,)).fetchone()
        if not valid_column:
            raise ValueError("Coluna inválida.")
        if project_id:
            valid_project = connection.execute("SELECT 1 FROM projects WHERE id = ?", (project_id,)).fetchone()
            if not valid_project:
                raise ValueError("Projeto inválido.")
        cursor = connection.execute(
            """
            INSERT INTO tasks (
                title, description, column_id, project_id, category, priority, due_date, tags
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                clean_title,
                (description or "").strip(),
                column_id,
                project_id,
                category,
                priority,
                due_value,
                (tags or "").strip(),
            ),
        )
        return cursor.lastrowid


def update_task(task_id, title, description, column_id, project_id, category, priority, due_date, tags):
    clean_title = (title or "").strip()
    if not clean_title:
        raise ValueError("Informe o título da tarefa.")
    if category not in VALID_CATEGORIES:
        raise ValueError("Categoria inválida.")
    if priority not in VALID_PRIORITIES:
        raise ValueError("Prioridade inválida.")
    due_value = due_date.isoformat() if isinstance(due_date, date) else None
    with get_connection() as connection:
        cursor = connection.execute(
            """
            UPDATE tasks
            SET title = ?, description = ?, column_id = ?, project_id = ?, category = ?, priority = ?,
                due_date = ?, tags = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (
                clean_title,
                (description or "").strip(),
                column_id,
                project_id,
                category,
                priority,
                due_value,
                (tags or "").strip(),
                task_id,
            ),
        )
        return cursor.rowcount > 0


def move_task(task_id, to_column_id):
    with get_connection() as connection:
        cursor = connection.execute(
            "UPDATE tasks SET column_id = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (to_column_id, task_id),
        )
        return cursor.rowcount > 0


def delete_task(task_id):
    with get_connection() as connection:
        cursor = connection.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        return cursor.rowcount > 0


def get_task_metrics():
    today = date.today().isoformat()
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT
                COUNT(*) AS total,
                SUM(CASE WHEN lower(c.name) = 'concluído' OR lower(c.name) = 'concluido' THEN 1 ELSE 0 END) AS completed,
                SUM(CASE WHEN lower(c.name) = 'em andamento' THEN 1 ELSE 0 END) AS in_progress,
                SUM(CASE WHEN t.due_date IS NOT NULL AND t.due_date < ? AND lower(c.name) NOT IN ('concluído', 'concluido') THEN 1 ELSE 0 END) AS overdue
            FROM tasks t
            JOIN kanban_columns c ON c.id = t.column_id
            """,
            (today,),
        ).fetchone()
    return {
        "total": row["total"] or 0,
        "completed": row["completed"] or 0,
        "in_progress": row["in_progress"] or 0,
        "overdue": row["overdue"] or 0,
    }
