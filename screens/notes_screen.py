# screens/notes_screen.py
# The notes list screen. Core lifecycle + navigation lives here; list
# rendering, multi-select, and the options menu are split into
# focused mixins under screens/notes/, same pattern already used for
# the note editor screen.

from kivymd.uix.screen import MDScreen
from kivy.properties import BooleanProperty, StringProperty

from theme.theme_manager import theme_manager
from theme.themed_screen import ThemedScreenMixin
from theme.palettes import BACKGROUND, TEXT_PRIMARY, CARD_SECONDARY, ACCENT

from screens.notes.list_mixin import NotesListMixin
from screens.notes.selection_mixin import SelectionMixin
from screens.notes.options_menu_mixin import OptionsMenuMixin
import user_prefs


class NotesScreen(
    ThemedScreenMixin,
    NotesListMixin,
    SelectionMixin,
    OptionsMenuMixin,
    MDScreen,
):
    sort_by = "date"
    selection_mode = BooleanProperty(False)
    view_mode = StringProperty("list")

    THEME_MAP = {
        "self":              ("md_bg_color", BACKGROUND),
        "back_button":       ("icon_color", TEXT_PRIMARY),
        "options_button":    ("icon_color", TEXT_PRIMARY),
        "header_label":      ("text_color", TEXT_PRIMARY),
        "search_bar":        ("md_bg_color", BACKGROUND),
        "notes_list":        ("md_bg_color", BACKGROUND),
        "add_note_fab":      ("md_bg_color", ACCENT),
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Ids of notes currently checked while in bulk-select mode.
        self.selected_note_ids = set()
        # Restore whichever view mode (list/grid) the user last chose,
        # instead of always starting back at the default.
        self.view_mode = user_prefs.get_pref("view_mode")

    def go_home(self):
        self.manager.current = "home"

    def open_recently_deleted(self):
        self.manager.current = "recently_deleted"

    def on_enter(self):
        self.load_notes()

    def on_theme_applied(self):
        for card in self.ids.notes_list.children:
            if hasattr(card, "apply_theme"):
                card.apply_theme()


    def open_note_editor(self, note_id=None):
        editor = self.manager.get_screen("note_editor")
        editor.current_note_id = note_id
        self.manager.current = "note_editor"