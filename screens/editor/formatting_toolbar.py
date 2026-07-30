# screens/editor/formatting_toolbar.py
# The bold/italic/undo/align/font toolbar, pulled out as its own
# reusable widget so the SAME instance can be moved between two
# different positions (docked at top for wide screens, floating at
# the bottom for narrow ones) instead of duplicating every button
# twice in app.kv.

from kivymd.uix.card import MDCard
from kivy.properties import BooleanProperty

class FormattingToolbar(MDCard):
    # Set from Python whenever the toolbar is moved -- the KV rule
    # below uses this to switch between its two visual styles (flat
    # and docked, vs rounded/elevated and floating).

    is_compact = BooleanProperty(False)
