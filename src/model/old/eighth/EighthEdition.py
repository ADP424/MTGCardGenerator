from PIL import Image, ImageDraw

from constants import (
    BLACK_BRUSH,
    CARD_ARTIST,
    CARD_CREATION_DATE,
    MATRIX_BOLD,
    MATRIX_BOLD_SMALL_CAPS,
)
from model.Layer import Layer
from model.regular.RegularCard import RegularCard
from utils import load_font


class EighthEdition(RegularCard):
    """
    A layered image representing an 8th Edition-bordered card and all the collection info on it,
    with all relevant card metadata.

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

        # Mana Cost
        self.MANA_COST_SYMBOL_SIZE = 88

        # Title Box
        self.TITLE_BOX_X = 70
        self.TITLE_BOX_Y = 163
        self.TITLE_BOX_WIDTH = 1781
        self.TITLE_BOX_HEIGHT = 155

        # Title Text
        self.TITLE_X = 181
        self.TITLE_BOTTOM_Y = 305
        self.TITLE_MAX_FONT_SIZE = 120
        self.TITLE_FONT = MATRIX_BOLD

        # Type Box
        self.TYPE_BOX_Y = 1590
        self.TYPE_BOX_HEIGHT = 153

        # Type Text
        self.TYPE_X = 205
        self.TYPE_BOTTOM_Y = 1726
        self.TYPE_MAX_FONT_SIZE = 102
        self.TYPE_FONT = MATRIX_BOLD

        # Rules Text Box
        self.RULES_BOX_X = 172
        self.RULES_BOX_Y = 1762
        self.RULES_BOX_WIDTH = 1656
        self.RULES_BOX_HEIGHT = 752

        # Rules Text
        self.RULES_TEXT_X = 179
        self.RULES_TEXT_Y = 1762
        self.RULES_TEXT_WIDTH = 1638
        self.RULES_TEXT_HEIGHT = 794
        self.RULES_TEXT_DIVIDER = None

        # Power & Toughness Text
        self.POWER_TOUGHNESS_X = 1493
        self.POWER_TOUGHNESS_Y = 2486
        self.POWER_TOUGHNESS_WIDTH = 372
        self.POWER_TOUGHNESS_HEIGHT = 174
        self.POWER_TOUGHNESS_FONT = MATRIX_BOLD_SMALL_CAPS
        self.POWER_TOUGHNESS_FONT_SIZE = 127

        # Set / Rarity Symbol
        self.SET_SYMBOL_X = 1714
        self.SET_SYMBOL_Y = 1601
        self.SET_SYMBOL_WIDTH = 111

        # Footer
        self.FOOTER_X = 146
        self.FOOTER_Y = 2580
        self.FOOTER_FONT = MATRIX_BOLD
        self.FOOTER_FONT_OUTLINE_SIZE = 0
        self.FOOTER_FONT_SIZE = 80
        self.FOOTER_LINE_HEIGHT_TO_GAP_RATIO = 1
        self.CREATION_DATE_FOOTER_FONT_SIZE = 50
        self.CREATION_DATE_FOOTER_FONT_COLOR = (0, 0, 0)
        self.BLACK_BRUSH_WIDTH = 157

    def _create_footer_layer(self):
        """
        Draw "<brush icon> <artist>", followed on the line below by the card's creation date.
        """

        artist = self.get_metadata(CARD_ARTIST)
        creation_date = self.get_metadata(CARD_CREATION_DATE)

        footer_font = load_font(self.FOOTER_FONT, self.FOOTER_FONT_SIZE)
        footer_fallback_fonts = self._load_fallback_fonts(self.FOOTER_FONT, self.FOOTER_FONT_SIZE)

        creation_date_font = load_font(self.LEGAL_FONT, self.CREATION_DATE_FOOTER_FONT_SIZE)
        creation_date_fallback_fonts = self._load_fallback_fonts(self.LEGAL_FONT, self.CREATION_DATE_FOOTER_FONT_SIZE)

        ascent, descent = footer_font.getmetrics()
        line_height = ascent + descent
        gap = line_height + line_height // self.FOOTER_LINE_HEIGHT_TO_GAP_RATIO

        image = Image.new("RGBA", (self.FOOTER_WIDTH, self.FOOTER_HEIGHT), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)

        brush_scale = self.BLACK_BRUSH_WIDTH / BLACK_BRUSH.image.height
        brush_width = self.BLACK_BRUSH_WIDTH
        brush_height = int(BLACK_BRUSH.image.height * brush_scale)
        brush_image = BLACK_BRUSH.get_formatted_image(brush_width, brush_height, self.FOOTER_FONT_OUTLINE_SIZE)

        if len(artist) > 0:
            image.alpha_composite(brush_image, (self.FOOTER_FONT_OUTLINE_SIZE, self.FOOTER_FONT_OUTLINE_SIZE - 52))
            self._draw_ucs_chunks(
                draw,
                (
                    self.FOOTER_FONT_OUTLINE_SIZE + brush_image.width + self.FOOTER_ARTIST_GAP_LENGTH,
                    self.FOOTER_FONT_OUTLINE_SIZE,
                ),
                artist,
                footer_font,
                footer_fallback_fonts,
                primary_font_path=self.FOOTER_FONT,
                font_size=self.FOOTER_FONT_SIZE,
                fill=(0, 0, 0),
                stroke_width=self.FOOTER_FONT_OUTLINE_SIZE,
                stroke_fill="black",
            )

        if len(creation_date) > 0:
            self._draw_ucs_chunks(
                draw,
                (self.FOOTER_FONT_OUTLINE_SIZE, self.FOOTER_FONT_OUTLINE_SIZE + gap),
                creation_date,
                creation_date_font,
                creation_date_fallback_fonts,
                primary_font_path=self.LEGAL_FONT,
                font_size=self.CREATION_DATE_FOOTER_FONT_SIZE,
                fill=self.CREATION_DATE_FOOTER_FONT_COLOR,
                stroke_width=self.FOOTER_FONT_OUTLINE_SIZE,
                stroke_fill="black",
            )

        self.text_layers.append(Layer(image, (self.FOOTER_X, self.FOOTER_Y)))
