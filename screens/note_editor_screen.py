#lets user write/edit a note
  #its layout is defined in app.kv
# screens/note_editor_screen.py

from kivymd.uix.screen import MDScreen

class NoteEditorScreen(MDScreen):

    current_note_id = None  # None = new note, a number = editing existing note

    # ─── runs when this screen opens ───
    def on_enter(self):
        if self.current_note_id is not None:
            self.load_note(self.current_note_id)
        # if current_note_id is None, the fields stay empty = new note

    # ─── load an existing note into the text fields ───
    def load_note(self, note_id):
        # ══ FAKE DATA — Week 3: replace with Person 1's get_note(note_id) ══
        fake_notes = {
            1: {"title": "Math Notes",    "content": "Chapter 3 covers derivatives and integrals."},
            2: {"title": "To-do List",    "content": "Buy groceries, call mom, submit assignment."},
            3: {"title": "History Essay", "content": "World War II began in 1939."},
        }
        note = fake_notes.get(note_id, {"title": "", "content": ""})
        # ════════════════════════════════════════════════════════════════════

        self.ids.title_field.text   = note["title"]
        self.ids.content_field.text = note["content"]

    # ─── save the note ───
    def save_note(self):
        title   = self.ids.title_field.text.strip()
        content = self.ids.content_field.text.strip()

        # Don't save if title is empty
        if not title:
            print("Please add a title")
            # Week 3: show a popup dialog here instead of print
            return

        if self.current_note_id is None:
            # It's a brand new note
            # Week 3: Person 1's create_note(title, content)
            print(f"Creating new note: '{title}'")
        else:
            # It's an edit to an existing note
            # Week 3: Person 1's update_note(self.current_note_id, title, content)
            print(f"Updating note {self.current_note_id}: '{title}'")

        self.go_back()

    # ─── delete the note ───
    def delete_note(self):
        if self.current_note_id is not None:
            # Week 3: Person 1's delete_note(self.current_note_id)
            print(f"Deleted note {self.current_note_id}")
        self.go_back()

    # ─── duplicate the note ───
    def duplicate_note(self):
        title   = self.ids.title_field.text.strip()
        content = self.ids.content_field.text.strip()

        if not title:
            return

        # Week 3: Person 1's create_note(title + " (copy)", content)
        print(f"Duplicated note: '{title} (copy)'")
        self.go_back()

    # ─── go back to home screen, reset everything ───
    def go_back(self):
        # Clear the fields for next time
        self.ids.title_field.text   = ""
        self.ids.content_field.text = ""
        self.current_note_id = None

        # Go back to home (on_enter will reload the note list)
        self.manager.current = "home"