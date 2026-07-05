from kivy.app import App
from kivy.core.window import Window
from screens.calendar_screen import CalendarScreen

Window.clearcolor = (0.96, 0.93, 0.86, 1)
Window.size = (400, 650)


class TestApp(App):
    def build(self):
        return CalendarScreen()


TestApp().run()