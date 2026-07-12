# screens/note_editor_screen.py
import os
import re
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivymd.uix.screen import MDScreen
from plyer import filechooser

from database.notes_queries import (
    get_notes_by_id, create_notes, update_notes, delete_notes, duplicate_notes,
)
from database.attachment_queries import create_attachment

DEFAULT_NOTEBOOK_ID = 1

# Matches an inline image marker in note content, e.g.
# {{img:C:/Users/raida/Pictures/photo.jpg}}
IMAGE_TOKEN_PATTERN = re.compile(r"\{\{img:(.*?)\}\}")


class NoteEditorScreen(MDScreen):
    current_note_id = None
    is_preview = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Built once here in Python, NOT in KV. This lets us fully add/remove
        # these from the screen when toggling preview, instead of just hiding
        # them with opacity -- which is what caused typing to break, since
        # ScrollView keeps intercepting touches even when "disabled".
        self._preview_content = BoxLayout(
            orientation="vertical", size_hint_y=None, spacing=dp(8)
        )
        self._preview_content.bind(minimum_height=self._preview_content.setter("height"))

        self._preview_scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False)
        self._preview_scroll.add_widget(self._preview_content)

    def on_enter(self):
        self.is_preview = False
        if self.current_note_id is not None:
            self.load_note(self.current_note_id)
        else:
            self.ids.title_field.text = ""
            self.ids.content_field.text = ""
        self.show_edit_mode()

    def load_note(self, note_id):
        note = get_notes_by_id(note_id)
        if note is None:
            self.ids.title_field.text = ""
            self.ids.content_field.text = ""
            return
        self.ids.title_field.text = note[2]
        self.ids.content_field.text = note[3] or ""

    # ─── image picking ───
    def pick_image(self):
        if self.current_note_id is None:
            # Now that create_notes() returns a real id, save the note on
            # the spot instead of blocking the user with an error message.
            title = self.ids.title_field.text.strip() or "Untitled"
            content = self.ids.content_field.text
            self.current_note_id = create_notes(DEFAULT_NOTEBOOK_ID, title, content)
            if not self.ids.title_field.text.strip():
                self.ids.title_field.text = title

        # Windows' native file dialog silently changes the working directory
        # to match wherever you picked a file from, which breaks the
        # database's relative path. Save it here, restore it right after.
        self._cwd_before_picker = os.getcwd()

        filechooser.open_file(
            on_selection=self.on_image_selected,
            filters=[["Images", "*.png", "*.jpg", "*.jpeg"]],
        )

    def on_image_selected(self, selection):
        os.chdir(self._cwd_before_picker)
        # The picker callback can run on a different thread; schedule the
        # actual widget update on Kivy's main thread instead.
        Clock.schedule_once(lambda dt: self._insert_image_token(selection))

    def _insert_image_token(self, selection):
        if not selection:
            return
        file_path = selection[0]
        create_attachment(self.current_note_id, file_path)

        token = f"{{{{img:{file_path}}}}}"
        field = self.ids.content_field
        try:
            field.insert_text(token)
        except AttributeError:
            # Fallback if this KivyMD build's MDTextField doesn't expose
            # insert_text() directly -- adds to the end instead of the
            # cursor, but keeps things working either way.
            field.text = field.text + ("\n" if field.text else "") + token

    # ─── Edit / Preview toggle ───
    def toggle_preview(self):
        self.is_preview = not self.is_preview
        if self.is_preview:
            self.show_preview_mode()
        else:
            self.show_edit_mode()

    def show_edit_mode(self):
        container = self.ids.content_container
        if self._preview_scroll.parent is not None:
            container.remove_widget(self._preview_scroll)
        if self.ids.content_field.parent is None:
            container.add_widget(self.ids.content_field)

    def show_preview_mode(self):
        raw = self.ids.content_field.text
        self._preview_content.clear_widgets()

        # Splitting on the token pattern gives alternating text/image-path
        # pieces: [text, path, text, path, ..., text]. Even indices are
        # plain text, odd indices are image file paths.
        parts = IMAGE_TOKEN_PATTERN.split(raw)

        for i, part in enumerate(parts):
            if i % 2 == 1:
                img = Image(
                    source=part,
                    size_hint=(None, None),
                    size=(dp(220), dp(220)),
                    allow_stretch=True,
                )
                self._preview_content.add_widget(img)
            elif part.strip():
                label = Label(
                    text=part,
                    size_hint_y=None,
                    color=(0.29, 0.20, 0.15, 1),
                    halign="left",
                    valign="top",
                )
                # Manual bindings since this widget is built in Python, not
                # KV -- keeps text wrapping to the actual available width
                # and the label's height matched to its rendered text.
                label.bind(width=lambda inst, val: setattr(inst, "text_size", (val, None)))
                label.bind(texture_size=lambda inst, val: setattr(inst, "height", val[1]))
                self._preview_content.add_widget(label)

        container = self.ids.content_container
        if self.ids.content_field.parent is not None:
            container.remove_widget(self.ids.content_field)
        if self._preview_scroll.parent is None:
            container.add_widget(self._preview_scroll)

    def save_note(self):
        title = self.ids.title_field.text.strip()
        content = self.ids.content_field.text.strip()

        if not title:
            print("Please add a title")
            return

        if self.current_note_id is None:
            create_notes(DEFAULT_NOTEBOOK_ID, title, content)
        else:
            update_notes(self.current_note_id, title, content)

        self.go_back()

    def delete_note(self):
        if self.current_note_id is not None:
            delete_notes(self.current_note_id)
        self.go_back()

    def duplicate_note(self):
        if self.current_note_id is not None:
            duplicate_notes(self.current_note_id)
        self.go_back()

    def go_back(self):
        self.ids.title_field.text = ""
        self.ids.content_field.text = ""
        self.current_note_id = None
        self.is_preview = False
        self.manager.current = "notes"