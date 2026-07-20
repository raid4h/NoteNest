# screens/notes_screen.py
# The notes list. 

from kivymd.uix.screen import MDScreen
from widgets.note_card import NoteCard
from kivy.metrics import dp
from kivy.properties import BooleanProperty
from kivy.uix.modalview import ModalView
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDButton, MDButtonText

from database.notes_queries import (
    get_all_notes, search_notes as db_search_notes, archive_notes,
    pin_notes, get_notes_by_id, delete_notes,
)
import trash_store
from datetime import datetime, timezone
import re
from screens.note_editor_screen import META_PATTERN, IMAGE_TOKEN_PATTERN

from theme.theme_manager import theme_manager
from theme.themed_screen import ThemedScreenMixin
from theme.palettes import BACKGROUND, TEXT_PRIMARY, CARD_SECONDARY, ACCENT

# Week 3 TEMP: every note needs a notebook_id, but there's no notebook
# creation/selection screen yet. Using 1 as a placeholder until Tabshira
# confirms how notebooks get created (one default per user? a picker?).
DEFAULT_NOTEBOOK_ID = 1

def _format_last_edited(updated_at):
    if not updated_at:
        return ""

    try:
        # SQLite's CURRENT_TIMESTAMP stores time in UTC, not this
        # device's local time zone -- parse it as UTC first, then
        # convert to whatever time zone the machine is actually set
        # to, instead of displaying the raw UTC value as if it were
        # local time (which is why it looked 6 hours off before).
        dt_utc = datetime.strptime(updated_at, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
        dt_local = dt_utc.astimezone()
    except (ValueError, TypeError):
        return f"Edited {updated_at}"

    now_local = datetime.now().astimezone()
    delta = now_local - dt_local
    seconds = delta.total_seconds()

    if seconds < 0:
        # Guards against a negative gap from clock rounding/skew --
        # treat it as "just now" instead of showing something confusing
        # like "-2 seconds ago".
        seconds = 0

    if seconds < 60:
        return "Edited just now"

    minutes = int(seconds // 60)
    if minutes < 60:
        return f"Edited {minutes} minute{'s' if minutes != 1 else ''} ago"

    hours = int(minutes // 60)
    if hours < 24:
        return f"Edited {hours} hour{'s' if hours != 1 else ''} ago"

    days = delta.days
    if days == 1:
        return "Edited yesterday"
    if days < 7:
        return f"Edited {days} days ago"

    # Older than a week -- switch to an actual date instead of an
    # ever-growing "X days ago" that stops being useful.
    return f"Edited {dt_local.strftime('%b %d, %Y')}"

def _clean_preview_text(content):
    # Strips internal formatting/metadata markers out of a note's raw
    # stored content, so the notes list preview shows clean readable
    # text instead of leaking implementation details like
    # {{meta:...}} or literal **/__/== characters to the user.
    if not content:
        return ""

    text = content

    # Strip the hidden per-note font/size/alignment marker at the start
    text = META_PATTERN.sub("", text)

    # Plain text instead of an emoji -- the default font used for note
    # card previews doesn't have that glyph, so it was showing as a
    # missing-character box instead of an actual camera icon.
    text = IMAGE_TOKEN_PATTERN.sub("[Photo] ", text)
    
    # Strip bold/underline/highlight/italic markers -- order matters,
    # same reasoning as convert_formatting_to_markup in the editor:
    # ** and __ must be handled before single *, or a leftover marker
    # gets misread as something else.
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text, flags=re.DOTALL)
    text = re.sub(r"__(.+?)__", r"\1", text, flags=re.DOTALL)
    text = re.sub(r"==(.+?)==", r"\1", text, flags=re.DOTALL)
    text = re.sub(r"\*(.+?)\*", r"\1", text, flags=re.DOTALL)

    return text.strip()

                    
class NotesScreen(ThemedScreenMixin,MDScreen):
    sort_by = "date"
    selection_mode = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Ids of notes currently checked while in bulk-select mode --
        # cleared whenever selection mode is switched on or off.
        self.selected_note_ids = set()

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

    def open_recently_deleted(self):
        self.manager.current = "recently_deleted"

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
                title=note[2],                        # title
                preview=_clean_preview_text(note[3]),  # cleaned content
                note_id=note[0],         # id
                is_pinned=bool(note[4]),
                last_edited=_format_last_edited(note[7]),  # updated_at
                selection_mode=self.selection_mode,
                is_selected=note[0] in self.selected_note_ids,
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
                title=note[2],                        # title
                preview=_clean_preview_text(note[3]),  # cleaned content
                note_id=note[0],         # id
                is_pinned=bool(note[4]),
                last_edited=_format_last_edited(note[7]),  # updated_at
                selection_mode=self.selection_mode,
                is_selected=note[0] in self.selected_note_ids,
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

    def toggle_pin_note(self, note_id, is_pinned):
        # is_pinned here is the CURRENT state, passed up from the card
        # before it changes -- flip it and save the opposite value.
        new_value = 0 if is_pinned else 1
        pin_notes(note_id, new_value)
        self.load_notes()
    
    def toggle_selection_mode(self):
        self.selection_mode = not self.selection_mode
        self.selected_note_ids = set()
        self._update_selection_label()
        self.load_notes()

    def on_card_selection_changed(self, note_id, is_selected):
        if is_selected:
            self.selected_note_ids.add(note_id)
        else:
            self.selected_note_ids.discard(note_id)
        self._update_selection_label()

    def _update_selection_label(self):
        if "selection_count_label" in self.ids:
            count = len(self.selected_note_ids)
            self.ids.selection_count_label.text = f"{count} selected"

    def delete_selected_notes(self):
        if not self.selected_note_ids:
            return
        self._show_bulk_delete_confirmation()

    def _show_bulk_delete_confirmation(self):
        count = len(self.selected_note_ids)
        card = MDCard(
            orientation="vertical", padding=dp(20), spacing=dp(16),
            radius=[16], size_hint=(None, None), size=(dp(300), dp(160)),
        )
        warning_label = MDLabel(
            text=f"Delete {count} note{'s' if count != 1 else ''}? This can't be undone.",
            halign="center", theme_text_color="Custom", size_hint_y=None,
        )
        warning_label.bind(width=lambda inst, val: setattr(inst, "text_size", (val, None)))
        warning_label.bind(texture_size=lambda inst, val: setattr(inst, "height", val[1]))
        card.add_widget(warning_label)

        button_row = BoxLayout(orientation="horizontal", spacing=dp(12), size_hint_y=None, height=dp(48))
        cancel_button = MDButton(MDButtonText(text="Cancel"), style="outlined")
        cancel_button.bind(on_release=lambda *_: modal.dismiss())
        confirm_button = MDButton(MDButtonText(text="Delete"), style="filled")
        confirm_button.bind(on_release=lambda *_: self._confirm_bulk_delete(modal))
        button_row.add_widget(cancel_button)
        button_row.add_widget(confirm_button)
        card.add_widget(button_row)

        modal = ModalView(
            size_hint=(None, None), size=(dp(300), dp(160)),
            auto_dismiss=True, background_color=(0, 0, 0, 0.5),
        )
        modal.add_widget(card)
        modal.open()

    def _confirm_bulk_delete(self, modal):
        modal.dismiss()
        # Snapshot each note into local trash before deleting, same
        # recovery mechanism as single-note deletion -- a bulk delete
        # is still recoverable from Recently Deleted afterward.
        for note_id in list(self.selected_note_ids):
            note = get_notes_by_id(note_id)
            if note is not None:
                trash_store.add_to_trash(
                    notebook_id=note[1], title=note[2],
                    content=note[3] or "", category_id=note[8],
                )
            delete_notes(note_id)

        self.selection_mode = False
        self.selected_note_ids = set()
        self.load_notes()