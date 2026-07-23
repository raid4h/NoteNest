# screens/notes/helpers.py
# Pure formatting helpers used when building note card previews.

from datetime import datetime, timezone
import re

from screens.editor.note_meta import META_PATTERN
from screens.editor.markup import IMAGE_TOKEN_PATTERN, LINK_TOKEN_PATTERN


def format_last_edited(updated_at):
    if not updated_at:
        return ""

    try:
        # SQLite's CURRENT_TIMESTAMP stores time in UTC, not this
        # device's local time zone -- parse as UTC first, then convert
        # to the machine's actual local time zone.
        dt_utc = datetime.strptime(updated_at, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
        dt_local = dt_utc.astimezone()
    except (ValueError, TypeError):
        return f"Edited {updated_at}"

    now_local = datetime.now().astimezone()
    delta = now_local - dt_local
    seconds = delta.total_seconds()
    if seconds < 0:
        seconds = 0

    if seconds < 60:
        return "Edited just now"

    minutes = int(seconds // 60)
    if minutes < 60:
        return f"Edited {minutes} minute{'s' if minutes != 1 else ''} ago"

    hours = int(minutes // 60)
    if hours < 24:
        return f"Edited {hours} hour{'s' if hours != 1 else ''} ago"

    days = delta.days
    if days == 1:
        return "Edited yesterday"
    if days < 7:
        return f"Edited {days} days ago"

    return f"Edited {dt_local.strftime('%b %d, %Y')}"


def clean_preview_text(content):
    # Strips internal formatting/metadata markers out of a note's raw
    # stored content, so the preview shows clean readable text.
    if not content:
        return ""

    text = content
    text = META_PATTERN.sub("", text)
    text = IMAGE_TOKEN_PATTERN.sub("[Photo] ", text)
    text = LINK_TOKEN_PATTERN.sub(lambda m: m.group(2), text)

    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text, flags=re.DOTALL)
    text = re.sub(r"__(.+?)__", r"\1", text, flags=re.DOTALL)
    text = re.sub(r"==(.+?)==", r"\1", text, flags=re.DOTALL)
    text = re.sub(r"\*(.+?)\*", r"\1", text, flags=re.DOTALL)

    return text.strip()