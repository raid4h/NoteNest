# screens/notes/list_mixin.py
# Loading, searching, sorting, and rendering the notes list in either
# list or grid layout. Also owns pin/archive, since both just mutate
# a note then reload this same list.

from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout

from widgets.note_card import NoteCard
from database.notes_queries import get_all_notes, search_notes as db_search_notes, archive_notes, pin_notes
from screens.notes.helpers import format_last_edited, clean_preview_text

DEFAULT_NOTEBOOK_ID = 1
GRID_ROW_HEIGHT = dp(180)


class NotesListMixin:
    """Requires: self.ids.notes_list, self.sort_by, self.view_mode,
    self.selection_mode, self.selected_note_ids."""

    def load_notes(self):
        all_notes = get_all_notes(DEFAULT_NOTEBOOK_ID)
        visible = [n for n in all_notes if n[5] == 0]
        pinned = [n for n in visible if n[4] == 1]
        unpinned = [n for n in visible if n[4] == 0]
        if self.sort_by == "title":
            unpinned.sort(key=lambda n: n[2].lower())
        self._populate_notes_list(pinned + unpinned)

    def search_notes(self, query):
        if query.strip() == "":
            self.load_notes()
            return
        results = db_search_notes(query)
        self._populate_notes_list(results)

    def _build_note_card(self, note, grid_mode=False):
        return NoteCard(
            title=note[2],
            preview=clean_preview_text(note[3]),
            note_id=note[0],
            is_pinned=bool(note[4]),
            last_edited=format_last_edited(note[7]),
            selection_mode=self.selection_mode,
            is_selected=note[0] in self.selected_note_ids,
            grid_mode=grid_mode,
        )

    def _populate_notes_list(self, notes):
        self.ids.notes_list.clear_widgets()

        if self.view_mode == "list":
            for note in notes:
                card = self._build_note_card(note, grid_mode=False)
                self.ids.notes_list.add_widget(card)
                if hasattr(card, "apply_theme"):
                    card.apply_theme()
        else:
            for i in range(0, len(notes), 2):
                row = BoxLayout(
                    orientation="horizontal", size_hint_y=None,
                    height=GRID_ROW_HEIGHT, spacing=dp(10),
                )
                for note in notes[i:i + 2]:
                    card = self._build_note_card(note, grid_mode=True)
                    row.add_widget(card)
                    if hasattr(card, "apply_theme"):
                        card.apply_theme()
                self.ids.notes_list.add_widget(row)

    def toggle_view_mode(self):
        self.view_mode = "grid" if self.view_mode == "list" else "list"
        self.load_notes()

    def sort_notes(self, mode):
        self.sort_by = mode
        self.load_notes()

    def archive_note(self, note_id):
        archive_notes(note_id, 1)
        self.load_notes()

    def toggle_pin_note(self, note_id, is_pinned):
        new_value = 0 if is_pinned else 1
        pin_notes(note_id, new_value)
        self.load_notes()