from datetime import datetime
from kivymd.uix.screen import MDScreen
from kivy.utils import get_color_from_hex
from kivymd.app import MDApp
from kivy.properties import ListProperty
from kivy.metrics import dp
from kivy.uix.behaviors import ButtonBehavior
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.label import MDIcon

from theme.theme_manager import theme_manager
from theme.palettes import (
    BACKGROUND, CARD_PRIMARY, CARD_SECONDARY,
    TEXT_PRIMARY, TEXT_SECONDARY, ACCENT, BORDER, BUTTON
)
from theme.themed_screen import ThemedScreenMixin
from widgets.dashboard_tile import DashboardTile

from database.planner_queries import get_today_tasks, get_continue_studying, get_next_event

# Maps activity_type -> icon, since tasks created via different Quick
# Add options ("Study Session" / "Event" / "Task" / "Shopping") should
# read differently at a glance on Home, even though they're all just
# rows from the same tasks table.
ACTIVITY_ICONS = {
    "study": "brain",
    "event": "calendar-outline",
    "task": "checkbox-marked-outline",
    "shopping": "cart-outline",
}


class TappableRow(ButtonBehavior, MDBoxLayout):
    """A today-plan row that can be tapped to open its ActivityDetailScreen."""
    pass


class HomeScreen(ThemedScreenMixin, MDScreen):

    divider_color = ListProperty([0, 0, 0, 0])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(on_kv_post=lambda *x: self.apply_theme())
        self._continue_studying_task_id = None

    THEME_MAP = {
        "self":              ("md_bg_color", BACKGROUND),
        "drawer_layout":     ("md_bg_color", BACKGROUND),
        "greeting_label":    ("text_color", TEXT_PRIMARY),
        "date_label":        ("text_color", TEXT_SECONDARY),
        "menu_button":       ("icon_color", TEXT_PRIMARY),
        "today_plan_card":   ("md_bg_color", CARD_PRIMARY),
    }

    def on_pre_enter(self, *args):
        self.apply_theme()
        self.set_greeting()
        self.refresh_stats()
        self.build_today_plan()

    def on_theme_applied(self):
        if hasattr(self.ids.up_next_tile, "apply_theme"):
            self.ids.up_next_tile.apply_theme()
    #    self.divider_color = get_color_from_hex(theme_manager.get_color(BORDER))

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

    def build_today_plan(self):
        self.ids.today_plan_list.clear_widgets()

        app = MDApp.get_running_app()
        user_id = getattr(app, "user_id", 1)
        today_str = datetime.now().strftime("%Y-%m-%d")

        tasks = get_today_tasks(user_id, today_str)

        text_color = get_color_from_hex(theme_manager.get_color(TEXT_PRIMARY))
        subtext_color = get_color_from_hex(theme_manager.get_color(TEXT_SECONDARY))

        if not tasks:
            empty_label = MDLabel(
                text="Nothing planned for today",
                font_style="Body", role="small",
                theme_text_color="Custom", text_color=subtext_color,
                size_hint_y=None, height=dp(28),
            )
            self.ids.today_plan_list.add_widget(empty_label)
            return

        for task in tasks:
            icon_name = ACTIVITY_ICONS.get(task["activity_type"], "checkbox-marked-outline")

            # Build the "note note · focus session" subtext -- this
            # one line is what actually sells "everything is linked"
            # on Home without opening anything.
            meta_parts = []
            if task["note_count"]:
                meta_parts.append(f"{task['note_count']} note{'s' if task['note_count'] != 1 else ''}")
            if task["pomodoro_completed"]:
                meta_parts.append(f"{task['pomodoro_completed']} focus session{'s' if task['pomodoro_completed'] != 1 else ''}")
            meta_text = " · ".join(meta_parts)

            row = TappableRow(
                orientation="vertical", spacing=dp(2),
                size_hint_y=None, height=dp(44) if meta_text else dp(28),
            )
            row.bind(on_release=lambda inst, tid=task["id"]: self.open_task_detail(tid))

            title_row = MDBoxLayout(orientation="horizontal", spacing=dp(10), size_hint_y=None, height=dp(28))
            title_row.add_widget(MDIcon(
                icon=icon_name,
                theme_text_color="Custom", text_color=subtext_color,
                size_hint=(None, None), size=(dp(24), dp(24)),
            ))

            title_label = MDLabel(
                text=task["title"], font_style="Body", role="small",
                size_hint_x=1, shorten=True, shorten_from="right",
                theme_text_color="Custom", text_color=text_color,
            )
            title_label.bind(width=lambda inst, w: setattr(inst, "text_size", (w, None)))

            due_label = MDLabel(
                text=task["due_date"] or "", font_style="Label", role="small",
                halign="right", size_hint_x=None, width=dp(80),
                theme_text_color="Custom", text_color=subtext_color,
            )

            title_row.add_widget(title_label)
            title_row.add_widget(due_label)
            row.add_widget(title_row)

            if meta_text:
                meta_label = MDLabel(
                    text=meta_text, font_style="Label", role="small",
                    size_hint_x=1, theme_text_color="Custom", text_color=subtext_color,
                    padding=(dp(34), 0),
                )
                row.add_widget(meta_label)

            self.ids.today_plan_list.add_widget(row)

    def open_task_detail(self, task_id):
        detail = self.manager.get_screen("activity_detail")
        detail.current_task_id = task_id
        self.manager.current = "activity_detail"

    def refresh_stats(self):
        app = MDApp.get_running_app()
        user_id = getattr(app, "user_id", 1)

        self.ids.continue_studying_container.clear_widgets()
        self._continue_studying_task_id = None

        continue_studying = get_continue_studying(user_id)
        if continue_studying:
            self._continue_studying_task_id = continue_studying["task_id"]

            label = MDLabel(
                text="Continue Studying",
                theme_text_color="Custom",
                text_color=get_color_from_hex(theme_manager.get_color(TEXT_PRIMARY)),
                font_style="Title", role="small",
                adaptive_height=True,
            )
            
            tile = DashboardTile(
                label=continue_studying["task_title"],
                subtitle="Resume focus session",
                icon_name="book-open-page-variant-outline",
                size_hint_y=None,
                height=dp(110),
            )
            
            tile.on_release = self.resume_studying
            if hasattr(tile, "apply_theme"):
                tile.apply_theme()

            self.ids.continue_studying_container.add_widget(label)
            self.ids.continue_studying_container.add_widget(tile)

        next_event = get_next_event(user_id)
        if next_event:
            due_date, due_time = next_event["due_date"].split(" ")
            self.ids.up_next_tile.label = next_event["title"]
            self.ids.up_next_tile.subtitle = due_time
            self._next_event_id = next_event["id"]

            due_datetime = datetime.strptime(next_event["due_date"], "%Y-%m-%d %H:%M")
            minutes_until = int((due_datetime - datetime.now()).total_seconds() // 60)

            if minutes_until < 60:
                self.ids.up_next_tile.stat_number = str(max(minutes_until, 0))
                self.ids.up_next_tile.stat_label = "min"
            else:
               self.ids.up_next_tile.stat_number = str(minutes_until // 60)
               self.ids.up_next_tile.stat_label = "hr" if minutes_until // 60 == 1 else "hrs"
        else:
            self.ids.up_next_tile.label = "Nothing scheduled"
            self.ids.up_next_tile.subtitle = " "
            self.ids.up_next_tile.stat_number = ""
            self.ids.up_next_tile.stat_label = ""
            self._next_event_id = None
            
    def resume_studying(self):
      if self._continue_studying_task_id is None:
          return
      timer = self.manager.get_screen("timer")
      timer.current_task_id = self._continue_studying_task_id
      self.manager.current = "timer"        
            
    def go_to(self, screen_name):
        self.manager.current = screen_name

    def open_settings(self):
        self.manager.current = "settings"