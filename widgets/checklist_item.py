import os
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, BooleanProperty, ListProperty
from kivy.lang import Builder

Builder.load_file(os.path.join(os.path.dirname(__file__), '..', 'kv', 'checklist_item.kv'))


class SubChecklistItem(BoxLayout):
    """A single subtask row inside a checklist item."""
    text = StringProperty("")
    checked = BooleanProperty(False)

    def toggle(self):
        self.checked = not self.checked


class ChecklistItem(BoxLayout):
    text = StringProperty("")
    checked = BooleanProperty(False)
    category = StringProperty("Study")
    priority = StringProperty("High")
    expanded = BooleanProperty(False)  # controls subtask visibility
    subtasks = ListProperty([])        # list of subtask text strings

    CATEGORY_COLORS = {
        "Study":  (0.98, 0.87, 0.85, 1),
        "Life":   (0.91, 0.95, 0.87, 1),
        "Health": (0.90, 0.94, 0.98, 1),
        "Work":   (0.98, 0.90, 0.90, 1),
    }

    PRIORITY_COLORS = {
        "High":   (0.98, 0.92, 0.92, 1),
        "Medium": (0.98, 0.93, 0.85, 1),
        "Low":    (0.91, 0.95, 0.87, 1),
    }

    PRIORITY_ORDER = ["High", "Medium", "Low"]

    def on_kv_post(self, base_widget):
        """Called after kv is loaded — build subtask widgets."""
        self.build_subtasks()

    def toggle(self):
        """Toggle main task checked state."""
        self.checked = not self.checked

    def toggle_expand(self):
        """Show or hide subtasks."""
        self.expanded = not self.expanded
        self.ids.subtask_container.opacity = 1 if self.expanded else 0
        self.ids.subtask_container.size_hint_y = None if self.expanded else None
        self.ids.subtask_container.height = self.ids.subtask_container.minimum_height if self.expanded else 0
        self.ids.expand_btn.text = "▼" if self.expanded else "►"

    def build_subtasks(self):
        """Add SubChecklistItem widgets for each subtask."""
        self.ids.subtask_container.clear_widgets()
        for task_text in self.subtasks:
            item = SubChecklistItem(text=task_text)
            self.ids.subtask_container.add_widget(item)

    def cycle_priority(self):
        current = self.PRIORITY_ORDER.index(self.priority)
        self.priority = self.PRIORITY_ORDER[(current + 1) % 3]

    def get_category_color(self):
        return self.CATEGORY_COLORS.get(self.category, (0.95, 0.90, 0.80, 1))

    def get_priority_color(self):
        return self.PRIORITY_COLORS.get(self.priority, (0.95, 0.90, 0.80, 1))