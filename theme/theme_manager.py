from theme.palettes import LIGHT, DARK, PINK


class ThemeManager:

    def __init__(self):
        self.current_theme = "light"

    def set_light_theme(self):
        self.current_theme = "light"

    def set_dark_theme(self):
        self.current_theme = "dark"

    def set_pink_theme(self):
        self.current_theme = "pink"

    def get_color(self, color):

        color = color.upper()

        if self.current_theme == "light":
            return LIGHT.get(color, color)

        elif self.current_theme == "dark":
            return DARK.get(color, color)

        elif self.current_theme == "pink":
            return PINK.get(color, color)

        return color


theme_manager = ThemeManager()
