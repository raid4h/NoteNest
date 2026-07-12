from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager
from kivymd.app import MDApp
from screens.home_screen import HomeScreen
from screens.notes_screen import NotesScreen
from screens.note_editor_screen import NoteEditorScreen
from screens.settings_screen import SettingsScreen
from screens.timer_screen import TimerScreen
from screens.calendar_screen import CalendarScreen # Amattullah's update


class NoteNestApp(MDApp):
    def build(self):
        self.title = "NoteNest"
        Builder.load_file("app.kv")
        Builder.load_file("settings_screen.kv")
        Builder.load_file("timer_screen.kv")

        sm = ScreenManager()
        sm.add_widget(HomeScreen(name="home"))
        sm.add_widget(NotesScreen(name="notes"))
        sm.add_widget(NoteEditorScreen(name="note_editor"))
        sm.add_widget(SettingsScreen(name="settings"))
        sm.add_widget(TimerScreen(name="timer"))
        sm.add_widget(CalendarScreen(name="calendar"))
        sm.current = "home"
        return sm


if __name__ == "__main__":
    NoteNestApp().run()