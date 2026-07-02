import os
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, BooleanProperty
from kivy.lang import Builder

Builder.load_file(os.path.join(os.path.dirname(__file__), '..', 'kv', 'checklist_item.kv'))


class ChecklistItem(BoxLayout):
    text = StringProperty("")
    checked = BooleanProperty(False)
    category = StringProperty("Study")
    priority = StringProperty("High")

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

    def toggle(self):
        self.checked = not self.checked

    def cycle_priority(self):
        current = self.PRIORITY_ORDER.index(self.priority)
        self.priority = self.PRIORITY_ORDER[(current + 1) % 3]

    def get_category_color(self):
        return self.CATEGORY_COLORS.get(self.category, (0.95, 0.90, 0.80, 1))

    def get_priority_color(self):
        return self.PRIORITY_COLORS.get(self.priority, (0.95, 0.90, 0.80, 1))