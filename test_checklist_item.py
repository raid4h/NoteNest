from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from widgets.checklist_item import ChecklistItem
from widgets.category_chip import CategoryChip

Window.clearcolor = (0.97, 0.95, 0.90, 1)
Window.size = (400, 650)

ITEMS = [
    ("Finish CSE299 report", "Study", "High",
     ["Write introduction", "Add diagrams", "Proofread"]),
    ("Buy groceries", "Life", "Low",
     ["Milk", "Bread", "Eggs"]),
    ("Walk the dog", "Health", "Medium", []),
    ("Read lecture slides", "Study", "High",
     ["Chapter 1", "Chapter 2"]),
    ("Submit assignment", "Work", "Medium", []),
]


class TestApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.active_category = "All"
        self.chips = {}

    def build(self):
        # Outer layout
        self.outer = BoxLayout(
            orientation="vertical",
            padding=20,
            spacing=10
        )

        # Category chip row
        chip_row = BoxLayout(
            orientation="horizontal",
            spacing=10,
            size_hint_y=None,
            height=50
        )
        for category in ["All", "Study", "Life", "Health", "Work"]:
            chip = CategoryChip(category=category)
            chip.on_select = self.on_chip_selected
            self.chips[category] = chip
            chip_row.add_widget(chip)

        # Select "All" by default
        self.chips["All"].selected = True
        self.chips["All"].update_style()

        # Task list
        self.task_layout = BoxLayout(
            orientation="vertical",
            spacing=10,
            size_hint_y=None
        )
        self.task_layout.bind(
            minimum_height=self.task_layout.setter("height")
        )

        self.scroll = ScrollView()
        self.scroll.add_widget(self.task_layout)

        self.outer.add_widget(chip_row)
        self.outer.add_widget(self.scroll)

        # Show all tasks at start
        self.filter_tasks("All")

        return self.outer

    def on_chip_selected(self, category, selected):
        # Deselect all other chips
        for cat, chip in self.chips.items():
            if cat != category:
                chip.deselect()

        # Always keep one selected
        if not selected:
            self.chips[category].selected = True
            self.chips[category].update_style()
            return

        self.active_category = category
        self.filter_tasks(category)

    def filter_tasks(self, category):
        """Show only tasks matching the selected category."""
        self.task_layout.clear_widgets()

        for text, cat, priority, subtasks in ITEMS:
            if category == "All" or cat == category:
                self.task_layout.add_widget(ChecklistItem(
                    text=text,
                    category=cat,
                    priority=priority,
                    subtasks=subtasks
                ))


TestApp().run()