# screens/editor/font_registry.py
# Registers each of the app's fonts as a full Kivy font family (with
# whichever Bold/Italic/BoldItalic files actually exist for it), so
# real [b]/[i] markup works correctly in Preview mode.

import os
from kivy.core.text import LabelBase
from kivy.metrics import sp

from screens.editor.paths import FONTS_DIR

# A fixed list of sizes to step through with the font-size buttons. Kivy
# text widgets only support ONE size for their entire content, not a
# different size per selection -- this is a whole-note setting.
FONT_SIZES = [sp(14), sp(16), sp(18), sp(20), sp(24), sp(28)]


def _font_path(filename):
    # Returns None for a missing filename (either because that style
    # doesn't exist for this font, or the file hasn't been added yet)
    # instead of crashing -- LabelBase.register() is fine receiving
    # None for an optional style and just falls back to Regular for it.
    if filename is None:
        return None
    path = os.path.join(FONTS_DIR, filename)
    return path if os.path.isfile(path) else None


# Each font's available style files. Missing keys (e.g. Caveat has no
# "italic") or missing files on disk are both handled the same way --
# that style just isn't registered, and Kivy uses Regular instead.
_FONT_FAMILY_FILES = {
    "Roboto": {
        "regular": "Roboto-Regular.ttf",
        "bold": "Roboto-Bold.ttf",
        "italic": "Roboto-Italic.ttf",
        "bolditalic": "Roboto-BoldItalic.ttf",
    },
    "OpenSans": {
        "regular": "OpenSans-Regular.ttf",
        "bold": "OpenSans-Bold.ttf",
        "italic": "OpenSans-Italic.ttf",
        "bolditalic": "OpenSans-BoldItalic.ttf",
    },
    "RobotoMono": {
        "regular": "RobotoMono-Regular.ttf",
        "bold": "RobotoMono-Bold.ttf",
        "italic": "RobotoMono-Italic.ttf",
        "bolditalic": "RobotoMono-BoldItalic.ttf",
    },
    "Baskerville": {
        "regular": "Baskerville-Regular.ttf",
        "bold": "Baskerville-Bold.ttf",
        "italic": "Baskerville-Italic.ttf",
        # No official Bold-Italic file exists for Libre Baskerville --
        # left out on purpose, falls back to Bold for that combination.
    },
    "Caveat": {
        "regular": "Caveat-Regular.ttf",
        "bold": "Caveat-Bold.ttf",
        # Handwriting font, no separate italic style exists at all.
    },
    "Yuyu": {
        "regular": "Yuyu-Regular.ttf",
        # No bold/italic files available -- always renders as Regular.
    },
}


def _register_font_families():
    # Registers each font family with Kivy, and returns the list of
    # family keys that were actually registered successfully (skipping
    # any whose Regular file isn't present yet), so FONT_CHOICES only
    # ever offers fonts that genuinely work.
    registered = []
    for family_key, variants in _FONT_FAMILY_FILES.items():
        regular_path = _font_path(variants.get("regular"))
        if regular_path is None:
            continue
        LabelBase.register(
            name=family_key,
            fn_regular=regular_path,
            fn_bold=_font_path(variants.get("bold")),
            fn_italic=_font_path(variants.get("italic")),
            fn_bolditalic=_font_path(variants.get("bolditalic")),
        )
        registered.append(family_key)
    return registered


FONT_CHOICES = _register_font_families()
if not FONT_CHOICES:
    # Should never actually happen (Roboto's Regular file should always
    # be present), but guards against an empty font list just in case.
    FONT_CHOICES = ["Roboto"]


# Maps OLD stored font values (full file paths, from before fonts were
# registered as proper families) to the new short registered family
# key, so notes saved before this change still show the right font.
_LEGACY_FONT_FILENAME_TO_KEY = {
    "opensans-regular.ttf": "OpenSans",
    "robotomono-regular.ttf": "RobotoMono",
    "baskerville-regular.ttf": "Baskerville",
    "caveat-regular.ttf": "Caveat",
    "yuyu-regular.ttf": "Yuyu",
}


def normalize_font_name(font_name):
    # Already a valid new-style family key -- nothing to translate.
    if font_name in FONT_CHOICES:
        return font_name
    # Old-style value was a full path -- match on the filename alone,
    # lowercased, since old paths vary in case and drive letter.
    filename = os.path.basename(font_name).lower()
    return _LEGACY_FONT_FILENAME_TO_KEY.get(filename, "Roboto")