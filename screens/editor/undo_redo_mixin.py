# screens/editor/undo_redo_mixin.py
# Undo/redo history for the whole note (full-text snapshots, not
# per-keystroke), plus the live word/character count.

from kivy.clock import Clock


class UndoRedoMixin:
    """Requires: self.ids.content_field, self._undo_stack,
    self._redo_stack, self._suppress_history, self._history_debounce_event
    (all set in __init__)."""

    def _on_content_text_changed(self, field, value):
        self._update_word_count(value)

        if self._suppress_history:
            return

        if self._history_debounce_event:
            self._history_debounce_event.cancel()
        self._history_debounce_event = Clock.schedule_once(self._push_history_snapshot, 1.2)

    def _push_history_snapshot(self, dt):
        field = self.ids.content_field
        current_text = field.text

        if self._undo_stack and self._undo_stack[-1] == current_text:
            return

        self._undo_stack.append(current_text)
        if len(self._undo_stack) > 50:
            self._undo_stack.pop(0)
        self._redo_stack.clear()

    def undo_note(self):
        if self._history_debounce_event:
            self._history_debounce_event.cancel()
            self._history_debounce_event = None

        if len(self._undo_stack) < 2:
            return

        field = self.ids.content_field
        current = self._undo_stack.pop()
        self._redo_stack.append(current)
        previous = self._undo_stack[-1]

        self._suppress_history = True
        field.text = previous
        field.cursor = field.get_cursor_from_index(len(previous))
        self._suppress_history = False

    def redo_note(self):
        if not self._redo_stack:
            return

        field = self.ids.content_field
        next_text = self._redo_stack.pop()
        self._undo_stack.append(next_text)

        self._suppress_history = True
        field.text = next_text
        field.cursor = field.get_cursor_from_index(len(next_text))
        self._suppress_history = False

    def _update_word_count(self, text):
        char_count = len(text)
        word_count = len(text.split()) if text.strip() else 0
        if "word_count_label" in self.ids:
            self.ids.word_count_label.text = f"{word_count} words · {char_count} chars"