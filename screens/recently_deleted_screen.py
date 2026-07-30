# screens/recently_deleted_screen.py
# Lists notes that were deleted from the editor. Each one can be
# Restored (recreated in the database) or permanently removed via
# Delete Forever. Backed entirely by trash_store.py's local JSON file,
# not the database.

from kivymd.uix.screen import MDScreen
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDIconButton
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout

import trash_store
from database.notes_queries import create_notes

from theme.theme_manager import theme_manager
from theme.themed_screen import ThemedScreenMixin
from theme.palettes import BACKGROUND, CARD_PRIMARY, CARD_SECONDARY, TEXT_PRIMARY, TEXT_SECONDARY


class RecentlyDeletedScreen(ThemedScreenMixin, MDScreen):

    THEME_MAP = {
        "self":         ("md_bg_color", BACKGROUND),
        "back_button":  ("icon_color", TEXT_PRIMARY),
        "header_label": ("text_color", TEXT_PRIMARY),
    }

    def go_home(self):
        self.manager.current = "notes"

    def on_enter(self):
        self.load_trash()

    def on_theme_applied(self):
        self.load_trash()

    def load_trash(self):
        self.ids.trash_list.clear_widgets()
        entries = trash_store.get_trash_entries()

        if not entries:
            empty_label = MDLabel(
                text="No recently deleted notes.",
                halign="center",
                theme_text_color="Custom",
                text_color=theme_manager.get_color(TEXT_SECONDARY),
                size_hint_y=None,
                height=dp(60),
            )
            self.ids.trash_list.add_widget(empty_label)
            return

        for entry in entries:
            self.ids.trash_list.add_widget(self._build_trash_card(entry))

    def _build_trash_card(self, entry):
        card = MDCard(
            orientation="vertical",
            padding=dp(14),
            spacing=dp(6),
            size_hint_y=None,
            height=dp(140),
            radius=[14],
            elevation=1,
            md_bg_color=theme_manager.get_color(CARD_PRIMARY),
        )

        title_label = MDLabel(
            text=entry["title"] or "Untitled",
            font_style="Title",
            role="medium",
            theme_text_color="Custom",
            text_color=theme_manager.get_color(TEXT_PRIMARY),
            adaptive_height=True,
            shorten=True,
            shorten_from="right",
        )
        # Needed for shorten/ellipsis to work, and keeps this label to
        # exactly one line regardless of how long the title is -- same
        # pattern used for the delete-confirmation popup's message text.
        title_label.bind(width=lambda inst, val: setattr(inst, "text_size", (val, None)))
        card.add_widget(title_label)

        deleted_label = MDLabel(
            text=f"Deleted {entry['deleted_at']}",
            font_style="Body",
            role="small",
            theme_text_color="Custom",
            text_color=theme_manager.get_color(TEXT_SECONDARY),
            adaptive_height=True,
        )
        card.add_widget(deleted_label)

        button_row = BoxLayout(
            orientation="horizontal", size_hint_y=None, height=dp(40), spacing=dp(16)
        )

        # Each action is now an icon PAIRED with a text label, instead
        # of a bare icon -- restore and delete-forever look too similar
        # as icons alone to tell apart at a glance.
        restore_box = BoxLayout(orientation="horizontal", size_hint_x=None, width=dp(110), spacing=dp(2))
        restore_button = MDIconButton(
            icon="delete-restore",
            theme_icon_color="Custom",
            icon_color=theme_manager.get_color(TEXT_PRIMARY),
        )
        restore_button.bind(on_release=lambda *_: self.restore_note(entry["trash_id"]))
        restore_label = MDLabel(
            text="Restore",
            theme_text_color="Custom",
            text_color=theme_manager.get_color(TEXT_PRIMARY),
            font_style="Body",
            role="small",
            valign="middle",
        )
        restore_box.add_widget(restore_button)
        restore_box.add_widget(restore_label)
        button_row.add_widget(restore_box)

        delete_forever_box = BoxLayout(orientation="horizontal", size_hint_x=None, width=dp(150), spacing=dp(2))
        delete_forever_button = MDIconButton(
            icon="delete-forever",
            theme_icon_color="Custom",
            icon_color=theme_manager.get_color(TEXT_PRIMARY),
        )
        delete_forever_button.bind(on_release=lambda *_: self.delete_forever(entry["trash_id"]))
        delete_forever_label = MDLabel(
            text="Delete Forever",
            theme_text_color="Custom",
            text_color=theme_manager.get_color(TEXT_PRIMARY),
            font_style="Body",
            role="small",
            valign="middle",
        )
        delete_forever_box.add_widget(delete_forever_button)
        delete_forever_box.add_widget(delete_forever_label)
        button_row.add_widget(delete_forever_box)

        card.add_widget(button_row)
        return card

    def restore_note(self, trash_id):
        entry = trash_store.get_trash_entry(trash_id)
        if entry is None:
            return

        # Recreates the note in the database -- it gets a brand-new
        # note id (the original one is gone for good), but the title
        # and content come back exactly as they were.
        create_notes(
            entry["notebook_id"],
            entry["title"],
            entry["content"],
            category_id=entry["category_id"],
        )
        trash_store.remove_from_trash(trash_id)
        self.load_trash()

    def delete_forever(self, trash_id):
        # The note is already gone from the database -- this just
        # removes its recovery snapshot. No way back after this.
        trash_store.remove_from_trash(trash_id)
        self.load_trash()