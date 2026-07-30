from kivy.properties import StringProperty, BooleanProperty
from kivymd.uix.boxlayout import MDBoxLayout


class Streak(MDBoxLayout):
    day_letter = StringProperty("")
    is_active = BooleanProperty(False)

    def apply_theme(self, active_color, inactive_color, text_color):
        if "dot" in self.ids:
            self.ids.dot.md_bg_color = active_color if self.is_active else inactive_color
        if "day_label" in self.ids:
            self.ids.day_label.text_color = text_color
        