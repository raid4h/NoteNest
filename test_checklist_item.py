from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle
from widgets.checklist_item import ChecklistItem

Window.clearcolor = (0.97, 0.95, 0.91, 1)
Window.size = (400, 680)


class TestApp(App):
    def build(self):
        root = BoxLayout(orientation="vertical", padding=[16, 20, 16, 20], spacing=16)

        # Title
        title = Label(
            text="My Checklist",
            font_size="22sp",
            bold=True,
            color=(0.15, 0.10, 0.05, 1),
            halign="left",
            size_hint_y=None,
            height=40
        )
        title.bind(size=title.setter("text_size"))
        root.add_widget(title)

        # Checklist items
        list_layout = BoxLayout(
            orientation="vertical",
            spacing=10,
            size_hint_y=None
        )
        list_layout.bind(minimum_height=list_layout.setter("height"))

        items = [
            ("Finish CSE299 report", "Study"),
            ("Buy groceries",        "Life"),
            ("Walk the dog",         "Health"),
            ("Read lecture slides",  "Study"),
            ("Submit assignment",    "Work"),
        ]
        for text, tag in items:
            list_layout.add_widget(ChecklistItem(text=text, tag=tag))

        scroll = ScrollView()
        scroll.add_widget(list_layout)
        root.add_widget(scroll)

        return root


TestApp().run()