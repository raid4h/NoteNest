# one note card widget (used by home_screen)
# widgets/note_card.py

# widgets/note_card.py

from kivy.properties import StringProperty, NumericProperty, BooleanProperty
from kivymd.uix.card import MDCard

class NoteCard(MDCard):
    title = StringProperty("Untitled")
    preview = StringProperty("")
    note_id = NumericProperty(0)
    is_pinned = BooleanProperty(False)