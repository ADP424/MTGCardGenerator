from constants import RULES_DIVIDING_LINE
from model.regular.RegularCard import RegularCard
from model.Layer import Layer
from model.showcase.promo.RegularPromo import RegularPromo


class ExtendedPromo(RegularPromo):
    """
    A layered image representing a promo card with an extended art frame
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
        metadata: dict[str, str | list["RegularCard"]] = None,
        art_layer: Layer = None,
        frame_layers: list[Layer] = None,
        collector_layers: list[Layer] = None,
        text_layers: list[Layer] = None,
        overlay_layers: list[Layer] = None,
        footer_largest_index: int = 999,
    ):
        super().__init__(
            metadata, art_layer, frame_layers, collector_layers, text_layers, overlay_layers, footer_largest_index
        )

        # Title Text
        self.TITLE_FONT_COLOR = (0, 0, 0)
        self.TITLE_TEXT_DROP_SHADOW_RELATIVE_OFFSET = (0, 0)

        # Rules Text
        self.RULES_TEXT_FONT_COLOR = (0, 0, 0)
        self.RULES_TEXT_DROP_SHADOW_RELATIVE_OFFSET = (0, 0)

        # Power & Toughness Text
        self.POWER_TOUGHNESS_FONT_COLOR = (0, 0, 0)

        # Other
        self.RULES_TEXT_DIVIDER = RULES_DIVIDING_LINE
