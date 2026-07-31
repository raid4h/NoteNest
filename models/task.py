class Task:
    def __init__(
        self,
        id,
        title,
        priority,
        is_completed,
        due_date,
        user_id,
        due_time=None,
        category="Study",
        link="",
        carry_forward=1,
        notify_enabled=0,
        completed_at=None,
        category_id=None,
        activity_type="task",
    ):
        self.id = id
        self.title = title
        self.priority = priority
        self.is_completed = is_completed
        self.due_date = due_date
        self.user_id = user_id

        self.due_time = due_time
        self.category = category
        self.link = link
        self.carry_forward = carry_forward
        self.notify_enabled = notify_enabled
        self.completed_at = completed_at

        self.category_id = category_id
        self.activity_type = activity_type

    @classmethod
    def from_row(cls, row):
        """
        Build a Task from the row returned by TASK_SELECT in task_queries.py.

        Expected order:
        id, title, priority, is_completed, due_date, user_id,
        due_time, category, link, carry_forward,
        notify_enabled, completed_at, category_id, activity_type
        """
        if row is None:
            return None

        return cls(
            id=row[0],
            title=row[1],
            priority=row[2],
            is_completed=row[3],
            due_date=row[4],
            user_id=row[5],
            due_time=row[6] if len(row) > 6 else None,
            category=row[7] if len(row) > 7 and row[7] else "Study",
            link=row[8] if len(row) > 8 and row[8] else "",
            carry_forward=row[9] if len(row) > 9 else 1,
            notify_enabled=row[10] if len(row) > 10 else 0,
            completed_at=row[11] if len(row) > 11 else None,
            category_id=row[12] if len(row) > 12 else None,
            activity_type=(
                row[13]
                if len(row) > 13 and row[13]
                else "task"
            ),
        )