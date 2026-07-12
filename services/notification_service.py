from datetime import datetime, timedelta
import threading


# ─────────────────────────────────────────────────────
# In-memory reminder store (mock — replace with DB later)
# ─────────────────────────────────────────────────────
_reminders = []
_next_id = 1


# ──────────────────────────────
# CORE FUNCTIONS
# ──────────────────────────────

def create_reminder(task_title, remind_at, task_id=None, priority="Medium"):
    """
    Create a new reminder and store it.
    task_title : name of the task
    remind_at  : datetime object for when to fire
    task_id    : optional link to real DB task
    priority   : "High", "Medium", or "Low"
    """
    global _next_id

    reminder = {
        "id":         _next_id,
        "task_id":    task_id,
        "task_title": task_title,
        "remind_at":  remind_at,
        "priority":   priority,
        "status":     "pending",  # pending | triggered | snoozed
        "created_at": datetime.now(),
    }
    _reminders.append(reminder)
    _next_id += 1

    print(f"[✓ Created] '{task_title}' → {remind_at.strftime('%Y-%m-%d %H:%M')}")
    return reminder


def schedule_reminder(reminder):
    """
    Schedule a reminder to fire at its remind_at time.
    Uses a background thread so the app doesn't freeze.
    """
    now = datetime.now()
    delay = (reminder["remind_at"] - now).total_seconds()

    if delay <= 0:
        # Already overdue — fire immediately
        trigger_reminder(reminder["id"])
        return

    # Background timer — fires after delay seconds
    timer = threading.Timer(delay, trigger_reminder, args=[reminder["id"]])
    timer.daemon = True  # stops automatically when app closes
    timer.start()

    print(f"[⏰ Scheduled] '{reminder['task_title']}' fires in {int(delay)}s")


def trigger_reminder(reminder_id):
    """
    Fire a reminder — update status and print alert.
    In a real app this would push a phone notification.
    """
    reminder = get_reminder_by_id(reminder_id)
    if not reminder:
        return

    reminder["status"] = "triggered"

    print(f"\n{'='*40}")
    print(f"🔔 REMINDER FIRED")
    print(f"   Task     : {reminder['task_title']}")
    print(f"   Priority : {reminder['priority']}")
    print(f"   Due      : {reminder['remind_at'].strftime('%Y-%m-%d %H:%M')}")
    print(f"{'='*40}\n")


def snooze_reminder(reminder_id, minutes=10):
    """
    Snooze a reminder by pushing it forward X minutes.
    Default is 10 minutes.
    """
    reminder = get_reminder_by_id(reminder_id)
    if not reminder:
        print(f"[Error] Reminder {reminder_id} not found")
        return

    reminder["remind_at"] = reminder["remind_at"] + timedelta(minutes=minutes)
    reminder["status"] = "snoozed"

    print(f"[💤 Snoozed] '{reminder['task_title']}' pushed by {minutes} mins")
    schedule_reminder(reminder)


# ──────────────────────────────
# TRUMP CARD FEATURE 1
# Smart Priority Escalation
# ──────────────────────────────

def escalate_priority(tasks):
    """
    Automatically bumps up priority if a task is due within 24 hours.
    Low → Medium → High
    Called when the app opens or on a schedule.

    tasks: list of task dicts with "title", "due_date", "priority" keys
    """
    ORDER = ["Low", "Medium", "High"]
    escalated = []

    for task in tasks:
        due = datetime.strptime(task["due_date"], "%Y-%m-%d")
        hours_left = (due - datetime.now()).total_seconds() / 3600

        if hours_left <= 24 and task["priority"] != "High":
            old = task["priority"]
            # Bump up one level
            idx = ORDER.index(old)
            task["priority"] = ORDER[min(idx + 1, 2)]
            escalated.append(task)

            print(f"[⬆ Escalated] '{task['title']}' {old} → {task['priority']} "
                  f"(due in {int(hours_left)}h)")

    if not escalated:
        print("[✓ Priority check] No escalations needed")

    return escalated


# ──────────────────────────────
# TRUMP CARD FEATURE 2
# Smart Reminder Clustering
# ──────────────────────────────

def cluster_reminders(tasks, remind_at):
    """
    Instead of firing one reminder per task,
    groups all tasks due on the same day into ONE reminder.

    tasks     : list of task dicts
    remind_at : datetime for when to fire the cluster
    """
    # Group tasks by due date
    clusters = {}
    for task in tasks:
        date = task["due_date"]
        if date not in clusters:
            clusters[date] = []
        clusters[date].append(task["title"])

    # Create one reminder per date cluster
    created = []
    for date, titles in clusters.items():
        if len(titles) == 1:
            # Only one task — normal reminder
            summary = titles[0]
        else:
            # Multiple tasks — combine into one message
            summary = f"{len(titles)} tasks due: " + ", ".join(titles)

        r = create_reminder(
            task_title=summary,
            remind_at=remind_at,
            priority="High" if len(titles) > 2 else "Medium"
        )
        schedule_reminder(r)
        created.append(r)

    return created


# ──────────────────────────────
# TRUMP CARD FEATURE 3
# Overdue Shame Alert
# ──────────────────────────────

def overdue_shame_alert(tasks):
    """
    Called when the app opens.
    Immediately fires alerts for any tasks past their due date.
    No hiding from overdue tasks.

    tasks: list of task dicts with "title", "due_date", "priority"
    """
    overdue = []

    for task in tasks:
        due = datetime.strptime(task["due_date"], "%Y-%m-%d")
        if datetime.now() > due:
            overdue.append(task)

    if not overdue:
        print("[✓ All clear] No overdue tasks!")
        return []

    print(f"\n{'!'*40}")
    print(f"⚠️  OVERDUE ALERT — {len(overdue)} task(s) past due!")
    for task in overdue:
        days_late = (datetime.now() - datetime.strptime(task["due_date"], "%Y-%m-%d")).days
        print(f"   ✗ {task['title']} — {days_late} day(s) overdue [{task['priority']}]")
    print(f"{'!'*40}\n")

    return overdue


# ──────────────────────────────
# HELPER FUNCTIONS
# ──────────────────────────────

def get_all_reminders():
    """Return all reminders."""
    return _reminders


def get_reminder_by_id(reminder_id):
    """Find a reminder by ID. Returns None if not found."""
    for r in _reminders:
        if r["id"] == reminder_id:
            return r
    return None


def get_pending_reminders():
    """Return only reminders that haven't fired yet."""
    return [r for r in _reminders if r["status"] == "pending"]