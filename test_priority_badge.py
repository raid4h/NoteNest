from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
from widgets.priority_badge import PriorityBadge

Window.clearcolor = (0.97, 0.95, 0.90, 1)
Window.size = (400, 400)


class TestApp(App):
    def build(self):
        layout = BoxLayout(
            orientation="vertical",
            padding=40,
            spacing=20
        )
        layout.add_widget(PriorityBadge(priority="High"))
        layout.add_widget(PriorityBadge(priority="Medium"))
        layout.add_widget(PriorityBadge(priority="Low"))
        return layout


TestApp().run()