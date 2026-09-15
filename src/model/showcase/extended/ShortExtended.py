from model.Layer import Layer
from model.regular.RegularCard import RegularCard
from model.showcase.extended.Extended import Extended

TYPE_BAR_Y_OFFSET = 91


class ShortExtended(Extended):
    """
    A layered image representing a card with a short extended showcase frame and all the collection info on it,
    with all relevant card metadata. As ExtendedShowcase, but the type bar (and therefore the rules text box
    below it) is shifted 91 pixels lower, shortening the rules text box by the same amount.

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

        # Type Box
        self.TYPE_BOX_Y += TYPE_BAR_Y_OFFSET

        # Type Text
        self.TYPE_BOTTOM_Y += TYPE_BAR_Y_OFFSET

        # Rules Text Box
        self.RULES_BOX_Y += TYPE_BAR_Y_OFFSET
        self.RULES_BOX_HEIGHT -= TYPE_BAR_Y_OFFSET

        # Rules Text
        self.RULES_TEXT_Y += TYPE_BAR_Y_OFFSET
        self.RULES_TEXT_HEIGHT -= TYPE_BAR_Y_OFFSET

        # Set / Rarity Symbol
        self.SET_SYMBOL_Y += TYPE_BAR_Y_OFFSET
