from constants import (
    CARD_FRAME_LAYOUT_EXTRAS,
    COPPERPLATE_GOTHIC_BOLD,
    NEUE_KABEL,
    NEUE_KABEL_BOLD_ITALICS,
    NEUE_KABEL_ITALICS,
)
from model.Layer import Layer
from model.regular.RegularCard import RegularCard


class Monopoly(RegularCard):
    """
    A layered image representing a card and all the collection info on it, with all relevant card metadata.

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
        self.TITLE_BOX_X = 167
        self.TITLE_BOX_Y = 146
        self.TITLE_BOX_WIDTH = 1170
        self.TITLE_BOX_HEIGHT = 490

        # Mana Cost
        self.MANA_COST_SYMBOL_SIZE = 80
        self.MANA_COST_SYMBOL_SPACING = 6
        self.MANA_COST_ALIGN = "center"
        self.MANA_COST_SYMBOL_SHADOW_OFFSET = (0, 0)
        self.MANA_COST_SYMBOL_OUTLINE_SIZE = 8
        self.MANA_COST_TEXT_FONT = NEUE_KABEL

        # Monopoly Mana Cost Location
        self.MANA_COST_BOX_X = 111
        self.MANA_COST_BOX_Y = 660
        self.MANA_COST_BOX_WIDTH = 1280
        self.MANA_COST_BOX_HEIGHT = 190

        # Title Text
        self.TITLE_X = 200
        self.TITLE_BOTTOM_Y = 600
        self.TITLE_WIDTH = 1104
        self.TITLE_MAX_FONT_SIZE = 158
        self.TITLE_FONT = COPPERPLATE_GOTHIC_BOLD
        self.TITLE_FONT_COLOR = (
            (0, 0, 0)
            if "black" not in self.get_metadata(CARD_FRAME_LAYOUT_EXTRAS, [])
            and "dark" not in self.get_metadata(CARD_FRAME_LAYOUT_EXTRAS, [])
            else (255, 255, 255)
        )
        self.TITLE_TEXT_ALIGN = "center"

        # Type Box
        self.TYPE_BOX_Y = 146
        self.TYPE_BOX_HEIGHT = 490

        # Type Text
        self.TYPE_X = 200
        self.TYPE_BOTTOM_Y = 310
        self.TYPE_WIDTH = 1104
        self.TYPE_MAX_FONT_SIZE = 70
        self.TYPE_FONT = NEUE_KABEL
        self.TYPE_FONT_COLOR = (
            (0, 0, 0)
            if "black" not in self.get_metadata(CARD_FRAME_LAYOUT_EXTRAS, [])
            and "dark" not in self.get_metadata(CARD_FRAME_LAYOUT_EXTRAS, [])
            else (255, 255, 255)
        )
        self.TYPE_TEXT_ALIGN = "center"

        # Rules Text Box
        self.RULES_BOX_X = 111
        self.RULES_BOX_Y = 841
        self.RULES_BOX_WIDTH = 1280
        self.RULES_BOX_HEIGHT = 1083

        # Rules Text
        self.RULES_TEXT_X = 131
        self.RULES_TEXT_Y = 841
        self.RULES_TEXT_WIDTH = 1240
        self.RULES_TEXT_HEIGHT = 1083
        self.RULES_TEXT_FONT = NEUE_KABEL
        self.RULES_TEXT_FONT_ITALICS = NEUE_KABEL_ITALICS
        self.RULES_TEXT_FONT_BOLD_ITALICS = NEUE_KABEL_BOLD_ITALICS
        self.RULES_TEXT_MAX_FONT_SIZE = 150
        self.RULES_TEXT_MIN_FONT_SIZE = 6

        # Set / Rarity Symbol
        self.SET_SYMBOL_X = 700
        self.SET_SYMBOL_Y = 500
        self.SET_SYMBOL_WIDTH = 100

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
        create_art_layer: bool, default : True
            Whether to put the card's art in or not.

        create_frame_layers: bool, default : True
            Whether to put the card's frames on or not.

        create_watermark_layer: bool, default : True
            Whether to put the watermark on the card or not.

        create_rarity_symbol_layer: bool, default : True
            Whether to put the rarity/set symbol on the card or not.

        create_footer_layer: bool, default : True
            Whether to put the footer collector info on the bottom of the card or not.

        create_mana_cost_layer: bool, default : True
            Whether to put the mana cost of the card on it or not.

        create_title_layer: bool, default : True
            Whether to put the title of the card on it or not.

        create_type_layer: bool, default : True
            Whether to put the type line of the card on it or not.

        create_rules_text_layer: bool, default : True
            Whether to put the rules text of the card on it or not.

        create_power_toughness_layer: bool, default : True
            Whether to put the power & toughness of the card on it or not.

        create_overlay_layers: bool, default : True
            Whether to put the overlays on top of the card after everything else or not.
        """

        super().create_layers(
            False,  # don't try to create an art layer for a Monopoly frame
            create_frame_layers,
            create_watermark_layer,
            create_rarity_symbol_layer,
            create_footer_layer,
            create_mana_cost_layer,
            create_title_layer,
            create_type_layer,
            create_rules_text_layer,
            create_power_toughness_layer,
            create_overlay_layers,
        )

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

    def _create_type_layer(self):
        """
        Process title text into the title and append it to `self.text_layers`.
        Negate the `self.mana_cost_x` handling, since the mana cost doesn't share a line
        with the title on these Monopoly frames.
        """

        set_symbol_x = self.SET_SYMBOL_X

        self.SET_SYMBOL_X = self.TYPE_X + self.TYPE_WIDTH
        super()._create_type_layer()

        self.SET_SYMBOL_X = set_symbol_x
