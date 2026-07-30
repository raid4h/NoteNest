import calendar
import webbrowser
from datetime import datetime

from kivy.clock import Clock
from kivy.graphics import Color, Line, Rectangle, RoundedRectangle
from kivy.metrics import dp, sp
from kivy.properties import BooleanProperty, NumericProperty, ObjectProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
from kivy.utils import get_color_from_hex

from database.category_queries import create_category, get_all_categories
from database.task_queries import (
    create_tasks,
    get_all_task_dates,
    get_tasks_by_date,
    set_task_completed,
)
from services.notification_service import (
    collect_due_notifications,
    send_system_notification,
)
from theme.palettes import (
    ACCENT,
    BACKGROUND,
    BORDER,
    BUTTON,
    BUTTON_TEXT,
    CARD_PRIMARY,
    CARD_SECONDARY,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
)
from theme.theme_manager import theme_manager
from theme.themed_screen import ThemedScreenMixin


BUILT_IN_CATEGORIES = ("Study", "Life", "Health", "Work")
CREATE_CATEGORY_VALUE = "+ Create new category"


def theme_rgba(token):
    """Return a Kivy RGBA list for one semantic theme token."""
    return get_color_from_hex(theme_manager.get_color(token))


class ThemedLabel(Label):
    """Label that follows the app's ThemeManager."""

    color_token = StringProperty(TEXT_PRIMARY)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        theme_manager.bind(theme_name=self._refresh_theme)
        self._refresh_theme()

    def _refresh_theme(self, *_args):
        self.color = theme_rgba(self.color_token)


class RoundedThemePanel(BoxLayout):
    """Rounded container using semantic colors instead of hard-coded colors."""

    background_token = StringProperty(CARD_PRIMARY)
    border_token = StringProperty(BORDER)
    radius_value = NumericProperty(16)
    border_width = NumericProperty(1)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            self._panel_bg = Color(1, 1, 1, 1)
            self._panel_rect = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(self.radius_value)],
            )
            self._panel_border_color = Color(1, 1, 1, 1)
            self._panel_border = Line(
                rounded_rectangle=(
                    self.x,
                    self.y,
                    self.width,
                    self.height,
                    dp(self.radius_value),
                ),
                width=self.border_width,
            )

        self.bind(
            pos=self._update_canvas,
            size=self._update_canvas,
            radius_value=self._update_canvas,
        )
        theme_manager.bind(theme_name=self._refresh_theme)
        self._refresh_theme()

    def _update_canvas(self, *_args):
        self._panel_rect.pos = self.pos
        self._panel_rect.size = self.size
        self._panel_rect.radius = [dp(self.radius_value)]
        self._panel_border.rounded_rectangle = (
            self.x,
            self.y,
            self.width,
            self.height,
            dp(self.radius_value),
        )

    def _refresh_theme(self, *_args):
        self._panel_bg.rgba = theme_rgba(self.background_token)
        self._panel_border_color.rgba = theme_rgba(self.border_token)


class ThemeButton(Button):
    """Rounded text button with ThemeManager-driven colors."""

    background_token = StringProperty(CARD_SECONDARY)
    text_token = StringProperty(TEXT_PRIMARY)
    border_token = StringProperty(BORDER)
    radius_value = NumericProperty(12)

    def __init__(self, **kwargs):
        kwargs.setdefault("background_normal", "")
        kwargs.setdefault("background_down", "")
        kwargs.setdefault("background_color", (0, 0, 0, 0))
        kwargs.setdefault("size_hint_y", None)
        kwargs.setdefault("height", dp(44))
        super().__init__(**kwargs)

        with self.canvas.before:
            self._button_bg = Color(1, 1, 1, 1)
            self._button_rect = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(self.radius_value)],
            )
            self._button_border_color = Color(1, 1, 1, 1)
            self._button_border = Line(
                rounded_rectangle=(
                    self.x,
                    self.y,
                    self.width,
                    self.height,
                    dp(self.radius_value),
                ),
                width=1,
            )

        self.bind(
            pos=self._update_canvas,
            size=self._update_canvas,
            radius_value=self._update_canvas,
        )
        theme_manager.bind(theme_name=self._refresh_theme)
        self._refresh_theme()

    def _update_canvas(self, *_args):
        self._button_rect.pos = self.pos
        self._button_rect.size = self.size
        self._button_rect.radius = [dp(self.radius_value)]
        self._button_border.rounded_rectangle = (
            self.x,
            self.y,
            self.width,
            self.height,
            dp(self.radius_value),
        )

    def _refresh_theme(self, *_args):
        self._button_bg.rgba = theme_rgba(self.background_token)
        self._button_border_color.rgba = theme_rgba(self.border_token)
        self.color = theme_rgba(self.text_token)


