from kivymd.uix.screen import MDScreen
from kivy.app import App

from theme.theme_manager import theme_manager
from theme.themed_screen import ThemedScreenMixin
from theme.palettes import (
    BACKGROUND,
    CARD_PRIMARY,
    CARD_SECONDARY,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
    BUTTON,
    ACCENT,
)


class SettingsScreen(ThemedScreenMixin, MDScreen):

    THEME_MAP = {
        "self":           ("md_bg_color", BACKGROUND),
        "title_label":    ("text_color", TEXT_PRIMARY),
        "subtitle_label": ("text_color", TEXT_SECONDARY),
        "back_button":    ("icon_color", TEXT_PRIMARY),

        # Theme
        "theme_section_label": ("text_color", ACCENT),
        "default_button":    ("md_bg_color", BUTTON),
        "dark_button":       ("md_bg_color", BUTTON),
        "floral_button":     ("md_bg_color", BUTTON),
        "matcha_button":     ("md_bg_color", BUTTON),
        "monochrome_button": ("md_bg_color", BUTTON),

        # Backup & Restore -- Export/Import only. App is fully offline;
        # no Google account, no cloud backup/restore.
        "backup_card":          ("md_bg_color", CARD_PRIMARY),
        "backup_section_label": ("text_color", ACCENT),
        "export_row_label":     ("text_color", TEXT_PRIMARY),
        "import_row_label":     ("text_color", TEXT_PRIMARY),

        # Privacy
        "privacy_card":          ("md_bg_color", CARD_SECONDARY),
        "privacy_section_label": ("text_color", ACCENT),
        "privacy_row_label":     ("text_color", TEXT_PRIMARY),
        "privacy_row_subtitle":  ("text_color", TEXT_SECONDARY),

        # Notifications
        "notifications_card":          ("md_bg_color", CARD_PRIMARY),
        "notifications_section_label": ("text_color", ACCENT),
        "notifications_row_label":     ("text_color", TEXT_PRIMARY),

        # About
        "about_card":                ("md_bg_color", CARD_SECONDARY),
        "about_section_label":       ("text_color", ACCENT),
        "rate_row_label":            ("text_color", TEXT_PRIMARY),
        "privacy_policy_row_label":  ("text_color", TEXT_PRIMARY),
        "footer_label":              ("text_color", TEXT_SECONDARY),

        # chevrons (row-tap affordance)
        "export_chevron":         ("icon_color", TEXT_SECONDARY),
        "import_chevron":         ("icon_color", TEXT_SECONDARY),
        "privacy_chevron":        ("icon_color", TEXT_SECONDARY),
        "rate_chevron":           ("icon_color", TEXT_SECONDARY),
        "privacy_policy_chevron": ("icon_color", TEXT_SECONDARY),
    }

    # ── theme ──
    def set_default_theme(self):
        theme_manager.set_default_theme()

    def set_dark_theme(self):
        theme_manager.set_dark_theme()

    def set_floral_theme(self):
        theme_manager.set_floral_theme()

    def set_monochrome_theme(self):
        theme_manager.set_monochrome_theme()

    def set_matcha_theme(self):
        theme_manager.set_matcha_theme()

    # ── backup: export/import only (offline app, no cloud) ──
    def export_to_file(self):
        # NOTE: the exported file is PLAIN, UNENCRYPTED JSON -- anyone
        # with access to it can read every note it contains.
        from services.manual_export import export_backup_to_file

        def on_success(file_path):
            print(f"Backup exported to {file_path}")
            # TODO: replace with real MDSnackbar/toast feedback.

        def on_error(exc):
            print(f"Export failed: {exc}")
            # TODO: real user-visible error feedback.

        export_backup_to_file(on_success, on_error)

    def import_from_file(self):
        from services.manual_export import import_backup_from_file

        def on_success():
            print("Backup imported successfully.")
            # TODO: real UI feedback, and consider refreshing/
            # navigating away from any screen showing now-stale data.

        def on_error(exc):
            print(f"Import failed: {exc}")
            # TODO: real UI feedback.

        import_backup_from_file(on_success, on_error)

    # ── privacy ──
    def open_privacy_settings(self):
        pass

    # ── notifications ──
    def toggle_notifications(self):
        pass

    # ── about ──
    def rate_app(self):
        pass

    def open_privacy_policy(self):
        pass

    # ── navigation ──
    def go_back(self):
        App.get_running_app().root.current = "home"