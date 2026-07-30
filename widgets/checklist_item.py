import os
import webbrowser
from datetime import datetime

from kivy.lang import Builder
from kivy.properties import (
    BooleanProperty,
    ListProperty,
    NumericProperty,
    StringProperty,
)
from kivy.uix.boxlayout import BoxLayout


# Load the separate KV layout file.
Builder.load_file(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "kv",
        "checklist_item.kv",
    )
)


class SubChecklistItem(BoxLayout):
    """
    A single subtask row inside a checklist item.
    """

    text = StringProperty("")
    checked = BooleanProperty(False)

    def toggle(self):
        """
        Toggle the subtask between completed and incomplete.
        """

        self.checked = not self.checked


class ChecklistItem(BoxLayout):
    """
    A complete checklist task.

    It supports:
    - completion checkbox
    - category
    - priority
    - optional due date
    - optional attachment link
    - expandable subtasks
    """

    task_id = NumericProperty(0)
    text = StringProperty("")
    checked = BooleanProperty(False)

    category = StringProperty("Study")
    priority = StringProperty("High")

    # Optional information.
    # An empty string means that the field is not shown.
    due_date = StringProperty("")
    due_time = StringProperty("")
    link = StringProperty("")
    is_carried = BooleanProperty(False)
    notify_enabled = BooleanProperty(False)

    # Controls subtask visibility.
    expanded = BooleanProperty(False)

    # List of subtask text strings.
    subtasks = ListProperty([])

    CATEGORY_COLORS = {
        "Study": (0.98, 0.87, 0.85, 1),
        "Life": (0.91, 0.95, 0.87, 1),
        "Health": (0.90, 0.94, 0.98, 1),
        "Work": (0.98, 0.90, 0.90, 1),
    }

    PRIORITY_COLORS = {
        "High": (0.98, 0.92, 0.92, 1),
        "Medium": (0.98, 0.93, 0.85, 1),
        "Low": (0.91, 0.95, 0.87, 1),
    }

    PRIORITY_ORDER = ["High", "Medium", "Low"]

    def on_kv_post(self, base_widget):
        """
        Runs after the KV layout has finished loading.
        """

        self.build_subtasks()

    def on_subtasks(self, instance, value):
        """
        Rebuild the visible subtask widgets if the subtask list changes.
        """

        if "subtask_container" in self.ids:
            self.build_subtasks()

    def toggle(self):
        """
        Toggle the main task between completed and incomplete.
        """

        self.checked = not self.checked

    def toggle_expand(self):
        """
        Show or hide the subtask section.
        """

        self.expanded = not self.expanded

        container = self.ids.subtask_container
        expand_button = self.ids.expand_btn

        if self.expanded:
            container.opacity = 1
            container.height = container.minimum_height
            expand_button.text = "▼"
        else:
            container.opacity = 0
            container.height = 0
            expand_button.text = "►"

    def build_subtasks(self):
        """
        Create one SubChecklistItem widget for each subtask.
        """

        container = self.ids.subtask_container
        container.clear_widgets()

        for task_text in self.subtasks:
            item = SubChecklistItem(text=task_text)
            container.add_widget(item)

        if self.expanded:
            container.height = container.minimum_height

    def cycle_priority(self):
        """
        Change priority in this order:

        High -> Medium -> Low -> High
        """

        try:
            current_index = self.PRIORITY_ORDER.index(self.priority)
        except ValueError:
            current_index = 0

        next_index = (current_index + 1) % len(self.PRIORITY_ORDER)
        self.priority = self.PRIORITY_ORDER[next_index]

    def get_category_color(self):
        """
        Return the background color for the selected category.
        """

        return self.CATEGORY_COLORS.get(
            self.category,
            (0.95, 0.90, 0.80, 1),
        )

    def get_priority_color(self):
        """
        Return the background color for the selected priority.
        """

        return self.PRIORITY_COLORS.get(
            self.priority,
            (0.95, 0.90, 0.80, 1),
        )

    def format_due_date(self, date_value):
        """
        Convert an ISO date such as:

        2026-07-25

        into:

        July 25, 2026

        If it is already written in another format, keep it unchanged.
        """

        if not date_value:
            return ""

        try:
            parsed_date = datetime.strptime(
                date_value,
                "%Y-%m-%d",
            )

            return parsed_date.strftime("%B %d, %Y")

        except ValueError:
            return date_value


    def format_due_details(self):
        """Return a compact date/time label for the task card."""
        date_text = self.format_due_date(self.due_date)
        if self.due_time:
            date_text = f"{date_text} at {self.due_time}" if date_text else self.due_time
        if self.is_carried:
            date_text = f"{date_text} · carried forward"
        if self.notify_enabled:
            date_text = f"{date_text} · notification on"
        return date_text

    def open_link(self):
        """
        Open the attachment link in the computer's default browser.
        """

        cleaned_link = self.link.strip()

        if not cleaned_link:
            return

        # Add https:// if the user stored a link without a protocol.
        if not cleaned_link.startswith(
            ("http://", "https://")
        ):
            cleaned_link = "https://" + cleaned_link

        webbrowser.open(cleaned_link)