class ThemedTextInput(TextInput):
    """Rounded single-line input that follows the active NoteNest palette."""

    radius_value = NumericProperty(10)

    def __init__(self, **kwargs):
        kwargs.setdefault("multiline", False)
        kwargs.setdefault("size_hint_y", None)
        kwargs.setdefault("height", dp(48))
        kwargs.setdefault("background_normal", "")
        kwargs.setdefault("background_active", "")
        kwargs.setdefault("background_color", (0, 0, 0, 0))
        kwargs.setdefault("padding", [dp(12), dp(13), dp(12), dp(10)])
        kwargs.setdefault("readonly", False)
        kwargs.setdefault("disabled", False)
        kwargs.setdefault("write_tab", False)
        kwargs.setdefault("cursor_blink", True)
        kwargs.setdefault("cursor_width", dp(1.4))
        super().__init__(**kwargs)

        with self.canvas.before:
            self._field_bg = Color(1, 1, 1, 1)
            self._field_rect = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(self.radius_value)],
            )
            self._field_border_color = Color(1, 1, 1, 1)
            self._field_border = Line(
                rounded_rectangle=(
                    self.x,
                    self.y,
                    self.width,
                    self.height,
                    dp(self.radius_value),
                ),
                width=1,
            )

        self.bind(
            pos=self._update_canvas,
            size=self._update_canvas,
            focus=self._refresh_theme,
        )
        theme_manager.bind(theme_name=self._refresh_theme)
        self._refresh_theme()

    def _update_canvas(self, *_args):
        self._field_rect.pos = self.pos
        self._field_rect.size = self.size
        self._field_border.rounded_rectangle = (
            self.x,
            self.y,
            self.width,
            self.height,
            dp(self.radius_value),
        )

    def _refresh_theme(self, *_args):
        self._field_bg.rgba = theme_rgba(CARD_SECONDARY)
        self._field_border_color.rgba = (
            theme_rgba(ACCENT) if self.focus else theme_rgba(BORDER)
        )

        # Values typed into light-theme fields stay solid black so editing,
        # selection and Backspace changes are always visible.
        light_theme = theme_manager.theme_name in {
            "default",
            "floral",
            "matcha",
        }
        self.foreground_color = (
            [0, 0, 0, 1] if light_theme else theme_rgba(TEXT_PRIMARY)
        )
        self.cursor_color = (
            [0, 0, 0, 1] if light_theme else theme_rgba(ACCENT)
        )

        hint = theme_rgba(TEXT_SECONDARY)
        self.hint_text_color = [hint[0], hint[1], hint[2], 0.72]
        accent = theme_rgba(ACCENT)
        self.selection_color = [accent[0], accent[1], accent[2], 0.38]


class SelectableThemeButton(ThemeButton):
    """Pill button used for category and priority selections."""

    selected = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(selected=self._refresh_theme)

    def _refresh_theme(self, *_args):
        if not hasattr(self, "_button_bg"):
            return
        self.background_token = ACCENT if self.selected else CARD_SECONDARY
        self.border_token = ACCENT if self.selected else BORDER
        super()._refresh_theme()


class OptionToggle(SelectableThemeButton):
    """Compact On/Off control with an ``active`` API."""

    active = BooleanProperty(False)

    def __init__(self, **kwargs):
        kwargs.setdefault("size_hint_x", None)
        kwargs.setdefault("width", dp(76))
        kwargs.setdefault("height", dp(38))
        kwargs.setdefault("font_size", sp(12))
        kwargs.setdefault("bold", True)
        super().__init__(**kwargs)
        self.bind(on_release=self._toggle)
        self.bind(active=self._sync_state)
        self._sync_state()

    def _toggle(self, *_args):
        self.active = not self.active

    def _sync_state(self, *_args):
        self.selected = self.active
        self.text = "On" if self.active else "Off"


class CalendarDayButton(ThemeButton):
    """Calendar date cell with selected/today/task states."""

    date_value = StringProperty("")
    is_today = BooleanProperty(False)
    has_tasks = BooleanProperty(False)
    selected = BooleanProperty(False)

    def __init__(self, **kwargs):
        kwargs.setdefault("size_hint_y", None)
        kwargs.setdefault("height", dp(34))
        kwargs.setdefault("font_size", sp(11))
        kwargs.setdefault("radius_value", 10)
        super().__init__(**kwargs)
        self.bind(
            is_today=self._refresh_theme,
            selected=self._refresh_theme,
            has_tasks=self._refresh_caption,
        )
        self._refresh_caption()

    def _refresh_caption(self, *_args):
        day_text = self.date_value[-2:].lstrip("0") if self.date_value else ""
        self.text = f"{day_text}\n•" if self.has_tasks else day_text
        self.line_height = 0.82 if self.has_tasks else 1.0

    def _refresh_theme(self, *_args):
        if not hasattr(self, "_button_bg"):
            return
        if self.selected:
            self.background_token = ACCENT
            self.border_token = ACCENT
        else:
            self.background_token = CARD_SECONDARY
            self.border_token = ACCENT if self.is_today else BORDER
        self.text_token = TEXT_PRIMARY
        super()._refresh_theme()


