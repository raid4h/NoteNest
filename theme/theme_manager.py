# ThemeManager is an EventDispatcher, which means it can hold Kivy
# Properties. theme_name is a StringProperty, so any object can
# "subscribe" to it via .bind() and get notified automatically
# whenever the theme changes — no manual refresh loop needed.

from kivy.event import EventDispatcher
from kivy.properties import StringProperty

from theme.palettes import DEFAULT, DARK, CREAM, MATCHA, MONOCHROME

_PALETTES = {
    "default": DEFAULT,
    "dark": DARK,
    "cream": CREAM,
    "matcha": MATCHA,
    "monochrome": MONOCHROME,
}


class ThemeManager(EventDispatcher):

    theme_name = StringProperty("default")

    def set_theme(self, name):
        if name in _PALETTES:
            self.theme_name = name

    def set_default_theme(self):
        self.set_theme("default")

    def set_dark_theme(self):
        self.set_theme("dark")

    def set_cream_theme(self):
        self.set_theme("cream")

    def set_matcha_theme(self):
        self.set_theme("matcha")

    def set_monochrome_theme(self):
        self.set_theme("monochrome")

    def get_color(self, token):
        return _PALETTES[self.theme_name].get(token, token)


theme_manager = ThemeManager()