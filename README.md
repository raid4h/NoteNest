# NoteNest

## Faculty task updates

The calendar task module now supports:

- task due date and 24-hour due time
- optional foreground/native notifications at the selected time
- daily carry-forward of unfinished tasks through the current day
- completion persistence, which stops future carry-forward and reminders
- embedded web links that open from the task card

Run the app from this folder with:

```bash
python main.py
```

Native desktop/mobile notifications use `plyer` when available. Without it,
NoteNest falls back to an in-app reminder popup.
