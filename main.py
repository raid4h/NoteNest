from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager
from screens.home_screen import HomeScreen
from screens.note_editor_screen import NoteEditorScreen
from widgets.note_card import NoteCard

class NotebookApp(MDApp):
    def build(self):
        Builder.load_file('app.kv')
        self.theme_cls.theme_style = 'Light'
        self.theme_cls.primary_palette = 'Green'
        sm = ScreenManager()
        sm.add_widget(HomeScreen(name='home'))
        sm.add_widget(NoteEditorScreen(name='note_editor'))
        return sm

if __name__ == '__main__':
    NotebookApp().run()
