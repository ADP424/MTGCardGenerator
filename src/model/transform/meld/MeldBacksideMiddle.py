from model.Layer import Layer
from model.regular.RegularCard import RegularCard


class MeldBacksideMiddle(RegularCard):
    """
    A layered image representing the middle strip of a meld backside, sitting between
    `MeldBacksideTop` and `MeldBacksideBottom`.

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

        # Nothing besides art and frames is ever drawn on this strip
        self.SET_SYMBOL_X = float("inf")
        self.SET_SYMBOL_Y = float("inf")
        self.HOLO_STAMP_X = float("inf")
        self.HOLO_STAMP_Y = float("inf")

    def create_layers(
        self,
        create_art_layer: bool = True,
        create_frame_layers: bool = True,
        create_overlay_layers: bool = True,
    ):
        """
        Append the art and frame layers to the card based on `self.metadata`. No text or collector
        info is drawn.

        Parameters
        ----------
        create_art_layer: bool, default: True
            Whether to put the card's art in or not.

        create_frame_layers: bool, default: True
            Whether to put the card's frames on or not.
        """

        if create_art_layer:
            self._create_art_layer()

        if create_frame_layers:
            self._create_frame_layers()

        if create_overlay_layers:
            self._create_overlay_layers()
