from kivy.uix.button import Button
from kivy.properties import StringProperty


class PriorityBadge(Button):
    priority = StringProperty("Medium")

    COLORS = {
        "High":   (0.9, 0.2, 0.2, 1),
        "Medium": (0.95, 0.6, 0.1, 1),
        "Low":    (0.2, 0.75, 0.3, 1),
    }
    ORDER = ["High", "Medium", "Low"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (100, 36)
        self.font_size = 14
        self.bold = True
        self.background_normal = ""
        self.update_badge()
        self.bind(on_press=self.cycle_priority)

    def update_badge(self):
        self.text = self.priority
        self.background_color = self.COLORS[self.priority]

    def cycle_priority(self, instance):
        current = self.ORDER.index(self.priority)
        next_index = (current + 1) % len(self.ORDER)
        self.priority = self.ORDER[next_index]
        self.update_badge()