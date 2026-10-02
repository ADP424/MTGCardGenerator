from PIL import Image, ImageDraw

from constants import (
    CARD_ARTIST,
    CARD_CREATION_DATE,
    CARD_FRAME_LAYOUT_EXTRAS,
    GOUDY_MEDIEVAL,
    MPLANTIN,
    MPLANTIN_ITALICS,
    ORIGINAL_SYMBOL_PLACEHOLDER_KEY,
)
from model.Layer import Layer
from model.regular.RegularCard import RegularCard
from utils import add_drop_shadow, load_font


class OriginalCard(RegularCard):
    """
    A shared base class for the original card layouts (e.g. 4th Edition & Alpha/Beta/Unlimited).

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

        # Symbols
        self.MANA_SYMBOL_KEY = ORIGINAL_SYMBOL_PLACEHOLDER_KEY

        # Title Text
        self.TITLE_FONT = GOUDY_MEDIEVAL
        self.TITLE_FONT_COLOR = (255, 255, 255)
        self.TITLE_TEXT_DROP_SHADOW_RELATIVE_OFFSET = (0.04, 0.04)

        # Type Text
        self.TYPE_FONT = MPLANTIN
        self.TYPE_FONT_COLOR = (255, 255, 255)
        self.TYPE_TEXT_DROP_SHADOW_RELATIVE_OFFSET = (0.04, 0.04)

        # Rules Text
        self.RULES_TEXT_FONT = MPLANTIN
        self.RULES_TEXT_FONT_ITALICS = MPLANTIN_ITALICS
        self.RULES_TEXT_DIVIDER = None

        # Power & Toughness Text
        self.POWER_TOUGHNESS_FONT = MPLANTIN
        self.POWER_TOUGHNESS_FONT_COLOR = (255, 255, 255)
        self.POWER_TOUGHNESS_DROP_SHADOW_RELATIVE_OFFSET = (0.04, 0.04)

        # Footer
        self.FOOTER_FONT = MPLANTIN
        self.FOOTER_FONT_OUTLINE_SIZE = 0
        self.FOOTER_FONT_COLOR = (255, 255, 255)
        self.CREATION_DATE_FOOTER_FONT_SIZE = 45
        self.CREATION_DATE_FOOTER_FONT_COLOR = (
            (0, 0, 0)
            if "black" not in self.get_metadata(CARD_FRAME_LAYOUT_EXTRAS, [])
            and "dark" not in self.get_metadata(CARD_FRAME_LAYOUT_EXTRAS, [])
            else (255, 255, 255)
        )
        self.FOOTER_DROP_SHADOW_OFFSET = (4, 4)

    def _create_footer_layer(self):
        """
        Draw "Illus. <artist>", followed on the line below by the card's creation date.
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

        if len(artist) > 0:
            illus_text = f"Illus. {artist}"
            self._draw_ucs_chunks(
                draw,
                (self.FOOTER_FONT_OUTLINE_SIZE, self.FOOTER_FONT_OUTLINE_SIZE),
                illus_text,
                footer_font,
                footer_fallback_fonts,
                primary_font_path=self.FOOTER_FONT,
                font_size=self.FOOTER_FONT_SIZE,
                fill=self.FOOTER_FONT_COLOR,
                stroke_width=self.FOOTER_FONT_OUTLINE_SIZE,
                stroke_fill="black",
            )

        image = add_drop_shadow(image, self.FOOTER_DROP_SHADOW_OFFSET, (0, 0, 0))
        draw = ImageDraw.Draw(image)

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
