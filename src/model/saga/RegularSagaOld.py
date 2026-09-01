from constants import CARD_FRAME_LAYOUT_EXTRAS
from model.Layer import Layer
from model.saga.RegularSaga import RegularSaga


class RegularSagaOld(RegularSaga):
    """
    A layered image representing a regular enchantment saga (legacy 1500x2100 scale) and all the
    collection info on it, with all relevant card metadata.

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
        metadata: dict[str, str | list["RegularSagaOld"]] = None,
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
        self.CARD_WIDTH = 1500
        self.CARD_HEIGHT = 2100

        # Title Box
        self.TITLE_BOX_X = 90
        self.TITLE_BOX_Y = 105
        self.TITLE_BOX_WIDTH = 1313
        self.TITLE_BOX_HEIGHT = 114

        # Mana Cost
        self.MANA_COST_SYMBOL_SIZE = 70
        self.MANA_COST_SYMBOL_SPACING = 6
        self.MANA_COST_SYMBOL_SHADOW_OFFSET = (-1, 6)

        # Title Text
        self.TITLE_X = 128
        self.TITLE_BOTTOM_Y = 200
        self.TITLE_WIDTH = 1244
        self.TITLE_MAX_FONT_SIZE = 79
        self.TITLE_MIN_FONT_SIZE = 6

        # Type Box
        self.TYPE_BOX_Y = 1779
        self.TYPE_BOX_HEIGHT = 114

        # Type Text
        self.TYPE_X = 128 if "pip" not in self.get_metadata(CARD_FRAME_LAYOUT_EXTRAS, []) else 199
        self.TYPE_Y = 1782
        self.TYPE_BOTTOM_Y = 1872
        self.TYPE_WIDTH = 1244 if "pip" not in self.get_metadata(CARD_FRAME_LAYOUT_EXTRAS, []) else 1173
        self.TYPE_MAX_FONT_SIZE = 67
        self.TYPE_MIN_FONT_SIZE = 6

        # Rules Text Box
        self.RULES_BOX_X = 116
        self.RULES_BOX_Y = 238
        self.RULES_BOX_WIDTH = 633
        self.RULES_BOX_HEIGHT = 1522

        # Saga Ability Text
        self.CHAPTER_TEXT_INDENT = 62

        # Rules Text
        self.RULES_TEXT_X = 116
        self.RULES_TEXT_Y = 238
        self.RULES_TEXT_WIDTH = 633
        self.RULES_TEXT_HEIGHT = 1522
        self.RULES_TEXT_MAX_FONT_SIZE = 78
        self.RULES_TEXT_MIN_FONT_SIZE = 6
        self.RULES_TEXT_MANA_SYMBOL_SCALE = 0.78
        self.RULES_TEXT_MANA_SYMBOL_SPACING = 5
        self.RULES_TEXT_LIMIT_HORIZONTAL_BUFFER = 5
        self.RULES_TEXT_LIMIT_VERTICAL_BUFFER = 8

        # Chapter Number Frame
        self.CHAPTER_NUMBER_X = 58
        self.CHAPTER_NUMBER_WIDTH = 118
        self.CHAPTER_NUMBER_HEIGHT = 132

        # Chapter Text
        self.STATIC_TEXT_HEIGHT = 339
        self.STATIC_CHAPTER_TEXT_GAP = 33
        self.CHAPTER_TEXT_START_Y = 620
        self.CHAPTER_NUMBER_FONT_SIZE = 70

        # Power & Toughness Text
        self.POWER_TOUGHNESS_X = 1166
        self.POWER_TOUGHNESS_Y = 1866
        self.POWER_TOUGHNESS_WIDTH = 252
        self.POWER_TOUGHNESS_HEIGHT = 124
        self.POWER_TOUGHNESS_FONT_SIZE = 80

        # Banner
        self.BANNER_STRIPE_X = 110
        self.BANNER_STRIPE_Y = 644
        self.BANNER_STRIPE_WIDTH = 12
        self.BANNER_STRIPE_HEIGHT = 1000

        # Set / Rarity Symbol
        self.SET_SYMBOL_X = 1305
        self.SET_SYMBOL_Y = 1795
        self.SET_SYMBOL_WIDTH = 80

        # Footer
        self.FOOTER_X = 96
        self.FOOTER_Y = 1968
        self.FOOTER_WIDTH = 1304
        self.FOOTER_HEIGHT = 152
        self.FOOTER_FONT_SIZE = 35
        self.FOOTER_FONT_OUTLINE_SIZE = 3
        self.FOOTER_TAB_LENGTH = 25
        self.FOOTER_ARTIST_GAP_LENGTH = 5

        # Other
        self.HOLO_STAMP_X = float("inf")
        self.HOLO_STAMP_Y = float("inf")

        self._determine_ability_heights_and_y_values()
