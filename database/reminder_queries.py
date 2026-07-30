from datetime import datetime

from database.db import get_connection


def create_reminder(task_id, remind_at):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO reminders(task_id, remind_at)
        VALUES(?, ?)
        """,
        (task_id, remind_at),
    )
    reminder_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return reminder_id


def upsert_task_reminder(task_id, remind_at):
    """Keep one active reminder per task."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE reminders SET is_active=0 WHERE task_id=?",
        (task_id,),
    )
    cursor.execute(
        """
        INSERT INTO reminders(task_id, remind_at, is_active)
        VALUES(?, ?, 1)
        """,
        (task_id, remind_at),
    )
    reminder_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return reminder_id


def get_reminders_by_task(task_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, task_id, remind_at, is_active
        FROM reminders
        WHERE task_id=?
        """,
        (task_id,),
    )
    reminders = cursor.fetchall()
    conn.close()
    return reminders


def get_active_reminders():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, task_id, remind_at, is_active
        FROM reminders
        WHERE is_active=1
        ORDER BY remind_at ASC
        """
    )
    reminders = cursor.fetchall()
    conn.close()
    return reminders


def get_due_reminders():
    conn = get_connection()
    cursor = conn.cursor()
    now_value = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute(
        """
        SELECT id, task_id, remind_at, is_active
        FROM reminders
        WHERE is_active=1
          AND remind_at>=?
        ORDER BY remind_at ASC
        """,
        (now_value,),
    )
    reminders = cursor.fetchall()
    conn.close()
    return reminders


def get_triggered_reminders():
    conn = get_connection()
    cursor = conn.cursor()
    now_value = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute(
        """
        SELECT r.id, r.task_id, r.remind_at, r.is_active,
               t.title, t.due_date, t.due_time
        FROM reminders r
        JOIN tasks t ON t.id = r.task_id
        WHERE r.is_active=1
          AND r.remind_at<=?
          AND t.is_completed=0
        ORDER BY r.remind_at ASC
        """,
        (now_value,),
    )
    reminders = cursor.fetchall()
    conn.close()
    return reminders


def deactivate_reminders(reminder_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE reminders SET is_active=0 WHERE id=?",
        (reminder_id,),
    )
    conn.commit()
    conn.close()


def deactivate_task_reminders(task_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE reminders SET is_active=0 WHERE task_id=?",
        (task_id,),
    )
    conn.commit()
    conn.close()


def update_reminders(reminder_id, remind_at):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE reminders
        SET remind_at=?, is_active=1
        WHERE id=?
        """,
        (remind_at, reminder_id),
    )
    conn.commit()
    conn.close()


def delete_reminder(reminder_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM reminders WHERE id=?", (reminder_id,))
    conn.commit()
    conn.close()
