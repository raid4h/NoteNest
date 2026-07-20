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
from kivy.properties import BooleanProperty
from kivy.uix.modalview import ModalView
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDButton, MDButtonText
from kivy.core.text import LabelBase
import trash_store
import webbrowser
from kivymd.uix.textfield import MDTextField, MDTextFieldHintText
from kivy.utils import platform

from database.notes_queries import (
    get_notes_by_id, create_notes, update_notes, delete_notes, duplicate_notes,
)
from database.attachment_queries import (
    create_attachment, get_all_attachments, delete_attachment,
)

from theme.theme_manager import theme_manager
from theme.themed_screen import ThemedScreenMixin
from theme.palettes import BACKGROUND, TEXT_PRIMARY, TEXT_SECONDARY, CARD_SECONDARY, CARD_PRIMARY, ACCENT

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

# Exported .txt copies of notes go here, same local-folder pattern
# already used for note_attachments/.
EXPORTS_DIR = os.path.join(_PROJECT_ROOT, "exported_notes")

# Characters not allowed in Windows filenames -- stripped out of a
# note's title before it's used as a filename.
_INVALID_FILENAME_CHARS = re.compile(r'[\\/:*?"<>|]')

# Matches an inline image marker in note content, e.g. {{img:note_attachments/abc123.jpg}}
IMAGE_TOKEN_PATTERN = re.compile(r"\{\{img:(.*?)\}\}")
# Matches an inline hyperlink marker, e.g. {{link:https://example.com|click here}}
LINK_TOKEN_PATTERN = re.compile(r"\{\{link:(.*?)\|(.*?)\}\}", re.DOTALL)

# A fixed list of sizes to step through with the font-size buttons. Kivy
# text widgets only support ONE size for their entire content, not a
# different size per selection -- this is a whole-note setting.
FONT_SIZES = [sp(14), sp(16), sp(18), sp(20), sp(24), sp(28)]

# ─── font family registration for real bold/italic ───
# Kivy's [b]/[i] markup only works if the font in use has been
# explicitly registered with its own Bold/Italic files -- a bare
# font_name string like "Roboto" isn't enough on its own for a plain
# Label. Registering every font ourselves, with whichever style files
# actually exist, means bold/italic genuinely work instead of silently
# doing nothing or being faked with a color tint.

_FONTS_DIR = os.path.join(_PROJECT_ROOT, "fonts")


def _font_path(filename):
    # Returns None for a missing filename (either because that style
    # doesn't exist for this font, or the file hasn't been added yet)
    # instead of crashing -- LabelBase.register() is fine receiving
    # None for an optional style and just falls back to Regular for it.
    if filename is None:
        return None
    path = os.path.join(_FONTS_DIR, filename)
    return path if os.path.isfile(path) else None


# Each font's available style files. Missing keys (e.g. Caveat has no
# "italic") or missing files on disk are both handled the same way --
# that style just isn't registered, and Kivy uses Regular instead.
_FONT_FAMILY_FILES = {
    "Roboto": {
        "regular": "Roboto-Regular.ttf",
        "bold": "Roboto-Bold.ttf",
        "italic": "Roboto-Italic.ttf",
        "bolditalic": "Roboto-BoldItalic.ttf",
    },
    "OpenSans": {
        "regular": "OpenSans-Regular.ttf",
        "bold": "OpenSans-Bold.ttf",
        "italic": "OpenSans-Italic.ttf",
        "bolditalic": "OpenSans-BoldItalic.ttf",
    },
    "RobotoMono": {
        "regular": "RobotoMono-Regular.ttf",
        "bold": "RobotoMono-Bold.ttf",
        "italic": "RobotoMono-Italic.ttf",
        "bolditalic": "RobotoMono-BoldItalic.ttf",
    },
    "Baskerville": {
        "regular": "Baskerville-Regular.ttf",
        "bold": "Baskerville-Bold.ttf",
        "italic": "Baskerville-Italic.ttf",
        # No official Bold-Italic file exists for Libre Baskerville --
        # left out on purpose, falls back to Bold for that combination.
    },
    "Caveat": {
        "regular": "Caveat-Regular.ttf",
        "bold": "Caveat-Bold.ttf",
        # Handwriting font, no separate italic style exists at all.
    },
    "Yuyu": {
        "regular": "Yuyu-Regular.ttf",
        # No bold/italic files available -- always renders as Regular.
    },
}


