import calendar
from datetime import datetime
from kivy.uix.screenmanager import Screen
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, RoundedRectangle, Rectangle


class CalendarScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_year = datetime.now().year
        self.current_month = datetime.now().month
        self.selected_date = None

        # Main layout with cream background
        self.main_layout = BoxLayout(
            orientation="vertical",
            padding=16,
            spacing=10
        )
        with self.main_layout.canvas.before:
            Color(0.96, 0.93, 0.86, 1)
            self.bg_rect = Rectangle(pos=self.main_layout.pos, size=self.main_layout.size)
        self.main_layout.bind(pos=lambda w, v: setattr(self.bg_rect, 'pos', v))
        self.main_layout.bind(size=lambda w, v: setattr(self.bg_rect, 'size', v))

        # Back button row
        back_row = BoxLayout(size_hint_y=None, height=40)
        back_btn = Button(
            text="← Home",
            size_hint_x=None, width=100,
            background_normal="",
            background_color=(0.24, 0.19, 0.15, 1),
            color=(0.96, 0.93, 0.86, 1),
            font_size=13
        )
        back_btn.bind(on_press=self.go_back)
        back_row.add_widget(back_btn)
        back_row.add_widget(Label())  # spacer

        # Header row with < Month Year >
        header = BoxLayout(size_hint_y=None, height=50, spacing=10)
        self.prev_btn = Button(
            text="<", size_hint_x=None, width=40,
            background_normal="",
            background_color=(0.24, 0.19, 0.15, 1),
            color=(0.96, 0.93, 0.86, 1),
            font_size=18
        )
        self.prev_btn.bind(on_press=self.prev_month)

        self.month_label = Label(
            text="",
            font_size=18,
            bold=True,
            color=(0.02, 0.01, 0.01, 1)
        )

        self.next_btn = Button(
            text=">", size_hint_x=None, width=40,
            background_normal="",
            background_color=(0.24, 0.19, 0.15, 1),
            color=(0.96, 0.93, 0.86, 1),
            font_size=18
        )
        self.next_btn.bind(on_press=self.next_month)

        header.add_widget(self.prev_btn)
        header.add_widget(self.month_label)
        header.add_widget(self.next_btn)

        # Day name labels
        days_header = GridLayout(cols=7, size_hint_y=None, height=30)
        for day in ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]:
            days_header.add_widget(Label(
                text=day,
                font_size=12,
                color=(0.43, 0.41, 0.38, 1),
                bold=True
            ))

        # Calendar grid
        self.calendar_grid = GridLayout(
            cols=7,
            size_hint_y=None,
            spacing=4
        )
        self.calendar_grid.bind(
            minimum_height=self.calendar_grid.setter("height")
        )

        # Task section label
        self.task_label = Label(
            text="Tap a date to see tasks",
            font_size=14,
            color=(0.43, 0.41, 0.38, 1),
            size_hint_y=None,
            height=30,
            halign="left",
            valign="middle"
        )
        self.task_label.bind(size=self.task_label.setter("text_size"))

        # Task list
        self.task_list = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            spacing=6
        )
        self.task_list.bind(
            minimum_height=self.task_list.setter("height")
        )

        scroll = ScrollView()
        scroll.add_widget(self.task_list)

        # Add everything to main layout
        self.main_layout.add_widget(back_row)
        self.main_layout.add_widget(header)
        self.main_layout.add_widget(days_header)
        self.main_layout.add_widget(self.calendar_grid)
        self.main_layout.add_widget(self.task_label)
        self.main_layout.add_widget(scroll)

        self.add_widget(self.main_layout)
        self.build_calendar()

    def go_back(self, instance):
        self.manager.current = "home"

    def build_calendar(self):
        self.calendar_grid.clear_widgets()
        month_name = datetime(
            self.current_year, self.current_month, 1
        ).strftime("%B %Y")
        self.month_label.text = month_name

        try:
            from database.task_queries import get_all_task_dates
        except ImportError:
            from mock_queries import get_all_task_dates

        task_dates = get_all_task_dates()
        cal = calendar.monthcalendar(self.current_year, self.current_month)
        today = datetime.now()

        for week in cal:
            for day in week:
                if day == 0:
                    self.calendar_grid.add_widget(Label(text=""))
                else:
                    date_str = f"{self.current_year}-{self.current_month:02d}-{day:02d}"
                    has_tasks = date_str in task_dates
                    is_today = (
                        day == today.day and
                        self.current_month == today.month and
                        self.current_year == today.year
                    )

                    btn = Button(
                        text=str(day),
                        background_normal="",
                        background_color=(
                            (0.24, 0.19, 0.15, 1) if is_today else
                            (0.82, 0.78, 0.72, 1) if has_tasks else
                            (0.91, 0.88, 0.86, 1)
                        ),
                        color=(
                            (0.96, 0.93, 0.86, 1) if is_today else
                            (0.02, 0.01, 0.01, 1)
                        ),
                        font_size=13,
                        size_hint_y=None,
                        height=36
                    )
                    btn.bind(on_press=lambda x, d=date_str: self.select_date(d))
                    self.calendar_grid.add_widget(btn)

    def select_date(self, date_str):
        self.selected_date = date_str
        self.task_list.clear_widgets()

        try:
            from database.task_queries import get_tasks_by_date
        except ImportError:
            from mock_queries import get_tasks_by_date

        tasks = get_tasks_by_date(date_str)
        display = datetime.strptime(date_str, "%Y-%m-%d").strftime("%B %d, %Y")
        self.task_label.text = f"Tasks for {display}:"

        if not tasks:
            self.task_list.add_widget(Label(
                text="No tasks for this day",
                font_size=13,
                color=(0.43, 0.41, 0.38, 1),
                size_hint_y=None,
                height=36
            ))
            return

        PRIORITY_COLORS = {
            "High":   (0.98, 0.85, 0.85, 1),
            "Medium": (0.98, 0.93, 0.85, 1),
            "Low":    (0.91, 0.95, 0.87, 1),
        }

        for task in tasks:
            row = BoxLayout(
                size_hint_y=None,
                height=44,
                padding=[12, 6, 12, 6],
                spacing=10
            )
            with row.canvas.before:
                Color(*PRIORITY_COLORS.get(task["priority"], (0.95, 0.93, 0.90, 1)))
                rect = RoundedRectangle(pos=row.pos, size=row.size, radius=[10])
            row.bind(pos=lambda w, v, r=rect: setattr(r, 'pos', v))
            row.bind(size=lambda w, v, r=rect: setattr(r, 'size', v))

            row.add_widget(Label(
                text=task["title"],
                font_size=13,
                color=(0.02, 0.01, 0.01, 1),
                halign="left",
                valign="middle",
                text_size=(None, None)
            ))
            row.add_widget(Label(
                text=task["priority"],
                font_size=11,
                bold=True,
                color=(0.43, 0.41, 0.38, 1),
                size_hint_x=None,
                width=60
            ))
            self.task_list.add_widget(row)

    def prev_month(self, instance):
        if self.current_month == 1:
            self.current_month = 12
            self.current_year -= 1
        else:
            self.current_month -= 1
        self.build_calendar()

    def next_month(self, instance):
        if self.current_month == 12:
            self.current_month = 1
            self.current_year += 1
        else:
            self.current_month += 1
        self.build_calendar()