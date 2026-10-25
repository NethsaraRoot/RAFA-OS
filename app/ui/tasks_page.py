
from datetime import datetime

from PySide6.QtCore import Qt, QDateTime
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QLabel,
    QPushButton,
    QLineEdit,
    QComboBox,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QDialog,
    QDialogButtonBox,
    QTextEdit,
    QDateTimeEdit,
    QCheckBox,
    QSpinBox,
    QMessageBox,
)

from app.modules import tasks


class TaskDialog(QDialog):
    """Dialog for creating or editing a task."""

    def __init__(self, parent=None, task=None):
        super().__init__(parent)

        self.task = task
        self.setWindowTitle("Edit Task" if task else "New Task")
        self.setMinimumWidth(460)

        layout = QVBoxLayout(self)
        form = QFormLayout()
        form.setSpacing(12)

        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("e.g. Study JavaScript")

        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("Task details...")
        self.description_input.setMaximumHeight(90)

        self.category_input = QLineEdit("General")

        self.priority_input = QComboBox()
        self.priority_input.addItems(["Low", "Medium", "High", "Urgent"])

        self.due_enabled = QCheckBox("Set a due date and time")
        self.due_input = QDateTimeEdit(QDateTime.currentDateTime())
        self.due_input.setCalendarPopup(True)
        self.due_input.setDisplayFormat("yyyy-MM-dd HH:mm")
        self.due_input.setEnabled(False)
        self.due_enabled.toggled.connect(self.due_input.setEnabled)

        self.estimate_input = QSpinBox()
        self.estimate_input.setRange(0, 100000)
        self.estimate_input.setSuffix(" minutes")
        self.estimate_input.setSpecialValueText("Not set")
        self.estimate_input.setValue(0)

        form.addRow("Task title *", self.title_input)
        form.addRow("Description", self.description_input)
        form.addRow("Category", self.category_input)
        form.addRow("Priority", self.priority_input)
        form.addRow("", self.due_enabled)
        form.addRow("Due date", self.due_input)
        form.addRow("Estimated time", self.estimate_input)

        layout.addLayout(form)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.validate_and_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        if task:
            self.title_input.setText(task["title"])
            self.description_input.setPlainText(
                task["description"] or ""
            )
            self.category_input.setText(task["category"] or "General")
            self.priority_input.setCurrentText(task["priority"])

            if task["due_at"]:
                parsed = QDateTime.fromString(
                    task["due_at"], "yyyy-MM-dd HH:mm:ss"
                )
                if not parsed.isValid():
                    parsed = QDateTime.fromString(
                        task["due_at"], "yyyy-MM-dd HH:mm"
                    )
                if parsed.isValid():
                    self.due_input.setDateTime(parsed)
                    self.due_enabled.setChecked(True)

            if task["estimated_minutes"] is not None:
                self.estimate_input.setValue(
                    task["estimated_minutes"]
                )

    def validate_and_accept(self):
        if not self.title_input.text().strip():
            QMessageBox.warning(
                self, "Missing title", "Enter a task title."
            )
            self.title_input.setFocus()
            return

        self.accept()

    def get_values(self):
        due_at = None

        if self.due_enabled.isChecked():
            due_at = self.due_input.dateTime().toString(
                "yyyy-MM-dd HH:mm:ss"
            )

        estimated = self.estimate_input.value()
        if estimated == 0:
            estimated = None

        return {
            "title": self.title_input.text().strip(),
            "description": self.description_input.toPlainText(),
            "category": self.category_input.text().strip() or "General",
            "priority": self.priority_input.currentText(),
            "due_at": due_at,
            "estimated_minutes": estimated,
        }


