# widgets/hourglass.py
#
# Image-based hourglass: two stacked, tintable PNG layers instead of
# canvas-drawn shapes. The glass outline is one static image; the sand
# swaps between 6 pre-made stage images as progress changes. Both are
# tinted at runtime via each Image's `color` property, which only
# looks correct because the source PNGs are plain white on transparent
# backgrounds (see the tinting explanation in chat).
#
# Public interface is unchanged: progress, glass_color, sand_color.
# timer_screen.py and timer_screen.kv do not need any changes.

import os

from kivy.uix.image import Image
from kivy.uix.relativelayout import RelativeLayout
from kivy.properties import NumericProperty, ColorProperty

ASSET_DIR = "assets/hourglass"
SAND_STAGE_PERCENTS = (0, 20, 40, 60, 80, 100)


class HourglassWidget(RelativeLayout):

    progress = NumericProperty(0.0)

    glass_color = ColorProperty("#000000")
    sand_color = ColorProperty("#000000")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Sand is added first (drawn behind), outline added second
        # (drawn in front), so the glass frame always reads on top.
        self._sand_image = Image(
            source=self._sand_source_for_progress(0.0),
            allow_stretch=True,
            keep_ratio=True,
        )
        self._outline_image = Image(
            source=os.path.join(ASSET_DIR, "glass_outline.png"),
            allow_stretch=True,
            keep_ratio=True,
        )

        self.add_widget(self._sand_image)
        self.add_widget(self._outline_image)

        self.bind(
            size=self._layout_images,
            pos=self._layout_images,
            progress=self._update_sand_stage,
            glass_color=self._update_colors,
            sand_color=self._update_colors,
        )

        self._layout_images()
        self._update_colors()

    def _layout_images(self, *args):
        # RelativeLayout positions children relative to its own corner,
        # so "fill the whole widget" is always just (0, 0) + full size.
        for image in (self._sand_image, self._outline_image):
            image.size = self.size
            image.pos = (0, 0)

    def _update_colors(self, *args):
        self._outline_image.color = self.glass_color
        self._sand_image.color = self.sand_color

    def _update_sand_stage(self, *args):
        self._sand_image.source = self._sand_source_for_progress(self.progress)

    @staticmethod
    def _sand_source_for_progress(progress):
        progress = max(0.0, min(1.0, progress))
        stage_count = len(SAND_STAGE_PERCENTS)
        stage_index = round(progress * (stage_count - 1))
        percent = SAND_STAGE_PERCENTS[stage_index]
        return os.path.join(ASSET_DIR, f"sand_{percent:02d}.png")