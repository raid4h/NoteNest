# ThemeManager is an EventDispatcher, which means it can hold Kivy
# Properties. theme_name is a StringProperty, so any object can
# "subscribe" to it via .bind() and get notified automatically
# whenever the theme changes — no manual refresh loop needed.

from kivy.event import EventDispatcher
from kivy.properties import StringProperty

from theme.palettes import CREAM, DARK, DEFAULT, MONOCHROME

_PALETTES = {
    "cream": CREAM,
    "dark": DARK,
    "default": DEFAULT,
    "monochrome": MONOCHROME,
}


class ThemeManager(EventDispatcher):

    # "default" is now the app's actual starting theme, per your
    # instruction to make the former Floral palette the default.
    theme_name = StringProperty("default")

    def set_theme(self, name):
        if name in _PALETTES:
            self.theme_name = name

    def set_cream_theme(self):
        self.set_theme("cream")

    def set_dark_theme(self):
        self.set_theme("dark")

    def set_default_theme(self):
        self.set_theme("default")

    def set_monochrome_theme(self):
        self.set_theme("monochrome")

    def get_color(self, token):
        return _PALETTES[self.theme_name].get(token, token)


theme_manager = ThemeManager()