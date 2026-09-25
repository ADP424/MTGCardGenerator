from model.Layer import Layer
from model.regular.RegularCard import RegularCard


class Crystal(RegularCard):
    """
    A layered image representing an Ikoria Crystal showcase card, with all relevant card metadata.

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

        # Title Text
        self.TITLE_FONT_COLOR = (255, 255, 255)

        # Title Box
        self.TITLE_BOX_WIDTH = 1751
        self.TITLE_BOX_HEIGHT = 143

        # Type Text
        self.TYPE_FONT_COLOR = (255, 255, 255)

        # Set Symbol
        self.SET_SYMBOL_WIDTH = 116

        # Rules Box
        self.RULES_BOX_X = 158
        self.RULES_BOX_Y = 1770
        self.RULES_BOX_WIDTH = 1673
        self.RULES_BOX_HEIGHT = 825

        # Rules Text
        self.RULES_TEXT_X = 172
        self.RULES_TEXT_Y = 1770
        self.RULES_TEXT_WIDTH = 1658
        self.RULES_TEXT_HEIGHT = 825
        self.RULES_TEXT_FONT_COLOR = (255, 255, 255)

        # Power & Toughness Box
        self.POWER_TOUGHNESS_X = 1551
        self.POWER_TOUGHNESS_Y = 2488
        self.POWER_TOUGHNESS_WIDTH = 396
        self.POWER_TOUGHNESS_HEIGHT = 230
        self.POWER_TOUGHNESS_FONT_COLOR = (255, 255, 255)
