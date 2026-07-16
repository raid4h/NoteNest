# screens/note_editor_screen.py
import os
import re
import shutil
import uuid
from kivy.clock import Clock
from kivy.metrics import dp, sp
from kivy.utils import escape_markup
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivymd.uix.screen import MDScreen
from plyer import filechooser

from database.notes_queries import (
    get_notes_by_id, create_notes, update_notes, delete_notes, duplicate_notes,
)
from database.attachment_queries import (
    create_attachment, get_all_attachments, delete_attachment,
)

DEFAULT_NOTEBOOK_ID = 1

# Photos get copied here instead of staying wherever they were picked from,
# so a note doesn't break if the original file gets moved or deleted, and
# so notes work the same on a different machine.
# Anchored to this file's own location instead of the current working
# directory, since the working directory isn't reliable here (the same
# issue that broke the database path when the file picker changed it).
_SCREENS_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_SCREENS_DIR)
ATTACHMENTS_DIR = os.path.join(_PROJECT_ROOT, "note_attachments")

# Matches an inline image marker in note content, e.g. {{img:note_attachments/abc123.jpg}}
IMAGE_TOKEN_PATTERN = re.compile(r"\{\{img:(.*?)\}\}")

# A fixed list of sizes to step through with the font-size buttons. Kivy
# text widgets only support ONE size for their entire content, not a
# different size per selection -- this is a whole-note setting.
FONT_SIZES = [sp(14), sp(16), sp(18), sp(20), sp(24), sp(28)]

# Fonts to cycle through with the font-family button. "Roboto" is
# KivyMD's built-in default; the other two need real .ttf files placed in
# a fonts/ folder in the project root (see Step 1 above). This is also a
# whole-note setting, same limitation as font size.
FONT_CHOICES = [
    "Roboto",
    os.path.join(_PROJECT_ROOT, "fonts", "OpenSans-Regular.ttf"),
    os.path.join(_PROJECT_ROOT, "fonts", "RobotoMono-Regular.ttf"),
    os.path.join(_PROJECT_ROOT, "fonts", "Baskerville-Regular.ttf"),
    os.path.join(_PROJECT_ROOT, "fonts", "Caveat-Regular.ttf"),
    os.path.join(_PROJECT_ROOT, "fonts", "Yuyu-Regular.ttf"),
]


# ─── converts our plain-text formatting markers into real Kivy markup ───
def convert_formatting_to_markup(text):
    # escape_markup() first, so if someone literally types [ or ] in a
    # note, it shows as plain text instead of breaking the markup parser.
    text = escape_markup(text)

    # Order matters: ** and __ must convert before single * or a leftover
    # underscore would be treated as a marker, since both bold/underline
    # use a doubled version of a character that plain italic uses singly.
    text = re.sub(r"\*\*(.+?)\*\*", r"[b]\1[/b]", text, flags=re.DOTALL)
    text = re.sub(r"__(.+?)__", r"[u]\1[/u]", text, flags=re.DOTALL)
    text = re.sub(r"\*(.+?)\*", r"[i]\1[/i]", text, flags=re.DOTALL)

    # Kivy's Label markup has no true background-highlight tag, so this
    # is approximated with a distinct text color instead of a real
    # highlighter background -- a known, deliberate simplification.
    text = re.sub(r"==(.+?)==", r"[color=#B8860B]\1[/color]", text, flags=re.DOTALL)
    return text


