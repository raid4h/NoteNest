# screens/category_helpers.py
# Shared helpers for note categories -- used by both the note editor
# (assigning a category while editing) and the notes list (filtering
# by category, showing a color indicator). Wraps Tabshira's
# category_queries.py with a placeholder user id, same pattern as
# DEFAULT_NOTEBOOK_ID until a real login system exists.

from database.category_queries import (
    create_category, get_all_categories, get_categories_by_id,
    assign_categories_to_notes, delete_categories,
)
from database.notes_queries import get_all_notes
from screens.editor.paths import DEFAULT_NOTEBOOK_ID

DEFAULT_USER_ID = 1

# A small preset palette instead of a full color picker -- keeps
# category colors consistent with the app's existing cottagecore
# palette instead of letting arbitrary colors clash with it.
CATEGORY_COLOR_PRESETS = [
    ("Sage", (0.72, 0.79, 0.54, 1)),
    ("Caramel", (0.54, 0.35, 0.17, 1)),
    ("Cocoa", (0.29, 0.20, 0.15, 1)),
    ("Blush", (0.82, 0.58, 0.56, 1)),
    ("Dusty Blue", (0.55, 0.64, 0.71, 1)),
    ("Mustard", (0.80, 0.65, 0.30, 1)),
]


def _color_to_hex(rgba):
    r, g, b = rgba[0], rgba[1], rgba[2]
    return "#{:02X}{:02X}{:02X}".format(int(r * 255), int(g * 255), int(b * 255))


def _hex_to_rgba(hex_color):
    hex_color = (hex_color or "").lstrip("#")
    if len(hex_color) != 6:
        return (0.7, 0.7, 0.7, 1)
    r = int(hex_color[0:2], 16) / 255
    g = int(hex_color[2:4], 16) / 255
    b = int(hex_color[4:6], 16) / 255
    return (r, g, b, 1)


def list_categories():
    """Returns raw rows: (id, name, color, user_id)."""
    return get_all_categories(DEFAULT_USER_ID)


def get_category(category_id):
    if category_id is None:
        return None
    return get_categories_by_id(category_id)


def make_category(name, color_rgba):
    return create_category(name.strip(), _color_to_hex(color_rgba), DEFAULT_USER_ID)


def assign_category(note_id, category_id):
    assign_categories_to_notes(note_id, category_id)

def rename_category(category_id, new_name, new_color_rgba):
    from database.category_queries import update_categories
    update_categories(category_id, new_name.strip(), _color_to_hex(new_color_rgba))

def delete_category(category_id):
    # Clears this category off any notes using it BEFORE deleting it,
    # so no note is left pointing at a category that no longer exists
    # (which would otherwise show a stale stripe color, or crash when
    # something tries to look up that missing category).
    notes = get_all_notes(DEFAULT_NOTEBOOK_ID)
    for note in notes:
        if note[8] == category_id:
            assign_categories_to_notes(note[0], None)
    delete_categories(category_id)


def category_color_rgba(color_hex):
    return _hex_to_rgba(color_hex)

def contrasting_text_color(rgba):
    # Standard relative-luminance formula -- picks near-black or
    # near-white text depending on how light or dark the background
    # color is, so category text never blends into its own chip
    # (this was the actual cause of the brown category being
    # unreadable with a fixed dark text color).
    r, g, b = rgba[0], rgba[1], rgba[2]
    luminance = 0.299 * r + 0.587 * g + 0.114 * b
    return (0.15, 0.10, 0.08, 1) if luminance > 0.55 else (0.98, 0.97, 0.94, 1)