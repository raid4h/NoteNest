#
    #A small tappable pill-shaped tag for filtering by category.
    #Toggles between selected and unselected state when tapped.
    
    #Usage
    #    chip = CategoryChip(category="Study")
    #    chip.bind(on_select=my_filter_function)
    #  18-7-2026, I have added the method inside the checklist_item ( check again before)


from kivy.uix.button import Button
from kivy.properties import StringProperty, BooleanProperty, ObjectProperty


class CategoryChip(Button):
    
    category = StringProperty("Study")
    selected = BooleanProperty(False)
    on_select = ObjectProperty(None, allownone=True)

    # Color mapping — unselected vs selected per category
    COLORS = {
        "Study":  {
            "normal":   (0.98, 0.87, 0.85, 1),
            "selected": (0.85, 0.30, 0.20, 1),
        },
        "Life":   {
            "normal":   (0.91, 0.95, 0.87, 1),
            "selected": (0.25, 0.65, 0.30, 1),
        },
        "Health": {
            "normal":   (0.90, 0.94, 0.98, 1),
            "selected": (0.20, 0.45, 0.80, 1),
        },
        "Work":   {
            "normal":   (0.98, 0.90, 0.90, 1),
            "selected": (0.75, 0.20, 0.20, 1),
        },
        "All":    {
            "normal":   (0.91, 0.88, 0.86, 1),
            "selected": (0.24, 0.19, 0.15, 1),
        },
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (90, 32)
        self.font_size = 12
        self.bold = True
        self.background_normal = ""
        self.border = (0, 0, 0, 0)
        self.update_style()
        self.bind(on_press=self.toggle)

    def toggle(self, instance):
        """Toggle selected state and update appearance."""
        self.selected = not self.selected
        self.update_style()

        # Notify parent screen that selection changed
        if self.on_select:
            self.on_select(self.category, self.selected)

    def update_style(self):
        """Update color and text based on selected state."""
        colors = self.COLORS.get(self.category, self.COLORS["All"])

        if self.selected:
            self.background_color = colors["selected"]
            self.color = (1, 1, 1, 1)  # white text when selected
        else:
            self.background_color = colors["normal"]
            self.color = (0.29, 0.20, 0.15, 1)  # dark text when unselected

        self.text = self.category

    def deselect(self):
        """Programmatically deselect this chip."""
        self.selected = False
        self.update_style()