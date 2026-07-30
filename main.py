from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager
from kivymd.app import MDApp
from screens.home_screen import HomeScreen
from screens.notes_screen import NotesScreen
from screens.note_editor_screen import NoteEditorScreen
from screens.settings_screen import SettingsScreen
from screens.timer_screen import TimerScreen
from screens.calendar_screen import CalendarScreen 
from database.db import create_tables
from screens.recently_deleted_screen import RecentlyDeletedScreen
from kivy.core.window import Window

# Tells Kivy to automatically resize the app's visible area so whatever
# text field currently has focus stays visible above the on-screen
# keyboard, instead of the keyboard covering it. Does nothing on
# desktop (there's no real on-screen keyboard here to trigger it) --
# this only takes effect once running on an actual Android device or
# emulator.
Window.softinput_mode = "below_target"


class NoteNestApp(MDApp):
    def build(self):
        create_tables() 
        self.title = "NoteNest"
        Builder.load_file("home_screen.kv")  # Tabshira: DashboardTile, SmallTile, Streak, HomeScreen
        Builder.load_file("notes.kv")  # Raidah: NoteCard, AttachmentThumbnail, NotesScreen, NoteEditorScreen, FormattingToolbar, RecentlyDeletedScreen
        Builder.load_file("settings_screen.kv")
        Builder.load_file("timer_screen.kv")

        sm = ScreenManager()
        sm.add_widget(HomeScreen(name="home"))
        sm.add_widget(NotesScreen(name="notes"))
        sm.add_widget(NoteEditorScreen(name="note_editor"))
        sm.add_widget(RecentlyDeletedScreen(name="recently_deleted"))
        sm.add_widget(SettingsScreen(name="settings"))
        sm.add_widget(TimerScreen(name="timer"))
        sm.add_widget(CalendarScreen(name="calendar"))
        sm.current = "home"
        return sm


if __name__ == "__main__":
    NoteNestApp().run()