class TasksPage(QWidget):
    """Task list with create, edit, complete, search and delete."""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setObjectName("TasksPage")

        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 24)
        root.setSpacing(18)

        heading = QLabel("Tasks")
        heading.setObjectName("PageTitle")

        subtitle = QLabel(
            "Plan your work, set priorities and track completion."
        )
        subtitle.setObjectName("MutedText")

        root.addWidget(heading)
        root.addWidget(subtitle)

        toolbar = QHBoxLayout()

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search tasks...")
        self.search_input.setClearButtonEnabled(True)
        self.search_input.textChanged.connect(self.refresh_tasks)

        self.status_filter = QComboBox()
        self.status_filter.addItems(
            ["All", "Not Started", "In Progress", "Completed"]
        )
        self.status_filter.currentTextChanged.connect(
            self.refresh_tasks
        )

        self.priority_filter = QComboBox()
        self.priority_filter.addItems(
            ["All", "Urgent", "High", "Medium", "Low"]
        )
        self.priority_filter.currentTextChanged.connect(
            self.refresh_tasks
        )

        self.add_button = QPushButton("+ New Task")
        self.add_button.setObjectName("PrimaryButton")
        self.add_button.clicked.connect(self.add_task)

        toolbar.addWidget(self.search_input, 1)
        toolbar.addWidget(self.status_filter)
        toolbar.addWidget(self.priority_filter)
        toolbar.addWidget(self.add_button)

        root.addLayout(toolbar)

        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(
            ["Done", "Task", "Priority", "Status", "Due Date", "Category"]
        )
        self.table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.table.setSelectionMode(
            QTableWidget.SelectionMode.SingleSelection
        )
        self.table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch
        )
        self.table.setColumnWidth(0, 58)
        self.table.setColumnWidth(2, 95)
        self.table.setColumnWidth(3, 120)
        self.table.setColumnWidth(4, 155)
        self.table.setColumnWidth(5, 115)
        self.table.setAlternatingRowColors(True)
        self.table.cellDoubleClicked.connect(self.edit_selected_task)

        root.addWidget(self.table, 1)

        actions = QHBoxLayout()

        self.edit_button = QPushButton("Edit Selected")
        self.edit_button.clicked.connect(self.edit_selected_task)

        self.complete_button = QPushButton("Mark Completed")
        self.complete_button.clicked.connect(self.complete_selected_task)

        self.reopen_button = QPushButton("Reopen Task")
        self.reopen_button.clicked.connect(self.reopen_selected_task)

        self.delete_button = QPushButton("Delete Selected")
        self.delete_button.clicked.connect(self.delete_selected_task)

        actions.addWidget(self.edit_button)
        actions.addWidget(self.complete_button)
        actions.addWidget(self.reopen_button)
        actions.addWidget(self.delete_button)
        actions.addStretch()

        root.addLayout(actions)

        self.refresh_tasks()

    def selected_task_id(self):
        row = self.table.currentRow()

        if row < 0:
            QMessageBox.information(
                self, "Select a task", "Please select a task first."
            )
            return None

        item = self.table.item(row, 0)
        if item is None:
            return None

        return item.data(Qt.ItemDataRole.UserRole)

    def refresh_tasks(self, *_):
        records = tasks.get_tasks(
            search=self.search_input.text(),
            status=self.status_filter.currentText(),
            priority=self.priority_filter.currentText(),
        )

        self.table.setRowCount(0)

        for record in records:
            row = self.table.rowCount()
            self.table.insertRow(row)

            checkbox = QCheckBox()
            checkbox.setChecked(record["status"] == "Completed")
            checkbox.setToolTip("Mark task completed or reopen it")
            checkbox.stateChanged.connect(
                lambda state, task_id=record["id"]:
                self.toggle_task(task_id, state)
            )

            checkbox_holder = QWidget()
            holder_layout = QHBoxLayout(checkbox_holder)
            holder_layout.setContentsMargins(0, 0, 0, 0)
            holder_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            holder_layout.addWidget(checkbox)
            self.table.setCellWidget(row, 0, checkbox_holder)

            title_item = QTableWidgetItem(record["title"])
            title_item.setData(
                Qt.ItemDataRole.UserRole, record["id"]
            )
            title_item.setToolTip(record["description"] or "")
            self.table.setItem(row, 1, title_item)

            self.table.setItem(
                row, 2, QTableWidgetItem(record["priority"])
            )
            self.table.setItem(
                row, 3, QTableWidgetItem(record["status"])
            )

            due = record["due_at"] or "No deadline"
            self.table.setItem(row, 4, QTableWidgetItem(due))

            self.table.setItem(
                row, 5, QTableWidgetItem(record["category"])
            )

            if record["status"] == "Completed":
                title_item.setForeground(Qt.GlobalColor.gray)

        self.table.resizeRowsToContents()

    def toggle_task(self, task_id, state):
        try:
            status = (
                "Completed"
                if state == Qt.CheckState.Checked.value
                else "Not Started"
            )
            tasks.set_task_status(task_id, status)
            self.refresh_tasks()
            self.notify_dashboard()
        except Exception as error:
            QMessageBox.critical(
                self, "Task error", str(error)
            )
            self.refresh_tasks()

    def add_task(self):
        dialog = TaskDialog(self)

        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        try:
            tasks.create_task(**dialog.get_values())
            self.refresh_tasks()
            self.notify_dashboard()
        except Exception as error:
            QMessageBox.critical(
                self, "Could not create task", str(error)
            )

    def edit_selected_task(self, *_):
        task_id = self.selected_task_id()
        if task_id is None:
            return

        record = tasks.get_task(task_id)
        if not record:
            QMessageBox.warning(
                self, "Task unavailable", "This task no longer exists."
            )
            self.refresh_tasks()
            return

        dialog = TaskDialog(self, record)

        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        try:
            tasks.update_task(task_id, **dialog.get_values())
            self.refresh_tasks()
            self.notify_dashboard()
        except Exception as error:
            QMessageBox.critical(
                self, "Could not update task", str(error)
            )

    def complete_selected_task(self):
        self.change_selected_status("Completed")

    def reopen_selected_task(self):
        self.change_selected_status("Not Started")

    def change_selected_status(self, status):
        task_id = self.selected_task_id()
        if task_id is None:
            return

        try:
            tasks.set_task_status(task_id, status)
            self.refresh_tasks()
            self.notify_dashboard()
        except Exception as error:
            QMessageBox.critical(self, "Task error", str(error))

    def delete_selected_task(self):
        task_id = self.selected_task_id()
        if task_id is None:
            return

        record = tasks.get_task(task_id)
        if not record:
            self.refresh_tasks()
            return

        answer = QMessageBox.question(
            self,
            "Delete Task",
            f"Delete '{record['title']}' permanently?",
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if answer != QMessageBox.StandardButton.Yes:
            return

        try:
            tasks.delete_task(task_id)
            self.refresh_tasks()
            self.notify_dashboard()
        except Exception as error:
            QMessageBox.critical(self, "Task error", str(error))

    def notify_dashboard(self):
        window = self.window()

        dashboard = getattr(window, "dashboard", None)
        if dashboard is not None:
            dashboard.refresh_data()
