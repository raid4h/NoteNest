from theme.theme_manager import theme_manager


class ThemedScreenMixin:

    THEME_MAP = {}

    def on_kv_post(self, base_widget):
        super().on_kv_post(base_widget)
        theme_manager.bind(theme_name=self._on_theme_changed)
        self.apply_theme()

    def _on_theme_changed(self, instance, value):
        self.apply_theme()

    def apply_theme(self):
        for widget_id, (prop_name, token) in self.THEME_MAP.items():
            widget = self if widget_id == "self" else self.ids.get(widget_id)
            if widget is None:
                continue
            setattr(widget, prop_name, theme_manager.get_color(token))
        if hasattr(self, "on_theme_applied"):
            try:
                self.on_theme_applied()
            except Exception as e:
                print(f"[ThemedScreenMixin] on_theme_applied failed for {self}: {e}")