from PIL import Image, ImageDraw

from constants import (
    CARD_ADD_TOTAL_TO_FOOTER,
    CARD_ARTIST,
    CARD_CREATION_DATE,
    CARD_FOOTER_LARGEST_INDEX,
    CARD_FRAME_LAYOUT_EXTRAS,
    CARD_INDEX,
    GOUDY_MEDIEVAL,
    MPLANTIN,
    MPLANTIN_ITALICS,
)
from model.Layer import Layer
from model.regular.RegularCard import RegularCard
from utils import add_drop_shadow, load_font


class FourthEdition(RegularCard):
    """
    A layered image representing a 4th Edition-bordered card and all the collection info on it,
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
        self.MANA_COST_SYMBOL_SIZE = 98
        self.MANA_COST_SYMBOL_SHADOW_OFFSET = (0, 0)

        # Title Box
        self.TITLE_BOX_X = 86
        self.TITLE_BOX_Y = 61
        self.TITLE_BOX_WIDTH = 1781
        self.TITLE_BOX_HEIGHT = 158

        # Title Text
        self.TITLE_X = 165
        self.TITLE_BOTTOM_Y = 206
        self.TITLE_MAX_FONT_SIZE = 116
        self.TITLE_FONT = GOUDY_MEDIEVAL
        self.TITLE_FONT_COLOR = (255, 255, 255)
        self.TITLE_TEXT_DROP_SHADOW_RELATIVE_OFFSET = (0.04, 0.04)
        self.TITLE_TEXT_DROP_SHADOW_COLOR = (0, 0, 0)

        # Type Box
        self.TYPE_BOX_Y = 1547

        # Type Text
        self.TYPE_X = 166
        self.TYPE_BOTTOM_Y = 1676
        self.TYPE_FONT = MPLANTIN
        self.TYPE_FONT_COLOR = (255, 255, 255)
        self.TYPE_TEXT_DROP_SHADOW_RELATIVE_OFFSET = (0.04, 0.04)
        self.TYPE_TEXT_DROP_SHADOW_COLOR = (0, 0, 0)

        # Rules Text Box
        self.RULES_BOX_X = 221
        self.RULES_BOX_Y = 1694
        self.RULES_BOX_WIDTH = 1564
        self.RULES_BOX_HEIGHT = 829

        # Rules Text
        self.RULES_TEXT_X = 276
        self.RULES_TEXT_Y = 1694
        self.RULES_TEXT_WIDTH = 1509
        self.RULES_TEXT_HEIGHT = 829
        self.RULES_TEXT_FONT = MPLANTIN
        self.RULES_TEXT_FONT_ITALICS = MPLANTIN_ITALICS
        self.RULES_TEXT_FONT_COLOR = (0, 0, 0)
        self.RULES_TEXT_DIVIDER = None

        # Power & Toughness Text
        self.POWER_TOUGHNESS_X = 1616
        self.POWER_TOUGHNESS_Y = 2520
        self.POWER_TOUGHNESS_FONT = MPLANTIN
        self.POWER_TOUGHNESS_FONT_SIZE = 122
        self.POWER_TOUGHNESS_FONT_COLOR = (255, 255, 255)
        self.POWER_TOUGHNESS_DROP_SHADOW_RELATIVE_OFFSET = (0.04, 0.04)
        self.POWER_TOUGHNESS_DROP_SHADOW_COLOR = (0, 0, 0)

        # Set / Rarity Symbol
        self.SET_SYMBOL_X = 1707
        self.SET_SYMBOL_Y = 1569
        self.SET_SYMBOL_WIDTH = 102

        # Footer
        self.FOOTER_X = 201
        self.FOOTER_Y = 2538
        self.FOOTER_FONT = MPLANTIN
        self.LEGAL_FONT = MPLANTIN
        self.FOOTER_FONT_OUTLINE_SIZE = 0
        self.FOOTER_FONT_SIZE = 76
        self.FOOTER_LINE_HEIGHT_TO_GAP_RATIO = 8
        self.CREATION_DATE_FOOTER_FONT_SIZE = 45
        self.CREATION_DATE_FOOTER_FONT_COLOR = (
            (0, 0, 0)
            if "black" not in self.get_metadata(CARD_FRAME_LAYOUT_EXTRAS, [])
            and "dark" not in self.get_metadata(CARD_FRAME_LAYOUT_EXTRAS, [])
            else (255, 255, 255)
        )

    def _create_footer_layer(self):
        """
        Draw "<index> Illus. <artist>", followed on the line below by the card's creation date.
        """

        artist = self.get_metadata(CARD_ARTIST)
        index = self.get_metadata(CARD_INDEX).zfill(len(str(self.get_metadata(CARD_FOOTER_LARGEST_INDEX))))
        creation_date = self.get_metadata(CARD_CREATION_DATE)

        footer_font = load_font(self.FOOTER_FONT, self.FOOTER_FONT_SIZE)
        footer_fallback_fonts = self._load_fallback_fonts(self.FOOTER_FONT, self.FOOTER_FONT_SIZE)

        creation_date_font = load_font(self.FOOTER_FONT, self.CREATION_DATE_FOOTER_FONT_SIZE)
        creation_date_fallback_fonts = self._load_fallback_fonts(self.FOOTER_FONT, self.CREATION_DATE_FOOTER_FONT_SIZE)

        ascent, descent = footer_font.getmetrics()
        line_height = ascent + descent
        gap = line_height + line_height // self.FOOTER_LINE_HEIGHT_TO_GAP_RATIO

        image = Image.new("RGBA", (self.FOOTER_WIDTH, self.FOOTER_HEIGHT), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)

        try:
            add_total_to_footer = int(self.get_metadata(CARD_ADD_TOTAL_TO_FOOTER)) > 0
        except ValueError:
            add_total_to_footer = False
        collector_number_text = (
            f"{index}{f"/{self.get_metadata(CARD_FOOTER_LARGEST_INDEX)}" if add_total_to_footer else ""}"
        )
        self._draw_ucs_chunks(
            draw,
            (self.FOOTER_FONT_OUTLINE_SIZE, self.FOOTER_FONT_OUTLINE_SIZE),
            collector_number_text,
            footer_font,
            footer_fallback_fonts,
            primary_font_path=self.FOOTER_FONT,
            font_size=self.FOOTER_FONT_SIZE,
            fill=(255, 255, 255),
            stroke_width=self.FOOTER_FONT_OUTLINE_SIZE,
            stroke_fill="black",
        )
        collector_number_text_width = self._get_ucs_chunks_length(
            collector_number_text, footer_font, footer_fallback_fonts
        )

        if len(artist) > 0:
            illus_text = f"Illus. {artist}"
            self._draw_ucs_chunks(
                draw,
                (
                    self.FOOTER_FONT_OUTLINE_SIZE + collector_number_text_width + self.FOOTER_TAB_LENGTH,
                    self.FOOTER_FONT_OUTLINE_SIZE,
                ),
                illus_text,
                footer_font,
                footer_fallback_fonts,
                primary_font_path=self.FOOTER_FONT,
                font_size=self.FOOTER_FONT_SIZE,
                fill=(255, 255, 255),
                stroke_width=self.FOOTER_FONT_OUTLINE_SIZE,
                stroke_fill="black",
            )

        image = add_drop_shadow(image, (4, 4), (0, 0, 0))
        draw = ImageDraw.Draw(image)

        if len(creation_date) > 0:
            self._draw_ucs_chunks(
                draw,
                (self.FOOTER_FONT_OUTLINE_SIZE, self.FOOTER_FONT_OUTLINE_SIZE + gap),
                creation_date,
                creation_date_font,
                creation_date_fallback_fonts,
                primary_font_path=self.FOOTER_FONT,
                font_size=self.CREATION_DATE_FOOTER_FONT_SIZE,
                fill=self.CREATION_DATE_FOOTER_FONT_COLOR,
                stroke_width=self.FOOTER_FONT_OUTLINE_SIZE,
                stroke_fill="black",
            )

        self.text_layers.append(Layer(image, (self.FOOTER_X, self.FOOTER_Y)))
