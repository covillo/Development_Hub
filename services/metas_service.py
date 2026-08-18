from datetime import date

from utils.database import get_connection

VALID_CATEGORIES = ["70", "20", "10"]
VALID_STATUS = ["Planejada", "Em andamento", "Concluída"]


def list_goals(category="Todas", status="Todos"):
    clauses = []
    params = []
    if category != "Todas":
        clauses.append("category = ?")
        params.append(category)
    if status != "Todos":
        clauses.append("status = ?")
        params.append(status)
    where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
    with get_connection() as connection:
        rows = connection.execute(
            f"SELECT * FROM goals {where} ORDER BY end_date, start_date, title",
            params,
        ).fetchall()
    return [dict(row) for row in rows]



def get_goal(goal_id):
    with get_connection() as connection:
        row = connection.execute(
            "SELECT * FROM goals WHERE id = ?",
            (goal_id,),
        ).fetchone()
    return dict(row) if row else None

def add_goal(title, description, category, start_date, end_date, status, progress, strategic_objective, evidence, competency, result):
    clean_title = (title or "").strip()
    if not clean_title:
        raise ValueError("Informe o título da meta.")
    if category not in VALID_CATEGORIES:
        raise ValueError("Categoria inválida.")
    if status not in VALID_STATUS:
        raise ValueError("Status inválido.")
    if not isinstance(start_date, date) or not isinstance(end_date, date):
        raise ValueError("Datas inválidas.")
    if end_date < start_date:
        raise ValueError("A data final não pode ser anterior à data inicial.")
    progress_value = max(0, min(100, int(progress or 0)))
    if status == "Concluída":
        progress_value = 100
    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO goals (
                title, description, category, status, progress, start_date, end_date,
                strategic_objective, evidence, competency, result
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                clean_title,
                (description or "").strip(),
                category,
                status,
                progress_value,
                start_date.isoformat(),
                end_date.isoformat(),
                (strategic_objective or "").strip(),
                (evidence or "").strip(),
                (competency or "").strip(),
                (result or "").strip(),
            ),
        )
        return cursor.lastrowid


def update_goal(goal_id, title, description, category, start_date, end_date, status, progress, strategic_objective, evidence, competency, result):
    clean_title = (title or "").strip()
    if not clean_title:
        raise ValueError("Informe o título da meta.")
    if category not in VALID_CATEGORIES:
        raise ValueError("Categoria inválida.")
    if status not in VALID_STATUS:
        raise ValueError("Status inválido.")
    if end_date < start_date:
        raise ValueError("A data final não pode ser anterior à data inicial.")
    progress_value = max(0, min(100, int(progress or 0)))
    if status == "Concluída":
        progress_value = 100
    with get_connection() as connection:
        cursor = connection.execute(
            """
            UPDATE goals
            SET title = ?, description = ?, category = ?, status = ?, progress = ?, start_date = ?, end_date = ?,
                strategic_objective = ?, evidence = ?, competency = ?, result = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (
                clean_title,
                (description or "").strip(),
                category,
                status,
                progress_value,
                start_date.isoformat(),
                end_date.isoformat(),
                (strategic_objective or "").strip(),
                (evidence or "").strip(),
                (competency or "").strip(),
                (result or "").strip(),
                goal_id,
            ),
        )
        return cursor.rowcount > 0


def delete_goal(goal_id):
    with get_connection() as connection:
        cursor = connection.execute("DELETE FROM goals WHERE id = ?", (goal_id,))
        return cursor.rowcount > 0


def summarize_by_category():
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT category, COUNT(*) AS count, COALESCE(AVG(progress), 0) AS avg_progress
            FROM goals
            GROUP BY category
            """
        ).fetchall()
    summary = {"70": {"count": 0, "avg_progress": 0}, "20": {"count": 0, "avg_progress": 0}, "10": {"count": 0, "avg_progress": 0}}
    for row in rows:
        if row["category"] in summary:
            summary[row["category"]] = {
                "count": row["count"],
                "avg_progress": round(row["avg_progress"]),
            }
    return summary


def get_goal_metrics():
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT
                COUNT(*) AS total,
                COALESCE(AVG(progress), 0) AS avg_progress,
                SUM(CASE WHEN status = 'Concluída' THEN 1 ELSE 0 END) AS completed
            FROM goals
            """
        ).fetchone()
    return {
        "total": row["total"] or 0,
        "avg_progress": round(row["avg_progress"] or 0),
        "completed": row["completed"] or 0,
    }
