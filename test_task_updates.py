import os
import tempfile
import unittest
from datetime import date, timedelta

import database.db as db
from database.task_queries import (
    create_tasks,
    get_all_task_dates,
    get_tasks_by_date,
    set_task_completed,
)
from services.notification_service import collect_due_notifications


class TaskFeatureTests(unittest.TestCase):
    def setUp(self):
        file_descriptor, self.db_path = tempfile.mkstemp(suffix=".db")
        os.close(file_descriptor)
        self.original_db_name = db.DB_NAME
        db.DB_NAME = self.db_path
        db.create_tables()

    def tearDown(self):
        db.DB_NAME = self.original_db_name
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_unfinished_task_carries_to_today_then_stops(self):
        yesterday = (date.today() - timedelta(days=1)).isoformat()
        today = date.today().isoformat()
        task_id = create_tasks(
            "Submit report",
            1,
            due_date=yesterday,
            due_time="09:00",
            carry_forward=True,
        )

        carried = [
            task
            for task in get_tasks_by_date(today)
            if task["id"] == task_id
        ]
        self.assertTrue(carried)
        self.assertTrue(carried[0]["is_carried"])
        self.assertIn(today, get_all_task_dates())

        set_task_completed(task_id, True)
        self.assertFalse(
            any(task["id"] == task_id for task in get_tasks_by_date(today))
        )

    def test_link_and_notification_are_stored_and_fire_once(self):
        yesterday = (date.today() - timedelta(days=1)).isoformat()
        task_id = create_tasks(
            "Open course page",
            1,
            due_date=yesterday,
            due_time="00:01",
            link="https://example.com/course",
            notify_enabled=True,
            carry_forward=False,
        )

        task = next(
            item
            for item in get_tasks_by_date(yesterday)
            if item["id"] == task_id
        )
        self.assertEqual(task["link"], "https://example.com/course")

        notifications = collect_due_notifications()
        self.assertTrue(
            any(item["task_id"] == task_id for item in notifications)
        )
        self.assertEqual(collect_due_notifications(), [])


if __name__ == "__main__":
    unittest.main()
