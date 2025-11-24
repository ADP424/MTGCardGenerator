from constants import CARD_SUBTYPES, CARD_SUPERTYPES, CARD_TYPES
from model.regular.RegularCard import RegularCard
from model.Layer import Layer


class FullArtBasicSNC(RegularCard):
    """
    A layered image representing a full art basic land card from SNC and all the collection info on it,
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

        # Type Box
        self.TYPE_BOX_Y = 1718

        # Type Text
        self.TYPE_BOTTOM_Y = 1814

        # Set / Rarity Symbol
        self.SET_SYMBOL_Y = 1730

        # Subtype Text
        self.SUBTYPE_X = 869
        self.SUBTYPE_WIDTH = 538

    def _create_type_layer(self):
        """
        Process type text into the type box and append it to `self.text_layers`.
        """

        supertypes = self.get_metadata(CARD_SUPERTYPES)
        types = self.get_metadata(CARD_TYPES)
        subtypes = self.get_metadata(CARD_SUBTYPES)

        type_x = self.TYPE_X
        type_width = self.TYPE_WIDTH

        self.set_metadata(CARD_SUBTYPES, "")
        super()._create_type_layer()

        self.TYPE_X = self.SUBTYPE_X
        self.TYPE_WIDTH = self.SUBTYPE_WIDTH
        self.set_metadata(CARD_SUPERTYPES, "")
        self.set_metadata(CARD_TYPES, subtypes + "{center}")
        self.set_metadata(CARD_SUBTYPES, "")
        super()._create_type_layer()

        self.TYPE_X = type_x
        self.TYPE_WIDTH = type_width

        self.set_metadata(CARD_SUPERTYPES, supertypes)
        self.set_metadata(CARD_TYPES, types)
        self.set_metadata(CARD_SUBTYPES, subtypes)
