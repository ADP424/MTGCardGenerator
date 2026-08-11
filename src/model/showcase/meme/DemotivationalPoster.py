from constants import (
    LATO,
    LATO_BOLD,
    LATO_ITALICS,
    NEUE_KABEL,
    TIMES_NEW_ROMAN,
)
from model.Layer import Layer
from model.regular.RegularCard import RegularCard


class DemotivationalPoster(RegularCard):
    """
    A layered image representing a demotivational poster meme showcase card and all the collection info on it,
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

        # The art frame for the poster
        self.ART_FRAME_X = 158
        self.ART_FRAME_Y = 267
        self.ART_FRAME_WIDTH = 1184
        self.ART_FRAME_HEIGHT = 876

        # Title Box
        self.TITLE_BOX_X = self.ART_FRAME_X
        self.TITLE_BOX_Y = self.ART_FRAME_Y + self.ART_FRAME_HEIGHT
        self.TITLE_BOX_WIDTH = self.ART_FRAME_WIDTH
        self.TITLE_BOX_HEIGHT = 210

        # Mana Cost
        self.MANA_COST_SYMBOL_SIZE = 120
        self.MANA_COST_ALIGN = "center"
        self.MANA_COST_SYMBOL_SHADOW_OFFSET = (0, 0)
        self.MANA_COST_SYMBOL_OUTLINE_SIZE = 8
        self.MANA_COST_TEXT_FONT = NEUE_KABEL

        self.MANA_COST_BOX_X = self.ART_FRAME_X
        self.MANA_COST_BOX_Y = 20
        self.MANA_COST_BOX_WIDTH = self.ART_FRAME_WIDTH
        self.MANA_COST_BOX_HEIGHT = self.ART_FRAME_Y - self.MANA_COST_BOX_Y

        # Title Text
        self.TITLE_X = self.TITLE_BOX_X
        self.TITLE_BOTTOM_Y = self.TITLE_BOX_Y + self.TITLE_BOX_HEIGHT
        self.TITLE_WIDTH = self.TITLE_BOX_WIDTH
        self.TITLE_MAX_FONT_SIZE = 110
        self.TITLE_FONT = TIMES_NEW_ROMAN
        self.TITLE_FONT_COLOR = (255, 255, 255)
        self.TITLE_TEXT_ALIGN = "center"

        # Type Box
        self.TYPE_BOX_Y = self.TITLE_BOX_Y + self.TITLE_BOX_HEIGHT - 50
        self.TYPE_BOX_HEIGHT = 113

        # Set / Rarity Symbol
        self.SET_SYMBOL_WIDTH = 90
        self.SET_SYMBOL_X = self.ART_FRAME_X + self.ART_FRAME_WIDTH - self.SET_SYMBOL_WIDTH - 20
        self.SET_SYMBOL_Y = self.ART_FRAME_Y + self.ART_FRAME_HEIGHT - self.SET_SYMBOL_WIDTH - 20

        # Type Text
        self.TYPE_X = self.ART_FRAME_X
        self.TYPE_BOTTOM_Y = self.TYPE_BOX_Y + self.TYPE_BOX_HEIGHT - 15
        self.TYPE_WIDTH = self.ART_FRAME_WIDTH
        self.TYPE_MAX_FONT_SIZE = 60
        self.TYPE_FONT = LATO
        self.TYPE_FONT_COLOR = (255, 255, 255)
        self.TYPE_TEXT_ALIGN = "center"

        # Rules Text Box
        self.RULES_BOX_X = self.ART_FRAME_X
        self.RULES_BOX_Y = 1445
        self.RULES_BOX_WIDTH = self.ART_FRAME_WIDTH
        self.RULES_BOX_HEIGHT = 480

        # Rules Text
        self.RULES_TEXT_X = self.RULES_BOX_X
        self.RULES_TEXT_Y = self.RULES_BOX_Y
        self.RULES_TEXT_WIDTH = self.RULES_BOX_WIDTH
        self.RULES_TEXT_HEIGHT = self.RULES_BOX_HEIGHT
        self.RULES_TEXT_FONT = LATO
        self.RULES_TEXT_FONT_ITALICS = LATO_ITALICS
        self.RULES_TEXT_MAX_FONT_SIZE = 68
        self.RULES_TEXT_FONT_COLOR = (255, 255, 255)

        # Power & Toughness
        self.POWER_TOUGHNESS_WIDTH = 250
        self.POWER_TOUGHNESS_HEIGHT = 100
        self.POWER_TOUGHNESS_X = 1190
        self.POWER_TOUGHNESS_Y = 1875
        self.POWER_TOUGHNESS_FONT = LATO_BOLD
        self.POWER_TOUGHNESS_FONT_SIZE = 100
        self.POWER_TOUGHNESS_FONT_COLOR = (255, 255, 255)

    def _create_mana_cost_layer(self):
        """
        Process MTG mana cost into the mana cost header and center it in the margin above the art
        frame, then append it to `self.text_layers`.
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
        with the title on these demotivational poster frames.
        """

        self.mana_cost_x = float("inf")
        super()._create_title_layer()

    def _create_type_layer(self):
        """
        Process type text into the type box and append it to `self.text_layers`.
        Negate the `self.SET_SYMBOL_X` bounding, since the rarity symbol sits in the corner of the
        art frame on these demotivational poster frames instead of sharing a line with the type text.
        """

        set_symbol_x = self.SET_SYMBOL_X

        self.SET_SYMBOL_X = self.TYPE_X + self.TYPE_WIDTH
        super()._create_type_layer()

        self.SET_SYMBOL_X = set_symbol_x
