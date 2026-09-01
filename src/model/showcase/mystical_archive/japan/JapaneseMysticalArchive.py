from PIL import Image, ImageDraw

from constants import CARD_TITLE, CARD_WATERMARK_COLOR, FRAMES_PATH
from model.Layer import Layer
from model.regular.RegularCard import RegularCard
from model.showcase.mystical_archive.japan.JapaneseMysticalArchiveHorizontal import (
    JapaneseMysticalArchiveHorizontal,
)
from utils import load_font, open_image


class JapaneseMysticalArchive(JapaneseMysticalArchiveHorizontal):
    """
    A layered image representing a Japanese Mystical Archive frame with a vertical title box
    that expands to fit (traditionally) kanjis inside it.

    Attributes
    ----------
    metadata : dict[str, str | list], optional
        Information about the card (title, mana cost, rules text, frame, etc.)

    base_width : int, optional
        The width of the root image. Determined by the frame layout in the metadata if not given.

    base_height : int, optional
        The height of the root image. Determined by the frame layout in the metadata if not given.

    art_layer : Layer, optional
        The art to use in the art slot of the frame. Renders first, before the frame layers.

    frame_layers : list[Layer], optional
        The layers of card frames. Lower-index layers are rendered first. Renders after art, before collector info.

    collector_layers : list[Layer], optional
        The layers of collector info. Lower-index layers are rendered first. Renders after frames, before text.

    text_layers : list[Layer], optional
        The layers of card text. Lower-index layers are rendered first. Renders after collector info and frames.

    overlay_layers : list[Layer], optional
        Any additional layers to render above everything else on the card. Rendered absolutely last.
    """

    def __init__(
        self,
        metadata: dict[str, str | list["RegularCard"]] = None,
        art_layer: Layer = None,
        frame_layers: list[Layer] = None,
        collector_layers: list[Layer] = None,
        text_layers: list[Layer] = None,
        overlay_layers: list[Layer] = None,
    ):
        super().__init__(
            metadata,
            art_layer,
            frame_layers,
            collector_layers,
            text_layers,
            overlay_layers,
        )

        # Title Box
        self.TITLE_BOX_X = 157
        self.TITLE_BOX_TOP_Y = 137
        self.TITLE_BOX_WIDTH = 289
        self.MAX_TITLE_BOX_HEIGHT = 1288

        # Where the three slices live: <dir>/{top,middle,bottom}/<color>.png
        self.TITLE_FRAME_DIR = f"{FRAMES_PATH}/showcase/mystical_archive/japan/title"
        self.TITLE_COLOR_FALLBACK = "artifact"

        # Mana Cost
        self.MANA_COST_SYMBOL_SIZE = 135
        self.MANA_COST_BOX_X = 500
        self.MANA_COST_BOX_Y = 96
        self.MANA_COST_BOX_WIDTH = 1404
        self.MANA_COST_BOX_HEIGHT = 199

        # Title Text
        self.TITLE_TEXT_PAD_Y = 75
        self.TITLE_GLYPH_SPACING = 5
        self.TITLE_SPACE_HEIGHT = 20

        # Type Text
        self.TYPE_WIDTH = 569
        self.TYPE_TEXT_ALIGN = "center"

        # Set / Rarity Symbol
        self.SET_SYMBOL_X = 1613
        self.SET_SYMBOL_Y = 1514
        self.SET_SYMBOL_WIDTH = 233

        # Needed because the title bar size is determined by the title text size
        self._vertical_title_layout = None

    def _get_title_colors(self):
        raw = self.get_metadata(CARD_WATERMARK_COLOR) or ""
        colors = [c.strip().lower() for c in raw.split("\n") if c.strip()]
        if not colors:
            return [self.TITLE_COLOR_FALLBACK]
        return colors[:2]

    def _load_title_slices(self, color):
        top = open_image(f"{self.TITLE_FRAME_DIR}/top/{color}.png").convert("RGBA")
        middle = open_image(f"{self.TITLE_FRAME_DIR}/middle/{color}.png").convert("RGBA")
        bottom = open_image(f"{self.TITLE_FRAME_DIR}/bottom/{color}.png").convert("RGBA")
        return top, middle, bottom

    def _glyph_ink_box(self, char, font):
        """
        (left, top, right, bottom) of the glyph's ink relative to a draw origin
        using anchor="la". Whitespace has no ink, so give it a fixed height.
        """

        if char.isspace():
            return (0, 0, 0, self.TITLE_SPACE_HEIGHT)
        left, top, right, bottom = font.getbbox(char, anchor="la")
        if bottom <= top:
            return (0, 0, 0, self.TITLE_SPACE_HEIGHT)
        return (left, top, right, bottom)

    def _build_vertical_glyphs(self, text, font_size):
        """
        Parse {DIRECTIVE} markup and flatten into [(char, font, ink_box), ...].
        """

        primary_font = load_font(self.TITLE_FONT, font_size)
        fallback_fonts = self._load_fallback_fonts(self.TITLE_FONT, font_size)

        glyphs = []
        for chunk_text, chunk_font, _ in self._split_ucs_chunks(text, primary_font, fallback_fonts):
            for char in chunk_text:
                glyphs.append((char, chunk_font, self._glyph_ink_box(char, chunk_font)))
        return glyphs, primary_font, fallback_fonts

    def _measure_vertical_text(self, glyphs):
        if not glyphs:
            return 0
        ink_total = sum(box[3] - box[1] for _, _, box in glyphs)
        return ink_total + self.TITLE_GLYPH_SPACING * (len(glyphs) - 1)

    def _get_vertical_title_layout(self):
        if self._vertical_title_layout is not None:
            return self._vertical_title_layout

        text = self.get_metadata(CARD_TITLE) or ""

        # Cap heights are identical across colours
        top, _, bottom = self._load_title_slices(self._get_title_colors()[0])
        min_box_height = top.height + bottom.height
        pad_total = 2 * self.TITLE_TEXT_PAD_Y
        max_text_height = self.MAX_TITLE_BOX_HEIGHT - pad_total

        # Measures height instead of width
        font_size = self.TITLE_MAX_FONT_SIZE
        while True:
            glyphs, primary_font, fallback_fonts = self._build_vertical_glyphs(text, font_size)
            text_height = self._measure_vertical_text(glyphs)
            if text_height <= max_text_height or font_size <= self.TITLE_MIN_FONT_SIZE:
                break
            font_size -= 1

        box_height = text_height + pad_total
        box_height = max(min_box_height, min(self.MAX_TITLE_BOX_HEIGHT, box_height))

        text_top = (box_height - text_height) // 2

        self._vertical_title_layout = {
            "glyphs": glyphs,  # [(char, font, ink_box), ...]
            "primary_font": primary_font,
            "fallback_fonts": fallback_fonts,
            "font_size": font_size,
            "text_height": text_height,
            "text_top": text_top,
            "box_height": box_height,
        }
        return self._vertical_title_layout

    def _build_title_box(self, color, box_height):
        top, middle, bottom = self._load_title_slices(color)

        middle_height = max(1, box_height - top.height - bottom.height)
        middle = middle.resize((self.TITLE_BOX_WIDTH, middle_height))

        box = Image.new("RGBA", (self.TITLE_BOX_WIDTH, box_height), (0, 0, 0, 0))
        box.alpha_composite(top, (0, 0))
        box.alpha_composite(middle, (0, top.height))
        box.alpha_composite(bottom, (0, top.height + middle_height))
        return box

    def _create_frame_layers(self):
        super()._create_frame_layers()

        layout = self._get_vertical_title_layout()
        colors = self._get_title_colors()
        box_height = layout["box_height"]

        box = self._build_title_box(colors[0], box_height)

        if len(colors) > 1:
            top_half = box
            bottom_half = self._build_title_box(colors[1], box_height)
            mask = open_image(f"{FRAMES_PATH}/regular/mask/top.png").resize(bottom_half.size).getchannel("A")
            # First color on top, second on the bottom, split at the midline.
            box = Image.composite(top_half, bottom_half, mask)

        self.frame_layers.append(Layer(box, (self.TITLE_BOX_X, self.TITLE_BOX_TOP_Y)))

    def _create_title_layer(self):
        layout = self._get_vertical_title_layout()

        canvas = Image.new("RGBA", (self.TITLE_BOX_WIDTH, layout["box_height"]), (0, 0, 0, 0))
        draw = ImageDraw.Draw(canvas)

        ink_y = layout["text_top"]  # where this glyph's ink top goes
        for char, font, (left, top, right, bottom) in layout["glyphs"]:
            ink_w = right - left
            ink_h = bottom - top

            if not char.isspace():
                origin_x = (self.TITLE_BOX_WIDTH - ink_w) / 2 - left
                origin_y = ink_y - top
                self._draw_ucs_chunks(
                    draw,
                    (origin_x, origin_y),
                    char,
                    font,
                    layout["fallback_fonts"],
                    primary_font_path=self.TITLE_FONT,
                    font_size=layout["font_size"],
                    fill=self.TITLE_FONT_COLOR,
                    anchor="la",
                )

            ink_y += ink_h + self.TITLE_GLYPH_SPACING

        self.text_layers.append(Layer(canvas, (self.TITLE_BOX_X, self.TITLE_BOX_TOP_Y)))

    def _create_mana_cost_layer(self):
        """
        Draw the mana cost on the far right side of the frame.
        """

        saved = (self.TITLE_BOX_X, self.TITLE_BOX_Y, self.TITLE_BOX_WIDTH, self.TITLE_BOX_HEIGHT)
        saved_mana_cost_x = getattr(self, "mana_cost_x", None)

        self.TITLE_BOX_X = self.MANA_COST_BOX_X
        self.TITLE_BOX_Y = self.MANA_COST_BOX_Y
        self.TITLE_BOX_WIDTH = self.MANA_COST_BOX_WIDTH
        self.TITLE_BOX_HEIGHT = self.MANA_COST_BOX_HEIGHT
        try:
            super()._create_mana_cost_layer()
        finally:
            (self.TITLE_BOX_X, self.TITLE_BOX_Y, self.TITLE_BOX_WIDTH, self.TITLE_BOX_HEIGHT) = saved
            self.mana_cost_x = saved_mana_cost_x
