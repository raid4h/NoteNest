#this testing file is only for testing the themes in settings screen
from kivy.lang import Builder
from kivymd.app import MDApp
from screens.settings_screen import SettingsScreen


class SettingsTestApp(MDApp):
    def build(self):
        Builder.load_file("test.kv")
        return SettingsScreen()


if __name__ == "__main__":
    SettingsTestApp().run()
