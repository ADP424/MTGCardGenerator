from model.Layer import Layer
from model.old.OriginalCard import OriginalCard


class FourthEdition(OriginalCard):
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
        metadata: dict[str, str | list["FourthEdition"]] = None,
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
        self.MANA_COST_SYMBOL_SPACING = 10
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

        # Type Box
        self.TYPE_BOX_Y = 1547

        # Type Text
        self.TYPE_X = 166
        self.TYPE_BOTTOM_Y = 1676

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

        # Power & Toughness Text
        self.POWER_TOUGHNESS_X = 1616
        self.POWER_TOUGHNESS_Y = 2520
        self.POWER_TOUGHNESS_FONT_SIZE = 122

        # Set / Rarity Symbol
        self.SET_SYMBOL_X = 1707
        self.SET_SYMBOL_Y = 1569
        self.SET_SYMBOL_WIDTH = 102

        # Footer
        self.FOOTER_X = 201
        self.FOOTER_Y = 2538
        self.FOOTER_FONT_SIZE = 76
        self.FOOTER_LINE_HEIGHT_TO_GAP_RATIO = 8
