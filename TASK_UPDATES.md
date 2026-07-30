# Task Feature Update

Implemented faculty-requested task updates:

1. **Time and notifications**
   - Tasks accept a 24-hour `HH:MM` time.
   - Optional notification is scheduled at the task date and time.
   - Uses Plyer native notifications when available.
   - Falls back to an in-app popup.
   - A reminder fires once and is disabled when the task is completed.

2. **Daily carry-forward**
   - Unfinished tasks can automatically appear on each following calendar day.
   - Carry-forward is limited through the current day, so future dates are not
     filled prematurely.
   - The original due date remains unchanged.
   - Completing the task stops later occurrences immediately.

3. **Embedded links**
   - The Add Task form stores an optional URL.
   - The task card displays an “Open embedded link” action.
   - URLs without a scheme automatically open with `https://`.

## Validation

- All Python files compile successfully.
- Database migration was tested against a copy of the original database.
- Automated tests cover carry-forward, completion cutoff, link persistence,
  and one-time reminder firing.

Run:

```bash
python -m unittest test_task_updates.py -v
python main.py
```

## Calendar UI refresh

- Replaced the basic calendar with a themed **Month + Agenda** layout.
- Calendar colors now come from `theme_manager` semantic palette tokens.
- Added selected-date highlighting, today outline, task indicators, category filters, and an agenda summary.
- Replaced the basic Add Task popup with a rounded, scrollable popup that matches the active app theme.
- Added reusable user-defined categories through the existing `categories` table.
- Kept task carry-forward, embedded links, completion, and in-app/system notification behavior connected to the main database.

## Calendar and task-entry polish

- The month calendar now scales responsively and stays short enough to keep the selected day's agenda visible on the same screen.
- Tapping a date resets the category filter to **All**, reloads every task for that date, and scrolls the agenda to its first item.
- The Add Task fields remain editable and support normal Backspace behavior.
- Typed text and the caret are black in NoteNest's light themes, while dark themes continue using semantic theme colors.
- Focused fields use the active theme accent border for clearer keyboard editing.