class NoteEditorScreen(MDScreen):
    current_note_id = None
    is_preview = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._preview_content = BoxLayout(
            orientation="vertical", size_hint_y=None, spacing=dp(8)
        )
        self._preview_content.bind(minimum_height=self._preview_content.setter("height"))

        self._preview_scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False)
        self._preview_scroll.add_widget(self._preview_content)

        self._last_selection = None
        # NOTE: deliberately not binding on_kv_post here. on_kv_post actually
        # fires DURING super().__init__() above, before this line would even
        # run -- so a bind placed here always misses it. Overriding the
        # method below is the correct way to hook into this event.

    def on_kv_post(self, base_widget):
        # Kivy calls this automatically once this screen's KV rule has been
        # fully applied and self.ids is populated -- guaranteed to run,
        # unlike binding to on_kv_post from inside __init__.
        super().on_kv_post(base_widget)
        self.ids.content_field.bind(selection_text=self._track_selection)

    def _track_selection(self, field, value):
        if value:
            start, end = sorted((field.selection_from, field.selection_to))
            self._last_selection = (value, start, end)

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

    # ─── image picking, now with local copying ───
    def pick_image(self):
        if self.current_note_id is None:
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
        # Runs on Kivy's main thread instead of directly in the picker's
        # callback, since that callback can run on a different thread.
        Clock.schedule_once(lambda dt: self._insert_image_token(selection))

    def _insert_image_token(self, selection):
        if not selection:
            return
        original_path = selection[0]

        # Copy the picked photo into the project's own folder instead of
        # referencing wherever it originally lived, so the note isn't
        # broken if that original file is later moved, renamed, or deleted.
        os.makedirs(ATTACHMENTS_DIR, exist_ok=True)
        file_extension = os.path.splitext(original_path)[1]
        stored_filename = f"{uuid.uuid4().hex}{file_extension}"
        stored_path = os.path.join(ATTACHMENTS_DIR, stored_filename)
        shutil.copy2(original_path, stored_path)

        create_attachment(self.current_note_id, stored_path)

        token = f"{{{{img:{stored_path}}}}}"
        field = self.ids.content_field
        try:
            field.insert_text(token)
        except AttributeError:
            field.text = field.text + ("\n" if field.text else "") + token

    # ─── removes attachment rows whose {{img:...}} marker no longer
    #     appears in the note's text (e.g. the user deleted it) ───
    def _cleanup_removed_attachments(self, content):
        remaining_paths = set(IMAGE_TOKEN_PATTERN.findall(content))
        # attachments table shape from db.py: (id, note_id, file_path, created_at)
        for row in get_all_attachments(self.current_note_id):
            if row[2] not in remaining_paths:
                delete_attachment(row[0])
                # Note: this only removes the database record. The copied
                # file in note_attachments/ is left on disk untouched --
                # harmless, but a further cleanup step if you want it.

    # ─── bold / italic / underline / highlight ───
    def _wrap_selection(self, marker):
        field = self.ids.content_field

        if not self._last_selection:
            # Nothing selected -- just drop an empty marker pair at the
            # cursor and place the cursor between them, like before.
            field.insert_text(marker + marker)
            index = field.cursor_index() - len(marker)
            field.cursor = field.get_cursor_from_index(index)
            return

        selected, start, end = self._last_selection
        text = field.text

        if text[start:end] != selected:
            # Selection went stale (text changed since it was recorded) --
            # fall back to inserting an empty marker pair instead of risking
            # wrapping the wrong text.
            self._last_selection = None
            field.insert_text(marker + marker)
            index = field.cursor_index() - len(marker)
            field.cursor = field.get_cursor_from_index(index)
            return

        m_len = len(marker)

        # Case 1: the selection ITSELF includes the markers, e.g. the user
        # dragged over "**bold**" including the asterisks. Strip them.
        if selected.startswith(marker) and selected.endswith(marker) and len(selected) >= 2 * m_len:
            inner = selected[m_len:-m_len]
            field.text = text[:start] + inner + text[end:]
            field.cursor = field.get_cursor_from_index(start + len(inner))
            self._last_selection = None
            return

        # Case 2: the markers sit just OUTSIDE the selection, e.g. the user
        # only selected "bold" but "**" is right before and after it. This is
        # the natural way people reselect text to undo formatting. Strip the
        # markers that are already there instead of adding new ones.
        before = text[max(0, start - m_len):start]
        after = text[end:end + m_len]
        if before == marker and after == marker:
            field.text = text[:start - m_len] + selected + text[end + m_len:]
            field.cursor = field.get_cursor_from_index(start - m_len + len(selected))
            self._last_selection = None
            return

        # Neither case matched -- this selection isn't already wrapped in
        # this marker, so wrap it normally (this is the original behavior).
        field.text = text[:start] + marker + selected + marker + text[end:]
        field.cursor = field.get_cursor_from_index(end + 2 * m_len)
        self._last_selection = None

    def make_bold(self):
        self._wrap_selection("**")

    def make_italic(self):
        self._wrap_selection("*")

    def make_underline(self):
        self._wrap_selection("__")

    def make_highlight(self):
        self._wrap_selection("==")

    # ─── text alignment (whole note, not per-selection — same Kivy
    #     limitation as font size/family above) ───
    def set_align_left(self):
        self.ids.content_field.halign = "left"

    def set_align_center(self):
        self.ids.content_field.halign = "center"

    def set_align_right(self):
        self.ids.content_field.halign = "right"

    # ─── font size (whole note, not per-selection) ───
    def increase_font_size(self):
        field = self.ids.content_field
        bigger = [s for s in FONT_SIZES if s > field.font_size]
        if bigger:
            field.font_size = bigger[0]

    def decrease_font_size(self):
        field = self.ids.content_field
        smaller = [s for s in FONT_SIZES if s < field.font_size]
        if smaller:
            field.font_size = smaller[-1]

    # ─── font family (whole note, not per-selection) ───
    def cycle_font(self):
        field = self.ids.content_field
        try:
            current_index = FONT_CHOICES.index(field.font_name)
        except ValueError:
            current_index = -1
        field.font_name = FONT_CHOICES[(current_index + 1) % len(FONT_CHOICES)]

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
                    text=convert_formatting_to_markup(part),
                    markup=True,
                    size_hint_y=None,
                    color=(0.29, 0.20, 0.15, 1),
                    halign=self.ids.content_field.halign,
                    valign="top",
                    font_size=self.ids.content_field.font_size,
                    font_name=self.ids.content_field.font_name,
                )
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
            self._cleanup_removed_attachments(content)

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