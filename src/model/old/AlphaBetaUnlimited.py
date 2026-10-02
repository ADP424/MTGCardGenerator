from model.Layer import Layer
from model.old.OldCard import OldCard


class AlphaBetaUnlimited(OldCard):
    """
    A layered image representing an Alpha/Beta/Unlimited-bordered card and all the collection info on it,
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
        metadata: dict[str, str | list["AlphaBetaUnlimited"]] = None,
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
        self.MANA_COST_SYMBOL_SPACING = 16
        self.MANA_COST_SYMBOL_SHADOW_OFFSET = (0, 0)

        # Title Box
        self.TITLE_BOX_X = 104
        self.TITLE_BOX_Y = 118
        self.TITLE_BOX_WIDTH = 1761
        self.TITLE_BOX_HEIGHT = 164

        # Title Text
        self.TITLE_X = 141
        self.TITLE_BOTTOM_Y = 262
        self.TITLE_MAX_FONT_SIZE = 122
        self.TITLE_FONT_COLOR = (171, 171, 171)

        # Type Box
        self.TYPE_BOX_Y = 1552

        # Type Text
        self.TYPE_X = 201
        self.TYPE_BOTTOM_Y = 1666
        self.TYPE_MAX_FONT_SIZE = 94
        self.TYPE_FONT_COLOR = (171, 171, 171)

        # Rules Text Box
        self.RULES_BOX_X = 276
        self.RULES_BOX_Y = 1710
        self.RULES_BOX_WIDTH = 1463
        self.RULES_BOX_HEIGHT = 777

        # Rules Text
        self.RULES_TEXT_X = 276
        self.RULES_TEXT_Y = 1707
        self.RULES_TEXT_WIDTH = 1463
        self.RULES_TEXT_HEIGHT = 777

        # Power & Toughness Text
        self.POWER_TOUGHNESS_X = 1601
        self.POWER_TOUGHNESS_Y = 2493
        self.POWER_TOUGHNESS_FONT_SIZE = 117
        self.POWER_TOUGHNESS_FONT_COLOR = (171, 171, 171)

        # Set / Rarity Symbol
        self.SET_SYMBOL_X = 1692
        self.SET_SYMBOL_Y = 1570
        self.SET_SYMBOL_WIDTH = 100

        # Footer
        self.FOOTER_X = 201
        self.FOOTER_Y = 2532
        self.FOOTER_FONT_SIZE = 93
        self.FOOTER_FONT_COLOR = (171, 171, 171)
        self.FOOTER_LINE_HEIGHT_TO_GAP_RATIO = 16
        self.FOOTER_DROP_SHADOW_OFFSET = (6, 6)
