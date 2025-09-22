from model.RegularCard import RegularCard
from model.Layer import Layer


class Battle(RegularCard):
    """
    A layered image representing a battle card and all the collection info on it,
    with all relevant card metadata.

    Attributes
    ----------
    metadata : dict[str, str | list], default : {}
        Information about the card (title, mana cost, rules text, frame, etc.)

    base_width : int, default : None
        The width of the root image. Determined by the frame layout in the metadata if not given.

    base_height : int, default : None
        The height of the root image. Determined by the frame layout in the metadata if not given.

    art_layer : Layer, optional
        The art to use in the art slot of the frame. Renders first, before the frame layers.

    frame_layers : list[Layer], default : []
        The layers of card frames. Lower-index layers are rendered first. Renders after art, before collector info.

    collector_layers : list[Layer], default : []
        The layers of collector info. Lower-index layers are rendered first. Renders after frames, before text.

    text_layers : list[Layer], default : []
        The layers of card text. Lower-index layers are rendered first. Renders after collector info and frames.

    overlay_layers : list[Layer], default : []
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
        footer_largest_index: int = 999,
    ):
        super().__init__(
            metadata, art_layer, frame_layers, collector_layers, text_layers, overlay_layers, footer_largest_index
        )

        # Overall Card
        self.CARD_WIDTH = 2814
        self.CARD_HEIGHT = 2010

        # Title Box
        self.TITLE_BOX_X = 298
        self.TITLE_BOX_Y = 101
        self.TITLE_BOX_WIDTH = 2335
        self.TITLE_BOX_HEIGHT = 145

        # Mana Cost
        self.MANA_COST_SYMBOL_SIZE = 94
        self.MANA_COST_SYMBOL_SPACING = 8
        self.MANA_COST_SYMBOL_SHADOW_OFFSET = (-1, 8)

        # Title Text
        self.TITLE_X = 344
        self.TITLE_Y = 114
        self.TITLE_WIDTH = 2246
        self.TITLE_MAX_FONT_SIZE = 106
        self.TITLE_MIN_FONT_SIZE = 8

        # Type Box
        self.TYPE_BOX_HEIGHT = 153

        # Type Text
        self.TYPE_X = 344
        self.TYPE_Y = 1170
        self.TYPE_WIDTH = 2248
        self.TYPE_MAX_FONT_SIZE = 90
        self.TYPE_MIN_FONT_SIZE = 8

        # Rules Text Box
        self.RULES_BOX_X = 324
        self.RULES_BOX_Y = 1339
        self.RULES_BOX_WIDTH = 2291
        self.RULES_BOX_HEIGHT = 579
        self.RULES_BOX_MAX_FONT_SIZE = 104
        self.RULES_BOX_MIN_FONT_SIZE = 8

        # Rules Text
        self.RULES_TEXT_X = 324
        self.RULES_TEXT_Y = 1339
        self.RULES_TEXT_WIDTH = 2291
        self.RULES_TEXT_HEIGHT = 579
        self.RULES_TEXT_MANA_SYMBOL_SPACING = 7

        # Power & Toughness Text
        self.POWER_TOUGHNESS_X = 2520
        self.POWER_TOUGHNESS_Y = 1732
        self.POWER_TOUGHNESS_WIDTH = 222
        self.POWER_TOUGHNESS_HEIGHT = 223
        self.POWER_TOUGHNESS_FONT_SIZE = 107
        self.POWER_TOUGHNESS_FONT_COLOR = (255, 255, 255)

        # Watermark
        self.WATERMARK_HEIGHT = 446

        # Set / Rarity Symbol
        self.SET_SYMBOL_X = 2490
        self.SET_SYMBOL_Y = 1182
        self.SET_SYMBOL_WIDTH = 115

        # Footer
        # All RELATIVE values assume 0 degree rotation, the way the text would be read
        # This means width, height, tab length, etc. but NOT x or y coordinates
        self.FOOTER_ROTATION = 270
        self.FOOTER_X = 0
        self.FOOTER_Y = 129
        self.FOOTER_WIDTH = 1760
        self.FOOTER_HEIGHT = 181
        self.FOOTER_FONT_SIZE = 47
        self.FOOTER_FONT_OUTLINE_SIZE = 4
        self.FOOTER_TAB_LENGTH = 33
        self.FOOTER_ARTIST_GAP_LENGTH = 7
