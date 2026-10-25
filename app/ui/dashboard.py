
from datetime import date

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
    QGridLayout,
    QListWidget,
    QListWidgetItem,
)

from app.database.connection import get_connection


class StatCard(QFrame):
    def __init__(self, title: str, value: str = "0"):
        super().__init__()

        self.setObjectName("StatCard")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(10)

        self.title_label = QLabel(title)
        self.title_label.setObjectName("MutedText")

        self.value_label = QLabel(value)
        self.value_label.setObjectName("StatValue")

        layout.addWidget(self.title_label)
        layout.addWidget(self.value_label)

    def set_value(self, value: str):
        self.value_label.setText(value)


class Dashboard(QWidget):
    def __init__(self):
        super().__init__()

        self.setObjectName("DashboardPage")

        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 24)
        root.setSpacing(22)

        header = QVBoxLayout()
        header.setSpacing(6)

        title = QLabel("Dashboard")
        title.setObjectName("PageTitle")

        subtitle = QLabel(
            "Your tasks, learning progress and daily overview."
        )
        subtitle.setObjectName("MutedText")

        header.addWidget(title)
        header.addWidget(subtitle)
        root.addLayout(header)

        self.stats = QGridLayout()
        self.stats.setSpacing(16)

        self.total_tasks = StatCard("Total Tasks")
        self.completed_tasks = StatCard("Completed Tasks")
        self.active_subjects = StatCard("Active Learning Subjects")
        self.completed_topics = StatCard("Completed Topics")

        self.stats.addWidget(self.total_tasks, 0, 0)
        self.stats.addWidget(self.completed_tasks, 0, 1)
        self.stats.addWidget(self.active_subjects, 0, 2)
        self.stats.addWidget(self.completed_topics, 0, 3)

        root.addLayout(self.stats)

        section_title = QLabel("Today's Tasks")
        section_title.setObjectName("SectionTitle")
        root.addWidget(section_title)

        self.task_list = QListWidget()
        self.task_list.setObjectName("TaskList")
        self.task_list.setMinimumHeight(180)
        root.addWidget(self.task_list)

        root.addStretch()

        self.refresh_data()

    def refresh_data(self):
        today = date.today().isoformat()

        with get_connection() as connection:
            total = connection.execute(
                "SELECT COUNT(*) FROM tasks"
            ).fetchone()[0]

            completed = connection.execute(
                "SELECT COUNT(*) FROM tasks WHERE status = 'Completed'"
            ).fetchone()[0]

            subjects = connection.execute(
                """
                SELECT COUNT(*)
                FROM learning_subjects
                WHERE status = 'Active'
                """
            ).fetchone()[0]

            topics = connection.execute(
                """
                SELECT COUNT(*)
                FROM topics
                WHERE status = 'Completed'
                """
            ).fetchone()[0]

            tasks = connection.execute(
                """
                SELECT title, status, priority
                FROM tasks
                WHERE status != 'Completed'
                  AND due_at IS NOT NULL
                  AND substr(due_at, 1, 10) <= ?
                ORDER BY
                    CASE priority
                        WHEN 'Urgent' THEN 1
                        WHEN 'High' THEN 2
                        WHEN 'Medium' THEN 3
                        ELSE 4
                    END,
                    due_at
                LIMIT 20
                """,
                (today,),
            ).fetchall()

        self.total_tasks.set_value(str(total))
        self.completed_tasks.set_value(str(completed))
        self.active_subjects.set_value(str(subjects))
        self.completed_topics.set_value(str(topics))

        self.task_list.clear()

        if not tasks:
            self.task_list.addItem(
                "No due or overdue tasks. You're all caught up!"
            )
        else:
            for task in tasks:
                item = QListWidgetItem(
                    f"{task['title']}   •   "
                    f"{task['priority']}   •   {task['status']}"
                )
                self.task_list.addItem(item)
