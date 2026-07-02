#uses note_card.py to show the list
  # its layout is defined in app.kv
# screens/home_screen.py

from kivymd.uix.screen import MDScreen
from widgets.note_card import NoteCard

class HomeScreen(MDScreen):

    sort_by = "date"   # keeps track of current sort mode

    # ─── runs every time home screen appears ───
    def on_enter(self):
        self.load_notes()

    # ─── loads and displays all notes ───
    def load_notes(self):
        # Clear whatever notes are showing right now
        self.ids.notes_list.clear_widgets()

        # ══ FAKE DATA — Week 3: replace with Person 1's get_all_notes() ══
        all_notes = [
            {"id": 1, "title": "Math Notes",    "content": "Chapter 3 covers derivatives and integrals.", "is_pinned": True,  "is_archived": False},
            {"id": 2, "title": "To-do List",    "content": "Buy groceries, call mom, submit assignment.", "is_pinned": False, "is_archived": False},
            {"id": 3, "title": "History Essay", "content": "World War II began in 1939 when Germany invaded Poland.", "is_pinned": False, "is_archived": False},
            {"id": 4, "title": "Old Draft",     "content": "This is archived and should not show here.",  "is_pinned": False, "is_archived": True},
        ]
        # ══════════════════════════════════════════════════════════════════

        # Filter out archived notes
        visible = [n for n in all_notes if not n["is_archived"]]

        # Sort pinned notes to the top, then apply date/title sort
        pinned   = [n for n in visible if n["is_pinned"]]
        unpinned = [n for n in visible if not n["is_pinned"]]

        if self.sort_by == "title":
            unpinned.sort(key=lambda n: n["title"].lower())

        # Display pinned first, then the rest
        for note in pinned + unpinned:
            card = NoteCard(
                title=note["title"],
                preview=note["content"],
                note_id=note["id"],
                is_pinned=note["is_pinned"]
            )
            self.ids.notes_list.add_widget(card)

    # ─── search: filters notes as user types ───
    def search_notes(self, query):
        # If search is empty, show all notes normally
        if query.strip() == "":
            self.load_notes()
            return

        self.ids.notes_list.clear_widgets()

        # ══ FAKE SEARCH — Week 3: replace with Person 1's search_notes(query) ══
        all_notes = [
            {"id": 1, "title": "Math Notes",    "content": "Chapter 3 covers derivatives."},
            {"id": 2, "title": "To-do List",    "content": "Buy groceries, call mom."},
            {"id": 3, "title": "History Essay", "content": "World War II began in 1939."},
        ]
        # ════════════════════════════════════════════════════════════════════════

        query_lower = query.lower()
        results = [
            n for n in all_notes
            if query_lower in n["title"].lower() or query_lower in n["content"].lower()
        ]

        for note in results:
            card = NoteCard(title=note["title"], preview=note["content"], note_id=note["id"])
            self.ids.notes_list.add_widget(card)

    # ─── sort: called from the sort buttons in app.kv ───
    def sort_notes(self, mode):
        self.sort_by = mode   # "date" or "title"
        self.load_notes()     # reload with new sort

    # ─── open editor for a new note (no id) or existing note ───
    def open_note_editor(self, note_id=None):
        editor = self.manager.get_screen("note_editor")
        editor.current_note_id = note_id
        self.manager.current = "note_editor"

    # ─── archive a note (called from a button on the note card) ───
    def archive_note(self, note_id):
        # Week 3: call Person 1's archive_note(note_id)
        print(f"Archived note {note_id}")
        self.load_notes()   # refresh the list