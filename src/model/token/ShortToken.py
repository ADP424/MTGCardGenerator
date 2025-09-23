from model.RegularCard import RegularCard
from model.Layer import Layer
from model.token.RegularToken import RegularToken


class ShortToken(RegularToken):
    """
    A layered image representing a short token and all the collection info on it,
    with all relevant card metadata.

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

        # Type Text
        self.TYPE_Y = 1424

        # Rules Text Box
        self.RULES_BOX_Y = 1555
        self.RULES_BOX_HEIGHT = 377

        # Rules Text
        self.RULES_TEXT_Y = 1555
        self.RULES_TEXT_HEIGHT = 377

        # Set / Rarity Symbol
        self.SET_SYMBOL_Y = 1432
