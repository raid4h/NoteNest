from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from widgets.checklist_item import ChecklistItem

Window.clearcolor = (0.97, 0.95, 0.90, 1)
Window.size = (400, 650)


class TestApp(App):
    def build(self):
        layout = BoxLayout(
            orientation="vertical",
            padding=20,
            spacing=10,
            size_hint_y=None
        )
        layout.bind(minimum_height=layout.setter("height"))

        items = [
            ("Finish CSE299 report", "Study", "High",
             ["Write introduction", "Add diagrams", "Proofread"]),
            ("Buy groceries", "Life", "Low",
             ["Milk", "Bread", "Eggs"]),
            ("Walk the dog", "Health", "Medium", []),
            ("Read lecture slides", "Study", "High",
             ["Chapter 1", "Chapter 2"]),
            ("Submit assignment", "Work", "Medium", []),
        ]

        for text, category, priority, subtasks in items:
            layout.add_widget(ChecklistItem(
                text=text,
                category=category,
                priority=priority,
                subtasks=subtasks
            ))

        scroll = ScrollView()
        scroll.add_widget(layout)
        return scroll


TestApp().run()