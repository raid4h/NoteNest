# one note card widget (used by home_screen)
# widgets/note_card.py

from kivymd.uix.card import MDCard
from kivy.properties import StringProperty, NumericProperty, BooleanProperty


class NoteCard(MDCard):
    title = StringProperty("Untitled")
    preview = StringProperty("")
    note_id = NumericProperty(0)
    is_pinned = BooleanProperty(False)

    # track that the touch started on this card
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self._touch_mine = True
        return super().on_touch_down(touch)

    # only open note if the tap both started and ended on this card
    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos) and getattr(self, '_touch_mine', False):
            self._touch_mine = False
            from kivymd.app import MDApp
            app = MDApp.get_running_app()
            editor = app.root.get_screen("note_editor")
            editor.current_note_id = self.note_id
            app.root.current = "note_editor"
            return True
        self._touch_mine = False
        return super().on_touch_up(touch)