from constants import (
    CARD_SUBTYPES,
    CARD_SUPERTYPES,
    CARD_TITLE,
    CARD_TYPES,
    PIXEL,
    PIXEL_SYMBOL_PLACEHOLDER_KEY,
)
from model.Layer import Layer
from model.regular.RegularCard import RegularCard


class Pixel(RegularCard):
    """
    A layered image representing a card with a pixel-art showcase frame
    and all the collection info on it, with all relevant card metadata.

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

        # Overall Card
        self.CARD_WIDTH = 2010
        self.CARD_HEIGHT = 2814

        # Symbols
        self.MANA_SYMBOL_KEY = PIXEL_SYMBOL_PLACEHOLDER_KEY

        # Title Box
        self.TITLE_BOX_X = 123
        self.TITLE_BOX_Y = 140
        self.TITLE_BOX_WIDTH = 1762
        self.TITLE_BOX_HEIGHT = 184

        # Mana Cost
        self.MANA_COST_SYMBOL_SIZE = 98
        self.MANA_COST_SYMBOL_SPACING = 10
        self.MANA_COST_SYMBOL_SHADOW_OFFSET = (0, 0)
        self.MANA_COST_TEXT_FONT = PIXEL

        # Title Text
        self.TITLE_X = 155
        self.TITLE_BOTTOM_Y = 296
        self.TITLE_WIDTH = 1670
        self.TITLE_MAX_FONT_SIZE = 135
        self.TITLE_FONT = PIXEL
        self.TITLE_FONT_COLOR = (255, 255, 255)

        # Type Box
        self.TYPE_BOX_Y = 1587
        self.TYPE_BOX_HEIGHT = 166

        # Type Text
        self.TYPE_X = 155
        self.TYPE_BOTTOM_Y = 1725
        self.TYPE_WIDTH = 1600
        self.TYPE_MAX_FONT_SIZE = 112
        self.TYPE_FONT = PIXEL
        self.TYPE_FONT_COLOR = (255, 255, 255)

        # Rules Text Box
        self.RULES_BOX_X = 123
        self.RULES_BOX_Y = 1798
        self.RULES_BOX_WIDTH = 1762
        self.RULES_BOX_HEIGHT = 709

        # Rules Text
        self.RULES_TEXT_X = 135
        self.RULES_TEXT_Y = 1776
        self.RULES_TEXT_WIDTH = 1698
        self.RULES_TEXT_HEIGHT = 709
        self.RULES_TEXT_FONT = PIXEL
        self.RULES_TEXT_FONT_ITALICS = PIXEL
        self.RULES_TEXT_MAX_FONT_SIZE = 110
        self.RULES_TEXT_FONT_COLOR = (255, 255, 255)

        # Power & Toughness Text
        self.POWER_TOUGHNESS_X = 1600
        self.POWER_TOUGHNESS_Y = 2418
        self.POWER_TOUGHNESS_WIDTH = 360
        self.POWER_TOUGHNESS_HEIGHT = 180
        self.POWER_TOUGHNESS_FONT = PIXEL
        self.POWER_TOUGHNESS_FONT_SIZE = 128
        self.POWER_TOUGHNESS_FONT_COLOR = (255, 255, 255)

        # Set / Rarity Symbol
        self.SET_SYMBOL_WIDTH = 130
        self.SET_SYMBOL_X = 1722
        self.SET_SYMBOL_Y = 1598

        # Footer
        card_scale = self.CARD_HEIGHT / 2100
        self.FOOTER_X = round(96 * card_scale)
        self.FOOTER_Y = round(1968 * card_scale)
        self.FOOTER_WIDTH = round(1304 * card_scale)
        self.FOOTER_HEIGHT = round(152 * card_scale)
        self.FOOTER_FONT_SIZE = round(35 * card_scale)
        self.FOOTER_FONT_OUTLINE_SIZE = round(3 * card_scale)
        self.FOOTER_TAB_LENGTH = round(25 * card_scale)
        self.FOOTER_ARTIST_GAP_LENGTH = round(5 * card_scale)

        # Other
        self.HOLO_STAMP_X = float("inf")
        self.HOLO_STAMP_Y = float("inf")

    def _create_title_layer(self):
        """
        Uppercase the title, matching the all-caps look of the pixel showcase frame, then defer to
        `RegularCard`'s title rendering.
        """

        full_title = self.get_metadata(CARD_TITLE)
        self.set_metadata(CARD_TITLE, full_title.upper())
        super()._create_title_layer()
        self.set_metadata(CARD_TITLE, full_title)

    def _create_type_layer(self):
        """
        Uppercase the type line, matching the all-caps look of the pixel showcase frame, then defer
        to `RegularCard`'s type line rendering.
        """

        full_supertypes = self.get_metadata(CARD_SUPERTYPES)
        full_types = self.get_metadata(CARD_TYPES)
        full_subtypes = self.get_metadata(CARD_SUBTYPES)
        self.set_metadata(CARD_SUPERTYPES, full_supertypes.upper())
        self.set_metadata(CARD_TYPES, full_types.upper())
        self.set_metadata(CARD_SUBTYPES, full_subtypes.upper())
        super()._create_type_layer()
        self.set_metadata(CARD_SUPERTYPES, full_supertypes)
        self.set_metadata(CARD_TYPES, full_types)
        self.set_metadata(CARD_SUBTYPES, full_subtypes)
