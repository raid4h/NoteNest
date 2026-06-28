from kivymd.uix.screen import MDScreen
from theme.theme_manager import theme_manager

class SettingsScreen(MDScreen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.bind(on_kv_post=lambda *x: self.apply_theme())

    #appearance settings
    def set_light_theme(self):
        theme_manager.set_light_theme()
        self.apply_theme()

    def set_dark_theme(self):
        theme_manager.set_dark_theme()
        self.apply_theme()

    def set_pink_theme(self):
        theme_manager.set_pink_theme()
        self.apply_theme()

    def apply_theme(self):

        self.md_bg_color = theme_manager.get_color("#F7F1E6")

        self.ids.title_label.text_color = theme_manager.get_color("#4A3426")

        self.ids.subtitle_label.text_color = theme_manager.get_color("#8A5A2B")

        self.ids.appearance_card.md_bg_color = theme_manager.get_color("#EBD6A7")

        self.ids.account_card.md_bg_color = theme_manager.get_color("#EBD6A7")

        self.ids.notification_card.md_bg_color = theme_manager.get_color("#EBD6A7")

        self.ids.about_card.md_bg_color = theme_manager.get_color("#EBD6A7")

        self.ids.light_button.md_bg_color = theme_manager.get_color("#4A3426")

        self.ids.dark_button.md_bg_color = theme_manager.get_color("#4A3426")

        self.ids.pink_button.md_bg_color = theme_manager.get_color("#4A3426")

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
        pass

    # Future implementation (after Firebase setup)
    #
    # def login(self):
    #     pass
    #
    # def signup(self):
    #     pass
