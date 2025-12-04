from model.adventure.RegularAdventure import RegularAdventure
from model.regular.RegularCard import RegularCard
from model.Layer import Layer


class RegularOmen(RegularAdventure):
    """
    A layered image representing an omen card and all the collection info on it,
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
    ):
        super().__init__(metadata, art_layer, frame_layers, collector_layers, text_layers, overlay_layers)

        # Omen Title Text
        self.ADVENTURE_TITLE_BOTTOM_Y = 1400
        self.ADVENTURE_TITLE_MAX_FONT_SIZE = 60

        # Omen Type Text
        self.ADVENTURE_TYPE_BOTTOM_Y = 1490

        # Right Rules Text Box
        self.RULES_BOX_X = 756

        # Omen Rules Text Box
        self.ADVENTURE_RULES_BOX_Y = 1528
        self.ADVENTURE_RULES_BOX_HEIGHT = 395

        # Right Rules Text
        self.RULES_TEXT_X = 771

        # Omen Rules Text
        self.ADVENTURE_RULES_TEXT_Y = 1528
        self.ADVENTURE_RULES_TEXT_HEIGHT = 395
