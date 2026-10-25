
from pathlib import Path
import sqlite3

from platformdirs import user_data_dir

APP_NAME = "MyPersonalOS"


def get_data_directory() -> Path:
    """Return a stable, user-writable application data directory."""
    data_dir = Path(user_data_dir(APP_NAME, appauthor=False))
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


def get_database_path() -> Path:
    """Return the absolute path to the SQLite database."""
    return get_data_directory() / "mypersonalos.db"


def get_connection() -> sqlite3.Connection:
    """Create and return a configured SQLite connection."""
    db_path = get_database_path()

    connection = sqlite3.connect(
        str(db_path),
        timeout=10.0,
    )

    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    connection.execute("PRAGMA busy_timeout = 10000")

    return connection


def initialize_database() -> None:
    """Create the database schema if it does not already exist."""
    from app.database.schema import initialize_schema

    with get_connection() as connection:
        initialize_schema(connection)


if __name__ == "__main__":
    initialize_database()
    print("Database initialized successfully!")
    print(f"Database location: {get_database_path()}")
