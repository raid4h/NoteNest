from kivy.properties import StringProperty
from kivymd.uix.card import MDCard
from kivymd.app import MDApp

from theme.theme_manager import theme_manager
from theme.palettes import CARD_PRIMARY, CARD_SECONDARY, TEXT_PRIMARY, TEXT_SECONDARY, BUTTON


class DashboardTile(MDCard):
    label = StringProperty("")
    subtitle = StringProperty("")
    stat_number = StringProperty("")
    stat_label = StringProperty("")
    icon_name = StringProperty("note-outline")
    target_screen = StringProperty("")

    def on_release(self):
        app = MDApp.get_running_app()
        if app and app.root and self.target_screen:
            app.root.current = self.target_screen

    def apply_theme(self):
        self.md_bg_color = theme_manager.get_color(CARD_PRIMARY)
        if "tile_label" in self.ids:
            self.ids.tile_label.text_color = theme_manager.get_color(TEXT_PRIMARY)
        if "tile_subtitle" in self.ids:
            self.ids.tile_subtitle.text_color = theme_manager.get_color(TEXT_SECONDARY)
        if "stat_number" in self.ids:
            self.ids.stat_number.text_color = theme_manager.get_color(BUTTON)
        if "stat_label" in self.ids:
            self.ids.stat_label.text_color = theme_manager.get_color(TEXT_SECONDARY)
        if "tile_icon" in self.ids:
            self.ids.tile_icon.icon_color = theme_manager.get_color(BUTTON)
        if "icon_container" in self.ids:
            self.ids.icon_container.md_bg_color = theme_manager.get_color(CARD_SECONDARY)


class SmallTile(MDCard):
    label = StringProperty("")
    stat_text = StringProperty("")
    icon_name = StringProperty("note-outline")
    target_screen = StringProperty("")
    accent_token = StringProperty("")

    def on_release(self):
        app = MDApp.get_running_app()
        if app and app.root and self.target_screen:
            app.root.current = self.target_screen

    def apply_theme(self):
        self.md_bg_color = theme_manager.get_color(CARD_PRIMARY)
        accent = theme_manager.get_color(self.accent_token) if self.accent_token else None

        if "tile_label" in self.ids:
            self.ids.tile_label.text_color = theme_manager.get_color(TEXT_PRIMARY)
        if "tile_stat" in self.ids:
            self.ids.tile_stat.text_color = accent if accent else theme_manager.get_color(TEXT_SECONDARY)
        if "tile_icon" in self.ids:
            self.ids.tile_icon.icon_color = accent if accent else theme_manager.get_color(BUTTON)
        if "icon_container" in self.ids:
            self.ids.icon_container.md_bg_color = theme_manager.get_color(CARD_SECONDARY)

