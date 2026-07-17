# screens/notes_screen.py
# The notes list. 

from kivymd.uix.screen import MDScreen
from widgets.note_card import NoteCard
from database.notes_queries import get_all_notes, search_notes as db_search_notes, archive_notes

from theme.theme_manager import theme_manager
from theme.themed_screen import ThemedScreenMixin
from theme.palettes import BACKGROUND, TEXT_PRIMARY, CARD_SECONDARY, ACCENT

# Week 3 TEMP: every note needs a notebook_id, but there's no notebook
# creation/selection screen yet. Using 1 as a placeholder until Tabshira
# confirms how notebooks get created (one default per user? a picker?).
DEFAULT_NOTEBOOK_ID = 1

                    #NEWLY ADDED PARAMETER
class NotesScreen(ThemedScreenMixin,MDScreen):
    sort_by = "date"

    #NEWLY ADDED CONSTANTS
    THEME_MAP = {
        "self":              ("md_bg_color", BACKGROUND),
        "top_bar":           ("md_bg_color", CARD_SECONDARY),
        "back_button":       ("icon_color", TEXT_PRIMARY),
        "header_label":      ("text_color", TEXT_PRIMARY),
        "sort_title_button": ("icon_color", TEXT_PRIMARY),
        "sort_date_button":  ("icon_color", TEXT_PRIMARY),
        "search_bar":        ("md_bg_color", BACKGROUND),
        "notes_list":        ("md_bg_color", BACKGROUND),
        "add_note_fab":      ("md_bg_color", ACCENT),
    }

    # ─── back to the dashboard ───
    def go_home(self):
        self.manager.current = "home"


    def on_enter(self):
        self.load_notes()

    def on_theme_applied(self):
        """
        THIS ALSO NEWLY ADDED METHOD
        """
        for card in self.ids.notes_list.children:
            if hasattr(card, "apply_theme"):
                card.apply_theme()

    def load_notes(self):
        self.ids.notes_list.clear_widgets()

        # get_all_notes() returns raw tuples in column order:
        # (id, notebook_id, title, content, is_pinned, is_archived,
        #  created_at, updated_at, category_id)
        all_notes = get_all_notes(DEFAULT_NOTEBOOK_ID)

        # is_archived is index 5 -- filter these out, get_all_notes()
        # doesn't do it for us
        visible = [n for n in all_notes if n[5] == 0]

        # is_pinned is index 4
        pinned = [n for n in visible if n[4] == 1]
        unpinned = [n for n in visible if n[4] == 0]

        if self.sort_by == "title":
            unpinned.sort(key=lambda n: n[2].lower())
        # "date" case needs no extra sort -- the SQL query already orders
        # by updated_at DESC

        for note in pinned + unpinned:
            card = NoteCard(
                title=note[2],           # title
                preview=note[3] or "",   # content (guard against None)
                note_id=note[0],         # id
                is_pinned=bool(note[4]),
            )
            self.ids.notes_list.add_widget(card)
            # Theme this card immediately with whatever the current
            # theme is -- it didn't exist yet the last time
            # on_theme_applied ran, so it can't wait for the next
            # theme change to look correct.
            if hasattr(card, "apply_theme"):
                card.apply_theme()

    def search_notes(self, query):
        if query.strip() == "":
            self.load_notes()
            return

        self.ids.notes_list.clear_widgets()

        # Note: db_search_notes() searches across ALL notebooks, not just
        # the current one. Fine while there's only one notebook in use --
        # revisit once real notebooks exist.
        results = db_search_notes(query)

        for note in results:
            card = NoteCard(
                title=note[2],
                preview=note[3] or "",
                note_id=note[0],
                is_pinned=bool(note[4]),
            )
            self.ids.notes_list.add_widget(card)
            if hasattr(card, "apply_theme"):
                card.apply_theme()

    def sort_notes(self, mode):
        self.sort_by = mode
        self.load_notes()

    def open_note_editor(self, note_id=None):
        editor = self.manager.get_screen("note_editor")
        editor.current_note_id = note_id
        self.manager.current = "note_editor"

    def archive_note(self, note_id):
        # is_archived column takes 0 or 1, not True/False
        archive_notes(note_id, 1)
        self.load_notes()