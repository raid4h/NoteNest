from datetime import datetime, timedelta
from services.notification_service import (
    create_reminder,
    schedule_reminder,
    snooze_reminder,
    get_all_reminders,
    escalate_priority,
    cluster_reminders,
    overdue_shame_alert
)
from mock_queries import MOCK_TASKS

print("=" * 40)
print("NOTIFICATION SERVICE TEST")
print("=" * 40)

# Trump Card 3 — Overdue Shame Alert
print("\n--- OVERDUE SHAME ALERT ---")
overdue_shame_alert(MOCK_TASKS)

# Trump Card 1 — Priority Escalation
print("\n--- PRIORITY ESCALATION ---")
escalate_priority(MOCK_TASKS)

# Trump Card 2 — Reminder Clustering
print("\n--- REMINDER CLUSTERING ---")
remind_time = datetime.now() + timedelta(seconds=5)
cluster_reminders(MOCK_TASKS, remind_time)

# Basic reminder + snooze
print("\n--- BASIC REMINDER + SNOOZE ---")
r = create_reminder("Walk the dog", datetime.now() + timedelta(seconds=3))
schedule_reminder(r)
snooze_reminder(r["id"], minutes=1)

# Show all reminders that i created
print("\n--- ALL REMINDERS ---")
for r in get_all_reminders():
    print(f"  [{r['status']}] {r['task_title']}")