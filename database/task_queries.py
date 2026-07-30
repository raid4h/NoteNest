from datetime import date, datetime, timedelta

from database.db import get_connection


TASK_SELECT = """
    SELECT id, title, priority, is_completed, due_date, user_id,
           due_time, category, link, carry_forward, notify_enabled, completed_at
    FROM tasks
"""


def _task_dict(row, occurrence_date=None):
    return {
        "id": row[0],
        "title": row[1],
        "priority": row[2] or "Medium",
        "completed": bool(row[3]),
        "due_date": row[4] or "",
        "user_id": row[5],
        "due_time": row[6] or "",
        "category": row[7] or "Study",
        "link": row[8] or "",
        "carry_forward": bool(row[9]),
        "notify_enabled": bool(row[10]),
        "completed_at": row[11],
        "occurrence_date": occurrence_date or row[4] or "",
        "is_carried": bool(occurrence_date and row[4] and occurrence_date != row[4]),
        "subtasks": [],
    }


def create_tasks(
    title,
    user_id,
    priority="Medium",
    due_date=None,
    due_time=None,
    category="Study",
    link="",
    carry_forward=True,
    notify_enabled=False,
    schedule_reminder=True,
):
    """Create a task. The original two-argument API remains supported."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO tasks(
            title, user_id, priority, due_date, due_time,
            category, link, carry_forward, notify_enabled
        )
        VALUES(?,?,?,?,?,?,?,?,?)
        """,
        (
            title.strip(),
            user_id,
            priority,
            due_date,
            due_time,
            category,
            link.strip(),
            int(bool(carry_forward)),
            int(bool(notify_enabled)),
        ),
    )
    task_id = cursor.lastrowid
    conn.commit()
    conn.close()

    if schedule_reminder and notify_enabled and due_date and due_time:
        from database.reminder_queries import upsert_task_reminder

        remind_at = f"{due_date} {due_time}:00"
        upsert_task_reminder(task_id, remind_at)

    return task_id


def get_all_tasks(user_id):
    """Return tuples for backward compatibility with backup/home code."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        TASK_SELECT
        + """
        WHERE user_id = ?
        ORDER BY due_date ASC, COALESCE(due_time, '23:59') ASC
        """,
        (user_id,),
    )
    tasks = cursor.fetchall()
    conn.close()
    return tasks


def get_tasks_by_id(task_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(TASK_SELECT + " WHERE id=?", (task_id,))
    task = cursor.fetchone()
    conn.close()
    return task


def get_tasks_by_date(due_date):
    """
    Return tasks shown on a calendar day.

    An unfinished carry-forward task appears on every day after its original
    due date up to today. Its original due date is never overwritten.
    """
    selected = datetime.strptime(due_date, "%Y-%m-%d").date()
    today = date.today()

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        TASK_SELECT
        + """
        WHERE due_date = ?
           OR (
               carry_forward = 1
               AND is_completed = 0
               AND due_date < ?
           )
        ORDER BY is_completed ASC, COALESCE(due_time, '23:59') ASC, id ASC
        """,
        (due_date, due_date),
    )
    rows = cursor.fetchall()
    conn.close()

    tasks = []
    for row in rows:
        original_due = row[4]
        is_original_day = original_due == due_date
        can_carry_to_day = (
            bool(row[9])
            and not bool(row[3])
            and original_due
            and original_due < due_date
            and selected <= today
        )
        if is_original_day or can_carry_to_day:
            tasks.append(_task_dict(row, occurrence_date=due_date))
    return tasks


def get_all_task_dates(year=None, month=None):
    """
    Return calendar dates containing tasks.

    Carry-forward dates are expanded only through today, preventing an
    unfinished task from marking every future calendar day.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT due_date, is_completed, carry_forward
        FROM tasks
        WHERE due_date IS NOT NULL AND due_date != ''
        """
    )
    rows = cursor.fetchall()
    conn.close()

    today = date.today()
    dates = set()

    for due_date, is_completed, carry_forward in rows:
        try:
            start = datetime.strptime(due_date, "%Y-%m-%d").date()
        except (TypeError, ValueError):
            continue

        dates.add(due_date)
        if carry_forward and not is_completed and start < today:
            current = start + timedelta(days=1)
            while current <= today:
                dates.add(current.isoformat())
                current += timedelta(days=1)

    if year is not None and month is not None:
        prefix = f"{year:04d}-{month:02d}-"
        dates = {value for value in dates if value.startswith(prefix)}

    return sorted(dates)


def update_tasks(
    task_id,
    title,
    due_date,
    due_time=None,
    priority=None,
    category=None,
    link=None,
    carry_forward=None,
    notify_enabled=None,
):
    fields = ["title=?", "due_date=?"]
    values = [title, due_date]

    optional = {
        "due_time": due_time,
        "priority": priority,
        "category": category,
        "link": link,
        "carry_forward": (
            int(bool(carry_forward)) if carry_forward is not None else None
        ),
        "notify_enabled": (
            int(bool(notify_enabled)) if notify_enabled is not None else None
        ),
    }
    for field, value in optional.items():
        if value is not None:
            fields.append(f"{field}=?")
            values.append(value)

    values.append(task_id)
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        f"UPDATE tasks SET {', '.join(fields)} WHERE id=?",
        tuple(values),
    )
    conn.commit()
    conn.close()


def delete_tasks(task_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM reminders WHERE task_id=?", (task_id,))
    cursor.execute("DELETE FROM tasks WHERE id=?", (task_id,))
    conn.commit()
    conn.close()


def search_tasks(keyword):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        TASK_SELECT
        + """
        WHERE title LIKE ? OR due_date LIKE ? OR link LIKE ?
        ORDER BY due_date ASC
        """,
        (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"),
    )
    results = cursor.fetchall()
    conn.close()
    return results


def set_priority(task_id, priority):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE tasks SET priority=? WHERE id=?", (priority, task_id))
    conn.commit()
    conn.close()


def set_due_date(task_id, due_date):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE tasks SET due_date=? WHERE id=?", (due_date, task_id))
    conn.commit()
    conn.close()


def set_task_completed(task_id, completed=True):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE tasks
        SET is_completed=?,
            completed_at=CASE WHEN ?=1 THEN CURRENT_TIMESTAMP ELSE NULL END
        WHERE id=?
        """,
        (int(bool(completed)), int(bool(completed)), task_id),
    )
    if completed:
        cursor.execute(
            "UPDATE reminders SET is_active=0 WHERE task_id=?",
            (task_id,),
        )
    conn.commit()
    conn.close()


def complete_tasks(task_id):
    set_task_completed(task_id, True)
