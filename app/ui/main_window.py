
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QPushButton,
    QLabel,
    QStackedWidget,
)

from app.config import APP_NAME, APP_VERSION, SIDEBAR_WIDTH
from app.ui.dashboard import Dashboard
from app.ui.tasks_page import TasksPage


class PlaceholderPage(QWidget):
    def __init__(self, title: str, description: str):
        super().__init__()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 30, 32, 30)
        layout.setSpacing(12)

        heading = QLabel(title)
        heading.setObjectName("PageTitle")

        message = QLabel(description)
        message.setObjectName("MutedText")
        message.setWordWrap(True)

        layout.addWidget(heading)
        layout.addWidget(message)
        layout.addStretch()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle(f"{APP_NAME} - v{APP_VERSION}")
        self.setMinimumSize(1000, 650)
        self.resize(1400, 850)

        central = QWidget()
        central.setObjectName("CentralWidget")
        self.setCentralWidget(central)

        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        sidebar = QWidget()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(SIDEBAR_WIDTH)

        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(16, 24, 16, 20)
        sidebar_layout.setSpacing(8)

        brand = QLabel("MY PERSONAL OS")
        brand.setObjectName("BrandTitle")
        sidebar_layout.addWidget(brand)

        subtitle = QLabel("Personal Productivity")
        subtitle.setObjectName("MutedText")
        sidebar_layout.addWidget(subtitle)
        sidebar_layout.addSpacing(24)

        self.stack = QStackedWidget()
        self.stack.setObjectName("ContentStack")

        self.dashboard = Dashboard()
        self.tasks_page = TasksPage()

        self.stack.addWidget(self.dashboard)
        self.stack.addWidget(self.tasks_page)

        self.page_indexes = {
            "Dashboard": 0,
            "Tasks": 1,
        }

        placeholders = [
            ("Reminders", "Reminder scheduling will be implemented next."),
            ("Learning", "Learning subjects and topics."),
            ("Roadmaps", "Build and manage learning roadmaps."),
            ("Calendar", "View deadlines and planned activities."),
            ("Study Timer", "Track focus sessions and study time."),
            ("Notes", "Manage your notes and resources."),
            ("Goals", "Set and track personal goals."),
            ("Habits", "Track daily habits and streaks."),
            ("Projects", "Manage projects and milestones."),
            ("Analytics", "Review weekly and monthly progress."),
        ]

        for name, description in placeholders:
            self.page_indexes[name] = self.stack.count()
            self.stack.addWidget(
                PlaceholderPage(name, description)
            )

        self.nav_buttons = []

        navigation_names = [
            "Dashboard",
            "Tasks",
            "Reminders",
            "Learning",
            "Roadmaps",
            "Calendar",
            "Study Timer",
            "Notes",
            "Goals",
            "Habits",
            "Projects",
            "Analytics",
        ]

        for name in navigation_names:
            button = QPushButton(name)
            button.setObjectName("NavButton")
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.setCheckable(True)

            button.clicked.connect(
                lambda checked=False, page_name=name:
                self.navigate(page_name)
            )

            sidebar_layout.addWidget(button)
            self.nav_buttons.append(button)

        sidebar_layout.addStretch()

        footer = QLabel(f"Version {APP_VERSION}")
        footer.setObjectName("MutedText")
        sidebar_layout.addWidget(footer)

        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.stack, 1)

        self.navigate("Dashboard")

    def navigate(self, page_name: str):
        index = self.page_indexes[page_name]
        self.stack.setCurrentIndex(index)

        for button in self.nav_buttons:
            button.setChecked(button.text() == page_name)

        if page_name == "Dashboard":
            self.dashboard.refresh_data()

        elif page_name == "Tasks":
            self.tasks_page.refresh_tasks()
