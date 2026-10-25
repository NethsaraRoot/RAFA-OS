
import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication, QMessageBox

from app.config import APP_NAME
from app.database.connection import initialize_database
from app.ui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setStyle("Fusion")

    project_dir = Path(__file__).resolve().parent
    stylesheet_path = (
        project_dir / "app" / "assets" / "styles" / "dark.qss"
    )

    if stylesheet_path.exists():
        app.setStyleSheet(
            stylesheet_path.read_text(encoding="utf-8")
        )

    try:
        initialize_database()
        window = MainWindow()
        window.show()
    except Exception as error:
        QMessageBox.critical(
            None,
            "Application Startup Error",
            f"Could not start the application:\n{error}",
        )
        return 1

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
