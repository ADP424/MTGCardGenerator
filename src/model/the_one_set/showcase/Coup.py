from constants import ETHNOCENTRIC_ITALICS, MAXIMILIEN_REGULAR
from model.Layer import Layer
from model.regular.RegularCard import RegularCard


class Coup(RegularCard):
    """
    A layered image representing a coup showcase card and all the collection info on it,
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

        # Title Box
        self.TITLE_BOX_X = 47
        self.TITLE_BOX_Y = 1927
        self.TITLE_BOX_WIDTH = 804
        self.TITLE_BOX_HEIGHT = 218

        # Mana Cost
        self.MANA_COST_SYMBOL_SIZE = 161
        self.MANA_COST_SYMBOL_SHADOW_OFFSET = (0, 0)
        self.MANA_COST_SYMBOL_OUTLINE_SIZE = 16
        self.MANA_COST_TEXT_FONT = MAXIMILIEN_REGULAR

        # Coup Mana Cost Location
        self.MANA_COST_BOX_X = 80
        self.MANA_COST_BOX_Y = 96
        self.MANA_COST_BOX_WIDTH = 1849
        self.MANA_COST_BOX_HEIGHT = 268

        # Title Text
        self.TITLE_X = 72
        self.TITLE_BOTTOM_Y = 2144
        self.TITLE_WIDTH = 804
        self.TITLE_MAX_FONT_SIZE = 268
        self.TITLE_FONT = MAXIMILIEN_REGULAR
        self.TITLE_FONT_COLOR = (255, 255, 255)
        self.TITLE_TEXT_DROP_SHADOW_RELATIVE_OFFSET = (0.075, 0.075)

        # Type Box
        self.TYPE_BOX_Y = 2144
        self.TYPE_BOX_HEIGHT = 114

        # Type Text
        self.TYPE_X = 72
        self.TYPE_BOTTOM_Y = 2265
        self.TYPE_WIDTH = 706
        self.TYPE_MAX_FONT_SIZE = 134
        self.TYPE_FONT = MAXIMILIEN_REGULAR
        self.TYPE_FONT_COLOR = (255, 255, 255)
        self.TYPE_TEXT_DROP_SHADOW_RELATIVE_OFFSET = (0.075, 0.075)

        # Rules Text Box
        self.RULES_BOX_X = 804
        self.RULES_BOX_Y = 2266
        self.RULES_BOX_WIDTH = 1206
        self.RULES_BOX_HEIGHT = 326

        # Rules Text
        self.RULES_TEXT_X = 804
        self.RULES_TEXT_Y = 2278
        self.RULES_TEXT_WIDTH = 1139
        self.RULES_TEXT_HEIGHT = 302
        self.RULES_TEXT_FONT = MAXIMILIEN_REGULAR
        self.RULES_TEXT_FONT_ITALICS = ETHNOCENTRIC_ITALICS
        self.RULES_TEXT_MAX_FONT_SIZE = 134
        self.RULES_TEXT_FONT_COLOR = (255, 255, 255)
        self.RULES_TEXT_DROP_SHADOW_RELATIVE_OFFSET = (0.075, 0.075)

        # Power & Toughness Text
        self.POWER_TOUGHNESS_X = 1545
        self.POWER_TOUGHNESS_Y = 2581
        self.POWER_TOUGHNESS_WIDTH = 402
        self.POWER_TOUGHNESS_HEIGHT = 134
        self.POWER_TOUGHNESS_FONT = MAXIMILIEN_REGULAR
        self.POWER_TOUGHNESS_FONT_SIZE = 177
        self.POWER_TOUGHNESS_FONT_COLOR = (255, 255, 255)
        self.POWER_TOUGHNESS_DROP_SHADOW_RELATIVE_OFFSET = (0.075, 0.075)

        # Set / Rarity Symbol
        self.SET_SYMBOL_X = 683
        self.SET_SYMBOL_Y = 2157
        self.SET_SYMBOL_WIDTH = 94

        # Footer
        self.FOOTER_Y = 2667
        self.FOOTER_WIDTH = 1747
        self.FOOTER_HEIGHT = 204
        self.FOOTER_FONT_SIZE = 47
        self.FOOTER_FONT_OUTLINE_SIZE = 4
        self.FOOTER_LINE_HEIGHT_TO_GAP_RATIO = 2
        self.FOOTER_TAB_LENGTH = 34
        self.FOOTER_ARTIST_GAP_LENGTH = 7

    def _create_mana_cost_layer(self):
        """
        Process MTG mana cost into the mana cost header Monopoly-style, exchanging mana placeholders
        for symbols, and append it to `self.text_layers`.
        """

        title_box_x = self.TITLE_BOX_X
        title_box_y = self.TITLE_BOX_Y
        title_box_width = self.TITLE_BOX_WIDTH
        title_box_height = self.TITLE_BOX_HEIGHT

        self.TITLE_BOX_X = self.MANA_COST_BOX_X
        self.TITLE_BOX_Y = self.MANA_COST_BOX_Y
        self.TITLE_BOX_WIDTH = self.MANA_COST_BOX_WIDTH
        self.TITLE_BOX_HEIGHT = self.MANA_COST_BOX_HEIGHT
        super()._create_mana_cost_layer()

        self.TITLE_BOX_X = title_box_x
        self.TITLE_BOX_Y = title_box_y
        self.TITLE_BOX_WIDTH = title_box_width
        self.TITLE_BOX_HEIGHT = title_box_height

    def _create_title_layer(self):
        """
        Process title text into the title and append it to `self.text_layers`.
        Negate the `self.mana_cost_x` handling, since the mana cost doesn't share a line
        with the title on these Monopoly frames.
        """

        self.mana_cost_x = float("inf")
        super()._create_title_layer()