class AgendaTaskCard(RoundedThemePanel):
    """One task row in the selected-day agenda."""

    task = ObjectProperty(None, allownone=True)
    on_completed = ObjectProperty(None, allownone=True)

    def __init__(self, task, on_completed=None, **kwargs):
        kwargs.setdefault("orientation", "horizontal")
        kwargs.setdefault("size_hint_y", None)
        kwargs.setdefault("height", dp(76))
        kwargs.setdefault("padding", [dp(14), dp(7), dp(14), dp(7)])
        kwargs.setdefault("spacing", dp(12))
        kwargs.setdefault("background_token", CARD_PRIMARY)
        kwargs.setdefault("radius_value", 14)
        super().__init__(**kwargs)

        self.task = task
        self.on_completed = on_completed

        with self.canvas.after:
            self._accent_color = Color(*theme_rgba(ACCENT))
            self._accent_bar = RoundedRectangle(
                pos=(self.x, self.y + dp(8)),
                size=(dp(5), max(0, self.height - dp(16))),
                radius=[dp(3)],
            )
        self.bind(pos=self._update_accent, size=self._update_accent)

        completed = bool(task.get("completed"))
        self.complete_btn = SelectableThemeButton(
            text="✓" if completed else "",
            selected=completed,
            size_hint_x=None,
            width=dp(38),
            height=dp(38),
            radius_value=19,
            font_size=sp(18),
            pos_hint={"center_y": 0.5},
        )
        self.complete_btn.bind(on_release=self._toggle_complete)
        self.add_widget(self.complete_btn)

        details = BoxLayout(
            orientation="vertical",
            spacing=dp(3),
        )
        title = task.get("title", "Untitled task")
        self.title_label = ThemedLabel(
            text=f"[s]{title}[/s]" if completed else title,
            markup=True,
            color_token=TEXT_PRIMARY,
            font_size=sp(14),
            bold=True,
            halign="left",
            valign="middle",
            size_hint_y=None,
            height=dp(27),
        )
        self.title_label.bind(size=self.title_label.setter("text_size"))

        metadata_parts = []
        if task.get("due_time"):
            metadata_parts.append(task["due_time"])
        else:
            metadata_parts.append("Any time")
        metadata_parts.append(task.get("category") or "Study")
        metadata_parts.append(task.get("priority") or "Medium")
        if task.get("is_carried"):
            metadata_parts.append("Carried forward")
        if task.get("notify_enabled"):
            metadata_parts.append("Reminder on")

        self.meta_label = ThemedLabel(
            text="  •  ".join(metadata_parts),
            color_token=TEXT_SECONDARY,
            font_size=sp(11),
            halign="left",
            valign="middle",
            size_hint_y=None,
            height=dp(24),
        )
        self.meta_label.bind(size=self.meta_label.setter("text_size"))

        details.add_widget(self.title_label)
        details.add_widget(self.meta_label)
        self.add_widget(details)

        if task.get("link"):
            link_btn = ThemeButton(
                text="Open link",
                size_hint_x=None,
                width=dp(92),
                height=dp(36),
                font_size=sp(11),
                pos_hint={"center_y": 0.5},
                background_token=CARD_SECONDARY,
            )
            link_btn.bind(on_release=self._open_link)
            self.add_widget(link_btn)

        theme_manager.bind(theme_name=self._update_accent_theme)

    def _update_accent(self, *_args):
        self._accent_bar.pos = (self.x, self.y + dp(8))
        self._accent_bar.size = (dp(5), max(0, self.height - dp(16)))

    def _update_accent_theme(self, *_args):
        self._accent_color.rgba = theme_rgba(ACCENT)

    def _toggle_complete(self, *_args):
        completed = not bool(self.task.get("completed"))
        self.task["completed"] = completed
        self.complete_btn.selected = completed
        self.complete_btn.text = "✓" if completed else ""
        title = self.task.get("title", "Untitled task")
        self.title_label.text = f"[s]{title}[/s]" if completed else title
        if self.on_completed:
            self.on_completed(self.task.get("id"), completed)

    def _open_link(self, *_args):
        link = (self.task.get("link") or "").strip()
        if not link:
            return
        if not link.startswith(("http://", "https://")):
            link = "https://" + link
        webbrowser.open(link)


