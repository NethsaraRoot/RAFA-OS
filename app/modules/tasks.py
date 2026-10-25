
from datetime import datetime

from app.database.connection import get_connection


VALID_PRIORITIES = {"Low", "Medium", "High", "Urgent"}
VALID_STATUSES = {"Not Started", "In Progress", "Completed"}


def create_task(
    title: str,
    description: str = "",
    category: str = "General",
    priority: str = "Medium",
    due_at: str | None = None,
    estimated_minutes: int | None = None,
) -> int:
    """Create a task and return its database ID."""

    title = title.strip()

    if not title:
        raise ValueError("Task title cannot be empty.")

    if priority not in VALID_PRIORITIES:
        raise ValueError("Invalid task priority.")

    if estimated_minutes is not None and estimated_minutes < 0:
        raise ValueError("Estimated minutes cannot be negative.")

    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO tasks (
                title,
                description,
                category,
                priority,
                due_at,
                estimated_minutes
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                title,
                description.strip(),
                category.strip() or "General",
                priority,
                due_at,
                estimated_minutes,
            ),
        )

        return cursor.lastrowid


def get_tasks(
    search: str = "",
    status: str = "All",
    priority: str = "All",
) -> list[dict]:
    """Return tasks filtered by search text, status, and priority."""

    query = """
        SELECT *
        FROM tasks
        WHERE (
            title LIKE ?
            OR description LIKE ?
            OR category LIKE ?
        )
    """
    pattern = f"%{search.strip()}%"
    params: list = [pattern, pattern, pattern]

    if status != "All":
        if status not in VALID_STATUSES:
            raise ValueError("Invalid task status.")
        query += " AND status = ?"
        params.append(status)

    if priority != "All":
        if priority not in VALID_PRIORITIES:
            raise ValueError("Invalid task priority.")
        query += " AND priority = ?"
        params.append(priority)

    query += """
        ORDER BY
            CASE status
                WHEN 'In Progress' THEN 1
                WHEN 'Not Started' THEN 2
                ELSE 3
            END,
            CASE priority
                WHEN 'Urgent' THEN 1
                WHEN 'High' THEN 2
                WHEN 'Medium' THEN 3
                ELSE 4
            END,
            due_at IS NULL,
            due_at ASC,
            id DESC
    """

    with get_connection() as connection:
        rows = connection.execute(query, params).fetchall()
        return [dict(row) for row in rows]


def get_task(task_id: int) -> dict | None:
    """Return a single task, or None if it does not exist."""

    with get_connection() as connection:
        row = connection.execute(
            "SELECT * FROM tasks WHERE id = ?",
            (task_id,),
        ).fetchone()

        return dict(row) if row else None


def update_task(
    task_id: int,
    title: str,
    description: str,
    category: str,
    priority: str,
    due_at: str | None,
    estimated_minutes: int | None,
) -> None:
    """Update an existing task without changing its status."""

    title = title.strip()

    if not title:
        raise ValueError("Task title cannot be empty.")

    if priority not in VALID_PRIORITIES:
        raise ValueError("Invalid task priority.")

    if estimated_minutes is not None and estimated_minutes < 0:
        raise ValueError("Estimated minutes cannot be negative.")

    with get_connection() as connection:
        cursor = connection.execute(
            """
            UPDATE tasks
            SET title = ?,
                description = ?,
                category = ?,
                priority = ?,
                due_at = ?,
                estimated_minutes = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (
                title,
                description.strip(),
                category.strip() or "General",
                priority,
                due_at,
                estimated_minutes,
                task_id,
            ),
        )

        if cursor.rowcount == 0:
            raise ValueError("Task not found.")


def set_task_status(task_id: int, status: str) -> None:
    """Change task status and maintain the completion timestamp."""

    if status not in VALID_STATUSES:
        raise ValueError("Invalid task status.")

    with get_connection() as connection:
        cursor = connection.execute(
            """
            UPDATE tasks
            SET status = ?,
                completed_at = CASE
                    WHEN ? = 'Completed'
                        THEN COALESCE(completed_at, CURRENT_TIMESTAMP)
                    ELSE NULL
                END,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (status, status, task_id),
        )

        if cursor.rowcount == 0:
            raise ValueError("Task not found.")


def delete_task(task_id: int) -> None:
    """Delete a task."""

    with get_connection() as connection:
        cursor = connection.execute(
            "DELETE FROM tasks WHERE id = ?",
            (task_id,),
        )

        if cursor.rowcount == 0:
            raise ValueError("Task not found.")


def get_task_statistics() -> dict:
    """Return task counts for the dashboard."""

    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT
                COUNT(*) AS total,
                COALESCE(SUM(status = 'Completed'), 0) AS completed,
                COALESCE(SUM(status = 'Not Started'), 0) AS pending,
                COALESCE(SUM(status = 'In Progress'), 0) AS in_progress,
                COALESCE(
                    SUM(
                        status != 'Completed'
                        AND due_at IS NOT NULL
                        AND due_at < ?
                    ),
                    0
                ) AS overdue
            FROM tasks
            """,
            (datetime.now().strftime("%Y-%m-%d %H:%M:%S"),),
        ).fetchone()

        return dict(row)
