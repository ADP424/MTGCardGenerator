from model.adventure.RegularAdventure import RegularAdventure
from model.Layer import Layer
from model.regular.RegularCard import RegularCard


class RegularPrepare(RegularAdventure):
    """
    A layered image representing an omen card and all the collection info on it,
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

        # Prepare Spell Title Box
        self.ADVENTURE_TITLE_BOX_X = 761
        self.ADVENTURE_TITLE_BOX_Y = 1324
        self.ADVENTURE_TITLE_BOX_WIDTH = 640
        self.ADVENTURE_TITLE_BOX_HEIGHT = 88

        # Prepare Spell Mana Cost
        self.ADVENTURE_MANA_COST_SYMBOL_SIZE = 60
        self.ADVENTURE_MANA_COST_SYMBOL_SPACING = 5

        # Prepare Spell Title Text
        self.ADVENTURE_TITLE_X = 777
        self.ADVENTURE_TITLE_BOTTOM_Y = 1395
        self.ADVENTURE_TITLE_WIDTH = 630
        self.ADVENTURE_TITLE_MAX_FONT_SIZE = 62
        self.ADVENTURE_TITLE_FONT_COLOR = (255, 255, 255)

        # Prepare Spell Type Box
        self.ADVENTURE_TYPE_BOX_Y = 1435
        self.ADVENTURE_TYPE_BOX_HEIGHT = 71

        # Prepare Spell Type Text
        self.ADVENTURE_TYPE_X = 777
        self.ADVENTURE_TYPE_BOTTOM_Y = 1486
        self.ADVENTURE_TYPE_WIDTH = 630
        self.ADVENTURE_TYPE_MAX_FONT_SIZE = 62
        self.ADVENTURE_TYPE_FONT_COLOR = (255, 255, 255)

        # Right Rules Text Box
        self.RULES_BOX_X = 112
        self.RULES_BOX_Y = 1323
        self.RULES_BOX_WIDTH = 630
        self.RULES_BOX_HEIGHT = 623

        # Prepare Spell Rules Text Box
        self.ADVENTURE_RULES_BOX_X = 760
        self.ADVENTURE_RULES_BOX_Y = 1528
        self.ADVENTURE_RULES_BOX_WIDTH = 630
        self.ADVENTURE_RULES_BOX_HEIGHT = 338

        # Rules Text
        self.RULES_TEXT_MAX_FONT_SIZE = 74

        # Right Rules Text
        self.RULES_TEXT_X = 112
        self.RULES_TEXT_Y = 1315
        self.RULES_TEXT_WIDTH = 632
        self.RULES_TEXT_HEIGHT = 623

        # Prepare Spell Rules Text
        self.ADVENTURE_RULES_TEXT_X = 754
        self.ADVENTURE_RULES_TEXT_Y = 1528
        self.ADVENTURE_RULES_TEXT_WIDTH = 636
        self.ADVENTURE_RULES_TEXT_HEIGHT = 338
