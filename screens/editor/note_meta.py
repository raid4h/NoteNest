# screens/editor/note_meta.py
# Handles the hidden per-note metadata marker (font, size, alignment)
# prepended to a note's stored content -- same inline-marker trick as
# {{img:...}} tokens, so no database changes are needed.

import re
from kivy.metrics import sp

from screens.editor.font_registry import FONT_CHOICES, normalize_font_name

DEFAULT_FONT_NAME = "Roboto"
DEFAULT_FONT_SIZE = sp(16)
DEFAULT_ALIGN = "left"

META_PATTERN = re.compile(r"^\{\{meta:(.*?)\}\}\n?")


def parse_note_meta(stored_content):
    """Returns (font_name, font_size, halign, visible_content)."""
    match = META_PATTERN.match(stored_content)
    if not match:
        return DEFAULT_FONT_NAME, DEFAULT_FONT_SIZE, DEFAULT_ALIGN, stored_content

    settings = {}
    for pair in match.group(1).split("|"):
        if "=" in pair:
            key, value = pair.split("=", 1)
            settings[key] = value

    font_name = normalize_font_name(settings.get("font", DEFAULT_FONT_NAME))
    try:
        font_size = float(settings.get("size", DEFAULT_FONT_SIZE))
    except ValueError:
        font_size = DEFAULT_FONT_SIZE
    halign = settings.get("align", DEFAULT_ALIGN)

    visible_content = stored_content[match.end():]
    return font_name, font_size, halign, visible_content


def build_note_meta(font_name, font_size, halign):
    return f"{{{{meta:font={font_name}|size={font_size}|align={halign}}}}}\n"