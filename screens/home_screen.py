import random
from datetime import datetime, timedelta
from kivymd.uix.screen import MDScreen
from database.notes_queries import get_all_notes
from database.task_queries import get_tasks_by_date
from kivy.utils import get_color_from_hex
from kivymd.app import MDApp
from kivy.properties import ListProperty

from theme.theme_manager import theme_manager
from theme.palettes import (
    BACKGROUND, CARD_PRIMARY, CARD_SECONDARY,
    TEXT_PRIMARY, TEXT_SECONDARY, ACCENT, BORDER, BUTTON
)
from theme.themed_screen import ThemedScreenMixin
from widgets.dashboard_tile import DashboardTile, SmallTile
from assets.data.home_quotes import QUOTES
from widgets.streak import Streak



class HomeScreen(ThemedScreenMixin, MDScreen):

    divider_color = ListProperty([0, 0, 0, 0])
 
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(on_kv_post=lambda *x: self.apply_theme())

    THEME_MAP = {
        "self":              ("md_bg_color", BACKGROUND),
        "drawer_layout":     ("md_bg_color", BACKGROUND),
        "greeting_label":    ("text_color", TEXT_PRIMARY),
        "date_label":        ("text_color", TEXT_SECONDARY),
        "menu_button":       ("icon_color", TEXT_PRIMARY),
        "quote_card":        ("md_bg_color", CARD_SECONDARY),
        "quote_label":       ("text_color", TEXT_PRIMARY),
        "streak_title":       ("text_color", TEXT_PRIMARY),
        "streak_card":       ("md_bg_color", CARD_PRIMARY),
        "last_edited_card":  ("md_bg_color", CARD_PRIMARY),
        "last_edited_label": ("text_color", TEXT_PRIMARY),
        "last_edited_static_label": ("text_color", TEXT_PRIMARY),
    }
     
    def on_pre_enter(self, *args):
        self.apply_theme()
        self.set_greeting()
        self.set_random_quote()
        self.refresh_stats()
        self.build_streak()

    def on_theme_applied(self):
        for tile in (self.ids.notes_tile, self.ids.pomodoro_tile, self.ids.tasks_tile):
            if hasattr(tile, "apply_theme"):
                tile.apply_theme()
        self.build_streak()
        self.divider_color = get_color_from_hex(theme_manager.get_color(BORDER))

    def set_greeting(self):
        hour = datetime.now().hour
        if hour < 12:
            greeting = "Good morning"
        elif hour < 18:
            greeting = "Good afternoon"
        else:
            greeting = "Good evening"
        self.ids.greeting_label.text = greeting
        self.ids.date_label.text = datetime.now().strftime("%A, %d %B")

    def set_random_quote(self):
        self.ids.quote_label.text = f'"{random.choice(QUOTES)}"'
    
    def build_streak(self):
        app = MDApp.get_running_app()
        notebook_id = getattr(app, "notebook_id", 1)
        self.ids.streak_row.clear_widgets()

        try:
            notes = get_all_notes(notebook_id)
            active_dates = {n[7][:10] for n in notes if n[7]}
        except Exception:
            active_dates = set()
        today = datetime.now().date()
        for i in range(6, -1, -1):
            day = today - timedelta(days=i)
            day_str = day.strftime("%Y-%m-%d")
            letter = day.strftime("%a")[0]
            dot = Streak(day_letter=letter, is_active=day_str in active_dates)
            self.ids.streak_row.add_widget(dot)
            dot.apply_theme(
                theme_manager.get_color(BUTTON),
                theme_manager.get_color(CARD_SECONDARY),
                theme_manager.get_color(TEXT_SECONDARY),
            )
    
    def refresh_stats(self):
        app = MDApp.get_running_app()
        notebook_id = getattr(app, "notebook_id", 1)   # adjust if you store this elsewhere
        user_id = getattr(app, "user_id", 1)             # adjust if you store this elsewhere

        # Notes count + last edited (one query, reused for both)
        try:
            notes = get_all_notes(notebook_id)
            note_count = len(notes)
            self.ids.notes_tile.stat_number = str(note_count)
            self.ids.notes_tile.stat_label = "note" if note_count == 1 else "notes"

            if notes:
               most_recent = max(notes, key=lambda n: n[7])  # index 7 = updated_at
               self.ids.last_edited_label.text = most_recent[2]  # index 2 = title
            else:
               self.ids.last_edited_label.text = "No notes yet"
        except Exception:
            self.ids.notes_tile.stat_number = "--"
            self.ids.notes_tile.stat_label = "notes"

        # Tasks due today
        try:
            today_str = datetime.now().strftime("%Y-%m-%d")
            due_today = [
                task
                for task in get_tasks_by_date(today_str)
                if not task.get("completed", False)
            ]
            due_count = len(due_today)
            self.ids.tasks_tile.stat_text = f"{due_count} due today" if due_count else "Nothing due today"
        except Exception:
            self.ids.tasks_tile.stat_text = "-- due today"

        # Pomodoro — no query module yet, stays a placeholder
        self.ids.pomodoro_tile.stat_text = "-- sessions today"

    def go_to(self, screen_name):
        self.manager.current = screen_name

    def open_settings(self):
        self.manager.current = "settings"