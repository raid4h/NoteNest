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
        "theme_card":          ("md_bg_color", CARD_PRIMARY),
        "theme_section_label": ("text_color", ACCENT),
        "light_button":  ("md_bg_color", BUTTON),
        "dark_button":   ("md_bg_color", BUTTON),
        "floral_button": ("md_bg_color", BUTTON),
        "cyber_button":  ("md_bg_color", BUTTON),

        # Google Account (identity only — sign in / sign out)
        "account_card":           ("md_bg_color", CARD_SECONDARY),
        "account_section_label":  ("text_color", ACCENT),
        "connect_google_row_label": ("text_color", TEXT_PRIMARY),
        "connect_google_row_subtitle": ("text_color", TEXT_SECONDARY),
        "logout_row_label":       ("text_color", TEXT_PRIMARY),

        # Backup & Restore (data actions — this is the backup_manager's UI surface)
        "backup_card":          ("md_bg_color", CARD_PRIMARY),
        "backup_section_label": ("text_color", ACCENT),
        "backup_now_row_label":       ("text_color", TEXT_PRIMARY),
        "restore_row_label":          ("text_color", TEXT_PRIMARY),
        "restore_row_subtitle":       ("text_color", TEXT_SECONDARY),
        "auto_backup_row_label":      ("text_color", TEXT_PRIMARY),
        "auto_backup_row_subtitle":   ("text_color", TEXT_SECONDARY),
        "export_row_label":           ("text_color", TEXT_PRIMARY),
        "import_row_label":           ("text_color", TEXT_PRIMARY),

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
        "connect_google_chevron": ("icon_color", TEXT_SECONDARY),
        "logout_chevron":         ("icon_color", TEXT_SECONDARY),
        "backup_now_chevron":     ("icon_color", TEXT_SECONDARY),
        "restore_chevron":        ("icon_color", TEXT_SECONDARY),
        "export_chevron":         ("icon_color", TEXT_SECONDARY),
        "import_chevron":         ("icon_color", TEXT_SECONDARY),
        "privacy_chevron":        ("icon_color", TEXT_SECONDARY),
        "rate_chevron":           ("icon_color", TEXT_SECONDARY),
        "privacy_policy_chevron": ("icon_color", TEXT_SECONDARY),
    }

    # ── theme ──
    def set_light_theme(self):
        theme_manager.set_light_theme()

    def set_dark_theme(self):
        theme_manager.set_dark_theme()

    def set_floral_theme(self):
        theme_manager.set_floral_theme()

    def set_cyberpunk_theme(self):
        theme_manager.set_cyberpunk_theme()

    # ── google account (identity) ──
    # Implemented in the backend roadmap's Phase 4 (services/auth_service.py).
    def connect_google_account(self):
        pass

    def logout(self):
        pass

    # ── backup & restore (data) ──
    # Implemented in Phase 3 (manual_export.py) and Phase 6
    # (backup_manager.py, once auth + drive_client exist).
    def backup_now(self):
        pass

    def restore_backup(self):
        pass

    def toggle_auto_backup(self):
        pass

    def export_to_file(self):
        pass

    def import_from_file(self):
        pass

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