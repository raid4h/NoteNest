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
