import sqlite3
from contextlib import contextmanager
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
DB_PATH = ROOT_DIR / "data" / "app.db"


@contextmanager
def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def init_database():
    with get_connection() as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS kanban_columns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE COLLATE NOCASE,
                position INTEGER NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT NOT NULL DEFAULT '',
                objective TEXT NOT NULL DEFAULT '',
                status TEXT NOT NULL DEFAULT 'Planejado',
                technology TEXT NOT NULL DEFAULT '',
                start_date TEXT,
                end_date TEXT,
                repository_url TEXT NOT NULL DEFAULT '',
                result TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT NOT NULL DEFAULT '',
                column_id INTEGER NOT NULL,
                project_id INTEGER,
                category TEXT NOT NULL DEFAULT 'Projeto',
                priority TEXT NOT NULL DEFAULT 'Média',
                due_date TEXT,
                tags TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (column_id) REFERENCES kanban_columns(id) ON DELETE RESTRICT,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE SET NULL
            );

            CREATE TABLE IF NOT EXISTS goals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT NOT NULL DEFAULT '',
                category TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Planejada',
                progress INTEGER NOT NULL DEFAULT 0,
                start_date TEXT NOT NULL,
                end_date TEXT NOT NULL,
                strategic_objective TEXT NOT NULL DEFAULT '',
                evidence TEXT NOT NULL DEFAULT '',
                competency TEXT NOT NULL DEFAULT '',
                result TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE INDEX IF NOT EXISTS idx_tasks_column ON tasks(column_id);
            CREATE INDEX IF NOT EXISTS idx_tasks_project ON tasks(project_id);
            CREATE INDEX IF NOT EXISTS idx_tasks_priority ON tasks(priority);
            CREATE INDEX IF NOT EXISTS idx_goals_category ON goals(category);
            """
        )

        count = connection.execute("SELECT COUNT(*) AS total FROM kanban_columns").fetchone()["total"]
        if count == 0:
            connection.executemany(
                "INSERT INTO kanban_columns (name, position) VALUES (?, ?)",
                [
                    ("Backlog", 1),
                    ("Planejado", 2),
                    ("Em andamento", 3),
                    ("Concluído", 4),
                ],
            )
