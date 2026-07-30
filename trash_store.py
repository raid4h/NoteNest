# trash_store.py
# A small local "Recently Deleted" store for notes, kept entirely
# separate from Tabshira's database layer -- deleting a note here does
# NOT touch the notes/attachments tables at all. It just remembers a
# snapshot of the note in a local JSON file right before the note is
# permanently removed from the database, so it can be restored later.

import os
import json
from datetime import datetime, timezone

_PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
TRASH_FILE = os.path.join(_PROJECT_ROOT, "trash.json")


def _load_trash():
    if not os.path.exists(TRASH_FILE):
        return []
    try:
        with open(TRASH_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        # Corrupted or unreadable trash file -- treat as empty rather
        # than crashing the whole app on startup.
        return []


def _save_trash(entries):
    with open(TRASH_FILE, "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=2)


def _next_trash_id(entries):
    # An id local to this trash file only -- unrelated to the
    # database's own note ids, since a restored note gets a brand-new
    # database id anyway (the original row is already gone for good).
    if not entries:
        return 1
    return max(e["trash_id"] for e in entries) + 1


def add_to_trash(notebook_id, title, content, category_id):
    # Called right before a note is permanently deleted -- stores
    # everything needed to recreate it later.
    entries = _load_trash()
    entry = {
        "trash_id": _next_trash_id(entries),
        "notebook_id": notebook_id,
        "title": title,
        "content": content,
        "category_id": category_id,
        "deleted_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
    }
    entries.append(entry)
    _save_trash(entries)


def get_trash_entries():
    # Most-recently-deleted first.
    entries = _load_trash()
    return sorted(entries, key=lambda e: e["deleted_at"], reverse=True)


def get_trash_entry(trash_id):
    for e in _load_trash():
        if e["trash_id"] == trash_id:
            return e
    return None


def remove_from_trash(trash_id):
    entries = _load_trash()
    entries = [e for e in entries if e["trash_id"] != trash_id]
    _save_trash(entries)