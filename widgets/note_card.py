# widgets/note_card.py
from kivymd.uix.card import MDCard
from kivy.properties import StringProperty, NumericProperty, BooleanProperty

from theme.theme_manager import theme_manager
from theme.palettes import CARD_PRIMARY, TEXT_PRIMARY, TEXT_SECONDARY, ACCENT


class NoteCard(MDCard):
    title = StringProperty("Untitled")
    preview = StringProperty("")
    note_id = NumericProperty(0)
    is_pinned = BooleanProperty(False)
    last_edited = StringProperty("")
    # Multi-select support: selection_mode is set the same on every
    # card by NotesScreen when bulk-select is toggled; is_selected
    # tracks whether THIS card is currently checked.
    selection_mode = BooleanProperty(False)
    grid_mode = BooleanProperty(False)
    is_selected = BooleanProperty(False)

    def apply_theme(self):
        
        self.md_bg_color = theme_manager.get_color(CARD_PRIMARY)

        if "title_label" in self.ids:
            self.ids.title_label.text_color = theme_manager.get_color(TEXT_PRIMARY)

        if "preview_label" in self.ids:
            self.ids.preview_label.text_color = theme_manager.get_color(TEXT_SECONDARY)

        if "last_edited_label" in self.ids:
            self.ids.last_edited_label.text_color = theme_manager.get_color(TEXT_SECONDARY)

        if "pin_icon" in self.ids:
            self.ids.pin_icon.icon_color = theme_manager.get_color(ACCENT)

        if "selection_checkbox" in self.ids:
            self.ids.selection_checkbox.icon_color = theme_manager.get_color(TEXT_PRIMARY)

    def on_touch_down(self, touch):
        if "pin_icon" in self.ids and self.ids.pin_icon.collide_point(*touch.pos):
            return super().on_touch_down(touch)
        if self.collide_point(*touch.pos):
            self._touch_mine = True
        return super().on_touch_down(touch)

    def on_touch_up(self, touch):
        if "pin_icon" in self.ids and self.ids.pin_icon.collide_point(*touch.pos):
            self._touch_mine = False
            return super().on_touch_up(touch)

        if self.collide_point(*touch.pos) and getattr(self, '_touch_mine', False):
            self._touch_mine = False

            if self.selection_mode:
                # In selection mode, tapping anywhere on the card
                # toggles its checked state instead of opening it.
                self.is_selected = not self.is_selected
                self._notify_selection_changed()
                return True

            from kivymd.app import MDApp
            app = MDApp.get_running_app()
            editor = app.root.get_screen("note_editor")
            editor.current_note_id = self.note_id
            app.root.current = "note_editor"
            return True
        self._touch_mine = False
        return super().on_touch_up(touch)

    def toggle_pin(self):
        from kivymd.app import MDApp
        app = MDApp.get_running_app()
        notes_screen = app.root.get_screen("notes")
        notes_screen.toggle_pin_note(self.note_id, self.is_pinned)

    def _notify_selection_changed(self):
        from kivymd.app import MDApp
        app = MDApp.get_running_app()
        notes_screen = app.root.get_screen("notes")
        notes_screen.on_card_selection_changed(self.note_id, self.is_selected)