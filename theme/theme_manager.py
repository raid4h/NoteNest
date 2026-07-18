
# ThemeManager is now an EventDispatcher, which means it can hold
# Kivy Properties. theme_name is a StringProperty, so any object
# can "subscribe" to it via .bind() and get notified automatically
# whenever the theme changes — no manual refresh loop needed.

from kivy.event import EventDispatcher
from kivy.properties import StringProperty

from theme.palettes import LIGHT, DARK, FLORAL, CYBERPUNK

_PALETTES = {
    "light": LIGHT,
    "dark": DARK,
    "floral": FLORAL,
    "cyberpunk": CYBERPUNK,
}


class ThemeManager(EventDispatcher):

    #new stuff .bind()
    theme_name = StringProperty("light")

    def set_theme(self, name):
        if name in _PALETTES:
            self.theme_name = name

    def set_light_theme(self):
        self.set_theme("light")

    def set_dark_theme(self):
        self.set_theme("dark")

    def set_floral_theme(self):
        self.set_theme("floral")

    def set_cyberpunk_theme(self):
        self.set_theme("cyberpunk")

    def get_color(self, token):
        return _PALETTES[self.theme_name].get(token, token)


theme_manager = ThemeManager()