def _register_font_families():
    # Registers each font family with Kivy, and returns the list of
    # family keys that were actually registered successfully (skipping
    # any whose Regular file isn't present yet), so FONT_CHOICES only
    # ever offers fonts that genuinely work.
    registered = []
    for family_key, variants in _FONT_FAMILY_FILES.items():
        regular_path = _font_path(variants.get("regular"))
        if regular_path is None:
            continue
        LabelBase.register(
            name=family_key,
            fn_regular=regular_path,
            fn_bold=_font_path(variants.get("bold")),
            fn_italic=_font_path(variants.get("italic")),
            fn_bolditalic=_font_path(variants.get("bolditalic")),
        )
        registered.append(family_key)
    return registered


FONT_CHOICES = _register_font_families()
if not FONT_CHOICES:
    # Should never actually happen (Roboto's Regular file should always
    # be present), but guards against an empty font list just in case.
    FONT_CHOICES = ["Roboto"]

DEFAULT_FONT_NAME = "Roboto"


# Maps OLD stored font values (full file paths, from before fonts were
# registered as proper families) to the new short registered family
# key, so notes saved before this change still show the right font
# instead of falling back to default.
_LEGACY_FONT_FILENAME_TO_KEY = {
    "opensans-regular.ttf": "OpenSans",
    "robotomono-regular.ttf": "RobotoMono",
    "baskerville-regular.ttf": "Baskerville",
    "caveat-regular.ttf": "Caveat",
    "yuyu-regular.ttf": "Yuyu",
}


def _normalize_font_name(font_name):
    # Already a valid new-style family key -- nothing to translate.
    if font_name in FONT_CHOICES:
        return font_name

    # Old-style value was a full path -- match on the filename alone,
    # lowercased, since old paths vary in case and drive letter.
    filename = os.path.basename(font_name).lower()
    return _LEGACY_FONT_FILENAME_TO_KEY.get(filename, DEFAULT_FONT_NAME)
DEFAULT_FONT_SIZE = sp(16)
DEFAULT_ALIGN = "left"

# Matches a hidden metadata marker at the very start of a note's stored
# content, e.g. {{meta:font=Roboto|size=16.0|align=left}} -- same
# inline-marker trick already used for {{img:...}} tokens, so this needs
# no database changes and stays entirely inside this file.
META_PATTERN = re.compile(r"^\{\{meta:(.*?)\}\}\n?")


def _parse_note_meta(stored_content):
    """Returns (font_name, font_size, halign, visible_content)."""
    match = META_PATTERN.match(stored_content)
    if not match:
        return DEFAULT_FONT_NAME, DEFAULT_FONT_SIZE, DEFAULT_ALIGN, stored_content

    settings = {}
    for pair in match.group(1).split("|"):
        if "=" in pair:
            key, value = pair.split("=", 1)
            settings[key] = value

    font_name = _normalize_font_name(settings.get("font", DEFAULT_FONT_NAME))
    try:
        font_size = float(settings.get("size", DEFAULT_FONT_SIZE))
    except ValueError:
        font_size = DEFAULT_FONT_SIZE
    halign = settings.get("align", DEFAULT_ALIGN)

    visible_content = stored_content[match.end():]
    return font_name, font_size, halign, visible_content


def _build_note_meta(font_name, font_size, halign):
    return f"{{{{meta:font={font_name}|size={font_size}|align={halign}}}}}\n"

def _escape_and_apply_format_markup(text):
    # Assumes text has ALREADY been escape_markup()'d -- kept separate
    # from escaping so link conversion (which injects real markup tags)
    # can happen safely in between the two steps.
    text = re.sub(r"\*\*(.+?)\*\*", r"[b]\1[/b]", text, flags=re.DOTALL)
    text = re.sub(r"__(.+?)__", r"[u]\1[/u]", text, flags=re.DOTALL)
    text = re.sub(r"\*(.+?)\*", r"[i]\1[/i]", text, flags=re.DOTALL)
    # Kivy's Label markup has no true background-highlight tag, so this
    # is approximated with a distinct text color instead of a real
    # highlighter background -- a known, deliberate simplification.
    text = re.sub(r"==(.+?)==", r"[color=#B8860B]\1[/color]", text, flags=re.DOTALL)
    return text


