from datetime import date, datetime, timedelta

from database.db import get_connection


TASK_SELECT = """
    SELECT id, title, priority, is_completed, due_date, user_id,
           due_time, category, link, carry_forward,
           notify_enabled, completed_at, category_id, activity_type
    FROM tasks
"""


def _task_dict(row, occurrence_date=None):
    original_due = row[4] or ""
    original_day = original_due[:10] if original_due else ""

    return {
        "id": row[0],
        "title": row[1],
        "priority": row[2] or "Medium",
        "completed": bool(row[3]),
        "due_date": original_due,
        "user_id": row[5],
        "due_time": row[6] or "",
        "category": row[7] or "Study",
        "link": row[8] or "",
        "carry_forward": bool(row[9]),
        "notify_enabled": bool(row[10]),
        "completed_at": row[11],
        "category_id": row[12],
        "activity_type": row[13] or "task",
        "occurrence_date": occurrence_date or original_day,
        "is_carried": bool(
            occurrence_date
            and original_day
            and occurrence_date != original_day
        ),
        "subtasks": [],
    }


def create_tasks(
    title,
    user_id,
    activity_type="task",
    category_id=None,
    due_date=None,
    priority=None,
    due_time=None,
    category="Study",
    link="",
    carry_forward=True,
    notify_enabled=False,
    schedule_reminder=True,
):
    clean_title = (title or "").strip()
    if not clean_title:
        raise ValueError("Task title cannot be empty.")

    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO tasks(
                title, user_id, activity_type, category_id, due_date,
                priority, due_time, category, link, carry_forward,
                notify_enabled
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                clean_title,
                user_id,
                activity_type or "task",
                category_id,
                due_date,
                priority or "Medium",
                due_time,
                category or "Study",
                (link or "").strip(),
                int(bool(carry_forward)),
                int(bool(notify_enabled)),
            ),
        )
        task_id = cursor.lastrowid
        conn.commit()
    finally:
        conn.close()

    if schedule_reminder and notify_enabled and due_date and due_time:
        from database.reminder_queries import upsert_task_reminder

        reminder_day = str(due_date)[:10]
        upsert_task_reminder(task_id, f"{reminder_day} {due_time}:00")

    return task_id


def get_all_tasks(user_id):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            TASK_SELECT
            + """
            WHERE user_id = ?
            ORDER BY due_date ASC, COALESCE(due_time, '23:59') ASC
            """,
            (user_id,),
        )
        return cursor.fetchall()
    finally:
        conn.close()


def get_tasks_by_id(task_id):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(TASK_SELECT + " WHERE id = ?", (task_id,))
        return cursor.fetchone()
    finally:
        conn.close()


def get_tasks_by_date(due_date, user_id=None):
    selected = datetime.strptime(due_date, "%Y-%m-%d").date()
    today = date.today()

    conditions = [
        """
        (
            substr(due_date, 1, 10) = ?
            OR (
                carry_forward = 1
                AND is_completed = 0
                AND substr(due_date, 1, 10) < ?
            )
        )
        """
    ]
    params = [due_date, due_date]

    if user_id is not None:
        conditions.append("user_id = ?")
        params.append(user_id)

    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            TASK_SELECT
            + " WHERE "
            + " AND ".join(conditions)
            + """
            ORDER BY is_completed ASC,
                     COALESCE(due_time, '23:59') ASC,
                     id ASC
            """,
            tuple(params),
        )
        rows = cursor.fetchall()
    finally:
        conn.close()

    tasks = []
    for row in rows:
        original_due = row[4] or ""
        original_day = original_due[:10]
        is_original_day = original_day == due_date
        can_carry_to_day = (
            bool(row[9])
            and not bool(row[3])
            and original_day
            and original_day < due_date
            and selected <= today
        )

        if is_original_day or can_carry_to_day:
            tasks.append(_task_dict(row, occurrence_date=due_date))

    return tasks


def get_tasks_by_date_for_calendar(due_date, user_id=1):
    return get_tasks_by_date(due_date, user_id=user_id)


def get_all_task_dates(year=None, month=None, user_id=None):
    if year is not None and month is None and user_id is None and year < 1900:
        user_id = year
        year = None

    conditions = ["due_date IS NOT NULL", "due_date != ''"]
    params = []

    if user_id is not None:
        conditions.append("user_id = ?")
        params.append(user_id)

    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT substr(due_date, 1, 10), is_completed, carry_forward
            FROM tasks
            WHERE
            """
            + " AND ".join(conditions),
            tuple(params),
        )
        rows = cursor.fetchall()
    finally:
        conn.close()

    today = date.today()
    dates = set()

    for due_day, is_completed, carry_forward in rows:
        try:
            start = datetime.strptime(due_day, "%Y-%m-%d").date()
        except (TypeError, ValueError):
            continue

        dates.add(due_day)

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
    activity_type=None,
    category_id=None,
):
    fields = ["title = ?", "due_date = ?"]
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
        "activity_type": activity_type,
        "category_id": category_id,
    }

    for field, value in optional.items():
        if value is not None:
            fields.append(f"{field} = ?")
            values.append(value)

    values.append(task_id)

    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            f"UPDATE tasks SET {', '.join(fields)} WHERE id = ?",
            tuple(values),
        )
        conn.commit()
    finally:
        conn.close()


def delete_tasks(task_id):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM reminders WHERE task_id = ?", (task_id,))
        cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()
    finally:
        conn.close()


def search_tasks(keyword):
    term = f"%{keyword}%"
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            TASK_SELECT
            + """
            WHERE title LIKE ?
               OR due_date LIKE ?
               OR link LIKE ?
            ORDER BY due_date ASC
            """,
            (term, term, term),
        )
        return cursor.fetchall()
    finally:
        conn.close()


def set_priority(task_id, priority):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE tasks SET priority = ? WHERE id = ?",
            (priority, task_id),
        )
        conn.commit()
    finally:
        conn.close()


def set_due_date(task_id, due_date):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE tasks SET due_date = ? WHERE id = ?",
            (due_date, task_id),
        )
        conn.commit()
    finally:
        conn.close()


def set_task_completed(task_id, completed=True):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE tasks
            SET is_completed = ?,
                completed_at = CASE
                    WHEN ? = 1 THEN CURRENT_TIMESTAMP
                    ELSE NULL
                END
            WHERE id = ?
            """,
            (int(bool(completed)), int(bool(completed)), task_id),
        )

        if completed:
            cursor.execute(
                "UPDATE reminders SET is_active = 0 WHERE task_id = ?",
                (task_id,),
            )

        conn.commit()
    finally:
        conn.close()


def complete_tasks(task_id):
    set_task_completed(task_id, True)