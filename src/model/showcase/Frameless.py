from constants import LIGHT_RULES_DIVIDING_LINE
from model.Layer import Layer
from model.regular.RegularCard import RegularCard


class Frameless(RegularCard):
    """
    A layered image representing a card with a frameless "source material" showcase frame and all the
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
        self.TITLE_BOX_Y = 134
        self.TITLE_BOX_WIDTH = 1781

        # Mana Cost
        self.MANA_COST_SYMBOL_SHADOW_OFFSET = (0, 0)
        self.MANA_COST_SYMBOL_OUTLINE_SIZE = 14

        # Title Text
        self.TITLE_X = 151
        self.TITLE_BOTTOM_Y = 255
        self.TITLE_FONT_COLOR = (255, 255, 255)
        self.TITLE_TEXT_OUTLINE_RELATIVE_SIZE = 0.125

        # Type Text
        self.TYPE_X = 161
        self.TYPE_BOTTOM_Y = 1691
        self.TYPE_FONT_COLOR = (255, 255, 255)
        self.TYPE_TEXT_OUTLINE_RELATIVE_SIZE = 0.125

        # Rules Text
        self.RULES_TEXT_X = 149
        self.RULES_TEXT_Y = 1750
        self.RULES_TEXT_WIDTH = 1712
        self.RULES_TEXT_FONT_COLOR = (255, 255, 255)
        self.RULES_TEXT_OUTLINE_RELATIVE_SIZE = 0.125
        self.RULES_TEXT_VERTICAL_ALIGNMENT = "top"

        # Power & Toughness Text
        self.POWER_TOUGHNESS_X = 1644
        self.POWER_TOUGHNESS_Y = 2468
        self.POWER_TOUGHNESS_WIDTH = 154
        self.POWER_TOUGHNESS_HEIGHT = 114
        self.POWER_TOUGHNESS_FONT_SIZE = 113
        self.POWER_TOUGHNESS_FONT_COLOR = (255, 255, 255)
        self.POWER_TOUGHNESS_OUTLINE_SIZE = 11

        # Other
        self.RULES_TEXT_DIVIDER = LIGHT_RULES_DIVIDING_LINE

    def create_layers(
        self,
        create_art_layer: bool = True,
        create_frame_layers: bool = True,
        create_watermark_layer: bool = True,
        create_rarity_symbol_layer: bool = True,
        create_footer_layer: bool = True,
        create_mana_cost_layer: bool = True,
        create_title_layer: bool = True,
        create_type_layer: bool = True,
        create_rules_text_layer: bool = True,
        create_power_toughness_layer: bool = True,
        create_overlay_layers: bool = True,
    ):
        """
        Append every frame, text, and collector layer to the card based on `self.metadata`.

        Parameters
        ----------
        create_art_layer: bool, default: True
            Whether to put the card's art in or not.

        create_frame_layers: bool, default: True
            Whether to put the card's frames on or not.

        create_watermark_layer: bool, default: True
            Whether to put the watermark on the card or not. Ignored; a frameless card never has a watermark.

        create_rarity_symbol_layer: bool, default: True
            Whether to put the rarity/set symbol on the card or not. Ignored; a frameless card never has one.

        create_footer_layer: bool, default: True
            Whether to put the footer collector info on the bottom of the card or not.

        create_mana_cost_layer: bool, default: True
            Whether to put the mana cost of the card on it or not.

        create_title_layer: bool, default: True
            Whether to put the title of the card on it or not.

        create_type_layer: bool, default: True
            Whether to put the type line of the card on it or not.

        create_rules_text_layer: bool, default: True
            Whether to put the rules text of the card on it or not.

        create_power_toughness_layer: bool, default: True
            Whether to put the power & toughness of the card on it or not.

        create_overlay_layers: bool, default: True
            Whether to put the overlays on top of the card after everything else or not.
        """

        super().create_layers(
            create_art_layer,
            create_frame_layers,
            False,  # a frameless card never has a watermark
            False,  # a frameless card never has a rarity/set symbol
            create_footer_layer,
            create_mana_cost_layer,
            create_title_layer,
            create_type_layer,
            create_rules_text_layer,
            create_power_toughness_layer,
            create_overlay_layers,
        )
