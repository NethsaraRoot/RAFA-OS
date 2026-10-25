
import sqlite3

SCHEMA_VERSION = 1


def initialize_schema(connection: sqlite3.Connection) -> None:
    """Create all application tables and indexes."""

    connection.executescript(
        """
        CREATE TABLE IF NOT EXISTS schema_version (
            version INTEGER NOT NULL
        );

        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL DEFAULT '',
            category TEXT NOT NULL DEFAULT 'General',
            priority TEXT NOT NULL DEFAULT 'Medium'
                CHECK(priority IN ('Low','Medium','High','Urgent')),
            status TEXT NOT NULL DEFAULT 'Not Started'
                CHECK(status IN ('Not Started','In Progress','Completed')),
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            due_at TEXT,
            completed_at TEXT,
            estimated_minutes INTEGER,
            actual_minutes INTEGER NOT NULL DEFAULT 0,
            tags TEXT NOT NULL DEFAULT '',
            notes TEXT NOT NULL DEFAULT '',
            recurring_rule TEXT,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            message TEXT NOT NULL DEFAULT '',
            remind_at TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Pending'
                CHECK(status IN ('Pending','Sent','Dismissed','Cancelled')),
            task_id INTEGER REFERENCES tasks(id) ON DELETE SET NULL,
            topic_id INTEGER,
            goal_id INTEGER,
            project_id INTEGER,
            recurrence_rule TEXT,
            last_notified_at TEXT,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS learning_subjects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT NOT NULL DEFAULT '',
            category TEXT NOT NULL DEFAULT 'General',
            current_level TEXT NOT NULL DEFAULT 'Beginner',
            objective TEXT NOT NULL DEFAULT '',
            start_date TEXT,
            target_date TEXT,
            status TEXT NOT NULL DEFAULT 'Active'
                CHECK(status IN ('Active','Completed','Archived')),
            color TEXT NOT NULL DEFAULT '#4F46E5',
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS topics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject_id INTEGER NOT NULL
                REFERENCES learning_subjects(id) ON DELETE CASCADE,
            parent_topic_id INTEGER REFERENCES topics(id) ON DELETE CASCADE,
            title TEXT NOT NULL,
            description TEXT NOT NULL DEFAULT '',
            status TEXT NOT NULL DEFAULT 'Not Started'
                CHECK(status IN ('Not Started','In Progress','Completed')),
            priority TEXT NOT NULL DEFAULT 'Medium',
            estimated_minutes INTEGER,
            actual_minutes INTEGER NOT NULL DEFAULT 0,
            notes TEXT NOT NULL DEFAULT '',
            resource_links TEXT NOT NULL DEFAULT '',
            completed_at TEXT,
            sort_order INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS roadmaps (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject_id INTEGER REFERENCES learning_subjects(id)
                ON DELETE SET NULL,
            title TEXT NOT NULL,
            description TEXT NOT NULL DEFAULT '',
            objective TEXT NOT NULL DEFAULT '',
            current_level TEXT NOT NULL DEFAULT 'Beginner',
            target_level TEXT NOT NULL DEFAULT 'Advanced',
            start_date TEXT,
            target_date TEXT,
            status TEXT NOT NULL DEFAULT 'Active'
                CHECK(status IN ('Active','Completed','Archived')),
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS roadmap_stages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            roadmap_id INTEGER NOT NULL
                REFERENCES roadmaps(id) ON DELETE CASCADE,
            title TEXT NOT NULL,
            description TEXT NOT NULL DEFAULT '',
            sort_order INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS milestones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            roadmap_id INTEGER NOT NULL
                REFERENCES roadmaps(id) ON DELETE CASCADE,
            stage_id INTEGER REFERENCES roadmap_stages(id)
                ON DELETE SET NULL,
            title TEXT NOT NULL,
            description TEXT NOT NULL DEFAULT '',
            due_date TEXT,
            status TEXT NOT NULL DEFAULT 'Not Started'
                CHECK(status IN ('Not Started','In Progress','Completed')),
            completed_at TEXT,
            sort_order INTEGER NOT NULL DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS learning_resources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject_id INTEGER REFERENCES learning_subjects(id)
                ON DELETE CASCADE,
            topic_id INTEGER REFERENCES topics(id) ON DELETE CASCADE,
            roadmap_id INTEGER REFERENCES roadmaps(id) ON DELETE CASCADE,
            title TEXT NOT NULL,
            url TEXT NOT NULL DEFAULT '',
            resource_type TEXT NOT NULL DEFAULT 'Link',
            notes TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS study_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject_id INTEGER REFERENCES learning_subjects(id)
                ON DELETE SET NULL,
            topic_id INTEGER REFERENCES topics(id)
                ON DELETE SET NULL,
            project_id INTEGER,
            started_at TEXT NOT NULL,
            ended_at TEXT,
            duration_minutes INTEGER NOT NULL DEFAULT 0,
            session_type TEXT NOT NULL DEFAULT 'Focus',
            notes TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL DEFAULT '',
            category TEXT NOT NULL DEFAULT 'General',
            tags TEXT NOT NULL DEFAULT '',
            subject_id INTEGER REFERENCES learning_subjects(id)
                ON DELETE SET NULL,
            topic_id INTEGER REFERENCES topics(id)
                ON DELETE SET NULL,
            task_id INTEGER REFERENCES tasks(id)
                ON DELETE SET NULL,
            project_id INTEGER,
            is_pinned INTEGER NOT NULL DEFAULT 0
                CHECK(is_pinned IN (0,1)),
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL DEFAULT '',
            period TEXT NOT NULL DEFAULT 'Custom',
            start_date TEXT,
            target_date TEXT,
            target_value REAL,
            current_value REAL NOT NULL DEFAULT 0,
            unit TEXT NOT NULL DEFAULT '',
            status TEXT NOT NULL DEFAULT 'Active'
                CHECK(status IN ('Active','Completed','Archived')),
            completed_at TEXT,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS habits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL DEFAULT '',
            target_frequency TEXT NOT NULL DEFAULT 'Daily',
            target_count INTEGER NOT NULL DEFAULT 1,
            is_active INTEGER NOT NULL DEFAULT 1
                CHECK(is_active IN (0,1)),
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS habit_completions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            habit_id INTEGER NOT NULL
                REFERENCES habits(id) ON DELETE CASCADE,
            completed_date TEXT NOT NULL,
            completion_count INTEGER NOT NULL DEFAULT 1,
            notes TEXT NOT NULL DEFAULT '',
            UNIQUE(habit_id, completed_date)
        );

        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL DEFAULT '',
            priority TEXT NOT NULL DEFAULT 'Medium',
            status TEXT NOT NULL DEFAULT 'Not Started'
                CHECK(status IN ('Not Started','In Progress','Completed','Archived')),
            start_date TEXT,
            due_date TEXT,
            completed_at TEXT,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS project_milestones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL
                REFERENCES projects(id) ON DELETE CASCADE,
            title TEXT NOT NULL,
            description TEXT NOT NULL DEFAULT '',
            due_date TEXT,
            status TEXT NOT NULL DEFAULT 'Not Started'
                CHECK(status IN ('Not Started','In Progress','Completed')),
            completed_at TEXT,
            sort_order INTEGER NOT NULL DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS roadmap_topic_links (
            roadmap_stage_id INTEGER NOT NULL
                REFERENCES roadmap_stages(id) ON DELETE CASCADE,
            topic_id INTEGER NOT NULL
                REFERENCES topics(id) ON DELETE CASCADE,
            sort_order INTEGER NOT NULL DEFAULT 0,
            PRIMARY KEY (roadmap_stage_id, topic_id)
        );

        CREATE TABLE IF NOT EXISTS topic_prerequisites (
            topic_id INTEGER NOT NULL
                REFERENCES topics(id) ON DELETE CASCADE,
            prerequisite_topic_id INTEGER NOT NULL
                REFERENCES topics(id) ON DELETE CASCADE,
            PRIMARY KEY (topic_id, prerequisite_topic_id),
            CHECK(topic_id <> prerequisite_topic_id)
        );

        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );

        CREATE INDEX IF NOT EXISTS idx_tasks_due_at
            ON tasks(due_at);
        CREATE INDEX IF NOT EXISTS idx_tasks_status
            ON tasks(status);
        CREATE INDEX IF NOT EXISTS idx_reminders_due
            ON reminders(status, remind_at);
        CREATE INDEX IF NOT EXISTS idx_topics_subject
            ON topics(subject_id, status);
        CREATE INDEX IF NOT EXISTS idx_topics_parent
            ON topics(parent_topic_id);
        CREATE INDEX IF NOT EXISTS idx_roadmap_stages
            ON roadmap_stages(roadmap_id, sort_order);
        CREATE INDEX IF NOT EXISTS idx_study_sessions_start
            ON study_sessions(started_at);
        CREATE INDEX IF NOT EXISTS idx_notes_updated
            ON notes(updated_at);
        CREATE INDEX IF NOT EXISTS idx_habit_completions_date
            ON habit_completions(completed_date);
        CREATE INDEX IF NOT EXISTS idx_projects_due
            ON projects(due_date);
        """
    )

    current_version = connection.execute(
        "SELECT MAX(version) FROM schema_version"
    ).fetchone()[0]

    if current_version is None:
        connection.execute(
            "INSERT INTO schema_version (version) VALUES (?)",
            (SCHEMA_VERSION,),
        )
    elif current_version < SCHEMA_VERSION:
        raise RuntimeError(
            f"Database schema version {current_version} is older than "
            f"required version {SCHEMA_VERSION}. Add a migration before "
            "upgrading this database."
        )
    elif current_version > SCHEMA_VERSION:
        raise RuntimeError(
            "This database was created by a newer application version."
        )
