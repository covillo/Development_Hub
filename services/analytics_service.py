from utils.database import get_connection


def tasks_by_category():
    with get_connection() as connection:
        rows = connection.execute(
            "SELECT category, COUNT(*) AS total FROM tasks GROUP BY category ORDER BY total DESC"
        ).fetchall()
    return [dict(row) for row in rows]


def tasks_by_priority():
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT priority, COUNT(*) AS total
            FROM tasks
            GROUP BY priority
            ORDER BY CASE priority WHEN 'Crítica' THEN 1 WHEN 'Alta' THEN 2 WHEN 'Média' THEN 3 ELSE 4 END
            """
        ).fetchall()
    return [dict(row) for row in rows]


def tasks_by_column():
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT c.name AS status, COUNT(t.id) AS total
            FROM kanban_columns c
            LEFT JOIN tasks t ON t.column_id = c.id
            GROUP BY c.id, c.name, c.position
            ORDER BY c.position
            """
        ).fetchall()
    return [dict(row) for row in rows]


def goals_by_category():
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT category, COUNT(*) AS total, ROUND(COALESCE(AVG(progress), 0), 0) AS avg_progress
            FROM goals
            GROUP BY category
            ORDER BY CASE category WHEN '70' THEN 1 WHEN '20' THEN 2 ELSE 3 END
            """
        ).fetchall()
    return [dict(row) for row in rows]


def monthly_completions():
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT substr(t.updated_at, 1, 7) AS month, COUNT(*) AS total
            FROM tasks t
            JOIN kanban_columns c ON c.id = t.column_id
            WHERE lower(c.name) IN ('concluído', 'concluido')
            GROUP BY substr(t.updated_at, 1, 7)
            ORDER BY month
            """
        ).fetchall()
    return [dict(row) for row in rows]