class CalendarScreen(ThemedScreenMixin, Screen):
    """Month + agenda calendar, visually synced with the NoteNest theme."""

    THEME_MAP = {}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        now = datetime.now()
        self.current_year = now.year
        self.current_month = now.month
        self.selected_date = now.strftime("%Y-%m-%d")
        self.active_category = "All"
        self.current_tasks = []
        self.category_buttons = {}
        self.date_buttons = {}

        with self.canvas.before:
            self._screen_bg = Color(*theme_rgba(BACKGROUND))
            self._screen_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(
            pos=self._update_background,
            size=self._update_background,
        )
        self.bind(size=self._update_calendar_scale)

        self.main_layout = BoxLayout(
            orientation="vertical",
            padding=[dp(20), dp(16), dp(20), dp(18)],
            spacing=dp(12),
        )
        self.add_widget(self.main_layout)
        self.bind(size=self._update_calendar_scale)

        self._build_header()
        self._build_category_filters()
        self._build_month_card()
        self._build_agenda()

        self.build_calendar()
        self.select_date(self.selected_date)

        self._notification_event = Clock.schedule_interval(
            self.check_notifications,
            30,
        )
        Clock.schedule_once(self.check_notifications, 1)
        Clock.schedule_once(lambda _dt: self.apply_theme(), 0)
        Clock.schedule_once(self._update_calendar_scale, 0)

    def on_theme_applied(self):
        self._screen_bg.rgba = theme_rgba(BACKGROUND)

    def _update_background(self, *_args):
        self._screen_rect.pos = self.pos
        self._screen_rect.size = self.size


    def _update_calendar_scale(self, *_args):
        """Keep six equal calendar rows and leave room for the day agenda."""
        if not hasattr(self, "month_card") or not hasattr(self, "calendar_grid"):
            return

        # The card stays visually identical, but scales to roughly one third
        # of the available screen height. Clamps keep it usable across common
        # Windows DPI settings and maximized/non-maximized window sizes.
        target_card_height = max(
            dp(270),
            min(dp(330), self.height * 0.34),
        )

        # Fixed vertical space inside the month card:
        # padding + navigation + weekday header + two layout gaps.
        fixed_height = dp(85)
        grid_spacing = dp(4)
        available_grid = max(dp(188), target_card_height - fixed_height)
        row_height = (available_grid - grid_spacing * 5) / 6
        row_height = max(dp(28), min(dp(40), row_height))

        grid_height = row_height * 6 + grid_spacing * 5
        self.calendar_grid.row_default_height = row_height
        self.calendar_grid.height = grid_height
        self.month_card.height = fixed_height + grid_height

    def _build_header(self):
        header = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(52),
            spacing=dp(10),
        )

        back_btn = ThemeButton(
            text="‹  Home",
            size_hint_x=None,
            width=dp(105),
            height=dp(44),
            background_token=CARD_SECONDARY,
            font_size=sp(13),
        )
        back_btn.bind(on_release=self.go_back)

        title_box = BoxLayout(orientation="vertical")
        title = ThemedLabel(
            text="Calendar",
            color_token=TEXT_PRIMARY,
            font_size=sp(21),
            bold=True,
            halign="left",
            valign="bottom",
        )
        title.bind(size=title.setter("text_size"))
        subtitle = ThemedLabel(
            text="Plan tasks and keep unfinished work visible",
            color_token=TEXT_SECONDARY,
            font_size=sp(11),
            halign="left",
            valign="top",
        )
        subtitle.bind(size=subtitle.setter("text_size"))
        title_box.add_widget(title)
        title_box.add_widget(subtitle)

        add_btn = ThemeButton(
            text="+  Add Task",
            size_hint_x=None,
            width=dp(132),
            height=dp(44),
            background_token=ACCENT,
            border_token=ACCENT,
            text_token=TEXT_PRIMARY,
            bold=True,
            font_size=sp(13),
        )
        add_btn.bind(on_release=self.open_add_task_popup)

        header.add_widget(back_btn)
        header.add_widget(title_box)
        header.add_widget(add_btn)
        self.main_layout.add_widget(header)

    def _build_category_filters(self):
        self.category_scroll = ScrollView(
            size_hint_y=None,
            height=dp(42),
            do_scroll_y=False,
            bar_width=0,
        )
        self.category_row = BoxLayout(
            orientation="horizontal",
            size_hint_x=None,
            height=dp(34),
            spacing=dp(8),
        )
        self.category_row.bind(
            minimum_width=self.category_row.setter("width")
        )
        self.category_scroll.add_widget(self.category_row)
        self.main_layout.add_widget(self.category_scroll)
        self.refresh_category_filters()

    def _build_month_card(self):
        self.month_card = RoundedThemePanel(
            orientation="vertical",
            size_hint_y=None,
            height=dp(255),
            padding=[dp(14), dp(9), dp(14), dp(10)],
            spacing=dp(5),
            background_token=CARD_PRIMARY,
            radius_value=18,
        )

        nav = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(36),
            spacing=dp(8),
        )
        prev_btn = ThemeButton(
            text="<",
            size_hint_x=None,
            width=dp(42),
            height=dp(34),
            background_token=CARD_SECONDARY,
            font_size=sp(16),
        )
        prev_btn.bind(on_release=self.prev_month)

        self.month_label = ThemedLabel(
            text="",
            color_token=TEXT_PRIMARY,
            font_size=sp(17),
            bold=True,
            halign="left",
            valign="middle",
        )
        self.month_label.bind(size=self.month_label.setter("text_size"))

        today_btn = ThemeButton(
            text="Today",
            size_hint_x=None,
            width=dp(74),
            height=dp(34),
            background_token=CARD_SECONDARY,
            text_token=TEXT_PRIMARY,
            font_size=sp(12),
        )
        today_btn.bind(on_release=self.go_to_today)

        next_btn = ThemeButton(
            text=">",
            size_hint_x=None,
            width=dp(42),
            height=dp(34),
            background_token=CARD_SECONDARY,
            font_size=sp(17),
        )
        next_btn.bind(on_release=self.next_month)

        nav.add_widget(prev_btn)
        nav.add_widget(self.month_label)
        nav.add_widget(today_btn)
        nav.add_widget(next_btn)
        self.month_card.add_widget(nav)

        days_header = GridLayout(
            cols=7,
            size_hint_y=None,
            height=dp(20),
            spacing=dp(4),
        )
        for name in ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"):
            days_header.add_widget(
                ThemedLabel(
                    text=name,
                    color_token=TEXT_SECONDARY,
                    font_size=sp(10),
                    bold=True,
                    halign="center",
                    valign="middle",
                )
            )
        self.month_card.add_widget(days_header)

        self.calendar_grid = GridLayout(
            cols=7,
            rows=6,
            size_hint_y=None,
            height=dp(224),
            spacing=dp(4),
            row_force_default=True,
            row_default_height=dp(34),
        )
        self.month_card.add_widget(self.calendar_grid)
        self.main_layout.add_widget(self.month_card)

    def _build_agenda(self):
        agenda_header = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(38),
            spacing=dp(8),
        )
        self.task_label = ThemedLabel(
            text="",
            color_token=TEXT_PRIMARY,
            font_size=sp(15),
            bold=True,
            halign="left",
            valign="middle",
        )
        self.task_label.bind(size=self.task_label.setter("text_size"))

        self.task_count_label = ThemedLabel(
            text="",
            color_token=TEXT_SECONDARY,
            font_size=sp(11),
            halign="right",
            valign="middle",
            size_hint_x=None,
            width=dp(110),
        )
        self.task_count_label.bind(
            size=self.task_count_label.setter("text_size")
        )

        agenda_header.add_widget(self.task_label)
        agenda_header.add_widget(self.task_count_label)
        self.main_layout.add_widget(agenda_header)

        self.task_list = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            spacing=dp(9),
            padding=[0, 0, dp(3), dp(6)],
        )
        self.task_list.bind(
            minimum_height=self.task_list.setter("height")
        )
        self.task_scroll = ScrollView(
            do_scroll_x=False,
            do_scroll_y=True,
            bar_width=dp(5),
            scroll_wheel_distance=dp(44),
        )
        self.task_scroll.add_widget(self.task_list)
        self.main_layout.add_widget(self.task_scroll)

    def _user_id(self):
        try:
            from kivy.app import App

            app = App.get_running_app()
            return getattr(app, "user_id", 1)
        except Exception:
            return 1

    def _category_names(self):
        names = list(BUILT_IN_CATEGORIES)
        try:
            for row in get_all_categories(self._user_id()):
                # categories schema: id, name, color, user_id
                name = row[1] if len(row) > 1 else ""
                if name and name.casefold() not in {
                    item.casefold() for item in names
                }:
                    names.append(name)
        except Exception as exc:
            print(f"[Calendar] Could not load custom categories: {exc}")
        return names

    def refresh_category_filters(self):
        if not hasattr(self, "category_row"):
            return

        self.category_row.clear_widgets()
        self.category_buttons = {}
        categories = ["All", *self._category_names()]

        if self.active_category not in categories:
            self.active_category = "All"

        for category in categories:
            button = SelectableThemeButton(
                text=category,
                selected=category == self.active_category,
                size_hint_x=None,
                width=max(dp(72), dp(18 + len(category) * 7)),
                height=dp(36),
                radius_value=18,
                font_size=sp(11),
                bold=True,
            )
            button.bind(
                on_release=lambda _button, value=category:
                self.select_category(value)
            )
            self.category_buttons[category] = button
            self.category_row.add_widget(button)

    def select_category(self, category):
        self.active_category = category
        for name, button in self.category_buttons.items():
            button.selected = name == category
        self.show_tasks(self.current_tasks)

    def build_calendar(self):
        self.calendar_grid.clear_widgets()
        self.date_buttons = {}

        first_day = datetime(self.current_year, self.current_month, 1)
        self.month_label.text = first_day.strftime("%B %Y")

        task_dates = set(
            get_all_task_dates(self.current_year, self.current_month)
        )
        weeks = calendar.monthcalendar(
            self.current_year,
            self.current_month,
        )
        while len(weeks) < 6:
            weeks.append([0] * 7)

        today_value = datetime.now().strftime("%Y-%m-%d")

        for week in weeks[:6]:
            for day in week:
                if day == 0:
                    self.calendar_grid.add_widget(Widget(size_hint_y=None, height=dp(30)))
                    continue

                date_value = (
                    f"{self.current_year:04d}-"
                    f"{self.current_month:02d}-"
                    f"{day:02d}"
                )
                date_button = CalendarDayButton(
                    date_value=date_value,
                    has_tasks=date_value in task_dates,
                    is_today=date_value == today_value,
                    selected=date_value == self.selected_date,
                )
                date_button.bind(
                    on_release=lambda _button, selected=date_value:
                    self.select_date(selected)
                )
                self.date_buttons[date_value] = date_button
                self.calendar_grid.add_widget(date_button)

    def select_date(self, date_value):
        """Select a day and show every task scheduled for that date."""
        self.selected_date = date_value

        # A date tap should never leave tasks hidden by a previous category
        # filter. Users can choose a category again after selecting the day.
        self.active_category = "All"
        for name, category_button in self.category_buttons.items():
            category_button.selected = name == "All"

        for value, button in self.date_buttons.items():
            button.selected = value == date_value

        self.current_tasks = get_tasks_by_date(date_value)
        selected = datetime.strptime(date_value, "%Y-%m-%d")
        self.task_label.text = selected.strftime("%A, %d %B")
        self.show_tasks(self.current_tasks)

        # Always start at the first task when a new date is tapped.
        if hasattr(self, "task_scroll"):
            Clock.schedule_once(
                lambda _dt: setattr(self.task_scroll, "scroll_y", 1),
                0,
            )

    def show_tasks(self, tasks):
        self.task_list.clear_widgets()

        if self.active_category == "All":
            filtered = list(tasks)
        else:
            filtered = [
                task
                for task in tasks
                if (task.get("category") or "Study") == self.active_category
            ]

        open_count = sum(
            1 for task in filtered if not task.get("completed", False)
        )
        total = len(filtered)
        if total:
            self.task_count_label.text = (
                f"{open_count} open · {total} total"
            )
        else:
            self.task_count_label.text = "No tasks"

        if not filtered:
            empty_card = RoundedThemePanel(
                orientation="vertical",
                size_hint_y=None,
                height=dp(90),
                padding=dp(14),
                background_token=CARD_PRIMARY,
                radius_value=14,
            )
            empty_card.add_widget(
                ThemedLabel(
                    text="No tasks for this date and category.",
                    color_token=TEXT_SECONDARY,
                    font_size=sp(12),
                    halign="center",
                    valign="middle",
                )
            )
            self.task_list.add_widget(empty_card)
            return

        for task in filtered:
            self.task_list.add_widget(
                AgendaTaskCard(
                    task=task,
                    on_completed=self.on_task_checked,
                )
            )

    def on_task_checked(self, task_id, completed):
        if not task_id:
            return
        set_task_completed(task_id, completed)
        date_value = self.selected_date
        self.build_calendar()
        Clock.schedule_once(
            lambda _dt: self.select_date(date_value),
            0,
        )

    def go_back(self, *_args):
        if self.manager:
            self.manager.current = "home"

    def go_to_today(self, *_args):
        today = datetime.now()
        self.current_year = today.year
        self.current_month = today.month
        self.selected_date = today.strftime("%Y-%m-%d")
        self.build_calendar()
        self.select_date(self.selected_date)

    def prev_month(self, *_args):
        if self.current_month == 1:
            self.current_month = 12
            self.current_year -= 1
        else:
            self.current_month -= 1

        self.selected_date = (
            f"{self.current_year:04d}-{self.current_month:02d}-01"
        )
        self.build_calendar()
        self.select_date(self.selected_date)

    def next_month(self, *_args):
        if self.current_month == 12:
            self.current_month = 1
            self.current_year += 1
        else:
            self.current_month += 1

        self.selected_date = (
            f"{self.current_year:04d}-{self.current_month:02d}-01"
        )
        self.build_calendar()
        self.select_date(self.selected_date)

    def on_pre_enter(self, *_args):
        self.refresh_category_filters()
        self.build_calendar()
        self.select_date(self.selected_date)

    def _section_title(self, text):
        return ThemedLabel(
            text=text.upper(),
            color_token=ACCENT,
            font_size=sp(10),
            bold=True,
            size_hint_y=None,
            height=dp(22),
            halign="left",
            valign="middle",
        )

    def _field_group(self, label_text, widget):
        group = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=dp(76),
            spacing=dp(4),
        )
        label = ThemedLabel(
            text=label_text,
            color_token=TEXT_SECONDARY,
            font_size=sp(10),
            size_hint_y=None,
            height=dp(20),
            halign="left",
            valign="middle",
        )
        label.bind(size=label.setter("text_size"))
        group.add_widget(label)
        group.add_widget(widget)
        return group

    def _option_row(self, title, description, toggle):
        row = RoundedThemePanel(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(62),
            padding=[dp(12), dp(7), dp(10), dp(7)],
            spacing=dp(10),
            background_token=CARD_SECONDARY,
            radius_value=12,
        )
        labels = BoxLayout(orientation="vertical", spacing=0)
        title_label = ThemedLabel(
            text=title,
            color_token=TEXT_PRIMARY,
            font_size=sp(11),
            bold=True,
            halign="left",
            valign="bottom",
        )
        title_label.bind(size=title_label.setter("text_size"))
        description_label = ThemedLabel(
            text=description,
            color_token=TEXT_SECONDARY,
            font_size=sp(9),
            halign="left",
            valign="top",
        )
        description_label.bind(size=description_label.setter("text_size"))
        labels.add_widget(title_label)
        labels.add_widget(description_label)
        row.add_widget(labels)
        row.add_widget(toggle)
        return row

    def open_add_task_popup(self, *_args):
        """Open the redesigned themed task editor."""
        panel = RoundedThemePanel(
            orientation="vertical",
            padding=[dp(20), dp(16), dp(20), dp(16)],
            spacing=dp(10),
            background_token=CARD_PRIMARY,
            border_token=BORDER,
            radius_value=20,
        )

        header = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(50),
            spacing=dp(10),
        )
        heading_box = BoxLayout(orientation="vertical")
        heading = ThemedLabel(
            text="Add New Task",
            color_token=TEXT_PRIMARY,
            font_size=sp(19),
            bold=True,
            halign="left",
            valign="bottom",
        )
        heading.bind(size=heading.setter("text_size"))
        subheading = ThemedLabel(
            text="Create a task for the selected calendar date",
            color_token=TEXT_SECONDARY,
            font_size=sp(9),
            halign="left",
            valign="top",
        )
        subheading.bind(size=subheading.setter("text_size"))
        heading_box.add_widget(heading)
        heading_box.add_widget(subheading)

        close_btn = ThemeButton(
            text="×",
            size_hint=(None, None),
            size=(dp(38), dp(38)),
            radius_value=19,
            font_size=sp(20),
            background_token=CARD_SECONDARY,
        )
        header.add_widget(heading_box)
        header.add_widget(close_btn)
        panel.add_widget(header)

        divider = Widget(size_hint_y=None, height=dp(2))
        with divider.canvas:
            divider_color = Color(*theme_rgba(ACCENT))
            divider_rect = Rectangle(pos=divider.pos, size=divider.size)
        divider.bind(
            pos=lambda widget, _value: setattr(divider_rect, "pos", widget.pos),
            size=lambda widget, _value: setattr(divider_rect, "size", widget.size),
        )
        theme_manager.bind(
            theme_name=lambda *_values: setattr(
                divider_color,
                "rgba",
                theme_rgba(ACCENT),
            )
        )
        panel.add_widget(divider)

        form_scroll = ScrollView(
            do_scroll_x=False,
            bar_width=dp(4),
        )
        form = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            spacing=dp(8),
            padding=[0, dp(4), dp(4), dp(6)],
        )
        form.bind(minimum_height=form.setter("height"))
        form_scroll.add_widget(form)

        default_date = (
            self.selected_date
            or datetime.now().strftime("%Y-%m-%d")
        )

        form.add_widget(self._section_title("Task details"))
        title_input = ThemedTextInput(
            hint_text="e.g. Finish database assignment",
        )
        form.add_widget(self._field_group("Title", title_input))

        form.add_widget(self._section_title("Schedule"))
        schedule_row = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(76),
            spacing=dp(12),
        )
        date_input = ThemedTextInput(
            text=default_date,
            hint_text="YYYY-MM-DD",
        )
        time_input = ThemedTextInput(
            hint_text="HH:MM (24-hour)",
        )
        schedule_row.add_widget(self._field_group("Date", date_input))
        schedule_row.add_widget(self._field_group("Time", time_input))
        form.add_widget(schedule_row)

        choices_row = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(82),
            spacing=dp(12),
        )

        priority_box = BoxLayout(
            orientation="vertical",
            spacing=dp(4),
        )
        priority_label = ThemedLabel(
            text="Priority",
            color_token=TEXT_SECONDARY,
            font_size=sp(10),
            size_hint_y=None,
            height=dp(20),
            halign="left",
            valign="middle",
        )
        priority_buttons_row = BoxLayout(
            orientation="horizontal",
            spacing=dp(6),
        )
        priority_buttons = {}
        selected_priority = {"value": "Medium"}

        def choose_priority(value):
            selected_priority["value"] = value
            for name, button in priority_buttons.items():
                button.selected = name == value

        for value in ("Low", "Medium", "High"):
            button = SelectableThemeButton(
                text=value,
                selected=value == "Medium",
                height=dp(42),
                radius_value=18,
                font_size=sp(10),
            )
            button.bind(
                on_release=lambda _button, choice=value:
                choose_priority(choice)
            )
            priority_buttons[value] = button
            priority_buttons_row.add_widget(button)

        priority_box.add_widget(priority_label)
        priority_box.add_widget(priority_buttons_row)

        category_input = ThemeButton(
            text="Study   ▾",
            height=dp(48),
            background_token=CARD_SECONDARY,
            border_token=BORDER,
            text_token=TEXT_PRIMARY,
            font_size=sp(11),
        )
        category_input.category_value = "Study"
        category_input.bind(
            on_release=lambda button: self.open_category_picker(button)
        )
        category_group = self._field_group("Category", category_input)

        choices_row.add_widget(priority_box)
        choices_row.add_widget(category_group)
        form.add_widget(choices_row)

        form.add_widget(self._section_title("Embedded link"))
        link_input = ThemedTextInput(
            hint_text="https://example.com/resource",
        )
        form.add_widget(self._field_group("Link (optional)", link_input))

        form.add_widget(self._section_title("Options"))
        carry_toggle = OptionToggle(active=True)
        notify_toggle = OptionToggle(active=False)
        form.add_widget(
            self._option_row(
                "Carry unfinished task forward",
                "Show it each day until it is completed",
                carry_toggle,
            )
        )
        form.add_widget(
            self._option_row(
                "Notify at task time",
                "Show a reminder while NoteNest is running",
                notify_toggle,
            )
        )

        panel.add_widget(form_scroll)

        error_label = ThemedLabel(
            text="",
            color_token=TEXT_PRIMARY,
            font_size=sp(10),
            size_hint_y=None,
            height=dp(22),
            halign="left",
            valign="middle",
        )
        error_label.bind(size=error_label.setter("text_size"))
        panel.add_widget(error_label)

        actions = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(46),
            spacing=dp(10),
        )
        actions.add_widget(Widget())
        cancel_btn = ThemeButton(
            text="Cancel",
            size_hint_x=None,
            width=dp(120),
            height=dp(44),
            background_token=CARD_SECONDARY,
        )
        save_btn = ThemeButton(
            text="Save Task",
            size_hint_x=None,
            width=dp(150),
            height=dp(44),
            background_token=ACCENT,
            border_token=ACCENT,
            text_token=TEXT_PRIMARY,
            bold=True,
        )
        actions.add_widget(cancel_btn)
        actions.add_widget(save_btn)
        panel.add_widget(actions)

        popup = Popup(
            title="",
            content=panel,
            size_hint=(0.82, 0.90),
            auto_dismiss=False,
            separator_height=0,
            background="",
            background_color=(0, 0, 0, 0),
        )

        close_btn.bind(on_release=popup.dismiss)
        cancel_btn.bind(on_release=popup.dismiss)
        save_btn.bind(
            on_release=lambda _button: self.save_task_from_popup(
                popup=popup,
                error_label=error_label,
                title=title_input.text,
                due_date=date_input.text,
                due_time=time_input.text,
                priority=selected_priority["value"],
                category=getattr(category_input, "category_value", "Study"),
                link=link_input.text,
                carry_forward=carry_toggle.active,
                notify_enabled=notify_toggle.active,
            )
        )
        popup.open()

    def open_category_picker(self, category_control):
        """Open a themed category picker instead of Kivy's gray Spinner menu."""
        panel = RoundedThemePanel(
            orientation="vertical",
            padding=[dp(16), dp(14), dp(16), dp(14)],
            spacing=dp(10),
            background_token=CARD_PRIMARY,
            border_token=BORDER,
            radius_value=18,
        )

        title_row = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(42),
            spacing=dp(8),
        )
        title_box = BoxLayout(orientation="vertical")
        title = ThemedLabel(
            text="Choose Category",
            color_token=TEXT_PRIMARY,
            font_size=sp(16),
            bold=True,
            halign="left",
            valign="bottom",
        )
        title.bind(size=title.setter("text_size"))
        subtitle = ThemedLabel(
            text="Select an existing category or create a new one",
            color_token=TEXT_SECONDARY,
            font_size=sp(9),
            halign="left",
            valign="top",
        )
        subtitle.bind(size=subtitle.setter("text_size"))
        title_box.add_widget(title)
        title_box.add_widget(subtitle)

        close_button = ThemeButton(
            text="×",
            size_hint=(None, None),
            size=(dp(36), dp(36)),
            radius_value=18,
            font_size=sp(18),
            background_token=CARD_SECONDARY,
        )
        title_row.add_widget(title_box)
        title_row.add_widget(close_button)
        panel.add_widget(title_row)

        divider = Widget(size_hint_y=None, height=dp(1))
        with divider.canvas:
            divider_color = Color(*theme_rgba(BORDER))
            divider_rect = Rectangle(pos=divider.pos, size=divider.size)
        divider.bind(
            pos=lambda widget, _value: setattr(divider_rect, "pos", widget.pos),
            size=lambda widget, _value: setattr(divider_rect, "size", widget.size),
        )
        theme_manager.bind(
            theme_name=lambda *_values: setattr(
                divider_color,
                "rgba",
                theme_rgba(BORDER),
            )
        )
        panel.add_widget(divider)

        category_list = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            spacing=dp(7),
            padding=[0, dp(2), dp(3), dp(2)],
        )
        category_list.bind(
            minimum_height=category_list.setter("height")
        )
        category_scroll = ScrollView(
            do_scroll_x=False,
            do_scroll_y=True,
            bar_width=dp(4),
        )
        category_scroll.add_widget(category_list)
        panel.add_widget(category_scroll)

        current_category = getattr(
            category_control,
            "category_value",
            "Study",
        )

        popup = Popup(
            title="",
            content=panel,
            size_hint=(0.44, 0.66),
            auto_dismiss=True,
            separator_height=0,
            background="",
            background_color=(0, 0, 0, 0),
        )

        def choose_category(value):
            category_control.category_value = value
            category_control.text = f"{value}   ▾"
            popup.dismiss()

        for category in self._category_names():
            option = SelectableThemeButton(
                text=category,
                selected=category == current_category,
                size_hint_y=None,
                height=dp(44),
                radius_value=12,
                font_size=sp(12),
            )
            option.bind(
                on_release=lambda _button, value=category:
                choose_category(value)
            )
            category_list.add_widget(option)

        create_button = ThemeButton(
            text="+  Create New Category",
            size_hint_y=None,
            height=dp(46),
            background_token=ACCENT,
            border_token=ACCENT,
            text_token=TEXT_PRIMARY,
            bold=True,
            font_size=sp(12),
        )
        create_button.bind(
            on_release=lambda *_args: (
                popup.dismiss(),
                Clock.schedule_once(
                    lambda _dt: self.open_new_category_popup(
                        category_control
                    ),
                    0,
                ),
            )
        )
        category_list.add_widget(create_button)

        close_button.bind(on_release=popup.dismiss)
        popup.open()

    def open_new_category_popup(self, category_control):
        """Create and select a reusable user-defined category."""
        panel = RoundedThemePanel(
            orientation="vertical",
            padding=[dp(18), dp(16), dp(18), dp(16)],
            spacing=dp(10),
            background_token=CARD_PRIMARY,
            border_token=BORDER,
            radius_value=18,
        )

        header = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(42),
            spacing=dp(8),
        )
        heading = ThemedLabel(
            text="Create New Category",
            color_token=TEXT_PRIMARY,
            font_size=sp(16),
            bold=True,
            halign="left",
            valign="middle",
        )
        heading.bind(size=heading.setter("text_size"))
        close = ThemeButton(
            text="×",
            size_hint=(None, None),
            size=(dp(36), dp(36)),
            radius_value=18,
            font_size=sp(18),
            background_token=CARD_SECONDARY,
        )
        header.add_widget(heading)
        header.add_widget(close)
        panel.add_widget(header)

        name_input = ThemedTextInput(
            hint_text="e.g. CSE299 Project",
        )
        panel.add_widget(self._field_group("Category name", name_input))

        helper = ThemedLabel(
            text="This category will be saved and available for future tasks.",
            color_token=TEXT_SECONDARY,
            font_size=sp(10),
            size_hint_y=None,
            height=dp(34),
            halign="left",
            valign="middle",
        )
        helper.bind(size=helper.setter("text_size"))
        panel.add_widget(helper)

        error = ThemedLabel(
            text="",
            color_token=TEXT_PRIMARY,
            font_size=sp(10),
            size_hint_y=None,
            height=dp(24),
            halign="left",
            valign="middle",
        )
        error.bind(size=error.setter("text_size"))
        panel.add_widget(error)

        actions = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(44),
            spacing=dp(8),
        )
        cancel = ThemeButton(
            text="Cancel",
            background_token=CARD_SECONDARY,
        )
        create = ThemeButton(
            text="Create",
            background_token=ACCENT,
            border_token=ACCENT,
            text_token=TEXT_PRIMARY,
            bold=True,
        )
        actions.add_widget(cancel)
        actions.add_widget(create)
        panel.add_widget(actions)

        popup = Popup(
            title="",
            content=panel,
            size_hint=(0.48, 0.46),
            auto_dismiss=False,
            separator_height=0,
            background="",
            background_color=(0, 0, 0, 0),
        )

        def save_category(*_args):
            name = name_input.text.strip()
            if not name:
                error.text = "Enter a category name."
                name_input.focus = True
                return

            existing = self._category_names()
            if name.casefold() in {item.casefold() for item in existing}:
                error.text = "That category already exists."
                name_input.focus = True
                return

            try:
                create_category(
                    name=name,
                    color=theme_manager.get_color(ACCENT),
                    user_id=self._user_id(),
                )
            except Exception as exc:
                error.text = f"Could not create category: {exc}"
                return

            category_control.category_value = name
            category_control.text = f"{name}   ▾"
            self.refresh_category_filters()
            popup.dismiss()

        close.bind(on_release=popup.dismiss)
        cancel.bind(on_release=popup.dismiss)
        create.bind(on_release=save_category)
        popup.bind(
            on_open=lambda *_args: Clock.schedule_once(
                lambda _dt: setattr(name_input, "focus", True),
                0.1,
            )
        )
        popup.open()

    def save_task_from_popup(
        self,
        popup,
        error_label,
        title,
        due_date,
        due_time,
        priority,
        category,
        link,
        carry_forward,
        notify_enabled,
    ):
        title = title.strip()
        due_date = due_date.strip()
        due_time = due_time.strip()
        link = link.strip()

        if not title:
            error_label.text = "Please enter a task title."
            return

        try:
            datetime.strptime(due_date, "%Y-%m-%d")
        except ValueError:
            error_label.text = "Date must use YYYY-MM-DD."
            return

        if due_time:
            try:
                datetime.strptime(due_time, "%H:%M")
            except ValueError:
                error_label.text = "Time must use 24-hour HH:MM."
                return

        if notify_enabled and not due_time:
            error_label.text = "Add a time before enabling notification."
            return

        if category == CREATE_CATEGORY_VALUE:
            error_label.text = "Select or create a category."
            return

        create_tasks(
            title=title,
            user_id=self._user_id(),
            priority=priority,
            due_date=due_date,
            due_time=due_time or None,
            category=category or "Study",
            link=link,
            carry_forward=carry_forward,
            notify_enabled=notify_enabled,
        )

        popup.dismiss()
        self.current_year = int(due_date[:4])
        self.current_month = int(due_date[5:7])
        self.selected_date = due_date
        self.refresh_category_filters()
        self.build_calendar()
        self.select_date(due_date)

    def check_notifications(self, _dt):
        for item in collect_due_notifications():
            message = f"{item['title']} is due"
            if item.get("due_time"):
                message += f" at {item['due_time']}"

            delivered = send_system_notification(
                "NoteNest task reminder",
                message,
            )
            if not delivered:
                self.show_notification_popup(message)

    def show_notification_popup(self, message):
        panel = RoundedThemePanel(
            orientation="vertical",
            padding=dp(18),
            spacing=dp(12),
            background_token=CARD_PRIMARY,
            radius_value=18,
        )
        panel.add_widget(
            ThemedLabel(
                text="Task Reminder",
                color_token=TEXT_PRIMARY,
                font_size=sp(17),
                bold=True,
                size_hint_y=None,
                height=dp(36),
            )
        )
        message_label = ThemedLabel(
            text=message,
            color_token=TEXT_PRIMARY,
            font_size=sp(12),
            halign="left",
            valign="middle",
        )
        message_label.bind(size=message_label.setter("text_size"))
        panel.add_widget(message_label)
        close_btn = ThemeButton(
            text="Got it",
            size_hint_y=None,
            height=dp(44),
            background_token=ACCENT,
            border_token=ACCENT,
            bold=True,
        )
        panel.add_widget(close_btn)
        popup = Popup(
            title="",
            content=panel,
            size_hint=(0.58, 0.38),
            separator_height=0,
            background="",
            background_color=(0, 0, 0, 0),
        )
        close_btn.bind(on_release=popup.dismiss)
        popup.open()
