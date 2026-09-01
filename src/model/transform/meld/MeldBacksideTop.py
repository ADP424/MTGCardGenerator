from model.Layer import Layer
from model.regular.RegularCard import RegularCard


class MeldBacksideTop(RegularCard):
    """
    A layered image representing the top half of a meld backside (see `MeldBacksideBottom` for the
    bottom half, and `MeldBacksideMiddle` for the plain art strip between them). Together, the three
    halves' physical cards line up to form one large landscape image.

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

        # Overall Card
        self.CARD_WIDTH = 2814
        self.CARD_HEIGHT = 2010

        # Title Box
        self.TITLE_BOX_X = 178
        self.TITLE_BOX_Y = 185
        self.TITLE_BOX_WIDTH = 2460
        self.TITLE_BOX_HEIGHT = 217

        # Title Text
        self.TITLE_X = 241
        self.TITLE_BOTTOM_Y = 400
        self.TITLE_WIDTH = 2420
        self.TITLE_MAX_FONT_SIZE = 151
        self.TITLE_FONT_COLOR = (255, 255, 255)

        # Other elements don't appear on this half
        self.SET_SYMBOL_X = float("inf")
        self.SET_SYMBOL_Y = float("inf")
        self.HOLO_STAMP_X = float("inf")
        self.HOLO_STAMP_Y = float("inf")

    def create_layers(
        self,
        create_art_layer: bool = True,
        create_frame_layers: bool = True,
        create_title_layer: bool = True,
        create_overlay_layers: bool = True,
    ):
        """
        Append every frame and text layer to the card based on `self.metadata`. Only the art, frame,
        mana cost, and title are ever drawn on this half.

        Parameters
        ----------
        create_art_layer: bool, default: True
            Whether to put the card's art in or not.

        create_frame_layers: bool, default: True
            Whether to put the card's frames on or not.

        create_mana_cost_layer: bool, default: True
            Whether to put the mana cost of the card on it or not.

        create_title_layer: bool, default: True
            Whether to put the title of the card on it or not.

        create_overlay_layers: bool, default: True
            Whether to put the overlays on top of the card after everything else or not.
        """

        if create_art_layer:
            self._create_art_layer()

        if create_frame_layers:
            self._create_frame_layers()

        if create_title_layer:
            self._create_title_layer()

        if create_overlay_layers:
            self._create_overlay_layers()
