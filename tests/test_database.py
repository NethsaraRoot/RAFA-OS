
import sqlite3

from app.database.connection import (
    get_connection,
    get_database_path,
    initialize_database,
)


def test_database_is_created():
    initialize_database()

    assert get_database_path().exists()


def test_required_tables_exist():
    initialize_database()

    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
            """
        ).fetchall()

        table_names = {row["name"] for row in rows}

    required_tables = {
        "tasks",
        "reminders",
        "learning_subjects",
        "topics",
        "roadmaps",
        "study_sessions",
        "notes",
        "goals",
        "habits",
        "projects",
        "settings",
    }

    assert required_tables.issubset(table_names)


def test_task_can_be_saved_and_read():
    initialize_database()

    with get_connection() as connection:
        connection.execute(
            "INSERT INTO tasks (title) VALUES (?)",
            ("Database test task",),
        )

        row = connection.execute(
            "SELECT title FROM tasks WHERE title = ?",
            ("Database test task",),
        ).fetchone()

        assert row is not None
        assert row["title"] == "Database test task"

        connection.execute(
            "DELETE FROM tasks WHERE title = ?",
            ("Database test task",),
        )


def test_foreign_keys_are_enabled():
    with get_connection() as connection:
        result = connection.execute(
            "PRAGMA foreign_keys"
        ).fetchone()

        assert result[0] == 1
