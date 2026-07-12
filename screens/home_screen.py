# screens/home_screen.py
# Main dashboard screen — shows the app's features as cards.
# Tapping a card switches the ScreenManager to that feature's screen.

from kivymd.uix.screen import MDScreen

from theme.theme_manager import theme_manager
from theme.palettes import BACKGROUND, TEXT_PRIMARY, TEXT_SECONDARY

# Importing DashboardTile registers it with Kivy's Factory.
# Without this, app.kv may throw "Unknown class <DashboardTile>".
from widgets.dashboard_tile import DashboardTile


class HomeScreen(MDScreen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # on_kv_post runs after the KV layout is built.
        # We need this because self.ids is not ready inside __init__.
        self.bind(on_kv_post=lambda *x: self.apply_theme())

    def on_pre_enter(self, *args):
        """
        Runs every time the Home screen becomes visible.
        This helps theme changes show immediately.
        """

        self.apply_theme()

    def apply_theme(self):
        """
        Apply the selected NoteNest theme to the Home screen.
        """

        self.md_bg_color = theme_manager.get_color(BACKGROUND)

        self.ids.drawer_layout.md_bg_color = theme_manager.get_color(BACKGROUND)

        self.ids.drawer_title.text_color = theme_manager.get_color(TEXT_PRIMARY)
        self.ids.menu_button.icon_color = theme_manager.get_color(TEXT_PRIMARY)

        self.ids.home_label.text_color = theme_manager.get_color(TEXT_PRIMARY)

        if "home_subtitle" in self.ids:
            self.ids.home_subtitle.text_color = theme_manager.get_color(TEXT_SECONDARY)

        # Tiles do not have separate ids, so we loop over the tile container.
        for tile in self.ids.tiles_row.children:
            if hasattr(tile, "apply_theme"):
                tile.apply_theme()

    def open_settings(self):
        """
        Open the Settings screen from the gear button.
        """

        self.manager.current = "settings"