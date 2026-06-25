from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, BooleanProperty
from kivy.lang import Builder
from kivy.graphics import Color, RoundedRectangle, Line
from kivy.clock import Clock

Builder.load_string("""
<ChecklistItem>:
    orientation: "horizontal"
    size_hint_y: None
    height: 60
    spacing: 12
    padding: [16, 0, 16, 0]

    Widget:
        size_hint_x: None
        width: 28
        canvas:
            Color:
                rgba: (0.91, 0.66, 0.49, 1) if root.checked else (1, 1, 1, 1)
            Ellipse:
                pos: self.x, self.center_y - 14
                size: (28, 28)
            Color:
                rgba: (0.91, 0.66, 0.49, 1) if root.checked else (0.75, 0.68, 0.58, 1)
            Line:
                ellipse: [self.x, self.center_y - 14, 28, 28]
                width: 1.5

    Label:
        text: root.text
        font_size: "14sp"
        color: (0.65, 0.60, 0.54, 1) if root.checked else (0.20, 0.15, 0.10, 1)
        halign: "left"
        valign: "middle"
        text_size: self.size
        strikethrough: root.checked

    BoxLayout:
        size_hint_x: None
        width: 70
        padding: [0, 16, 0, 16]
        canvas.before:
            Color:
                rgba: \
                    (0.99, 0.91, 0.85, 1) if root.tag == "Study" else \
                    (0.88, 0.97, 0.88, 1) if root.tag == "Life" else \
                    (0.88, 0.91, 0.99, 1) if root.tag == "Health" else \
                    (0.99, 0.93, 0.85, 1) if root.tag == "Work" else \
                    (0.93, 0.91, 0.88, 1)
            RoundedRectangle:
                pos: self.pos
                size: self.size
                radius: [20,]
        Label:
            text: root.tag
            font_size: "11sp"
            bold: True
            color: \
                (0.80, 0.38, 0.15, 1) if root.tag == "Study" else \
                (0.22, 0.58, 0.22, 1) if root.tag == "Life" else \
                (0.28, 0.35, 0.78, 1) if root.tag == "Health" else \
                (0.72, 0.42, 0.15, 1) if root.tag == "Work" else \
                (0.45, 0.40, 0.33, 1)

    on_touch_down:
        if self.collide_point(*args[1].pos): root.toggle()
""")


class ChecklistItem(BoxLayout):
    text = StringProperty("")
    checked = BooleanProperty(False)
    tag = StringProperty("General")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(self._draw_bg, 0)
        self.bind(pos=self._draw_bg, size=self._draw_bg, checked=self._draw_bg)

    def _draw_bg(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(1, 1, 1, 1)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[16])
            Color(0.90, 0.85, 0.78, 1)
            Line(rounded_rectangle=[self.x, self.y, self.width, self.height, 16], width=1)

    def toggle(self):
        self.checked = not self.checked