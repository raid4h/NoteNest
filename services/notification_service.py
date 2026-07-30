"""Small foreground reminder service for NoteNest."""

from database.reminder_queries import (
    deactivate_reminders,
    get_triggered_reminders,
)


def collect_due_notifications():
    """
    Return due notifications and atomically deactivate each reminder.

    The UI polls this function with Kivy Clock. Deactivation prevents the same
    reminder from appearing more than once.
    """
    notifications = []
    for row in get_triggered_reminders():
        reminder_id, task_id, remind_at, _, title, due_date, due_time = row
        deactivate_reminders(reminder_id)
        notifications.append(
            {
                "reminder_id": reminder_id,
                "task_id": task_id,
                "title": title,
                "remind_at": remind_at,
                "due_date": due_date,
                "due_time": due_time,
            }
        )
    return notifications


def send_system_notification(title, message):
    """
    Use a native notification when Plyer is available.

    Returns False on desktop/development environments without Plyer so the
    caller can display an in-app popup instead.
    """
    try:
        from plyer import notification

        notification.notify(
            title=title,
            message=message,
            app_name="NoteNest",
            timeout=10,
        )
        return True
    except Exception:
        return False
