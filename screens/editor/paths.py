# screens/editor/paths.py
# Central place for filesystem paths and small shared constants used
# across the note editor's helper modules, so every module agrees on
# these instead of each hardcoding or recalculating its own copy.
import os

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))     # .../screens/editor
PROJECT_ROOT = os.path.dirname(os.path.dirname(_THIS_DIR))  # two levels up -> project root

FONTS_DIR = os.path.join(PROJECT_ROOT, "fonts")
ATTACHMENTS_DIR = os.path.join(PROJECT_ROOT, "note_attachments")
EXPORTS_DIR = os.path.join(PROJECT_ROOT, "exported_notes")

# Week 3 TEMP: every note needs a notebook_id, but there's no notebook
# creation/selection screen yet -- same placeholder used in
# notes_screen.py, kept here too since image_mixin needs it when
# auto-creating a blank note for a first photo attachment.
DEFAULT_NOTEBOOK_ID = 1