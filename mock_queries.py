# Mock task data — replace with real DB queries on integration day

MOCK_TASKS = [
    {
        "id": 1,
        "title": "Submit CSE299 report",
        "due_date": "2026-07-05",
        "priority": "High",
        "category": "Study",
        "completed": False,
        "subtasks": ["Write introduction", "Add diagrams", "Proofread"]
    },
    {
        "id": 2,
        "title": "Buy groceries",
        "due_date": "2026-07-05",
        "priority": "Low",
        "category": "Life",
        "completed": False,
        "subtasks": ["Milk", "Bread", "Eggs"]
    },
    {
        "id": 3,
        "title": "Read lecture slides",
        "due_date": "2026-07-07",
        "priority": "Medium",
        "category": "Study",
        "completed": False,
        "subtasks": ["Chapter 1", "Chapter 2", "Chapter 3"]
    },
    {
        "id": 4,
        "title": "Walk the dog",
        "due_date": "2026-07-10",
        "priority": "Low",
        "category": "Health",
        "completed": False,
        "subtasks": []
    },
    {
        "id": 5,
        "title": "Team meeting",
        "due_date": "2026-07-12",
        "priority": "High",
        "category": "Work",
        "completed": False,
        "subtasks": ["Prepare slides", "Send agenda"]
    },
    {
        "id": 6,
        "title": "Pay tuition fees",
        "due_date": "2026-07-15",
        "priority": "High",
        "category": "Life",
        "completed": False,
        "subtasks": ["Check bank balance", "Log into portal"]
    },
]


def get_tasks_by_date(date_str):
    return [t for t in MOCK_TASKS if t["due_date"] == date_str]


def get_all_task_dates():
    return list(set(t["due_date"] for t in MOCK_TASKS))