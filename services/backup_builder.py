# services/backup_builder.py
#
# Builds a single, versioned, checksummed JSON "manifest" describing
# a complete snapshot of the app's data -- notes, categories, tasks,
# reminders, attachment records, and anything currently sitting in
# Recently Deleted. This file NEVER writes its own SQL -- it only
# calls query functions that already exist in database/*_queries.py,
# so there is exactly one place in the whole app that knows how notes
# (or tasks, or reminders...) are actually stored.
#
# "Versioned" means every manifest carries a schema_version number.
# That's what lets a future version of the app -- one that's added
# new fields nobody has today -- still know how to safely read an
# older backup instead of guessing at what's missing.

import hashlib
import json
from datetime import datetime, timezone

from database.notes_queries import get_all_notes
from database.category_queries import get_all_categories
from database.task_queries import get_all_tasks
from database.reminder_queries import get_reminders_by_task
from database.attachment_queries import get_all_attachments
import trash_store

from models.note import Note
from models.category import Category
from models.task import Task
from models.reminder import Reminder

from screens.editor.paths import DEFAULT_NOTEBOOK_ID

# The current manifest format version. Bump this only when the
# structure of the "data" section below actually changes shape (a
# field added/removed/renamed) -- not for every code change.
SCHEMA_VERSION = 1

# The app doesn't yet have real multi-user accounts (no
# user_queries.py, no login screen) -- categories and tasks still
# require a user_id today only because the schema has the column.
# This mirrors the same "single implicit default" pattern the note
# editor already uses for DEFAULT_NOTEBOOK_ID. Update this the moment
# a real user system exists.
DEFAULT_USER_ID = 1


def _note_to_dict(row):
    # Reuses the Note model class as the single source of truth for
    # field names/order, instead of redefining that mapping here too
    # -- if Tabshira ever reorders notes' columns, this line doesn't
    # need to change, only models/note.py does.
    return vars(Note(*row))


def _category_to_dict(row):
    return vars(Category(*row))


def _task_to_dict(row):
    return vars(Task(*row))


def _reminder_to_dict(row):
    return vars(Reminder(*row))


def _attachment_to_dict(row):
    # No Attachment model class exists yet -- built as a plain dict
    # here. Column order matches the "attachments" table in db.py:
    # id, note_id, file_path, created_at.
    return {
        "id": row[0],
        "note_id": row[1],
        "file_path": row[2],
        "created_at": row[3],
    }


def _collect_notes():
    rows = get_all_notes(DEFAULT_NOTEBOOK_ID)
    return [_note_to_dict(row) for row in rows]


def _collect_categories():
    rows = get_all_categories(DEFAULT_USER_ID)
    return [_category_to_dict(row) for row in rows]


def _collect_tasks():
    rows = get_all_tasks(DEFAULT_USER_ID)
    return [_task_to_dict(row) for row in rows]


def _collect_reminders(tasks):
    # There's no get_all_reminders() -- only get_reminders_by_task().
    # Looping over every task and collecting its reminders reuses that
    # existing function rather than writing a new query, and still
    # captures inactive reminders too (get_active_reminders() would
    # have silently dropped those).
    reminders = []
    for task in tasks:
        rows = get_reminders_by_task(task["id"])
        reminders.extend(_reminder_to_dict(row) for row in rows)
    return reminders


def _collect_attachments(notes):
    # Same technique as _collect_reminders -- get_all_attachments()
    # needs a note_id, so we loop over every note and gather its
    # attachments. This only backs up the ATTACHMENT RECORDS (id,
    # file path, timestamp) -- the actual image files on disk in
    # note_attachments/ are a separate concern for a later phase
    # (uploading/copying binary files alongside this manifest).
    attachments = []
    for note in notes:
        rows = get_all_attachments(note["id"])
        attachments.extend(_attachment_to_dict(row) for row in rows)
    return attachments


def _collect_trash():
    # trash_store already returns plain dicts (it's backed by JSON,
    # not SQLite), so no tuple-to-dict mapping is needed here.
    return trash_store.get_trash_entries()


def _compute_checksum(data):
    # sort_keys=True is what makes this deterministic -- the same
    # data always produces the same checksum regardless of what order
    # Python happened to build the dictionary in. Without this, the
    # checksum would be useless for corruption detection, since it
    # could differ even when nothing actually changed.
    canonical = json.dumps(data, sort_keys=True, default=str)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def build_backup_manifest():
    """
    Builds and returns one complete manifest dictionary describing the
    current state of the app's data. Does not touch the network or the
    filesystem -- this function is pure data assembly, which is what
    makes it fully testable offline.
    """
    notes = _collect_notes()
    categories = _collect_categories()
    tasks = _collect_tasks()
    reminders = _collect_reminders(tasks)
    attachments = _collect_attachments(notes)
    trash = _collect_trash()

    data = {
        # Intentionally empty for now -- there's no notebook_queries.py
        # yet, and the app currently only ever uses one implicit
        # default notebook (DEFAULT_NOTEBOOK_ID). Restoring always
        # targets that same default, matching how notes are created
        # today. Revisit once real notebook management exists.
        "notebooks": [],
        "categories": categories,
        "notes": notes,
        "tasks": tasks,
        "reminders": reminders,
        "attachments": attachments,
        "trash": trash,
    }

    return {
        "schema_version": SCHEMA_VERSION,
        "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "checksum": _compute_checksum(data),
        "encrypted": False,
        "data": data,
    }


def save_manifest_to_path(manifest, file_path):
    """
    Writes a manifest dictionary to disk as a JSON file. Kept separate
    from build_backup_manifest() so callers (manual export, Drive
    upload) can build once and choose where it goes.
    """
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)


def verify_manifest_checksum(manifest):
    """
    Returns True if the manifest's stored checksum matches its actual
    data. Used before ever restoring a backup -- if this returns
    False, the file was corrupted or tampered with somewhere between
    being created and being read back.
    """
    return manifest.get("checksum") == _compute_checksum(manifest.get("data", {}))