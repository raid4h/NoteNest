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
)


class SettingsScreen(ThemedScreenMixin, MDScreen):

    THEME_MAP = {
        "self":              ("md_bg_color", BACKGROUND),
        "title_label":       ("text_color", TEXT_PRIMARY),
        "subtitle_label":    ("text_color", TEXT_SECONDARY),
        "appearance_card":   ("md_bg_color", CARD_PRIMARY),
        "account_card":      ("md_bg_color", CARD_SECONDARY),
        "notification_card": ("md_bg_color", CARD_PRIMARY),
        "about_card":        ("md_bg_color", CARD_SECONDARY),
        "light_button":      ("md_bg_color", BUTTON),
        "dark_button":       ("md_bg_color", BUTTON),
        "pink_button":       ("md_bg_color", BUTTON),
        "cyber_button":      ("md_bg_color", BUTTON),
    }

    #appearance settings
    def set_light_theme(self):
        theme_manager.set_light_theme()

    def set_dark_theme(self):
        theme_manager.set_dark_theme()

    def set_pink_theme(self):
        theme_manager.set_floral_theme()

    def set_cyberpunk_theme(self):
        theme_manager.set_cyberpunk_theme()

    #account settings
    def update_account(self):
        pass

    def logout(self):
        pass

    #notification settings
    def toggle_notifications(self):
        pass

    #navigation settings
    def go_back(self):
        App.get_running_app().root.current = "home"

    # Future implementation (after Firebase setup)
    #
    # def login(self):
    #     pass
    #
    # def signup(self):
    #     pass