def convert_formatting_to_markup(text):
    # Kept for any other caller that just needs bold/italic/underline/
    # highlight with no link support.
    return _escape_and_apply_format_markup(escape_markup(text))

class NoteEditorScreen(ThemedScreenMixin,MDScreen):
    current_note_id = None
    is_preview = False
    show_search = BooleanProperty(False)

    THEME_MAP = {
        "self":                ("md_bg_color", BACKGROUND),
        "header_bar":          ("md_bg_color", CARD_SECONDARY),
        "back_button":         ("icon_color", TEXT_PRIMARY),
        "header_label":        ("text_color", TEXT_PRIMARY),
        "image_button":        ("icon_color", TEXT_PRIMARY),
        "preview_button":      ("icon_color", TEXT_PRIMARY),
        "duplicate_button":    ("icon_color", TEXT_PRIMARY),
        "delete_button":       ("icon_color", TEXT_PRIMARY),
        "save_button":         ("icon_color", TEXT_PRIMARY),
        "title_bar":           ("md_bg_color", BACKGROUND),
        "toolbar":             ("md_bg_color", BACKGROUND),
        "bold_button":         ("icon_color", TEXT_PRIMARY),
        "italic_button":       ("icon_color", TEXT_PRIMARY),
        "underline_button":    ("icon_color", TEXT_PRIMARY),
        "highlight_button":    ("icon_color", TEXT_PRIMARY),
        "align_left_button":   ("icon_color", TEXT_PRIMARY),
        "align_center_button": ("icon_color", TEXT_PRIMARY),
        "align_right_button":  ("icon_color", TEXT_PRIMARY),
        "decrease_font_button": ("icon_color", TEXT_PRIMARY),
        "increase_font_button": ("icon_color", TEXT_PRIMARY),
        "cycle_font_button":   ("icon_color", TEXT_PRIMARY),
        "content_card":        ("md_bg_color", CARD_PRIMARY),
    }

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
        # Undo/redo history for the whole note. Each entry is a full
        # snapshot of the note's text at some point in time -- simple,
        # not per-keystroke, but easy to reason about.
        self._undo_stack = []
        self._redo_stack = []
        # True while WE are the ones changing field.text (e.g. during an
        # undo/redo itself) -- stops that change from being recorded as
        # a brand-new edit, which would corrupt the history.
        # In-note search state: list of (start, end) match positions,
        # and which match is currently selected/highlighted.
        self._search_matches = []
        self._search_match_index = -1
        self._suppress_history = False
        # Holds the pending "user paused typing" timer so it can be
        # cancelled/restarted on every keystroke.
        self._history_debounce_event = None
        # Maps a per-render "ref" key (e.g. "link0") to its real URL --
        # rebuilt fresh every time Preview mode renders, since Kivy
        # Label's [ref=...] markup can only carry a short id, not a
        # full URL directly.
        self._preview_link_map = {}
        self._link_ref_counter = 0
        # Holds whatever text was selected right before the link popup
        # opened, since opening the popup shifts keyboard focus away
        # from content_field.
        self._pending_link_selection = None

    def on_kv_post(self, base_widget):
        # Kivy calls this automatically once this screen's KV rule has been
        # fully applied and self.ids is populated -- guaranteed to run,
        # unlike binding to on_kv_post from inside __init__.
        super().on_kv_post(base_widget)
        self.ids.content_field.bind(selection_text=self._track_selection)
        # Fires on every keystroke -- drives both the word/char count
        # and the undo checkpoint timer.
        self.ids.content_field.bind(text=self._on_content_text_changed)

    def on_theme_applied(self):
        field = self.ids.get("content_field")
        if field is not None:
            field.background_color = theme_manager.get_color(CARD_PRIMARY)
            field.foreground_color = theme_manager.get_color(TEXT_PRIMARY)
            field.hint_text_color = theme_manager.get_color(TEXT_SECONDARY)
            field.cursor_color = theme_manager.get_color(TEXT_PRIMARY)
            field.selection_color = self._faded(theme_manager.get_color(ACCENT), 0.4)

        self._refresh_preview_if_active()

    def _track_selection(self, field, value):
        if value:
            start, end = sorted((field.selection_from, field.selection_to))
            self._last_selection = (value, start, end)
    
    def _on_content_text_changed(self, field, value):
        # Runs on every single keystroke.
        self._update_word_count(value)

        if self._suppress_history:
            # This change came from our own undo/redo code, not the
            # user typing -- don't record it as a new edit.
            return

        # Restart the "pause" timer -- if the user keeps typing, this
        # keeps getting cancelled and rescheduled, so a checkpoint only
        # actually saves once typing stops for a moment.
        if self._history_debounce_event:
            self._history_debounce_event.cancel()
        self._history_debounce_event = Clock.schedule_once(self._push_history_snapshot, 1.2)

    def _push_history_snapshot(self, dt):
        # Saves the current text as a checkpoint, unless it's identical
        # to the most recent one already saved (avoids useless duplicates).
        field = self.ids.content_field
        current_text = field.text

        if self._undo_stack and self._undo_stack[-1] == current_text:
            return

        self._undo_stack.append(current_text)
        # Cap history length so a long writing session can't grow this
        # list forever.
        if len(self._undo_stack) > 50:
            self._undo_stack.pop(0)

        # A fresh edit invalidates any redo history, same as standard
        # editors (you can't redo forward after making a new change).
        self._redo_stack.clear()

    def undo_note(self):
        # Cancel any pending "pause" checkpoint -- we don't want it
        # firing after we've already jumped to an older state.
        if self._history_debounce_event:
            self._history_debounce_event.cancel()
            self._history_debounce_event = None

        if len(self._undo_stack) < 2:
            # Only the current/baseline checkpoint exists -- nothing
            # older to go back to.
            return

        field = self.ids.content_field
        current = self._undo_stack.pop()
        self._redo_stack.append(current)
        previous = self._undo_stack[-1]

        self._suppress_history = True
        field.text = previous
        field.cursor = field.get_cursor_from_index(len(previous))
        self._suppress_history = False

    def redo_note(self):
        if not self._redo_stack:
            return

        field = self.ids.content_field
        next_text = self._redo_stack.pop()
        self._undo_stack.append(next_text)

        self._suppress_history = True
        field.text = next_text
        field.cursor = field.get_cursor_from_index(len(next_text))
        self._suppress_history = False

    def _update_word_count(self, text):
        # Refreshes the word/character count label in the toolbar, if
        # it exists in this screen's KV (guarded with the "in self.ids"
        # check so this doesn't crash before the label is added below).
        char_count = len(text)
        word_count = len(text.split()) if text.strip() else 0
        if "word_count_label" in self.ids:
            self.ids.word_count_label.text = f"{word_count} words · {char_count} chars"
    
    def toggle_search(self):
        # Shows/hides the search bar. If the user opens search while in
        # Preview mode, switch to Edit mode first -- match highlighting
        # happens on content_field, which isn't visible during Preview.
        self.show_search = not self.show_search
        field = self.ids.content_field

        if self.show_search:
            if self.is_preview:
                self.is_preview = False
                self.show_edit_mode()
            self.ids.search_query_field.text = ""
            self._search_matches = []
            self._search_match_index = -1
            self._update_search_match_label()
            # Give focus to the search box so the user can type right
            # away, scheduled for next frame so the widget is ready.
            Clock.schedule_once(lambda dt: setattr(self.ids.search_query_field, "focus", True))
        else:
            field.cancel_selection()

    def _find_all_matches(self, text, query):
        # Case-insensitive substring search, returns a list of
        # (start_index, end_index) tuples for every match found.
        matches = []
        if not query:
            return matches
        lower_text = text.lower()
        lower_query = query.lower()
        start = 0
        while True:
            index = lower_text.find(lower_query, start)
            if index == -1:
                break
            matches.append((index, index + len(query)))
            start = index + 1
        return matches

    def on_search_text_change(self, query):
        # Recomputes matches live as the user types in the search box.
        field = self.ids.content_field
        self._search_matches = self._find_all_matches(field.text, query)
        self._search_match_index = 0 if self._search_matches else -1
        self._update_search_match_label()

        if self._search_matches:
            self._jump_to_match(self._search_match_index)
        else:
            field.cancel_selection()

    def search_next(self):
        if not self._search_matches:
            return
        # Wraps back to the first match after the last one.
        self._search_match_index = (self._search_match_index + 1) % len(self._search_matches)
        self._jump_to_match(self._search_match_index)
        self._update_search_match_label()

    def search_prev(self):
        if not self._search_matches:
            return
        # Wraps back to the last match before the first one.
        self._search_match_index = (self._search_match_index - 1) % len(self._search_matches)
        self._jump_to_match(self._search_match_index)
        self._update_search_match_label()

    def _jump_to_match(self, index):
        # Moves the cursor to the match (which scrolls it into view,
        # the same trick already used in _wrap_selection), then selects
        # it so it shows highlighted using the text box's normal
        # selection color.
        field = self.ids.content_field
        start, end = self._search_matches[index]
        field.cursor = field.get_cursor_from_index(start)
        field.select_text(start, end)

    def _update_search_match_label(self):
        if "search_match_label" not in self.ids:
            return
        if not self._search_matches:
            self.ids.search_match_label.text = "0/0"
        else:
            self.ids.search_match_label.text = f"{self._search_match_index + 1}/{len(self._search_matches)}"

    def on_enter(self):
        self.is_preview = False
        if self.current_note_id is not None:
            self.load_note(self.current_note_id)
        else:
            field = self.ids.content_field
            self.ids.title_field.text = ""
            field.text = ""
            field.font_name = DEFAULT_FONT_NAME
            field.font_size = DEFAULT_FONT_SIZE
            field.halign = DEFAULT_ALIGN

            if self._history_debounce_event:
                self._history_debounce_event.cancel()
                self._history_debounce_event = None
            self._undo_stack = [field.text]
            self._redo_stack = []
            self._update_word_count(field.text)
            # Close and reset in-note search too, so a leftover query typed
            # for a previous note doesn't carry over into this one.
            self.show_search = False
            self._search_matches = []
            self._search_match_index = -1
            if "search_query_field" in self.ids:
                self.ids.search_query_field.text = ""
        self.show_edit_mode()

    def load_note(self, note_id):
            note = get_notes_by_id(note_id)
            field = self.ids.content_field

            if note is None:
                self.ids.title_field.text = ""
                field.text = ""
                field.font_name = DEFAULT_FONT_NAME
                field.font_size = DEFAULT_FONT_SIZE
                field.halign = DEFAULT_ALIGN
            else:
                self.ids.title_field.text = note[2]
                stored_content = note[3] or ""
                font_name, font_size, halign, visible_content = _parse_note_meta(stored_content)
                field.text = visible_content
                field.font_name = font_name
                field.font_size = font_size
                field.halign = halign

            # Start a brand-new undo history for whichever note just loaded,
            # with its current text as checkpoint zero -- and cancel any
            # leftover pause-timer from whatever note was open before this,
            # so it can't fire late and pollute this note's history.
            if self._history_debounce_event:
                self._history_debounce_event.cancel()
                self._history_debounce_event = None
            self._undo_stack = [field.text]
            self._redo_stack = []
            self._update_word_count(field.text)
            # Close and reset in-note search too, so a leftover query typed
            # for a previous note doesn't carry over into this one.
            self.show_search = False
            self._search_matches = []
            self._search_match_index = -1
            if "search_query_field" in self.ids:
                self.ids.search_query_field.text = ""

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

    def _convert_links_to_markup(self, text):
        # Replaces each {{link:URL|label}} token with a Kivy [ref=key]
        # markup span (clickable text), recording key -> URL in
        # self._preview_link_map so _on_preview_link_pressed can look
        # it up when tapped.
        def _replace(match):
            url, label = match.group(1), match.group(2)
            key = f"link{self._link_ref_counter}"
            self._link_ref_counter += 1
            self._preview_link_map[key] = url
            return f"[ref={key}][u][color=#3B6EA5]{label}[/color][/u][/ref]"
        return LINK_TOKEN_PATTERN.sub(_replace, text)

    def _convert_part_for_preview(self, text):
        # Order matters: escape first (protects literal [ ] the user
        # typed), THEN convert links (injects real [ref]/[color] tags),
        # THEN bold/italic/underline/highlight -- doing links before
        # escaping would corrupt the tags we just inserted.
        text = escape_markup(text)
        text = self._convert_links_to_markup(text)
        text = _escape_and_apply_format_markup(text)
        return text

    def _on_preview_link_pressed(self, instance, ref):
        # Fires when a [ref=...] span is tapped in Preview mode.
        url = self._preview_link_map.get(ref)
        if url:
            self._open_url(url)

    def _open_url(self, url):
        # webbrowser.open() works fine on Windows/Mac/Linux, but has no
        # reliable browser to hand off to on Android. On Android,
        # firing an explicit system "open this URL" intent via pyjnius
        # is the standard, well-tested way Kivy apps do this instead.
        # This only ever runs on an actual Android device/build --
        # desktop behavior below is completely unchanged.
        if platform == "android":
            from jnius import autoclass
            Intent = autoclass("android.content.Intent")
            Uri = autoclass("android.net.Uri")
            PythonActivity = autoclass("org.kivy.android.PythonActivity")

            intent = Intent(Intent.ACTION_VIEW, Uri.parse(url))
            PythonActivity.mActivity.startActivity(intent)
        else:
            webbrowser.open(url)

    # ─── hyperlink insertion ───
    def make_link(self):
        field = self.ids.content_field
        # Snapshot the current selection before the popup steals focus.
        if self._last_selection:
            selected, start, end = self._last_selection
            if field.text[start:end] == selected:
                self._pending_link_selection = (selected, start, end)
            else:
                self._pending_link_selection = None
        else:
            self._pending_link_selection = None

        self._show_link_url_popup()

    def _show_link_url_popup(self):
        card = MDCard(
            orientation="vertical", padding=dp(20), spacing=dp(14),
            radius=[16], size_hint=(None, None), size=(dp(320), dp(180)),
        )

        prompt_label = MDLabel(
            text="Enter a URL to link to:", halign="center",
            theme_text_color="Custom", size_hint_y=None, height=dp(28),
        )
        card.add_widget(prompt_label)

        url_field = MDTextField(size_hint_y=None, height=dp(48))
        url_field.add_widget(MDTextFieldHintText(text="https://example.com"))
        card.add_widget(url_field)

        button_row = BoxLayout(orientation="horizontal", spacing=dp(12), size_hint_y=None, height=dp(48))
        cancel_button = MDButton(MDButtonText(text="Cancel"), style="outlined")
        cancel_button.bind(on_release=lambda *_: modal.dismiss())
        add_button = MDButton(MDButtonText(text="Add Link"), style="filled")
        add_button.bind(on_release=lambda *_: self._confirm_link(url_field.text, modal))
        button_row.add_widget(cancel_button)
        button_row.add_widget(add_button)
        card.add_widget(button_row)

        modal = ModalView(
            size_hint=(None, None), size=(dp(320), dp(180)),
            auto_dismiss=True, background_color=(0, 0, 0, 0.5),
        )
        modal.add_widget(card)
        modal.open()

    def _confirm_link(self, url, modal):
        modal.dismiss()
        url = url.strip()
        if not url:
            return  # nothing entered -- treat as cancel

        # Assume https:// if the user just typed "example.com" -- makes
        # the link actually openable without them needing to know to
        # type the scheme themselves.
        if not (url.startswith("http://") or url.startswith("https://")):
            url = "https://" + url

        field = self.ids.content_field

        if self._pending_link_selection:
            selected, start, end = self._pending_link_selection
            if field.text[start:end] == selected:
                token = f"{{{{link:{url}|{selected}}}}}"
                field.text = field.text[:start] + token + field.text[end:]
                field.cursor = field.get_cursor_from_index(start + len(token))
                self._pending_link_selection = None
                return

        # No usable selection -- insert a placeholder link at the cursor.
        token = f"{{{{link:{url}|Link}}}}"
        field.insert_text(token)

    def make_bold(self):
        self._wrap_selection("**")

    def make_italic(self):
        self._wrap_selection("*")

    def make_underline(self):
        self._wrap_selection("__")

    def make_highlight(self):
        self._wrap_selection("==")

    def increase_font_size(self):
        field = self.ids.content_field
        bigger = [s for s in FONT_SIZES if s > field.font_size]
        if bigger:
            field.font_size = bigger[0]
        self._refresh_preview_if_active()

    def decrease_font_size(self):
        field = self.ids.content_field
        smaller = [s for s in FONT_SIZES if s < field.font_size]
        if smaller:
            field.font_size = smaller[-1]
        self._refresh_preview_if_active()

    def cycle_font(self):
        field = self.ids.content_field
        try:
            current_index = FONT_CHOICES.index(field.font_name)
        except ValueError:
            current_index = -1
        field.font_name = FONT_CHOICES[(current_index + 1) % len(FONT_CHOICES)]
        self._refresh_preview_if_active()

    def set_align_left(self):
        self.ids.content_field.halign = "left"
        self._refresh_preview_if_active()

    def set_align_center(self):
        self.ids.content_field.halign = "center"
        self._refresh_preview_if_active()

    def set_align_right(self):
        self.ids.content_field.halign = "right"
        self._refresh_preview_if_active()

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
        # Fresh link map every render -- ref keys only need to be
        # unique within a single Preview render, not across renders.
        self._preview_link_map = {}
        self._link_ref_counter = 0

        parts = IMAGE_TOKEN_PATTERN.split(raw)

        for i, part in enumerate(parts):
            if i % 2 == 1:
                align = self.ids.content_field.halign
                if align == "center":
                    img_pos_hint = {"center_x": 0.5}
                elif align == "right":
                    img_pos_hint = {"right": 1}
                else:
                    img_pos_hint = {"x": 0}

                img = Image(
                    source=part,
                    size_hint=(None, None),
                    size=(dp(220), dp(220)),
                    pos_hint=img_pos_hint,
                    allow_stretch=True,
                )
                self._preview_content.add_widget(img)
            elif part.strip():
                label = Label(
                    text=self._convert_part_for_preview(part),
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
                label.bind(on_ref_press=self._on_preview_link_pressed)
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

        # Record a checkpoint for the exact state being saved.
        if self._history_debounce_event:
            self._history_debounce_event.cancel()
            self._history_debounce_event = None
        self._push_history_snapshot(0)

        field = self.ids.content_field
        meta = _build_note_meta(field.font_name, field.font_size, field.halign)
        content_to_store = meta + content

        # Prepend the current font/size/alignment as a hidden metadata
        # marker -- the same trick as {{img:...}} tokens -- so it's
        # remembered per-note instead of leaking into the next note opened.
        field = self.ids.content_field
        meta = _build_note_meta(field.font_name, field.font_size, field.halign)
        content_to_store = meta + content

        if self.current_note_id is None:
            create_notes(DEFAULT_NOTEBOOK_ID, title, content_to_store)
        else:
            update_notes(self.current_note_id, title, content_to_store)
            self._cleanup_removed_attachments(content)

        self.go_back()

# ─── delete confirmation popup ───
    def _build_delete_confirmation(self):
        # Built once, the first time delete is pressed, and reused
        # after that -- no need to rebuild these widgets every tap.
        card = MDCard(
            orientation="vertical",
            padding=dp(20),
            spacing=dp(16),
            radius=[16],
            size_hint=(None, None),
            size=(dp(300), dp(160)),
        )

        warning_label = MDLabel(
            text="Delete this note? This can't be undone.",
            halign="center",
            theme_text_color="Custom",
            size_hint_y=None,
        )
        # Same wrapping trick used in show_preview_mode -- makes the
        # label wrap to the card's width instead of overflowing it.
        warning_label.bind(width=lambda inst, val: setattr(inst, "text_size", (val, None)))
        warning_label.bind(texture_size=lambda inst, val: setattr(inst, "height", val[1]))
        card.add_widget(warning_label)

        button_row = BoxLayout(
            orientation="horizontal", spacing=dp(12),
            size_hint_y=None, height=dp(48),
        )

        cancel_button = MDButton(MDButtonText(text="Cancel"), style="outlined")
        cancel_button.bind(on_release=lambda *_: self._delete_modal.dismiss())

        confirm_button = MDButton(MDButtonText(text="Delete"), style="filled")
        confirm_button.bind(on_release=lambda *_: self._confirm_delete())

        button_row.add_widget(cancel_button)
        button_row.add_widget(confirm_button)
        card.add_widget(button_row)

        self._delete_modal = ModalView(
            size_hint=(None, None),
            size=(dp(300), dp(160)),
            auto_dismiss=True,
            background_color=(0, 0, 0, 0.5),
        )
        self._delete_modal.add_widget(card)

    def delete_note(self):
        if self.current_note_id is None:
            # Never saved -- nothing in the database to delete, and
            # nothing worth confirming.
            self.go_back()
            return

        if not hasattr(self, "_delete_modal"):
            self._build_delete_confirmation()
        self._delete_modal.open()

    def _confirm_delete(self):
        self._delete_modal.dismiss()

        # Snapshot the note into local trash before permanently
        # deleting it, so it can be recovered from "Recently Deleted"
        # if this was a mistake.
        note = get_notes_by_id(self.current_note_id)
        if note is not None:
            trash_store.add_to_trash(
                notebook_id=note[1],
                title=note[2],
                content=note[3] or "",
                category_id=note[8],
            )

        delete_notes(self.current_note_id)
        self.go_back()

    def duplicate_note(self):
        if self.current_note_id is not None:
            duplicate_notes(self.current_note_id)
        self.go_back()

    def _sanitize_filename(self, name):
        # Removes characters Windows won't allow in a filename, and
        # falls back to "Untitled" if nothing usable is left.
        cleaned = _INVALID_FILENAME_CHARS.sub("", name).strip()
        return cleaned if cleaned else "Untitled"

    def _strip_markers_for_export(self, raw_content):
        # Turns the note's raw stored text (still containing {{img:...}}
        # tokens and **/__/== markers) into clean plain text -- same
        # idea as the notes-list preview cleanup, just applied here.
        text = IMAGE_TOKEN_PATTERN.sub("[Photo]", raw_content)
        text = re.sub(r"\*\*(.+?)\*\*", r"\1", text, flags=re.DOTALL)
        text = re.sub(r"__(.+?)__", r"\1", text, flags=re.DOTALL)
        text = re.sub(r"==(.+?)==", r"\1", text, flags=re.DOTALL)
        text = re.sub(r"\*(.+?)\*", r"\1", text, flags=re.DOTALL)
        return text.strip()

    def export_note_as_txt(self):
        title = self.ids.title_field.text.strip() or "Untitled"
        # Stashed here so the picker's callback (which fires later,
        # possibly on a different thread) still has access to them.
        self._export_title = title
        self._export_clean_content = self._strip_markers_for_export(self.ids.content_field.text)

        safe_title = self._sanitize_filename(title)
        os.makedirs(EXPORTS_DIR, exist_ok=True)

        # Same working-directory protection already used for the photo
        # picker -- this dialog can silently change the app's working
        # directory too, which would break the database's relative path.
        self._cwd_before_export_picker = os.getcwd()

        filechooser.save_file(
            on_selection=self.on_export_location_selected,
            filters=[["Text files", "*.txt"]],
            path=os.path.join(EXPORTS_DIR, f"{safe_title}.txt"),
        )

    def on_export_location_selected(self, selection):
        os.chdir(self._cwd_before_export_picker)
        # Runs on the main thread instead of directly in the picker's
        # callback, same reasoning as the photo picker.
        Clock.schedule_once(lambda dt: self._write_export_file(selection))

    def _write_export_file(self, selection):
        if not selection:
            # User cancelled the save dialog -- nothing to export.
            return

        export_path = selection[0]
        if not export_path.lower().endswith(".txt"):
            export_path += ".txt"

        with open(export_path, "w", encoding="utf-8") as f:
            f.write(f"{self._export_title}\n\n{self._export_clean_content}")

        self._show_export_confirmation(export_path)

    def _show_export_confirmation(self, export_path):
        # Reuses the same popup pattern as the delete confirmation --
        # a small MDCard inside a ModalView -- since that combination
        # is already confirmed working in this project.
        card = MDCard(
            orientation="vertical",
            padding=dp(20),
            spacing=dp(16),
            radius=[16],
            size_hint=(None, None),
            size=(dp(320), dp(170)),
        )

        message_label = MDLabel(
            text=f"Note exported to:\n{export_path}",
            halign="center",
            theme_text_color="Custom",
            size_hint_y=None,
        )
        message_label.bind(width=lambda inst, val: setattr(inst, "text_size", (val, None)))
        message_label.bind(texture_size=lambda inst, val: setattr(inst, "height", val[1]))
        card.add_widget(message_label)

        modal = ModalView(
            size_hint=(None, None),
            size=(dp(320), dp(170)),
            auto_dismiss=True,
            background_color=(0, 0, 0, 0.5),
        )

        ok_button = MDButton(MDButtonText(text="OK"), style="filled")
        ok_button.bind(on_release=lambda *_: modal.dismiss())

        button_row = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(48))
        button_row.add_widget(ok_button)
        card.add_widget(button_row)

        modal.add_widget(card)
        modal.open()

    def go_back(self):
        self.ids.title_field.text = ""
        self.ids.content_field.text = ""
        self.current_note_id = None
        self.is_preview = False
        self.manager.current = "notes"
    
    def _refresh_preview_if_active(self):
        if self.is_preview:
            self.show_preview_mode()