from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager

from kivymd.app import MDApp

from screens.home_screen import HomeScreen
from screens.settings_screen import SettingsScreen


class NoteNestApp(MDApp):

    def build(self):
        self.title = "NoteNest"

        Builder.load_file("app.kv")

        sm = ScreenManager()

        sm.add_widget(HomeScreen(name="home"))
        sm.add_widget(SettingsScreen(name="settings"))

        sm.current = "home"

        return sm


if __name__ == "__main__":
    NoteNestApp().run()
