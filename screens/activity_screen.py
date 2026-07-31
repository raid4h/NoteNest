# screens/activity_detail_screen.py
# The Smart Planner's hub screen. Opened from Home or Calendar with a
# task_id, it pulls everything related to that task -- linked notes,
# pomodoro progress, reminders -- via planner_queries.get_task_detail(),
# so this screen never has to know the schema details itself.

from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.screen import MDScreen
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDIconButton

from theme.theme_manager import theme_manager
from theme.themed_screen import ThemedScreenMixin
from theme.palettes import (
    BACKGROUND, CARD_PRIMARY, CARD_SECONDARY,
    TEXT_PRIMARY, TEXT_SECONDARY, ACCENT,
)

from database.planner_queries import get_task_detail

try:
    from database.notes_queries import create_notes
    from screens.editor.paths import DEFAULT_NOTEBOOK_ID
except ImportError:
    # Lets this screen still load/be tested even before those pieces
    # exist elsewhere in the app -- Add Note button just no-ops.
    create_notes = None
    DEFAULT_NOTEBOOK_ID = 1

# No per-task pomodoro goal field exists in the schema yet -- fixed
# default so the progress label has something to compare against.
# Bump this once/if tasks gets a real pomodoro_goal column.
DEFAULT_POMODORO_GOAL = 4


class ActivityDetailScreen(ThemedScreenMixin, MDScreen):

    # Set this before switching to this screen, e.g.:
    #   detail = self.manager.get_screen("activity_detail")
    #   detail.current_task_id = task_id
    #   self.manager.current = "activity_detail"
    current_task_id = None

    THEME_MAP = {
        "self":                    ("md_bg_color", BACKGROUND),
        "back_button":             ("icon_color", TEXT_PRIMARY),
        "header_label":            ("text_color", TEXT_PRIMARY),
        "subtitle_label":          ("text_color", TEXT_SECONDARY),
        "note_card":               ("md_bg_color", CARD_PRIMARY),
        "note_section_label":      ("text_color", ACCENT),
        "add_note_button":         ("icon_color", TEXT_PRIMARY),
        "pomodoro_card":           ("md_bg_color", CARD_SECONDARY),
        "pomodoro_section_label":  ("text_color", ACCENT),
        "pomodoro_progress_label":("text_color", TEXT_PRIMARY),
        "start_focus_button":     ("icon_color", TEXT_PRIMARY),
        "reminder_card":          ("md_bg_color", CARD_PRIMARY),
        "reminder_section_label": ("text_color", ACCENT),
        "reminder_label":         ("text_color", TEXT_SECONDARY),
    }

    def on_pre_enter(self, *args):
        self.apply_theme()
        self.load_task()

    def load_task(self):
        if self.current_task_id is None:
            self.ids.header_label.text = "No task selected"
            return

        task = get_task_detail(self.current_task_id)
        if task is None:
            # Task was deleted out from under us -- bail out rather
            # than show a blank/broken detail screen.
            self.go_back()
            return

        self.task = task

        self.ids.header_label.text = task["title"] or "Untitled"

        subtitle_parts = []
        if task["due_date"]:
            subtitle_parts.append(task["due_date"])
        if task["category_name"]:
            subtitle_parts.append(task["category_name"])
        self.ids.subtitle_label.text = (
            " · ".join(subtitle_parts) if subtitle_parts else "No due date"
        )

        self._build_notes_section(task["notes"])
        self._build_pomodoro_section(task["pomodoro_completed_count"])
        self._build_reminder_section(task["reminders"])

    def _build_notes_section(self, notes):
        self.ids.notes_list.clear_widgets()
        text_color = theme_manager.get_color(TEXT_PRIMARY)
        sub_color = theme_manager.get_color(TEXT_SECONDARY)

        if not notes:
            empty = MDLabel(
                text="No notes linked yet",
                theme_text_color="Custom", text_color=sub_color,
                font_style="Body", role="small",
                adaptive_height=True,
            )
            self.ids.notes_list.add_widget(empty)
            return

        for note_id, title, content, updated_at in notes:
            row = BoxLayout(
                orientation="horizontal", size_hint_y=None,
                height=dp(32), spacing=dp(8),
            )

            label = MDLabel(
                text=title or "Untitled",
                theme_text_color="Custom", text_color=text_color,
                font_style="Body", role="medium",
                shorten=True, shorten_from="right",
            )
            label.bind(width=lambda inst, w: setattr(inst, "text_size", (w, None)))
            row.add_widget(label)

            open_btn = MDIconButton(
                icon="chevron-right",
                theme_icon_color="Custom", icon_color=sub_color,
            )
            open_btn.bind(on_release=lambda *_a, nid=note_id: self.open_note(nid))
            row.add_widget(open_btn)

            self.ids.notes_list.add_widget(row)

    def _build_pomodoro_section(self, completed_count):
        self.ids.pomodoro_progress_label.text = (
            f"{completed_count} / {DEFAULT_POMODORO_GOAL} focus sessions"
        )

    def _build_reminder_section(self, reminders):
        if not reminders:
            self.ids.reminder_label.text = "No reminder set"
            return

        # Soonest active reminder, since reminders are already ordered
        # by remind_at ASC in get_task_detail's query.
        active = [r for r in reminders if r[2] == 1]
        if not active:
            self.ids.reminder_label.text = "No active reminder"
            return

        _, remind_at, _ = active[0]
        self.ids.reminder_label.text = f"Reminder at {remind_at}"

    def open_note(self, note_id):
        editor = self.manager.get_screen("note_editor")
        editor.current_note_id = note_id
        self.manager.current = "note_editor"

    def add_note(self):
        if create_notes is None or self.current_task_id is None:
            return
        note_id = create_notes(
            DEFAULT_NOTEBOOK_ID,
            self.task["title"],
            "",
            task_id=self.current_task_id,
        )
        self.open_note(note_id)

    def start_focus_session(self):
        if self.current_task_id is None:
            return
        timer = self.manager.get_screen("timer")
        # timer_screen.py needs a current_task_id attribute added, and
        # needs to call pomodoro_queries.create_pomodoro_session /
        # complete_pomodoro_session when a focus session starts/ends
        # for this to actually save progress -- that's the missing
        # piece flagged earlier ("pomodoro save query yet to write").
        timer.current_task_id = self.current_task_id
        self.manager.current = "timer"

    def go_back(self):
        self.manager.current = "home"