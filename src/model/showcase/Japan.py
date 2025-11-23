from constants import CARD_FRAME_LAYOUT_EXTRAS, LIGHT_RULES_DIVIDING_LINE
from model.Layer import Layer
from model.regular.RegularCard import RegularCard


class Japan(RegularCard):
    """
    A layered image representing a card with a japanese showcase frame
    and all the collection info on it, with all relevant card metadata.

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
        metadata: dict[str, str | list[RegularCard]] = None,
        art_layer: Layer = None,
        frame_layers: list[Layer] = None,
        collector_layers: list[Layer] = None,
        text_layers: list[Layer] = None,
        overlay_layers: list[Layer] = None,
    ):
        super().__init__(metadata, art_layer, frame_layers, collector_layers, text_layers, overlay_layers)

        # Title Box
        self.TITLE_BOX_X = 82
        self.TITLE_BOX_WIDTH = 1300
        self.TITLE_BOX_HEIGHT = 131

        # Mana Cost
        self.MANA_COST_SYMBOL_SIZE = 70
        self.MANA_COST_SYMBOL_SPACING = -8
        self.MANA_COST_SYMBOL_SHADOW_OFFSET = (0, 0)
        self.MANA_COST_SYMBOL_OUTLINE_SIZE = 8

        # Title Text
        self.TITLE_X = 120
        self.TITLE_WIDTH = 1252
        self.TITLE_FONT_COLOR = (255, 255, 255)
        self.TITLE_TEXT_OUTLINE_RELATIVE_SIZE = 0.1

        # Type Box
        self.TYPE_BOX_Y = 1285
        self.TYPE_BOX_HEIGHT = 114

        # Type Text
        self.TYPE_X = 120 if "pip" not in self.get_metadata(CARD_FRAME_LAYOUT_EXTRAS, []) else 191
        self.TYPE_BOTTOM_Y = 1373
        self.TYPE_WIDTH = 1234 if "pip" not in self.get_metadata(CARD_FRAME_LAYOUT_EXTRAS, []) else 1163
        self.TYPE_FONT_COLOR = (255, 255, 255)
        self.TYPE_TEXT_OUTLINE_RELATIVE_SIZE = 0.1

        # Rules Text Box
        self.RULES_BOX_Y = 1420
        self.RULES_BOX_HEIGHT = 515

        # Rules Text
        self.RULES_TEXT_Y = 1420
        self.RULES_TEXT_HEIGHT = 515
        self.RULES_TEXT_FONT_COLOR = (255, 255, 255)
        self.RULES_TEXT_OUTLINE_RELATIVE_SIZE = 0.15

        # Power & Toughness Text
        self.POWER_TOUGHNESS_X = 1168
        self.POWER_TOUGHNESS_FONT_COLOR = (255, 255, 255)

        # Set / Rarity Symbol
        self.SET_SYMBOL_X = 1278
        self.SET_SYMBOL_Y = 1292
        self.SET_SYMBOL_WIDTH = 90

        # Other
        self.RULES_TEXT_DIVIDER = LIGHT_RULES_DIVIDING_LINE
