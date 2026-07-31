import sqlite3

DB_NAME = "MyApp.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


def _column_names(cursor, table_name):
    return {
        row[1]
        for row in cursor.execute(
            f"PRAGMA table_info({table_name})"
        ).fetchall()
    }


def _add_missing_columns(cursor, table_name, columns):
    existing = _column_names(cursor, table_name)

    for column_name, definition in columns.items():
        if column_name not in existing:
            cursor.execute(
                f"ALTER TABLE {table_name} "
                f"ADD COLUMN {column_name} {definition}"
            )


def create_tables():
    """Create tables and migrate older NoteNest databases safely."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS notebooks(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER REFERENCES users(id),
            name TEXT NOT NULL,
            color TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS categories(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            color TEXT,
            user_id INTEGER REFERENCES users(id)
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS tasks(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            priority TEXT DEFAULT 'Medium',
            is_completed INTEGER DEFAULT 0,
            due_date DATE,
            user_id INTEGER REFERENCES users(id),
            due_time TEXT,
            category TEXT DEFAULT 'Study',
            category_id INTEGER REFERENCES categories(id),
            activity_type TEXT DEFAULT 'task',
            link TEXT DEFAULT '',
            carry_forward INTEGER DEFAULT 1,
            notify_enabled INTEGER DEFAULT 0,
            completed_at TIMESTAMP
        )
        """
    )

    _add_missing_columns(
        cursor,
        "tasks",
        {
            "due_time": "TEXT",
            "category": "TEXT DEFAULT 'Study'",
            "category_id": "INTEGER REFERENCES categories(id)",
            "activity_type": "TEXT DEFAULT 'task'",
            "link": "TEXT DEFAULT ''",
            "carry_forward": "INTEGER DEFAULT 1",
            "notify_enabled": "INTEGER DEFAULT 0",
            "completed_at": "TIMESTAMP",
        },
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS notes(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            notebook_id INTEGER REFERENCES notebooks(id),
            title TEXT NOT NULL,
            content TEXT,
            is_pinned INTEGER DEFAULT 0,
            is_archived INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            category_id INTEGER REFERENCES categories(id),
            task_id INTEGER REFERENCES tasks(id)
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS attachments(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            note_id INTEGER REFERENCES notes(id),
            file_path TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS reminders(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id INTEGER REFERENCES tasks(id),
            remind_at TIMESTAMP,
            is_active INTEGER DEFAULT 1
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS pomodoro_sessions(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id INTEGER REFERENCES tasks(id),
            started_at TIMESTAMP,
            completed INTEGER DEFAULT 0,
            duration INTEGER
        )
        """
    )

    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_tasks_due_date
        ON tasks(due_date)
        """
    )

    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_reminders_active_time
        ON reminders(is_active, remind_at)
        """
    )

    conn.commit()
    conn.close()


if __name__ == "__main__":
    create_tables()
    print("Database and tables created successfully!")