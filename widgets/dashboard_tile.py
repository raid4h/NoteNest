from kivy.properties import StringProperty
from kivy.uix.behaviors import ButtonBehavior
from kivymd.uix.card import MDCard
from kivymd.app import MDApp

from theme.theme_manager import theme_manager
from theme.palettes import CARD_PRIMARY, TEXT_PRIMARY, TEXT_SECONDARY, BUTTON


class DashboardTile(MDCard):
    """
    One clickable card on the Home Screen.

    Example:
    Notes card -> opens Notes screen
    Pomodoro card -> opens Timer screen
    Tasks & Calendar card -> opens Calendar screen
    """

    label = StringProperty("")
    subtitle = StringProperty("")
    icon_name = StringProperty("note-outline")
    target_screen = StringProperty("")

    def on_release(self):
        """
        Runs when the card is clicked.
        It changes the screen.
        """

        app = MDApp.get_running_app()

        if app and app.root and self.target_screen:
            app.root.current = self.target_screen

    def apply_theme(self):
        """
        Apply NoteNest theme colors to this card.
        """

        self.md_bg_color = theme_manager.get_color(CARD_PRIMARY)

        if "tile_label" in self.ids:
            self.ids.tile_label.text_color = theme_manager.get_color(TEXT_PRIMARY)

        if "tile_subtitle" in self.ids:
            self.ids.tile_subtitle.text_color = theme_manager.get_color(TEXT_SECONDARY)

        if "tile_icon" in self.ids:
            self.ids.tile_icon.icon_color = theme_manager.get_color(BUTTON)